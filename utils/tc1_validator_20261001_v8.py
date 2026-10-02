from pathlib import Path
import hashlib, json, math, re, zipfile
import pandas as pd

VERSION = "2026-10-01-tc1-native-v8"
STAGE_MAX = {"E1":15, "E2":30, "E3":20, "E4":25, "E5":10}

def _truthy(x):
    return bool(x)

def _norm(s):
    return re.sub(r"\s+"," ",str(s or "")).strip().lower()

def _num(x):
    try:
        return float(x)
    except Exception:
        return None

def _close(a,b,tol=1e-6):
    a=_num(a); b=_num(b)
    if a is None or b is None: return False
    return abs(a-b) <= max(tol, abs(b)*1e-9)

def _validate_page_cache(cache_dir, expected_offsets):
    cache_dir=Path(cache_dir)
    if not cache_dir.exists():
        return False, "cache ausente"
    if list(cache_dir.glob("*.part")):
        return False, "quedaron archivos .part"

    expected=set(int(x) for x in expected_offsets)
    seen=set()
    for data_path in sorted(cache_dir.glob("page_*.json")):
        m=re.fullmatch(r"page_(\d{7})\.json", data_path.name)
        if not m:
            continue
        offset=int(m.group(1))
        meta_path=data_path.with_name(data_path.stem+".meta.json")
        if not meta_path.exists():
            return False, f"falta metadata para offset {offset}"
        try:
            raw=data_path.read_bytes()
            rows=json.loads(raw.decode("utf-8"))
            meta=json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return False, f"chunk ilegible {offset}: {exc}"
        if not isinstance(rows,list):
            return False, f"chunk no es lista {offset}"
        if int(meta.get("offset",-1)) != offset:
            return False, f"offset metadata inválido {offset}"
        if int(meta.get("rows",-1)) != len(rows):
            return False, f"conteo metadata inválido {offset}"
        if not re.fullmatch(r"[0-9a-f]{64}", str(meta.get("query_signature",""))):
            return False, f"firma inválida {offset}"
        if meta.get("sha256") != hashlib.sha256(raw).hexdigest():
            return False, f"sha inválido {offset}"
        seen.add(offset)

    extras=sorted(seen-expected)
    missing=sorted(expected-seen)
    if extras:
        return False, "chunks extra: "+",".join(map(str,extras))
    if missing:
        return False, "faltan chunks: "+",".join(map(str,missing))
    return True, f"{len(seen)} chunks válidos"

def _atlas_pipeline_ok(pipeline, departamento):
    if not isinstance(pipeline,list) or len(pipeline) < 4:
        return False, "el pipeline debe tener al menos $match, $group, $sort y $limit"
    stages=[next(iter(x.keys()),"") if isinstance(x,dict) and x else "" for x in pipeline]
    needed=["$match","$group","$sort","$limit"]
    pos=[]
    for k in needed:
        try: pos.append(stages.index(k))
        except ValueError: return False, f"falta etapa {k}"
    if pos != sorted(pos):
        return False, "las etapas deben conservar el orden match → group → sort → limit"

    match=pipeline[pos[0]].get("$match",{})
    if str(match.get("entidad.departamento","")).strip() != str(departamento).strip():
        return False, "$match no usa el departamento asignado"
    shared=match.get("red.proveedores_compartidos")
    if not (isinstance(shared,dict) and _num(shared.get("$gt")) == 0):
        return False, "$match debe exigir red.proveedores_compartidos > 0"

    group=pipeline[pos[1]].get("$group",{})
    gid=group.get("_id")
    if not isinstance(gid,dict):
        return False, "$group debe agrupar por NIT y nombre"
    if gid.get("nit") != "$entidad.nit" or gid.get("nombre") != "$entidad.nombre":
        return False, "$group debe usar entidad.nit y entidad.nombre"
    valor=group.get("valor_total")
    if not (isinstance(valor,dict) and valor.get("$sum") == "$contratos.valor_total"):
        return False, "$group debe sumar contratos.valor_total"

    sort=pipeline[pos[2]].get("$sort",{})
    if _num(sort.get("valor_total")) != -1 or _num(sort.get("_id.nit")) != 1:
        return False, "$sort debe ser valor_total DESC y _id.nit ASC"
    if int(pipeline[pos[3]].get("$limit",0) or 0) != 5:
        return False, "$limit debe ser 5"
    return True, "pipeline Atlas correcto"

def _cql_design_ok(cql):
    s=_norm(cql)
    if "allow filtering" in s:
        return False, "no use ALLOW FILTERING"
    pk=re.search(r"primary\s+key\s*\(\s*\(\s*corte\s*,\s*departamento\s*\)\s*,\s*valor_contratos\s*,\s*id_proceso\s*\)",s,re.I)
    clustering=re.search(r"clustering\s+order\s+by\s*\(\s*valor_contratos\s+desc\s*,\s*id_proceso\s+asc\s*\)",s,re.I)
    if not pk:
        return False, "PRIMARY KEY no corresponde a corte + departamento → valor + id"
    if not clustering:
        return False, "CLUSTERING ORDER BY debe ser valor DESC, id ASC"
    return True, "diseño query-first correcto"

def _cypher_ok(q):
    s=_norm(q)
    required=["match","publica","adjudicado_a","otra.nit <> a.nit","count(distinct otra)","order by otras_entidades desc","limit 5"]
    missing=[x for x in required if x not in s]
    if missing:
        return False, "faltan elementos Cypher: "+", ".join(missing)
    return True, "consulta Cypher relacional correcta"

def _scan_secrets(paths):
    pats=[
        re.compile(r"mongodb\+srv://[^\s]+:[^\s]+@",re.I),
        re.compile(r"AstraCS:[A-Za-z0-9_-]{20,}",re.I),
        re.compile(r"(?:password|contrase(?:n|ñ)a)\s*[:=]\s*['\"][^'\"]{4,}",re.I),
    ]
    hits=[]
    for p in paths:
        p=Path(p)
        if not p.exists() or p.suffix.lower() not in {".json",".cql",".cypher",".md",".txt"}:
            continue
        try: txt=p.read_text(encoding="utf-8",errors="ignore")
        except Exception: continue
        if any(rx.search(txt) for rx in pats):
            hits.append(p.name)
    return hits

def evaluar(ns):
    OUT=Path(ns.get("OUT","entrega_tc1"))
    RAW=Path(ns.get("RAW",OUT/"raw"))
    OUT.mkdir(parents=True,exist_ok=True)

    scores={k:0 for k in STAGE_MAX}
    checks=[]
    def check(stage,label,ok,pts,evidence=""):
        if ok: scores[stage]+=pts
        checks.append({"stage":stage,"label":label,"ok":bool(ok),"points":pts if ok else 0,"max":pts,"evidence":str(evidence)})
        icon="✅" if ok else "❌"
        print(f"{icon} {stage} · {label}: {pts if ok else 0}/{pts}")
        if not ok and evidence:
            print("   ↳",evidence)

    # ---------- E1 ----------
    data_contract=ns.get("data_contract",{})
    bench=ns.get("benchmark_threads",{})
    acq=ns.get("acquisition_manifest",{})
    quality=ns.get("quality_report",{})
    matched=int(ns.get("matched_processes",0) or 0)

    e11=(
        data_contract.get("procesos",{}).get("id")=="p6dx-8zbt"
        and data_contract.get("contratos",{}).get("id")=="jbjy-vk9h"
        and data_contract.get("join",{}).get("procesos.id_del_portafolio")=="contratos.proceso_de_compra"
    )
    check("E1","Contrato de datos",e11,3,"endpoints y clave de cruce")

    e12=all(bool(bench.get(k)) for k in ["same_offsets","same_rows","same_hash"])
    check("E1","Secuencial = concurrente",e12,4,f"offsets={bench.get('same_offsets')} rows={bench.get('same_rows')} hash={bench.get('same_hash')}")

    seq_ok,seq_ev=_validate_page_cache(ns.get("CACHE_SEQ_PROCESOS",""),ns.get("OFFSETS_PROCESOS",[]))
    thr_ok,thr_ev=_validate_page_cache(ns.get("CACHE_THR_PROCESOS",""),ns.get("OFFSETS_PROCESOS",[]))
    con_ok,con_ev=_validate_page_cache(ns.get("CACHE_CONTRATOS",""),ns.get("OFFSETS_CONTRATOS",[]))
    check("E1","Cache íntegro",seq_ok and thr_ok and con_ok,4,f"seq={seq_ev}; threads={thr_ev}; contratos={con_ev}")

    e14=(
        acq.get("schema")==VERSION
        and matched>=30
        and _num(quality.get("join_coverage")) is not None
        and (RAW/"procesos.parquet").exists()
        and (RAW/"contratos.parquet").exists()
    )
    check("E1","RAW reutilizable y población relacional",e14,4,f"matched={matched}; join={quality.get('join_coverage')}; schema={acq.get('schema')}")

    # ---------- E2 ----------
    historico=ns.get("historico")
    documentos=ns.get("documentos")
    esperado=ns.get("ATLAS_ESPERADO",{})
    dept=ns.get("DEPARTAMENTO_OBJETIVO","")
    model_ok=(
        isinstance(historico,pd.DataFrame)
        and isinstance(documentos,list)
        and len(documentos)==historico["id_proceso"].nunique()
        and bool(dept)
        and bool(esperado)
        and (OUT/"02_atlas_documentos.json").exists()
    )
    check("E2","Modelo documental preparado",model_ok,5,f"documentos={len(documentos) if isinstance(documentos,list) else 'NA'}; departamento={dept}")

    pipeline=ns.get("atlas_pipeline_student")
    p_ok,p_ev=_atlas_pipeline_ok(pipeline,dept)
    check("E2","Pipeline real de Atlas",p_ok,10,p_ev)

    atlas_ev=ns.get("atlas_evidence",{})
    top_ok=(
        str(atlas_ev.get("top_nit","")).strip()==str(esperado.get("nit_entidad","")).strip()
        and _close(atlas_ev.get("top_valor"),esperado.get("valor_total"))
    )
    check("E2","Resultado de priorización Atlas",top_ok,10,f"esperado NIT={esperado.get('nit_entidad')} valor={esperado.get('valor_total')}; recibido NIT={atlas_ev.get('top_nit')} valor={atlas_ev.get('top_valor')}")

    expected_name=f"tc1_{str(ns.get('PAREJA_ID','')).strip()}_priorizacion".lower()
    saved_ok=str(atlas_ev.get("pipeline_guardado","")).strip().lower()==expected_name
    check("E2","Pipeline guardado",saved_ok,5,f"nombre esperado={expected_name}")

    # ---------- E3 ----------
    cql_ev=ns.get("astra_evidence",{})
    cql_ok,cql_msg=_cql_design_ok(cql_ev.get("create_table",""))
    check("E3","Diseño Cassandra query-first",cql_ok,10,cql_msg)

    got_ids=[str(x).strip() for x in cql_ev.get("top5_ids",[]) if str(x).strip()]
    exp_ids=[str(x).strip() for x in ns.get("ASTRA_TOP5_ESPERADO",[]) if str(x).strip()]
    ids_ok=(len(exp_ids)==5 and got_ids==exp_ids and (OUT/"03_astra_carga.cql").exists())
    check("E3","Top 5 de CQL Console",ids_ok,10,f"esperado={exp_ids}; recibido={got_ids}")

    # ---------- E4 ----------
    neo_ev=ns.get("neo4j_evidence",{})
    cy_ok,cy_msg=_cypher_ok(neo_ev.get("query",""))
    check("E4","Consulta Cypher relacional",cy_ok,10,cy_msg)

    neo_exp=ns.get("NEO4J_ESPERADO",{})
    neo_result=(
        str(neo_ev.get("nit_proveedor","")).strip()==str(neo_exp.get("nit_proveedor","")).strip()
        and int(neo_ev.get("otras_entidades",0) or 0)==int(neo_exp.get("otras_entidades",0) or 0)
    )
    check("E4","Resultado de Aura Query",neo_result,10,f"esperado NIT={neo_exp.get('nit_proveedor')} otras={neo_exp.get('otras_entidades')}; recibido NIT={neo_ev.get('nit_proveedor')} otras={neo_ev.get('otras_entidades')}")

    load_ok=(
        (OUT/"04_neo4j_carga.cypher").exists()
        and bool(ns.get("ENTIDAD_ANCLA_NIT"))
        and isinstance(ns.get("rel_grafo"),pd.DataFrame)
        and len(ns.get("rel_grafo"))>0
    )
    check("E4","Subgrafo cargable de la entidad ancla",load_ok,5,f"ancla={ns.get('ENTIDAD_ANCLA_NIT')}; relaciones={len(ns.get('rel_grafo')) if isinstance(ns.get('rel_grafo'),pd.DataFrame) else 0}")

    # ---------- E5 ----------
    d=ns.get("decision_log",{})
    decision_ok=(
        d.get("rol_atlas")=="Explorar/agregar documentos flexibles y priorizar entidades"
        and d.get("rol_cassandra")=="Servir repetidamente corte + departamento → top 5"
        and d.get("rol_neo4j")=="Recorrer proveedores compartidos entre entidades"
        and d.get("limite_relacional")=="Un proveedor compartido describe conectividad, no prueba irregularidad"
    )
    check("E5","Decisiones de modelo",decision_ok,6,"seleccione el papel correcto de cada motor y el límite de interpretación")

    # Evidence artifacts are generated from structured values.
    evidence_paths=[]
    artifacts={
        "02_atlas_evidencia.json": ns.get("atlas_evidence",{}),
        "03_astra_evidencia.json": ns.get("astra_evidence",{}),
        "04_neo4j_evidencia.json": ns.get("neo4j_evidence",{}),
        "05_decisiones.json": ns.get("decision_log",{}),
    }
    for name,obj in artifacts.items():
        p=OUT/name
        p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")
        evidence_paths.append(p)

    secret_paths=list(OUT.glob("*.json"))+list(OUT.glob("*.cql"))+list(OUT.glob("*.cypher"))
    secret_hits=_scan_secrets(secret_paths)
    security_ok=not secret_hits
    check("E5","Seguridad de la entrega",security_ok,4,"archivos con posible secreto: "+",".join(secret_hits) if secret_hits else "sin secretos detectados")

    total=sum(scores.values())
    note=round(1+4*(total/100),2)

    manifest={
        "validator_version":VERSION,
        "pair_id":str(ns.get("PAREJA_ID","")),
        "score":total,
        "grade_1_to_5":note,
        "rubric_scores":scores,
        "checks":checks,
        "case":{
            "department":dept,
            "anchor_nit":str(ns.get("ENTIDAD_ANCLA_NIT","")),
            "anchor_entity":str(ns.get("ENTIDAD_ANCLA","")),
        },
        "security_no_secrets":security_ok,
    }
    manifest_path=OUT/"manifest_tc1.json"
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")

    package_candidates=[
        OUT/"00_dataset_contract.json",
        OUT/"01_acquisition_manifest.json",
        OUT/"01_benchmark_threads.json",
        OUT/"01_quality_report.json",
        RAW/"procesos.parquet",
        RAW/"contratos.parquet",
        OUT/"02_atlas_documentos.json",
        OUT/"02_atlas_evidencia.json",
        OUT/"03_astra_carga.cql",
        OUT/"03_astra_evidencia.json",
        OUT/"04_neo4j_carga.cypher",
        OUT/"04_neo4j_evidencia.json",
        OUT/"05_decisiones.json",
        manifest_path,
    ]

    zip_path=OUT/f"TC1_{str(ns.get('PAREJA_ID','EQUIPO')).strip() or 'EQUIPO'}.zip"
    if security_ok:
        with zipfile.ZipFile(zip_path,"w",compression=zipfile.ZIP_DEFLATED) as z:
            for p in package_candidates:
                if Path(p).exists():
                    p=Path(p)
                    arc=("raw/"+p.name) if p.parent==RAW else p.name
                    z.write(p,arcname=arc)
    else:
        if zip_path.exists(): zip_path.unlink()

    print("="*72)
    print(f"RESULTADO: {total}/100 · NOTA {note}/5.0")
    if security_ok:
        print("ENTREGA:",zip_path.name)
        print("SHA-256:",hashlib.sha256(zip_path.read_bytes()).hexdigest())
    else:
        print("ENTREGA BLOQUEADA: elimine secretos y vuelva a validar.")
    print("="*72)
    return manifest
