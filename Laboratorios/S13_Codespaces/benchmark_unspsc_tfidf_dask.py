"""S13: benchmark real UNSPSC TF-IDF local vs Dask (1000/10000/20000).

Los textos y etiquetas provienen de CSV SECOP versionados; NO genera datos
sinteticos, NO presupone ofertas o precios; etiquetas UNSPSC de formato válido.

La ruta Dask de TF-IDF paraleliza la TRANSFORMACION, no LinearSVC.fit.
La ruta XGBoost.dask entrena UN clasificador entre varios workers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import re
import sys
import time
from collections import Counter
from pathlib import Path

import dask.array as da
import numpy as np
import pandas as pd
from dask.distributed import Client, LocalCluster
from scipy.sparse import vstack
from sklearn.decomposition import TruncatedSVD
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import balanced_accuracy_score, f1_score
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parents[2]
FUENTES = sorted((ROOT / "Cuadernos/datos/secop_chunks").glob("secop_chunk_*.csv"))
SALIDA = Path(__file__).resolve().parent / "salidas" / "benchmark_unspsc"
COLUMNAS = [
    "id_del_proceso", "fecha_de_publicacion_del",
    "nombre_del_procedimiento", "descripci_n_del_procedimiento",
    "codigo_principal_de_categoria",
]
TOP_SEGMENTOS = ("80", "85", "93", "81", "72")  # segun auditoria de 300k
ETIQUETAS = tuple(sorted(TOP_SEGMENTOS + ("OTRAS",)))
CODIGO = re.compile(r"^(?:V[0-9]+\.)?([0-9]{8})$")
NUMEROS_LARGOS = re.compile(r"(?<![a-zA-Z0-9])(?:V\d+\.)?\d{7,12}(?!\d)")


def texto_limpio(titulo, descripcion):
    """Quita códigos largos que podrían revelar la etiqueta literal."""
    t = str(titulo or "").strip() + " " + str(descripcion or "").strip()
    t = NUMEROS_LARGOS.sub(" ", t)
    return re.sub(r"\s+", " ", t).strip()[:1600]


def leer_muestra(tamano_maximo=20000):
    """Reservorio sobre 300k filas; deduplicación por ID global.

    No se seleccionan los primeros 20k: el muestreo recorre todas las fuentes.
    Sólo los procesos con código UNSPSC válido se consideran etiquetados.
    """
    if not FUENTES:
        raise FileNotFoundError("Faltan secop_chunk_*.csv del repositorio.")
    rng = random.Random(42)
    vistos = set()
    muestra = []
    n_elegibles = 0
    estad = Counter()
    usados = []
    for path in FUENTES:
        usados.append(str(path.relative_to(ROOT)))
        for fragmento in pd.read_csv(
            path, usecols=COLUMNAS, chunksize=5000, dtype=str,
            keep_default_na=False, on_bad_lines="error",
        ):
            estad["filas_leidas"] += len(fragmento)
            for fila in fragmento.itertuples(index=False, name=None):
                r = dict(zip(fragmento.columns, fila))
                id_ = r["id_del_proceso"].strip()
                if not id_ or id_ in vistos:
                    estad["id_vacio_o_repetido"] += 1
                    continue
                vistos.add(id_)
                codigo = CODIGO.fullmatch(r["codigo_principal_de_categoria"].strip())
                if codigo is None:
                    estad["codigo_no_valido"] += 1
                    continue
                fecha = pd.to_datetime(
                    r["fecha_de_publicacion_del"], errors="coerce",
                )
                if pd.isna(fecha):
                    estad["fecha_no_valida"] += 1
                    continue
                texto = texto_limpio(
                    r["nombre_del_procedimiento"],
                    r["descripci_n_del_procedimiento"],
                )
                if len(texto) < 20:
                    estad["texto_muy_corto"] += 1
                    continue
                segmento = codigo.group(1)[:2]
                etiqueta = segmento if segmento in TOP_SEGMENTOS else "OTRAS"
                registro = (id_, fecha, texto, etiqueta)
                n_elegibles += 1
                if len(muestra) < tamano_maximo:
                    muestra.append(registro)
                else:
                    j = rng.randrange(n_elegibles)
                    if j < tamano_maximo:
                        muestra[j] = registro
    if len(muestra) < tamano_maximo:
        raise RuntimeError(
            f"Sólo {len(muestra)} fichas válidas, se pidieron {tamano_maximo}. "
            "No se completará con datos inventados."
        )
    tabla = pd.DataFrame(muestra, columns=["id", "fecha", "texto", "etiqueta"])
    tabla = tabla.sort_values(["fecha", "id"]).reset_index(drop=True)
    assert tabla["id"].is_unique
    assert set(tabla["etiqueta"]).issubset(set(ETIQUETAS))
    return tabla, {
        "archivos": usados,
        "filas_elegibles": n_elegibles,
        "filas_muestreadas": len(tabla),
        "semilla_reservorio": 42,
        "descartes": dict(estad),
        "segmentos": list(TOP_SEGMENTOS),
    }


def seleccion_n(tabla, n):
    """El mismo muestreo fijo, luego partición temporal 80/20."""
    if n > len(tabla):
        raise ValueError(f"{n} supera {len(tabla)} filas")
    sub = tabla if n == len(tabla) else tabla.sample(n=n, random_state=42)
    sub = sub.sort_values(["fecha", "id"]).reset_index(drop=True)
    corte = int(n * 0.8)
    entrenamiento, prueba = sub.iloc[:corte], sub.iloc[corte:]
    assert entrenamiento["fecha"].max() <= prueba["fecha"].min()
    assert not set(entrenamiento.id).intersection(set(prueba.id))
    return entrenamiento, prueba


def chunks_lista(textos, chunk_size):
    t = list(textos)
    return [t[i:i + chunk_size] for i in range(0, len(t), chunk_size)]


def transformar_bloque(vectorizador, textos):
    return vectorizador.transform(textos)


def transformar_dask(client, vectorizador, textos, chunk_size=1000):
    partes = chunks_lista(textos, chunk_size)
    vec_futuro = client.scatter(vectorizador, broadcast=True)
    tareas = [
        client.submit(transformar_bloque, vec_futuro, bloque, pure=False)
        for bloque in partes
    ]
    resultados = client.gather(tareas)
    return vstack(resultados, format="csr")


def puntuar(verdad, prediccion):
    return {
        "f1_macro": round(float(f1_score(verdad, prediccion, average="macro",
                                         labels=list(ETIQUETAS), zero_division=0)), 4),
        "balanced_accuracy": round(float(balanced_accuracy_score(verdad, prediccion)), 4),
    }


def entrenar_xgb_distribuido(client, x_train, y_train, x_test, clases, rondas):
    from xgboost import dask as dxgb
    dim = x_train.shape[1]
    nombres = [f"svd_{j:02d}" for j in range(dim)]
    datos = da.from_array(
        np.ascontiguousarray(x_train, dtype="float32"),
        chunks=(1000, dim),
    )
    labels = da.from_array(
        np.asarray(y_train, dtype="float32"), chunks=(1000,),
    )
    matriz = dxgb.DaskDMatrix(client, datos, labels, feature_names=nombres)
    start = time.perf_counter()
    res = dxgb.train(
        client,
        {
            "objective": "multi:softprob",
            "num_class": len(clases),
            "tree_method": "hist",
            "max_depth": 4,
            "eta": 0.15,
            "nthread": 1,
            "seed": 42,
        },
        matriz, num_boost_round=rondas,
    )
    fit_s = time.perf_counter() - start
    test_da = da.from_array(
        np.ascontiguousarray(x_test, dtype="float32"), chunks=(1000, dim),
    )
    pred_matriz = dxgb.DaskDMatrix(client, test_da, feature_names=nombres)
    prob = np.asarray(dxgb.predict(client, res["booster"], pred_matriz).compute())
    return np.argmax(prob, axis=1), fit_s, int(datos.npartitions)


def ejecutar(sizes, workers=2, rondas=25, svd_dim=32):
    if not sizes or min(sizes) < 100 or workers < 2:
        raise ValueError("Usa tamaños >=100 y al menos 2 workers Dask.")
    maximo = max(sizes)
    salida = {"resultados": [], "equipo": {
        "python": sys.version.split()[0],
        "plataforma": platform.platform(),
        "cpu_logicos": os.cpu_count(),
        "workers_en_un_solo_runner": workers,
        "dask_nodos_fisicos": 1,
        "nota": "Tiempos medidos en GitHub Actions, no en HP del profesor.",
    }}
    tabla, metadatos = leer_muestra(maximo)
    salida["fuentes"] = metadatos
    SALIDA.mkdir(parents=True, exist_ok=True)
    t_cluster = time.perf_counter()
    with LocalCluster(
        n_workers=workers, threads_per_worker=1, processes=True,
        memory_limit="2GiB", dashboard_address=":8787",
    ) as cluster:
        with Client(cluster) as client:
            salida["segundos_crear_cluster"] = round(time.perf_counter()-t_cluster, 3)
            assert len(client.scheduler_info()["workers"]) == workers
            for n in sizes:
                train, test = seleccion_n(tabla, n)
                texts_tr = train.texto.tolist()
                texts_te = test.texto.tolist()
                y_train = train.etiqueta.tolist()
                y_test = test.etiqueta.tolist()
                if len(set(y_train)) < 5:
                    raise RuntimeError(f"No hay suficientes clases presentes en n={n}")
                inicio = time.perf_counter()
                vec = TfidfVectorizer(
                    max_features=6000, ngram_range=(1, 2),
                    min_df=2, max_df=0.98, sublinear_tf=True,
                    strip_accents="unicode", dtype=np.float32,
                )
                vec.fit(texts_tr)
                t_vocab = time.perf_counter()-inicio

                t0 = time.perf_counter()
                xtr_local = vec.transform(texts_tr)
                xte_local = vec.transform(texts_te)
                t_local = time.perf_counter()-t0

                t0 = time.perf_counter()
                xtr_dask = transformar_dask(client, vec, texts_tr, chunk_size=1000)
                xte_dask = transformar_dask(client, vec, texts_te, chunk_size=1000)
                t_dask = time.perf_counter()-t0

                if xtr_local.shape != xtr_dask.shape:
                    raise AssertionError("Dask alteró las dimensiones")
                if (xtr_local != xtr_dask).nnz or (xte_local != xte_dask).nnz:
                    raise AssertionError("Dask no produjo exactamente el mismo TF-IDF")

                t0 = time.perf_counter()
                clf = LinearSVC(class_weight="balanced", random_state=42)
                clf.fit(xtr_local, y_train)
                pred_local = clf.predict(xte_local)
                t_svc = time.perf_counter()-t0
                pred_dask = clf.predict(xte_dask)
                if not np.array_equal(pred_local, pred_dask):
                    raise AssertionError("Predicciones cambiaron entre motores")

                base = DummyClassifier(strategy="most_frequent")
                base.fit(xtr_local, y_train)
                pred_base = base.predict(xte_local)

                t0 = time.perf_counter()
                svd = TruncatedSVD(n_components=svd_dim, n_iter=3, random_state=42)
                ztr = svd.fit_transform(xtr_dask).astype("float32")
                zte = svd.transform(xte_dask).astype("float32")
                t_svd = time.perf_counter()-t0

                enc = LabelEncoder().fit(list(ETIQUETAS))
                train_labels = enc.transform(y_train)
                pred_enc, t_xgb, part_xgb = entrenar_xgb_distribuido(
                    client, ztr, train_labels, zte, enc.classes_, rondas
                )
                pred_xgb = enc.inverse_transform(pred_enc)
                r = {
                    "n": n,
                    "train": len(train),
                    "test": len(test),
                    "etiquetas_train": dict(Counter(y_train)),
                    "vocabulario": len(vec.vocabulary_),
                    "dim_svd": svd_dim,
                    "workers": workers,
                    "segundos_vocabulario_local": round(t_vocab, 3),
                    "segundos_tfidf_local": round(t_local, 3),
                    "segundos_tfidf_dask": round(t_dask, 3),
                    "factor_tiempo_dask_sobre_local_tfidf":
                        round(t_dask/max(t_local, 1e-9), 3),
                    "segundos_svc_local_fit_predict": round(t_svc, 3),
                    "segundos_svd_local": round(t_svd, 3),
                    "segundos_xgb_train_distribuido": round(t_xgb, 3),
                    "particiones_xgb_train": part_xgb,
                    "metricas": {
                        "mayoritaria": puntuar(y_test, pred_base),
                        "tfidf_linearsvc": puntuar(y_test, pred_local),
                        "tfidf_svd_xgboost_dask": puntuar(y_test, pred_xgb),
                    },
                }
                salida["resultados"].append(r)
                (SALIDA / f"metricas_{n}.json").write_text(
                    json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8",
                )
                print("RESULTADO_"+str(n)+" "+json.dumps(r,ensure_ascii=False),flush=True)
    (SALIDA / "benchmark.json").write_text(
        json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    print("BENCHMARK_FINAL "+json.dumps(salida,ensure_ascii=False),flush=True)
    return salida


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", type=int, nargs="+", default=[1000, 10000, 20000])
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--rondas", type=int, default=25)
    parser.add_argument("--svd-dim", type=int, default=32)
    args = parser.parse_args()
    ejecutar(args.sizes, workers=args.workers, rondas=args.rondas,
             svd_dim=args.svd_dim)
