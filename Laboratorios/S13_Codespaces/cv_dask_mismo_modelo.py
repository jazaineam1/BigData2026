"""Caso profesional donde Dask puede ayudar: validación cruzada en paralelo.

Mismo TF-IDF, LinearSVC y particiones de CV en TODAS las alternativas:
1. Secuencial: 3 modelos uno detrás del otro.
2. Multiproceso local: mismo trabajo, joblib con 2 workers.
3. Dask Distributed: mismo trabajo, 2 workers, sin cambiar modelo.
4. Opcional Dask 4 workers: en máquina con >=4 CPU.

Esto DISTRIBUYE ENTRENAMIENTOS INDEPENDIENTES DE LOS FOLDS,
NO entrena internamente un solo LinearSVC.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import numpy as np
from dask.distributed import Client, LocalCluster
from joblib import Parallel, delayed
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.svm import LinearSVC

from benchmark_50k_test_fijo import generar_conjuntos, SALIDA, ETIQUETAS


def entrenar_un_fold(textos, etiquetas, idx_entrenar, idx_validar):
    """Una tarea de ML totalmente independiente y reproducible."""
    x_train=[textos[i] for i in idx_entrenar]
    x_test=[textos[i] for i in idx_validar]
    y_train=[etiquetas[i] for i in idx_entrenar]
    y_test=[etiquetas[i] for i in idx_validar]
    # El TF-IDF se ajusta SOLO sobre el fold de entrenamiento:
    # no hay fuga de vocabulario del fold de validación.
    modelo=make_pipeline(
        TfidfVectorizer(max_features=6000,ngram_range=(1,2),min_df=2,
                        max_df=0.98,sublinear_tf=True,
                        strip_accents="unicode",dtype=np.float32),
        LinearSVC(class_weight="balanced",random_state=42),
    )
    modelo.fit(x_train,y_train)
    pred=modelo.predict(x_test)
    return round(float(f1_score(
        y_test,pred,average="macro",labels=list(ETIQUETAS),zero_division=0)),6)


def medir_local(textos,y,folds,n_jobs):
    inicio=time.perf_counter()
    if n_jobs==1:
        score=[entrenar_un_fold(textos,y,tr,va) for tr,va in folds]
    else:
        score=Parallel(n_jobs=n_jobs,backend="loky")(
            delayed(entrenar_un_fold)(textos,y,tr,va) for tr,va in folds
        )
    return score,round(time.perf_counter()-inicio,4)


def medir_distribuido(client,textos,y,folds):
    t0=time.perf_counter()
    # hash=False evita colisiones de llaves cuando se repite el benchmark.
    texts_fut=client.scatter(textos,broadcast=True,hash=False)
    y_fut=client.scatter(y,broadcast=True,hash=False)
    trabajos=[
        client.submit(entrenar_un_fold,texts_fut,y_fut,tr,va,pure=False)
        for tr,va in folds
    ]
    scores=client.gather(trabajos)
    return scores,round(time.perf_counter()-t0,4)


def ejecutar(sizes=(1000,10000,20000,50000),n_cv=3,workers=2):
    if workers < 2 or n_cv < 3:
        raise ValueError("Se requieren al menos dos workers y tres folds")
    pool,test,orden,proveniencia=generar_conjuntos()
    salida={"procedimiento":"3-fold TF-IDF/LinearSVC mismos ejemplos por fold",
            "folds":n_cv,"workers":workers,"cpu_logicos":os.cpu_count(),
            "test_fijo_externo_no_usado_en_cv":len(test),
            "modelo_constante":True,"resultados":[]}
    with LocalCluster(n_workers=workers,threads_per_worker=1,processes=True,
                      memory_limit="1.7GiB",dashboard_address=":8787") as cl:
        with Client(cl) as client:
            for n in sizes:
                tab=pool.iloc[orden[:n]]
                textos=tab.texto.tolist()
                y=tab.etiqueta.tolist()
                splitter=StratifiedKFold(n_splits=n_cv,shuffle=True,random_state=42)
                folds=[(tr.tolist(),va.tolist()) for tr,va in
                       splitter.split(textos,y)]
                scores_1,t1=medir_local(textos,y,folds,n_jobs=1)
                scores_2,t2=medir_local(textos,y,folds,n_jobs=workers)
                scores_d,td=medir_distribuido(client,textos,y,folds)
                if not (scores_1==scores_2==scores_d):
                    raise AssertionError(
                        f"Los folds/modelo dejaron de coincidir: {scores_1} "
                        f"{scores_2} {scores_d}"
                    )
                m={"train":n,"mismos_folds":True,"scores":scores_1,
                   "f1_macro_cv_promedio":round(float(np.mean(scores_1)),5),
                   "segundos_secuencial":t1,
                   "segundos_local_multiproceso":t2,
                   "segundos_dask_distributed":td,
                   "aceleracion_dask_frente_a_secuencial":round(t1/td,3) if td else None,
                   "aceleracion_dask_frente_a_multiproceso":round(t2/td,3) if td else None}
                salida["resultados"].append(m)
                print("CV_REAL_"+str(n)+" "+json.dumps(m),flush=True)
    SALIDA.mkdir(parents=True,exist_ok=True)
    (SALIDA/"cv_linearsvc_local_vs_dask.json").write_text(
        json.dumps(salida,indent=2,ensure_ascii=False),encoding="utf-8")
    return salida


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--sizes",nargs="+",type=int,default=[1000,10000,20000,50000])
    p.add_argument("--cv",type=int,default=3)
    p.add_argument("--workers",type=int,default=2)
    a=p.parse_args()
    ejecutar(a.sizes,a.cv,a.workers)
