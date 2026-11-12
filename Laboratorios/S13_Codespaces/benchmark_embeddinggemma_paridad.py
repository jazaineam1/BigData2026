"""EmbeddingGemma2: misma inferencia /api/embed con y sin orquestación Dask.

Prueba real sobre los mismos textos y el mismo Ollama 270m.
Dos workers que llaman al MISMO servidor no crean dos GPUs o dos modelos.
Extrapolaciones 1k/10k/20k/50k etiquetadas, no medidas en esos tamaños.
"""
from __future__ import annotations
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from dask.distributed import Client, LocalCluster

from medir_embeddinggemma2 import embed
from benchmark_unspsc_tfidf_dask import SALIDA, texto_limpio

ROOT=Path(__file__).resolve().parents[2]
CSV=ROOT/"Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv"

def inferir_lote(endpoint, model, chunk):
    start=time.perf_counter()
    secs, dimension, body=embed(endpoint, model, chunk, timeout=600)
    if dimension!=768:
        raise RuntimeError(f"Embedding inesperado: {dimension}, esperado 768.")
    return (np.asarray(body["embeddings"],dtype=np.float32),
            time.perf_counter()-start)

def medir(n=16, batch=4, model="embeddinggemma-2:270m",
          endpoint="http://127.0.0.1:11434"):
    if n < 4 or n % batch:
        raise ValueError("n debe ser múltiplo de batch y al menos 4")
    tabla=pd.read_csv(CSV,
        usecols=["nombre_del_procedimiento","descripci_n_del_procedimiento"],
        dtype=str,nrows=1000,keep_default_na=False)
    textos=[
        texto_limpio(t,d)[:1200]
        for t,d in zip(tabla["nombre_del_procedimiento"],
                       tabla["descripci_n_del_procedimiento"])
    ]
    textos=[t for t in textos if len(t)>30][:n]
    if len(textos)!=n:
        raise RuntimeError("No hay suficiente texto SECOP para piloto.")
    chunks=[textos[i:i+batch] for i in range(0,n,batch)]
    warm,dims,_=embed(endpoint,model,textos[:1],timeout=600)
    t0=time.perf_counter()
    baseline=[inferir_lote(endpoint,model,part) for part in chunks]
    t_local=time.perf_counter()-t0
    t0=time.perf_counter()
    with LocalCluster(n_workers=2,threads_per_worker=1,processes=True,
                      memory_limit="2GiB",dashboard_address=None) as cl:
        with Client(cl) as client:
            t_cluster=time.perf_counter()-t0
            t1=time.perf_counter()
            futures=[
                client.submit(inferir_lote,endpoint,model,part,pure=False)
                for part in chunks
            ]
            parallel=client.gather(futures)
            t_dask=time.perf_counter()-t1
    A=np.vstack([row[0] for row in baseline])
    B=np.vstack([row[0] for row in parallel])
    error=float(np.max(np.abs(A-B)))
    if not np.allclose(A,B,rtol=1e-4,atol=1e-5):
        raise AssertionError(f"Embeddings distintos entre local/Dask: {error}")
    result={
        "fuente":"SECOP prueba_chunk_0000000.csv", "n_medido":n,
        "batch":batch,"modelo":model,"dimensiones":dims,
        "mismo_servicio_ollama":endpoint,
        "tiempo_carga_inicial_s":round(warm,3),
        "tiempo_inferencia_secuencial_s":round(t_local,3),
        "tiempo_inferencia_dask_s":round(t_dask,3),
        "tiempo_crear_cluster_dask_s":round(t_cluster,3),
        "max_error_embedd_local_dask":error,
        "local_y_dask_mismos_vectores":True,
        "local_y_dask_mismo_modelo":True,
        "proyecciones_no_mediciones": {
            str(size): {
                "secuencial_h": round((t_local/n)*size/3600,3),
                "dask_h": round((t_dask/n)*size/3600,3),
            } for size in [1000,10000,20000,50000]
        },
        "advertencia":(
            "EXTRAPOLACION lineal: no garantiza rendimiento para 50k. "
            "Ollama es un único servidor en la misma CPU; "
            "dos workers Dask no duplican capacidad. "
            "Se midió sólo n pequeño, no F1 de clasificación para 50k."
        ),
    }
    SALIDA.mkdir(parents=True,exist_ok=True)
    (SALIDA/"embeddinggemma_paridad_piloto.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print("EMBEDDINGGEMMA_PILOTO "+json.dumps(result,ensure_ascii=False),
          flush=True)
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--n",type=int,default=16)
    p.add_argument("--batch",type=int,default=4)
    p.add_argument("--model",default="embeddinggemma-2:270m")
    p.add_argument("--endpoint",default="http://127.0.0.1:11434")
    a=p.parse_args()
    medir(a.n,a.batch,a.model,a.endpoint)
