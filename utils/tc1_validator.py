from pathlib import Path
import json, re, hashlib, zipfile
import pandas as pd

VERSION = "2026-09-17-v3-historico-atlas"

EXPECTED_FIELDS = [
    "id_proceso", "entidad", "nit_entidad", "departamento", "ciudad",
    "fecha_publicacion", "anio", "precio_base", "modalidad", "respuestas",
    "estado", "adjudicado", "proveedor", "nit_proveedor", "url", "archivo_origen",
]

EXPECTED_CHUNKS = {
    "prueba_chunk_0000000.csv",
    "prueba_chunk_0001000.csv",
    "prueba_chunk_0002000.csv",
    "prueba_chunk_0003000.csv",
    "prueba_chunk_0004000.csv",
    "prueba_chunk_0005000.csv",
}


def _canon(rows):
    out = []
    for row in rows:
        d = dict(row)
        d.pop("_id", None)
        for k, v in list(d.items()):
            if isinstance(v, float):
                d[k] = round(v, 7)
        out.append(d)
    return out


def _safe_num(x):
    try:
        if pd.isna(x):
            return None
        return float(x)
    except Exception:
        return None


def evaluar(ns):
    OUT = Path(ns.get("OUT", "entrega_tc1"))
    OUT.mkdir(exist_ok=True)
    checks = {}

    def check(k, ok, puntos, evidencia=""):
        ok = bool(ok)
        checks[k] = {
            "ok": ok,
            "puntos": puntos if ok else 0,
            "maximo": puntos,
            "evidencia": str(evidencia)[:500],
        }
        print(("✅" if ok else "❌"), k, f"{checks[k]['puntos']}/{puntos}")

    fragmentos = ns.get("fragmentos")
    secop_historico = ns.get("secop_historico")
    historico = ns.get("historico")
    documentos = ns.get("documentos")
    control = ns.get("control_ingesta", {})

    # E1 — 20 puntos
    try:
        e11 = (
            isinstance(fragmentos, list)
            and len(fragmentos) == 6
            and all(isinstance(x, pd.DataFrame) and len(x) == 1000 for x in fragmentos)
            and isinstance(secop_historico, pd.DataFrame)
            and len(secop_historico) == 6000
            and "archivo_origen" in secop_historico.columns
            and set(secop_historico["archivo_origen"].dropna().astype(str)) == EXPECTED_CHUNKS
        )
    except Exception as e:
        print("E1.1", type(e).__name__, e)
        e11 = False
    check("E1_integracion_6_archivos", e11, 5)

    try:
        e12 = (
            isinstance(historico, pd.DataFrame)
            and len(historico) == 6000
            and list(historico.columns) == EXPECTED_FIELDS
            and pd.api.types.is_datetime64_any_dtype(historico["fecha_publicacion"])
            and pd.api.types.is_numeric_dtype(historico["precio_base"])
            and pd.api.types.is_numeric_dtype(historico["respuestas"])
            and pd.api.types.is_bool_dtype(historico["adjudicado"])
        )
    except Exception as e:
        print("E1.2", type(e).__name__, e)
        e12 = False
    check("E1_esquema_y_tipos", e12, 7)

    try:
        archivo_json = OUT / "01_secop_historico_6000.json"
        archivo_control = OUT / "01_control_ingesta.json"
        docs_archivo = json.loads(archivo_json.read_text(encoding="utf-8")) if archivo_json.exists() else []
        control_archivo = json.loads(archivo_control.read_text(encoding="utf-8")) if archivo_control.exists() else {}
        base_ok = (
            isinstance(documentos, list)
            and len(documentos) == len(historico) == 6000
            and len(docs_archivo) == 6000
            and all(set(d.keys()) == set(EXPECTED_FIELDS) for d in documentos[:20])
            and all(str(d.get("precio_base", "")).lower() != "nan" for d in documentos[:100])
        )
        anios = pd.to_numeric(historico["anio"], errors="coerce")
        esperado_control = {
            "archivos_cargados": 6,
            "filas_integradas": len(historico),
            "procesos_unicos": int(historico["id_proceso"].nunique()),
            "departamentos": int(historico["departamento"].nunique(dropna=True)),
            "anio_min": int(anios.min()) if anios.notna().any() else None,
            "anio_max": int(anios.max()) if anios.notna().any() else None,
            "documentos_json": len(documentos),
        }
        e13 = base_ok and all(control.get(k) == v for k, v in esperado_control.items()) and all(
            control_archivo.get(k) == v for k, v in esperado_control.items()
        )
    except Exception as e:
        print("E1.3", type(e).__name__, e)
        e13 = False
    check("E1_json_y_control", e13, 8, control)

    # E2 — 30 puntos
    coleccion = ns.get("coleccion")
    try:
        modulo_coleccion = type(coleccion).__module__.casefold() if coleccion is not None else ""
        documentos_atlas = ns.get("documentos_atlas")
        e21 = (
            coleccion is not None
            and "pymongo" in modulo_coleccion
            and ns.get("atlas_ping") is True
            and isinstance(ns.get("atlas_server_version"), str)
            and bool(ns.get("atlas_server_version"))
            and documentos_atlas == 6000
            and coleccion.count_documents({}) == 6000
        )
    except Exception as e:
        print("E2.1", type(e).__name__, e)
        e21 = False
    check("E2_atlas_real_y_carga", e21, 8)

    try:
        ref_a = sum(
            1
            for d in documentos
            if isinstance(d.get("anio"), (int, float))
            and d.get("anio") >= 2024
            and "directa" in str(d.get("modalidad", "")).casefold()
            and d.get("respuestas") == 0
            and (_safe_num(d.get("precio_base")) or 0) > 0
        )
        filtro_a = ns.get("filtro_a", {})
        resultado_a = ns.get("resultado_a")
        e22 = isinstance(filtro_a, dict) and resultado_a == ref_a and isinstance(resultado_a, int)
    except Exception as e:
        print("E2.2", type(e).__name__, e)
        e22 = False
        ref_a = None
    check("E2_consulta_A_count", e22, 6, f"resultado={ns.get('resultado_a')}")

    try:
        ref_b_df = pd.DataFrame([
            {
                "id_proceso": d.get("id_proceso"),
                "entidad": d.get("entidad"),
                "precio_base": d.get("precio_base"),
                "modalidad": d.get("modalidad"),
            }
            for d in documentos
            if d.get("anio") == 2025
            and d.get("departamento") == "Antioquia"
            and (_safe_num(d.get("precio_base")) or 0) > 0
        ])
        if len(ref_b_df):
            ref_b_df = ref_b_df.sort_values(
                ["precio_base", "id_proceso"], ascending=[False, True], kind="mergesort"
            ).head(10)
            ref_b = ref_b_df.to_dict("records")
        else:
            ref_b = []
        resultado_b = ns.get("resultado_b", [])
        filtro_b = ns.get("filtro_b", {})
        proy_b = ns.get("proyeccion_b", {})
        e23 = (
            isinstance(filtro_b, dict)
            and isinstance(proy_b, dict)
            and _canon(resultado_b) == _canon(ref_b)
            and proy_b.get("_id") == 0
            and all(proy_b.get(k) == 1 for k in ["id_proceso", "entidad", "precio_base", "modalidad"])
        )
    except Exception as e:
        print("E2.3", type(e).__name__, e)
        e23 = False
    check("E2_consulta_B_find", e23, 7)

    try:
        base_c = pd.DataFrame(documentos)
        base_c["precio_base"] = pd.to_numeric(base_c["precio_base"], errors="coerce")
        base_c["anio"] = pd.to_numeric(base_c["anio"], errors="coerce")
        base_c = base_c[(base_c["anio"] >= 2024) & (base_c["precio_base"] > 0)].copy()
        ref_c_df = (
            base_c.groupby("departamento", dropna=False)
            .agg(
                procesos=("id_proceso", "size"),
                valor_total=("precio_base", "sum"),
                valor_promedio=("precio_base", "mean"),
            )
            .reset_index()
            .rename(columns={"departamento": "_id"})
            .sort_values(["procesos", "_id"], ascending=[False, True], kind="mergesort")
            .head(8)
        )
        ref_c = ref_c_df.to_dict("records")
        resultado_c = ns.get("resultado_c", [])
        pipeline_c = ns.get("pipeline_c", [])
        e24 = isinstance(pipeline_c, list) and len(pipeline_c) == 4 and _canon(resultado_c) == _canon(ref_c)
    except Exception as e:
        print("E2.4", type(e).__name__, e)
        e24 = False
    check("E2_consulta_C_aggregate", e24, 7)

    try:
        ar = ns.get("atlas_resultados", {})
        archivo = OUT / "02_atlas_consultas.json"
        cargado = json.loads(archivo.read_text(encoding="utf-8")) if archivo.exists() else {}
        e25 = (
            archivo.exists()
            and isinstance(ar, dict)
            and ar.get("carga", {}).get("documentos") == 6000
            and ar.get("consulta_a", {}).get("resultado") == ref_a
            and cargado.get("carga", {}).get("documentos") == 6000
            and "consulta_b" in cargado
            and "consulta_c" in cargado
        )
    except Exception as e:
        print("E2.5", type(e).__name__, e)
        e25 = False
    check("E2_evidencia_atlas", e25, 2)

    # E3 — 10 puntos
    try:
        ref_band = pd.DataFrame([
            d for d in documentos
            if isinstance(d.get("anio"), (int, float))
            and d.get("anio") >= 2024
            and d.get("adjudicado") is True
            and (_safe_num(d.get("precio_base")) or 0) >= 50_000_000
            and d.get("respuestas") is not None
            and _safe_num(d.get("respuestas")) is not None
            and _safe_num(d.get("respuestas")) <= 1
        ])
        campos_band = [
            "id_proceso", "entidad", "nit_entidad", "departamento",
            "fecha_publicacion", "anio", "precio_base", "respuestas",
            "proveedor", "nit_proveedor", "url",
        ]
        if len(ref_band):
            ref_band = ref_band.sort_values(
                ["precio_base", "fecha_publicacion", "id_proceso"],
                ascending=[False, False, True], kind="mergesort",
            ).head(100)[campos_band].reset_index(drop=True)
        else:
            ref_band = pd.DataFrame(columns=campos_band)
        bandeja = ns.get("bandeja_historica")
        pipe_band = ns.get("pipeline_bandeja", [])
        ids_ok = isinstance(bandeja, pd.DataFrame) and list(bandeja["id_proceso"]) == list(ref_band["id_proceso"])
        e31 = isinstance(pipe_band, list) and len(pipe_band) == 4 and ids_ok
        e32 = (
            (OUT / "03_bandeja_historica.csv").exists()
            and isinstance(bandeja, pd.DataFrame)
            and len(bandeja) == len(ref_band)
            and set(campos_band).issubset(bandeja.columns)
        )
    except Exception as e:
        print("E3", type(e).__name__, e)
        e31 = e32 = False
    check("E3_pipeline_bandeja", e31, 7)
    check("E3_artefacto_bandeja", e32, 3)

    # E4 — 15 puntos
    try:
        bc = ns.get("bandeja_cassandra")
        e41 = (
            isinstance(bc, pd.DataFrame)
            and isinstance(ns.get("bandeja_historica"), pd.DataFrame)
            and len(bc) == len(ns.get("bandeja_historica"))
            and {"anio", "departamento", "fecha_publicacion", "precio_base", "id_proceso"}.issubset(bc.columns)
            and pd.api.types.is_datetime64_any_dtype(bc["fecha_publicacion"])
        )
    except Exception as e:
        print("E4.1", type(e).__name__, e)
        e41 = False
    check("E4_datos_cassandra", e41, 5)

    try:
        cql = re.sub(r"\s+", " ", str(ns.get("cql_create", "")).casefold())
        pk = re.search(
            r"primary\s+key\s*\(\s*\(\s*anio\s*,\s*departamento\s*\)\s*,\s*fecha_publicacion\s*,\s*precio_base\s*,\s*id_proceso\s*\)", cql,
        )
        order = re.search(
            r"clustering\s+order\s+by\s*\(\s*fecha_publicacion\s+desc\s*,\s*precio_base\s+desc\s*,\s*id_proceso\s+asc\s*\)", cql,
        )
        e42 = (
            "tc1.procesos_por_anio_departamento" in cql
            and pk is not None and order is not None
            and "allow filtering" not in cql
            and (OUT / "04_modelo_cassandra.cql").exists()
        )
    except Exception as e:
        print("E4.2", type(e).__name__, e)
        e42 = False
    check("E4_modelo_query_first", e42, 6)

    try:
        ref_bc = bc.copy()
        conteos = (
            ref_bc.groupby(["anio", "departamento"], dropna=False).size().rename("n").reset_index()
            .sort_values(["n", "anio", "departamento"], ascending=[False, True, True], kind="mergesort")
            .reset_index(drop=True)
        )
        r0 = conteos.iloc[0]
        ref_part = (int(r0["anio"]), r0["departamento"])
        ref_top = (
            ref_bc[(ref_bc["anio"] == ref_part[0]) & (ref_bc["departamento"] == ref_part[1])]
            .sort_values(["fecha_publicacion", "precio_base", "id_proceso"], ascending=[False, False, True], kind="mergesort")
            .head(10)
        )
        top10 = ns.get("top10_cassandra")
        part = ns.get("particion_prueba")
        e43 = tuple(part) == tuple(ref_part) and isinstance(top10, pd.DataFrame) and list(top10["id_proceso"]) == list(ref_top["id_proceso"])
    except Exception as e:
        print("E4.3", type(e).__name__, e)
        e43 = False
    check("E4_consulta_simulada", e43, 4)

    # E5 — 20 puntos
    try:
        h = historico.copy()
        mask = (
            h["adjudicado"].eq(True)
            & h["nit_proveedor"].notna() & h["nit_entidad"].notna()
            & h["nit_proveedor"].astype(str).str.strip().ne("")
            & h["nit_entidad"].astype(str).str.strip().ne("")
            & h["nit_proveedor"].astype(str).str.strip().str.casefold().ne("no definido")
        )
        ref_hist = h[mask].copy()
        ref_hist["nit_proveedor"] = ref_hist["nit_proveedor"].astype(str).str.strip()
        ref_hist["nit_entidad"] = ref_hist["nit_entidad"].astype(str).str.strip()
        rank = (
            ref_hist.groupby("nit_entidad")["id_proceso"].nunique().rename("procesos").reset_index()
            .sort_values(["procesos", "nit_entidad"], ascending=[False, True], kind="mergesort").reset_index(drop=True)
        )
        ref_nit = str(rank.iloc[0]["nit_entidad"])
        ref_ancla = ref_hist[ref_hist["nit_entidad"] == ref_nit].copy()
        e51 = (
            isinstance(ns.get("hist_adjudicado"), pd.DataFrame)
            and list(ns.get("hist_adjudicado")["id_proceso"]) == list(ref_hist["id_proceso"])
            and str(ns.get("nit_ancla")) == ref_nit
            and ns.get("entidad_ancla") is not None
        )
    except Exception as e:
        print("E5.1", type(e).__name__, e)
        e51 = False
        ref_hist = pd.DataFrame(); ref_ancla = pd.DataFrame(); ref_nit = None
    check("E5_historial_y_ancla", e51, 5)

    try:
        rpa = ref_ancla.groupby("nit_proveedor")["id_proceso"].nunique().rename("procesos_con_ancla").reset_index()
        rpg = ref_hist.groupby("nit_proveedor")["nit_entidad"].nunique().rename("entidades_conectadas").reset_index()
        ref_rel = (
            rpa.merge(rpg, on="nit_proveedor", how="left")
            .sort_values(["entidades_conectadas", "procesos_con_ancla", "nit_proveedor"], ascending=[False, False, True], kind="mergesort")
            .reset_index(drop=True)
        )
        res = ns.get("resultado_relacional")
        e52 = (
            isinstance(res, pd.DataFrame)
            and list(res["nit_proveedor"].astype(str)) == list(ref_rel["nit_proveedor"].astype(str))
            and list(res["procesos_con_ancla"]) == list(ref_rel["procesos_con_ancla"])
            and list(res["entidades_conectadas"]) == list(ref_rel["entidades_conectadas"])
            and (OUT / "05_resultado_relacional.csv").exists()
        )
    except Exception as e:
        print("E5.2", type(e).__name__, e)
        e52 = False
    check("E5_metrica_relacional", e52, 6)

    try:
        qc = re.sub(r"\s+", " ", str(ns.get("cypher_carga", "")).casefold())
        q1 = re.sub(r"\s+", " ", str(ns.get("cypher_contexto", "")).casefold())
        q2 = re.sub(r"\s+", " ", str(ns.get("cypher_compartidos", "")).casefold())
        q3 = re.sub(r"\s+", " ", str(ns.get("cypher_ranking", "")).casefold())
        e53 = (
            "unwind $rows" in qc and "merge" in qc
            and ":entidad" in qc and ":proceso" in qc and ":proveedor" in qc
            and ":publica" in qc and ":adjudicado_a" in qc
            and "$nit_ancla" in q1 and "$nit_ancla" in q2
            and ("<>" in q2 or "!=" in q2)
            and "count(distinct" in q3 and "order by" in q3
            and (OUT / "05_neo4j_consultas.cypher").exists()
        )
    except Exception as e:
        print("E5.3", type(e).__name__, e)
        e53 = False
    check("E5_cypher", e53, 6)

    try:
        import networkx as nx
        G = ns.get("G")
        np_ = ref_ancla["id_proceso"].nunique()
        nv_ = ref_ancla["nit_proveedor"].nunique()
        edge_pp = ref_ancla[["id_proceso", "nit_proveedor"]].drop_duplicates().shape[0]
        ref_nodes = 1 + np_ + nv_
        ref_edges = np_ + edge_pp
        e54 = isinstance(G, nx.DiGraph) and ns.get("nodos_grafo") == ref_nodes and ns.get("aristas_grafo") == ref_edges
    except Exception as e:
        print("E5.4", type(e).__name__, e)
        e54 = False
    check("E5_subgrafo", e54, 3)

    # E6 — 5 puntos
    try:
        informe = str(ns.get("informe_tecnico", "")); inf = informe.casefold()
        secciones = [
            "## 1. cómo construimos el histórico",
            "## 2. qué comprobamos en mongodb atlas",
            "## 3. cómo funciona la bandeja histórica",
            "## 4. por qué el modelo cassandra responde la consulta",
            "## 5. qué relaciones aporta neo4j y qué no podemos concluir",
        ]
        max_conn = int(ns.get("resultado_relacional")["entidades_conectadas"].max()) if isinstance(ns.get("resultado_relacional"), pd.DataFrame) and not ns.get("resultado_relacional").empty else None
        e61 = (
            all(s in inf for s in secciones)
            and str(len(fragmentos)) in informe
            and str(ns.get("documentos_atlas")) in informe
            and str(ns.get("resultado_a")) in informe
            and str(len(ns.get("bandeja_historica"))) in informe
            and str(ns.get("nit_ancla")) in informe
            and (max_conn is None or str(max_conn) in informe)
            and re.search(r"no\s+(demuestra|prueba)", inf) is not None
            and (OUT / "06_informe_tecnico.md").exists()
        )
        files = [
            "01_secop_historico_6000.json", "01_control_ingesta.json", "02_atlas_consultas.json",
            "03_bandeja_historica.csv", "04_modelo_cassandra.cql", "05_neo4j_consultas.cypher",
            "05_resultado_relacional.csv", "06_informe_tecnico.md",
        ]
        e62 = all((OUT / f).exists() and (OUT / f).stat().st_size > 0 for f in files)
    except Exception as e:
        print("E6", type(e).__name__, e)
        e61 = e62 = False; files = []
    check("E6_informe", e61, 3)
    check("E6_paquete", e62, 2)

    puntaje = sum(x["puntos"] for x in checks.values())
    maximo = sum(x["maximo"] for x in checks.values())
    nota = round(1 + 4 * puntaje / maximo, 2)
    manifest = {
        "taller": "TC1 historico SECOP + Atlas + Cassandra + Neo4j",
        "version": VERSION,
        "pareja_id": ns.get("PAREJA_ID", ""),
        "integrantes": [
            {"nombre": ns.get("INTEGRANTE_1", ""), "codigo": ns.get("CODIGO_1", "")},
            {"nombre": ns.get("INTEGRANTE_2", ""), "codigo": ns.get("CODIGO_2", "")},
        ],
        "puntaje": puntaje, "maximo": maximo, "nota_5": nota,
        "controles": checks, "artefactos": files,
    }
    previo = json.dumps(manifest, ensure_ascii=False, indent=2)
    manifest["sha256"] = hashlib.sha256(previo.encode("utf-8")).hexdigest()
    (OUT / "manifest_tc1.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    pareja = re.sub(r"[^A-Za-z0-9_-]+", "_", str(ns.get("PAREJA_ID", "pareja")))
    zip_path = Path(f"TC1_{pareja}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(OUT.iterdir()):
            zf.write(f, arcname=f.name)
    print("=" * 68)
    print(f"RESULTADO: {puntaje}/{maximo} · NOTA {nota}/5.0")
    print("ENTREGA:", zip_path)
    print("SHA-256:", manifest["sha256"])
    print("=" * 68)
    return manifest
