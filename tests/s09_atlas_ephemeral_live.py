#!/usr/bin/env python3
"""Smoke test REAL de Atlas Ephemeral, sin credenciales preexistentes.
No imprime conexión, contraseña, clusterId ni claimUrl. Crea datos ficticios.
"""
import os, secrets, time, sys
import requests
from pymongo import MongoClient, UpdateOne
from pymongo.operations import SearchIndexModel

API="https://cloud.mongodb.com/api/atlas/v2/unauth/ephemeralClusters:create"
def main():
    print("LIVE CHECK: solicitando clúster Atlas Ephemeral M0 (datos sintéticos).", flush=True)
    response=requests.post(API,
      headers={"Accept":"application/vnd.atlas.preview+json","Content-Type":"application/json"},
      json={"clusterName":"S09QA-"+secrets.token_hex(5)},timeout=50)
    if response.status_code==429:
        raise RuntimeError("Atlas API devolvió 429 (límite de creación). No se acredita ejecución remota.")
    response.raise_for_status()
    data=response.json()
    assert data["connectionString"].startswith("mongodb+srv://")
    assert data.get("claimUrl") and data.get("clusterId")
    print("LIVE CHECK: API 201; respuesta de clúster temporal recibida SIN mostrar credenciales.",flush=True)
    client=MongoClient(data["connectionString"],serverSelectionTimeoutMS=12000,connectTimeoutMS=8000)
    try:
        for attempt in range(20):
            try:
                client.admin.command("ping")
                break
            except Exception:
                if attempt==19:raise
                time.sleep(5)
        print("LIVE CHECK: ping Atlas real OK.",flush=True)
        db=client["clase_s09_demo"]
        col=db["secop_vectores"]
        batch="qa-"+secrets.token_hex(3)
        def vec(i):
            x=[0.0]*384;x[i]=1.0;return x
        docs=[
          {"_id":"QA1","id_proceso":"QA1","nombre_proceso":"Mantenimiento aeronaves","entidad":"A","lote":batch,"embedding":vec(0)},
          {"_id":"QA2","id_proceso":"QA2","nombre_proceso":"Licencias tecnología","entidad":"B","lote":batch,"embedding":vec(1)},
          {"_id":"QA3","id_proceso":"QA3","nombre_proceso":"Repuestos aviones","entidad":"A","lote":batch,"embedding":vec(0)}
        ]
        for _ in range(2):
            col.bulk_write([UpdateOne({"_id":d["_id"]},{"$set":d},upsert=True) for d in docs])
        assert col.count_documents({"lote":batch})==3
        print("LIVE CHECK: upsert repetido y conteo real 3 de 3.",flush=True)
        definition={"fields":[
           {"type":"vector","path":"embedding","numDimensions":384,"similarity":"cosine"},
           {"type":"filter","path":"lote"},{"type":"filter","path":"entidad"}]}
        col.create_search_index(model=SearchIndexModel(
           name="s09_vector_index",type="vectorSearch",definition=definition))
        ready=False
        for attempt in range(36):
            statuses=list(col.list_search_indexes("s09_vector_index"))
            ready=bool(statuses and statuses[0].get("queryable") is True)
            if ready:break
            time.sleep(5)
        if not ready:raise RuntimeError("Índice MongoDB no llegó a queryable=True dentro de 180s.")
        print("LIVE CHECK: índice real vectorSearch 384D queryable=True.",flush=True)
        pipeline=[{"$vectorSearch":{"index":"s09_vector_index","path":"embedding",
                    "queryVector":vec(0),"numCandidates":100,"limit":2,
                    "filter":{"lote":batch,"entidad":"A"}}},
                  {"$project":{"_id":0,"id_proceso":1,"entidad":1,"score":{"$meta":"vectorSearchScore"}}}]
        results=list(col.aggregate(pipeline,maxTimeMS=30000))
        assert results and all(r["entidad"]=="A" for r in results)
        assert all("score" in r for r in results)
        assert set(r["id_proceso"] for r in results)=={"QA1","QA3"}
        print("LIVE CHECK: $vectorSearch REAL devolvió Top-2 correcto, filtro y score.",flush=True)
        print("S09 ATLAS LIVE: OK · API → ping → upsert → índice → consulta.",flush=True)
    finally:
        client.close()
if __name__=="__main__":
    main()
