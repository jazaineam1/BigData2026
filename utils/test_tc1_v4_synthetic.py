#!/usr/bin/env python3
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib, json, os, sys
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"utils"))
import tc1_validator as V

def write_cache(cache_dir, df, offsets, endpoint):
    cache_dir.mkdir(parents=True,exist_ok=True)
    for off in offsets:
        part=df.iloc[off:off+250].to_dict("records")
        raw=json.dumps(part,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str).encode()
        stem=f"page_{off:07d}"
        (cache_dir/f"{stem}.json").write_bytes(raw)
        meta={
            "endpoint":endpoint,"offset":off,"limit":250,"rows":len(part),
            "query_signature":hashlib.sha256(f"{endpoint}:{off}".encode()).hexdigest(),
            "sha256":hashlib.sha256(raw).hexdigest(),"attempts":1,"from_cache":False,
        }
        (cache_dir/f"{stem}.meta.json").write_text(json.dumps(meta),encoding="utf-8")

def touch(p,content="ok"):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    if isinstance(content,bytes): p.write_bytes(content)
    else: p.write_text(content,encoding="utf-8")

def main():
  with TemporaryDirectory() as td:
    td=Path(td); out=td/"entrega_tc1"; raw=out/"raw"; pages=raw/"pages"/"scope-test"
    seq=pages/"procesos"/"sequential"; thr=pages/"procesos"/"threaded"; con=pages/"contratos"/"official"
    n=40; matched=35

    procesos=pd.DataFrame([
      {"id_del_proceso":f"P{i:03d}","id_del_portafolio":f"B{i:03d}","entidad":f"Entidad {i%4}",
       "nit_entidad":str(100+i%4),"departamento_entidad":"Bogotá D.C.","precio_base":1000+i}
      for i in range(n)
    ])
    contratos=pd.DataFrame([
      {"proceso_de_compra":f"B{i:03d}","id_contrato":f"C{i:03d}","valor_del_contrato":str(100000-i*1000)}
      for i in range(matched)
    ])
    offsets=[0]; offsets_c=[0]
    write_cache(seq,procesos,offsets,"p6dx-8zbt")
    write_cache(thr,procesos,offsets,"p6dx-8zbt")
    write_cache(con,contratos,offsets_c,"jbjy-vk9h")

    raw.mkdir(parents=True,exist_ok=True)
    touch(raw/"procesos.parquet",b"PAR1")
    touch(raw/"contratos.parquet",b"PAR1")
    for name in ["00_dataset_contract.json","01_acquisition_manifest.json","01_benchmark_threads.json","01_quality_report.json"]:
      touch(out/name,"{}")

    historico=pd.DataFrame([
      {"id_proceso":f"P{i:03d}","nit_entidad":str(100+i%4),"entidad":f"Entidad {i%4}",
       "departamento":"Bogotá D.C.","valor_contratos":float(100000-i*1000)}
      for i in range(n)
    ])
    documentos=[{"id_proceso":x} for x in historico.id_proceso]
    touch(out/"02_atlas_documentos.json",json.dumps(documentos))

    atlas_expected={"nit_entidad":"100","entidad":"Entidad 0","valor_total":970000.0}
    atlas_pipeline=[
      {"$match":{"entidad.departamento":"Bogotá D.C.","red.proveedores_compartidos":{"$gt":0}}},
      {"$group":{"_id":{"nit":"$entidad.nit","nombre":"$entidad.nombre"},
                  "valor_total":{"$sum":"$contratos.valor_total"},"procesos":{"$sum":1}}},
      {"$sort":{"valor_total":-1,"_id.nit":1}},
      {"$limit":5},
    ]
    atlas_evidence={
      "pipeline":atlas_pipeline,"top_nit":"100","top_entidad":"Entidad 0",
      "top_valor":970000.0,"pipeline_guardado":"tc1_test_priorizacion"
    }

    cql="""CREATE TABLE IF NOT EXISTS compras_claras.prioridades_tc1_test (
      corte text, departamento text, valor_contratos decimal, id_proceso text,
      entidad text, nit_entidad text,
      PRIMARY KEY ((corte, departamento), valor_contratos, id_proceso)
    ) WITH CLUSTERING ORDER BY (valor_contratos DESC, id_proceso ASC);"""
    top5=["P000","P001","P002","P003","P004"]
    touch(out/"03_astra_carga.cql",cql)
    astra_evidence={"create_table":cql,"top5_ids":top5}

    rel_grafo=pd.DataFrame([
      {"id_contrato":"C0","id_proceso":"P000","nit_entidad":"100","entidad":"Entidad 0","nit_proveedor":"900","proveedor":"Proveedor X"},
      {"id_contrato":"C1","id_proceso":"P001","nit_entidad":"101","entidad":"Entidad 1","nit_proveedor":"900","proveedor":"Proveedor X"},
      {"id_contrato":"C2","id_proceso":"P002","nit_entidad":"102","entidad":"Entidad 2","nit_proveedor":"900","proveedor":"Proveedor X"},
    ])
    cypher='''MATCH (a:Entidad {nit:"100"})-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v:Proveedor)
MATCH (otra:Entidad)-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v)
WHERE otra.nit <> a.nit
RETURN v.nit AS nit_proveedor, v.nombre AS proveedor, count(DISTINCT otra) AS otras_entidades
ORDER BY otras_entidades DESC, nit_proveedor ASC
LIMIT 5'''
    touch(out/"04_neo4j_carga.cypher",cypher)
    neo_expected={"nit_proveedor":"900","proveedor":"Proveedor X","otras_entidades":2}
    neo_evidence={"query":cypher,"nit_proveedor":"900","proveedor":"Proveedor X","otras_entidades":2}

    decision_log={
      "rol_atlas":"Explorar/agregar documentos flexibles y priorizar entidades",
      "rol_cassandra":"Servir repetidamente corte + departamento → top 5",
      "rol_neo4j":"Recorrer proveedores compartidos entre entidades",
      "limite_relacional":"Un proveedor compartido describe conectividad, no prueba irregularidad",
    }

    ns={
      "OUT":out,"RAW":raw,
      "CACHE_SEQ_PROCESOS":seq,"CACHE_THR_PROCESOS":thr,"CACHE_CONTRATOS":con,
      "OFFSETS_PROCESOS":offsets,"OFFSETS_CONTRATOS":offsets_c,
      "PAREJA_ID":"TEST",
      "data_contract":{
        "procesos":{"id":"p6dx-8zbt"},"contratos":{"id":"jbjy-vk9h"},
        "join":{"procesos.id_del_portafolio":"contratos.proceso_de_compra"}
      },
      "benchmark_threads":{"same_offsets":True,"same_rows":True,"same_hash":True},
      "acquisition_manifest":{"schema":V.VERSION},
      "quality_report":{"join_coverage":matched/n},
      "matched_processes":matched,
      "historico":historico,"documentos":documentos,
      "DEPARTAMENTO_OBJETIVO":"Bogotá D.C.","ATLAS_ESPERADO":atlas_expected,
      "atlas_pipeline_student":atlas_pipeline,"atlas_evidence":atlas_evidence,
      "ASTRA_TOP5_ESPERADO":top5,"astra_evidence":astra_evidence,
      "neo4j_evidence":neo_evidence,"NEO4J_ESPERADO":neo_expected,
      "ENTIDAD_ANCLA_NIT":"100","ENTIDAD_ANCLA":"Entidad 0","rel_grafo":rel_grafo,
      "decision_log":decision_log,
    }

    old=os.getcwd()
    try:
      os.chdir(td)

      # Riesgo conocido: chunk sobrante debe verse claramente y restar E1.
      extra=thr/"page_0999999.json"
      extra.write_text("[]",encoding="utf-8")
      broken=V.evaluar(ns)
      assert broken["score"] < 100
      assert any((not c["ok"]) and c["stage"]=="E1" for c in broken["checks"])
      extra.unlink()
      print("V8 detecta chunk extra: OK")

      manifest=V.evaluar(ns)
    finally:
      os.chdir(old)

    assert manifest["validator_version"]==V.VERSION, manifest
    assert manifest["score"]==100, manifest
    assert manifest["rubric_scores"]=={"E1":15,"E2":30,"E3":20,"E4":25,"E5":10}
    assert manifest["security_no_secrets"] is True
    assert (out/"TC1_TEST.zip").exists()
    print("TC1 V8 native-tools synthetic path 100/100: OK")

if __name__=="__main__":
  main()
