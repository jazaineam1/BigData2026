"""Embeddings reales EmbeddingGemma 2 por Ollama -> clasificador UNSPSC.

Separa temporalmente los mismos procesos SECOP que benchmark_unspsc_tfidf_dask.
NO entrena los pesos de Gemma: los usa como caracteristicas para LinearSVC.

Cache SQLite incremental: si se interrumpe al documento 450 se reanuda sin
recalcular los 450 vectores ya guardados. No requiere APIs pagadas.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import time
import urllib.request
from pathlib import Path

import numpy as np
from sklearn.metrics import f1_score, balanced_accuracy_score
from sklearn.preprocessing import Normalizer
from sklearn.svm import LinearSVC

from benchmark_unspsc_tfidf_dask import (
    SALIDA, ETIQUETAS, leer_muestra, seleccion_n,
)

DB = SALIDA / "cache_embeddinggemma2.sqlite3"


def solicitar_ollama(endpoint, model, textos, timeout=240):
    peticion = urllib.request.Request(
        endpoint.rstrip("/") + "/api/embed",
        data=json.dumps({
            "model": model, "input": textos,
            "truncate": True, "keep_alive": "10m",
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(peticion, timeout=timeout) as res:
        respuesta = json.load(res)
    vectores = np.asarray(respuesta["embeddings"], dtype=np.float32)
    if vectores.shape != (len(textos), 768):
        raise ValueError(f"Esperaba embeddings 768d para {len(textos)} textos; "
                         f"devolvió {vectores.shape}")
    if not np.isfinite(vectores).all():
        raise ValueError("El modelo devolvió valores no finitos.")
    return vectores


def clave(model, texto):
    return hashlib.sha256((model+"\n"+texto).encode("utf-8")).hexdigest()


def extraer_con_cache(textos, model, endpoint, batch_size, db_path=DB):
    """Reutiliza vectores por hash(modelo+texto), incluso entre runs."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as cx:
        cx.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                clave TEXT PRIMARY KEY,
                modelo TEXT NOT NULL,
                dimension INTEGER NOT NULL,
                vector BLOB NOT NULL
            )
        """)
        claves = [clave(model, t) for t in textos]
        por_calcular = []
        for i, k in enumerate(claves):
            if cx.execute("SELECT 1 FROM embeddings WHERE clave=?", (k,)).fetchone() is None:
                por_calcular.append(i)
        llamadas = 0
        segundos = 0.0
        for j in range(0, len(por_calcular), batch_size):
            indices = por_calcular[j:j+batch_size]
            start = time.perf_counter()
            bloque = solicitar_ollama(
                endpoint, model, [textos[i] for i in indices],
            )
            segundos += time.perf_counter()-start
            llamadas += 1
            cx.executemany(
                "INSERT OR REPLACE INTO embeddings (clave,modelo,dimension,vector) "
                "VALUES (?,?,?,?)",
                [(claves[i],model,768,vec.astype(np.float32).tobytes())
                 for i,vec in zip(indices,bloque)],
            )
            cx.commit()
            print(f"Calculados {min(j+batch_size,len(por_calcular))}/"
                  f"{len(por_calcular)} nuevos; cache {db_path}",flush=True)
        mat = []
        for k in claves:
            row = cx.execute(
                "SELECT dimension,vector FROM embeddings WHERE clave=?", (k,)
            ).fetchone()
            if not row or row[0]!=768:
                raise RuntimeError(f"Vector no encontrado o dimensión inválida: {k}")
            mat.append(np.frombuffer(row[1],dtype=np.float32).copy())
        return np.vstack(mat), {
            "solicitados": len(textos), "nuevos": len(por_calcular),
            "reutilizados": len(textos)-len(por_calcular),
            "llamadas_api": llamadas, "segundos_embeddings_nuevos": round(segundos,3),
            "textos_por_segundo_medido": (
                round(len(por_calcular)/segundos,3) if segundos else None
            ),
        }


def entrenar(n, model, endpoint, batch_size):
    if n not in (1000,10000,20000):
        raise ValueError("n debe ser 1000, 10000 o 20000.")
    t0=time.perf_counter()
    tabla,_=leer_muestra(20000)
    train,test=seleccion_n(tabla,n)
    texts=train.texto.tolist()+test.texto.tolist()
    vecs, tiempos=extraer_con_cache(texts, model, endpoint, batch_size)
    transformador=Normalizer(copy=True)
    z=transformador.fit_transform(vecs)
    clf=LinearSVC(class_weight="balanced",random_state=42)
    clf.fit(z[:len(train)],train.etiqueta.tolist())
    pred=clf.predict(z[len(train):])
    y=test.etiqueta.tolist()
    metricas={
        "f1_macro":round(float(f1_score(
            y,pred,average="macro",labels=list(ETIQUETAS),zero_division=0)),4),
        "balanced_accuracy":round(float(balanced_accuracy_score(y,pred)),4),
    }
    salida={
        "modelo":model, "n":n, "train":len(train), "test":len(test),
        "dimensiones":vecs.shape[1],
        "metrica_embeddings_linearsvc":metricas, "tiempos_ollama":tiempos,
        "segundos_pipeline_completo":round(time.perf_counter()-t0,3),
        "advertencia":"Embeddings INFERIDOS, no fine-tuning; mismo split temporal de TF-IDF.",
    }
    SALIDA.mkdir(parents=True,exist_ok=True)
    (SALIDA/f"embgemma_{n}.json").write_text(
        json.dumps(salida,ensure_ascii=False,indent=2),encoding="utf-8",
    )
    print(json.dumps(salida,ensure_ascii=False,indent=2))
    return salida


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--n",type=int,default=1000)
    p.add_argument("--model",default="embeddinggemma-2:270m")
    p.add_argument("--endpoint",default="http://127.0.0.1:11434")
    p.add_argument("--batch",type=int,default=4)
    args=p.parse_args()
    entrenar(args.n,args.model,args.endpoint,args.batch)
