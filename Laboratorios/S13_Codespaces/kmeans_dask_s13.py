#!/usr/bin/env python3
"""S13 | K-means local frente a K-means DISTRIBUIDO con Dask-ML sobre SECOP.

Laboratorio OPCIONAL, no se ejecuta con Run All, Actions ni al abrir Streamlit.
Un único modelo Dask-ML comparte centroides y combina datos de varios workers.
No afirma que sea más rápido, ni presenta agrupamientos como indicios jurídicos.

Uso: python Laboratorios/S13_Codespaces/kmeans_dask_s13.py --n 1000 --workers 2
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import time
from collections import Counter
from pathlib import Path

# Evita atribuir el paralelismo de BLAS/OpenMP local al scheduler Dask.
for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"

ROOT = Path(__file__).resolve().parents[2]
FUENTE = ROOT / "Cuadernos/datos/secop_chunks/secop_chunk_0000000.csv"
SALIDA = ROOT / "Laboratorios/S13_Codespaces/salidas/kmeans_s13.json"
TAMANOS = (250, 1000, 10000, 20000)


def cargar_secop(n: int) -> tuple[list[str], list[str]]:
    """Lee solo las primeras n fichas válidas del CSV real, sin cargar los 100 MB."""
    if n not in TAMANOS:
        raise ValueError(f"n debe estar en {TAMANOS}; 50.000 no pertenece a esta práctica")
    ids, textos, vistos = [], [], set()
    with FUENTE.open(encoding="utf-8-sig", errors="replace", newline="") as archivo:
        lector = csv.DictReader(archivo)
        obligatorias = {"id_del_proceso", "nombre_del_procedimiento"}
        if not obligatorias.issubset(lector.fieldnames or []):
            raise ValueError("Faltan columnas SECOP esperadas")
        for fila in lector:
            clave = (fila.get("id_del_proceso") or "").strip()
            texto = " ".join(filter(None, (
                (fila.get("nombre_del_procedimiento") or "").strip(),
                (fila.get("descripci_n_del_procedimiento") or "").strip()[:500],
            ))).strip()
            if not clave or clave in vistos or len(texto) < 12:
                continue
            vistos.add(clave)
            ids.append(clave)
            textos.append(texto)
            if len(textos) == n:
                break
    if len(textos) != n:
        raise RuntimeError(f"Solo se encontraron {len(textos)} fichas elegibles de {n}")
    return ids, textos


def preparar_vectores(textos: list[str], dimensiones: int = 20):
    """TF-IDF + reducción SVD + normalización: una sola preparación compartida."""
    import numpy as np
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import Normalizer

    vectorizador = TfidfVectorizer(
        max_features=1500, min_df=2, strip_accents="unicode", dtype=np.float64
    )
    dispersa = vectorizador.fit_transform(textos)
    if dimensiones >= min(dispersa.shape):
        raise ValueError("Hay menos palabras/filas que componentes SVD solicitados")
    reducida = TruncatedSVD(
        n_components=dimensiones, n_iter=5, random_state=42
    ).fit_transform(dispersa)
    x = Normalizer().fit_transform(reducida).astype("float64", copy=False)
    assert np.isfinite(x).all()
    return x, int(dispersa.shape[1])


def grupos_representativos(textos, x, etiquetas, centros, max_por_grupo=3):
    """Extracto descriptivo, no etiqueta automática ni detección de anomalías."""
    import numpy as np

    resultado = []
    for i in range(len(centros)):
        indices = np.flatnonzero(etiquetas == i)
        if not len(indices):
            resultado.append({"grupo": i, "cantidad": 0, "ejemplos": []})
            continue
        distancias = np.sum((x[indices] - centros[i]) ** 2, axis=1)
        cercanos = indices[np.argsort(distancias)[:max_por_grupo]]
        resultado.append({
            "grupo": i,
            "cantidad": int(len(indices)),
            "ejemplos": [textos[int(j)][:125] for j in cercanos],
        })
    return resultado


def ejecutar(n=1000, workers=2, k=4, max_iter=12):
    import numpy as np
    import dask.array as da
    from distributed import Client, LocalCluster, get_task_stream, wait
    from dask_ml.cluster import KMeans as DaskKMeans
    from sklearn.cluster import KMeans as LocalKMeans
    from sklearn.metrics import adjusted_rand_score
    from threadpoolctl import threadpool_limits

    inicio = time.perf_counter()
    ids, textos = cargar_secop(n)
    x, vocabulario = preparar_vectores(textos)
    rng = np.random.default_rng(42)
    # Centroides idénticos para ambos métodos; no comparar k-means++ con k-means||.
    centroides = x[rng.choice(n, size=k, replace=False)].copy()
    t_preparacion = time.perf_counter() - inicio

    inicio = time.perf_counter()
    with threadpool_limits(limits=1):
        local = LocalKMeans(n_clusters=k, init=centroides.copy(), n_init=1,
                            max_iter=max_iter, algorithm="lloyd", random_state=42)
        local.fit(x)
    t_local = time.perf_counter() - inicio
    inicio = time.perf_counter()
    with threadpool_limits(limits=1):
        etiquetas_locales = local.predict(x)
    t_predecir_local = time.perf_counter() - inicio

    inicio_cluster = time.perf_counter()
    with LocalCluster(n_workers=workers, threads_per_worker=1,
                      processes=True, dashboard_address=None) as cluster:
        with Client(cluster) as client:
            client.wait_for_workers(workers)
            informacion = client.scheduler_info()["workers"]
            t_arranque = time.perf_counter() - inicio_cluster
            # Cada chunk tiene todas las columnas y se reparte por filas.
            filas_chunk = max(125, n // (workers * 3))
            xd = da.from_array(x, chunks=(filas_chunk, x.shape[1]))
            inicio = time.perf_counter()
            xd = client.persist(xd)
            wait(xd)
            t_persistir = time.perf_counter() - inicio
            modelo = DaskKMeans(n_clusters=k, init=centroides.copy(), n_init=1,
                                 max_iter=max_iter, random_state=42)
            inicio = time.perf_counter()
            with get_task_stream(client=client) as registro:
                modelo.fit(xd)
            t_entrenar = time.perf_counter() - inicio
            inicio = time.perf_counter()
            etiquetas_dask = np.asarray(modelo.predict(xd).compute(), dtype=int)
            t_predecir = time.perf_counter() - inicio
            direcciones = sorted(informacion)
            tareas_por_worker = dict(Counter(
                str(evento.get("worker")) for evento in registro.data
                if evento.get("worker")
            ))
            centros_dask = np.asarray(modelo.cluster_centers_, dtype=float)
            inercia_dask = float(modelo.inertia_)
    assert len(etiquetas_dask) == n
    assert len(etiquetas_locales) == n
    assert np.isfinite(centros_dask).all()

    total_local = t_preparacion + t_local + t_predecir_local
    total_dask = t_preparacion + t_arranque + t_persistir + t_entrenar + t_predecir
    resultado = {
        "caso": "Agrupamiento textual SECOP sin etiquetas",
        "n": n, "variables": int(x.shape[1]), "vocabulario": vocabulario,
        "k": k, "max_iter": max_iter, "fuente": str(FUENTE.relative_to(ROOT)),
        "sha256_ids": hashlib.sha256("\n".join(ids).encode()).hexdigest(),
        "workers_configurados": workers, "workers_reales": direcciones,
        "tareas_entrenamiento_por_worker": tareas_por_worker,
        "workers_con_tareas_entrenamiento": len(tareas_por_worker),
        "alcance_traza": "Tareas observadas durante fit; no es porcentaje de CPU ni tiempo de cada worker",
        "configuracion": "1 hilo por worker; mismas características y centroides iniciales",
        "tiempos_segundos": {
            "lectura_tfidf_svd_y_centroides": round(t_preparacion, 4),
            "fit_kmeans_local": round(t_local, 4),
            "prediccion_local": round(t_predecir_local, 4),
            "arranque_workers_dask": round(t_arranque, 4),
            "transferencia_persistencia": round(t_persistir, 4),
            "fit_kmeans_dask": round(t_entrenar, 4),
            "prediccion_dask": round(t_predecir, 4),
            "pipeline_local_sin_guardado": round(total_local, 4),
            "pipeline_dask_sin_guardado": round(total_dask, 4),
        },
        "inercia_local": float(local.inertia_),
        "inercia_dask": inercia_dask,
        "ari_acuerdo_de_grupos": float(adjusted_rand_score(etiquetas_locales, etiquetas_dask)),
        "grupos_locales": grupos_representativos(textos, x, etiquetas_locales, local.cluster_centers_),
        "grupos_dask": grupos_representativos(textos, x, etiquetas_dask, centros_dask),
        "interpretacion": (
            "Los IDs de grupos pueden permutarse y los algoritmos pueden converger "
            "a soluciones distintas. ARI=1 implica acuerdo de asignaciones; no es "
            "una puntuación de calidad semántica ni un juicio jurídico. "
            "Comparar tiempos TOTALES; no garantizar aceleración."
        ),
        "aviso": "Datos reales; primera muestra del CSV, no representativa de SECOP completo. Sin DBSCAN ni 50k.",
    }
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
    return resultado


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, choices=TAMANOS, default=1000)
    parser.add_argument("--workers", type=int, choices=(1, 2, 4), default=2)
    parser.add_argument("--k", type=int, choices=(3, 4, 5, 6, 8), default=4)
    parser.add_argument("--max-iter", type=int, choices=(8, 12, 20), default=12)
    args = parser.parse_args()
    if args.n >= 10000 and os.environ.get("S13_PERMITIR_AMPLIACION") != "1":
        parser.error("Para 10k/20k, habilitar S13_PERMITIR_AMPLIACION=1 tras prueba pequeña")
    datos = ejecutar(args.n, args.workers, args.k, args.max_iter)
    print(json.dumps({
        "registros": datos["n"],
        "workers_reales": datos["workers_reales"],
        "tareas_entrenamiento_por_worker": datos["tareas_entrenamiento_por_worker"],
        "tiempos_segundos": datos["tiempos_segundos"],
        "ari_acuerdo_de_grupos": datos["ari_acuerdo_de_grupos"],
        "salida": str(SALIDA),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
