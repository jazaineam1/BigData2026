#!/usr/bin/env python3
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib, json, os, sys
import pandas as pd
import networkx as nx

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"utils"))
import tc1_validator as V

class FakeCollection:
    __module__="pymongo.collection"
    def __init__(self,n): self.n=n
    def count_documents(self,_): return self.n
    def index_information(self):
        return {
            "_id_":{"key":[("_id",1)]},
            "id_proceso_1":{"key":[("id_proceso",1)],"unique":True},
            "valor_contratos_-1":{"key":[("contratos_resumen.valor_total",-1)]},
        }

def chash(df,key):
    x=df.copy().sort_values(key,kind="mergesort").reset_index(drop=True)
    return hashlib.sha256(x.to_json(orient="records",force_ascii=False,date_format="iso").encode()).hexdigest()

def touch(p,txt="ok"):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(txt,encoding="utf-8")

def main():
  with TemporaryDirectory() as td:
    out=Path(td)/"entrega_tc1"; raw=out/"raw"; raw.mkdir(parents=True)
    n=637               # prueba explícita: una ventana real puede tener < 1000 procesos
    linked=320
    pro=[]; hist=[]; docs=[]; cont=[]

    for i in range(n):
      pid=f"CO1.REQ.{i:05d}"
      portfolio=f"CO1.BDOS.{i:05d}"
      nit_ent=str(100+i%3)
      dept=["Antioquia","Bogotá D.C.","Valle"][i%3]
      nit_prov=str(900+i%17)
      has=i<linked
      val=float(5_000_000+i*25_000) if has else 0.0
      pro.append({
        "id_del_proceso":pid,"id_del_portafolio":portfolio,
        "entidad":f"Entidad {nit_ent}","nit_entidad":nit_ent,"departamento_entidad":dept,
        "ciudad_entidad":"Ciudad","fecha_de_publicacion_del":"2025-01-15T00:00:00.000","precio_base":float(1_000_000+i),
        "modalidad_de_contratacion":"Directa","respuestas_al_procedimiento":0,"estado_del_procedimiento":"Adjudicado",
        "adjudicado":"Si","nombre_del_proveedor":f"Proveedor {nit_prov}","nit_del_proveedor_adjudicado":nit_prov,
        "urlproceso":f"https://example.test/{pid}"
      })
      hist.append({
        "id_proceso":pid,"id_portafolio":portfolio,"entidad":f"Entidad {nit_ent}","nit_entidad":nit_ent,
        "departamento":dept,"ciudad":"Ciudad","fecha_publicacion":pd.Timestamp("2025-01-15"),"anio":2025,
        "precio_base":float(1_000_000+i),"modalidad":"Directa","respuestas":0,"estado":"Adjudicado",
        "adjudicado":True,"proveedor":f"Proveedor {nit_prov}","nit_proveedor":nit_prov,
        "url":f"https://example.test/{pid}","contratos_cantidad":1 if has else 0,"valor_contratos":val,
        "contratos_estados":["En ejecución"] if has else []
      })
      docs.append({
        "id_proceso":pid,
        "entidad":{"nit":nit_ent,"nombre":f"Entidad {nit_ent}","departamento":dept,"ciudad":"Ciudad"},
        "proceso":{"fecha_publicacion":"2025-01-15","anio":2025,"precio_base":float(1_000_000+i),"modalidad":"Directa","estado":"Adjudicado","adjudicado":True},
        "proveedor_adjudicado":{"nit":nit_prov,"nombre":f"Proveedor {nit_prov}"},
        "contratos_resumen":{"cantidad":1 if has else 0,"valor_total":val,"estados":["En ejecución"] if has else []},
        "metadata_ingesta":{"dataset":"p6dx-8zbt","pareja_id":"TEST-V5","window_start":"2025-01-01","window_end":"2025-03-01"}
      })
      if has:
        cont.append({
          "proceso_de_compra":portfolio,"id_contrato":f"C{i:05d}","estado_contrato":"En ejecución","tipo_de_contrato":"Servicios",
          "modalidad_de_contratacion":"Directa","fecha_de_firma":"2025-02-01T00:00:00",
          "nombre_entidad":f"Entidad {nit_ent}","nit_entidad":nit_ent,
          "proveedor_adjudicado":f"Proveedor {nit_prov}","documento_proveedor":nit_prov,
          "valor_del_contrato":str(val)
        })

    procesos=pd.DataFrame(pro); procesos_seq=procesos.copy()
    historico=pd.DataFrame(hist); contratos=pd.DataFrame(cont)

    offsets=list(range(0,n,250))
    h=chash(procesos,"id_del_proceso")
    bench={
      "workers":4,"target_rows":n,"page_size":250,
      "rows_sequential":n,"rows_threaded":n,
      "seconds_sequential":2.8,"seconds_threaded":3.1,
      "hash_sequential":h,"hash_threaded":h,
      "offsets_sequential":offsets,"offsets_threaded":offsets,
      "same_offsets":True,"same_rows":True,"same_hash":True
    }
    data_contract={
      "procesos":{"id":"p6dx-8zbt","grain":"proceso","fields":sorted(V.PROCESS_FIELDS)},
      "contratos":{"id":"jbjy-vk9h","grain":"contrato","fields":sorted(V.CONTRACT_FIELDS)},
      "join":{"procesos.id_del_portafolio":"contratos.proceso_de_compra"},
      "window":{"start":"2025-01-01","end":"2025-03-01"}
    }
    query_plan={
      "procesos":{"where":"fecha_de_publicacion_del >= '2025-01-01' and fecha_de_publicacion_del < '2025-03-01'",
                  "order":"fecha_de_publicacion_del ASC,id_del_proceso ASC"},
      "contratos":{"where":"fecha_de_firma >= '2025-01-01' and fecha_de_firma < '2025-03-01'",
                   "order":"fecha_de_firma ASC,id_contrato ASC"}
    }
    coverage=linked/n
    quality={
      "join_key":"id_del_portafolio -> proceso_de_compra",
      "matched_processes":linked,"join_coverage":coverage,
      "procesos":{"rows":n},"contratos":{"rows":linked}
    }
    acq={
      "schema":"2026-09-30-secoppipeline-v5",
      "queried_at_utc":"2026-09-30T00:00:00+00:00","workers":4,"page_size":250,
      "target_rows":{"procesos":n,"contratos":linked},
      "datasets":{"procesos":{"id":"p6dx-8zbt","rows":n},"contratos":{"id":"jbjy-vk9h","rows":linked}}
    }

    for p in [
      raw/"procesos.parquet",raw/"contratos.parquet",out/"00_dataset_contract.json",
      out/"01_acquisition_manifest.json",out/"01_benchmark_threads.json",out/"01_quality_report.json",
      out/"02_secop_integrado.parquet",out/"02_modelo_documental.json"
    ]: touch(p)

    idem={"count_after_first":n,"count_after_second":n,"duplicates_after_second":0}
    ref_a=linked
    topdocs=sorted(
      [{"id_proceso":d["id_proceso"],"valor_contratos":float(d["contratos_resumen"]["valor_total"])} for d in docs],
      key=lambda x:(-x["valor_contratos"],x["id_proceso"])
    )[:10]
    atlas_resultados={
      "carga":{"documentos":n,"server_version":"8.0","idempotencia":idem,"indices":["id_proceso_1","valor_contratos_-1"]},
      "consulta_a":{"filtro":{"x":1},"resultado":ref_a},
      "consulta_b":{"filtro":{},"proyeccion":{},"resultado":topdocs}
    }
    touch(out/"02_atlas_evidence.json",json.dumps(atlas_resultados))

    band_ref=sorted(
      [{"id_proceso":d["id_proceso"],"valor_contratos":float(d["contratos_resumen"]["valor_total"])}
       for d in docs if d["contratos_resumen"]["cantidad"]>0],
      key=lambda x:(-x["valor_contratos"],x["id_proceso"])
    )[:100]
    bandeja=pd.DataFrame(band_ref)
    bandeja["anio"]=2025
    depmap=dict(zip(historico.id_proceso,historico.departamento))
    bandeja["departamento"]=bandeja.id_proceso.map(depmap)
    bandeja.to_csv(out/"03_bandeja_historica.csv",index=False)

    bc=bandeja.copy()
    cql="""CREATE TABLE tc1.procesos_por_anio_departamento (
      anio int, departamento text, valor_contratos double, id_proceso text,
      PRIMARY KEY ((anio, departamento), valor_contratos, id_proceso)
    ) WITH CLUSTERING ORDER BY (valor_contratos DESC, id_proceso ASC);"""
    touch(out/"04_modelo_cassandra.cql",cql)
    counts=(bc.groupby(["anio","departamento"],dropna=False).size().rename("n").reset_index()
            .sort_values(["n","anio","departamento"],ascending=[False,True,True],kind="mergesort").reset_index(drop=True))
    rr=counts.iloc[0]; part=(int(rr["anio"]),rr["departamento"])
    top10=(bc[(bc.anio==part[0])&(bc.departamento==part[1])]
           .sort_values(["valor_contratos","id_proceso"],ascending=[False,True],kind="mergesort").head(10))

    pmap=procesos[["id_del_portafolio","id_del_proceso"]].rename(columns={"id_del_proceso":"id_proceso"}).copy()
    relaciones=contratos.merge(pmap,left_on="proceso_de_compra",right_on="id_del_portafolio",how="inner")
    relaciones["nit_proveedor"]=relaciones["documento_proveedor"].astype(str)
    relaciones["proveedor"]=relaciones["proveedor_adjudicado"].astype(str)
    relaciones["entidad"]=relaciones["nombre_entidad"].astype(str)
    relaciones=relaciones[["id_contrato","id_proceso","nit_entidad","entidad","nit_proveedor","proveedor"]]
    relaciones=relaciones.sort_values(["id_contrato","id_proceso","nit_proveedor"],kind="mergesort").reset_index(drop=True)

    rank=(relaciones.groupby("nit_entidad")["id_contrato"].nunique().rename("contratos").reset_index()
          .sort_values(["contratos","nit_entidad"],ascending=[False,True],kind="mergesort").reset_index(drop=True))
    nit_ancla=str(rank.iloc[0]["nit_entidad"])
    rel_ancla=relaciones[relaciones.nit_entidad.astype(str)==nit_ancla]
    entidad_ancla=str(rel_ancla.entidad.iloc[0])
    a=rel_ancla.groupby("nit_proveedor")["id_contrato"].nunique().rename("contratos_con_ancla").reset_index()
    g=relaciones.groupby("nit_proveedor")["nit_entidad"].nunique().rename("entidades_conectadas").reset_index()
    rel=a.merge(g,on="nit_proveedor").sort_values(
      ["entidades_conectadas","contratos_con_ancla","nit_proveedor"],
      ascending=[False,False,True],kind="mergesort"
    ).reset_index(drop=True)
    rel.to_csv(out/"05_resultado_relacional.csv",index=False)

    cy_load="UNWIND $rows AS row MERGE (e:Entidad {nit: row.nit_entidad}) MERGE (c:Contrato {id: row.id_contrato}) MERGE (v:Proveedor {nit: row.nit_proveedor})"
    cy_ctx="MATCH (e:Entidad {nit:$nit_ancla}) RETURN e"
    cy_share="MATCH (e:Entidad {nit:$nit_ancla})--(:Contrato)--(v:Proveedor)--(:Contrato)--(o:Entidad) WHERE o.nit <> $nit_ancla RETURN v,o"
    cy_rank="MATCH (v:Proveedor)--(:Contrato)--(e:Entidad) RETURN v.nit, count(distinct e) AS entidades"
    touch(out/"05_neo4j_consultas.cypher","\n".join([cy_load,cy_ctx,cy_share,cy_rank]))

    correct_429="Reducir concurrencia, respetar Retry-After/backoff y volver a comprobar filas + hash"
    correct_indice="Crear un índice adicional alineado con una consulta real y comprobarlo con index_information()"
    correct_limite="La priorización y las conexiones orientan revisión; no demuestran fraude ni causalidad"
    decisions=[
      {"decision":correct_429,"evidence":"workers=4; same_offsets=True; same_hash=True","alternative":"Aumentar workers sin controlar throttling","risk":"snapshot"},
      {"decision":correct_indice,"evidence":"indices=['id_proceso_1','valor_contratos_-1']","alternative":"índice sin consulta","risk":"costo de escritura"},
      {"decision":correct_limite,"evidence":f"join_coverage={coverage}; matched_processes={linked}","alternative":"interpretar como prueba","risk":"sobreinterpretación"},
    ]
    touch(out/"06_decision_log.json",json.dumps(decisions))
    report=f"""## 1. Adquisición y contrato de datos
Procesos={n}; contratos={linked}; clave=id_del_portafolio→proceso_de_compra.
## 2. Concurrencia, robustez y calidad
Workers=4; mismos_offsets=True; mismo_hash=True; join_coverage={coverage}.
## 3. Modelo documental e idempotencia Atlas
Documentos={n}; idempotencia={idem}; índices=['id_proceso_1','valor_contratos_-1'].
## 4. Producto analítico y Cassandra
Filas_bandeja={len(bandeja)}; modelo Cassandra=query-first + simulación local.
## 5. Neo4j, decisiones y límites
Entidad ancla={entidad_ancla}. La priorización y las conexiones no demuestran fraude ni causalidad.
"""
    touch(out/"06_informe_tecnico.md",report)

    correct_d429="Reducir workers, respetar Retry-After/backoff y repetir la comparación de filas + hash"
    correct_cov="La cobertura mide qué proporción de procesos encontró contrato en este snapshot; no se inventan los faltantes"
    defensa={
      "escenario_429":{"workers_observados":4,"same_hash":True,"seleccion":correct_d429},
      "escenario_cobertura":{"join_coverage":coverage,"matched_processes":linked,"seleccion":correct_cov},
    }
    touch(out/"06_microdefensa_grupal.json",json.dumps(defensa))

    G=nx.DiGraph()
    ns={
      "OUT":out,"PAREJA_ID":"TEST-V5","INTEGRANTE_1":"A","CODIGO_1":"1","INTEGRANTE_2":"B","CODIGO_2":"2",
      "N_PROCESOS":n,"OFFSETS_PROCESOS":offsets,
      "data_contract":data_contract,"query_plan":query_plan,
      "procesos_seq":procesos_seq,"procesos_df":procesos,"contratos_df":contratos,
      "benchmark_threads":bench,"acquisition_manifest":acq,"quality_report":quality,
      "historico":historico,"relaciones_contrato":relaciones,"documentos":docs,
      "coleccion":FakeCollection(n),"atlas_ping":True,"atlas_server_version":"8.0",
      "atlas_idempotencia":idem,"atlas_indexes":["id_proceso_1","valor_contratos_-1"],
      "filtro_a":{"x":1},"resultado_a":ref_a,"filtro_b":{},"proyeccion_b":{},"resultado_b":topdocs,
      "atlas_resultados":atlas_resultados,
      "pipeline_bandeja":[{"$match":{}},{"$sort":{}},{"$limit":100}],"bandeja_historica":bandeja,
      "bandeja_cassandra":bc,"cql_create":cql,"particion_prueba":part,"top10_cassandra":top10,
      "nit_ancla":nit_ancla,"entidad_ancla":entidad_ancla,"resultado_relacional":rel,
      "cypher_carga":cy_load,"cypher_contexto":cy_ctx,"cypher_compartidos":cy_share,"cypher_ranking":cy_rank,
      "G":G,"nodos_grafo":1+rel_ancla.id_contrato.nunique()+rel_ancla.nit_proveedor.nunique(),
      "aristas_grafo":rel_ancla.id_contrato.nunique()+rel_ancla[["id_contrato","nit_proveedor"]].drop_duplicates().shape[0],
      "decision_429":correct_429,"CORRECT_429":correct_429,
      "decision_indice":correct_indice,"CORRECT_INDICE":correct_indice,
      "decision_limite":correct_limite,"CORRECT_LIMITE":correct_limite,
      "decision_log":decisions,"informe_tecnico":report,
      "respuesta_429":correct_d429,"CORRECT_DEFENSA_429":correct_d429,
      "respuesta_cobertura":correct_cov,"CORRECT_DEFENSA_COBERTURA":correct_cov,
      "defensa_grupal":defensa,
    }

    old=os.getcwd()
    try:
      os.chdir(td)
      manifest=V.evaluar(ns)
    finally:
      os.chdir(old)

    assert manifest["puntaje"]==100, manifest
    assert manifest["maximo"]==100
    assert manifest["version"]==V.VERSION
    assert manifest["gates"]["security_no_secrets"]["ok"] is True
    print("TC1 V5 synthetic (<1000 procesos) 100/100: OK")

if __name__=="__main__":
  main()
