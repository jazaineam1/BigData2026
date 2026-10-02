# -*- coding: utf-8 -*-
'''Pasos del cuaderno TC1, en el orden de las etapas.

Cada función deja su evidencia en la carpeta de trabajo y la imprime. Si Colab se
reinició, cada etapa vuelve a leer lo que necesita desde esos archivos: solo hay que
volver a ejecutar las celdas de preparación e identidad, y la de conexión del servicio.
'''
from __future__ import annotations

import json
import re
import time
import unicodedata
from pathlib import Path

import pandas as pd

import tc1_contrato as C
import tc1_secop as S
import tc1_servicios as X
import tc1_validador as V

ESTADO = {}


def _R():
    if "out" not in ESTADO:
        raise RuntimeError("Primero ejecuta la celda «0 · Identidad de la pareja».")
    return C.rutas(ESTADO["out"])


def _marca(ok):
    return "✓ sí" if ok else "✗ no"


def _sin_tildes(texto):
    t = unicodedata.normalize("NFKD", str(texto or "")).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "", t).upper()


# ── 0 · Identidad ─────────────────────────────────────────────────────────────
def iniciar(pareja, integrantes, guardar_drive, base=None):
    if pareja not in C.VENTANAS:
        raise ValueError("Elige en la lista el PAREJA_ID que te confirmó el docente por correo. Si aún no lo tienes, "
                         f"escríbele a {C.CORREO_DOCENTE} antes de seguir: no elijas uno por tu cuenta.")
    vivos = [{"nombre": n.strip(), "codigo": c.strip(), "apellido": a.strip()} for n, c, a in integrantes if n.strip()]
    if not vivos or any(not x["codigo"] or not x["apellido"] for x in vivos):
        raise ValueError("Escribe el nombre, el código y el primer apellido de cada integrante "
                         "(los apellidos nombran tu carpeta de entrega).")
    raiz_drive = None
    if guardar_drive.startswith("Sí") and X.EN_COLAB:
        raiz_drive = X.montar_drive()
    out = Path(base or ("/content" if X.EN_COLAB else ".")) / f"tc1_{pareja}"
    restaurado = X.restaurar_avance(out, pareja, raiz_drive)
    out.mkdir(parents=True, exist_ok=True)
    ESTADO.clear()
    ESTADO.update({"out": out, "pareja": pareja, "drive": raiz_drive, "integrantes": vivos})
    X.escribir_json(C.rutas(out)["identidad"], {"pareja": pareja, "integrantes": vivos, "version": C.VERSION})
    ini, fin = C.VENTANAS[pareja]
    print(f"Pareja {pareja} · ventana {ini[:10]} → {fin[:10]}")
    print(f"Si {pareja} no es el número que te asignó el docente, corrígelo ahora: con otro número descargarías datos ajenos.")
    print(f"Carpeta de trabajo: {out}")
    print("Avance en Drive: " + ("restaurado desde tu última sesión" if restaurado else
                                 "activado" if raiz_drive else "desactivado (si Colab se reinicia, repites desde E1)"))
    return out, raiz_drive


def guardar_avance():
    destino = X.guardar_avance(ESTADO["out"], ESTADO["pareja"], ESTADO.get("drive"))
    if destino:
        print(f"Avance guardado en Drive: {destino.name}")


def checkpoint(etapa):
    m = V.evaluar(ESTADO["out"], escribir=False)
    print(f"CHECKPOINT {etapa} · {C.STAGE_NOMBRE[etapa]}")
    for item, c in m["controles"].items():
        if c["etapa"] != etapa:
            continue
        estado = "✓" if c["ok"] else "✗"
        nota = " (provisional: falta que el docente vea la captura)" if c["pendiente_visual"] else ""
        print(f"  {estado} {item} · {c['descripcion']} · {c['puntos']}/{c['maximo']}{nota}")
        if not c["ok"]:
            print(f"      Qué revisar: {c['feedback']}")
            print(f"      Encontrado: {c['evidencia']}")
    e = m["etapas"][etapa]
    print(f"  → {e['puntos']}/{e['maximo']} puntos en {etapa}.", "Puedes pasar a la siguiente etapa." if e["puntos"] == e["maximo"]
          else "Corrige lo marcado con ✗ antes de seguir (puedes seguir, pero esos puntos quedan en 0).")
    print(f"  Archivos de {etapa} en tu carpeta (irán en el ZIP):")
    for linea in _arbol_etapa(etapa):
        print("    " + linea)
    guardar_avance()
    return m


# La captura de E2 se sube en la celda de captura de E3; las demás, en su propia etapa.
CAPTURA_SE_SUBE_EN = {"E2": "E3", "E4": "E4", "E5": "E5"}


def _arbol_etapa(etapa):
    R = _R()
    lineas = []
    for rel in C.ARTEFACTOS[etapa]:
        p = R[etapa] / rel
        kb = p.stat().st_size / 1024 if p.exists() else 0
        nota = (f" · {kb:,.0f} KB" if kb >= 1 else " · <1 KB") if p.exists() else ""
        if not p.exists() and rel == C.CAPTURAS.get(etapa):
            nota = f" (captura: se sube en la celda CAPTURA de {CAPTURA_SE_SUBE_EN[etapa]})"
        lineas.append(f"{'✓' if p.exists() else '✗'} {etapa}/{rel}{nota}")
    if etapa == "E1":
        paginas = [p for p in (R["raw"] / "pages").rglob("page_*.json") if not p.name.endswith(".meta.json")]
        lineas.append(f"{'✓' if paginas else '✗'} E1/raw/pages/ · {len(paginas)} páginas firmadas (procesos ×2 y contratos)")
    return lineas


def ver_carpeta():
    '''Tu carpeta de trabajo tal como irá en el ZIP: ✓ lo que existe, ✗ lo que falta.'''
    R, out = _R(), ESTADO["out"]
    print(f"{out.name}/   ← tu carpeta de trabajo = el contenido de TC1_{ESTADO['pareja']}.zip")
    print(f"  {'✓' if R['identidad'].exists() else '✗'} identidad.json")
    for etapa in C.ARTEFACTOS:
        for linea in _arbol_etapa(etapa):
            print("  " + linea)
    print(f"  {'✓' if R['manifest'].exists() else '✗'} {C.MANIFEST} (lo escribe la validación final)")


# ── E1 ────────────────────────────────────────────────────────────────────────
def contrato_e1():
    R, pareja = _R(), ESTADO["pareja"]
    contrato = C.contrato_de_datos(pareja)
    X.escribir_json(R["E1"] / "00_dataset_contract.json", contrato)
    plan = S.plan_consulta(pareja)
    ESTADO["plan"] = plan
    for nombre, q in plan.items():
        print(f"{nombre.upper()} · {q['endpoint']}")
        print(f"  $where : {q['where']}")
        print(f"  $order : {q['order']}")
        print(f"  $select: {len(q['select'])} columnas")
    print("Contrato guardado en E1/00_dataset_contract.json")
    return plan


def preflight_e1():
    R, pareja = _R(), ESTADO["pareja"]
    plan = S.plan_consulta(pareja)
    total_p = S.count_rows(plan["procesos"]["endpoint"], plan["procesos"]["where"])
    total_c = S.count_rows(plan["contratos"]["endpoint"], plan["contratos"]["where"])
    n_p, n_c = min(C.TARGET_PROCESOS, total_p), min(C.TARGET_CONTRATOS, total_c)
    ESTADO.update({"plan": plan, "total_p": total_p, "total_c": total_c, "n_p": n_p, "n_c": n_c})
    print(f"Procesos en tu ventana: {total_p:,} · descargarás los primeros {n_p:,} ({len(S.offsets_para(n_p))} páginas de {C.PAGE_SIZE})")
    print(f"Contratos con empresas en tu ventana: {total_c:,} · descargarás los primeros {n_c:,} ({len(S.offsets_para(n_c))} páginas)")
    print(f"En total pedirás {len(S.offsets_para(n_p))} páginas de procesos dos veces (secuencial y concurrente) "
          f"y {len(S.offsets_para(n_c))} de contratos.")
    return (S.descargador(pareja, "procesos", n_p, R["pag_seq"]),
            S.descargador(pareja, "procesos", n_p, R["pag_thr"]),
            S.offsets_para(n_p), n_p)


def comparar_e1(paginas_seq, seg_seq, paginas_thr, seg_thr, workers):
    R = _R()
    n_p = ESTADO["n_p"]
    seq, metas_seq = S.unir_paginas(paginas_seq, n_p, C.SELECT_PROCESOS)
    thr, metas_thr = S.unir_paginas(paginas_thr, n_p, C.SELECT_PROCESOS)
    h_seq, h_thr = S.canonical_hash(seq, C.SELECT_PROCESOS), S.canonical_hash(thr, C.SELECT_PROCESOS)
    off_seq, off_thr = sorted(paginas_seq), sorted(paginas_thr)
    bench = {
        "workers": int(workers), "n_procesos": n_p, "page_size": C.PAGE_SIZE,
        "offsets_secuencial": off_seq, "offsets_concurrente": off_thr,
        "segundos_secuencial": round(seg_seq, 3), "segundos_concurrente": round(seg_thr, 3),
        "hash_secuencial": h_seq, "hash_concurrente": h_thr,
        "mismos_offsets": off_seq == off_thr == S.offsets_para(n_p), "mismas_filas": len(seq) == len(thr) == n_p,
        "mismo_hash": h_seq == h_thr,
        "paginas_desde_cache": {"secuencial": sum(bool(m.get("from_cache")) for m in metas_seq),
                                "concurrente": sum(bool(m.get("from_cache")) for m in metas_thr)},
        "eventos_http": dict(S.EVENTOS_HTTP),
    }
    X.escribir_json(R["E1"] / "01_benchmark_threads.json", bench)
    ESTADO.update({"procesos": thr, "metas_seq": metas_seq, "metas_thr": metas_thr, "bench": bench})
    print(f"Mismos offsets: {_marca(bench['mismos_offsets'])} · Mismas filas: {_marca(bench['mismas_filas'])} · "
          f"Mismo hash: {_marca(bench['mismo_hash'])}")
    print(f"Tiempo secuencial {seg_seq:.1f} s · concurrente {seg_thr:.1f} s con {workers} workers "
          f"(speedup {seg_seq / seg_thr if seg_thr else 0:.2f}; no se califica)")
    if any(bench["paginas_desde_cache"].values()):
        print("ℹ Algunas páginas salieron del caché: los tiempos no son un benchmark limpio, la equivalencia sí vale.")
    if not bench["mismo_hash"]:
        print("✗ Los hashes no coinciden. Si SECOP cambió entre las dos corridas, repite limpio: ejecuta "
              "secop.limpiar_cache(reglas.rutas(OUT)['pag_seq']) y secop.limpiar_cache(reglas.rutas(OUT)['pag_thr']) "
              "y vuelve a descargar.")
    return bench


def descargador_contratos():
    R, pareja = _R(), ESTADO["pareja"]
    if "n_c" not in ESTADO:
        raise RuntimeError("Ejecuta antes la celda del preflight de E1.")
    return S.descargador(pareja, "contratos", ESTADO["n_c"], R["pag_con"]), S.offsets_para(ESTADO["n_c"])


def consolidar_e1(paginas_contratos):
    R, pareja = _R(), ESTADO["pareja"]
    contratos, metas_con = S.unir_paginas(paginas_contratos, ESTADO["n_c"], C.SELECT_CONTRATOS)
    procesos = ESTADO["procesos"]
    cruce = S.cruce(procesos, contratos)
    fp, fc = S.rango_fechas(procesos["fecha_de_publicacion_del"]), S.rango_fechas(contratos["fecha_de_firma"])
    R["raw"].mkdir(parents=True, exist_ok=True)
    procesos.to_parquet(R["raw"] / "procesos.parquet", index=False)
    contratos.to_parquet(R["raw"] / "contratos.parquet", index=False)
    X.escribir_json(R["E1"] / "01_quality_report.json", {
        **cruce, "procesos": S.perfil_calidad(procesos, "id_del_proceso"),
        "contratos": S.perfil_calidad(contratos, "id_contrato"),
        "fechas_procesos": fp, "fechas_contratos": fc})
    paginas = lambda metas: [{k: m.get(k) for k in ("offset", "limit", "rows", "sha256", "query_signature", "attempts", "from_cache")}
                             for m in metas]
    X.escribir_json(R["E1"] / "01_acquisition_manifest.json", {
        "schema": C.E1_SCHEMA, "version": C.VERSION, "pareja": pareja, "ventana": C.VENTANAS[pareja],
        "consultado_utc": X.ahora_utc(), "totales": {"procesos": ESTADO["total_p"], "contratos": ESTADO["total_c"]},
        "objetivos": {"procesos": ESTADO["n_p"], "contratos": ESTADO["n_c"]},
        "workers": ESTADO["bench"]["workers"], "page_size": C.PAGE_SIZE,
        "procesos": {"paginas_secuencial": paginas(ESTADO["metas_seq"]), "paginas_concurrente": paginas(ESTADO["metas_thr"]),
                     "snapshot_sha256": ESTADO["bench"]["hash_concurrente"]},
        "contratos": {"paginas": paginas(metas_con), "snapshot_sha256": S.canonical_hash(contratos, C.SELECT_CONTRATOS)},
        "eventos_http": dict(S.EVENTOS_HTTP)})
    ESTADO.update({"contratos": contratos, "cruce": cruce})
    print(f"Contratos descargados: {len(contratos):,}")
    print(f"Tu snapshot de procesos cubre {fp[0]} → {fp[1]} ({fp[2]} día(s)); el de contratos {fc[0]} → {fc[1]} ({fc[2]} días).")
    print(f"Procesos únicos con contrato cruzado: {cruce['matched_processes']} de {cruce['procesos_unicos']} "
          f"(cobertura {100 * cruce['join_coverage']:.1f} %) · mínimo exigido {C.MIN_MATCHED_PROCESSES}")
    enlazados = int(contratos["proceso_de_compra"].isin(set(procesos["id_del_portafolio"].dropna())).sum())
    print(f"Contratos que cruzan con tus procesos: {enlazados:,} de {len(contratos):,}")
    print("RAW consolidado: E1/raw/procesos.parquet y E1/raw/contratos.parquet. Desde E2 no se vuelve a consultar la API.")
    return cruce


def _raw():
    R = _R()
    if "procesos" not in ESTADO or "contratos" not in ESTADO:
        if not (R["raw"] / "procesos.parquet").exists():
            raise RuntimeError("Falta el RAW de E1: completa E1 antes de esta etapa.")
        ESTADO["procesos"] = pd.read_parquet(R["raw"] / "procesos.parquet")
        ESTADO["contratos"] = pd.read_parquet(R["raw"] / "contratos.parquet")
    return ESTADO["procesos"], ESTADO["contratos"]


# ── E2 ────────────────────────────────────────────────────────────────────────
def documentos_e2(grano):
    if grano not in C.GRANOS:
        raise ValueError("Elige el grano en la lista desplegable.")
    R, pareja = _R(), ESTADO["pareja"]
    procesos, contratos = _raw()
    docs = S.construir_documentos(procesos, contratos, grano, pareja)
    unicos = int(procesos["id_del_proceso"].nunique())
    ids = [d["id_proceso"] for d in docs]
    repetidos = len(ids) - len(set(ids))
    print(f"Filas de la API: {len(procesos):,} · procesos únicos: {unicos:,} · documentos con este grano: {len(docs):,}")
    print(f"id_proceso repetidos entre documentos: {repetidos:,}")
    if grano != C.GRANO_CORRECTO:
        print("✗ Con este grano un mismo proceso aparece en varios documentos (o faltan procesos sin contrato): "
              "la consulta B contaría el mismo proceso dos veces. Elige otro grano y vuelve a ejecutar.")
        return docs
    rel = S.relaciones_contrato(procesos, contratos)
    R["E2"].mkdir(parents=True, exist_ok=True)
    S.historico(procesos, rel).to_parquet(R["E2"] / "02_secop_integrado.parquet", index=False)
    X.escribir_json(R["E2"] / "02_modelo_documental.json", {"grano": grano, "n_documentos": len(docs),
                                                            "esquema": C.EJEMPLO_DOCUMENTO, "documentos": docs})
    ESTADO["documentos"] = docs
    print("✓ Un documento por proceso. Guardado: E2/02_modelo_documental.json y E2/02_secop_integrado.parquet")
    print("Ejemplo de tu primer documento:")
    print(json.dumps(docs[0], ensure_ascii=False, indent=2)[:1200])
    return docs


def _docs():
    if "documentos" not in ESTADO:
        modelo = X.leer_json(_R()["E2"] / "02_modelo_documental.json", {}) or {}
        if modelo.get("grano") != C.GRANO_CORRECTO:
            raise RuntimeError("Primero genera el modelo documental con el grano correcto (E2.1).")
        ESTADO["documentos"] = modelo["documentos"]
    return ESTADO["documentos"]


def _evidencia_atlas():
    return X.leer_json(_R()["E2"] / "02_atlas_evidence.json", {}) or {}


def _guardar_atlas(**partes):
    ev = {**_evidencia_atlas(), **partes}
    X.escribir_json(_R()["E2"] / "02_atlas_evidence.json", ev)
    return ev


def conectar_atlas_e2():
    cliente, version = X.conectar_atlas()
    ESTADO.update({"atlas": cliente, "atlas_version": version})
    print(f"✓ Conectado a Atlas (MongoDB {version}). Base: {C.ATLAS_DB} · colección: {C.coleccion_oficial(ESTADO['pareja'])}")
    return cliente


def _coleccion():
    if "atlas" not in ESTADO:
        raise RuntimeError("Ejecuta la celda de conexión a Atlas (E2.2): Colab pudo reiniciarse.")
    return ESTADO["atlas"][C.ATLAS_DB][C.coleccion_oficial(ESTADO["pareja"])]


def cargar_e2(estrategia):
    if estrategia not in C.ESTRATEGIAS_CARGA:
        raise ValueError("Elige una estrategia de carga en la lista.")
    docs = _docs()
    db = ESTADO["atlas"][C.ATLAS_DB] if "atlas" in ESTADO else None
    if db is None:
        raise RuntimeError("Ejecuta la celda de conexión a Atlas (E2.2).")
    ensayo = X.ensayar_estrategia(db, ESTADO["pareja"], docs, estrategia)
    print("Ensayo en una colección aparte (se borra al terminar):")
    print(f"  1.ª carga → {ensayo['count_after_first']:,} documentos · 2.ª carga → {ensayo['count_after_second']:,} "
          f"· duplicados {ensayo['duplicates_after_second']:,}" + (f" · error: {ensayo['error_segunda']}" if ensayo["error_segunda"] else ""))
    carga = X.cargar_oficial(db, ESTADO["pareja"], docs, estrategia, ESTADO["atlas_version"])
    _guardar_atlas(capturado_por="pymongo", server_version=ESTADO["atlas_version"], carga=carga, ensayo=ensayo)
    ok = (carga["count_after_first"] == carga["count_after_second"] == len(docs)
          and carga["duplicates_after_second"] == 0 and not carga["error_segunda"])
    print(f"Carga oficial en {C.coleccion_oficial(ESTADO['pareja'])}: 1.ª {carga['count_after_first']:,} · "
          f"2.ª {carga['count_after_second']:,} · duplicados {carga['duplicates_after_second']:,} → idempotente: {_marca(ok)}")
    if not ok:
        print("✗ Esta estrategia no resiste una segunda ejecución. Cambia la estrategia y vuelve a ejecutar la celda "
              "(la colección se vacía antes de cada carga y conserva sus índices).")
    return carga


def indices_e2():
    indices = X.capturar_indices(_coleccion())
    _guardar_atlas(indices=indices)
    for ix in indices:
        print(f"  {ix['nombre']}: {ix['clave']}{' · ÚNICO' if ix['unico'] else ''}")
    unico = any(ix["unico"] and [c[0] for c in ix["clave"]] == ["id_proceso"] for ix in indices)
    alineado = V._indice_alineado(indices)
    print(f"Índice único en id_proceso: {_marca(unico)} · índice alineado con una consulta: "
          f"{_marca(bool(alineado))}{f' ({alineado}: ' + C.CAMPOS_INDICE_ALINEADOS[alineado] + ')' if alineado else ''}")
    return indices


def consulta_a_e2(texto):
    filtro = X.parse_consulta(texto)
    n = X.ejecutar_consulta_a(_coleccion(), filtro)
    _guardar_atlas(consulta_a={"texto": X.limpiar_texto_pegado(texto), "filtro": filtro, "resultado": n})
    ok = n == S.ref_consulta_a(_docs())
    print(f"Tu filtro devuelve {n:,} documentos en Atlas · coincide con la referencia de tu snapshot: {_marca(ok)}")
    if not ok:
        print("  Revisa: los dos campos (proceso.precio_base y contratos_resumen.cantidad) y el operador $gt con 0.")
    return n


def consulta_b_e2(texto_orden, texto_filtro="{}"):
    orden, filtro = X.parse_consulta(texto_orden), X.parse_consulta(texto_filtro or "{}")
    ids, valores = X.ejecutar_consulta_b(_coleccion(), filtro, orden, 10)
    _guardar_atlas(consulta_b={"texto_orden": X.limpiar_texto_pegado(texto_orden), "orden": orden, "filtro": filtro,
                               "limite": 10, "ids": ids, "valores": valores})
    ok = ids == S.ref_consulta_b(_docs())
    for i, (pid, v) in enumerate(zip(ids, valores), 1):
        print(f"  {i:>2}. {pid} · {v:,.0f}")
    print(f"Top 10 igual a la referencia y en el mismo orden: {_marca(ok)}")
    if not ok:
        print("  Revisa el sentido del orden (-1 = descendente) y el desempate por id_proceso ascendente.")
    return ids


# ── E3 ────────────────────────────────────────────────────────────────────────
def pipeline_e3(texto):
    R, pareja = _R(), ESTADO["pareja"]
    pipeline = X.parse_consulta(texto)
    a = V.analizar_pipeline(pipeline)
    print(f"Etapas: {a['etapas']}")
    print(f"$match con los dos filtros: {_marca(a['match_ok'])} · $sort valor DESC + id ASC: {_marca(a['sort_ok'])} · "
          f"$limit ≤ {C.BANDEJA_MAX}: {_marca(a['limit_ok'])}")
    filas = X.ejecutar_pipeline(_coleccion(), pipeline)
    X.escribir_json(R["E3"] / "03_pipeline_bandeja.json", {"nombre_guardado": C.nombre_pipeline(pareja),
                                                            "texto": X.limpiar_texto_pegado(texto), "pipeline": pipeline})
    ids = [f.get("id_proceso") for f in filas]
    X.escribir_json(R["E3"] / "03_resultado_atlas.json", {"capturado_por": "pymongo", "ids": ids, "filas": filas,
                                                           "momento_utc": X.ahora_utc()})
    df = pd.DataFrame(filas)
    faltan = [c for c in C.COLUMNAS_BANDEJA if c not in df.columns]
    if faltan:
        print(f"✗ Tu $project no produce estas columnas: {faltan}. Usa los nombres exactos de la tabla de E3.")
    else:
        df[C.COLUMNAS_BANDEJA].to_csv(R["E3"] / "03_bandeja_historica.csv", index=False)
        print(f"✓ E3/03_bandeja_historica.csv con {len(df)} filas")
    ref = [f["id_proceso"] for f in S.ref_bandeja(_docs())]
    print(f"Mismo resultado y orden que la referencia: {_marca(ids == ref)}")
    return df


# ── E4 ────────────────────────────────────────────────────────────────────────
def _bandeja():
    propia = V.bandeja_propia(ESTADO["out"])
    if propia:
        return propia, False
    return S.ref_bandeja(_docs()), True


def cql_e4(particion, clustering, tipo_valor, keyspace):
    for valor, lista in ((particion, C.OPCIONES_PARTICION), (clustering, C.OPCIONES_CLUSTERING),
                         (tipo_valor, C.OPCIONES_TIPO_VALOR)):
        if valor not in lista:
            raise ValueError("Elige una opción en cada lista desplegable.")
    R, pareja = _R(), ESTADO["pareja"]
    bandeja, rescate = _bandeja()
    if rescate:
        print("ℹ Usando la bandeja de referencia porque E3 no está completa (pierdes los puntos de E3, no los de E4).")
    datos = S.datos_cassandra(bandeja)
    part = S.particion_prueba(datos)
    diseno = {"particion": particion, "clustering": clustering, "tipo_valor": tipo_valor}
    cql = S.generar_cql(diseno, datos, keyspace.strip() or C.KEYSPACE_DEFECTO, C.tabla_cassandra(pareja), part)
    R["E4"].mkdir(parents=True, exist_ok=True)
    datos.to_csv(R["E4"] / "04_datos_cassandra.csv", index=False)
    (R["E4"] / "04_modelo_cassandra.cql").write_text(cql["script"], encoding="utf-8")
    X.escribir_json(R["E4"] / "04_cassandra_evidence.json", {"diseno": diseno, "keyspace": keyspace, "tabla": C.tabla_cassandra(pareja),
                                                             "anio": part[0], "departamento": part[1]})
    ESTADO.update({"cql": cql, "particion": part, "diseno": diseno})
    print(f"PRIMARY KEY ({cql['primary_key']}) · valor_contratos {tipo_valor}")
    print(f"Partición de prueba: anio = {part[0]} · departamento = '{part[1]}' ({len(datos)} filas en total para cargar)")
    for aviso in S.consecuencia_diseno(diseno):
        print("⚠ Qué pasará en Astra:", aviso)
    print("Script guardado en E4/04_modelo_cassandra.cql. Pégalo en CQL Console por bloques:")
    return cql


def bloques_cql(tamano=40):
    cql = ESTADO["cql"]
    bloques = ["\n".join([cql["script"].splitlines()[0], cql["create"]])]
    for i in range(0, len(cql["inserts"]), tamano):
        bloques.append("\n".join(cql["inserts"][i:i + tamano]))
    bloques.append(cql["select_count"] + "\n" + cql["select_top"])
    for i, b in enumerate(bloques, 1):
        print(f"──────── BLOQUE {i} de {len(bloques)} ────────")
        print(b)
    return bloques


def astra_e4(salida):
    R = _R()
    ev = X.leer_json(R["E4"] / "04_cassandra_evidence.json", {}) or {}
    leido = X.evidencia_astra(salida)
    X.escribir_json(R["E4"] / "04_cassandra_evidence.json", {**ev, "salida_consola": salida, **leido,
                                                             "momento_utc": X.ahora_utc()})
    datos = S.datos_cassandra(_bandeja()[0])
    ref = S.ref_cassandra(datos, S.particion_prueba(datos))
    print(f"COUNT leído de tu salida: {leido['count']} · esperado para la partición: {ref['count']} → {_marca(leido['count'] == ref['count'])}")
    print(f"Top 10 leído: {len(leido['top10_ids'])} IDs · igual a la referencia y en orden: {_marca(leido['top10_ids'] == ref['top10_ids'])}")
    if leido["errores"]:
        print("Astra respondió con error:", leido["errores"][0][:200])
        print("Esa es la consecuencia de tu diseño: vuelve a la celda de decisiones, cámbialo y repite.")
    if not S.diseno_correcto(ESTADO.get("diseno") or ev.get("diseno") or {}):
        for aviso in S.consecuencia_diseno(ESTADO.get("diseno") or ev.get("diseno")):
            print("✗", aviso)
    return leido


# ── E5 ────────────────────────────────────────────────────────────────────────
def conectar_aura_e5():
    driver = X.conectar_aura()
    ESTADO["aura"] = driver
    print("✓ Conectado a tu instancia de Aura.")
    return driver


def cargar_e5():
    R, pareja = _R(), ESTADO["pareja"]
    if "aura" not in ESTADO:
        raise RuntimeError("Ejecuta la celda de conexión a Aura: Colab pudo reiniciarse.")
    _, contratos = _raw()
    rel = S.relaciones_grafo(contratos)
    R["E5"].mkdir(parents=True, exist_ok=True)
    rel.to_csv(R["E5"] / "05_relaciones_grafo.csv", index=False)
    filas = rel.to_dict("records")
    t0 = time.perf_counter()
    X.cargar_grafo(ESTADO["aura"], filas, pareja)
    primera = X.conteos_aura(ESTADO["aura"], rel["id_contrato"].tolist())
    X.cargar_grafo(ESTADO["aura"], filas, pareja)
    segunda = X.conteos_aura(ESTADO["aura"], rel["id_contrato"].tolist())
    ESTADO["rel"] = rel
    ev = {"capturado_por": "neo4j-driver", "conteos": segunda, "conteos_primera_carga": primera, "momento_utc": X.ahora_utc()}
    X.escribir_json(R["E5"] / "05_neo4j_evidence.json", ev)
    print(f"Carga en {time.perf_counter() - t0:.1f} s · {len(filas):,} contratos con empresas")
    print(f"En Aura: {segunda['entidades']:,} entidades · {segunda['contratos']:,} contratos · {segunda['proveedores']:,} proveedores")
    print(f"Segunda carga igual a la primera (MERGE no duplica): {_marca(primera == segunda)}")
    return segunda


def ancla_e5():
    R = _R()
    filas = X.ejecutar_lectura(ESTADO["aura"], S.CYPHER_ANCLA)
    if not filas:
        raise RuntimeError("Aura no devolvió entidades: revisa que la carga terminó.")
    nit = str(filas[0]["nit"])
    rel = ESTADO.get("rel")
    if rel is None:
        rel = S.relaciones_grafo(_raw()[1])
    nombres = rel.loc[rel["nit_entidad"] == nit, "entidad"].nunique()
    ev = X.leer_json(R["E5"] / "05_neo4j_evidence.json", {}) or {}
    X.escribir_json(R["E5"] / "05_neo4j_evidence.json", {**ev, "ancla_aura": filas, "nit_ancla": nit, "nombres_bajo_nit": int(nombres)})
    ESTADO["nit_ancla"] = nit
    for f in filas:
        print(f"  {f['nit']} · {f['entidad'][:60]} · {f['proveedores_compartidos']} proveedores compartidos · {f['contratos']} contratos")
    print(f"Tu entidad ancla: NIT {nit}. Bajo ese NIT aparecen {nombres} nombres distintos en tus contratos.")
    contexto = X.ejecutar_lectura(ESTADO["aura"], S.CYPHER_CONTEXTO, {"nit_ancla": nit})
    _guardar_e5(contexto=contexto)
    print("Consulta de contexto para pegar en Aura Query:\n")
    print(S.cypher_para_aura(S.CYPHER_CONTEXTO, nit))
    return nit


def _guardar_e5(**partes):
    R = _R()
    ev = {**(X.leer_json(R["E5"] / "05_neo4j_evidence.json", {}) or {}), **partes}
    X.escribir_json(R["E5"] / "05_neo4j_evidence.json", ev)
    return ev


def preparar_consulta_e5(nombre, consulta):
    if "____" in consulta:
        raise ValueError("Todavía queda el hueco ____: complétalo antes de ejecutar la celda.")
    if not X.es_solo_lectura(consulta):
        raise ValueError("Esta consulta debe ser de lectura (sin CREATE, MERGE, SET ni DELETE).")
    ESTADO.setdefault("consultas", {})[nombre] = consulta
    if set(ESTADO["consultas"]) == {"compartidos", "ranking"}:
        _escribir_cypher(ESTADO["consultas"])
        print("Archivo Cypher guardado: E5/05_neo4j_consultas.cypher")
    print(f"Versión para pegar en Aura Query ({nombre}):\n")
    print(S.cypher_para_aura(consulta, ESTADO["nit_ancla"]))


def _escribir_cypher(consultas):
    '''El artefacto reproducible de E5: no depende de que Aura responda.'''
    R = _R()
    R["E5"].mkdir(parents=True, exist_ok=True)
    secciones = [("restricciones", ";\n".join(S.CYPHER_RESTRICCIONES) + ";"), ("carga", S.CYPHER_CARGA + ";"),
                 ("ancla", S.CYPHER_ANCLA + ";"), ("contexto", S.CYPHER_CONTEXTO + ";"),
                 ("compartidos", consultas["compartidos"].strip().rstrip(";") + ";"),
                 ("ranking", consultas["ranking"].strip().rstrip(";") + ";")]
    (R["E5"] / "05_neo4j_consultas.cypher").write_text(
        "\n\n".join(f"// --- {n} ---\n{q}" for n, q in secciones) + "\n", encoding="utf-8")


def capturar_e5():
    R, nit = _R(), ESTADO["nit_ancla"]
    consultas = ESTADO.get("consultas", {})
    if set(consultas) != {"compartidos", "ranking"}:
        raise RuntimeError("Prepara primero las dos consultas (compartidos y ranking).")
    compartidos = X.ejecutar_lectura(ESTADO["aura"], consultas["compartidos"], {"nit_ancla": nit})
    ranking = X.ejecutar_lectura(ESTADO["aura"], consultas["ranking"], {"nit_ancla": nit})
    top = ranking[0] if ranking else {}
    _guardar_e5(compartidos=compartidos, ranking=ranking, proveedor_top=top.get("nit_proveedor"),
                contratos_con_ancla=top.get("contratos_con_ancla"), entidades_conectadas=top.get("entidades_conectadas"),
                consultas=consultas)
    pd.DataFrame(ranking, columns=["nit_proveedor", "proveedor", "contratos_con_ancla", "entidades_conectadas"]).to_csv(
        R["E5"] / "05_resultado_relacional.csv", index=False)
    _escribir_cypher(consultas)
    print(f"Proveedores compartidos con la ancla: {len(compartidos)}")
    for r in ranking[:10]:
        print(f"  {r['nit_proveedor']} · {str(r.get('proveedor'))[:45]} · contratos con la ancla {r['contratos_con_ancla']} · "
              f"entidades conectadas {r['entidades_conectadas']}")
    print("Guardado: E5/05_neo4j_consultas.cypher, E5/05_resultado_relacional.csv, E5/05_neo4j_evidence.json")
    return ranking


# ── E6 ────────────────────────────────────────────────────────────────────────
def decisiones_e6(decision_429, segundos, indice, posicion, valor_millones, dato_faltante):
    for v in (decision_429, indice, dato_faltante):
        if v == C.SIN_SELECCION:
            raise ValueError("Elige una opción en cada lista: aquí no se escribe, se decide.")
    R = _R()
    bench = X.leer_json(R["E1"] / "01_benchmark_threads.json", {}) or {}
    bandeja = _bandeja()[0]
    k = int(posicion)
    proceso = bandeja[k - 1] if 1 <= k <= len(bandeja) else {}
    log = {"decisiones": [
        {"tema": "concurrencia_429", "seleccion": decision_429, "segundos_declarados": float(segundos),
         "evidencia": {"workers": bench.get("workers"), "mismo_hash": bench.get("mismo_hash")}},
        {"tema": "indice_atlas", "seleccion": indice, "evidencia": {"indices": [ix.get("nombre") for ix in _evidencia_atlas().get("indices", [])]}},
        {"tema": "limite_bandeja", "posicion": k, "id_proceso": proceso.get("id_proceso"), "valor_millones": int(valor_millones),
         "dato_faltante": dato_faltante},
    ]}
    X.escribir_json(R["E6"] / "06_decision_log.json", log)
    (R["E6"] / "06_informe_tecnico.md").write_text(_informe(), encoding="utf-8")
    print("Decisiones guardadas en E6/06_decision_log.json · informe generado en E6/06_informe_tecnico.md")
    print(f"Elegiste la posición {k} de tu bandeja: {proceso.get('id_proceso')}")
    return log


def microdefensa_e6(rango, causa, limite_red, entidades_puente):
    for v in (rango, causa, limite_red):
        if v == C.SIN_SELECCION:
            raise ValueError("Elige una opción en cada lista: aquí no se escribe, se decide.")
    X.escribir_json(_R()["E6"] / "06_microdefensa_grupal.json", {
        "cobertura": {"rango": rango, "causa": causa},
        "red": {"limite": limite_red, "entidades_puente": int(entidades_puente)}})
    print("Microdefensa guardada en E6/06_microdefensa_grupal.json")


def _informe():
    R = _R()
    cal = X.leer_json(R["E1"] / "01_quality_report.json", {}) or {}
    bench = X.leer_json(R["E1"] / "01_benchmark_threads.json", {}) or {}
    ev2 = _evidencia_atlas()
    ev4 = X.leer_json(R["E4"] / "04_cassandra_evidence.json", {}) or {}
    ev5 = X.leer_json(R["E5"] / "05_neo4j_evidence.json", {}) or {}
    fp, fc = cal.get("fechas_procesos") or [None, None, 0], cal.get("fechas_contratos") or [None, None, 0]
    return f'''# Informe técnico TC1 · {ESTADO['pareja']}

## 1. Adquisición (E1)
Procesos {fp[0]} → {fp[1]} ({fp[2]} día(s)); contratos con empresas {fc[0]} → {fc[1]} ({fc[2]} días).
Workers={bench.get('workers')}; mismo hash secuencial/concurrente={bench.get('mismo_hash')}.

## 2. Modelo documental y Atlas (E2)
Carga: {(ev2.get('carga') or {}).get('estrategia')}; duplicados tras la segunda carga={(ev2.get('carga') or {}).get('duplicates_after_second')}.
Consulta A={(ev2.get('consulta_a') or {}).get('resultado')}.

## 3. Producto analítico (E3)
Bandeja de hasta {C.BANDEJA_MAX} procesos priorizados por valor de contratos.

## 4. Cassandra query-first (E4)
Partición de prueba=({ev4.get('anio')}, {ev4.get('departamento')}); top 10 leído de Astra={len(ev4.get('top10_ids') or [])} IDs.

## 5. Contexto relacional (E5)
Entidad ancla NIT={ev5.get('nit_ancla')} con {ev5.get('nombres_bajo_nit')} nombres bajo el mismo NIT; proveedor puente={ev5.get('proveedor_top')}.

## 6. Límites
Qué NO permite concluir: la bandeja y la red orientan una revisión; no demuestran sobrecosto, fraude, colusión ni causalidad.
El snapshot cubre solo los primeros días de la ventana y, en contratos, solo personas jurídicas que no son consorcio.
Cobertura del cruce procesos→contratos={round(100 * float(cal.get('join_coverage') or 0), 1)} %.
'''


# ── Validación y entrega ──────────────────────────────────────────────────────
def validar():
    m = V.evaluar(ESTADO["out"])
    print(V.resumen_texto(m))
    guardar_avance()
    return m


def entregar(manifest):
    R, pareja, out = _R(), ESTADO["pareja"], ESTADO["out"]
    if not manifest["gates"]["sin_secretos"]["ok"]:
        raise RuntimeError("Entrega bloqueada: elimina los secretos señalados y vuelve a validar.")
    zip_path = X.empaquetar(out, pareja)
    apellidos = [_sin_tildes(x.get("apellido")) for x in ESTADO.get("integrantes", []) if x.get("apellido")]
    carpeta = "_".join(["TC1_BIGDATA", pareja] + apellidos)
    destino = (Path(ESTADO["drive"]) / carpeta) if ESTADO.get("drive") else (out.parent / carpeta)
    destino.mkdir(parents=True, exist_ok=True)
    nb_path = destino / f"TC1_{pareja}.ipynb"
    if X.EN_COLAB:
        nb = X.notebook_actual()
        hallazgos = V.escanear_secretos(out, notebook=nb)
        if hallazgos:
            raise RuntimeError("Tu notebook tiene un posible secreto en una celda o salida: " + "; ".join(hallazgos[:3]) +
                               ". Bórralo, limpia esa salida (Editar → Borrar resultados) y vuelve a ejecutar esta celda.")
        nb_path.write_text(json.dumps(nb, ensure_ascii=False), encoding="utf-8")
    for origen in (zip_path, R["manifest"]):
        (destino / origen.name).write_bytes(Path(origen).read_bytes())
    huella = X.huella_archivo(destino / C.MANIFEST)
    print(f"Carpeta lista: {destino}")
    for nombre in (nb_path.name, zip_path.name, C.MANIFEST):
        p = destino / nombre
        print(f"  {_marca(p.exists())} {nombre}" + (f" · {p.stat().st_size / 1024:.0f} KB" if p.exists() else
                                                     " · descárgalo con Archivo → Descargar → .ipynb y súbelo a esta carpeta"))
    if ESTADO.get("drive"):
        print(f"Comparte SOLO esta carpeta. {X.carpeta_drive(ESTADO['drive'], pareja).name}/avance es tu copia de trabajo: no la compartas.")
    print(f"\nHUELLA DE ENTREGA (SHA-256 de manifest_tc1.json): {huella}")
    print("Copia esta huella en el correo. Si vuelves a validar, la huella cambia: envía siempre la última.")
    return destino, huella
