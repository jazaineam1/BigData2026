#!/usr/bin/env python3
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib, json, sys
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
            "compound":{"key":[("proceso.anio",1),("contratos_resumen.valor_total",-1)]},
        }

def chash(df,key):
    x=df.copy().sort_values(key,kind="mergesort").reset_index(drop=True)
    return hashlib.sha256(x.to_json(orient="records",force_ascii=False,date_format="iso").encode()).hexdigest()

def touch(p,txt="ok"):
    p.parent.mkdir(parents=True,exist_ok=True); p.write_text(txt,encoding="utf-8")

def main():
  with TemporaryDirectory() as td:
    out=Path(td)/"entrega_tc1"; raw=out/"raw"; raw.mkdir(parents=True)
    n=1200
    pro=[]; hist=[]; docs=[]
    for i in range(n):
      pid=f"P{i:05d}"; nit_ent=str(100+i%3); nit_prov=str(900+i%17); dept=["Antioquia","Bogotá D.C.","Valle"][i%3]
      has=i<600; val=float(5_000_000+i*25_000) if has else 0.0
      pro.append({
        "id_del_proceso":pid,"entidad":f"Entidad {nit_ent}","nit_entidad":nit_ent,"departamento_entidad":dept,
        "ciudad_entidad":"Ciudad","fecha_de_publicacion":"2025-01-15T00:00:00.000","precio_base":float(1_000_000+i),
        "modalidad_de_contratacion":"Directa","respuestas_al_procedimiento":0,"estado_del_procedimiento":"Adjudicado",
        "adjudicado":"Si","nombre_del_proveedor_adjudicado":f"Proveedor {nit_prov}","nit_del_proveedor_adjudicado":nit_prov,
        "urlproceso":f"https://example.test/{pid}"
      })
      hist.append({
        "id_proceso":pid,"entidad":f"Entidad {nit_ent}","nit_entidad":nit_ent,"departamento":dept,"ciudad":"Ciudad",
        "fecha_publicacion":pd.Timestamp("2025-01-15"),"anio":2025,"precio_base":float(1_000_000+i),"modalidad":"Directa",
        "respuestas":0,"estado":"Adjudicado","adjudicado":True,"proveedor":f"Proveedor {nit_prov}","nit_proveedor":nit_prov,
        "url":f"https://example.test/{pid}","contratos_cantidad":1 if has else 0,"valor_contratos":val,
        "contratos_estados":["En ejecución"] if has else []
      })
      docs.append({
        "id_proceso":pid,
        "entidad":{"nit":nit_ent,"nombre":f"Entidad {nit_ent}","departamento":dept,"ciudad":"Ciudad"},
        "proceso":{"fecha_publicacion":"2025-01-15","anio":2025,"precio_base":float(1_000_000+i),"modalidad":"Directa","estado":"Adjudicado","adjudicado":True},
        "proveedor_adjudicado":{"nit":nit_prov,"nombre":f"Proveedor {nit_prov}"},
        "contratos_resumen":{"cantidad":1 if has else 0,"valor_total":val,"estados":["En ejecución"] if has else []},
        "metadata_ingesta":{"dataset":"p6dx-8zbt","pareja_id":"TEST-V4","window_start":"2025-01-01","window_end":"2025-03-01"}
      })
    procesos=pd.DataFrame(pro); procesos_seq=procesos.copy(); historico=pd.DataFrame(hist)
    contratos=pd.DataFrame([{
      "proceso_de_compra":f"P{i:05d}","id_contrato":f"C{i:05d}","estado_contrato":"En ejecución","tipo_de_contrato":"Servicios",
      "modalidad_de_contratacion":"Directa","fecha_de_firma":"2025-02-01T00:00:00","proveedor_adjudicado":f"Proveedor {900+i%17}",
      "documento_proveedor":str(900+i%17),"valor_del_contrato":str(5_000_000+i*25_000)
    } for i in range(600)])

    h=chash(procesos,"id_del_proceso")
    bench={"workers":4,"rows_sequential":n,"rows_threaded":n,"seconds_sequential":8.2,"seconds_threaded":3.9,
           "hash_sequential":h,"hash_threaded":h,"same_rows":True,"same_hash":True}
    data_contract={
      "procesos":{"id":"p6dx-8zbt","grain":"proceso","fields":sorted(V.PROCESS_FIELDS)},
      "contratos":{"id":"jbjy-vk9h","grain":"contrato","fields":sorted(V.CONTRACT_FIELDS)},
      "join":{"procesos.id_del_proceso":"contratos.proceso_de_compra"},"window":{"start":"2025-01-01","end":"2025-03-01"}
    }
    query_plan={
      "procesos":{"where":"fecha_de_publicacion >= '2025-01-01' and fecha_de_publicacion < '2025-03-01'","order":"fecha_de_publicacion ASC,id_del_proceso ASC"},
      "contratos":{"where":"fecha_de_firma >= '2025-01-01' and fecha_de_firma < '2025-03-01'","order":"fecha_de_firma ASC,id_contrato ASC"}
    }
    quality={"join_coverage":0.5,"procesos":{"rows":n},"contratos":{"rows":600}}
    acq={"queried_at_utc":"2026-09-26T00:00:00+00:00","workers":4,
         "datasets":{"procesos":{"id":"p6dx-8zbt","rows":n},"contratos":{"id":"jbjy-vk9h","rows":600}}}
    for p in [raw/"procesos.parquet",raw/"contratos.parquet",out/"00_dataset_contract.json",out/"01_acquisition_manifest.json",
              out/"01_benchmark_threads.json",out/"01_quality_report.json",out/"02_secop_integrado.parquet",out/"02_modelo_documental.json"]:
      touch(p)

    idem={"count_after_first":n,"count_after_second":n,"duplicates_after_second":0}
    ref_a=600
    topdocs=sorted([{"id_proceso":d["id_proceso"],"valor_contratos":float(d["contratos_resumen"]["valor_total"])} for d in docs],
                   key=lambda x:(-x["valor_contratos"],x["id_proceso"]))[:10]
    atlas_resultados={"carga":{"documentos":n,"server_version":"8.0","idempotencia":idem,"indices":["id_proceso_1","compound"]},
                      "consulta_a":{"filtro":{"x":1},"resultado":ref_a},
                      "consulta_b":{"filtro":{},"proyeccion":{},"resultado":topdocs}}
    touch(out/"02_atlas_evidence.json",json.dumps(atlas_resultados))

    band_ref=sorted([{"id_proceso":d["id_proceso"],"valor_contratos":float(d["contratos_resumen"]["valor_total"])}
                     for d in docs if d["contratos_resumen"]["cantidad"]>0],
                    key=lambda x:(-x["valor_contratos"],x["id_proceso"]))[:100]
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

    ref_hist=historico.copy()
    rank=(ref_hist.groupby("nit_entidad")["id_proceso"].nunique().rename("procesos").reset_index()
          .sort_values(["procesos","nit_entidad"],ascending=[False,True],kind="mergesort").reset_index(drop=True))
    nit_ancla=str(rank.iloc[0]["nit_entidad"]); ref_ancla=ref_hist[ref_hist.nit_entidad==nit_ancla]
    a=ref_ancla.groupby("nit_proveedor")["id_proceso"].nunique().rename("procesos_con_ancla").reset_index()
    g=ref_hist.groupby("nit_proveedor")["nit_entidad"].nunique().rename("entidades_conectadas").reset_index()
    rel=a.merge(g,on="nit_proveedor").sort_values(["entidades_conectadas","procesos_con_ancla","nit_proveedor"],
                                                  ascending=[False,False,True],kind="mergesort").reset_index(drop=True)
    rel.to_csv(out/"05_resultado_relacional.csv",index=False)
    cy_load="UNWIND $rows AS row MERGE (e:Entidad {nit: row.nit_entidad}) MERGE (p:Proceso {id: row.id_proceso}) MERGE (v:Proveedor {nit: row.nit_proveedor})"
    cy_ctx="MATCH (e:Entidad {nit:$nit_ancla}) RETURN e"
    cy_share="MATCH (e:Entidad {nit:$nit_ancla})--(v:Proveedor)--(o:Entidad) WHERE o.nit <> $nit_ancla RETURN v,o"
    cy_rank="MATCH (v:Proveedor)--(e:Entidad) RETURN v.nit, count(distinct e) AS entidades"
    touch(out/"05_neo4j_consultas.cypher","\n".join([cy_load,cy_ctx,cy_share,cy_rank]))

    decisions=[{"decision":"4 workers","evidence":"mismo hash","alternative":"2 workers","risk":"429"},
               {"decision":"select reducido","evidence":"menos bytes","alternative":"todas las columnas","risk":"pérdida de campos"},
               {"decision":"upsert","evidence":"segunda carga estable","alternative":"insert_many","risk":"duplicados"}]
    touch(out/"06_decision_log.json",json.dumps(decisions))
    report="""## 1. Adquisición y contrato de datos
ok
## 2. Concurrencia, robustez y calidad
ok
## 3. Modelo documental e idempotencia Atlas
ok
## 4. Producto analítico y Cassandra
ok
## 5. Neo4j, decisiones y límites
La priorización y las conexiones no demuestran fraude.
"""
    touch(out/"06_informe_tecnico.md",report)
    defensa={
      "pregunta_concurrencia":"Con 4 workers, ¿qué cambiaríamos ante HTTP 429 sin alterar el snapshot?",
      "respuesta_concurrencia":"Si aparece HTTP 429 reduciríamos los workers y respetaríamos Retry-After/backoff. Luego volveríamos a ejecutar la descarga y comprobaríamos que el hash canónico sigue siendo exactamente el mismo que en la referencia secuencial, además del mismo número de filas.",
      "pregunta_calidad":"Con join_coverage=0.5, ¿qué significa la cobertura y por qué no rellenamos contratos faltantes?",
      "respuesta_calidad":"La cobertura del join indica qué proporción de procesos encontró contrato relacionado dentro de la ventana y muestra el alcance del snapshot. No debemos inventar ni rellenar contratos faltantes porque convertiríamos ausencia de evidencia en datos fabricados y alteraríamos la interpretación."
    }
    touch(out/"06_microdefensa_grupal.json",json.dumps(defensa))

    ns={
      "OUT":out,"PAREJA_ID":"TEST-V4","INTEGRANTE_1":"A","CODIGO_1":"1","INTEGRANTE_2":"B","CODIGO_2":"2",
      "data_contract":data_contract,"query_plan":query_plan,"procesos_seq":procesos_seq,"procesos_df":procesos,"contratos_df":contratos,
      "benchmark_threads":bench,"acquisition_manifest":acq,"quality_report":quality,"historico":historico,"documentos":docs,
      "coleccion":FakeCollection(n),"atlas_ping":True,"atlas_server_version":"8.0","atlas_idempotencia":idem,"atlas_indexes":["id_proceso_1","compound"],
      "filtro_a":{"x":1},"resultado_a":ref_a,"filtro_b":{},"proyeccion_b":{},"resultado_b":topdocs,"atlas_resultados":atlas_resultados,
      "pipeline_bandeja":[{"$match":{}},{"$sort":{}},{"$limit":100}],"bandeja_historica":bandeja,
      "bandeja_cassandra":bc,"cql_create":cql,"particion_prueba":part,"top10_cassandra":top10,
      "hist_adjudicado":ref_hist,"nit_ancla":nit_ancla,"entidad_ancla":f"Entidad {nit_ancla}","resultado_relacional":rel,
      "cypher_carga":cy_load,"cypher_contexto":cy_ctx,"cypher_compartidos":cy_share,"cypher_ranking":cy_rank,
      "G":nx.DiGraph(),"nodos_grafo":1+ref_ancla.id_proceso.nunique()+ref_ancla.nit_proveedor.nunique(),
      "aristas_grafo":ref_ancla.id_proceso.nunique()+ref_ancla[["id_proceso","nit_proveedor"]].drop_duplicates().shape[0],
      "decision_log":decisions,"informe_tecnico":report,"defensa_grupal":defensa,
    }
    manifest=V.evaluar(ns)
    assert manifest["puntaje"]==100, manifest
    assert manifest["maximo"]==100
    assert manifest["version"]==V.VERSION
    print("TC1 synthetic 100/100: OK")

if __name__=="__main__":
  main()
