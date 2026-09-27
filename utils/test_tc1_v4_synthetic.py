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
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(txt,encoding="utf-8")

def main():
  with TemporaryDirectory() as td:
    out=Path(td)/"entrega_tc1"
    raw=out/"raw"
    raw.mkdir(parents=True)

    n=1200
    n_contracts=600
    pro=[]
    hist=[]
    docs=[]

    for i in range(n):
      pid=f"P{i:05d}"
      nit_ent=str(100+i%3)
      nit_prov=str(900+i%17)
      dept=["Antioquia","Bogotá D.C.","Valle del Cauca"][i%3]
      year=2025 if i<600 else 2026
      fecha=f"{year}-{'02' if year==2025 else '07'}-15T00:00:00.000"
      has=i<n_contracts
      base=float(1_000_000+i*1_000)
      valor=float(5_000_000+i*25_000) if has else 0.0
      diferencia=valor-base if has else 0.0

      pro.append({
        "id_del_proceso":pid,
        "entidad":f"Entidad {nit_ent}",
        "nit_entidad":nit_ent,
        "departamento_entidad":dept,
        "ciudad_entidad":"Ciudad",
        "fecha_de_publicacion_del":fecha,
        "precio_base":base,
        "modalidad_de_contratacion":"Contratación directa",
        "respuestas_al_procedimiento":"1",
        "estado_del_procedimiento":"Adjudicado",
        "adjudicado":"Si",
        "valor_total_adjudicacion":valor,
      })

      hist.append({
        "id_proceso":pid,
        "entidad":f"Entidad {nit_ent}",
        "nit_entidad":nit_ent,
        "departamento":dept,
        "ciudad":"Ciudad",
        "fecha_publicacion":pd.Timestamp(fecha),
        "anio":year,
        "precio_base":base,
        "modalidad":"Contratación directa",
        "respuestas":1,
        "estado":"Adjudicado",
        "adjudicado":True,
        "proveedor":f"Proveedor {nit_prov}",
        "nit_proveedor":nit_prov,
        "contratos_cantidad":1 if has else 0,
        "valor_contratos":valor,
        "contratos_estados":["En ejecución"] if has else [],
      })

      docs.append({
        "id_proceso":pid,
        "entidad":{
          "nit":nit_ent,
          "nombre":f"Entidad {nit_ent}",
          "departamento":dept,
          "ciudad":"Ciudad",
        },
        "proceso":{
          "fecha_publicacion":fecha,
          "anio":year,
          "precio_base":base,
          "modalidad":"Contratación directa",
          "estado":"Adjudicado",
          "adjudicado":True,
          "diferencia_valor":diferencia,
        },
        "proveedor_adjudicado":{
          "nit":nit_prov if has else None,
          "nombre":f"Proveedor {nit_prov}" if has else None,
        },
        "contratos_resumen":{
          "cantidad":1 if has else 0,
          "valor_total":valor,
          "estados":["En ejecución"] if has else [],
        },
        "metadata_ingesta":{
          "dataset":"p6dx-8zbt",
          "pareja_id":"TEST-V5",
          "window_start":"2025-01-01T00:00:00.000",
          "latest_procesos":"2026-09-26T23:59:59.000",
          "latest_contratos":"2026-09-26T23:59:59.000",
        },
      })

    procesos=pd.DataFrame(pro)
    procesos_seq=procesos.copy()
    procesos_threads_benchmark=procesos.copy()
    historico=pd.DataFrame(hist)

    contratos=pd.DataFrame([{
      "proceso_de_compra":f"P{i:05d}",
      "id_contrato":f"C{i:05d}",
      "estado_contrato":"En ejecución",
      "tipo_de_contrato":"Prestación de servicios",
      "modalidad_de_contratacion":"Contratación directa",
      "fecha_de_firma":("2025-03-01T00:00:00.000" if i<300 else "2026-08-01T00:00:00.000"),
      "proveedor_adjudicado":f"Proveedor {900+i%17}",
      "documento_proveedor":str(900+i%17),
      "valor_del_contrato":str(5_000_000+i*25_000),
    } for i in range(n_contracts)])

    h=chash(procesos_seq,"id_del_proceso")
    bench={
      "workers":4,
      "benchmark_rows":n,
      "rows_sequential":n,
      "rows_threaded":n,
      "seconds_sequential":8.2,
      "seconds_threaded":3.9,
      "hash_sequential":h,
      "hash_threaded":h,
      "same_rows":True,
      "same_hash":True,
    }

    data_contract={
      "procesos":{"id":"p6dx-8zbt","grain":"proceso de contratación","fields":sorted(V.PROCESS_FIELDS)},
      "contratos":{"id":"jbjy-vk9h","grain":"contrato electrónico","fields":sorted(V.CONTRACT_FIELDS)},
      "join":{"procesos.id_del_proceso":"contratos.proceso_de_compra"},
      "coverage":{
        "start":"2025-01-01T00:00:00.000",
        "latest_procesos":"2026-09-26T23:59:59.000",
        "latest_contratos":"2026-09-26T23:59:59.000",
        "years_required":[2025,2026],
      },
      "expected_rows":{"procesos":n,"contratos":n_contracts},
    }

    query_plan={
      "procesos":{
        "where":"fecha_de_publicacion_del >= '2025-01-01T00:00:00.000' AND fecha_de_publicacion_del <= '2026-09-26T23:59:59.000'",
        "order":"fecha_de_publicacion_del ASC,id_del_proceso ASC",
      },
      "contratos":{
        "where":"fecha_de_firma >= '2025-01-01T00:00:00.000' AND fecha_de_firma <= '2026-09-26T23:59:59.000'",
        "order":"fecha_de_firma ASC,id_contrato ASC",
      },
    }

    quality={
      "join_coverage":0.5,
      "procesos":{"rows":n},
      "contratos":{"rows":n_contracts},
      "years":{"procesos":[2025,2026],"contratos":[2025,2026]},
      "coverage_by_department":[],
    }

    acq={
      "schema":"2026-09-27-secoppipeline",
      "queried_at_utc":"2026-09-27T00:00:00+00:00",
      "coverage":{
        "start":"2025-01-01T00:00:00.000",
        "latest_procesos":"2026-09-26T23:59:59.000",
        "latest_contratos":"2026-09-26T23:59:59.000",
      },
      "workers":4,
      "datasets":{
        "procesos":{"id":"p6dx-8zbt","expected_rows":n,"rows":n,"requests":1},
        "contratos":{"id":"jbjy-vk9h","expected_rows":n_contracts,"rows":n_contracts,"requests":1},
      },
      "benchmark":bench,
    }

    for p in [
      raw/"procesos.parquet",raw/"contratos.parquet",
      out/"00_dataset_contract.json",out/"01_acquisition_manifest.json",
      out/"01_benchmark_threads.json",out/"01_quality_report.json",
      out/"01_cobertura_departamento.csv",
      out/"02_secop_integrado.parquet",out/"02_modelo_documental.json",
    ]:
      touch(p)

    idem={"count_after_first":n,"count_after_second":n,"duplicates_after_second":0}
    ref_a=n_contracts
    topdocs=sorted(
      [{"id_proceso":d["id_proceso"],"valor_contratos":float(d["contratos_resumen"]["valor_total"])} for d in docs],
      key=lambda x:(-x["valor_contratos"],x["id_proceso"])
    )[:10]
    atlas_resultados={
      "carga":{"documentos":n,"server_version":"8.0","idempotencia":idem,"indices":["id_proceso_1","compound"]},
      "consulta_a":{"filtro":{"x":1},"resultado":ref_a},
      "consulta_b":{"filtro":{},"proyeccion":{},"resultado":topdocs},
    }
    touch(out/"02_atlas_evidence.json",json.dumps(atlas_resultados))

    queue=[]
    for d in docs:
      base=float(d["proceso"]["precio_base"])
      valor=float(d["contratos_resumen"]["valor_total"])
      cantidad=int(d["contratos_resumen"]["cantidad"])
      if base>0 and cantidad>0:
        diff=valor-base
        queue.append({
          "id_proceso":d["id_proceso"],
          "precio_base":base,
          "valor_contratos":valor,
          "diferencia_valor":diff,
          "diferencia_abs":abs(diff),
          "anio":int(d["proceso"]["anio"]),
          "departamento":d["entidad"]["departamento"],
        })
    queue=sorted(queue,key=lambda x:(-x["diferencia_abs"],x["id_proceso"]))[:100]
    bandeja=pd.DataFrame(queue)
    bandeja.to_csv(out/"03_bandeja_historica.csv",index=False)

    concentracion_departamento=(
      bandeja.groupby("departamento",dropna=False)["valor_contratos"].sum().rename("valor_total").reset_index()
      .sort_values(["valor_total","departamento"],ascending=[False,True],kind="mergesort").reset_index(drop=True)
    )
    concentracion_departamento.to_csv(out/"03_concentracion_departamento.csv",index=False)

    bc=bandeja.copy()
    cql="""CREATE TABLE tc1.procesos_por_anio_departamento (
      anio int, departamento text, diferencia_abs double, id_proceso text,
      precio_base double, valor_contratos double,
      PRIMARY KEY ((anio, departamento), diferencia_abs, id_proceso)
    ) WITH CLUSTERING ORDER BY (diferencia_abs DESC, id_proceso ASC);"""
    touch(out/"04_modelo_cassandra.cql",cql)
    counts=(
      bc.groupby(["anio","departamento"],dropna=False).size().rename("n").reset_index()
      .sort_values(["n","anio","departamento"],ascending=[False,True,True],kind="mergesort").reset_index(drop=True)
    )
    rr=counts.iloc[0]
    part=(int(rr["anio"]),rr["departamento"])
    top10=(
      bc[(bc.anio==part[0])&(bc.departamento==part[1])]
      .sort_values(["diferencia_abs","id_proceso"],ascending=[False,True],kind="mergesort").head(10)
    )

    ref_hist=historico.copy()
    rank=(
      ref_hist.groupby("nit_entidad")["id_proceso"].nunique().rename("procesos").reset_index()
      .sort_values(["procesos","nit_entidad"],ascending=[False,True],kind="mergesort").reset_index(drop=True)
    )
    nit_ancla=str(rank.iloc[0]["nit_entidad"])
    ref_ancla=ref_hist[ref_hist.nit_entidad==nit_ancla]
    a=ref_ancla.groupby("nit_proveedor")["id_proceso"].nunique().rename("procesos_con_ancla").reset_index()
    g=ref_hist.groupby("nit_proveedor")["nit_entidad"].nunique().rename("entidades_conectadas").reset_index()
    rel=(
      a.merge(g,on="nit_proveedor")
      .sort_values(["entidades_conectadas","procesos_con_ancla","nit_proveedor"],ascending=[False,False,True],kind="mergesort")
      .reset_index(drop=True)
    )
    rel.to_csv(out/"05_resultado_relacional.csv",index=False)

    cy_load="UNWIND $rows AS row MERGE (e:Entidad {nit: row.nit_entidad}) MERGE (p:Proceso {id: row.id_proceso}) MERGE (v:Proveedor {nit: row.nit_proveedor})"
    cy_ctx="MATCH (e:Entidad {nit:$nit_ancla}) RETURN e"
    cy_share="MATCH (e:Entidad {nit:$nit_ancla})--(v:Proveedor)--(o:Entidad) WHERE o.nit <> $nit_ancla RETURN v,o"
    cy_rank="MATCH (v:Proveedor)--(e:Entidad) RETURN v.nit, count(distinct e) AS entidades"
    touch(out/"05_neo4j_consultas.cypher","\n".join([cy_load,cy_ctx,cy_share,cy_rank]))

    decisions=[
      {"decision":"4 workers","evidence":"mismo hash","alternative":"2 workers","risk":"429"},
      {"decision":"select reducido","evidence":"menos bytes","alternative":"todas las columnas","risk":"pérdida de campos"},
      {"decision":"upsert","evidence":"segunda carga estable","alternative":"insert_many","risk":"duplicados"},
    ]
    touch(out/"06_decision_log.json",json.dumps(decisions))

    report="""## 1. Adquisición y contrato de datos
El snapshot usa 2025 y 2026 y un corte consultado a la API.

## 2. Cobertura proceso → contrato
La cobertura del caso sintético es 0.50 y se interpreta como alcance del cruce.

## 3. Concentración y bandeja de revisión
La bandeja ordena diferencias absolutas y no demuestra fraude.

## 4. Modelo documental y Cassandra
El modelo conserva año, departamento y diferencia para la consulta operacional.

## 5. Red de proveedores, decisiones y límites
La conectividad contractual aporta contexto y no demuestra colusión.
"""
    touch(out/"06_informe_tecnico.md",report)

    respuestas_caso={
      "pregunta_1_cobertura":"La cobertura proceso a contrato es 0.50: 600 de 1200 procesos tienen un contrato relacionado. Los departamentos deben compararse con sus propios denominadores; una cobertura menor describe ausencia de relación en este snapshot y no permite afirmar incumplimiento ni pérdida de información fuera del corte.",
      "pregunta_2_concentracion":"La bandeja usa diferencia absoluta entre precio base y valor contratado y prioriza 100 procesos. En este caso sintético, los departamentos y entidades con mayor valor se identifican por agregación; una diferencia alta sirve para revisión analítica, pero no es una señal suficiente de fraude.",
      "pregunta_3_red":"La red contiene 17 proveedores sintéticos conectados con varias entidades. El proveedor con más entidades conectadas describe una posición estructural en la red contractual; esa conectividad permite priorizar contexto, pero no demuestra colusión, favorecimiento ni conducta irregular.",
    }
    touch(out/"06_respuestas_caso.json",json.dumps(respuestas_caso))

    ns={
      "OUT":out,
      "PAREJA_ID":"TEST-V5",
      "INTEGRANTE_1":"A","CODIGO_1":"1","INTEGRANTE_2":"B","CODIGO_2":"2",
      "data_contract":data_contract,
      "query_plan":query_plan,
      "procesos_seq":procesos_seq,
      "procesos_threads_benchmark":procesos_threads_benchmark,
      "procesos_df":procesos,
      "contratos_df":contratos,
      "benchmark_threads":bench,
      "acquisition_manifest":acq,
      "quality_report":quality,
      "historico":historico,
      "documentos":docs,
      "coleccion":FakeCollection(n),
      "atlas_ping":True,
      "atlas_server_version":"8.0",
      "atlas_idempotencia":idem,
      "atlas_indexes":["id_proceso_1","compound"],
      "filtro_a":{"x":1},
      "resultado_a":ref_a,
      "filtro_b":{},
      "proyeccion_b":{},
      "resultado_b":topdocs,
      "atlas_resultados":atlas_resultados,
      "pipeline_bandeja":[{"$match":{}},{"$addFields":{}},{"$sort":{}},{"$limit":100}],
      "bandeja_historica":bandeja,
      "concentracion_departamento":concentracion_departamento,
      "bandeja_cassandra":bc,
      "cql_create":cql,
      "particion_prueba":part,
      "top10_cassandra":top10,
      "hist_adjudicado":ref_hist,
      "nit_ancla":nit_ancla,
      "entidad_ancla":f"Entidad {nit_ancla}",
      "resultado_relacional":rel,
      "cypher_carga":cy_load,
      "cypher_contexto":cy_ctx,
      "cypher_compartidos":cy_share,
      "cypher_ranking":cy_rank,
      "G":nx.DiGraph(),
      "nodos_grafo":1+ref_ancla.id_proceso.nunique()+ref_ancla.nit_proveedor.nunique(),
      "aristas_grafo":ref_ancla.id_proceso.nunique()+ref_ancla[["id_proceso","nit_proveedor"]].drop_duplicates().shape[0],
      "decision_log":decisions,
      "informe_tecnico":report,
      "respuestas_caso":respuestas_caso,
    }

    manifest=V.evaluar(ns)
    assert manifest["puntaje"]==100, manifest
    assert manifest["maximo"]==100
    assert manifest["version"]==V.VERSION
    print("TC1 synthetic 100/100: OK")

if __name__=="__main__":
  main()
