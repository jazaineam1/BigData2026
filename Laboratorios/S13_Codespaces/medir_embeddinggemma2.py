"""Mide EmbeddingGemma 2 REALMENTE en tu Ollama; estima 1k/10k/20k.

NO hace llamadas a APIs pagadas, NO descarga el modelo automaticamente.
Para clasificacion UNSPSC usar la etiqueta como verdad y el embedding como X.
Dask solo aceleraria esto si hay servidores de inferencia independientes.
"""
from __future__ import annotations

import argparse
import json
import statistics
import time
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv"


def embed(endpoint, model, batch, timeout):
    payload = {
        "model": model, "input": batch,
        "keep_alive": "10m",
        "truncate": True,
    }
    req = urllib.request.Request(
        endpoint.rstrip("/") + "/api/embed",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    inicio = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as res:
        body = json.load(res)
    segundos = time.perf_counter() - inicio
    e = body.get("embeddings", [])
    if len(e) != len(batch):
        raise RuntimeError("Ollama no devolvió una representación por documento.")
    dimensiones = {len(v) for v in e}
    if len(dimensiones) != 1:
        raise RuntimeError("Dimensión de embedding inconsistente.")
    return segundos, dimensiones.pop(), body


def medir(model="embeddinggemma-2:270m", endpoint="http://127.0.0.1:11434",
          n=48, lote=4, rondas=2, timeout=180):
    if not CSV.exists():
        raise FileNotFoundError("Primero abre el repositorio BigData2026 con sus datos.")
    tabla = pd.read_csv(CSV, usecols=["descripci_n_del_procedimiento"],
                        dtype=str, nrows=max(n, 50)).fillna("")
    textos = [str(x)[:1200] for x in tabla["descripci_n_del_procedimiento"]
              if len(str(x).strip()) >= 20][:n]
    if len(textos) < n:
        raise RuntimeError(f"Sólo hay {len(textos)} textos válidos.")
    print("Modelo Ollama:", model)
    print("Textos reales:", len(textos), "caracteres medios:",
          round(statistics.mean(map(len, textos)), 1))
    print("Calentamiento (no entra en la tasa):")
    inicio = time.perf_counter()
    warm, dim, _ = embed(endpoint, model, textos[:1], timeout)
    print("Carga + primera inferencia: {:.2f} s, dimensiones: {}".format(
        time.perf_counter()-inicio, dim))

    muestras = []
    for i in range(rondas):
        for start in range(0, len(textos), lote):
            bloque = textos[start:start+lote]
            t, dimensiones, resp = embed(endpoint, model, bloque, timeout)
            muestras.append({"textos":len(bloque), "segundos":t,
                             "dimensiones":dimensiones,
                             "duracion_api_s":resp.get("total_duration", 0)/1e9})
            print("Lote", start//lote+1, "ronda", i+1, ":",len(bloque),
                  "textos en", round(t,3),"s")
    n_doc = sum(m["textos"] for m in muestras)
    total = sum(m["segundos"] for m in muestras)
    tasa = n_doc / total
    print("\n=== RENDIMIENTO MEDIDO EN ESTA MAQUINA ===")
    print("textos/s:",round(tasa,3), "lote:", lote,
          "dimensiones:",dim)
    print("El arranque/carga del modelo no está incluido en la tasa.")
    for size in [1000,10000,20000]:
        secs = size / tasa
        print(f"{size:,} documentos: {secs/60:.1f} min "
              f"({secs/3600:.2f} h), extrapolación lineal, NO medición")
    return {"modelo":model,"lote":lote,"muestra":n_doc,
            "segundos":total, "textos_por_segundo":tasa,
            "dimension":dim, "arranque_medido_s":warm,
            "estimaciones_segundos":{str(n):n/tasa for n in [1000,10000,20000]},
            "nota":"Extrapolaciones no incluyen cambios por memoria, contención o contexto largo."}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model",default="embeddinggemma-2:270m")
    p.add_argument("--endpoint",default="http://127.0.0.1:11434")
    p.add_argument("--n",type=int,default=48)
    p.add_argument("--lote",type=int,default=4)
    p.add_argument("--rondas",type=int,default=2)
    args=p.parse_args()
    try:
        medir(model=args.model,endpoint=args.endpoint,n=args.n,
              lote=args.lote,rondas=args.rondas)
    except urllib.error.HTTPError as e:
        raise SystemExit(
            f"Error Ollama {e.code}. Comprueba que el modelo esté instalado: "
            f"ollama pull {args.model}. Este script no lo descarga."
        ) from e
    except urllib.error.URLError as e:
        raise SystemExit(
            "No conecta con Ollama local. Comprueba: systemctl status ollama "
            "y curl http://127.0.0.1:11434/api/tags"
        ) from e
