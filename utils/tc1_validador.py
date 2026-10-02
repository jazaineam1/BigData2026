# -*- coding: utf-8 -*-
'''Validador del TC1. El estudiante y el docente ejecutan este mismo código.

- Valida ARCHIVOS, no variables en memoria: sirve igual en Colab que sobre el ZIP entregado.
- Recalcula toda referencia desde las páginas RAW y comprueba que esas páginas se
  descargaron con la consulta oficial de la pareja (firma de la consulta).
- Ningún requisito aparece aquí sin estar en tc1_contrato (y por tanto en el cuaderno).
- Las capturas acreditan el uso del servicio; el resultado estructurado acredita el
  resultado; el artefacto acredita la reproducibilidad. Una captura sola no da puntos.
'''
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

import tc1_contrato as C
import tc1_secop as S
import tc1_servicios as X

RUBRICA = {codigo: {"etapa": e, "maximo": p, "descripcion": d, "tipo": t} for codigo, e, p, d, t in C.RUBRICA}


class _Registro:
    def __init__(self):
        self.controles = {}

    def poner(self, item, puntos, evidencia, ok=None, pendiente_visual=False):
        maximo = RUBRICA[item]["maximo"]
        puntos = max(0, min(int(puntos), maximo))
        ok = (puntos == maximo) if ok is None else bool(ok)
        self.controles[item] = {
            "etapa": RUBRICA[item]["etapa"], "descripcion": RUBRICA[item]["descripcion"],
            "verificacion": RUBRICA[item]["tipo"], "ok": ok, "puntos": puntos, "maximo": maximo,
            "evidencia": str(evidencia)[:700], "feedback": "" if ok else C.FEEDBACK.get(item, ""),
            "pendiente_visual": bool(pendiente_visual),
        }

    def fallo(self, item, exc):
        self.poner(item, 0, f"no se pudo calcular: {type(exc).__name__}: {exc}")


# ── Lectura del paquete ───────────────────────────────────────────────────────
def _df(filas, columnas):
    df = pd.DataFrame(filas)
    for c in columnas:
        if c not in df.columns:
            df[c] = None
    return df[columnas] if len(df.columns) else pd.DataFrame(columns=columnas)


def _contexto(out):
    R = C.rutas(out)
    ctx = {"R": R, "out": Path(out)}
    ident = X.leer_json(R["identidad"], {}) or {}
    ctx["identidad"] = ident
    ctx["pareja"] = str(ident.get("pareja", "")).strip()
    ctx["acq"] = X.leer_json(R["E1"] / "01_acquisition_manifest.json", {}) or {}
    ctx["bench"] = X.leer_json(R["E1"] / "01_benchmark_threads.json", {}) or {}
    ctx["calidad"] = X.leer_json(R["E1"] / "01_quality_report.json", {}) or {}
    ctx["contrato"] = X.leer_json(R["E1"] / "00_dataset_contract.json", {}) or {}
    obj = ctx["acq"].get("objetivos", {}) or {}
    ctx["n_proc"], ctx["n_con"] = int(obj.get("procesos", 0) or 0), int(obj.get("contratos", 0) or 0)
    ctx["off_p"], ctx["off_c"] = S.offsets_para(ctx["n_proc"]), S.offsets_para(ctx["n_con"])
    ctx["cache"] = {k: S.validar_cache(R[k], ctx["off_c"] if k == "pag_con" else ctx["off_p"])
                    for k in ("pag_seq", "pag_thr", "pag_con")}
    ctx["procesos"] = ctx["procesos_seq"] = ctx["contratos"] = None
    if ctx["cache"]["pag_thr"][0]:
        ctx["procesos"] = _df(S.leer_paginas(R["pag_thr"], ctx["off_p"]), C.SELECT_PROCESOS)
    if ctx["cache"]["pag_seq"][0]:
        ctx["procesos_seq"] = _df(S.leer_paginas(R["pag_seq"], ctx["off_p"]), C.SELECT_PROCESOS)
    if ctx["cache"]["pag_con"][0]:
        ctx["contratos"] = _df(S.leer_paginas(R["pag_con"], ctx["off_c"]), C.SELECT_CONTRATOS)
    ctx["docs_ref"] = ctx["bandeja_ref"] = ctx["rel_ref"] = None
    if ctx["procesos"] is not None and ctx["contratos"] is not None and ctx["pareja"] in C.VENTANAS:
        ctx["docs_ref"] = S.construir_documentos(ctx["procesos"], ctx["contratos"], C.GRANO_CORRECTO, ctx["pareja"])
        ctx["bandeja_ref"] = S.ref_bandeja(ctx["docs_ref"])
        ctx["rel_ref"] = S.relaciones_grafo(ctx["contratos"])
    return ctx


def _firmas_oficiales(ctx, dataset, carpeta, offsets, n):
    q = S.plan_consulta(ctx["pareja"])[dataset]
    esperadas = [S.query_signature(q["endpoint"], select=q["select"], where=q["where"], order=q["order"],
                                   limit=S.limite_pagina(o, n)) for o in offsets]
    try:
        return S.firmas_cache(carpeta, offsets) == esperadas
    except Exception:
        return False


# ── E1 ────────────────────────────────────────────────────────────────────────
def _e1(ctx, reg):
    R, pareja = ctx["R"], ctx["pareja"]
    try:
        oficial = C.contrato_de_datos(pareja) if pareja in C.VENTANAS else None
        dado = ctx["contrato"]
        ok = (oficial is not None and dado.get("pareja") == pareja
              and all(dado.get(k, {}).get(c) == oficial[k][c] for k in ("procesos", "contratos")
                      for c in ("id", "select", "where", "order"))
              and _firmas_oficiales(ctx, "procesos", R["pag_thr"], ctx["off_p"], ctx["n_proc"])
              and _firmas_oficiales(ctx, "contratos", R["pag_con"], ctx["off_c"], ctx["n_con"]))
        reg.poner("E1.1", 4 if ok else 0, f"pareja={pareja or '(vacía)'}; ventana={C.VENTANAS.get(pareja)}; "
                  f"páginas con la consulta oficial={ok}")
    except Exception as exc:
        reg.fallo("E1.1", exc)

    try:
        ok_cache, msg = ctx["cache"]["pag_seq"]
        filas = 0 if ctx["procesos_seq"] is None else len(ctx["procesos_seq"])
        ok = (ok_cache and ctx["n_proc"] > 0 and filas == ctx["n_proc"]
              and float(ctx["bench"].get("segundos_secuencial") or 0) > 0
              and _firmas_oficiales(ctx, "procesos", R["pag_seq"], ctx["off_p"], ctx["n_proc"]))
        reg.poner("E1.2", 4 if ok else 0, f"caché secuencial: {msg}; filas={filas}; objetivo={ctx['n_proc']}")
    except Exception as exc:
        reg.fallo("E1.2", exc)

    try:
        ok_cache, msg = ctx["cache"]["pag_thr"]
        h_seq = S.canonical_hash(ctx["procesos_seq"], C.SELECT_PROCESOS) if ctx["procesos_seq"] is not None else None
        h_thr = S.canonical_hash(ctx["procesos"], C.SELECT_PROCESOS) if ctx["procesos"] is not None else None
        b = ctx["bench"]
        workers = int(b.get("workers", 0) or 0)
        ok = (ok_cache and h_seq is not None and h_seq == h_thr
              and C.WORKERS_MIN <= workers <= C.WORKERS_MAX
              and b.get("hash_secuencial") == h_seq and b.get("hash_concurrente") == h_thr
              and b.get("mismo_hash") is True and b.get("mismos_offsets") is True and b.get("mismas_filas") is True
              and float(b.get("segundos_concurrente") or 0) > 0)
        reg.poner("E1.3", 8 if ok else 0, f"caché concurrente: {msg}; workers={workers}; "
                  f"hash secuencial={str(h_seq)[:12]}…; hash concurrente={str(h_thr)[:12]}…")
    except Exception as exc:
        reg.fallo("E1.3", exc)

    try:
        ok_cache, msg = ctx["cache"]["pag_con"]
        cruce = S.cruce(ctx["procesos"], ctx["contratos"]) if ctx["procesos"] is not None and ctx["contratos"] is not None else {}
        raw_p = R["raw"] / "procesos.parquet"
        raw_c = R["raw"] / "contratos.parquet"
        ok_parquet = (raw_p.exists() and raw_c.exists()
                      and S.canonical_hash(pd.read_parquet(raw_p), C.SELECT_PROCESOS) == S.canonical_hash(ctx["procesos"], C.SELECT_PROCESOS)
                      and S.canonical_hash(pd.read_parquet(raw_c), C.SELECT_CONTRATOS) == S.canonical_hash(ctx["contratos"], C.SELECT_CONTRATOS))
        cal = ctx["calidad"]
        ok = (ok_cache and ok_parquet and ctx["acq"].get("schema") == C.E1_SCHEMA
              and cruce.get("matched_processes", 0) >= C.MIN_MATCHED_PROCESSES
              and int(cal.get("matched_processes", -1)) == cruce.get("matched_processes")
              and _firmas_oficiales(ctx, "contratos", R["pag_con"], ctx["off_c"], ctx["n_con"]))
        reg.poner("E1.4", 9 if ok else 0, f"caché contratos: {msg}; RAW parquet = páginas: {ok_parquet}; "
                  f"procesos cruzados={cruce.get('matched_processes')} (mínimo {C.MIN_MATCHED_PROCESSES})")
    except Exception as exc:
        reg.fallo("E1.4", exc)


# ── E2 ────────────────────────────────────────────────────────────────────────
def _indice_alineado(indices):
    for ix in indices or []:
        if ix.get("nombre") == "_id_":
            continue
        clave = [c[0] for c in ix.get("clave", [])]
        if clave == ["id_proceso"]:
            continue
        if clave and clave[0] in C.CAMPOS_INDICE_ALINEADOS:
            return clave[0]
    return None


def _e2(ctx, reg):
    R = ctx["R"]
    modelo = X.leer_json(R["E2"] / "02_modelo_documental.json", {}) or {}
    docs = modelo.get("documentos") or []
    ref = ctx["docs_ref"] or []
    try:
        ids = [d.get("id_proceso") for d in docs]
        integrado = R["E2"] / "02_secop_integrado.parquet"
        ok = (bool(ref) and modelo.get("grano") == C.GRANO_CORRECTO and len(docs) == len(ref)
              and len(set(ids)) == len(ids) and S.huella_documentos(docs) == S.huella_documentos(ref)
              and integrado.exists() and len(pd.read_parquet(integrado)) == len(ref))
        reg.poner("E2.1", 5 if ok else 0, f"grano='{modelo.get('grano')}'; documentos={len(docs)}; "
                  f"procesos únicos en tu RAW={len(ref)}; ids únicos={len(set(ids))}")
    except Exception as exc:
        reg.fallo("E2.1", exc)

    ev = X.leer_json(R["E2"] / "02_atlas_evidence.json", {}) or {}
    carga = ev.get("carga", {}) or {}
    try:
        n = len(ref)
        ok = (ev.get("capturado_por") == "pymongo" and bool(ev.get("server_version"))
              and carga.get("estrategia") == C.ESTRATEGIA_CORRECTA
              and carga.get("count_after_first") == n and carga.get("count_after_second") == n
              and carga.get("duplicates_after_second") == 0 and not carga.get("error_segunda"))
        reg.poner("E2.2", 7 if ok else 0, f"estrategia='{carga.get('estrategia')}'; primera={carga.get('count_after_first')}; "
                  f"segunda={carga.get('count_after_second')}; duplicados={carga.get('duplicates_after_second')}; esperado={n}")
    except Exception as exc:
        reg.fallo("E2.2", exc)

    try:
        indices = ev.get("indices") or []
        unico = any(ix.get("unico") and [c[0] for c in ix.get("clave", [])] == ["id_proceso"] for ix in indices)
        alineado = _indice_alineado(indices)
        reg.poner("E2.3", 4 if unico and alineado else 0,
                  f"único en id_proceso={unico}; índice alineado={alineado}; índices={[ix.get('nombre') for ix in indices]}")
    except Exception as exc:
        reg.fallo("E2.3", exc)

    try:
        a = ev.get("consulta_a", {}) or {}
        campos = X.campos_de(a.get("filtro"))
        esperado = S.ref_consulta_a(ref) if ref else None
        ok = (esperado is not None and a.get("resultado") == esperado
              and {C.CAMPO["precio_base"], C.CAMPO["cantidad"]} <= campos)
        reg.poner("E2.4", 3 if ok else 0, f"conteo en Atlas={a.get('resultado')}; referencia={esperado}; campos del filtro={sorted(campos)}")
    except Exception as exc:
        reg.fallo("E2.4", exc)

    try:
        b = ev.get("consulta_b", {}) or {}
        esperado = S.ref_consulta_b(ref) if ref else None
        ok = esperado is not None and list(b.get("ids") or []) == esperado
        reg.poner("E2.5", 3 if ok else 0, f"Atlas={list(b.get('ids') or [])[:3]}…; referencia={(esperado or [])[:3]}…")
    except Exception as exc:
        reg.fallo("E2.5", exc)

    completo = all(k in ev for k in ("carga", "indices", "consulta_a", "consulta_b")) and bool(ev.get("server_version"))
    _visual(ctx, reg, "E2.6", completo, f"evidencia completa={completo}")


def _visual(ctx, reg, item, correcto, evidencia):
    alto, medio, bajo = C.NIVELES_VISUALES[item]
    etapa = C.CAPTURA_DE_ITEM[item]
    ok_img, motivo = X.validar_captura(ctx["R"][etapa] / C.CAPTURAS[etapa])
    confirmacion = (ctx.get("capturas") or {}).get(etapa)
    if not correcto:
        reg.poner(item, bajo, f"{evidencia}; captura: {motivo}", ok=False)
    elif not ok_img or confirmacion is False:
        nota = "el docente no la aceptó" if confirmacion is False else motivo
        reg.poner(item, medio, f"{evidencia}; captura: {nota}", ok=False)
    else:
        reg.poner(item, alto, f"{evidencia}; captura: {motivo}", pendiente_visual=confirmacion is None)


# ── E3 ────────────────────────────────────────────────────────────────────────
def _orden_valido(sort):
    claves = list((sort or {}).items())
    if len(claves) < 2:
        return False
    (c1, d1), (c2, d2) = claves[0], claves[1]
    return (c1 in ("valor_contratos", C.CAMPO["valor"]) and int(d1) == -1
            and c2 == "id_proceso" and int(d2) == 1)


def analizar_pipeline(pipeline):
    etapas = [next(iter(e)) for e in pipeline if isinstance(e, dict) and e] if isinstance(pipeline, list) else []
    match = next((e["$match"] for e in pipeline if isinstance(e, dict) and "$match" in e), None) if etapas else None
    sort = next((e["$sort"] for e in pipeline if isinstance(e, dict) and "$sort" in e), None) if etapas else None
    limite = next((e["$limit"] for e in pipeline if isinstance(e, dict) and "$limit" in e), None) if etapas else None
    campos = X.campos_de(match) if match is not None else set()
    return {
        "etapas": etapas,
        "match_ok": {C.CAMPO["precio_base"], C.CAMPO["cantidad"]} <= campos,
        "sort_ok": _orden_valido(sort),
        "limit_ok": isinstance(limite, int) and 0 < limite <= C.BANDEJA_MAX,
        "sin_escritura": not (X.ETAPAS_PROHIBIDAS & set(etapas)),
    }


def _e3(ctx, reg):
    R = ctx["R"]
    esperado = [f["id_proceso"] for f in (ctx["bandeja_ref"] or [])]
    resultado = X.leer_json(R["E3"] / "03_resultado_atlas.json", {}) or {}
    ids_atlas = list(resultado.get("ids") or [])
    try:
        p = X.leer_json(R["E3"] / "03_pipeline_bandeja.json", {}) or {}
        a = analizar_pipeline(p.get("pipeline"))
        estructura = a["match_ok"] and a["sort_ok"] and a["limit_ok"] and a["sin_escritura"]
        ok = (estructura and resultado.get("capturado_por") == "pymongo" and bool(esperado) and ids_atlas == esperado
              and p.get("nombre_guardado") == C.nombre_pipeline(ctx["pareja"]))
        reg.poner("E3.1", 7 if ok else 0, f"etapas={a['etapas']}; $match={a['match_ok']}; $sort={a['sort_ok']}; "
                  f"$limit={a['limit_ok']}; filas Atlas={len(ids_atlas)}; referencia={len(esperado)}; "
                  f"mismo orden={ids_atlas == esperado}")
    except Exception as exc:
        reg.fallo("E3.1", exc)
    try:
        csv = R["E3"] / "03_bandeja_historica.csv"
        df = pd.read_csv(csv, dtype={"id_proceso": str}) if csv.exists() else pd.DataFrame()
        ok = (not df.empty and set(C.COLUMNAS_BANDEJA) <= set(df.columns) and len(df) <= C.BANDEJA_MAX
              and df["id_proceso"].tolist() == ids_atlas == esperado)
        reg.poner("E3.2", 3 if ok else 0, f"filas={len(df)}; columnas={list(df.columns)}")
    except Exception as exc:
        reg.fallo("E3.2", exc)


# ── E4 ────────────────────────────────────────────────────────────────────────
def bandeja_propia(out):
    '''La bandeja que la pareja obtuvo de Atlas (E3). E4 y E6 se miden contra ella para no castigar
    dos veces un error de E3; E3 se califica aparte contra la referencia.'''
    csv = C.rutas(out)["E3"] / "03_bandeja_historica.csv"
    try:
        df = pd.read_csv(csv, dtype={"id_proceso": str})
    except Exception:
        return None
    if df.empty or not set(C.COLUMNAS_BANDEJA) <= set(df.columns):
        return None
    return df[C.COLUMNAS_BANDEJA].to_dict("records")


def _parentesis(texto, inicio):
    nivel = 0
    for i in range(inicio, len(texto)):
        if texto[i] == "(":
            nivel += 1
        elif texto[i] == ")":
            nivel -= 1
            if nivel == 0:
                return texto[inicio + 1:i]
    return ""


def analizar_cql(texto):
    t = re.sub(r"/\*.*?\*/", " ", str(texto or ""), flags=re.S)
    t = re.sub(r"(--|//)[^\n]*", " ", t)
    plano = re.sub(r"\s+", " ", t).strip().lower().replace('"', "")
    info = {"particion": [], "clustering": [], "orden": [], "tipo_valor": None,
            "allow_filtering": "allow filtering" in plano, "select_ok": False, "create": False}
    m = re.search(r"create table (?:if not exists )?[\w.]+ \(", plano)
    if not m:
        return info
    info["create"] = True
    cuerpo = _parentesis(plano, m.end() - 1)
    tipo = re.search(r"\bvalor_contratos (\w+)", cuerpo)
    info["tipo_valor"] = tipo.group(1) if tipo else None
    k = cuerpo.find("primary key")
    if k >= 0:
        pk = _parentesis(cuerpo, cuerpo.find("(", k))
        if pk.strip().startswith("("):
            particion = _parentesis(pk, pk.find("("))
            resto = pk[pk.find(particion) + len(particion) + 1:]
        else:
            particion, _, resto = pk.partition(",")
        info["particion"] = [c.strip() for c in particion.split(",") if c.strip()]
        info["clustering"] = [c.strip() for c in resto.split(",") if c.strip()]
    o = re.search(r"clustering order by \(([^)]*)\)", plano)
    if o:
        info["orden"] = [tuple(x.strip().split()[:2]) for x in o.group(1).split(",") if x.strip()]
    info["select_ok"] = bool(re.search(r"select [^;]*id_proceso[^;]* from [\w.]+ where anio = \d+ and departamento = '[^']*' limit 10", plano))
    return info


def _e4(ctx, reg):
    R = ctx["R"]
    ev = X.leer_json(R["E4"] / "04_cassandra_evidence.json", {}) or {}
    base = bandeja_propia(ctx["out"]) or ctx["bandeja_ref"]
    datos_ref = S.datos_cassandra(base) if base else None
    ref = S.ref_cassandra(datos_ref, S.particion_prueba(datos_ref)) if datos_ref is not None and len(datos_ref) else {}
    leido = X.evidencia_astra(ev.get("salida_consola", ""))
    try:
        csv = R["E4"] / "04_datos_cassandra.csv"
        filas = len(pd.read_csv(csv)) if csv.exists() else 0
        ok = (bool(ref) and filas == len(datos_ref) and leido["count"] == ref.get("count")
              and ev.get("anio") == ref.get("anio") and ev.get("departamento") == ref.get("departamento"))
        reg.poner("E4.1", 5 if ok else 0, f"partición de prueba=({ref.get('anio')}, {ref.get('departamento')}); "
                  f"COUNT en Astra={leido['count']}; esperado={ref.get('count')}; errores={leido['errores'][:2]}")
    except Exception as exc:
        reg.fallo("E4.1", exc)
    try:
        cql = (R["E4"] / "04_modelo_cassandra.cql").read_text(encoding="utf-8") if (R["E4"] / "04_modelo_cassandra.cql").exists() else ""
        a = analizar_cql(cql)
        ok = (a["create"] and a["particion"] == ["anio", "departamento"]
              and a["clustering"] == ["valor_contratos", "id_proceso"]
              and a["orden"] == [("valor_contratos", "desc"), ("id_proceso", "asc")]
              and a["tipo_valor"] in C.TIPOS_VALOR_NUMERICOS and not a["allow_filtering"] and a["select_ok"])
        reg.poner("E4.2", 6 if ok else 0, f"partición={a['particion']}; clustering={a['clustering']}; orden={a['orden']}; "
                  f"tipo valor={a['tipo_valor']}; ALLOW FILTERING={a['allow_filtering']}; SELECT por partición={a['select_ok']}")
    except Exception as exc:
        reg.fallo("E4.2", exc)
    correcto = bool(ref) and leido["top10_ids"] == ref.get("top10_ids")
    _visual(ctx, reg, "E4.3", correcto, f"top10 Astra={leido['top10_ids'][:3]}…; referencia={(ref.get('top10_ids') or [])[:3]}…")


# ── E5 ────────────────────────────────────────────────────────────────────────
def secciones_cypher(texto):
    partes, actual = {}, None
    for linea in str(texto or "").splitlines():
        m = re.match(r"^\s*//\s*---\s*(\w+)\s*---", linea)
        if m:
            actual = m.group(1).lower()
            partes[actual] = []
        elif actual:
            partes[actual].append(linea)
    return {k: "\n".join(v).strip() for k, v in partes.items()}


def analizar_cypher(texto):
    sec = secciones_cypher(texto)
    plano = {k: re.sub(r"\s+", " ", v).lower() for k, v in sec.items()}
    carga = plano.get("carga", "")
    comp = plano.get("compartidos", "")
    rank = plano.get("ranking", "")
    return {
        "carga": ("unwind $filas" in carga and all(re.search(rf"merge \(\w*:{x}\b", carga) for x in ("entidad", "contrato", "proveedor"))
                  and ":firma]" in carga and ":adjudicado_a]" in carga),
        "contexto": "match" in plano.get("contexto", "") and ("$nit_ancla" in plano.get("contexto", "") or re.search(r"nit: ?\"\d+\"", plano.get("contexto", ""))),
        "compartidos": ("____" not in comp and comp.count(":adjudicado_a") >= 2 and ("<>" in comp or "!=" in comp)),
        "ranking": ("____" not in rank and re.search(r"count\(distinct [\w.]+\) as entidades_conectadas", rank) is not None
                    and "order by" in rank and "desc" in rank),
    }


def _filas_ranking(filas):
    return [(str(f.get("nit_proveedor")), int(f.get("contratos_con_ancla", -1)), int(f.get("entidades_conectadas", -1)))
            for f in filas or []]


def _e5(ctx, reg):
    R = ctx["R"]
    ev = X.leer_json(R["E5"] / "05_neo4j_evidence.json", {}) or {}
    rel = ctx["rel_ref"]
    ancla = S.entidad_ancla(rel) if rel is not None and len(rel) else {}
    rank = S.ranking_ancla(rel, ancla["nit_ancla"]) if ancla else pd.DataFrame()
    try:
        esperados = S.conteos_grafo(rel) if rel is not None else {}
        conteos = ev.get("conteos") or {}
        aura = (ev.get("ancla_aura") or [{}])[0]
        ok = (bool(ancla) and ev.get("capturado_por") == "neo4j-driver"
              and all(int(conteos.get(k, -1)) == v for k, v in esperados.items())
              and str(ev.get("nit_ancla")) == ancla["nit_ancla"] and str(aura.get("nit")) == ancla["nit_ancla"])
        reg.poner("E5.1", 4 if ok else 0, f"conteos Aura={conteos}; esperados={esperados}; ancla Aura={aura.get('nit')}; "
                  f"ancla esperada={ancla.get('nit_ancla')}")
    except Exception as exc:
        reg.fallo("E5.1", exc)
    try:
        esperado = _filas_ranking(rank.to_dict("records"))
        obtenido = _filas_ranking(ev.get("ranking"))
        csv = R["E5"] / "05_resultado_relacional.csv"
        en_csv = _filas_ranking(pd.read_csv(csv, dtype={"nit_proveedor": str}).to_dict("records")) if csv.exists() else []
        ok = bool(esperado) and obtenido == esperado == en_csv
        reg.poner("E5.2", 4 if ok else 0, f"filas Aura={len(obtenido)}; esperadas={len(esperado)}; "
                  f"primera Aura={obtenido[:1]}; primera esperada={esperado[:1]}")
    except Exception as exc:
        reg.fallo("E5.2", exc)
    try:
        archivo = R["E5"] / "05_neo4j_consultas.cypher"
        a = analizar_cypher(archivo.read_text(encoding="utf-8") if archivo.exists() else "")
        reg.poner("E5.3", 5 if all(a.values()) else 0, f"secciones={ {k: bool(v) for k, v in a.items()} }")
    except Exception as exc:
        reg.fallo("E5.3", exc)
    top = rank.iloc[0].to_dict() if len(rank) else {}
    correcto = (bool(top) and str(ev.get("proveedor_top")) == str(top.get("nit_proveedor"))
                and ev.get("contratos_con_ancla") == top.get("contratos_con_ancla")
                and ev.get("entidades_conectadas") == top.get("entidades_conectadas"))
    _visual(ctx, reg, "E5.4", correcto, f"proveedor puente Aura={ev.get('proveedor_top')}; esperado={top.get('nit_proveedor')}")


# ── E6 ────────────────────────────────────────────────────────────────────────
def _e6(ctx, reg, hallazgos_secretos):
    R = ctx["R"]
    log = X.leer_json(R["E6"] / "06_decision_log.json", {}) or {}
    dec = {d.get("tema"): d for d in log.get("decisiones", []) if isinstance(d, dict)}
    try:
        puntos, detalle = 0, []
        d1 = dec.get("concurrencia_429", {})
        seg = float(ctx["bench"].get("segundos_concurrente") or 0)
        if d1.get("seleccion") == C.E6_CORRECTAS["decision_429"] and abs(float(d1.get("segundos_declarados", -99)) - seg) <= 1.0:
            puntos += 2
        detalle.append(f"429: {'ok' if puntos == 2 else 'revisar'}")
        d2 = dec.get("indice_atlas", {})
        ev2 = X.leer_json(R["E2"] / "02_atlas_evidence.json", {}) or {}
        alineado = _indice_alineado(ev2.get("indices"))
        if alineado and C.E6_INDICE_CAMPO.get(d2.get("seleccion")) == alineado:
            puntos += 1
            detalle.append("índice: ok")
        else:
            detalle.append("índice: no coincide con el índice que creaste")
        d3 = dec.get("limite_bandeja", {})
        bandeja = bandeja_propia(ctx["out"]) or ctx["bandeja_ref"] or []
        k = int(d3.get("posicion", 0) or 0)
        valor_ok = 1 <= k <= min(10, len(bandeja)) and abs(int(d3.get("valor_millones", -1)) - round(bandeja[k - 1]["valor_contratos"] / 1e6)) <= 1
        if valor_ok and d3.get("dato_faltante") == C.E6_CORRECTAS["dato_faltante"]:
            puntos += 2
            detalle.append("límite: ok")
        else:
            detalle.append("límite: revisa el valor de esa posición o el dato que falta")
        informe = (R["E6"] / "06_informe_tecnico.md").read_text(encoding="utf-8") if (R["E6"] / "06_informe_tecnico.md").exists() else ""
        if not all(s in informe for s in ("## 1.", "## 6.", "Qué NO permite concluir")):
            puntos = 0
            detalle.append("falta el informe generado")
        reg.poner("E6.1", puntos, "; ".join(detalle))
    except Exception as exc:
        reg.fallo("E6.1", exc)
    try:
        mic = X.leer_json(R["E6"] / "06_microdefensa_grupal.json", {}) or {}
        puntos, detalle = 0, []
        cob = mic.get("cobertura", {}) or {}
        cruce = S.cruce(ctx["procesos"], ctx["contratos"]) if ctx["procesos"] is not None and ctx["contratos"] is not None else {}
        if cruce and cob.get("rango") == C.rango_cobertura(cruce["join_coverage"]) and cob.get("causa") == C.E6_CORRECTAS["causa_cobertura"]:
            puntos += 2
            detalle.append("cobertura: ok")
        else:
            detalle.append(f"cobertura: tu valor real es {round(100 * cruce.get('join_coverage', 0), 1)} %")
        red = mic.get("red", {}) or {}
        rel = ctx["rel_ref"]
        rank = S.ranking_ancla(rel, S.entidad_ancla(rel)["nit_ancla"]) if rel is not None and len(rel) else pd.DataFrame()
        if len(rank) and red.get("limite") == C.E6_CORRECTAS["limite_red"] and int(red.get("entidades_puente", -1)) == int(rank.iloc[0]["entidades_conectadas"]):
            puntos += 1
            detalle.append("red: ok")
        else:
            detalle.append("red: revisa el límite o el número de entidades de tu proveedor puente")
        reg.poner("E6.2", puntos, "; ".join(detalle))
    except Exception as exc:
        reg.fallo("E6.2", exc)
    faltan = [f"{e}/{a}" for e, lista in C.ARTEFACTOS.items() for a in lista
              if a not in C.CAPTURAS.values() and (not (R[e] / a).exists() or (R[e] / a).stat().st_size == 0)]
    ok = not faltan and not hallazgos_secretos
    reg.poner("E6.3", 2 if ok else 0, f"faltantes={faltan[:6]}; secretos={hallazgos_secretos[:3]}")


# ── Secretos ──────────────────────────────────────────────────────────────────
TEXTO = {".json", ".csv", ".md", ".cql", ".cypher", ".txt", ".ipynb", ".py", ".html"}


def escanear_secretos(out, notebook=None):
    hallazgos = []
    for p in sorted(Path(out).rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(out).as_posix()
        if X.prohibido(p.name):
            hallazgos.append(f"{rel} (archivo de credenciales)")
            continue
        if p.suffix.lower() in TEXTO:
            texto = p.read_text(encoding="utf-8", errors="ignore")
            hallazgos += [f"{rel} ({n})" for n, patron in C.PATRONES_SECRETOS if re.search(patron, texto)]
    if notebook is not None:
        blob = json.dumps(notebook, ensure_ascii=False) if not isinstance(notebook, (str, Path)) else Path(notebook).read_text(encoding="utf-8", errors="ignore")
        hallazgos += [f"notebook ({n})" for n, patron in C.PATRONES_SECRETOS if re.search(patron, blob)]
    return hallazgos


# ── Evaluación completa ───────────────────────────────────────────────────────
def evaluar(out, *, modo="estudiante", capturas=None, notebook=None, escribir=True):
    '''Califica la carpeta de trabajo (estudiante) o el ZIP extraído (docente).

    capturas: {"E2": True/False/None, ...} confirmación visual del docente (None = sin revisar).
    '''
    out = Path(out)
    reg = _Registro()
    ctx = _contexto(out)
    ctx["capturas"] = capturas or {}
    secretos = escanear_secretos(out, notebook)
    for etapa in (_e1, _e2, _e3, _e4, _e5):
        try:
            etapa(ctx, reg)
        except Exception as exc:
            for item, info in RUBRICA.items():
                if item not in reg.controles and info["etapa"] == etapa.__name__[1:].upper():
                    reg.fallo(item, exc)
    _e6(ctx, reg, secretos)
    for item in RUBRICA:
        if item not in reg.controles:
            reg.poner(item, 0, "sin evidencia")
    puntaje = sum(c["puntos"] for c in reg.controles.values())
    ident = ctx["identidad"]
    manifest = {
        "taller": "TC1 · SECOP Data Pipeline",
        "version": C.VERSION,
        "modo": modo,
        "pareja_id": ctx["pareja"],
        "integrantes": ident.get("integrantes", []),
        "puntaje": puntaje,
        "maximo": C.puntos_totales(),
        "nota_exacta": round(C.nota_exacta(puntaje), 2),
        "nota_registrada": C.nota_registrada(puntaje),
        "etapas": {e: {"nombre": C.STAGE_NOMBRE[e], "puntos": sum(c["puntos"] for c in reg.controles.values() if c["etapa"] == e),
                       "maximo": m} for e, m in C.STAGE_MAX.items()},
        "controles": dict(sorted(reg.controles.items())),
        "pendiente_confirmacion_visual": [k for k, c in sorted(reg.controles.items()) if c["pendiente_visual"]],
        "gates": {"sin_secretos": {"ok": not secretos, "hallazgos": secretos}},
        "generado_utc": X.ahora_utc(),
    }
    if escribir:
        X.escribir_json(out / C.MANIFEST, manifest)
    return manifest


def resumen_texto(manifest):
    lineas = [f"TC1 · {manifest['pareja_id']} · {manifest['version']}", ""]
    for e, info in manifest["etapas"].items():
        marca = "✓ completa" if info["puntos"] == info["maximo"] else "✗ revisar"
        lineas.append(f"{e} · {info['nombre']:<34} {info['puntos']:>2} / {info['maximo']:<2}  {marca}")
    lineas += ["", f"TOTAL {manifest['puntaje']} / {manifest['maximo']}",
               f"NOTA {manifest['nota_exacta']:.2f} (se registra {manifest['nota_registrada']:.1f} según el PDA)"]
    pend = manifest.get("pendiente_confirmacion_visual") or []
    if pend:
        lineas.append(f"Provisional: {', '.join(pend)} dependen de que el docente confirme tus capturas.")
    fallas = [(k, c) for k, c in manifest["controles"].items() if not c["ok"]]
    if fallas:
        lineas += ["", "QUÉ CORREGIR"]
        for k, c in fallas:
            lineas.append(f"✗ {k} · {c['descripcion']} ({c['puntos']}/{c['maximo']})")
            lineas.append(f"   Qué revisar: {c['feedback']}")
            lineas.append(f"   Lo que encontró el validador: {c['evidencia']}")
    gate = manifest["gates"]["sin_secretos"]
    lineas += ["", "SEGURIDAD: " + ("sin secretos detectados." if gate["ok"] else
                                    "ENTREGA BLOQUEADA, se detectaron posibles secretos en: " + "; ".join(gate["hallazgos"]))]
    return "\n".join(lineas)
