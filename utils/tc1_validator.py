from pathlib import Path
import json, re, hashlib, zipfile
import pandas as pd

VERSION = "2026-10-01-secoppipeline-v6"
STAGE_MAX = {"E1": 25, "E2": 25, "E3": 10, "E4": 15, "E5": 15, "E6": 10}
FEEDBACK = {
    "E1_contrato_y_query": "Revise el contrato de datos y el plan SoQL: fuente, campos, filtros y orden estable deben corresponder a la ventana asignada.",
    "E1_descarga_secuencial": "La descarga secuencial debe producir exactamente la población objetivo real de su ventana; no se exige un mínimo artificial de 1.000 filas.",
    "E1_concurrencia_equivalente": "Compare en igualdad de condiciones: mismos offsets, mismas filas y mismo hash canónico. El speedup puede ser menor que 1.",
    "E1_trazabilidad_calidad": "Guarde RAW consolidado y páginas reanudables con firma/SHA-256; no deben quedar .part, el manifest debe enumerar los offsets y el cruce id_del_portafolio → proceso_de_compra debe producir población relacional (>0).",
    "E2_modelo_documental": "Construya un documento coherente por proceso y conserve el snapshot integrado como evidencia.",
    "E2_atlas_idempotente": "La colección debe ser real y la segunda ejecución no puede aumentar el número de documentos.",
    "E2_indices": "Debe existir un índice único de identidad y al menos un índice adicional justificado por una consulta.",
    "E2_consulta_A_count": "Recalcule la consulta A directamente en Atlas y contraste el conteo con el snapshot local.",
    "E2_consulta_B_find": "El top 10 debe coincidir con el orden de referencia: valor contractual descendente e id_proceso ascendente.",
    "E2_evidencia_atlas": "Registre carga, consultas e índices en 02_atlas_evidence.json sin credenciales.",
    "E3_pipeline_bandeja": "La bandeja debe derivarse de Atlas y conservar exactamente la priorización especificada.",
    "E3_artefacto_bandeja": "Exporte la bandeja con las columnas y límite requeridos.",
    "E4_datos_cassandra": "Prepare el DataFrame operacional con año, departamento, valor e identificador.",
    "E4_modelo_query_first": "Diseñe la PRIMARY KEY desde la consulta objetivo y evite ALLOW FILTERING.",
    "E4_consulta_simulada": "La simulación debe devolver el mismo top 10 que el patrón query-first definido.",
    "E5_historial_y_ancla": "Construya relaciones desde contratos realmente enlazados por id_del_portafolio → proceso_de_compra y derive la entidad ancla por número de contratos.",
    "E5_metrica_relacional": "La métrica de proveedores compartidos debe coincidir con el cálculo tabular sobre contratos enlazados.",
    "E5_cypher": "El Cypher debe cargar Entidad–Contrato–Proveedor con MERGE/UNWIND y responder las consultas parametrizadas solicitadas.",
    "E5_subgrafo": "El subgrafo NetworkX debe representar la estructura Entidad–Contrato–Proveedor de la entidad ancla.",
    "E6_decisiones_informe": "Complete las tres decisiones estructuradas; el informe se genera con evidencia de su propia ejecución y declara límites explícitos.",
    "E6_microdefensa_grupal": "Complete las dos decisiones cerradas de transferencia sobre HTTP 429 y cobertura del cruce.",
    "E6_paquete_reproducible": "Complete todos los artefactos requeridos antes de generar la entrega final.",
}

PROCESS_FIELDS = {
    "id_del_proceso","id_del_portafolio","entidad","nit_entidad","departamento_entidad","ciudad_entidad",
    "fecha_de_publicacion_del","precio_base","modalidad_de_contratacion",
    "respuestas_al_procedimiento","estado_del_procedimiento","adjudicado",
    "nombre_del_proveedor","nit_del_proveedor_adjudicado","urlproceso",
}
CONTRACT_FIELDS = {
    "proceso_de_compra","id_contrato","estado_contrato","tipo_de_contrato",
    "modalidad_de_contratacion","fecha_de_firma","nombre_entidad","nit_entidad",
    "proveedor_adjudicado","documento_proveedor","valor_del_contrato",
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

def _validate_page_cache(cache_dir, expected_offsets):
    cache_dir=Path(cache_dir)
    if not cache_dir.exists(): return False, "cache ausente"
    if list(cache_dir.glob("*.part")): return False, "quedaron archivos .part"
    expected=[int(x) for x in expected_offsets]
    seen=[]
    for offset in expected:
        stem=f"page_{offset:07d}"
        data_path=cache_dir/f"{stem}.json"
        meta_path=cache_dir/f"{stem}.meta.json"
        if not data_path.exists() or not meta_path.exists():
            return False, f"falta chunk {offset}"
        try:
            raw=data_path.read_bytes()
            meta=json.loads(meta_path.read_text(encoding="utf-8"))
            rows=json.loads(raw.decode("utf-8"))
        except Exception:
            return False, f"chunk ilegible {offset}"
        if not isinstance(rows,list): return False, f"chunk no es lista {offset}"
        if int(meta.get("offset",-1))!=offset: return False, f"offset metadata inválido {offset}"
        if int(meta.get("rows",-1))!=len(rows): return False, f"conteo metadata inválido {offset}"
        if not re.fullmatch(r"[0-9a-f]{64}",str(meta.get("query_signature",""))): return False, f"firma inválida {offset}"
        sha=hashlib.sha256(raw).hexdigest()
        if meta.get("sha256")!=sha: return False, f"sha inválido {offset}"
        seen.append(offset)
    extras=[]
    for p in cache_dir.glob("page_*.json"):
        if p.name.endswith(".meta.json"): continue
        m=re.fullmatch(r"page_(\d{7})\.json",p.name)
        if m and int(m.group(1)) not in expected: extras.append(int(m.group(1)))
    if extras: return False, "chunks extra: "+",".join(map(str,extras))
    return seen==expected, f"{len(seen)} chunks válidos"

def evaluar(ns):
    OUT=Path(ns.get("OUT","entrega_tc1")); OUT.mkdir(exist_ok=True)
    checks={}

    def check(k,ok,puntos,evidencia=""):
        ok=bool(ok)
        checks[k]={
            "ok":ok,
            "puntos":puntos if ok else 0,
            "maximo":puntos,
            "evidencia":str(evidencia)[:500],
            "feedback":"" if ok else FEEDBACK.get(k,"Revise la evidencia y vuelva a ejecutar el criterio.")
        }
        print(("✅" if ok else "❌"),k,f"{checks[k]['puntos']}/{puntos}")
        if not ok:
            print("   ↳",checks[k]["feedback"])

    pareja=str(ns.get("PAREJA_ID","")).strip()
    procesos=ns.get("procesos_df"); contratos=ns.get("contratos_df")
    procesos_seq=ns.get("procesos_seq")
    data_contract=ns.get("data_contract",{})
    query_plan=ns.get("query_plan",{})
    bench=ns.get("benchmark_threads",{})
    acq=ns.get("acquisition_manifest",{})
    quality=ns.get("quality_report",{})

    # E1 · 25
    try:
        q1=query_plan.get("procesos",{}); q2=query_plan.get("contratos",{})
        e11=(
            len(pareja)>=3
            and data_contract.get("procesos",{}).get("id")=="p6dx-8zbt"
            and data_contract.get("contratos",{}).get("id")=="jbjy-vk9h"
            and PROCESS_FIELDS.issubset(set(data_contract.get("procesos",{}).get("fields",[])))
            and CONTRACT_FIELDS.issubset(set(data_contract.get("contratos",{}).get("fields",[])))
            and data_contract.get("join",{}).get("procesos.id_del_portafolio")=="contratos.proceso_de_compra"
            and isinstance(q1.get("where"),str) and "fecha_de_publicacion_del" in q1["where"]
            and isinstance(q2.get("where"),str) and "fecha_de_firma" in q2["where"]
            and "order" in q1 and "fecha_de_publicacion_del" in q1["order"] and "id_del_proceso" in q1["order"]
            and "order" in q2 and "id_contrato" in q2["order"]
            and (OUT/"00_dataset_contract.json").exists()
        )
    except Exception: e11=False
    check("E1_contrato_y_query",e11,4)

    expected_n=int(ns.get("N_PROCESOS",0) or 0)
    expected_offsets=list(ns.get("OFFSETS_PROCESOS",[]) or [])
    try:
        e12=(
            expected_n>0
            and isinstance(procesos_seq,pd.DataFrame) and len(procesos_seq)==expected_n
            and PROCESS_FIELDS.issubset(set(procesos_seq.columns))
            and bench.get("rows_sequential")==len(procesos_seq)
            and int(bench.get("target_rows",0) or 0)==expected_n
            and isinstance(bench.get("seconds_sequential"),(int,float))
            and bench.get("seconds_sequential")>0
        )
    except Exception: e12=False
    check("E1_descarga_secuencial",e12,4,f"rows={0 if not isinstance(procesos_seq,pd.DataFrame) else len(procesos_seq)}; objetivo={expected_n}")

    try:
        h_seq=_canon_df(procesos_seq,"id_del_proceso")
        h_thr=_canon_df(procesos,"id_del_proceso")
        workers=int(bench.get("workers",0))
        off_seq=list(bench.get("offsets_sequential",[]) or [])
        off_thr=list(bench.get("offsets_threaded",[]) or [])
        e13=(
            expected_n>0
            and isinstance(procesos,pd.DataFrame) and len(procesos)==expected_n
            and PROCESS_FIELDS.issubset(set(procesos.columns))
            and 2<=workers<=6
            and bench.get("rows_threaded")==len(procesos)
            and len(procesos)==len(procesos_seq)
            and off_seq==expected_offsets and off_thr==expected_offsets and bench.get("same_offsets") is True
            and h_seq is not None and h_seq==h_thr
            and bench.get("same_rows") is True and bench.get("same_hash") is True
            and bench.get("hash_sequential")==h_seq and bench.get("hash_threaded")==h_thr
            and isinstance(bench.get("seconds_threaded"),(int,float)) and bench["seconds_threaded"]>0
            and (OUT/"01_benchmark_threads.json").exists()
        )
    except Exception as e:
        print("E1.3",type(e).__name__,e); e13=False
    check("E1_concurrencia_equivalente",e13,8)

    try:
        join_cov=quality.get("join_coverage")
        matched=int(quality.get("matched_processes",0) or 0)
        raw_proc=(OUT/"raw"/"procesos.parquet")
        raw_cont=(OUT/"raw"/"contratos.parquet")
        secret_blob=json.dumps(acq,ensure_ascii=False).lower()

        expected_proc=list(ns.get("OFFSETS_PROCESOS",[]) or [])
        expected_cont=list(ns.get("OFFSETS_CONTRATOS",[]) or [])
        raw_pages=Path(ns.get("RAW_PAGES",OUT/"raw"/"pages"))
        cache_seq=Path(ns.get("CACHE_SEQ_PROCESOS",raw_pages/"procesos"/"sequential"))
        cache_thr=Path(ns.get("CACHE_THR_PROCESOS",raw_pages/"procesos"/"threaded"))
        cache_cont=Path(ns.get("CACHE_CONTRATOS",raw_pages/"contratos"/"official"))
        seq_ok,seq_ev=_validate_page_cache(cache_seq,expected_proc)
        thr_ok,thr_ev=_validate_page_cache(cache_thr,expected_proc)
        cont_ok,cont_ev=_validate_page_cache(cache_cont,expected_cont)

        pages_seq=acq.get("datasets",{}).get("procesos",{}).get("pages_sequential",[])
        pages_thr=acq.get("datasets",{}).get("procesos",{}).get("pages_threaded",[])
        pages_cont=acq.get("datasets",{}).get("contratos",{}).get("pages",[])
        man_offsets_seq=[int(x.get("offset",-1)) for x in pages_seq]
        man_offsets_thr=[int(x.get("offset",-1)) for x in pages_thr]
        man_offsets_cont=[int(x.get("offset",-1)) for x in pages_cont]
        page_fields=lambda xs: all(
            isinstance(x,dict)
            and re.fullmatch(r"[0-9a-f]{64}",str(x.get("sha256","")))
            and re.fullmatch(r"[0-9a-f]{64}",str(x.get("query_signature","")))
            and int(x.get("rows",-1))>=0
            for x in xs
        )

        e14=(
            isinstance(contratos,pd.DataFrame) and len(contratos)>0
            and CONTRACT_FIELDS.issubset(set(contratos.columns))
            and isinstance(join_cov,(int,float)) and 0<float(join_cov)<=1 and matched>0
            and quality.get("join_key")=="id_del_portafolio -> proceso_de_compra"
            and isinstance(acq,dict) and acq.get("schema")=="2026-10-01-secoppipeline-v6"
            and acq.get("datasets",{}).get("procesos",{}).get("id")=="p6dx-8zbt"
            and acq.get("datasets",{}).get("contratos",{}).get("id")=="jbjy-vk9h"
            and acq.get("datasets",{}).get("procesos",{}).get("snapshot_sha256")==bench.get("hash_threaded")
            and re.fullmatch(r"[0-9a-f]{64}",str(acq.get("datasets",{}).get("contratos",{}).get("snapshot_sha256","")))
            and man_offsets_seq==expected_proc and man_offsets_thr==expected_proc and man_offsets_cont==expected_cont
            and page_fields(pages_seq) and page_fields(pages_thr) and page_fields(pages_cont)
            and seq_ok and thr_ok and cont_ok
            and int(acq.get("workers",0))==int(bench.get("workers",0))
            and "queried_at_utc" in acq
            and "password" not in secret_blob and "mongodb+srv" not in secret_blob and "app_token" not in secret_blob
            and isinstance(quality.get("procesos"),dict) and isinstance(quality.get("contratos"),dict)
            and raw_proc.exists() and raw_cont.exists()
            and (OUT/"01_acquisition_manifest.json").exists()
            and (OUT/"01_quality_report.json").exists()
        )
        e14_ev=f"seq={seq_ev}; threaded={thr_ev}; contratos={cont_ev}; join={join_cov:.4f}"
    except Exception as e:
        print("E1.4",type(e).__name__,e); e14=False; e14_ev=str(e)
    check("E1_trazabilidad_calidad",e14,9,e14_ev)

    # E2 · 25
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
    check("E2_modelo_documental",e21,5)

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
            and remote==local_n and local_n>=1
            and isinstance(idem,dict)
            and idem.get("count_after_first")==local_n
            and idem.get("count_after_second")==local_n
            and int(idem.get("duplicates_after_second",999))==0
        )
    except Exception as e:
        print("E2.2",type(e).__name__,e); e22=False
    check("E2_atlas_idempotente",e22,7)

    try:
        info=coleccion.index_information() if coleccion is not None else {}
        unique_id=any(v.get("unique") is True and any(k=="id_proceso" for k,_ in v.get("key",[])) for v in info.values())
        additional_index=any(
            name!="_id_"
            and not (len(v.get("key",[]))==1 and v.get("key",[])[0][0]=="id_proceso")
            for name,v in info.items()
        )
        e23=unique_id and additional_index and isinstance(ns.get("atlas_indexes"),list)
    except Exception: e23=False
    check("E2_indices",e23,4)

    try:
        ref_a=sum(
            1 for d in documentos
            if (_safe_float(d.get("proceso",{}).get("precio_base")) or 0)>0
            and int(d.get("contratos_resumen",{}).get("cantidad") or 0)>0
        )
        e24=isinstance(ns.get("filtro_a"),dict) and ns.get("resultado_a")==ref_a
    except Exception: e24=False
    check("E2_consulta_A_count",e24,3,ns.get("resultado_a"))

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
    check("E2_consulta_B_find",e25,3)

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

    # E5 · 15
    relaciones=ns.get("relaciones_contrato")
    try:
        pmap=procesos[["id_del_portafolio","id_del_proceso"]].copy()
        pmap=pmap.dropna(subset=["id_del_portafolio","id_del_proceso"])
        pmap["id_del_portafolio"]=pmap["id_del_portafolio"].astype(str).str.strip()
        pmap["id_del_proceso"]=pmap["id_del_proceso"].astype(str).str.strip()
        pmap=pmap[pmap["id_del_portafolio"].ne("")].drop_duplicates("id_del_portafolio")
        pmap=pmap.rename(columns={"id_del_proceso":"id_proceso"})

        rc=contratos.copy()
        rc["proceso_de_compra"]=rc["proceso_de_compra"].fillna("").astype(str).str.strip()
        rc=rc.merge(pmap,left_on="proceso_de_compra",right_on="id_del_portafolio",how="inner")
        rc["nit_entidad"]=rc["nit_entidad"].fillna("").astype(str).str.strip()
        rc["nit_proveedor"]=rc["documento_proveedor"].fillna("").astype(str).str.strip()
        rc["entidad"]=rc["nombre_entidad"].fillna("").astype(str).str.strip()
        rc["proveedor"]=rc["proveedor_adjudicado"].fillna("").astype(str).str.strip()
        rc["id_contrato"]=rc["id_contrato"].fillna("").astype(str).str.strip()
        ref_rel=rc[
            rc["nit_entidad"].ne("")
            & rc["nit_proveedor"].ne("")
            & rc["id_contrato"].ne("")
            & rc["nit_proveedor"].str.casefold().ne("no definido")
        ][["id_contrato","id_proceso","nit_entidad","entidad","nit_proveedor","proveedor"]].copy()
        ref_rel=ref_rel.sort_values(["id_contrato","id_proceso","nit_proveedor"],kind="mergesort").reset_index(drop=True)

        req_cols=["id_contrato","id_proceso","nit_entidad","entidad","nit_proveedor","proveedor"]
        got_rel=relaciones[req_cols].copy() if isinstance(relaciones,pd.DataFrame) else pd.DataFrame()
        for c in req_cols:
            if c in got_rel: got_rel[c]=got_rel[c].fillna("").astype(str).str.strip()
        got_rel=got_rel.sort_values(["id_contrato","id_proceso","nit_proveedor"],kind="mergesort").reset_index(drop=True)

        rank=(ref_rel.groupby("nit_entidad")["id_contrato"].nunique().rename("contratos").reset_index()
              .sort_values(["contratos","nit_entidad"],ascending=[False,True],kind="mergesort").reset_index(drop=True))
        ref_nit=str(rank.iloc[0]["nit_entidad"])
        ref_ancla=ref_rel[ref_rel["nit_entidad"]==ref_nit].copy()
        ref_entidad=str(ref_ancla["entidad"].dropna().iloc[0]) if len(ref_ancla) else ""
        e51=(
            len(ref_rel)>0
            and isinstance(relaciones,pd.DataFrame)
            and got_rel.to_dict("records")==ref_rel.to_dict("records")
            and str(ns.get("nit_ancla"))==ref_nit
            and str(ns.get("entidad_ancla","")).strip()==ref_entidad
        )
    except Exception as e:
        print("E5.1",type(e).__name__,e); e51=False; ref_rel=pd.DataFrame(); ref_ancla=pd.DataFrame()
    check("E5_historial_y_ancla",e51,4)

    try:
        a=ref_ancla.groupby("nit_proveedor")["id_contrato"].nunique().rename("contratos_con_ancla").reset_index()
        g=ref_rel.groupby("nit_proveedor")["nit_entidad"].nunique().rename("entidades_conectadas").reset_index()
        ref_metric=a.merge(g,on="nit_proveedor").sort_values(
            ["entidades_conectadas","contratos_con_ancla","nit_proveedor"],
            ascending=[False,False,True],kind="mergesort"
        ).reset_index(drop=True)
        got=ns.get("resultado_relacional")
        e52=(
            isinstance(got,pd.DataFrame)
            and {"nit_proveedor","contratos_con_ancla","entidades_conectadas"}.issubset(got.columns)
            and list(got["nit_proveedor"].astype(str))==list(ref_metric["nit_proveedor"].astype(str))
            and list(got["contratos_con_ancla"])==list(ref_metric["contratos_con_ancla"])
            and list(got["entidades_conectadas"])==list(ref_metric["entidades_conectadas"])
            and (OUT/"05_resultado_relacional.csv").exists()
        )
    except Exception:e52=False
    check("E5_metrica_relacional",e52,4)

    try:
        qc=re.sub(r"\s+"," ",str(ns.get("cypher_carga","")).casefold())
        q1=str(ns.get("cypher_contexto","")).casefold(); q2=str(ns.get("cypher_compartidos","")).casefold(); q3=str(ns.get("cypher_ranking","")).casefold()
        e53=(
            "unwind $rows" in qc and "merge" in qc and ":entidad" in qc and ":contrato" in qc and ":proveedor" in qc
            and "$nit_ancla" in q1 and "$nit_ancla" in q2 and ("<>" in q2 or "!=" in q2)
            and "count(distinct" in q3 and (OUT/"05_neo4j_consultas.cypher").exists()
        )
    except Exception:e53=False
    check("E5_cypher",e53,5)

    try:
        import networkx as nx
        G=ns.get("G")
        nc_=ref_ancla["id_contrato"].nunique(); nv_=ref_ancla["nit_proveedor"].nunique()
        edge_cp=ref_ancla[["id_contrato","nit_proveedor"]].drop_duplicates().shape[0]
        e54=isinstance(G,nx.DiGraph) and ns.get("nodos_grafo")==1+nc_+nv_ and ns.get("aristas_grafo")==nc_+edge_cp
    except Exception:e54=False
    check("E5_subgrafo",e54,2)

    # E6 · 10
    decisions=ns.get("decision_log",[])
    informe=str(ns.get("informe_tecnico","")); inf=informe.casefold()
    try:
        e61=(
            ns.get("decision_429")==ns.get("CORRECT_429")
            and ns.get("decision_indice")==ns.get("CORRECT_INDICE")
            and ns.get("decision_limite")==ns.get("CORRECT_LIMITE")
            and isinstance(decisions,list) and len(decisions)==3
            and all(isinstance(d,dict) and all(str(d.get(k,"")).strip() for k in ["decision","evidence","alternative","risk"]) for d in decisions)
            and (OUT/"06_decision_log.json").exists()
            and all(x in inf for x in [
                "## 1. adquisición y contrato de datos",
                "## 2. concurrencia, robustez y calidad",
                "## 3. modelo documental e idempotencia atlas",
                "## 4. producto analítico y cassandra",
                "## 5. neo4j, decisiones y límites",
            ])
            and "no demuestran fraude ni causalidad" in inf
            and (OUT/"06_informe_tecnico.md").exists()
        )
    except Exception:e61=False
    check("E6_decisiones_informe",e61,5)

    defensa=ns.get("defensa_grupal",{})
    try:
        d1=defensa.get("escenario_429",{})
        d2=defensa.get("escenario_cobertura",{})
        e62=(
            ns.get("respuesta_429")==ns.get("CORRECT_DEFENSA_429")
            and ns.get("respuesta_cobertura")==ns.get("CORRECT_DEFENSA_COBERTURA")
            and isinstance(defensa,dict)
            and int(d1.get("workers_observados",0) or 0)==int(bench.get("workers",0) or 0)
            and d1.get("same_hash") is True
            and isinstance(d2.get("join_coverage"),(int,float))
            and abs(float(d2.get("join_coverage"))-float(quality.get("join_coverage")))<1e-12
            and int(d2.get("matched_processes",0) or 0)==int(quality.get("matched_processes",0) or 0)
            and (OUT/"06_microdefensa_grupal.json").exists()
        )
    except Exception:e62=False
    check("E6_microdefensa_grupal",e62,3)

    files=[
        "00_dataset_contract.json","01_acquisition_manifest.json","01_benchmark_threads.json","01_quality_report.json",
        "02_secop_integrado.parquet","02_modelo_documental.json","02_atlas_evidence.json",
        "03_bandeja_historica.csv","04_modelo_cassandra.cql","05_neo4j_consultas.cypher",
        "05_resultado_relacional.csv","06_decision_log.json","06_informe_tecnico.md","06_microdefensa_grupal.json",
    ]
    e63=all((OUT/f).exists() and (OUT/f).stat().st_size>0 for f in files)
    check("E6_paquete_reproducible",e63,2)

    secret_patterns=[
        re.compile(r"mongodb\+srv://[^\s:@/]+:[^\s@]+@",re.I),
        re.compile(r"(?i)(x-app-token|app_token)\s*[:=]\s*['\"][A-Za-z0-9_-]{8,}"),
        re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{4,}"),
    ]
    secret_hits=[]
    for p in OUT.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in {".json",".csv",".md",".cql",".cypher",".txt",".ipynb"}:
            continue
        try:
            txt=p.read_text(encoding="utf-8",errors="ignore")
        except Exception:
            continue
        if any(rx.search(txt) for rx in secret_patterns):
            secret_hits.append(str(p.relative_to(OUT)))

    notebook_json=ns.get("notebook_json_for_secret_scan")
    if notebook_json is not None:
        try:
            notebook_blob=json.dumps(notebook_json,ensure_ascii=False)
            if any(rx.search(notebook_blob) for rx in secret_patterns):
                secret_hits.append("notebook_ejecutado.ipynb")
        except Exception:
            pass

    gates={
        "security_no_secrets":{
            "ok":not secret_hits,
            "message":"Sin secretos detectados." if not secret_hits else "Elimine credenciales o tokens de: "+", ".join(secret_hits)
        }
    }

    puntaje=sum(x["puntos"] for x in checks.values()); maximo=sum(x["maximo"] for x in checks.values())
    assert maximo==100, f"El validador debe sumar 100, suma {maximo}"
    nota=round(1+4*puntaje/maximo,2)
    manifest={
        "taller":"TC1 · SECOP Data Pipeline",
        "version":VERSION,
        "pareja_id":pareja,
        "integrantes":[
            {"nombre":ns.get("INTEGRANTE_1",""),"codigo":ns.get("CODIGO_1","")},
            {"nombre":ns.get("INTEGRANTE_2",""),"codigo":ns.get("CODIGO_2","")},
        ],
        "puntaje":puntaje,"maximo":maximo,"nota_5":nota,
        "controles":checks,"gates":gates,
        "feedback_summary":[{"control":k,"feedback":v["feedback"]} for k,v in checks.items() if not v["ok"]],
        "artefactos":files,
    }
    previo=json.dumps(manifest,ensure_ascii=False,indent=2)
    manifest["sha256"]=hashlib.sha256(previo.encode("utf-8")).hexdigest()
    (OUT/"manifest_tc1.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")

    safe_pair=re.sub(r"[^A-Za-z0-9_-]+","_",pareja or "pareja")
    zip_path=Path(f"TC1_{safe_pair}.zip")
    print("="*72)
    print(f"RESULTADO: {puntaje}/{maximo} · NOTA {nota}/5.0")
    if secret_hits:
        print("ENTREGA BLOQUEADA: se detectaron posibles secretos. Corrija antes de generar el ZIP.")
        print("ARCHIVOS/ORIGEN:", ", ".join(secret_hits))
    else:
        with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(OUT.rglob("*")):
                if p.is_file():
                    zf.write(p,arcname=str(p.relative_to(OUT)))
        print("ENTREGA:",zip_path)
    print("SHA-256:",manifest["sha256"])
    print("="*72)
    return manifest
