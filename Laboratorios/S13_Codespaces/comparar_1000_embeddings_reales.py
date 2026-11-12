"""Comparación 1.000 procesos REALES: TF-IDF vs EmbeddingGemma 2 en misma CPU.

Siempre mismas 800 train + 200 test SECOP, mismas etiquetas, mismo LinearSVC
class_weight balanced/random_state 42. Sin extrapolaciones ni F1 inventada.
Los embeddings se miden por lote, tienen cache y exigen completar 1000/1000.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import time
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score, balanced_accuracy_score, classification_report
from sklearn.preprocessing import Normalizer
from sklearn.svm import LinearSVC
from benchmark_unspsc_tfidf_dask import (leer_muestra, seleccion_n, ETIQUETAS, SALIDA)
from clasificar_unspsc_embeddinggemma2 import extraer_con_cache


def experimento(model="embeddinggemma-2:270m", endpoint="http://127.0.0.1:11434",
                lote=8):
    start=time.perf_counter()
    data,meta=leer_muestra(20000)
    train,test=seleccion_n(data,1000)
    assert len(train)==800 and len(test)==200
    assert not set(train.id)&set(test.id)
    xtrain=train.texto.tolist()
    xtest=test.texto.tolist()
    yt=train.etiqueta.tolist()
    ytest=test.etiqueta.tolist()
    vec=TfidfVectorizer(max_features=6000,ngram_range=(1,2),min_df=2,
                        max_df=0.98,sublinear_tf=True,strip_accents="unicode",
                        dtype=np.float32)
    s=time.perf_counter()
    tftrain=vec.fit_transform(xtrain)
    tftest=vec.transform(xtest)
    tf_seconds=time.perf_counter()-s
    clf=LinearSVC(class_weight="balanced",random_state=42)
    s=time.perf_counter()
    clf.fit(tftrain,yt)
    tfpred=clf.predict(tftest)
    tf_fit=time.perf_counter()-s
    salida_tf={
        "f1_macro":round(float(f1_score(
            ytest,tfpred,labels=list(ETIQUETAS),average="macro",zero_division=0)),5),
        "balanced_accuracy":round(float(balanced_accuracy_score(ytest,tfpred)),5),
        "segundos_vectorizacion":round(tf_seconds,4),
        "segundos_fit_predict":round(tf_fit,4),
        "features":int(tftrain.shape[1]),
    }
    print("TFIDF_REAL_1000 "+json.dumps(salida_tf),flush=True)
    s=time.perf_counter()
    matrices,meta_inferencia=extraer_con_cache(
        xtrain+xtest,model,endpoint,lote,
        db_path=SALIDA/"embgemma_1000_cache.sqlite3",
    )
    emb_seconds=time.perf_counter()-s
    assert matrices.shape==(1000,768),"No se procesaron 1000/1000 textos reales"
    arr=Normalizer().fit_transform(matrices)
    clf_emb=LinearSVC(class_weight="balanced",random_state=42)
    s=time.perf_counter()
    clf_emb.fit(arr[:800],yt)
    empred=clf_emb.predict(arr[800:])
    emb_fit=time.perf_counter()-s
    salida_emb={
        "f1_macro":round(float(f1_score(
            ytest,empred,labels=list(ETIQUETAS),average="macro",zero_division=0)),5),
        "balanced_accuracy":round(float(balanced_accuracy_score(ytest,empred)),5),
        "segundos_vectorizacion":round(emb_seconds,4),
        "segundos_fit_predict":round(emb_fit,4),
        "features":768,
        "cache":meta_inferencia,
    }
    res={
        "fuente":"20000 procesos muestreados del universo SECOP; mismos 1000 que benchmark anterior",
        "train":800,"test":200,"n_total":1000,
        "modelo_ollama":model,"misma_muestra_y_clasificador":True,
        "hardware":{"cpu_logicos":os.cpu_count(),"sistema":platform.platform()},
        "tfidf":salida_tf,"embeddinggemma2":salida_emb,
        "f1_por_clase_embeddinggemma":classification_report(
            ytest,empred,labels=list(ETIQUETAS),output_dict=True,zero_division=0),
        "f1_por_clase_tfidf":classification_report(
            ytest,tfpred,labels=list(ETIQUETAS),output_dict=True,zero_division=0),
        "segundos_total":round(time.perf_counter()-start,3),
        "no_estimaciones":True,
        "advertencia":"Se midieron 1000 embeddings de verdad, no se entrenaron pesos Gemma. "
        "Aún no se han generado embeddings para 10k/20k/50k.",
    }
    SALIDA.mkdir(parents=True,exist_ok=True)
    (SALIDA/"embgemma_vs_tfidf_1000_real.json").write_text(
        json.dumps(res,ensure_ascii=False,indent=2),encoding="utf-8")
    print("COMPARACION_1000_REAL "+json.dumps(res,ensure_ascii=False),flush=True)
    return res


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--model",default="embeddinggemma-2:270m")
    p.add_argument("--endpoint",default="http://127.0.0.1:11434")
    p.add_argument("--batch",type=int,default=8)
    args=p.parse_args()
    experimento(args.model,args.endpoint,args.batch)
