# -*- coding: utf-8 -*-
'''Infraestructura provista del TC1: descarga SECOP, caché verificable y preparación de
datos para E2–E5. El estudiante no reescribe nada de esto; lo usa y comprueba lo que produce.

Lo que sí escribe o decide el estudiante vive en el cuaderno: la descarga secuencial y la
concurrente con ThreadPoolExecutor (E1), el grano documental (E2), las consultas de Atlas
(E2–E3), el diseño de la tabla Cassandra (E4), las consultas Cypher (E5) y las decisiones (E6).

Las referencias que usa el validador se calculan aquí, con el mismo código para el
estudiante y para el docente, a partir de las páginas RAW, nunca de un resultado declarado.
'''
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import pandas as pd

import tc1_contrato as C

BASE = os.environ.get("TC1_SOCRATA_BASE", C.BASE_SOCRATA)
HEADERS = {"Accept": "application/json", "User-Agent": "BigData2026-UCentral-TC1/9 (Google Colab)"}
RETRY_STATUS = {429, 500, 502, 503, 504}
EVENTOS_HTTP = {"reintentos": 0, "http_429": 0}


# ── Cliente HTTP con reintentos ───────────────────────────────────────────────
def _espera_retry_after(valor, intento, base):
    if valor:
        if str(valor).strip().isdigit():
            return float(valor)
        try:
            return max(0.0, (parsedate_to_datetime(valor) - datetime.now(timezone.utc)).total_seconds())
        except Exception:
            pass
    return base * (2 ** (intento - 1))


def request_json(url, params, *, timeout=60, max_attempts=6, base_backoff=1.0):
    '''GET con timeout finito, reintentos acotados y backoff; respeta Retry-After.'''
    import requests  # solo al descargar: revisar una entrega no necesita red
    ultimo = None
    for intento in range(1, max_attempts + 1):
        inicio = time.perf_counter()
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
        except requests.RequestException as exc:
            ultimo = exc
            if intento == max_attempts:
                raise
            EVENTOS_HTTP["reintentos"] += 1
            time.sleep(min(base_backoff * (2 ** (intento - 1)), 20))
            continue
        if r.status_code in RETRY_STATUS:
            if r.status_code == 429:
                EVENTOS_HTTP["http_429"] += 1
            if intento == max_attempts:
                r.raise_for_status()
            EVENTOS_HTTP["reintentos"] += 1
            time.sleep(min(_espera_retry_after(r.headers.get("Retry-After"), intento, base_backoff), 20))
            continue
        if r.status_code >= 400:
            try:
                detalle = r.json().get("message") or r.text[:400]
            except Exception:
                detalle = r.text[:400]
            raise ValueError(f"HTTP {r.status_code} en datos.gov.co: {detalle}\n"
                             "Un nombre de columna o filtro inválido no se corrige reintentando.")
        return r.json(), {"status": r.status_code, "elapsed_s": round(time.perf_counter() - inicio, 4),
                          "bytes": len(r.content), "attempts": intento}
    raise RuntimeError(ultimo)


def count_rows(endpoint_id, where):
    filas, _ = request_json(f"{BASE}/{endpoint_id}.json", {"$select": "count(*) AS n", "$where": where})
    if not filas or "n" not in filas[0]:
        raise RuntimeError("datos.gov.co no devolvió el conteo esperado.")
    return int(filas[0]["n"])


# ── Caché de páginas: firma + SHA-256 + escritura atómica ─────────────────────
def query_signature(endpoint_id, *, select, where, order, limit):
    payload = {"endpoint": endpoint_id, "select": list(select), "where": str(where),
               "order": str(order), "limit": int(limit)}
    canon = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _rutas_pagina(cache_dir, offset):
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    stem = f"page_{int(offset):07d}"
    return cache_dir / f"{stem}.json", cache_dir / f"{stem}.meta.json"


def _escritura_atomica(path, contenido: bytes):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".part")
    tmp.write_bytes(contenido)
    os.replace(tmp, path)


def _leer_pagina_cache(data_path, meta_path, *, firma, offset, limit):
    if not data_path.exists() or not meta_path.exists():
        return None
    try:
        raw = data_path.read_bytes()
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if (meta.get("query_signature") != firma or int(meta.get("offset", -1)) != int(offset)
                or int(meta.get("limit", -1)) != int(limit)
                or meta.get("sha256") != hashlib.sha256(raw).hexdigest()):
            return None
        filas = json.loads(raw.decode("utf-8"))
        if not isinstance(filas, list) or int(meta.get("rows", -1)) != len(filas):
            return None
        return filas, {**meta, "from_cache": True}
    except Exception:
        return None


def fetch_page_persisted(endpoint_id, *, select, where, order, limit, offset, cache_dir):
    '''Descarga UNA página y la deja persistida de forma atómica. Un .part nunca es evidencia.'''
    firma = query_signature(endpoint_id, select=select, where=where, order=order, limit=limit)
    data_path, meta_path = _rutas_pagina(cache_dir, offset)
    cacheada = _leer_pagina_cache(data_path, meta_path, firma=firma, offset=offset, limit=limit)
    if cacheada is not None:
        return cacheada
    params = {"$select": ",".join(select), "$where": where, "$order": order,
              "$limit": int(limit), "$offset": int(offset)}
    filas, meta_http = request_json(f"{BASE}/{endpoint_id}.json", params)
    raw = json.dumps(filas, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    meta = {**meta_http, "endpoint": endpoint_id, "offset": int(offset), "limit": int(limit),
            "rows": len(filas), "query_signature": firma, "sha256": hashlib.sha256(raw).hexdigest(),
            "downloaded_at_utc": datetime.now(timezone.utc).isoformat(), "from_cache": False}
    _escritura_atomica(data_path, raw)
    _escritura_atomica(meta_path, json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8"))
    return filas, meta


def fetch_page(endpoint_id, *, select, where, order, limit, offset):
    '''Lectura directa sin caché: solo para la prueba de 50 filas.'''
    params = {"$select": ",".join(select), "$where": where, "$order": order,
              "$limit": int(limit), "$offset": int(offset)}
    filas, meta = request_json(f"{BASE}/{endpoint_id}.json", params)
    return filas, {**meta, "endpoint": endpoint_id, "offset": int(offset), "limit": int(limit), "rows": len(filas)}


# ── Plan de consulta por ventana ──────────────────────────────────────────────
def plan_consulta(ventana):
    '''Las dos consultas SoQL de una ventana, tomadas del contrato (no se escriben a mano).'''
    return {
        "procesos": {"endpoint": C.ENDPOINTS["procesos"], "select": C.SELECT_PROCESOS,
                     "where": C.where_procesos(ventana), "order": C.ORDER_PROCESOS},
        "contratos": {"endpoint": C.ENDPOINTS["contratos"], "select": C.SELECT_CONTRATOS,
                      "where": C.where_contratos(ventana), "order": C.ORDER_CONTRATOS},
    }


def offsets_para(n, page_size=C.PAGE_SIZE):
    return list(range(0, int(n), int(page_size)))


def limite_pagina(offset, n, page_size=C.PAGE_SIZE):
    return min(int(page_size), int(n) - int(offset))


def descargador(ventana, dataset, n, cache_dir):
    '''Devuelve descargar_pagina(offset) -> (filas, meta) para una fuente de la ventana.'''
    q = plan_consulta(ventana)[dataset]

    def descargar_pagina(offset):
        return fetch_page_persisted(q["endpoint"], select=q["select"], where=q["where"], order=q["order"],
                                    limit=limite_pagina(offset, n), offset=offset, cache_dir=cache_dir)
    return descargar_pagina


def unir_paginas(paginas, n_esperado, columnas):
    '''paginas: {offset: (filas, meta)} en cualquier orden -> (DataFrame en orden de offset, metas).'''
    orden = sorted(paginas)
    filas = [f for o in orden for f in paginas[o][0]]
    metas = [paginas[o][1] for o in orden]
    df = pd.DataFrame(filas, columns=None) if filas else pd.DataFrame(columns=columnas)
    for c in columnas:
        if c not in df.columns:
            df[c] = None
    df = df[columnas]
    if len(df) != int(n_esperado):
        raise RuntimeError(f"Descarga incompleta: se esperaban {n_esperado} filas y llegaron {len(df)}.")
    return df.reset_index(drop=True), metas


# ── Hash canónico del snapshot ────────────────────────────────────────────────
def _canon(v):
    if v is None:
        return None
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False, sort_keys=True)
    if isinstance(v, float) and math.isnan(v):
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    return str(v)


def canonical_hash(df, columnas):
    '''Huella del multiconjunto de filas: no depende del orden y conserva duplicados.'''
    if not isinstance(df, pd.DataFrame):
        return None
    cols = sorted(columnas)
    lineas = []
    for registro in df.reindex(columns=cols).to_dict("records"):
        lineas.append(json.dumps({c: _canon(registro.get(c)) for c in cols}, ensure_ascii=False,
                                 sort_keys=True, separators=(",", ":")))
    lineas.sort()
    return hashlib.sha256("\n".join(lineas).encode("utf-8")).hexdigest()


# ── Verificación del caché ────────────────────────────────────────────────────
def validar_cache(cache_dir, offsets_esperados):
    '''(ok, mensaje): todos los chunks esperados, íntegros, sin .part y sin chunks extra.'''
    cache_dir = Path(cache_dir)
    if not cache_dir.exists():
        return False, "no existe el caché"
    if list(cache_dir.glob("*.part")):
        return False, "quedaron archivos .part (descarga interrumpida)"
    esperados = [int(x) for x in offsets_esperados]
    for offset in esperados:
        data_path = cache_dir / f"page_{offset:07d}.json"
        meta_path = cache_dir / f"page_{offset:07d}.meta.json"
        if not data_path.exists() or not meta_path.exists():
            return False, f"falta el chunk {offset}"
        try:
            raw = data_path.read_bytes()
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            filas = json.loads(raw.decode("utf-8"))
        except Exception:
            return False, f"chunk ilegible {offset}"
        if not isinstance(filas, list) or int(meta.get("rows", -1)) != len(filas):
            return False, f"conteo inválido en el chunk {offset}"
        if int(meta.get("offset", -1)) != offset:
            return False, f"offset inválido en el chunk {offset}"
        if not re.fullmatch(r"[0-9a-f]{64}", str(meta.get("query_signature", ""))):
            return False, f"firma inválida en el chunk {offset}"
        if meta.get("sha256") != hashlib.sha256(raw).hexdigest():
            return False, f"SHA-256 no coincide en el chunk {offset} (archivo alterado o incompleto)"
    extras = []
    for p in cache_dir.glob("page_*.json"):
        if p.name.endswith(".meta.json"):
            continue
        m = re.fullmatch(r"page_(\d{7})\.json", p.name)
        if m and int(m.group(1)) not in esperados:
            extras.append(int(m.group(1)))
    if extras:
        return False, "chunks extra de otra consulta: " + ",".join(map(str, sorted(extras)))
    return True, f"{len(esperados)} chunks íntegros"


def leer_paginas(cache_dir, offsets):
    '''Filas de las páginas del caché, en orden de offset (el validador parte de aquí).'''
    filas = []
    for offset in offsets:
        filas.extend(json.loads((Path(cache_dir) / f"page_{int(offset):07d}.json").read_text(encoding="utf-8")))
    return filas


def firmas_cache(cache_dir, offsets):
    out = []
    for offset in offsets:
        meta = json.loads((Path(cache_dir) / f"page_{int(offset):07d}.meta.json").read_text(encoding="utf-8"))
        out.append(meta.get("query_signature"))
    return out


def limpiar_cache(cache_dir):
    '''Para repetir limpio: si SECOP cambió entre corridas, el hash puede diferir sin culpa del grupo.'''
    shutil.rmtree(cache_dir, ignore_errors=True)


def rango_fechas(serie):
    fechas = pd.to_datetime(pd.Series(serie).astype(str).str[:10], errors="coerce").dropna()
    if fechas.empty:
        return None, None, 0
    ini, fin = fechas.min(), fechas.max()
    return ini.strftime("%Y-%m-%d"), fin.strftime("%Y-%m-%d"), int((fin - ini).days) + 1


def perfil_calidad(df, clave):
    return {
        "filas": int(len(df)),
        "columnas": int(df.shape[1]),
        "claves_duplicadas": int(df[clave].duplicated().sum()) if clave in df else None,
        "claves_nulas": int(df[clave].isna().sum()) if clave in df else None,
        "pct_nulos": {c: round(float(df[c].isna().mean() * 100), 2) for c in df.columns},
    }


# ── Cruce procesos → contratos ────────────────────────────────────────────────
def _txt(serie):
    return serie.fillna("").astype(str).str.strip()


def _num(serie):
    return pd.to_numeric(serie, errors="coerce")


def mapa_portafolio(procesos):
    p = pd.DataFrame({"id_del_portafolio": _txt(procesos["id_del_portafolio"]),
                      "id_proceso": _txt(procesos["id_del_proceso"])})
    p = p[p["id_del_portafolio"].ne("") & p["id_proceso"].ne("")]
    return p.drop_duplicates("id_del_portafolio", keep="first")


def cruce(procesos, contratos):
    '''Procesos únicos con al menos un contrato y cobertura del cruce id_del_portafolio → proceso_de_compra.'''
    claves = set(_txt(contratos["proceso_de_compra"])) - {""}
    port = _txt(procesos["id_del_portafolio"])
    mask = port.ne("") & port.isin(claves)
    unicos = int(_txt(procesos["id_del_proceso"]).nunique())
    matched = int(_txt(procesos.loc[mask, "id_del_proceso"]).nunique())
    return {"procesos_unicos": unicos, "matched_processes": matched,
            "join_coverage": (matched / unicos) if unicos else 0.0,
            "join_key": "id_del_portafolio -> proceso_de_compra"}


def relaciones_contrato(procesos, contratos):
    '''Una fila por contrato enlazado a un proceso del snapshot (base de contratos_resumen).'''
    c = pd.DataFrame({
        "id_contrato": _txt(contratos["id_contrato"]),
        "proceso_de_compra": _txt(contratos["proceso_de_compra"]),
        "nit_entidad": _txt(contratos["nit_entidad"]),
        "entidad": _txt(contratos["nombre_entidad"]),
        "nit_proveedor": _txt(contratos["documento_proveedor"]),
        "proveedor": _txt(contratos["proveedor_adjudicado"]),
        "estado_contrato": _txt(contratos["estado_contrato"]),
        "valor": _num(contratos["valor_del_contrato"]).fillna(0.0),
    })
    c = c[c["id_contrato"].ne("") & c["proceso_de_compra"].ne("")].drop_duplicates("id_contrato", keep="first")
    r = c.merge(mapa_portafolio(procesos), left_on="proceso_de_compra", right_on="id_del_portafolio", how="inner")
    cols = ["id_contrato", "id_proceso", "nit_entidad", "entidad", "nit_proveedor", "proveedor", "estado_contrato", "valor"]
    return r[cols].sort_values(["id_proceso", "id_contrato"], kind="mergesort").reset_index(drop=True)


def _anio(fecha):
    s = str(fecha or "")[:4]
    return int(s) if s.isdigit() else None


def _int_o_none(v):
    try:
        f = float(v)
        return None if math.isnan(f) else int(f)
    except (TypeError, ValueError):
        return None


def _float_o_none(v):
    try:
        f = float(v)
        return None if math.isnan(f) else f
    except (TypeError, ValueError):
        return None


def historico(procesos, relaciones):
    '''Una fila por id_del_proceso (la primera del snapshot) con el resumen de sus contratos.'''
    p = procesos.copy()
    p["_id"] = _txt(p["id_del_proceso"])
    p = p[p["_id"].ne("")].drop_duplicates("_id", keep="first")
    agg = relaciones.groupby("id_proceso").agg(
        contratos_cantidad=("id_contrato", "nunique"), valor_contratos=("valor", "sum"),
        contratos_estados=("estado_contrato", lambda s: sorted({x for x in s if x}))).reset_index()
    h = pd.DataFrame({
        "id_proceso": p["_id"], "id_portafolio": _txt(p["id_del_portafolio"]),
        "entidad": _txt(p["entidad"]), "nit_entidad": _txt(p["nit_entidad"]),
        "departamento": _txt(p["departamento_entidad"]), "ciudad": _txt(p["ciudad_entidad"]),
        "fecha_publicacion": _txt(p["fecha_de_publicacion_del"]).str[:10],
        "anio": p["fecha_de_publicacion_del"].map(_anio),
        "precio_base": _num(p["precio_base"]),
        "modalidad": _txt(p["modalidad_de_contratacion"]), "estado": _txt(p["estado_del_procedimiento"]),
        "nit_proveedor": _txt(p["nit_del_proveedor_adjudicado"]), "proveedor": _txt(p["nombre_del_proveedor"]),
    }).merge(agg, on="id_proceso", how="left")
    h["contratos_cantidad"] = h["contratos_cantidad"].fillna(0).astype(int)
    h["valor_contratos"] = h["valor_contratos"].fillna(0.0).astype(float)
    h["contratos_estados"] = h["contratos_estados"].map(lambda x: x if isinstance(x, list) else [])
    return h.reset_index(drop=True)


def _documento(r, pareja):
    return {
        "id_proceso": r["id_proceso"],
        "entidad": {"nit": r["nit_entidad"], "nombre": r["entidad"], "departamento": r["departamento"],
                    "ciudad": r["ciudad"]},
        "proceso": {"fecha_publicacion": r["fecha_publicacion"], "anio": _int_o_none(r["anio"]),
                    "precio_base": _float_o_none(r["precio_base"]), "modalidad": r["modalidad"],
                    "estado": r["estado"]},
        "proveedor_adjudicado": {"nit": r["nit_proveedor"], "nombre": r["proveedor"]},
        "contratos_resumen": {"cantidad": int(r["contratos_cantidad"]), "valor_total": float(r["valor_contratos"]),
                              "estados": list(r["contratos_estados"])},
        "metadata_ingesta": {"pareja": pareja, "version": C.VERSION, "fuentes": list(C.ENDPOINTS.values())},
    }


def construir_documentos(procesos, contratos, grano, pareja):
    '''Documentos según el grano elegido. Solo 'un documento por proceso' respeta el caso.'''
    rel = relaciones_contrato(procesos, contratos)
    if grano == C.GRANOS[1]:
        return [_documento(r, pareja) for r in historico(procesos, rel).to_dict("records")]
    if grano == C.GRANOS[0]:
        h = historico(procesos, rel).set_index("id_proceso")
        docs = []
        for pid in _txt(procesos["id_del_proceso"]):
            if pid in h.index:
                docs.append(_documento({**h.loc[pid].to_dict(), "id_proceso": pid}, pareja))
        return docs
    if grano == C.GRANOS[2]:
        h = historico(procesos, rel).set_index("id_proceso")
        docs = []
        for r in rel.to_dict("records"):
            base = {**h.loc[r["id_proceso"]].to_dict(), "id_proceso": r["id_proceso"],
                    "contratos_cantidad": 1, "valor_contratos": r["valor"], "contratos_estados": [r["estado_contrato"]]}
            docs.append(_documento(base, pareja))
        return docs
    raise ValueError("Elige un grano de la lista.")


def huella_documentos(documentos):
    '''Huella de los campos que usan las consultas: detecta documentos alterados.'''
    filas = sorted(
        json.dumps([d.get("id_proceso"), (d.get("proceso") or {}).get("precio_base"),
                    (d.get("proceso") or {}).get("anio"), (d.get("entidad") or {}).get("departamento"),
                    (d.get("contratos_resumen") or {}).get("cantidad"),
                    (d.get("contratos_resumen") or {}).get("valor_total")], ensure_ascii=False)
        for d in documentos)
    return hashlib.sha256("\n".join(filas).encode("utf-8")).hexdigest()


# ── Referencias de E2 y E3 (lo que Atlas debe devolver) ───────────────────────
def _pasa_a(d):
    pb = (d.get("proceso") or {}).get("precio_base")
    cant = (d.get("contratos_resumen") or {}).get("cantidad") or 0
    return pb is not None and float(pb) > 0 and int(cant) > 0


def _clave_orden(d):
    return (-float((d.get("contratos_resumen") or {}).get("valor_total") or 0.0), str(d.get("id_proceso")))


def ref_consulta_a(documentos):
    return sum(1 for d in documentos if _pasa_a(d))


def ref_consulta_b(documentos, n=10):
    return [d["id_proceso"] for d in sorted(documentos, key=_clave_orden)[:n]]


def ref_bandeja(documentos):
    filas = []
    for d in sorted((d for d in documentos if _pasa_a(d)), key=_clave_orden)[:C.BANDEJA_MAX]:
        filas.append({"id_proceso": d["id_proceso"], "anio": (d.get("proceso") or {}).get("anio"),
                      "departamento": (d.get("entidad") or {}).get("departamento"),
                      "entidad": (d.get("entidad") or {}).get("nombre"),
                      "valor_contratos": float((d.get("contratos_resumen") or {}).get("valor_total") or 0.0)})
    return filas


# ── E4: Cassandra query-first ─────────────────────────────────────────────────
def datos_cassandra(bandeja):
    df = pd.DataFrame(bandeja, columns=C.COLUMNAS_BANDEJA).copy()
    df["anio"] = pd.to_numeric(df["anio"], errors="coerce").astype("Int64")
    df["valor_contratos"] = pd.to_numeric(df["valor_contratos"], errors="coerce").astype(float)
    df["departamento"] = df["departamento"].fillna("").astype(str)
    return df.dropna(subset=["anio"]).reset_index(drop=True)


def particion_prueba(df):
    conteo = (df.groupby(["anio", "departamento"]).size().rename("n").reset_index()
              .sort_values(["n", "anio", "departamento"], ascending=[False, True, True], kind="mergesort"))
    fila = conteo.iloc[0]
    return int(fila["anio"]), str(fila["departamento"])


def ref_cassandra(df, particion):
    anio, dep = particion
    parte = df[(df["anio"] == anio) & (df["departamento"] == dep)]
    top = parte.sort_values(["valor_contratos", "id_proceso"], ascending=[False, True], kind="mergesort").head(10)
    return {"anio": anio, "departamento": dep, "count": int(len(parte)), "top10_ids": top["id_proceso"].tolist()}


def _cql_txt(v):
    return "'" + str(v).replace("'", "''") + "'"


def _cql_valor(v, tipo):
    num = f"{float(v):.2f}"
    return _cql_txt(num) if tipo == "text" else num


def clave_primaria(diseno):
    part = list(C.OPCIONES_PARTICION[diseno["particion"]])
    clus = [(c, o) for c, o in C.OPCIONES_CLUSTERING[diseno["clustering"]] if c not in part]
    return part, clus


def generar_cql(diseno, df, keyspace, tabla, particion):
    '''Script completo para pegar en CQL Console, derivado de TUS decisiones de diseño.'''
    part, clus = clave_primaria(diseno)
    tipo = diseno["tipo_valor"]
    pk = "(" + ", ".join(part) + ")"
    if clus:
        pk += ", " + ", ".join(c for c, _ in clus)
    create = (f"CREATE TABLE IF NOT EXISTS {keyspace}.{tabla} (\n"
              f"  anio int,\n  departamento text,\n  valor_contratos {tipo},\n  id_proceso text,\n  entidad text,\n"
              f"  PRIMARY KEY ({pk})\n)")
    if clus:
        create += " WITH CLUSTERING ORDER BY (" + ", ".join(f"{c} {o}" for c, o in clus) + ")"
    create += ";"
    inserts = [
        f"INSERT INTO {keyspace}.{tabla} (anio, departamento, valor_contratos, id_proceso, entidad) VALUES "
        f"({int(r['anio'])}, {_cql_txt(r['departamento'])}, {_cql_valor(r['valor_contratos'], tipo)}, "
        f"{_cql_txt(r['id_proceso'])}, {_cql_txt(r['entidad'])});"
        for r in df.to_dict("records")]
    anio, dep = particion
    where = f"WHERE anio = {anio} AND departamento = {_cql_txt(dep)}"
    select_count = f"SELECT COUNT(*) FROM {keyspace}.{tabla} {where};"
    select_top = f"SELECT id_proceso, valor_contratos FROM {keyspace}.{tabla} {where} LIMIT 10;"
    script = "\n".join([f"DROP TABLE IF EXISTS {keyspace}.{tabla};", create, "", *inserts, "", select_count, select_top]) + "\n"
    return {"create": create, "inserts": inserts, "select_count": select_count, "select_top": select_top,
            "script": script, "primary_key": pk}


def consecuencia_diseno(diseno):
    '''Qué verás en Astra con cada decisión (se muestra antes de ejecutar).'''
    avisos = []
    if diseno["particion"] != C.DISENO_CORRECTO["particion"]:
        avisos.append("La consulta pide anio y departamento con igualdad, pero tu partición no es (anio, departamento): "
                      "Astra responderá 'Cannot execute this query as it might involve data filtering' y pedirá "
                      "ALLOW FILTERING, que está prohibido en este taller.")
    if diseno["clustering"] == "valor_contratos DESC":
        avisos.append("Sin id_proceso en la clave, dos procesos con el mismo valor en la misma partición tienen la misma "
                      "PRIMARY KEY: el segundo INSERT sobrescribe al primero y el COUNT sale menor.")
    if diseno["clustering"] == "id_proceso ASC, valor_contratos DESC":
        avisos.append("Con id_proceso primero, la partición queda ordenada por identificador y LIMIT 10 devuelve los diez "
                      "primeros IDs, no los diez de mayor valor.")
    if diseno["tipo_valor"] == "text":
        avisos.append("Con valor_contratos como text el orden es alfabético: '9000.00' queda antes que '15000000.00'.")
    return avisos


def diseno_correcto(diseno):
    return (diseno.get("particion") == C.DISENO_CORRECTO["particion"]
            and diseno.get("clustering") == C.DISENO_CORRECTO["clustering"]
            and diseno.get("tipo_valor") in C.TIPOS_VALOR_NUMERICOS)


# ── E5: grafo Entidad → Contrato → Proveedor ──────────────────────────────────
def relaciones_grafo(contratos):
    '''Todos los contratos del snapshot: el contrato ya trae entidad y proveedor, no necesita el cruce.'''
    g = pd.DataFrame({
        "id_contrato": _txt(contratos["id_contrato"]),
        "nit_entidad": _txt(contratos["nit_entidad"]),
        "entidad": _txt(contratos["nombre_entidad"]),
        "nit_proveedor": _txt(contratos["documento_proveedor"]),
        "proveedor": _txt(contratos["proveedor_adjudicado"]),
        "valor": _num(contratos["valor_del_contrato"]).fillna(0.0),
        "fecha_firma": _txt(contratos["fecha_de_firma"]).str[:10],
        "tipo_contrato": _txt(contratos["tipo_de_contrato"]),
    })
    g = g[g["id_contrato"].ne("") & g["nit_entidad"].ne("") & g["nit_proveedor"].ne("")
          & g["nit_proveedor"].str.casefold().ne("no definido")]
    return g.drop_duplicates("id_contrato", keep="first").reset_index(drop=True)


def _proveedores_compartidos(rel):
    por_prov = rel.groupby("nit_proveedor")["nit_entidad"].nunique()
    return set(por_prov[por_prov > 1].index)


def entidad_ancla(rel):
    '''Regla de E5: la entidad con más proveedores compartidos (desempate: más contratos, NIT ascendente).'''
    compartidos = _proveedores_compartidos(rel)
    por_ent = rel[rel["nit_proveedor"].isin(compartidos)].groupby("nit_entidad")["nit_proveedor"].nunique()
    contratos = rel.groupby("nit_entidad")["id_contrato"].nunique()
    tabla = pd.DataFrame({"compartidos": por_ent, "contratos": contratos}).fillna(0).astype(int)
    tabla["nit"] = tabla.index.astype(str)
    tabla = tabla.sort_values(["compartidos", "contratos", "nit"], ascending=[False, False, True], kind="mergesort")
    nit = str(tabla.index[0])
    nombres = rel.loc[rel["nit_entidad"] == nit, "entidad"]
    return {"nit_ancla": nit, "nombre": nombres.mode().iat[0] if not nombres.empty else "",
            "nombres_bajo_nit": int(nombres.nunique()), "proveedores_compartidos": int(tabla.iloc[0]["compartidos"]),
            "contratos": int(tabla.iloc[0]["contratos"])}


def ranking_ancla(rel, nit_ancla):
    '''Por cada proveedor de la ancla que también contrata con otra entidad: contratos con la ancla y entidades conectadas.'''
    ancla = rel[rel["nit_entidad"] == nit_ancla]
    con_ancla = ancla.groupby("nit_proveedor")["id_contrato"].nunique().rename("contratos_con_ancla")
    otras = (rel[rel["nit_proveedor"].isin(con_ancla.index) & rel["nit_entidad"].ne(nit_ancla)]
             .groupby("nit_proveedor")["nit_entidad"].nunique().rename("entidades_conectadas"))
    r = pd.concat([con_ancla, otras], axis=1, join="inner").reset_index().rename(columns={"index": "nit_proveedor"})
    nombres = rel.groupby("nit_proveedor")["proveedor"].agg(lambda s: s.mode().iat[0])
    r["proveedor"] = r["nit_proveedor"].map(nombres)
    r = r.sort_values(["entidades_conectadas", "contratos_con_ancla", "nit_proveedor"],
                      ascending=[False, False, True], kind="mergesort").reset_index(drop=True)
    return r[["nit_proveedor", "proveedor", "contratos_con_ancla", "entidades_conectadas"]].astype(
        {"contratos_con_ancla": int, "entidades_conectadas": int})


def conteos_grafo(rel):
    return {"entidades": int(rel["nit_entidad"].nunique()), "contratos": int(rel["id_contrato"].nunique()),
            "proveedores": int(rel["nit_proveedor"].nunique()), "firma": int(len(rel)), "adjudicado_a": int(len(rel))}


CYPHER_RESTRICCIONES = [
    "CREATE CONSTRAINT tc1_entidad_nit IF NOT EXISTS FOR (e:Entidad) REQUIRE e.nit IS UNIQUE",
    "CREATE CONSTRAINT tc1_contrato_id IF NOT EXISTS FOR (c:Contrato) REQUIRE c.id IS UNIQUE",
    "CREATE CONSTRAINT tc1_proveedor_nit IF NOT EXISTS FOR (p:Proveedor) REQUIRE p.nit IS UNIQUE",
]
CYPHER_CARGA = '''UNWIND $filas AS fila
MERGE (e:Entidad {nit: fila.nit_entidad})
  SET e.nombre = fila.entidad
MERGE (c:Contrato {id: fila.id_contrato})
  SET c.valor = fila.valor, c.fecha_firma = fila.fecha_firma, c.tipo = fila.tipo_contrato, c.pareja = fila.pareja
MERGE (p:Proveedor {nit: fila.nit_proveedor})
  SET p.nombre = fila.proveedor
MERGE (e)-[:FIRMA]->(c)
MERGE (c)-[:ADJUDICADO_A]->(p)'''
CYPHER_ANCLA = '''MATCH (e:Entidad)-[:FIRMA]->(:Contrato)-[:ADJUDICADO_A]->(p:Proveedor)<-[:ADJUDICADO_A]-(:Contrato)<-[:FIRMA]-(otra:Entidad)
WHERE otra <> e
WITH e, count(DISTINCT p) AS proveedores_compartidos
MATCH (e)-[:FIRMA]->(c:Contrato)
RETURN e.nit AS nit, e.nombre AS entidad, proveedores_compartidos, count(DISTINCT c) AS contratos
ORDER BY proveedores_compartidos DESC, contratos DESC, nit ASC
LIMIT 5'''
CYPHER_CONTEXTO = '''MATCH (a:Entidad {nit: $nit_ancla})-[:FIRMA]->(c:Contrato)-[:ADJUDICADO_A]->(p:Proveedor)
RETURN a.nombre AS entidad, count(DISTINCT c) AS contratos, count(DISTINCT p) AS proveedores'''


def cypher_para_aura(consulta, nit_ancla):
    '''Versión para pegar en Aura Query: el parámetro se reemplaza por el valor literal.'''
    return consulta.replace("$nit_ancla", json.dumps(str(nit_ancla)))
