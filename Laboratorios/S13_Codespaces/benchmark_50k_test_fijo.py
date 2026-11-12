"""Benchmark comparativo JUSTO SECOP UNSPSC: 1k/10k/20k/50k.

Rigurosidad: MISMO test fijo (10.000 procesos), entrenamientos anidados,
MISMAS clases, TfidfVectorizer, LinearSVC y parámetros; misma máquina.
TF-IDF Dask realiza sólo vectorización (NO fit de LinearSVC distribuido).
La pista XGBoost usa igual vectorización/SVD y un modelo entre workers.

Los registros son fichas SECOP, NO contratos PDF ni datos sinteticos.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from dask.distributed import Client, LocalCluster
from scipy.sparse import vstack
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (balanced_accuracy_score, classification_report,
                             confusion_matrix, f1_score)
from sklearn.svm import LinearSVC
import xgboost as xgb

from benchmark_unspsc_tfidf_dask import (ETIQUETAS, SALIDA, FUENTES, leer_muestra,
                                         transformar_bloque, chunks_lista,
                                         entrenar_xgb_distribuido)
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import LabelEncoder

TAMANOS = (1000, 10000, 20000, 50000)
N_TEST = 10000
SEMILLA = 42
MAX_TERMS = 6000
CHUNK = 1000


def generar_conjuntos(tamano_max=50000, test_size=N_TEST):
    """Reservorio FIJO de 60k fichas, test último periodo, train anterior.

    No depende de la etiqueta al escoger test; train n anidados dentro del
    conjunto más antiguo (semilla fija). No se reusa NINGUN ID de test.
    """
    assert tamano_max >= max(TAMANOS)
    tabla, meta = leer_muestra(tamano_max+test_size)
    tabla = tabla.sort_values(["fecha","id"]).reset_index(drop=True)
    pool = tabla.iloc[:tamano_max].copy()
    test = tabla.iloc[tamano_max:].copy()
    assert len(test)==test_size and len(pool)==tamano_max
    assert pool["fecha"].max() <= test["fecha"].min()
    assert not set(pool.id)&set(test.id)
    # Un solo orden aleatorio fijo, prefijos anidados; no volver a samplear.
    orden = np.random.default_rng(SEMILLA).permutation(len(pool))
    return pool, test, orden, meta


def vectorizador():
    return TfidfVectorizer(
        max_features=MAX_TERMS, ngram_range=(1,2), min_df=2,
        max_df=0.98, sublinear_tf=True, strip_accents="unicode",
        dtype=np.float32,
    )


def tfidf_paralelo(client, vec, textos):
    """Tiempo visible de envio de vocabulario, transformacion y recoleccion."""
    futuro = client.scatter(vec, broadcast=True, hash=False)  # key único: sin borrar dependencias de ejecuciones anteriores
    piezas = chunks_lista(textos, CHUNK)
    trabajos = [
        client.submit(transformar_bloque, futuro, chunk, pure=False)
        for chunk in piezas
    ]
    return vstack(client.gather(trabajos),format="csr")


def medir(operacion, repeticiones=3):
    muestras=[]
    salida=None
    for _ in range(repeticiones):
        inicio=time.perf_counter()
        salida=operacion()
        muestras.append(time.perf_counter()-inicio)
    return salida, [round(x,4) for x in muestras], round(float(np.median(muestras)),4)


def huellas_ids(ids):
    return hashlib.sha256(
        "\n".join(str(v) for v in ids).encode("utf-8")
    ).hexdigest()


def calidad(real, pred):
    return {
        "f1_macro": round(float(f1_score(
            real,pred,labels=list(ETIQUETAS),average="macro",zero_division=0)),5),
        "balanced_accuracy":round(float(balanced_accuracy_score(real,pred)),5),
        "exactitud":round(float(np.mean(np.asarray(real)==np.asarray(pred))),5),
    }


def ejecutar(sizes=TAMANOS, workers=2, repeticiones=3, rondas=20,
             con_xgboost=True):
    if list(sizes)!=sorted(set(sizes)) or not sizes or min(sizes)<100:
        raise ValueError("Tamanos ordenados, unicos y positivos")
    if max(sizes)>50000 or workers<2 or repeticiones<1:
        raise ValueError("Maximo 50000; workers>=2; repeticiones>=1")
    t0=time.perf_counter()
    pool, test, orden, origen=generar_conjuntos()
    lectura=time.perf_counter()-t0
    print("FUENTE REAL leida. Train pool:",len(pool),"test temporal FIJO:",
          len(test),"filas de origen:",origen["descartes"]["filas_leidas"],
          "lectura segundos:",round(lectura,3),flush=True)
    yte=test.etiqueta.tolist()
    texto_test=test.texto.tolist()
    test_hash=huellas_ids(test.id)
    datos={"diseño":{
        "n_test_fijo":len(test),"test_sha256_ids":test_hash,
        "test_primera_fecha":str(test.fecha.min()),"test_ultima_fecha":str(test.fecha.max()),
        "train_ultima_fecha":str(pool.fecha.max()),
        "train_pool":len(pool), "tamano_train_pedidos":list(sizes),
        "entrenamientos_anidados":True,"semilla":SEMILLA,
        "classes":list(ETIQUETAS),"max_features":MAX_TERMS,
        "ngram_range":[1,2],"min_df":2,"max_df":0.98,
        "class_weight":"balanced","svc_random_state":42,
        "xgboost_params_identicos_except_threads":True,
        "xgboost_threads_local":2,"xgboost_threads_por_worker":1,
        "rondas_xgboost":rondas,"svd_dim":32,
        "repeticiones_transformacion":repeticiones,
        "advertencia":"Test FIJO, pero vocabulario ajustado por tamano de train; "
        "SVD local + XGBoost.dask usa otro algoritmo y representacion.",
    },"origen":origen,"equipo":{
        "python":sys.version.split()[0],"plataforma":platform.platform(),
        "cpu_logicos":os.cpu_count(),"workers":workers,
        "nodos_fisicos":1,"segundos_lectura_y_muestreo":round(lectura,3),
    },"resultados":[]}
    SALIDA.mkdir(parents=True,exist_ok=True)
    inicio_cluster=time.perf_counter()
    with LocalCluster(
        n_workers=workers,threads_per_worker=1,processes=True,
        memory_limit="2GiB",dashboard_address=":8787",
    ) as cluster:
        with Client(cluster) as client:
            datos["equipo"]["segundos_arranque_cluster"]=round(
                time.perf_counter()-inicio_cluster,4)
            assert len(client.scheduler_info()["workers"])==workers
            prev=set()
            for n in sizes:
                indices=orden[:n]
                tr=pool.iloc[indices].copy().sort_values(["fecha","id"])
                assert len(tr)==n and tr.id.is_unique
                assert not prev.difference(set(tr.id)), "Los train NO son anidados"
                prev=set(tr.id)
                assert tr.fecha.max()<=test.fecha.min()
                textos=tr.texto.tolist()
                ytr=tr.etiqueta.tolist()
                v=vectorizador()
                start=time.perf_counter()
                v.fit(textos)
                t_fit_vocab=time.perf_counter()-start
                (xtr,xte),muestras_loc,seg_local=medir(
                    lambda:(v.transform(textos),v.transform(texto_test)),
                    repeticiones)
                # Mantener el Future en este ámbito durante TODAS las
                # repeticiones y transformaciones (evita lost dependencies).
                vectorizador_remoto=client.scatter(v,broadcast=True)
                (dxtr,dxte),muestras_dask,seg_dask=medir(
                    lambda:(
                        tfidf_paralelo(client,vectorizador_remoto,textos),
                        tfidf_paralelo(client,vectorizador_remoto,texto_test)
                    ),repeticiones)
                assert xtr.shape==dxtr.shape and xte.shape==dxte.shape
                dif1=xtr-dxtr
                dif2=xte-dxte
                assert dif1.nnz==0 and dif2.nnz==0, "Transformaciones difieren"
                baseline=DummyClassifier(strategy="most_frequent")
                baseline.fit(xtr,ytr)
                pred_baseline=baseline.predict(xte)
                classifier=LinearSVC(class_weight="balanced",random_state=42)
                start=time.perf_counter()
                classifier.fit(xtr,ytr)
                pred_svc=classifier.predict(xte)
                t_clf=time.perf_counter()-start
                assert np.array_equal(pred_svc,classifier.predict(dxte))
                pred_xgb=None
                pred_xgb_local=None
                txgb=None
                txgb_local=None
                t_svd=None
                if con_xgboost:
                    from sklearn.decomposition import TruncatedSVD
                    from sklearn.preprocessing import LabelEncoder
                    start=time.perf_counter()
                    svd=TruncatedSVD(n_components=32,n_iter=3,random_state=42)
                    ztr=np.asarray(svd.fit_transform(xtr),dtype="float32")
                    zte=np.asarray(svd.transform(xte),dtype="float32")
                    t_svd=time.perf_counter()-start
                    le=LabelEncoder().fit(ETIQUETAS)
                    ynum=le.transform(ytr)
                    # Control comparable: MISMO XGBoost, mismos datos SVD,
                    # semillas, arboles, rondas e hiperparametros.
                    # 2 threads locales vs 2 workers x 1 thread distribuido.
                    nombres_svd=[f"svd_{i:02d}" for i in range(ztr.shape[1])]
                    dl=xgb.DMatrix(ztr,label=ynum,feature_names=nombres_svd)
                    dt=xgb.DMatrix(zte,feature_names=nombres_svd)
                    params={
                        "objective":"multi:softprob","num_class":len(le.classes_),
                        "tree_method":"hist","max_depth":4,"eta":0.15,
                        "nthread":2,"seed":42,
                    }
                    start=time.perf_counter()
                    booster_local=xgb.train(params,dl,num_boost_round=rondas)
                    pred_xgb_local=le.inverse_transform(
                        np.argmax(booster_local.predict(dt),axis=1)
                    )
                    txgb_local=time.perf_counter()-start
                    pred_idx,txgb,parts=entrenar_xgb_distribuido(
                        client,ztr,ynum,zte,le.classes_,rondas
                    )
                    pred_xgb=le.inverse_transform(pred_idx)
                metricas={
                    "mayoritaria":calidad(yte,pred_baseline),
                    "tfidf_linearsvc":calidad(yte,pred_svc),
                }
                if pred_xgb is not None:
                    metricas["tfidf_svd_xgboost_local"]=calidad(yte,pred_xgb_local)
                    metricas["tfidf_svd_xgboost_dask"]=calidad(yte,pred_xgb)
                res={
                    "n_train":n,"n_test_fijo":len(test),
                    "test_sha256_ids":test_hash,"train_sha256_ids":huellas_ids(tr.id),
                    "n_particiones_tfidf":(n+len(test)+CHUNK-1)//CHUNK,
                    "vocabulario":len(v.vocabulary_),
                    "segundos_vocabulario_local":round(t_fit_vocab,4),
                    "segundos_transformacion_local_repeticiones":muestras_loc,
                    "segundos_transformacion_dask_repeticiones":muestras_dask,
                    "segundos_transformacion_local_mediana":seg_local,
                    "segundos_transformacion_dask_mediana":seg_dask,
                    "segundos_fit_predict_linearsvc":round(t_clf,4),
                    "segundos_svd":round(t_svd,4) if t_svd is not None else None,
                    "segundos_xgboost_local_fit_predict":round(txgb_local,4) if txgb_local is not None else None,
                    "segundos_xgboost_dask_fit":round(txgb,4) if txgb is not None else None,
                    "metricas":metricas,
                    "f1_por_clase":classification_report(
                        yte,pred_svc,labels=list(ETIQUETAS),
                        output_dict=True,zero_division=0
                    ),
                    "matriz_confusion":confusion_matrix(
                        yte,pred_svc,labels=list(ETIQUETAS)).tolist(),
                    "n_clases_presentes_train":len(set(ytr)),
                    "distribucion_train":dict(Counter(ytr)),
                }
                datos["resultados"].append(res)
                (SALIDA/f"justo_{n}.json").write_text(
                    json.dumps(res,ensure_ascii=False,indent=2),encoding="utf-8")
                print("RESULTADO_JUSTO_"+str(n)+" "+json.dumps({
                    "train":n,"test":len(test),"local":seg_local,"dask":seg_dask,
                    "f1_svc":metricas["tfidf_linearsvc"]["f1_macro"],
                    "f1_xgb":metricas.get("tfidf_svd_xgboost_dask",{}).get("f1_macro"),
                    "tiempo_xgb_local":round(txgb_local,4) if txgb_local is not None else None,
                    "tiempo_xgb_dask":round(txgb,4) if txgb is not None else None,
                }),flush=True)
    datos["equipo"]["segundos_total"]=round(time.perf_counter()-t0,3)
    archivo=SALIDA/"benchmark_50k_test_fijo.json"
    archivo.write_text(json.dumps(datos,ensure_ascii=False,indent=2),encoding="utf-8")
    print("BENCHMARK_COMPLETO "+json.dumps({
        "muestras":list(sizes),"test_sha256":test_hash,
        "segundos_total":datos["equipo"]["segundos_total"],
        "archivo":str(archivo),
    }),flush=True)
    return datos


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--sizes",nargs="+",type=int,default=list(TAMANOS))
    p.add_argument("--workers",type=int,default=2)
    p.add_argument("--repeticiones",type=int,default=3)
    p.add_argument("--rondas",type=int,default=20)
    p.add_argument("--sin-xgboost",action="store_true")
    a=p.parse_args()
    ejecutar(a.sizes,a.workers,a.repeticiones,a.rondas,not a.sin_xgboost)


if __name__=="__main__":
    main()
