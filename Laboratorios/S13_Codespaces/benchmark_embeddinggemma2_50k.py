"""Benchmark EmbeddingGemma 2: MISMO modelo y MISMO test para 1k..50k.

pilot: inferencia REAL sobre 32 textos del test fijo; estima tiempos,
NO inventa F1.
full: embeddings 60k (50k train + 10k test) almacenados SQLite,
entrena el mismo LinearSVC para 1k,10k,20k,50k sin re-inferir en re-runs.
Una sola Ollama CPU no se acelera por añadir workers de Dask.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
from sklearn.metrics import balanced_accuracy_score, f1_score
from sklearn.preprocessing import Normalizer
from sklearn.svm import LinearSVC

from benchmark_50k_test_fijo import generar_conjuntos, ETIQUETAS, SALIDA
from clasificar_unspsc_embeddinggemma2 import extraer_con_cache, solicitar_ollama

DEFAULT_MODEL="embeddinggemma-2:270m"
SIZES=(1000,10000,20000,50000)


def prueba_real_piloto(endpoint,model,limit=32,batch=4):
    t0=time.perf_counter()
    pool,test,orden,meta=generar_conjuntos()
    texts=test.texto.iloc[:limit].tolist()
    assert len(texts)==limit
    # Calentamiento EXCLUIDO de las medidas de inferencia estable.
    t1=time.perf_counter()
    _=solicitar_ollama(endpoint,model,texts[:1])
    calentamiento=time.perf_counter()-t1
    muestras=[]
    for pos in range(0,len(texts),batch):
        lote=texts[pos:pos+batch]
        inicio=time.perf_counter()
        vec=solicitar_ollama(endpoint,model,lote)
        t=time.perf_counter()-inicio
        muestras.append({
            "n":len(lote),"segundos":round(t,4),
            "dim":int(vec.shape[1]),"caracteres":sum(len(x) for x in lote),
        })
        print(f"LOTE_REAL {pos//batch+1} textos={len(lote)} seg={t:.3f}",flush=True)
    total=sum(r["segundos"] for r in muestras)
    tasa=len(texts)/total
    datos={
        "modo":"piloto_no_F1","modelo":model,
        "endpoint":"Ollama local en runner/HP, segun maquina usada",
        "textos_reales_medidos":len(texts),
        "dimension":768,"calentamiento_segundos":round(calentamiento,4),
        "tasa_textos_segundo":round(tasa,5),
        "lotes":muestras,
        "segundos_lectura_300k":round(t1-t0,3),
        "estimaciones_carga_completa":{
            # La inferencia del test fijo de 10k tambien cuesta tiempo,
            # por lo que siempre sumar 10k documentos.
            str(n):{
                "documentos_totales":n+len(test),
                "horas_estimadas":round((n+len(test))/tasa/3600,3),
            }
            for n in SIZES
        },
        "advertencia":"Extrapolacion lineal desde 32 textos. No se ha inferido "
        "sobre 60k ni medido F1 EmbeddingGemma, y no garantiza misma tasa "
        "con textos diferentes o al ejecutarse en HP.",
    }
    SALIDA.mkdir(exist_ok=True,parents=True)
    (SALIDA/"embgemma2_piloto_real.json").write_text(
        json.dumps(datos,ensure_ascii=False,indent=2),encoding="utf-8",
    )
    print("PILOTO_EMBEDDINGGEMMA "+json.dumps(datos,ensure_ascii=False),flush=True)
    return datos


def evaluacion_full(endpoint,model,batch=4,sizes=SIZES):
    pool,test,orden,meta=generar_conjuntos()
    t0=time.perf_counter()
    # Incluye TODOS los registros del test fijo y los 50k de train;
    # con cache SQLite se reanuda desde cualquier lote confirmado.
    all_texts=pool.texto.tolist()+test.texto.tolist()
    emb,stats=extraer_con_cache(all_texts,model,endpoint,batch)
    norm=Normalizer()
    z=norm.fit_transform(emb)
    zpool=z[:len(pool)]
    ztest=z[len(pool):]
    out={"modelo":model,"n_test_fijo":len(test),"n_entrenamiento_max":len(pool),
         "mismo_test":True,"metodo":"EmbeddingGemma 2 + LinearSVC balanced",
         "cache":stats,"resultados":[]}
    for n in sizes:
        indices=orden[:n]
        clf=LinearSVC(class_weight="balanced",random_state=42)
        start=time.perf_counter()
        clf.fit(zpool[indices],pool.etiqueta.iloc[indices].tolist())
        pred=clf.predict(ztest)
        train_time=time.perf_counter()-start
        yte=test.etiqueta.tolist()
        result={"n_train":n,"n_test":len(test),
                "f1_macro":round(float(f1_score(
                    yte,pred,average="macro",labels=list(ETIQUETAS),
                    zero_division=0)),5),
                "balanced_accuracy":round(float(
                    balanced_accuracy_score(yte,pred)),5),
                "segundos_fit_predict":round(train_time,4)}
        out["resultados"].append(result)
        print("RESULTADO_EMBGEMMA_"+str(n)+" "+json.dumps(result),flush=True)
    out["segundos_total_con_cache"]=round(time.perf_counter()-t0,3)
    SALIDA.mkdir(exist_ok=True,parents=True)
    (SALIDA/"embeddinggemma2_50k_test_fijo.json").write_text(
        json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8",
    )
    return out


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--modo",choices=["piloto","full"],default="piloto")
    ap.add_argument("--endpoint",default="http://127.0.0.1:11434")
    ap.add_argument("--model",default=DEFAULT_MODEL)
    ap.add_argument("--n-piloto",type=int,default=32)
    ap.add_argument("--batch",type=int,default=4)
    ap.add_argument("--sizes",nargs="+",type=int,default=list(SIZES))
    args=ap.parse_args()
    if args.modo=="piloto":
        prueba_real_piloto(args.endpoint,args.model,args.n_piloto,args.batch)
    else:
        if max(args.sizes)>50000:
            raise ValueError("50k es el máximo del universo entrenable")
        evaluacion_full(args.endpoint,args.model,args.batch,args.sizes)
