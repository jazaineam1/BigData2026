from pathlib import Path
from datetime import date
import json, re, hashlib, zipfile
import pandas as pd

VERSION = "2026-09-17-v2"
DATA_COMMIT = "c7031e3a58daa22d4ceff2d2f01d66aa967ba9e3"


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
            "evidencia": str(evidencia)[:400],
        }
        print(("✅" if ok else "❌"), k, f"{checks[k]['puntos']}/{puntos}")

    secop = ns.get("secop")
    noticias = ns.get("noticias")
    menciones = ns.get("menciones")
    relacional = ns.get("relacional")
    manifest_s06 = ns.get("manifest_s06")
    perfil = ns.get("perfil_fuentes", {})

    # E1
    try:
        c11 = (
            isinstance(secop, pd.DataFrame)
            and isinstance(noticias, list)
            and isinstance(menciones, list)
            and isinstance(relacional, pd.DataFrame)
            and isinstance(manifest_s06, dict)
            and (len(secop), len(noticias), len(menciones), len(relacional)) == (1000, 987, 142, 2109)
        )
        niv = {str(k).lower(): int(v) for k, v in perfil["menciones"]["niveles"].items()}
        c12 = (
            perfil["noticias"]["con_mas_800_palabras"] == 189
            and niv == {"baja": 111, "media": 25, "alta": 6}
            and perfil["relacional"]["historicos_adjudicados"] == 2032
            and (OUT / "01_perfil_fuentes.json").exists()
        )
        arq = str(ns.get("arquitectura_inicial", "")).casefold()
        c13 = all(x in arq for x in ["secop", "notic", "mongo", "bandeja", "cassandra", "neo4j"]) and "-->" in arq
    except Exception as e:
        print("E1:", type(e).__name__, e)
        c11 = c12 = c13 = False
    check("E1_carga", c11, 5)
    check("E1_perfil", c12, 6)
    check("E1_arquitectura", c13, 4)

    # E2
    try:
        contexto = ns.get("contexto_menciones")
        paso1, paso2, paso3, candidatos = [ns.get(x) for x in ["paso1", "paso2", "paso3", "candidatos"]]
        traza = ns.get("trazabilidad_regla", {})
        bandeja = ns.get("bandeja")
        c21 = (
            isinstance(contexto, pd.DataFrame)
            and list(contexto.columns) == ["entidad", "noticias_entidad", "nivel_menciones"]
            and contexto["entidad"].is_unique
            and len(contexto) == 142
        )
        c22 = (
            all(isinstance(x, pd.DataFrame) for x in [paso1, paso2, paso3, candidatos])
            and len(paso1) == 163
            and len(candidatos) == 77
            and traza.get("entrada") == 1000
            and traza.get("entidad_en_prensa") == 163
            and traza.get("salida") == 77
        )
        c23 = (
            isinstance(bandeja, pd.DataFrame)
            and len(bandeja) == 77
            and bandeja["noticias_entidad"].notna().all()
            and bandeja["nivel_menciones"].notna().all()
            and (OUT / "02_bandeja_candidatos.csv").exists()
        )
    except Exception as e:
        print("E2:", type(e).__name__, e)
        c21 = c22 = c23 = False
    check("E2_contexto", c21, 5)
    check("E2_regla", c22, 9, ns.get("trazabilidad_regla", {}))
    check("E2_bandeja", c23, 6)

    # E3
    try:
        import mongomock
        coleccion = ns.get("coleccion")
        resultado_largas = ns.get("resultado_largas", [])
        top_bogota = ns.get("top_bogota", [])
        resumen_secciones = ns.get("resumen_secciones", [])
        mongo_resultados = ns.get("mongo_resultados", {})

        def canon(rows):
            out = []
            for r in rows:
                d = dict(r)
                d.pop("_id", None)
                if d.get("promedio_palabras") is not None:
                    d["promedio_palabras"] = round(float(d["promedio_palabras"]), 8)
                out.append(d)
            return out

        c = mongomock.MongoClient().tc1.noticias
        c.insert_many([dict(x) for x in noticias])
        ref_largas = list(c.find(
            {"n_palabras": {"$gt": 800}},
            {"_id": 0, "titulo": 1, "seccion": 1, "n_palabras": 1},
        ).sort([("n_palabras", -1), ("titulo", 1)]))
        ref_bogota = list(c.find(
            {"seccion": "bogota", "n_palabras": {"$gt": 500}},
            {"_id": 0, "titulo": 1, "fecha": 1, "n_palabras": 1},
        ).sort([("n_palabras", -1), ("titulo", 1)]).limit(10))
        pipe = [
            {"$match": {"n_palabras": {"$gt": 0}}},
            {"$group": {"_id": "$seccion", "noticias": {"$sum": 1}, "promedio_palabras": {"$avg": "$n_palabras"}}},
            {"$sort": {"noticias": -1, "_id": 1}},
            {"$limit": 10},
        ]
        ref_resumen = list(c.aggregate(pipe))
        c31 = coleccion is not None and coleccion.count_documents({}) == 987
        c32 = canon(resultado_largas) == canon(ref_largas)
        c33 = canon(top_bogota) == canon(ref_bogota)
        c34 = canon(resumen_secciones) == canon(ref_resumen)
        c35 = (
            (OUT / "03_mongo_resultados.json").exists()
            and mongo_resultados.get("documentos") == 987
            and mongo_resultados.get("noticias_largas") == 189
        )
    except Exception as e:
        print("E3:", type(e).__name__, e)
        c31 = c32 = c33 = c34 = c35 = False
    check("E3_coleccion", c31, 3)
    check("E3_filtro", c32, 4)
    check("E3_bogota", c33, 4)
    check("E3_pipeline", c34, 6)
    check("E3_artefacto", c35, 3)

    # E4
    try:
        bo = ns.get("bandeja_operacional")
        cql = str(ns.get("cql_create", ""))
        departamento_prueba = ns.get("departamento_prueba")
        top5 = ns.get("top5_operacional")
        t = re.sub(r"\s+", " ", cql.casefold())
        c41 = isinstance(bo, pd.DataFrame) and len(bo) == 77 and {"corte", "departamento", "valor_base", "id_proceso"}.issubset(bo.columns)
        c42 = (
            re.search(r"primary\s+key\s*\(\s*\(\s*corte\s*,\s*departamento\s*\)\s*,\s*valor_base\s*,\s*id_proceso\s*\)", t) is not None
            and re.search(r"clustering\s+order\s+by\s*\(\s*valor_base\s+desc\s*,\s*id_proceso\s+asc\s*\)", t) is not None
            and "allow filtering" not in t
            and (OUT / "04_modelo_cassandra.cql").exists()
        )
        d = bo["departamento"].value_counts().index[0]
        ref = bo[(bo["corte"] == date(2026, 9, 3)) & (bo["departamento"] == d)].sort_values(
            ["valor_base", "id_proceso"], ascending=[False, True]
        ).head(5)
        c43 = departamento_prueba == d and isinstance(top5, pd.DataFrame) and list(top5["id_proceso"]) == list(ref["id_proceso"])
    except Exception as e:
        print("E4:", type(e).__name__, e)
        c41 = c42 = c43 = False
    check("E4_operacional", c41, 4)
    check("E4_query_first", c42, 7)
    check("E4_top5", c43, 4)

    # E5
    try:
        import networkx as nx
        ancla = ns.get("ancla")
        nit_ancla = ns.get("nit_ancla")
        hist = ns.get("hist")
        hist_ancla = ns.get("hist_ancla")
        resultado = ns.get("resultado_h2r")
        maximo = ns.get("maximo_h2r")
        mediana = ns.get("mediana_referencia")
        G = ns.get("G")
        nodos = ns.get("nodos_grafo")
        aristas = ns.get("aristas_grafo")

        rel = relacional.copy()
        for col in ["nit_entidad", "nit_proveedor", "id_proceso"]:
            rel[col] = rel[col].astype(str).str.strip()
        ra = manifest_s06["ancla_pedagogica"]
        rn = str(ra["nit_entidad"]).strip()
        rh = rel[(rel["tipo_registro"] == "historico_adjudicado") & rel["nit_proveedor"].ne("")]
        rha = rh[rh["nit_entidad"] == rn]
        rpa = rha.groupby(["nit_proveedor", "proveedor"], dropna=False)["id_proceso"].nunique().rename("procesos_con_entidad").reset_index()
        rpg = rh.groupby("nit_proveedor")["nit_entidad"].nunique().rename("entidades_conectadas").reset_index()
        rr = rpa.merge(rpg, on="nit_proveedor").sort_values(
            ["entidades_conectadas", "procesos_con_entidad", "nit_proveedor"], ascending=[False, False, True]
        ).reset_index(drop=True)
        c51 = (
            isinstance(ancla, dict)
            and str(nit_ancla) == rn
            and isinstance(hist, pd.DataFrame)
            and isinstance(hist_ancla, pd.DataFrame)
            and len(hist) == 2032
            and hist_ancla["id_proceso"].nunique() == ra["procesos_historicos"]
        )
        c52 = (
            isinstance(resultado, pd.DataFrame)
            and list(resultado["nit_proveedor"]) == list(rr["nit_proveedor"])
            and int(maximo) == 39
            and float(mediana) == 21.0
            and (OUT / "06_contexto_relacional.csv").exists()
        )
        q1, q2, q3 = [re.sub(r"\s+", " ", str(ns.get(k, "")).casefold()) for k in ["cypher_contexto", "cypher_compartido", "cypher_ranking"]]
        c53 = (
            ":entidad" in q1 and ":publica" in q1 and ":adjudicado_a" in q1 and "$nit_ancla" in q1
            and "otra:entidad" in q2 and "$nit_ancla" in q2 and ("<>" in q2 or "!=" in q2)
            and "count(distinct" in q3 and "order by" in q3
            and (OUT / "05_consultas_neo4j.cypher").exists()
        )
        np_ = rha["id_proceso"].nunique()
        nv_ = rha["nit_proveedor"].nunique()
        ref_edges = np_ + rha[["id_proceso", "nit_proveedor"]].drop_duplicates().shape[0]
        c54 = isinstance(G, nx.DiGraph) and nodos == 1 + np_ + nv_ and aristas == ref_edges
    except Exception as e:
        print("E5:", type(e).__name__, e)
        c51 = c52 = c53 = c54 = False
    check("E5_historial", c51, 4)
    check("E5_h2r", c52, 7, f"max={ns.get('maximo_h2r')} mediana={ns.get('mediana_referencia')}")
    check("E5_cypher", c53, 6)
    check("E5_grafo", c54, 3)

    # E6
    try:
        af = str(ns.get("arquitectura_final", ""))
        a = af.casefold()
        informe = str(ns.get("informe_tecnico", ""))
        r = informe.casefold()
        c61 = all(x in a for x in ["secop", "notic", "mongo", "pandas", "bandeja", "cassandra", "neo4j", "revisi"]) and "-->" in af
        secciones = [
            "## 1. problema y decisión", "## 2. fuentes y calidad", "## 3. regla de priorización",
            "## 4. por qué mongodb", "## 5. por qué cassandra", "## 6. por qué neo4j", "## 7. límites de la evidencia",
        ]
        c62 = (
            all(s in r for s in secciones)
            and str(len(secop)) in informe
            and str(len(ns.get("candidatos"))) in informe
            and str(int(ns.get("maximo_h2r"))) in informe
            and str(int(ns.get("mediana_referencia"))) in informe
            and "entidad" in r and "contrato" in r
            and re.search(r"no\s+(demuestra|prueba)", r) is not None
            and "corte" in r and "departamento" in r and "top 5" in r
            and (OUT / "07_informe_tecnico.md").exists()
        )
        files = [
            "01_perfil_fuentes.json", "02_bandeja_candidatos.csv", "03_mongo_resultados.json",
            "04_modelo_cassandra.cql", "05_consultas_neo4j.cypher", "06_contexto_relacional.csv", "07_informe_tecnico.md",
        ]
        c63 = all((OUT / f).exists() and (OUT / f).stat().st_size > 0 for f in files)
    except Exception as e:
        print("E6:", type(e).__name__, e)
        c61 = c62 = c63 = False
        files = []
    check("E6_arquitectura", c61, 4)
    check("E6_informe", c62, 4)
    check("E6_artefactos", c63, 2)

    puntaje = sum(x["puntos"] for x in checks.values())
    maximo_total = sum(x["maximo"] for x in checks.values())
    nota = round(1 + 4 * puntaje / maximo_total, 2)
    manifest = {
        "taller": "TC1 domiciliario S1-S6",
        "version": VERSION,
        "data_commit": DATA_COMMIT,
        "estudiante": ns.get("NOMBRE", ""),
        "codigo": ns.get("CODIGO", ""),
        "puntaje": puntaje,
        "maximo": maximo_total,
        "nota_5": nota,
        "controles": checks,
        "artefactos": files,
    }
    previo = json.dumps(manifest, ensure_ascii=False, indent=2)
    manifest["sha256"] = hashlib.sha256(previo.encode("utf-8")).hexdigest()
    (OUT / "manifest_tc1.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    codigo = re.sub(r"[^A-Za-z0-9_-]+", "_", str(ns.get("CODIGO", "sin_codigo")))
    zip_path = Path(f"TC1_{codigo}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(OUT.iterdir()):
            zf.write(f, arcname=f.name)

    print("=" * 62)
    print(f"RESULTADO: {puntaje}/{maximo_total} · NOTA {nota}/5.0")
    print("ENTREGA:", zip_path)
    print("SHA-256:", manifest["sha256"])
    print("=" * 62)
    return manifest
