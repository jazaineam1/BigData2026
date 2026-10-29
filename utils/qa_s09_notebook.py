#!/usr/bin/env python3
"""QA S09: cuaderno sincronizado y pruebas offline para Atlas + respaldo local."""
import hashlib
import json
import re
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
from build_session9_notebook import build_notebook
nb=json.loads((ROOT/"Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb").read_text(encoding="utf-8"))
assert nb==build_notebook(), "Cuaderno y generador desincronizados"
assert len(nb["cells"])==21, "La ruta debía tener 21 celdas, no el apéndice antiguo de 48"
sources=["".join(c["source"]) for c in nb["cells"]]
def snippet(n): return sources[n-1]
assert "SECOP a MongoDB Atlas" in snippet(1)
assert "MODO_DEMO" in snippet(4) and "COLUMNA_ID" in snippet(4)
assert 'intfloat/multilingual-e5-small' in snippet(4)
assert "MAX_TOKENS" in snippet(6)
assert 'upsert=True' in snippet(10) and '"s09:"+LOTE' in snippet(10)
assert "CREAR_INDICE_EN_COLAB = True" in snippet(12), "La ruta personal crea el índice automáticamente"
# No basta mostrar un formulario vacío: el alumno necesita instrucciones de obtención.
for phrase in ("Atlas temporal automático", "Reclamar mi clúster", "Data Explorer",
               "Search & Vector Search", "0.0.0.0/0", "NO EJECUTADO ATLAS"):
    assert phrase in snippet(7), f"Guía del estudiante incompleta: {phrase}"
assert "sin contraseñas ni configuración de IP" in snippet(2)
assert 'MODO_ATLAS = "Atlas temporal automático"' in snippet(8), "Falta Atlas autónomo predeterminado"
assert "ephemeralClusters:create" in snippet(8) and "application/vnd.atlas.preview+json" in snippet(8)
assert '_s09_atlas_temporal_privado' in snippet(8) and "connectionString" in snippet(8)
assert "getpass" in snippet(8) and "MongoClient" in snippet(8)

assert "MongoDB Atlas real" in snippet(7)
assert "SearchIndexModel(" in snippet(12)
assert 'list_search_indexes(' in snippet(13) and 'queryable' in snippet(13)
assert '"$vectorSearch"' in snippet(15) and '"exact":True' in snippet(15)
assert "solapamiento_ann_enn_atlas" in snippet(16)
assert "s09_atlas_evidencia.json" in snippet(16)
assert "EJECUTAR_BENCHMARK = False" in snippet(21)
# La ruta SECOP curso no importa requests: conexión debe traer su propia dependencia.
import ast
connection_tree=ast.parse(snippet(8))
assert any(isinstance(n,ast.Import) and any(a.name=="requests" for a in n.names) for n in ast.walk(connection_tree)), "IP de conexión depende de importación condicional externa"
assert "LMSBridge" not in "\n".join(sources)
for i,c in enumerate(nb["cells"],1):
    if c["cell_type"]!="code":continue
    program="\n".join(l for l in sources[i-1].splitlines()
                      if not l.lstrip().startswith(("%","!")))
    compile(program,f"s09_cell_{i}.py","exec")

class ModeloFalso:
    """Sólo para QA offline: NO emula el rendimiento ni precisión de E5."""
    def encode(self,texts,normalize_embeddings=True,**_):
        vectors=[]
        for t in texts:
            v=np.zeros(384,dtype=np.float32)
            for word in re.findall(r"\w+",str(t).lower()):
                if word in ("query","passage"):continue
                j=int(hashlib.sha256(word.encode()).hexdigest()[:8],16)%384
                v[j]+=1
            norm=np.linalg.norm(v)
            vectors.append(v/norm if norm else v)
        return np.array(vectors,dtype=np.float32)

class Update:
    def __init__(self,where,change,upsert=False):
        self.where,self.change,self.upsert=where,change,upsert

class Index:
    def __init__(self,definition,name,type):
        self.definition,self.name,self.type=definition,name,type

class AtlasFalso:
    """Interfaz mínima de PyMongo. Resultados de prueba, NO Atlas real."""
    def __init__(self):
        self.rows={}
        self.idx=None
        self.query_params=[]
    def bulk_write(self,requests,ordered=False):
        for req in requests:
            assert req.upsert
            self.rows[req.where["_id"]]=req.change["$set"]
    def count_documents(self,filtro):
        return sum(all(doc.get(k)==v for k,v in filtro.items())
                   for doc in self.rows.values())
    def find_one(self,filtro,projection=None):
        return next((v for v in self.rows.values()
                     if all(v.get(k)==val for k,val in filtro.items())),None)
    def list_search_indexes(self,name=None):
        if self.idx is None:return []
        return [dict(name=self.idx.name,queryable=True,
                     latestDefinition=self.idx.definition)]
    def create_search_index(self,model):
        assert model.type=="vectorSearch"
        self.idx=model
        return model.name
    def aggregate(self,pipeline,maxTimeMS=None):
        stage=pipeline[0]["$vectorSearch"]
        self.query_params.append(stage)
        assert stage["path"]=="embedding" and len(stage["queryVector"])==384
        assert "lote" in stage["filter"] and stage["index"]=="s09_vector_index"
        assert not ("exact" in stage and "numCandidates" in stage)
        if not stage.get("exact"):
            assert stage["numCandidates"]>=stage["limit"]
        docs=[x for x in self.rows.values()
              if all(x.get(k)==v for k,v in stage["filter"].items())]
        q=np.array(stage["queryVector"])
        docs.sort(key=lambda x:float(np.array(x["embedding"])@q),reverse=True)
        return [dict(_id=x["_id"],id_proceso=x["id_proceso"],
                     nombre_proceso=x["nombre_proceso"],
                     entidad=x["entidad"],url_secop=x["url_secop"],
                     score=float(np.array(x["embedding"])@q))
                for x in docs[:stage["limit"]]]

with tempfile.TemporaryDirectory() as directory:
    import os
    before=os.getcwd()
    os.chdir(directory)
    try:
        sandbox={"__name__":"__main__"}
        source=snippet(4).replace(
            'MODO_DEMO = "SECOP curso · 120"',
            'MODO_DEMO = "Respaldo sintético · 6"')
        exec(compile(source,"load.py","exec"),sandbox)
        assert len(sandbox["corpus"])==6 and sandbox["corpus"]["id_proceso"].is_unique
        assert "SINTÉTICO" in sandbox["ORIGEN"]
        model=ModeloFalso()
        sandbox["modelo"]=model
        sandbox["embeddings"]=model.encode(
            ["passage: "+s for s in sandbox["corpus"]["texto_busqueda"]])
        sandbox.update(UpdateOne=Update,SearchIndexModel=Index,
                       INDEX_NAME="s09_vector_index",NOMBRE_BD="clase_s09_demo",
                       NOMBRE_COL="secop_vectores")
        # Respaldo: Atlas apagado, NumPy devuelve vecinos; JSON declara fallo remoto.
        sandbox.update(atlas_ok=False,atlas_cargado=False,indice_queryable=False)
        # El JSON del índice/variable definition nace en la celda 12, ANTES de la búsqueda.
        # Atlas apagado: debe crear el JSON sin intentar conectar ni crear índice remoto.
        exec(compile(snippet(12),"local_index_config.py","exec"),sandbox)
        assert Path("s09_indice_atlas_ui.json").exists()
        exec(compile(snippet(15),"local_search.py","exec"),sandbox)
        assert sandbox["resultados_atlas"].empty
        assert len(sandbox["resultados_numpy"])==5
        exec(compile(snippet(16),"local_evidence.py","exec"),sandbox)
        evidence=json.loads(Path("s09_atlas_evidencia.json").read_text())
        assert evidence["motor_ann_ejecutado"]=="NO EJECUTADO"
        assert evidence["motor_enn_ejecutado"]=="NO EJECUTADO"
        assert evidence["respaldo"].startswith("NumPy exacto LOCAL")
        assert not evidence["resultados_ann_atlas"]
        index_ui=json.loads(Path("s09_indice_atlas_ui.json").read_text())
        pipeline_ui=json.loads(Path("s09_pipeline_atlas_ui.json").read_text())
        assert index_ui["fields"][0]["path"]=="embedding"
        assert index_ui["fields"][0]["numDimensions"]==384
        assert len(pipeline_ui)==2
        assert len(pipeline_ui[0]["$vectorSearch"]["queryVector"])==384
        assert pipeline_ui[0]["$vectorSearch"]["filter"]["lote"]==sandbox["LOTE"]
        assert pipeline_ui[0]["$vectorSearch"]["limit"]==5
        assert pipeline_ui[1]["$project"]["score"]=={"$meta":"vectorSearchScore"}
        assert "password" not in json.dumps(pipeline_ui).lower()
        assert "mongodb+srv://" not in json.dumps(pipeline_ui)


        # Simulación de una colección remota: comprobar idempotencia y contratos,
        # nunca llamar a este mock evidencia de Atlas verdadero.
        atlas=AtlasFalso()
        sandbox.update(atlas_ok=True,col=atlas,atlas_cargado=False)
        exec(compile(snippet(10),"upsert.py","exec"),sandbox)
        assert sandbox["atlas_cargado"] and len(atlas.rows)==6
        assert all(k.startswith("s09:"+sandbox["LOTE"]+":") for k in atlas.rows)
        exec(compile(snippet(10),"upsert_again.py","exec"),sandbox)
        assert len(atlas.rows)==6, "Duplicados al repetir bulk_write"
        # Ruta de consola Atlas UI: el notebook NO debe crear el índice
        # si se eligió explícitamente la interfaz web.
        atlas_ui=AtlasFalso()
        sandbox["col"]=atlas_ui
        ui_source=snippet(12).replace(
            "CREAR_INDICE_EN_COLAB = True","CREAR_INDICE_EN_COLAB = False")
        exec(compile(ui_source,"index_ui_manual.py","exec"),sandbox)
        assert not sandbox["indice_creado"] and atlas_ui.idx is None
        # Simular que el docente lo creó en Atlas UI y reejecutó celda 5:
        atlas_ui.idx=Index(sandbox["definition"],"s09_vector_index","vectorSearch")
        exec(compile(ui_source,"index_ui_existing.py","exec"),sandbox)
        assert sandbox["indice_creado"] and atlas_ui.idx is not None
        # Reponer la colección de prueba; ruta PyMongo crea de forma programática.
        sandbox["col"]=atlas
        exec(compile(snippet(12).replace("CREAR_INDICE_EN_COLAB = True","CREAR_INDICE_EN_COLAB = True"),"index.py","exec"),sandbox)
        assert sandbox["indice_creado"] and atlas.idx is not None
        sandbox["indice_queryable"]=True
        exec(compile(snippet(15).replace("COMPARAR_ENN_ATLAS = False","COMPARAR_ENN_ATLAS = True"),"remote_mock.py","exec"),sandbox)
        assert sandbox["atlas_query_ejecutada"]
        assert sandbox["enn_query_ejecutada"]
        assert len(atlas.query_params)==2
        assert "exact" not in atlas.query_params[0]
        assert atlas.query_params[1].get("exact") is True
        assert "numCandidates" not in atlas.query_params[1]
        exec(compile(snippet(16),"remote_mock_evidence.py","exec"),sandbox)
        evidence=json.loads(Path("s09_atlas_evidencia.json").read_text())
        assert evidence["motor_ann_ejecutado"]=="MongoDB Atlas Vector Search"
        assert evidence["motor_enn_ejecutado"]=="MongoDB Atlas ENN"
        assert evidence["solapamiento_ann_enn_atlas"]==1
        assert len(evidence["resultados_ann_atlas"])==5
        assert "password" not in evidence and "URI_ATLAS" not in evidence
        # Una segunda consulta conserva el historial; el filtro viene de un resultado propio.
        before_history=len(sandbox["historial_s09"])
        filtered=snippet(15).replace("USAR_ENTIDAD_DEL_RESULTADO = False","USAR_ENTIDAD_DEL_RESULTADO = True").replace("POSICION_ENTIDAD = 0","POSICION_ENTIDAD = 1")
        exec(compile(filtered,"own_entity.py","exec"),sandbox)
        assert len(sandbox["historial_s09"])==before_history+1
        assert sandbox["FILTRO_ENTIDAD"]
        assert sandbox["ultimo_ranking_s09"].entidad.eq(sandbox["FILTRO_ENTIDAD"]).all()
        selected=snippet(16).replace("POSICION_EVIDENCIA = 0","POSICION_EVIDENCIA = 1").replace("LIMITE_ELEGIDO = 0","LIMITE_ELEGIDO = 1")
        exec(compile(selected,"selected_evidence.py","exec"),sandbox)
        evidence=json.loads(Path("s09_atlas_evidencia.json").read_text())
        assert evidence["seleccion_propia"]["id_proceso"]==sandbox["ultimo_ranking_s09"].iloc[0]["id_proceso"]
        for invalid in ['"mi respuesta"','True', '-1']:
            try:
                exec(compile(snippet(16).replace("LIMITE_ELEGIDO = 0","LIMITE_ELEGIDO = "+invalid),"reject_free_response.py","exec"),sandbox)
            except ValueError:
                pass
            else:
                raise AssertionError("Aceptó respuesta académica no estructurada: "+invalid)
    finally:
        os.chdir(before)
print("S09 QA OK: 21 celdas sincronizadas + sintaxis + Atlas automático por contrato + mocks offline (NO conexión real).")


# CONTRATO DE APROVISIONAMIENTO TEMPORAL SIN RED:
# Simular la API real (respuesta 201 y error 429) y el driver de MongoDB.
# Nunca se crea clúster ni se utiliza una URI real durante la CI.
def verificar_alta_atlas_ephemeral_offline():
    import contextlib, io, sys, types
    from unittest.mock import patch
    call_count={"post":0,"ping":0}
    placeholder_uri="mongodb+srv://mockUser:mockPassword@example.mongodb.net/"
    private_claim="https://account.mongodb.com/account/register?claimId=VALOR_PRIVADO_FICTICIO"
    class FakeResponse:
        status_code=201
        def raise_for_status(self): return None
        def json(self):
            return {"connectionString":placeholder_uri,"clusterId":"PRIVATE-MOCK-ID",
                    "claimUrl":private_claim,"expiresAt":"2026-10-31T22:00:00Z"}
    def fake_post(url,headers,json,timeout):
        assert url=="https://cloud.mongodb.com/api/atlas/v2/unauth/ephemeralClusters:create"
        assert headers["Accept"]=="application/vnd.atlas.preview+json"
        assert headers["Content-Type"]=="application/json"
        assert json["clusterName"].startswith("S09-") and timeout>0
        call_count["post"]+=1
        return FakeResponse()
    class FakeClient:
        def __init__(self,uri,**options):
            assert uri==placeholder_uri
            self.admin=types.SimpleNamespace(command=self._ping)
        def _ping(self,command):
            assert command=="ping"
            call_count["ping"]+=1
            return {"ok":1}
        def __getitem__(self,db):
            assert db=="clase_s09_demo"
            return types.SimpleNamespace(__getitem__=lambda key:None) if False else FakeDB()
    class FakeDB:
        def __getitem__(self,coll):
            assert coll=="secop_vectores"
            return "COLLECTION_MOCK"
    fake_pymongo=types.ModuleType("pymongo")
    fake_pymongo.MongoClient=FakeClient
    fake_pymongo.UpdateOne=object
    fake_operations=types.ModuleType("pymongo.operations")
    fake_operations.SearchIndexModel=object
    fake_requests=types.ModuleType("requests")
    fake_requests.post=fake_post
    with patch.dict(sys.modules,{"pymongo":fake_pymongo,
                                 "pymongo.operations":fake_operations,
                                 "requests":fake_requests}):
        env={"__name__":"__main__"}
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(compile(snippet(8),"atlas_ephemeral_201_mock.py","exec"),env)
            assert env["atlas_ok"] and env["col"]=="COLLECTION_MOCK"
            assert env["_s09_atlas_temporal_privado"]["connectionString"]==placeholder_uri
            assert call_count["post"]==1 and call_count["ping"]==1
            # Reiniciar la celda debe reutilizar el recurso del mismo runtime.
            exec(compile(snippet(8),"atlas_ephemeral_reuse_mock.py","exec"),env)
            assert call_count["post"]==1 and call_count["ping"]==2
        exposed=output.getvalue()
        assert placeholder_uri not in exposed and "mockPassword" not in exposed
        assert private_claim not in exposed and "PRIVATE-MOCK-ID" not in exposed
        assert "ATLAS REAL · conexión confirmada" in exposed
        class LimitedResponse:
            status_code=429
            def raise_for_status(self): raise AssertionError("429 must be handled first")
        fake_requests.post=lambda *args,**kw:LimitedResponse()
        no_conn={"__name__":"__main__"}
        with contextlib.redirect_stdout(io.StringIO()) as output429:
            exec(compile(snippet(8),"atlas_ephemeral_429_mock.py","exec"),no_conn)
        assert not no_conn["atlas_ok"] and no_conn["col"] is None
        assert "_s09_atlas_temporal_privado" not in no_conn
        assert "ATLAS TEMPORAL NO CREADO" in output429.getvalue()
        assert "NO SE EJECUTÓ ATLAS" in output429.getvalue()
    print("S09 API MOCK OK: alta, reutilización, ping, 429 y no exposición de URI/claim.")

verificar_alta_atlas_ephemeral_offline()
