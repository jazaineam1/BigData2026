"""S13: SECOP, pandas, Dask y entrenamiento clásico. No detecta fraude.

Uso dentro de Codespaces, desde la raíz del repositorio:
    python Laboratorios/S13_Codespaces/analisis.py todo
Las funciones son reutilizables y muestran resultados verificables.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import dask
import dask.dataframe as dd
import pandas as pd
from dask.distributed import Client
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline

ROOT = Path(__file__).resolve().parents[2]
LAB = Path(__file__).resolve().parent
SALIDAS = LAB / "salidas"
CORPUS = ROOT / "Datos/tc2_corpus_2026.json"
CSV = ROOT / "Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv"
CLASES = ("Contratación directa", "Contratación régimen especial")
COL_TEXTO = "descripci_n_del_procedimiento"
COL_LABEL = "modalidad_de_contratacion"


def leer_corpus():
    """Lee el corpus de referencia de 200 expedientes; no tiene etiqueta de modalidad."""
    with CORPUS.open(encoding="utf-8") as archivo:
        documentos = json.load(archivo)["documentos"]
    tabla = pd.DataFrame(documentos)
    assert len(tabla) == 200, "El corpus docente debería tener 200 expedientes"
    assert tabla["id_proceso"].is_unique, "ID duplicado en corpus de referencia"
    return tabla


def leer_etiquetados():
    """Lee una muestra REAL SECOP: 1000 filas, 59 columnas, con modalidad."""
    tabla = pd.read_csv(CSV, low_memory=False)
    obligatorias = {"id_del_proceso", COL_TEXTO, COL_LABEL}
    faltantes = obligatorias - set(tabla.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas del contrato de datos: {sorted(faltantes)}")
    assert len(tabla) == 1000, "La muestra versionada debe tener 1000 filas"
    return tabla


def preparar_clasificacion(tabla):
    """Filtra dos etiquetas frecuentes y mantiene una fila por proceso."""
    muestra = tabla[tabla[COL_LABEL].isin(CLASES)].copy()
    muestra = muestra.drop_duplicates("id_del_proceso").copy()
    muestra[COL_TEXTO] = muestra[COL_TEXTO].fillna("").astype(str)
    muestra = muestra[muestra[COL_TEXTO].str.strip().ne("")].copy()
    if muestra[COL_LABEL].nunique() != 2:
        raise ValueError("Se necesitan dos clases etiquetadas distintas")
    return muestra


def mapear_promedio(lote):
    """MAP: transmite suficiente información para agregar sin sesgo."""
    return sum(lote), len(lote)


def reducir_promedio(parciales):
    """REDUCE: combina las sumas y las cantidades, NO medias locales."""
    total = sum(suma for suma, _ in parciales)
    cantidad = sum(n for _, n in parciales)
    return total / cantidad


def contraste_mapreduce():
    lotes = [[100, 120], [10, 12, 11, 9, 8], [1] * 100]
    parciales = [mapear_promedio(lote) for lote in lotes]
    correcto = reducir_promedio(parciales)
    incorrecto = sum(s / n for s, n in parciales) / len(parciales)
    assert abs(correcto - 370 / 107) < 1e-9
    print(f"Promedio correcto: {correcto:.4f}; ingenuo: {incorrecto:.4f}")
    return {"parciales": parciales, "correcto": correcto, "incorrecto": incorrecto}


def comparar_pandas_dask(tabla, npartitions=4):
    """Misma pregunta, dos motores. Lo primero es la CORRECCIÓN."""
    t0 = time.perf_counter()
    referencia = tabla.groupby(COL_LABEL).size().sort_index()
    t_pandas = time.perf_counter() - t0

    t0 = time.perf_counter()
    ddf = dd.from_pandas(tabla, npartitions=npartitions)
    diferido = ddf.groupby(COL_LABEL).size()
    calculado = diferido.compute().sort_index()
    t_dask = time.perf_counter() - t0

    # Pandas puede usar índice object y Dask StringDtype(pyarrow).
    # La corrección analítica se decide por claves y cantidades, no por el dtype del índice.
    valores_pandas = {str(k): int(v) for k, v in referencia.items()}
    valores_dask = {str(k): int(v) for k, v in calculado.items()}
    assert valores_pandas == valores_dask, "Los conteos por modalidad no coinciden"
    return {
        "filas": len(tabla),
        "particiones": ddf.npartitions,
        "conteos": {str(k): int(v) for k, v in calculado.items()},
        "segundos_pandas": round(t_pandas, 6),
        "segundos_dask": round(t_dask, 6),
        "coinciden": True,
    }


def separar_muestra(tabla):
    muestra = preparar_clasificacion(tabla)
    x = muestra[COL_TEXTO]
    y = muestra[COL_LABEL]
    return train_test_split(x, y, test_size=0.2, random_state=42, stratify=y)


def nuevo_modelo(c=1.0):
    """El vectorizador aprende sólo con entrenamiento: evita fuga por TF-IDF."""
    return make_pipeline(
        TfidfVectorizer(max_features=1500, min_df=2),
        LogisticRegression(C=c, max_iter=500),
    )


def entrenar_y_evaluar(tabla):
    x_train, x_test, y_train, y_test = separar_muestra(tabla)
    modelo = nuevo_modelo()
    t0 = time.perf_counter()
    modelo.fit(x_train, y_train)
    predicciones = modelo.predict(x_test)
    tiempo = time.perf_counter() - t0

    control = DummyClassifier(strategy="most_frequent")
    control.fit(x_train.to_frame(), y_train)
    pred_control = control.predict(x_test.to_frame())
    matriz = confusion_matrix(y_test, predicciones, labels=list(CLASES))
    return {
        "entrenamiento": len(x_train),
        "prueba": len(x_test),
        "f1_macro": round(float(f1_score(y_test, predicciones, average="macro")), 4),
        "f1_control": round(float(f1_score(y_test, pred_control, average="macro")), 4),
        "matriz_confusion": matriz.tolist(),
        "orden_clases": list(CLASES),
        "segundos": round(tiempo, 5),
        "modelo": modelo,
        "division": (x_train, x_test, y_train, y_test),
    }


def evaluar_parametro(c, x_train, y_train):
    """Una tarea Dask: entrena localmente una configuración de scikit-learn."""
    modelo = nuevo_modelo(float(c))
    scores = cross_val_score(modelo, x_train, y_train, cv=3, scoring="f1_macro", n_jobs=1)
    return {"C": float(c), "f1_cv": round(float(scores.mean()), 4)}


def experimentos_distribuidos(tabla, n_workers=2):
    """Distribuye experimentos INDEPENDIENTES; no reparte un solo fit()."""
    x_train, x_test, y_train, y_test = separar_muestra(tabla)
    opciones = [0.1, 1.0, 10.0]
    with Client(processes=False, n_workers=n_workers, threads_per_worker=1,
                dashboard_address=":8787") as client:
        trabajadores = len(client.scheduler_info()["workers"])
        futuros = client.map(evaluar_parametro, opciones,
                             x_train=x_train, y_train=y_train, pure=False)
        resultados = client.gather(futuros)
    ganador = max(resultados, key=lambda r: r["f1_cv"])
    modelo = nuevo_modelo(ganador["C"])
    modelo.fit(x_train, y_train)
    f1_final = f1_score(y_test, modelo.predict(x_test), average="macro")
    return {
        "workers_en_un_codespace": trabajadores,
        "configuraciones": resultados,
        "mejor_C": ganador["C"],
        "f1_prueba_final": round(float(f1_final), 4),
        "nota": "Cada modelo scikit-learn se entrena localmente; Dask distribuye tareas independientes.",
    }


def tarea_con_fallo(numero):
    """Falla intencional y controlada: NO destruye el trabajador."""
    if numero < 0:
        raise ValueError("Entrada inválida de demostración")
    return numero * 2


def recuperacion_demostrativa():
    with Client(processes=False, n_workers=2, threads_per_worker=1,
                dashboard_address=":8787") as client:
        try:
            client.submit(tarea_con_fallo, -1, pure=False).result()
        except ValueError as error:
            fallo = str(error)
        else:
            raise AssertionError("La tarea debía fallar")
        reintento = client.submit(tarea_con_fallo, 4, pure=False).result()
    assert reintento == 8
    return {"fallo_controlado": fallo, "reintento": reintento}


def escribir_resultados(tabla):
    """Parquet con 1000 procesos originales: sin replicaciones ficticias."""
    SALIDAS.mkdir(parents=True, exist_ok=True)
    columnas = ["id_del_proceso", COL_TEXTO, COL_LABEL]
    datos = tabla[columnas].drop_duplicates("id_del_proceso").copy()
    destino = SALIDAS / "secop_s13.parquet"
    datos.to_parquet(destino, index=False)
    leido = pd.read_parquet(destino)
    assert set(leido["id_del_proceso"]) == set(datos["id_del_proceso"])
    with CSV.open("rb") as archivo:
        huella = hashlib.sha256(archivo.read()).hexdigest()
    manifiesto = {
        "fuente": str(CSV.relative_to(ROOT)),
        "sha256_fuente": huella,
        "filas": int(len(leido)),
        "columnas": columnas,
        "salida": "secop_s13.parquet",
        "uso": "didáctico; no detección de fraude ni etiqueta de irregularidad",
    }
    (SALIDAS / "manifest.json").write_text(
        json.dumps(manifiesto, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return manifiesto


def ejecutar_todo():
    print("=== 1. Contexto: corpus sin etiquetas de modalidad ===")
    print("Expedientes del Taller 2:", len(leer_corpus()))
    print("=== 2. MapReduce manual ===")
    contraste_mapreduce()
    print("=== 3. Preparación SECOP etiquetado ===")
    tabla = leer_etiquetados()
    print(tabla[[COL_LABEL, "id_del_proceso"]].head())
    print("=== 4. pandas vs Dask ===")
    print(json.dumps(comparar_pandas_dask(tabla), indent=2, ensure_ascii=False))
    print("=== 5. Modelo clásico ===")
    baseline = entrenar_y_evaluar(tabla)
    print({k: v for k, v in baseline.items() if k not in ("modelo", "division")})
    print("=== 6. Experimentos Dask Distributed ===")
    print(experimentos_distribuidos(tabla))
    print("=== 7. Error y recuperación ===")
    print(recuperacion_demostrativa())
    print("=== 8. Entrega Parquet + manifiesto ===")
    print(escribir_resultados(tabla))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Práctica S13 · sin servicios de pago")
    parser.add_argument("accion", choices=["todo", "mapreduce", "datos", "comparar", "modelo", "experimentos", "fallo", "exportar"])
    args = parser.parse_args()
    if args.accion == "todo":
        ejecutar_todo()
    elif args.accion == "mapreduce":
        print(contraste_mapreduce())
    elif args.accion == "datos":
        print(leer_etiquetados().shape, "y corpus TC2:", len(leer_corpus()))
    elif args.accion == "comparar":
        print(comparar_pandas_dask(leer_etiquetados()))
    elif args.accion == "modelo":
        r = entrenar_y_evaluar(leer_etiquetados())
        print({k: v for k, v in r.items() if k not in ("modelo", "division")})
    elif args.accion == "experimentos":
        print(experimentos_distribuidos(leer_etiquetados()))
    elif args.accion == "fallo":
        print(recuperacion_demostrativa())
    elif args.accion == "exportar":
        print(escribir_resultados(leer_etiquetados()))
