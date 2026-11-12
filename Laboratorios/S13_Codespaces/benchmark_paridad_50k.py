"""Comparación justa local vs Dask: MISMO modelo, datos y parámetros, tamaños 1k/10k/20k/50k.

1) TF-IDF: un solo vocabulario entrenado SOLO en train. Se comparan las matrices
   locales y distribuidas; se entrena el MISMO LinearSVC en cada una.
2) XGBoost: una sola matriz SVD entrenada SOLO en train, MISMO objetivo,
   hiperparámetros y rondas para xgboost.train y xgboost.dask.train.
   Los resultados XGBoost pueden diferir por reducciones flotantes entre workers.
3) Tiempo de carga/selección y de iniciar Dask se registra APARTE.
   El tiempo "end-to-end" de un modelo incluye TF-IDF fit/transform + fit/predict;
   no incluye lectura inicial del universo ni reutilización del cluster precreado.

No hay datos sintéticos ni inferencias de EmbeddingGemma disfrazadas de TF-IDF.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from pathlib import Path

import dask.array as da
import numpy as np
import pandas as pd
import xgboost as xgb
from dask.distributed import Client, LocalCluster
from scipy.sparse import vstack
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import balanced_accuracy_score, f1_score
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC

from benchmark_unspsc_tfidf_dask import leer_muestra, seleccion_n, ETIQUETAS, SALIDA

PARAMETROS_XGB = {
    "objective": "multi:softprob", "num_class": len(ETIQUETAS),
    "tree_method": "hist", "max_depth": 4, "eta": 0.15,
    "subsample": 1.0, "colsample_bytree": 1.0,
    "seed": 42, "verbosity": 0,
}
RONDAS = 30


def evaluar(y, pred):
    return {
        "f1_macro": round(float(f1_score(
            y, pred, labels=list(ETIQUETAS),
            average="macro", zero_division=0)), 5),
        "balanced_accuracy": round(float(balanced_accuracy_score(y, pred)), 5),
    }


def transformar_bloque(vec, textos):
    return vec.transform(textos)


def transformar_paralelo(cliente, vec_futuro, textos, filas_por_bloque=1000):
    pendientes = [
        cliente.submit(
            transformar_bloque, vec_futuro,
            textos[i:i + filas_por_bloque], pure=False,
        )
        for i in range(0, len(textos), filas_por_bloque)
    ]
    return vstack(cliente.gather(pendientes), format="csr")


def svm():
    # Dos ajustes en las matrices equivalentes: mismos valores e hiperparámetros.
    return LinearSVC(
        class_weight="balanced", random_state=42, dual="auto",
        max_iter=3000, tol=1e-4,
    )


def matrices_tfidf(client, textos_train, textos_test):
    t0 = time.perf_counter()
    vec = TfidfVectorizer(
        max_features=6000, min_df=2, max_df=0.98,
        ngram_range=(1, 2), sublinear_tf=True,
        strip_accents="unicode", dtype=np.float32,
    )
    vec.fit(textos_train)
    t_vocab = time.perf_counter() - t0

    t0 = time.perf_counter()
    x_l = vec.transform(textos_train)
    x_lt = vec.transform(textos_test)
    t_local = time.perf_counter() - t0

    t0 = time.perf_counter()
    futuro = client.scatter(vec, broadcast=True)
    # Mantener 'futuro' vivo hasta que TERMINE train y test.
    x_d = transformar_paralelo(client, futuro, textos_train)
    x_dt = transformar_paralelo(client, futuro, textos_test)
    t_dask = time.perf_counter() - t0
    if x_l.shape != x_d.shape or x_lt.shape != x_dt.shape:
        raise AssertionError("Dask cambió las dimensiones TF-IDF.")
    if (x_l != x_d).nnz or (x_lt != x_dt).nnz:
        raise AssertionError("El TF-IDF Dask NO es idéntico al local.")
    return vec, (x_l, x_lt), (x_d, x_dt), {
        "tfidf_fit_vocabulario_local_s": t_vocab,
        "tfidf_transform_local_s": t_local,
        "tfidf_transform_dask_s": t_dask,
        "tfidf_igualdad_matrices": True,
        "vocabulario": len(vec.vocabulary_),
    }


def xgb_local(X_train, y_train, X_test, rounds):
    nombres = [f"svd_{j:02d}" for j in range(X_train.shape[1])]
    dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=nombres)
    dtest = xgb.DMatrix(X_test, feature_names=nombres)
    t0 = time.perf_counter()
    booster = xgb.train(
        {**PARAMETROS_XGB, "nthread": 2},
        dtrain, num_boost_round=rounds,
    )
    tiempo = time.perf_counter() - t0
    pred = np.asarray(booster.predict(dtest)).argmax(axis=1)
    return pred, tiempo, booster.num_boosted_rounds()


def xgb_dask(client, X_train, y_train, X_test, rounds):
    from xgboost import dask as dxgb

    dim = X_train.shape[1]
    tamano_chunk = max(100, min(2500, int(np.ceil(len(X_train) / 6))))
    nombres = [f"svd_{j:02d}" for j in range(dim)]
    dax = da.from_array(
        np.ascontiguousarray(X_train, dtype=np.float32),
        chunks=(tamano_chunk, dim),
    )
    day = da.from_array(
        np.asarray(y_train, dtype=np.float32),
        chunks=(tamano_chunk,),
    )
    matriz = dxgb.DaskDMatrix(
        client, dax, day, feature_names=nombres,
    )
    t0 = time.perf_counter()
    booster = dxgb.train(
        client, {**PARAMETROS_XGB, "nthread": 1},
        matriz, num_boost_round=rounds,
    )["booster"]
    tiempo = time.perf_counter() - t0
    test_a = da.from_array(
        np.ascontiguousarray(X_test, dtype=np.float32),
        chunks=(tamano_chunk, dim),
    )
    test_dm = dxgb.DaskDMatrix(client, test_a, feature_names=nombres)
    probs = np.asarray(dxgb.predict(client, booster, test_dm).compute())
    return probs.argmax(axis=1), tiempo, booster.num_boosted_rounds(), dax.npartitions


def correr(sizes=(1000, 10000, 20000, 50000), workers=2, rounds=RONDAS):
    if not sizes or min(sizes) < 200 or max(sizes) > 100000 or workers < 2:
        raise ValueError("sizes 200..100000, workers >=2")
    SALIDA.mkdir(parents=True, exist_ok=True)
    comienzo = time.perf_counter()
    tabla, origen = leer_muestra(max(sizes))
    t_lectura = time.perf_counter() - comienzo
    t0 = time.perf_counter()
    resultados = []
    with LocalCluster(
        n_workers=workers, threads_per_worker=1, processes=True,
        memory_limit="2GiB", dashboard_address=None,
    ) as cluster:
        with Client(cluster) as client:
            t_cluster = time.perf_counter() - t0
            if len(client.scheduler_info()["workers"]) != workers:
                raise RuntimeError("No se iniciaron suficientes trabajadores")
            for n in sizes:
                train, test = seleccion_n(tabla, n)
                ytr = train.etiqueta.to_numpy()
                yte = test.etiqueta.to_numpy()
                textos_tr = train.texto.tolist()
                textos_te = test.texto.tolist()

                vec, local, distribuido, tiempos = matrices_tfidf(
                    client, textos_tr, textos_te,
                )
                xtr, xte = local
                xdtr, xdte = distribuido

                t0 = time.perf_counter()
                svm_local = svm().fit(xtr, ytr)
                fit_svm_local = time.perf_counter() - t0
                pred_l = svm_local.predict(xte)
                t0 = time.perf_counter()
                svm_dask = svm().fit(xdtr, ytr)
                fit_svm_dask = time.perf_counter() - t0
                pred_d = svm_dask.predict(xdte)
                if not np.array_equal(pred_l, pred_d):
                    raise AssertionError(
                        "Mismo LinearSVC + mismas matrices, predicciones distintas"
                    )
                if not np.allclose(
                    svm_local.coef_, svm_dask.coef_, atol=1e-5, rtol=1e-4,
                ):
                    raise AssertionError("Pesos LinearSVC local / Dask distintos")

                # Ambos XGBoost reciben literalmente las MISMAS matrices y etiquetas.
                t0 = time.perf_counter()
                svd = TruncatedSVD(
                    n_components=32, random_state=42, n_iter=3,
                )
                Xtr_svd = svd.fit_transform(xtr).astype(np.float32)
                Xte_svd = svd.transform(xte).astype(np.float32)
                t_svd = time.perf_counter() - t0
                codificador = LabelEncoder().fit(list(ETIQUETAS))
                y_enc = codificador.transform(ytr)

                local_pred, local_fit, local_rounds = xgb_local(
                    Xtr_svd, y_enc, Xte_svd, rounds,
                )
                dask_pred, dask_fit, dask_rounds, particiones = xgb_dask(
                    client, Xtr_svd, y_enc, Xte_svd, rounds,
                )
                pred_local_xgb = codificador.inverse_transform(local_pred)
                pred_dask_xgb = codificador.inverse_transform(dask_pred)

                resultados.append({
                    "n": n, "train": len(train), "test": len(test),
                    "workers": workers, "particiones_dask_xgb": particiones,
                    **{k: round(v, 5) if isinstance(v, float) else v
                       for k, v in tiempos.items()},
                    "svm_fit_local_s": round(fit_svm_local, 5),
                    "svm_fit_dask_transform_s": round(fit_svm_dask, 5),
                    "svd_ajuste_transformacion_local_s": round(t_svd, 5),
                    "xgb_fit_local_s": round(local_fit, 5),
                    "xgb_fit_dask_s": round(dask_fit, 5),
                    "rondas_ambos": [local_rounds, dask_rounds],
                    "tfidf_svm_predicciones_iguales": True,
                    "acuerdo_xgb_predicciones_porcentaje": round(
                        float(np.mean(local_pred == dask_pred) * 100), 2,
                    ),
                    "metricas": {
                        "tfidf_svm_local": evaluar(yte, pred_l),
                        "tfidf_svm_dask_transform": evaluar(yte, pred_d),
                        "svd_xgb_local": evaluar(yte, pred_local_xgb),
                        "svd_xgb_dask": evaluar(yte, pred_dask_xgb),
                    },
                    "tfidf_svm_tiempo_pipeline_local_s": round(
                        tiempos["tfidf_fit_vocabulario_local_s"]
                        + tiempos["tfidf_transform_local_s"] + fit_svm_local, 5,
                    ),
                    "tfidf_svm_tiempo_pipeline_dask_s": round(
                        tiempos["tfidf_fit_vocabulario_local_s"]
                        + tiempos["tfidf_transform_dask_s"] + fit_svm_dask, 5,
                    ),
                    "nota": (
                        "Mismas matrices TF-IDF, etiquetas, hiperparametros "
                        "y 32 componentes SVD para XGBoost local y distribuido. "
                        "La reduccion distribuida de histogramas puede variar "
                        "levemente el modelo entrenado."
                    ),
                })
                fila = resultados[-1]
                print("PARIDAD_"+str(n)+" "+json.dumps(
                    fila, ensure_ascii=False, sort_keys=True,
                ), flush=True)
                (SALIDA/f"paridad_{n}.json").write_text(
                    json.dumps(fila, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
    resumen = {
        "equipo": {
            "python": sys.version.split()[0],
            "plataforma": platform.platform(),
            "nucleos_logicos_reportados": os.cpu_count(),
            "workers": workers, "nodos_fisicos": 1,
        },
        "origen": origen, "segundos_lectura_muestreo_300k": round(t_lectura, 3),
        "segundos_inicio_cluster": round(t_cluster, 3),
        "hiperparametros_xgb": PARAMETROS_XGB,
        "xgb_rounds": rounds,
        "sizes": list(sizes), "resultados": resultados,
    }
    (SALIDA/"paridad_50k_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("PARIDAD_FINAL "+json.dumps(resumen, ensure_ascii=False), flush=True)
    return resumen


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--sizes", nargs="+", type=int,
                   default=[1000, 10000, 20000, 50000])
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--rondas", type=int, default=RONDAS)
    args = p.parse_args()
    correr(sizes=args.sizes, workers=args.workers, rounds=args.rondas)
