"""Ensayo 1.000 SECOP COMPLETOS: TF-IDF frente a EmbeddingGemma 2 REAL.

Mismo texto, misma variable objetivo, mismo split 800/200, mismo LinearSVC,
mismos hiperparametros. EmbeddingGemma se usa como encoder congelado.
No inventa resultados: falla si Ollama no está disponible o faltan vectores.
"""
from __future__ import annotations
import argparse
import json
import time
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import balanced_accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.preprocessing import Normalizer
from sklearn.svm import LinearSVC

from benchmark_unspsc_tfidf_dask import (
    leer_muestra, seleccion_n, ETIQUETAS, SALIDA,
)
from clasificar_unspsc_embeddinggemma2 import extraer_con_cache

def puntuar(y,pred):
    return {
        "f1_macro":round(float(f1_score(
            y,pred,average="macro",labels=list(ETIQUETAS),zero_division=0)),5),
        "balanced_accuracy":round(float(balanced_accuracy_score(y,pred)),5),
        "accuracy":round(float(np.mean(np.asarray(y)==np.asarray(pred))),5),
        "reporte_por_clase":classification_report(
            y,pred,labels=list(ETIQUETAS),zero_division=0,output_dict=True),
        "matriz_confusion":confusion_matrix(y,pred,labels=list(ETIQUETAS)).tolist()
    }

def ejecutar(model="embeddinggemma-2:270m",endpoint="http://127.0.0.1:11434",batch=4):
    start=time.perf_counter()
    tabla,meta=leer_muestra(1000)
    train,test=seleccion_n(tabla,1000)
    assert len(train)==800 and len(test)==200
    textos_train=train.texto.tolist()
    textos_test=test.texto.tolist()
    ytrain=train.etiqueta.tolist()
    ytest=test.etiqueta.tolist()
    args={"class_weight":"balanced","random_state":42}
    # Exactamente el mismo clasificador entrenado en cada representacion.
    t0=time.perf_counter()
    tfidf=TfidfVectorizer(
        max_features=6000,ngram_range=(1,2),min_df=2,
        max_df=0.98,sublinear_tf=True,strip_accents="unicode",dtype=np.float32
    )
    xtr=tfidf.fit_transform(textos_train)
    xte=tfidf.transform(textos_test)
    tvec=time.perf_counter()-t0
    t0=time.perf_counter()
    clf_tfidf=LinearSVC(**args)
    clf_tfidf.fit(xtr,ytrain)
    pt=clf_tfidf.predict(xte)
    t_fit_tfidf=time.perf_counter()-t0
    tfidf_metricas=puntuar(ytest,pt)
    print("TFIDF_REAL_1000 "+json.dumps({
        "f1_macro":tfidf_metricas["f1_macro"],
        "segundos_vectorizacion":round(tvec,3),
        "segundos_fit":round(t_fit_tfidf,3),
    }),flush=True)
    # Inferencia de los 1000 textos AUTENTICOS; SQLite para reanudar.
    start_embed=time.perf_counter()
    vecs,stats=extraer_con_cache(textos_train+textos_test,model,endpoint,batch)
    tiempo_embedding=time.perf_counter()-start_embed
    assert vecs.shape==(1000,768),vecs.shape
    vecs=Normalizer(copy=True).fit_transform(vecs)
    t0=time.perf_counter()
    clf=LinearSVC(**args)
    clf.fit(vecs[:800],ytrain)
    pe=clf.predict(vecs[800:])
    t_fit_embedding=time.perf_counter()-t0
    emetricas=puntuar(ytest,pe)
    SALIDA.mkdir(exist_ok=True,parents=True)
    resultado={
        "nota":"1000 fichas SECOP reales, ni una estimacion para F1 ni tiempo.",
        "modelo_encoder":model,"clasificador_ambas_ramas":"LinearSVC",
        "hiperparametros_clasificador":args,
        "train":800,"test":200,"mismo_corte_temporal":True,
        "fuentes":meta,"etiquetas":list(ETIQUETAS),
        "tfidf":{
            "metricas":tfidf_metricas,
            "segundos_vectorizar_train_test":round(tvec,3),
            "segundos_fit_predict":round(t_fit_tfidf,3),
            "dimensiones":xtr.shape[1]},
        "embeddinggemma2":{
            "metricas":emetricas,
            "segundos_embeddings_total_con_cache":round(tiempo_embedding,3),
            "segundos_fit_predict":round(t_fit_embedding,3),
            "dimensiones":768,"estadisticas_ollama":stats},
        "segundos_todo_incluida_lectura_csv":round(time.perf_counter()-start,3),
    }
    (SALIDA/"tfidf_vs_embeddinggemma2_1000_REAL.json").write_text(
        json.dumps(resultado,indent=2,ensure_ascii=False),encoding="utf-8"
    )
    print("COMPARACION_REAL_1000 "+json.dumps({
        "f1_tfidf":tfidf_metricas["f1_macro"],
        "f1_embeddinggemma2":emetricas["f1_macro"],
        "s_tfidf":round(tvec+t_fit_tfidf,3),
        "s_embeddinggemma2":round(tiempo_embedding+t_fit_embedding,3),
        "n_emb_real":stats["nuevos"]},
        ensure_ascii=False),flush=True)
    return resultado

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--model",default="embeddinggemma-2:270m")
    p.add_argument("--endpoint",default="http://127.0.0.1:11434")
    p.add_argument("--batch",type=int,default=4)
    args=p.parse_args()
    ejecutar(args.model,args.endpoint,args.batch)
