"""Escala TF-IDF en una misma maquina de 4 CPU: local vs Dask 2 vs 4 workers.

MISMO vectorizador ajustado una sola vez, mismos 50.000 train y 10.000
test, tres repeticiones de transformacion. NO se cambia el modelo ni test.
No confundir 4 procesos del mismo runner con un cluster multinodo.
"""
from __future__ import annotations

import argparse
import json
import os
import time
import numpy as np
from dask.distributed import LocalCluster, Client
from scipy.sparse import vstack
from sklearn.feature_extraction.text import TfidfVectorizer
from benchmark_50k_test_fijo import generar_conjuntos, SALIDA, vectorizador
from benchmark_unspsc_tfidf_dask import transformar_bloque, chunks_lista


def transformar_dask(client, vec, textos):
    # Un future único por medición: nunca perder referencias del vectorizador.
    vf=client.scatter(vec,broadcast=True,hash=False)
    chunks=chunks_lista(textos,1000)
    jobs=[client.submit(transformar_bloque,vf,chunk,pure=False) for chunk in chunks]
    return vstack(client.gather(jobs),format="csr")


def medir(reps=3):
    if (os.cpu_count() or 0) < 4:
        raise RuntimeError("Benchmark 4 workers exige Codespace o runner de al menos 4 CPU lógicas.")
    pool,test,orden,meta=generar_conjuntos()
    train=pool.iloc[orden[:50000]]
    x=train.texto.tolist()+test.texto.tolist()
    vec=vectorizador()
    start=time.perf_counter()
    vec.fit(train.texto.tolist())
    fit_vocab=time.perf_counter()-start
    local=[]
    for _ in range(reps):
        t=time.perf_counter()
        referencia=vec.transform(x)
        local.append(time.perf_counter()-t)
    rows=[]
    for workers in [2,4]:
        t=time.perf_counter()
        with LocalCluster(n_workers=workers,threads_per_worker=1,
                          processes=True,memory_limit="1.7GiB",
                          dashboard_address=":8787") as cluster:
            with Client(cluster) as client:
                arranque=time.perf_counter()-t
                assert len(client.scheduler_info()["workers"])==workers
                mediciones=[]
                for _ in range(reps):
                    init=time.perf_counter()
                    visto=transformar_dask(client,vec,x)
                    mediciones.append(time.perf_counter()-init)
                    dif=referencia-visto
                    assert referencia.shape==visto.shape and dif.nnz==0
        rows.append({"workers":workers,"segundos_arranque":round(arranque,4),
                     "repeticiones":[round(z,4) for z in mediciones],
                     "mediana":round(float(np.median(mediciones)),4)})
        print("WORKERS_"+str(workers)+" "+json.dumps(rows[-1]),flush=True)
    out={"n_train":50000,"n_test":10000,"misma_matriz":True,
         "mismo_modelo_vectorizador":True,"cpu_logicos":os.cpu_count(),
         "nodos_fisicos":1,"t_vocab_fit":round(fit_vocab,4),
         "local":{"repeticiones":[round(z,4) for z in local],
                  "mediana":round(float(np.median(local)),4)},
         "dask":rows,"nota":"Dask 4workers no implica 4 máquinas; "
         "mediciones excluyen lectura, creación del clúster y fit de vocabulario."}
    SALIDA.mkdir(parents=True,exist_ok=True)
    (SALIDA/"workers_2_vs_4_50k.json").write_text(
        json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print("TRABAJO_MISMO_"+json.dumps(out,ensure_ascii=False),flush=True)
    return out


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--reps",type=int,default=3)
    args=p.parse_args()
    medir(reps=args.reps)
