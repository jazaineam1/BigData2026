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
assert "SearchIndexModel(" in snippet(12)
assert 'list_search_indexes(' in snippet(13) and 'queryable' in snippet(13)
assert '"$vectorSearch"' in snippet(15) and '"exact":True' in snippet(15)
assert "solapamiento_ann_enn_atlas" in snippet(16)
assert "s09_atlas_evidencia.json" in snippet(16)
assert "EJECUTAR_BENCHMARK = False" in snippet(21)
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
        exec(compile(snippet(12),"index.py","exec"),sandbox)
        assert sandbox["indice_creado"] and atlas.idx is not None
        sandbox["indice_queryable"]=True
        exec(compile(snippet(15),"remote_mock.py","exec"),sandbox)
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
    finally:
        os.chdir(before)
print("S09 QA OK: 21 celdas sincronizadas + sintaxis + ruta local + Atlas simulado (NO conexión real).")
