from pathlib import Path
import json, re, hashlib, zipfile
import pandas as pd

VERSION = "2026-09-26-v4-secoppipeline"
STAGE_MAX = {"E1": 20, "E2": 30, "E3": 10, "E4": 15, "E5": 20, "E6": 5}
PROCESS_FIELDS = {
    "id_del_proceso","entidad","nit_entidad","departamento_entidad","ciudad_entidad",
    "fecha_de_publicacion","precio_base","modalidad_de_contratacion",
    "respuestas_al_procedimiento","estado_del_procedimiento","adjudicado",
    "nombre_del_proveedor_adjudicado","nit_del_proveedor_adjudicado","urlproceso",
}
CONTRACT_FIELDS = {
    "proceso_de_compra","id_contrato","estado_contrato","tipo_de_contrato",
    "modalidad_de_contratacion","fecha_de_firma","proveedor_adjudicado",
    "documento_proveedor","valor_del_contrato",
}

def _canon_df(df, key):
    if not isinstance(df, pd.DataFrame) or key not in df.columns:
        return None
    x=df.copy().sort_values(key,kind="mergesort").reset_index(drop=True)
    payload=x.to_json(orient="records",force_ascii=False,date_format="iso")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def _safe_float(x):
    try:
        if pd.isna(x): return None
        return float(x)
    except Exception:
        return None

def _read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
    except Exception:
        return None

def evaluar(ns):
    OUT=Path(ns.get("OUT","entrega_tc1")); OUT.mkdir(exist_ok=True)
    checks={}

    def check(k,ok,puntos,evidencia=""):
        ok=bool(ok)
        checks[k]={"ok":ok,"puntos":puntos if ok else 0,"maximo":puntos,"evidencia":str(evidencia)[:500]}
        print(("✅" if ok else "❌"),k,f"{checks[k]['puntos']}/{puntos}")

    pareja=str(ns.get("PAREJA_ID","")).strip()
    procesos=ns.get("procesos_df"); contratos=ns.get("contratos_df")
    procesos_seq=ns.get("procesos_seq")
    data_contract=ns.get("data_contract",{})
    query_plan=ns.get("query_plan",{})
    bench=ns.get("benchmark_threads",{})
    acq=ns.get("acquisition_manifest",{})
    quality=ns.get("quality_report",{})

    # E1 · 20
    try:
        q1=query_plan.get("procesos",{}); q2=query_plan.get("contratos",{})
        e11=(
            len(pareja)>=3
            and data_contract.get("procesos",{}).get("id")=="p6dx-8zbt"
            and data_contract.get("contratos",{}).get("id")=="jbjy-vk9h"
            and PROCESS_FIELDS.issubset(set(data_contract.get("procesos",{}).get("fields",[])))
            and CONTRACT_FIELDS.issubset(set(data_contract.get("contratos",{}).get("fields",[])))
            and isinstance(q1.get("where"),str) and "fecha_de_publicacion" in q1["where"]
            and isinstance(q2.get("where"),str) and "fecha_de_firma" in q2["where"]
            and "order" in q1 and "id_del_proceso" in q1["order"]
            and "order" in q2 and "id_contrato" in q2["order"]
            and (OUT/"00_dataset_contract.json").exists()
        )
    except Exception: e11=False
    check("E1_contrato_y_query",e11,4)

    try:
        e12=(
            isinstance(procesos_seq,pd.DataFrame) and len(procesos_seq)>=1000
            and PROCESS_FIELDS.issubset(set(procesos_seq.columns))
            and bench.get("rows_sequential")==len(procesos_seq)
            and isinstance(bench.get("seconds_sequential"),(int,float))
            and bench.get("seconds_sequential")>0
        )
    except Exception: e12=False
    check("E1_descarga_secuencial",e12,4,f"rows={0 if not isinstance(procesos_seq,pd.DataFrame) else len(procesos_seq)}")

    try:
        h_seq=_canon_df(procesos_seq,"id_del_proceso")
        h_thr=_canon_df(procesos,"id_del_proceso")
        workers=int(bench.get("workers",0))
        e13=(
            isinstance(procesos,pd.DataFrame) and len(procesos)>=1000
            and PROCESS_FIELDS.issubset(set(procesos.columns))
            and 2<=workers<=6
            and bench.get("rows_threaded")==len(procesos)
            and len(procesos)==len(procesos_seq)
            and h_seq is not None and h_seq==h_thr
            and bench.get("same_rows") is True and bench.get("same_hash") is True
            and bench.get("hash_sequential")==h_seq and bench.get("hash_threaded")==h_thr
            and isinstance(bench.get("seconds_threaded"),(int,float)) and bench["seconds_threaded"]>0
            and (OUT/"01_benchmark_threads.json").exists()
        )
    except Exception as e:
        print("E1.3",type(e).__name__,e); e13=False
    check("E1_concurrencia_equivalente",e13,6)

    try:
        join_cov=quality.get("join_coverage")
        raw_proc=(OUT/"raw"/"procesos.parquet")
        raw_cont=(OUT/"raw"/"contratos.parquet")
        secret_blob=json.dumps(acq,ensure_ascii=False).lower()
        e14=(
            isinstance(contratos,pd.DataFrame) and len(contratos)>=100
            and CONTRACT_FIELDS.issubset(set(contratos.columns))
            and isinstance(join_cov,(int,float)) and 0<=float(join_cov)<=1
            and isinstance(acq,dict) and acq.get("datasets",{}).get("procesos",{}).get("id")=="p6dx-8zbt"
            and acq.get("datasets",{}).get("contratos",{}).get("id")=="jbjy-vk9h"
            and int(acq.get("workers",0))==int(bench.get("workers",0))
            and "queried_at_utc" in acq
            and "password" not in secret_blob and "mongodb+srv" not in secret_blob and "app_token" not in secret_blob
            and isinstance(quality.get("procesos"),dict) and isinstance(quality.get("contratos"),dict)
            and raw_proc.exists() and raw_cont.exists()
            and (OUT/"01_acquisition_manifest.json").exists()
            and (OUT/"01_quality_report.json").exists()
        )
    except Exception as e:
        print("E1.4",type(e).__name__,e); e14=False
    check("E1_trazabilidad_calidad",e14,6)

    # E2 · 30
    historico=ns.get("historico"); documentos=ns.get("documentos")
    try:
        sample=documentos[:20] if isinstance(documentos,list) else []
        required_top={"id_proceso","entidad","proceso","proveedor_adjudicado","contratos_resumen","metadata_ingesta"}
        nested_ok=bool(sample) and all(required_top.issubset(d.keys()) for d in sample)
        cr_ok=all(isinstance(d.get("contratos_resumen"),dict) and {"cantidad","valor_total","estados"}.issubset(d["contratos_resumen"].keys()) for d in sample)
        e21=(
            isinstance(historico,pd.DataFrame) and len(historico)==len(procesos)
            and historico["id_proceso"].nunique()==len(historico)
            and isinstance(documentos,list) and len(documentos)==len(historico)
            and nested_ok and cr_ok
            and (OUT/"02_secop_integrado.parquet").exists()
            and (OUT/"02_modelo_documental.json").exists()
        )
    except Exception as e:
        print("E2.1",type(e).__name__,e); e21=False
    check("E2_modelo_documental",e21,6)

    coleccion=ns.get("coleccion")
    try:
        modulo=type(coleccion).__module__.casefold() if coleccion is not None else ""
        idem=ns.get("atlas_idempotencia",{})
        local_n=len(documentos) if isinstance(documentos,list) else -1
        remote=coleccion.count_documents({}) if coleccion is not None else -2
        e22=(
            coleccion is not None and "pymongo" in modulo
            and ns.get("atlas_ping") is True
            and isinstance(ns.get("atlas_server_version"),str) and bool(ns.get("atlas_server_version"))
            and remote==local_n and local_n>=1000
            and isinstance(idem,dict)
            and idem.get("count_after_first")==local_n
            and idem.get("count_after_second")==local_n
            and int(idem.get("duplicates_after_second",999))==0
        )
    except Exception as e:
        print("E2.2",type(e).__name__,e); e22=False
    check("E2_atlas_idempotente",e22,8)

    try:
        info=coleccion.index_information() if coleccion is not None else {}
        unique_id=any(v.get("unique") is True and any(k=="id_proceso" for k,_ in v.get("key",[])) for v in info.values())
        useful_compound=any(len(v.get("key",[]))>=2 for name,v in info.items() if name!="_id_")
        e23=unique_id and useful_compound and isinstance(ns.get("atlas_indexes"),list)
    except Exception: e23=False
    check("E2_indices",e23,5)

    try:
        ref_a=sum(
            1 for d in documentos
            if (_safe_float(d.get("proceso",{}).get("precio_base")) or 0)>0
            and int(d.get("contratos_resumen",{}).get("cantidad") or 0)>0
        )
        e24=isinstance(ns.get("filtro_a"),dict) and ns.get("resultado_a")==ref_a
    except Exception: e24=False
    check("E2_consulta_A_count",e24,4,ns.get("resultado_a"))

    try:
        ref_b=sorted(
            [
                {
                    "id_proceso":d.get("id_proceso"),
                    "valor_contratos":float(d.get("contratos_resumen",{}).get("valor_total") or 0),
                }
                for d in documentos
            ],
            key=lambda x:(-x["valor_contratos"],str(x["id_proceso"]))
        )[:10]
        got=ns.get("resultado_b",[])
        got2=[{"id_proceso":x.get("id_proceso"),"valor_contratos":float(x.get("valor_contratos") or 0)} for x in got]
        e25=got2==ref_b
    except Exception as e:
        print("E2.5",type(e).__name__,e); e25=False
    check("E2_consulta_B_find",e25,4)

    try:
        ar=ns.get("atlas_resultados",{})
        af=_read_json(OUT/"02_atlas_evidence.json")
        e26=(
            isinstance(ar,dict) and isinstance(af,dict)
            and ar.get("carga",{}).get("documentos")==len(documentos)
            and af.get("carga",{}).get("documentos")==len(documentos)
            and "consulta_a" in af and "consulta_b" in af
        )
    except Exception: e26=False
    check("E2_evidencia_atlas",e26,3)

    # E3 · 10
    bandeja=ns.get("bandeja_historica")
    try:
        ref=sorted(
            [
                {
                    "id_proceso":d.get("id_proceso"),
                    "valor_contratos":float(d.get("contratos_resumen",{}).get("valor_total") or 0),
                }
                for d in documentos
                if (_safe_float(d.get("proceso",{}).get("precio_base")) or 0)>0
                and int(d.get("contratos_resumen",{}).get("cantidad") or 0)>0
            ],
            key=lambda x:(-x["valor_contratos"],str(x["id_proceso"]))
        )[:100]
        ids_ref=[x["id_proceso"] for x in ref]
        e31=(
            isinstance(ns.get("pipeline_bandeja"),list) and len(ns.get("pipeline_bandeja"))>=3
            and isinstance(bandeja,pd.DataFrame)
            and list(bandeja["id_proceso"])==ids_ref
        )
    except Exception as e:
        print("E3.1",type(e).__name__,e); e31=False
    check("E3_pipeline_bandeja",e31,7)
    try:
        e32=(OUT/"03_bandeja_historica.csv").exists() and len(bandeja)<=100 and {"id_proceso","valor_contratos"}.issubset(bandeja.columns)
    except Exception:e32=False
    check("E3_artefacto_bandeja",e32,3)

    # E4 · 15
    bc=ns.get("bandeja_cassandra")
    try:
        e41=(
            isinstance(bc,pd.DataFrame) and len(bc)==len(bandeja)
            and {"anio","departamento","valor_contratos","id_proceso"}.issubset(bc.columns)
        )
    except Exception:e41=False
    check("E4_datos_cassandra",e41,5)

    try:
        cql=re.sub(r"\s+"," ",str(ns.get("cql_create","")).casefold())
        pk=re.search(r"primary\s+key\s*\(\s*\(\s*anio\s*,\s*departamento\s*\)\s*,\s*valor_contratos\s*,\s*id_proceso\s*\)",cql)
        order=re.search(r"clustering\s+order\s+by\s*\(\s*valor_contratos\s+desc\s*,\s*id_proceso\s+asc\s*\)",cql)
        e42="tc1.procesos_por_anio_departamento" in cql and pk is not None and order is not None and "allow filtering" not in cql and (OUT/"04_modelo_cassandra.cql").exists()
    except Exception:e42=False
    check("E4_modelo_query_first",e42,6)

    try:
        counts=(bc.groupby(["anio","departamento"],dropna=False).size().rename("n").reset_index()
                .sort_values(["n","anio","departamento"],ascending=[False,True,True],kind="mergesort").reset_index(drop=True))
        rr=counts.iloc[0]; ref_part=(int(rr["anio"]),rr["departamento"])
        ref_top=(bc[(bc["anio"]==ref_part[0])&(bc["departamento"]==ref_part[1])]
                 .sort_values(["valor_contratos","id_proceso"],ascending=[False,True],kind="mergesort").head(10))
        top=ns.get("top10_cassandra")
        e43=tuple(ns.get("particion_prueba"))==ref_part and isinstance(top,pd.DataFrame) and list(top["id_proceso"])==list(ref_top["id_proceso"])
    except Exception as e:
        print("E4.3",type(e).__name__,e); e43=False
    check("E4_consulta_simulada",e43,4)

    # E5 · 20
    try:
        h=historico.copy()
        mask=(
            h["adjudicado"].eq(True)
            & h["nit_entidad"].notna() & h["nit_proveedor"].notna()
            & h["nit_entidad"].astype(str).str.strip().ne("")
            & h["nit_proveedor"].astype(str).str.strip().ne("")
            & h["nit_proveedor"].astype(str).str.casefold().ne("no definido")
        )
        ref_hist=h[mask].copy()
        ref_hist["nit_entidad"]=ref_hist["nit_entidad"].astype(str).str.strip()
        ref_hist["nit_proveedor"]=ref_hist["nit_proveedor"].astype(str).str.strip()
        rank=(ref_hist.groupby("nit_entidad")["id_proceso"].nunique().rename("procesos").reset_index()
              .sort_values(["procesos","nit_entidad"],ascending=[False,True],kind="mergesort").reset_index(drop=True))
        ref_nit=str(rank.iloc[0]["nit_entidad"])
        ref_ancla=ref_hist[ref_hist["nit_entidad"]==ref_nit]
        hh=ns.get("hist_adjudicado")
        e51=isinstance(hh,pd.DataFrame) and list(hh["id_proceso"])==list(ref_hist["id_proceso"]) and str(ns.get("nit_ancla"))==ref_nit and ns.get("entidad_ancla") is not None
    except Exception as e:
        print("E5.1",type(e).__name__,e); e51=False; ref_hist=pd.DataFrame(); ref_ancla=pd.DataFrame()
    check("E5_historial_y_ancla",e51,5)

    try:
        a=ref_ancla.groupby("nit_proveedor")["id_proceso"].nunique().rename("procesos_con_ancla").reset_index()
        g=ref_hist.groupby("nit_proveedor")["nit_entidad"].nunique().rename("entidades_conectadas").reset_index()
        ref_rel=a.merge(g,on="nit_proveedor").sort_values(["entidades_conectadas","procesos_con_ancla","nit_proveedor"],ascending=[False,False,True],kind="mergesort").reset_index(drop=True)
        got=ns.get("resultado_relacional")
        e52=isinstance(got,pd.DataFrame) and list(got["nit_proveedor"].astype(str))==list(ref_rel["nit_proveedor"].astype(str)) and list(got["entidades_conectadas"])==list(ref_rel["entidades_conectadas"]) and (OUT/"05_resultado_relacional.csv").exists()
    except Exception:e52=False
    check("E5_metrica_relacional",e52,6)

    try:
        qc=re.sub(r"\s+"," ",str(ns.get("cypher_carga","")).casefold())
        q1=str(ns.get("cypher_contexto","")).casefold(); q2=str(ns.get("cypher_compartidos","")).casefold(); q3=str(ns.get("cypher_ranking","")).casefold()
        e53=(
            "unwind $rows" in qc and "merge" in qc and ":entidad" in qc and ":proceso" in qc and ":proveedor" in qc
            and "$nit_ancla" in q1 and "$nit_ancla" in q2 and ("<>" in q2 or "!=" in q2)
            and "count(distinct" in q3 and (OUT/"05_neo4j_consultas.cypher").exists()
        )
    except Exception:e53=False
    check("E5_cypher",e53,6)

    try:
        import networkx as nx
        G=ns.get("G")
        np_=ref_ancla["id_proceso"].nunique(); nv_=ref_ancla["nit_proveedor"].nunique()
        edge_pp=ref_ancla[["id_proceso","nit_proveedor"]].drop_duplicates().shape[0]
        e54=isinstance(G,nx.DiGraph) and ns.get("nodos_grafo")==1+np_+nv_ and ns.get("aristas_grafo")==np_+edge_pp
    except Exception:e54=False
    check("E5_subgrafo",e54,3)

    # E6 · 5
    decisions=ns.get("decision_log",[])
    informe=str(ns.get("informe_tecnico","")); inf=informe.casefold()
    try:
        e61=(
            isinstance(decisions,list) and len(decisions)>=3
            and all(isinstance(d,dict) and all(str(d.get(k,"")).strip() for k in ["decision","evidence","alternative","risk"]) for d in decisions[:3])
            and (OUT/"06_decision_log.json").exists()
            and all(x in inf for x in [
                "## 1. adquisición y contrato de datos",
                "## 2. concurrencia, robustez y calidad",
                "## 3. modelo documental e idempotencia atlas",
                "## 4. producto analítico y cassandra",
                "## 5. neo4j, decisiones y límites",
            ])
            and re.search(r"no\s+(demuestra|prueba)",inf) is not None
            and (OUT/"06_informe_tecnico.md").exists()
        )
    except Exception:e61=False
    check("E6_decisiones_informe",e61,3)

    files=[
        "00_dataset_contract.json","01_acquisition_manifest.json","01_benchmark_threads.json","01_quality_report.json",
        "02_secop_integrado.parquet","02_modelo_documental.json","02_atlas_evidence.json",
        "03_bandeja_historica.csv","04_modelo_cassandra.cql","05_neo4j_consultas.cypher",
        "05_resultado_relacional.csv","06_decision_log.json","06_informe_tecnico.md",
    ]
    e62=all((OUT/f).exists() and (OUT/f).stat().st_size>0 for f in files)
    check("E6_paquete_reproducible",e62,2)

    puntaje=sum(x["puntos"] for x in checks.values()); maximo=sum(x["maximo"] for x in checks.values())
    assert maximo==100, f"El validador debe sumar 100, suma {maximo}"
    nota=round(1+4*puntaje/maximo,2)
    manifest={
        "taller":"TC1 V4 · SECOP Data Pipeline",
        "version":VERSION,
        "pareja_id":pareja,
        "integrantes":[
            {"nombre":ns.get("INTEGRANTE_1",""),"codigo":ns.get("CODIGO_1","")},
            {"nombre":ns.get("INTEGRANTE_2",""),"codigo":ns.get("CODIGO_2","")},
        ],
        "puntaje":puntaje,"maximo":maximo,"nota_5":nota,
        "controles":checks,"artefactos":files,
    }
    previo=json.dumps(manifest,ensure_ascii=False,indent=2)
    manifest["sha256"]=hashlib.sha256(previo.encode("utf-8")).hexdigest()
    (OUT/"manifest_tc1.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")

    safe_pair=re.sub(r"[^A-Za-z0-9_-]+","_",pareja or "pareja")
    zip_path=Path(f"TC1_{safe_pair}.zip")
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(OUT.rglob("*")):
            if p.is_file():
                zf.write(p,arcname=str(p.relative_to(OUT)))
    print("="*72)
    print(f"RESULTADO: {puntaje}/{maximo} · NOTA {nota}/5.0")
    print("ENTREGA:",zip_path)
    print("SHA-256:",manifest["sha256"])
    print("="*72)
    return manifest
