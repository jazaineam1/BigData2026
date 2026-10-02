#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Pruebas del TC1 V9 que no necesitan servicios externos (corren en CI).

1. Construye un paquete completo y realista desde los datos reales congelados de P03:
   E1 con el código real contra una API simulada (incluye un HTTP 429), Atlas con mongomock,
   Astra y Aura con las salidas reales de Cassandra y Neo4j grabadas por test_tc1_v9_e2e.py.
2. Exige 100/100 al estudiante y la misma nota en la revalidación docente.
3. Manipula copias del paquete y exige que el docente detecte cada manipulación.
4. Prueba los lectores de lo que se pega desde Atlas, Astra y Aura.
5. Prueba el contrato, el cuaderno generado y los secretos.
'''
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "utils"))
sys.path.insert(0, str(ROOT))

import mongomock  # noqa: E402

import tc1_contrato as C  # noqa: E402
import tc1_cuaderno as T  # noqa: E402
import tc1_secop as S  # noqa: E402
import tc1_servicios as X  # noqa: E402
import tc1_teacher_validator as TV  # noqa: E402
import tc1_validador as V  # noqa: E402
from tc1_pruebas import FIXTURES, png, servidor_socrata  # noqa: E402

FILTRO_A = '{"proceso.precio_base": {"$gt": 0}, "contratos_resumen.cantidad": {"$gt": 0}}'
ORDEN_B = "{contratos_resumen.valor_total: -1, id_proceso: 1}"
PIPELINE = ("result = client['tc1_bigdata']['tc1_p03'].aggregate([\n"
            "  {'$match': {'proceso.precio_base': {'$gt': 0}, 'contratos_resumen.cantidad': {'$gt': 0}}},\n"
            "  {'$project': {'_id': 0, 'id_proceso': 1, 'anio': '$proceso.anio', 'departamento': '$entidad.departamento',"
            " 'entidad': '$entidad.nombre', 'valor_contratos': '$contratos_resumen.valor_total'}},\n"
            "  {'$sort': {'valor_contratos': -1, 'id_proceso': 1}},\n  {'$limit': 100}\n])")
OK, FALLA = [], []


def _bulk_write_compatible(self, requests, ordered=True, **_):
    '''mongomock no acepta el UpdateOne de pymongo 4.9+ (trae sort). Solo para pruebas: contra
    MongoDB real el bulk_write se verificó en test_tc1_v9_e2e.py.'''
    from pymongo import UpdateOne
    for r in requests:
        if not isinstance(r, UpdateOne):
            raise NotImplementedError(type(r).__name__)
        self.update_one(r._filter, r._doc, upsert=r._upsert)


mongomock.collection.Collection.bulk_write = _bulk_write_compatible


def caso(nombre, condicion, detalle=""):
    (OK if condicion else FALLA).append(nombre)
    print(("✓ " if condicion else "✗ ") + nombre + ("" if condicion else f" · {detalle}"))


def construir_paquete(trabajo):
    srv, api = servidor_socrata("P03")
    S.BASE = f"http://127.0.0.1:{srv.server_port}/resource"
    print(f"TC1 {C.VERSION_VISIBLE} listo. Siguiente paso: la celda «0 · Identidad de la pareja».")
    out, _ = T.iniciar("P03", [("Estudiante de prueba", "000000", "Prueba")], "No", base=trabajo)
    T.contrato_e1()
    seq, thr, offsets, _ = T.preflight_e1()
    t0 = time.perf_counter()
    paginas_seq = {o: seq(o) for o in offsets}
    s_seq = time.perf_counter() - t0
    t0 = time.perf_counter()
    paginas_thr = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futuros = {pool.submit(thr, o): o for o in offsets}
        for f in as_completed(futuros):
            paginas_thr[futuros[f]] = f.result()
    s_thr = time.perf_counter() - t0
    bench = T.comparar_e1(paginas_seq, s_seq, paginas_thr, s_thr, 4)
    con, offs_c = T.descargador_contratos()
    T.consolidar_e1({o: con(o) for o in offs_c})
    T.checkpoint("E1")
    T.documentos_e2(C.GRANO_CORRECTO)
    cliente = mongomock.MongoClient()
    T.ESTADO.update({"atlas": cliente, "atlas_version": "mongomock"})
    T.cargar_e2(C.ESTRATEGIA_CORRECTA)
    col = cliente[C.ATLAS_DB][C.coleccion_oficial("P03")]
    col.create_index("id_proceso", unique=True)
    col.create_index([("contratos_resumen.valor_total", -1), ("id_proceso", 1)])
    T.indices_e2()
    T.consulta_a_e2(FILTRO_A)
    T.consulta_b_e2(ORDEN_B)
    T.pipeline_e3(PIPELINE)
    img = Path(trabajo) / "captura.png"
    img.write_bytes(png(1280, 720))
    for etapa in C.CAPTURAS:
        ruta, (ok, motivo) = X.guardar_captura(out, etapa, ruta=img)
        print(("✓ " if ok else "✗ ") + f"{ruta.name}: {motivo}")
    T.checkpoint("E2")
    T.checkpoint("E3")
    T.cql_e4(C.DISENO_CORRECTO["particion"], C.DISENO_CORRECTO["clustering"], "decimal", C.KEYSPACE_DEFECTO)
    T.astra_e4((FIXTURES / "P03_cqlsh_salida.txt").read_text(encoding="utf-8"))
    T.checkpoint("E4")
    R = C.rutas(out)
    for f in (FIXTURES / "P03_E5").iterdir():
        shutil.copyfile(f, R["E5"] / f.name)
    S.relaciones_grafo(T._raw()[1]).to_csv(R["E5"] / "05_relaciones_grafo.csv", index=False)
    import pandas as pd
    bandeja = pd.read_csv(R["E3"] / "03_bandeja_historica.csv", dtype={"id_proceso": str})
    ev5 = json.loads((R["E5"] / "05_neo4j_evidence.json").read_text(encoding="utf-8"))
    cal = json.loads((R["E1"] / "01_quality_report.json").read_text(encoding="utf-8"))
    T.decisiones_e6(C.E6_CORRECTAS["decision_429"], round(bench["segundos_concurrente"]), C.E6_INDICE[1], 3,
                    round(bandeja.loc[2, "valor_contratos"] / 1e6), C.E6_CORRECTAS["dato_faltante"])
    T.microdefensa_e6(C.rango_cobertura(cal["join_coverage"]), C.E6_CORRECTAS["causa_cobertura"],
                      C.E6_CORRECTAS["limite_red"], ev5["entidades_conectadas"])
    manifest = T.validar()
    destino, _ = T.entregar(manifest)
    srv.shutdown()
    return out, manifest, api, destino


def variante(base, nombre, mutar):
    destino = Path(tempfile.mkdtemp(prefix=f"tc1_{nombre}_"))
    shutil.copytree(base, destino / base.name)
    copia = destino / base.name
    mutar(C.rutas(copia), copia)
    return V.evaluar(copia, modo="docente", escribir=False)


def editar_json(path, fn):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    fn(data)
    Path(path).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def puntos(m, item):
    return m["controles"][item]["puntos"]


def main():
    trabajo = Path(tempfile.mkdtemp(prefix="tc1_v9_"))
    import contextlib
    import io

    class Tee(io.StringIO):
        def write(self, s):
            sys.__stdout__.write(s)
            return super().write(s)
    capturado = Tee()
    with contextlib.redirect_stdout(capturado):
        out, m, api, entrega = construir_paquete(trabajo)
    from tc1_pruebas import verificar_evidencias
    html = (ROOT / "assets" / "tutoriales" / "s08-secoppipeline.html").read_text(encoding="utf-8")
    faltan = verificar_evidencias(html, capturado.getvalue(), omitir={"e5a", "e5b", "e5c"})
    caso("cada evidencia del checklist aparece en la salida real (salvo E5, que se prueba con Neo4j)", not faltan, faltan)
    print(f"API simulada: {api['peticiones']} peticiones, 429 inyectados: {api['429_enviados']}")
    caso("paquete completo obtiene 100/100", m["puntaje"] == 100,
         {k: c["evidencia"] for k, c in m["controles"].items() if not c["ok"]})
    caso("tres controles quedan provisionales hasta ver las capturas", m["pendiente_confirmacion_visual"] == ["E2.6", "E4.3", "E5.4"])
    caso("el 429 se resolvió con reintento", api["429_enviados"] == 1 and m["controles"]["E1.3"]["ok"])
    caso("nota registrada con un decimal", m["nota_registrada"] == 5.0 and C.nota_registrada(96) == 4.8 and C.nota_registrada(87.5) == 4.5)

    # Revalidación docente sobre la entrega de tres archivos
    zip_path = entrega / "TC1_P03.zip"
    caso("entregar() deja ZIP y manifest en la carpeta con apellidos", entrega.name == "TC1_BIGDATA_P03_PRUEBA"
         and zip_path.exists() and (entrega / C.MANIFEST).exists())
    (entrega / "TC1_P03.ipynb").write_text(json.dumps({"cells": [{"source": [C.VERSION_VISIBLE]}]}), encoding="utf-8")
    huella = hashlib.sha256((entrega / C.MANIFEST).read_bytes()).hexdigest()
    r = TV.revisar(entrega, huella, {"E2": True, "E4": True, "E5": True})
    caso("docente recalcula 100 y coincide con el manifest", r["docente"]["puntaje"] == 100 and not r["diferencias"] and not r["avisos"], r["avisos"])
    r = TV.revisar(entrega, "0" * 64, {"E2": True, "E4": False, "E5": None})
    caso("docente detecta huella del correo distinta", any("huella" in a for a in r["avisos"]))
    caso("captura rechazada por el docente baja E4.3 a 2", puntos(r["docente"], "E4.3") == 2)
    caso("captura sin revisar queda pendiente", r["docente"]["pendiente_confirmacion_visual"] == ["E5.4"])
    editar_json(entrega / C.MANIFEST, lambda d: d.update(puntaje=100))
    externo = json.loads((entrega / C.MANIFEST).read_text(encoding="utf-8"))
    externo["controles"]["E2.4"]["puntos"] = 3
    (entrega / C.MANIFEST).write_text(json.dumps(externo), encoding="utf-8")
    r = TV.revisar(entrega, None, {})
    caso("docente detecta manifest externo editado", any("NO es idéntico" in a for a in r["avisos"]))
    caso("el ZIP no contiene archivos de credenciales", not any(X.prohibido(n.split("/")[-1]) for n in __import__("zipfile").ZipFile(zip_path).namelist()))

    # Manipulaciones y errores que el validador debe detectar
    m2 = variante(out, "part", lambda R, o: (R["pag_thr"] / "page_0000000.json.part").write_text("x"))
    caso(".part en el caché invalida E1", puntos(m2, "E1.3") == 0 and puntos(m2, "E1.4") == 0)
    m2 = variante(out, "extra", lambda R, o: (R["pag_seq"] / "page_0999999.json").write_text("[]"))
    caso("chunk extra invalida la descarga secuencial", puntos(m2, "E1.2") == 0)

    def alterar_pagina(R, o):
        p = R["pag_thr"] / "page_0000250.json"
        filas = json.loads(p.read_text(encoding="utf-8"))
        filas[0]["precio_base"] = "1"
        p.write_text(json.dumps(filas, ensure_ascii=False, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    m2 = variante(out, "pagina", alterar_pagina)
    caso("página RAW alterada invalida E1 (SHA-256)", puntos(m2, "E1.3") == 0)

    m2 = variante(out, "pareja", lambda R, o: editar_json(R["identidad"], lambda d: d.update(pareja="P04")))
    caso("cambiar PAREJA_ID no hereda el RAW de otra ventana", puntos(m2, "E1.1") == 0)

    def duplicar(R, o):
        editar_json(R["E2"] / "02_modelo_documental.json", lambda d: d["documentos"].append(dict(d["documentos"][0])))
    m2 = variante(out, "duplicado", duplicar)
    caso("documento duplicado invalida el modelo", puntos(m2, "E2.1") == 0)

    m2 = variante(out, "conteo", lambda R, o: editar_json(R["E2"] / "02_atlas_evidence.json",
                                                         lambda d: d["consulta_a"].update(resultado=d["consulta_a"]["resultado"] + 1)))
    caso("conteo A editado se detecta", puntos(m2, "E2.4") == 0)
    m2 = variante(out, "insert", lambda R, o: editar_json(R["E2"] / "02_atlas_evidence.json",
                                                         lambda d: d["carga"].update(estrategia=C.ESTRATEGIAS_CARGA[0])))
    caso("estrategia no idempotente no da E2.2", puntos(m2, "E2.2") == 0)

    def orden_sin_desempate(R, o):
        editar_json(R["E3"] / "03_pipeline_bandeja.json", lambda d: d["pipeline"][2].update({"$sort": {"valor_contratos": -1}}))
    m2 = variante(out, "sort", orden_sin_desempate)
    caso("pipeline sin desempate pierde E3.1", puntos(m2, "E3.1") == 0)

    def cql_filtering(R, o):
        p = R["E4"] / "04_modelo_cassandra.cql"
        p.write_text(p.read_text(encoding="utf-8").replace("LIMIT 10;", "LIMIT 10 ALLOW FILTERING;"), encoding="utf-8")
    m2 = variante(out, "filtering", cql_filtering)
    caso("ALLOW FILTERING invalida el modelo Cassandra", puntos(m2, "E4.2") == 0)

    def astra_sin_id(R, o):
        def f(d):
            d["salida_consola"] = d["salida_consola"].replace("    22", "    21")
        editar_json(R["E4"] / "04_cassandra_evidence.json", f)
    m2 = variante(out, "count", astra_sin_id)
    caso("COUNT menor (empates sobrescritos) pierde E4.1", puntos(m2, "E4.1") == 0)
    m2 = variante(out, "sincaptura", lambda R, o: (R["E4"] / C.CAPTURAS["E4"]).unlink())
    caso("sin captura E4.3 baja a 2 aunque el top 10 sea correcto", puntos(m2, "E4.3") == 2)

    def cypher_sin_distinct(R, o):
        p = R["E5"] / "05_neo4j_consultas.cypher"
        p.write_text(p.read_text(encoding="utf-8").replace("count(DISTINCT otra)", "count(otra)"), encoding="utf-8")
    m2 = variante(out, "cypher", cypher_sin_distinct)
    caso("ranking sin DISTINCT pierde E5.3", puntos(m2, "E5.3") == 0)
    m2 = variante(out, "ancla", lambda R, o: editar_json(R["E5"] / "05_neo4j_evidence.json", lambda d: d.update(nit_ancla="000")))
    caso("ancla equivocada pierde E5.1", puntos(m2, "E5.1") == 0)

    m2 = variante(out, "secreto", lambda R, o: editar_json(R["E2"] / "02_atlas_evidence.json",
                                                          lambda d: d.update(nota="mongodb+srv://ana:Clave2026x@c0.example.mongodb.net/")))
    caso("URI de Atlas con contraseña bloquea la entrega", not m2["gates"]["sin_secretos"]["ok"] and puntos(m2, "E6.3") == 0)
    m2 = variante(out, "astra_token", lambda R, o: (R["E4"] / "notas.txt").write_text("AstraCS:abcdefGHIJ:" + "0f" * 32))
    caso("token de Astra bloquea la entrega", not m2["gates"]["sin_secretos"]["ok"])
    m2 = variante(out, "credenciales", lambda R, o: (R["E5"] / "Neo4j-abc123-Created-2026-10-01.txt").write_text("NEO4J_URI=x"))
    caso("archivo de credenciales de Aura bloquea la entrega", not m2["gates"]["sin_secretos"]["ok"])
    m2 = variante(out, "e6", lambda R, o: editar_json(R["E6"] / "06_decision_log.json",
                                                     lambda d: d["decisiones"][2].update(valor_millones=d["decisiones"][2]["valor_millones"] + 50)))
    caso("decisión con un valor que no es el propio pierde puntos", puntos(m2, "E6.1") == 3)

    # Lectores de lo que el estudiante pega
    caso("lee JSON estricto", X.parse_consulta(FILTRO_A) == json.loads(FILTRO_A))
    caso("lee sintaxis de shell", X.parse_consulta(ORDEN_B) == {"contratos_resumen.valor_total": -1, "id_proceso": 1})
    caso("lee Export Code con .aggregate(...)", len(X.parse_consulta(PIPELINE)) == 4)
    caso("lee el pipeline del modo Texto", len(X.parse_consulta("[{\"$match\": {}}, {\"$limit\": 5}]")) == 2)
    caso("no guarda la línea de conexión pegada", "mongodb" not in X.limpiar_texto_pegado("client = MongoClient('mongodb+srv://u:p@h/')\n[1]"))
    salida = (FIXTURES / "P03_cqlsh_salida.txt").read_text(encoding="utf-8")
    leido = X.evidencia_astra(salida)
    caso("lee la salida real de cqlsh", leido["count"] == 22 and len(leido["top10_ids"]) == 10)
    error = "/tmp/x.cql:113:InvalidRequest: Error from server: code=2200 [Invalid query] message=\"Cannot execute this query\""
    caso("reconoce el error de Cassandra", X.evidencia_astra(error)["errores"])
    correcto = V.analizar_cql(S.generar_cql({**C.DISENO_CORRECTO, "tipo_valor": "decimal"},
                                            S.datos_cassandra(S.ref_bandeja(T._docs())), "ks", "t", (2025, "X"))["script"])
    caso("analiza la PRIMARY KEY correcta", correcto["particion"] == ["anio", "departamento"] and correcto["clustering"] == ["valor_contratos", "id_proceso"])
    mal = V.analizar_cql("CREATE TABLE ks.t (anio int, departamento text, valor_contratos text, id_proceso text, "
                         "PRIMARY KEY (departamento, valor_contratos)) WITH CLUSTERING ORDER BY (valor_contratos DESC);")
    caso("analiza una clave mal diseñada", mal["particion"] == ["departamento"] and mal["tipo_valor"] == "text")
    caso("rechaza consultas Cypher de escritura", not X.es_solo_lectura("MATCH (n) DETACH DELETE n") and X.es_solo_lectura(S.CYPHER_ANCLA))

    # Contrato y cuaderno
    caso("rúbrica 25/25/10/15/15/10 = 100", C.puntos_totales() == 100 and list(C.STAGE_MAX.values()) == [25, 25, 10, 15, 15, 10])
    caso("ventanas únicas por pareja", len(set(C.VENTANAS.values())) == len(C.VENTANAS) == 12)
    caso("exactamente tres capturas", list(C.CAPTURAS.values()) == ["E2_atlas.png", "E4_astra.png", "E5_neo4j.png"])
    import build_taller_control_1 as B
    nb_txt = (ROOT / "Cuadernos" / "Taller_Control_1.ipynb").read_bytes().decode("utf-8")
    caso("el cuaderno versionado es el del generador", nb_txt == B.serializar(B.notebook()))
    nb = json.loads(nb_txt)
    fuentes = ["".join(c["source"]) for c in nb["cells"]]
    todo = "\n".join(fuentes)
    caso("sin salidas preejecutadas", not any(c.get("outputs") for c in nb["cells"] if c["cell_type"] == "code"))
    caso("sin App Token, NetworkX ni Cassandra simulada", not any(x in todo for x in ("APP_TOKEN", "X-App-Token", "networkx", "consulta_cassandra_simulada")))
    caso("el primer bloque enlaza el checklist", C.CHECKLIST_URL in fuentes[1])
    caso("seis fichas de etapa con los ocho rótulos", all(todo.count(f"| **{r}** |") == 6 for r in
                                                          ("Objetivo", "Pregunta", "Dónde trabajas", "Ya está provisto", "Tú haces",
                                                           "Checkpoint para avanzar", "Evidencia que queda", "Puntos")))
    lecturas = [f for f in fuentes if f.startswith("**Cómo se lee.**")]
    caso("cada lectura usa los cuatro rótulos en orden", len(lecturas) >= 8 and all(
        f.index("Cómo se lee") < f.index("Qué nos dice") < f.index("Qué NO permite concluir todavía") < f.index("Qué error común") for f in lecturas))
    listas = [l for f in fuentes for l in f.splitlines() if "#@param [" in l and not l.startswith("GUARDAR_AVANCE")]
    caso("ninguna lista trae una opción preseleccionada", len(listas) == 12 and all(f'= "{C.SIN_SELECCION}" #@param' in l for l in listas))
    codigo = "\n".join(f for f, c in zip(fuentes, nb["cells"]) if c["cell_type"] == "code")
    caso("tres huecos de código (E1 y dos en E5)", codigo.count("____") == 3)
    caso("el cuaderno no contiene secretos", not V.escanear_secretos(trabajo / "vacio", notebook=nb))
    caso("los módulos no contienen secretos", not [p for p in (ROOT / "utils").glob("tc1_*.py") for _, pat in C.PATRONES_SECRETOS
                                                   if __import__("re").search(pat, p.read_text(encoding="utf-8"))])

    shutil.rmtree(trabajo, ignore_errors=True)
    print(f"\n{len(OK)} casos OK · {len(FALLA)} fallas")
    if FALLA:
        print("FALLAN:", FALLA)
        sys.exit(1)
    print("TC1 V9: OK")


if __name__ == "__main__":
    main()
