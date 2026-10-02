#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Prueba de punta a punta del TC1 V9: ejecuta el cuaderno real, celda por celda.

- API SECOP: servidor local que sirve los datos reales congelados de una pareja
  (tests/fixtures/tc1) e inyecta un HTTP 429 para ejercitar los reintentos.
- Atlas, Astra y Aura: MongoDB, Cassandra y Neo4j reales en Docker. Las interfaces web
  (Data Explorer, CQL Console, Aura Query) no se pueden automatizar: la prueba crea los
  índices como lo haría el estudiante en Atlas, ejecuta el script CQL con cqlsh (el mismo
  motor de CQL Console) y pega su salida en la celda, como haría el estudiante.
- Responde como un solucionario: completa los huecos y elige las opciones correctas.

Requisitos: Docker con los contenedores tc1-mongo, tc1-cassandra (keyspace compras_claras)
y tc1-neo4j; variable TC1_NEO4J_CLAVE con la contraseña local de Neo4j.

Uso:
    python utils/test_tc1_v9_e2e.py --trabajo <carpeta temporal> [--guardar <notebook ejecutado>]
'''
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "utils"))
import tc1_contrato as C  # noqa: E402
from tc1_pruebas import png, servidor_socrata  # noqa: E402

PAREJA = "P03"


def reemplazar(src, patron, valor):
    nuevo, n = re.subn(patron, valor, src, count=1, flags=re.M)
    assert n == 1, f"no encontré {patron!r}"
    return nuevo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trabajo", required=True)
    ap.add_argument("--guardar")
    a = ap.parse_args()
    trabajo = Path(a.trabajo)
    trabajo.mkdir(parents=True, exist_ok=True)
    srv, est_api = servidor_socrata(PAREJA)
    os.environ["TC1_SOCRATA_BASE"] = f"http://127.0.0.1:{srv.server_port}/resource"
    capturas = trabajo / "capturas"
    capturas.mkdir(exist_ok=True)
    for e in C.CAPTURAS:
        (capturas / f"{e}.png").write_bytes(png(1280, 720))

    nb = nbformat.read(ROOT / "Cuadernos" / "Taller_Control_1.ipynb", as_version=4)
    out = trabajo / f"tc1_{PAREJA}"
    clave_neo4j = os.environ["TC1_NEO4J_CLAVE"]
    respuestas_getpass = []

    def preparar(src):
        if src.startswith("#@title 0 · Identidad"):
            src = reemplazar(src, r'^PAREJA_ID = ".*?"', f'PAREJA_ID = "{PAREJA}"')
            src = reemplazar(src, r'^INTEGRANTE_1 = ""', 'INTEGRANTE_1 = "Estudiante de prueba"')
            src = reemplazar(src, r'^CODIGO_1 = ""', 'CODIGO_1 = "000000"')
            src = reemplazar(src, r'^APELLIDO_1 = ""', 'APELLIDO_1 = "Prueba"')
            src = reemplazar(src, r'^GUARDAR_AVANCE_EN_DRIVE = ".*?"', 'GUARDAR_AVANCE_EN_DRIVE = "No"')
            src = src.replace("GUARDAR_AVANCE_EN_DRIVE)", f"GUARDAR_AVANCE_EN_DRIVE, base={str(trabajo)!r})")
        elif "pool.submit(descargar_pagina, ____)" in src:
            src = src.replace("pool.submit(descargar_pagina, ____)", "pool.submit(descargar_pagina, offset)")
        elif src.startswith("#@title E2.1"):
            src = reemplazar(src, r'^GRANO = ".*?"', f"GRANO = {json.dumps(C.GRANO_CORRECTO, ensure_ascii=False)}")
        elif src.startswith("#@title E2.2a"):
            respuestas_getpass[:] = ["mongodb://localhost:27017"]
        elif src.startswith("#@title E2.2b"):
            src = reemplazar(src, r'^ESTRATEGIA = ".*?"', f"ESTRATEGIA = {json.dumps(C.ESTRATEGIA_CORRECTA, ensure_ascii=False)}")
        elif src.startswith("#@title E2.3"):
            from pymongo import MongoClient
            col = MongoClient("mongodb://localhost:27017")[C.ATLAS_DB][C.coleccion_oficial(PAREJA)]
            col.create_index("id_proceso", unique=True)
            col.create_index([("contratos_resumen.valor_total", -1), ("id_proceso", 1)])
        elif src.startswith("# E2.4"):
            src = src.replace("pega aquí tu filtro", '{"proceso.precio_base": {"$gt": 0}, "contratos_resumen.cantidad": {"$gt": 0}}')
        elif src.startswith("# E2.5"):
            src = src.replace("pega aquí tu sort", "{contratos_resumen.valor_total: -1, id_proceso: 1}")
        elif src.startswith("# E3 · Pega"):
            export = ("# Requires the PyMongo package.\nclient = MongoClient('mongodb+srv://<db_username>:<db_password>@x.mongodb.net/')\n"
                      "result = client['tc1_bigdata']['tc1_p03'].aggregate([\n"
                      "    {'$match': {'proceso.precio_base': {'$gt': 0}, 'contratos_resumen.cantidad': {'$gt': 0}}},\n"
                      "    {'$project': {'_id': 0, 'id_proceso': 1, 'anio': '$proceso.anio', 'departamento': '$entidad.departamento', "
                      "'entidad': '$entidad.nombre', 'valor_contratos': '$contratos_resumen.valor_total'}},\n"
                      "    {'$sort': {'valor_contratos': -1, 'id_proceso': 1}},\n    {'$limit': 100}\n])")
            src = src.replace("pega aquí tu pipeline", export.replace("'''", ""))
        elif "guardar_captura(OUT, " in src:
            etapa = re.search(r'guardar_captura\(OUT, "(E\d)"\)', src).group(1)
            src = src.replace(f'guardar_captura(OUT, "{etapa}")', f'guardar_captura(OUT, "{etapa}", ruta={str(capturas / (etapa + ".png"))!r})')
        elif src.startswith("#@title E4.1"):
            src = reemplazar(src, r'^PARTICION = ".*?"', f'PARTICION = "{C.DISENO_CORRECTO["particion"]}"')
            src = reemplazar(src, r'^CLUSTERING = ".*?"', f'CLUSTERING = "{C.DISENO_CORRECTO["clustering"]}"')
            src = reemplazar(src, r'^TIPO_VALOR = ".*?"', 'TIPO_VALOR = "decimal"')
        elif src.startswith("# E4.2"):
            script = out / "E4" / "04_modelo_cassandra.cql"
            subprocess.run(["docker", "cp", str(script), "tc1-cassandra:/tmp/tc1.cql"], check=True)
            salida = subprocess.run(["docker", "exec", "tc1-cassandra", "cqlsh", "-f", "/tmp/tc1.cql"],
                                    capture_output=True, text=True, encoding="utf-8").stdout
            (trabajo / "salida_cqlsh.txt").write_text(salida, encoding="utf-8")
            src = src.replace("pega aquí la salida de Astra", salida.replace("'''", ""))
        elif src.startswith("#@title E5.1"):
            respuestas_getpass[:] = ["bolt://localhost:7687", "neo4j", clave_neo4j]
        elif src.startswith("# E5.3a"):
            src = src.replace("WHERE ____", "WHERE otra <> a")
        elif src.startswith("# E5.3b"):
            src = src.replace("____ AS entidades_conectadas", "count(DISTINCT otra) AS entidades_conectadas")
        elif src.startswith("#@title E6.1"):
            bench = json.loads((out / "E1" / "01_benchmark_threads.json").read_text(encoding="utf-8"))
            import pandas as pd
            bandeja = pd.read_csv(out / "E3" / "03_bandeja_historica.csv", dtype={"id_proceso": str})
            src = reemplazar(src, r'^DECISION_429 = ".*?"', f"DECISION_429 = {json.dumps(C.E6_CORRECTAS['decision_429'], ensure_ascii=False)}")
            src = reemplazar(src, r'^SEGUNDOS_DESCARGA_CONCURRENTE = 0', f"SEGUNDOS_DESCARGA_CONCURRENTE = {round(bench['segundos_concurrente'])}")
            src = reemplazar(src, r'^INDICE_ADICIONAL = ".*?"', f"INDICE_ADICIONAL = {json.dumps(C.E6_INDICE[1], ensure_ascii=False)}")
            src = reemplazar(src, r'^POSICION_EN_TU_BANDEJA = 1', "POSICION_EN_TU_BANDEJA = 3")
            src = reemplazar(src, r'^VALOR_EN_MILLONES = 0', f"VALOR_EN_MILLONES = {round(bandeja.loc[2, 'valor_contratos'] / 1e6)}")
            src = reemplazar(src, r'^DATO_QUE_FALTA = ".*?"', f"DATO_QUE_FALTA = {json.dumps(C.E6_CORRECTAS['dato_faltante'], ensure_ascii=False)}")
        elif src.startswith("#@title E6.2"):
            cal = json.loads((out / "E1" / "01_quality_report.json").read_text(encoding="utf-8"))
            ev5 = json.loads((out / "E5" / "05_neo4j_evidence.json").read_text(encoding="utf-8"))
            src = reemplazar(src, r'^RANGO_DE_TU_COBERTURA = ".*?"', f"RANGO_DE_TU_COBERTURA = {json.dumps(C.rango_cobertura(cal['join_coverage']), ensure_ascii=False)}")
            src = reemplazar(src, r'^QUE_EXPLICA_TU_COBERTURA = ".*?"', f"QUE_EXPLICA_TU_COBERTURA = {json.dumps(C.E6_CORRECTAS['causa_cobertura'], ensure_ascii=False)}")
            src = reemplazar(src, r'^QUE_NO_PERMITE_CONCLUIR_LA_RED = ".*?"', f"QUE_NO_PERMITE_CONCLUIR_LA_RED = {json.dumps(C.E6_CORRECTAS['limite_red'], ensure_ascii=False)}")
            src = reemplazar(src, r'^ENTIDADES_DE_TU_PROVEEDOR_PUENTE = 0', f"ENTIDADES_DE_TU_PROVEEDOR_PUENTE = {ev5['entidades_conectadas']}")
        return src

    client = NotebookClient(nb, timeout=900, kernel_name="python3", resources={"metadata": {"path": str(trabajo)}})
    tiempos = []
    with client.setup_kernel():
        for i, cell in enumerate(nb.cells):
            if cell.cell_type != "code":
                continue
            cell.source = preparar(cell.source)
            if respuestas_getpass:
                inyeccion = nbformat.v4.new_code_cell(
                    "import getpass as _gp, tc1_servicios as _X\n"
                    f"_resp = iter({respuestas_getpass!r})\n"
                    "_X.getpass = lambda prompt='': next(_resp)")
                client.execute_cell(inyeccion, -1)
                respuestas_getpass.clear()
            import time
            t0 = time.perf_counter()
            try:
                client.execute_cell(cell, i)
            except CellExecutionError as exc:
                limpio = re.sub(r"\x1b\[[0-9;]*m", "", str(exc))
                ultima = [ln for ln in limpio.splitlines() if ln.strip()][-1]
                print(f"FALLA en la celda {i}: {cell.source.splitlines()[0][:80]}")
                print(f"  {ultima}")
                sys.exit(1)
            tiempos.append((time.perf_counter() - t0, cell.source.splitlines()[0][:70]))
    if a.guardar:
        nbformat.write(nb, a.guardar)
    # Reinicio de Colab: kernel nuevo, solo preparación + identidad, repetir E2.1 y validar desde archivos.
    reinicio = [c for c in nb.cells if c.cell_type == "code" and c.source.startswith(
        ("#@title Preparar el entorno", "#@title 0 · Identidad", "#@title E2.1"))]
    reinicio.append(nbformat.v4.new_code_cell("M2 = T.validar()\nprint('PUNTAJE_TRAS_REINICIO', M2['puntaje'])"))
    nb2 = nbformat.v4.new_notebook(cells=reinicio)
    cliente2 = NotebookClient(nb2, timeout=600, kernel_name="python3", resources={"metadata": {"path": str(trabajo)}})
    cliente2.execute()
    salida2 = "\n".join(o.get("text", "") for c in nb2.cells for o in c.get("outputs", []) if o.get("output_type") == "stream")
    assert "PUNTAJE_TRAS_REINICIO 100" in salida2, salida2[-800:]
    print("Reinicio simulado: el trabajo se rehidrata desde los archivos y la validación sigue en 100/100.")
    from tc1_pruebas import verificar_evidencias
    salida = "\n".join(o.get("text", "") for c in nb.cells if c.cell_type == "code" for o in c.get("outputs", [])
                       if o.get("output_type") == "stream")
    html = (ROOT / "assets" / "tutoriales" / "s08-secoppipeline.html").read_text(encoding="utf-8")
    faltan = verificar_evidencias(html, salida)
    assert not faltan, f"evidencias del checklist que el cuaderno no imprime: {faltan}"
    print("Checklist: cada evidencia citada aparece en la salida real del cuaderno.")
    manifest = json.loads((out / C.MANIFEST).read_text(encoding="utf-8"))
    print("Celdas más lentas:")
    for s, t in sorted(tiempos, reverse=True)[:5]:
        print(f"  {s:6.1f} s · {t}")
    print(f"API simulada: {est_api['peticiones']} peticiones · 429 inyectados: {est_api['429_enviados']}")
    print(f"PUNTAJE {manifest['puntaje']}/100 · nota {manifest['nota_exacta']} → {manifest['nota_registrada']}")
    fallas = {k: c["evidencia"] for k, c in manifest["controles"].items() if not c["ok"]}
    for k, v in fallas.items():
        print("  ✗", k, v)
    zip_path = trabajo / f"TC1_{PAREJA}.zip"
    entrega = [p for p in trabajo.iterdir() if p.is_dir() and p.name.startswith("TC1_BIGDATA_")]
    assert manifest["puntaje"] == 100, "el solucionario debe obtener 100/100"
    assert manifest["pendiente_confirmacion_visual"] == ["E2.6", "E4.3", "E5.4"]
    assert manifest["gates"]["sin_secretos"]["ok"] is True
    assert zip_path.exists() and entrega, "falta el paquete o la carpeta de entrega"
    # Fuera de Colab el notebook no se guarda solo: se copia como lo haría el estudiante.
    nbformat.write(nb, entrega[0] / f"TC1_{PAREJA}.ipynb")
    import tc1_teacher_validator as TV
    huella = (entrega[0] / C.MANIFEST).read_bytes()
    import hashlib
    r = TV.revisar(entrega[0], hashlib.sha256(huella).hexdigest(), {"E2": True, "E4": True, "E5": True})
    print(TV.panel(r))
    assert not r["avisos"], r["avisos"]
    assert not r["diferencias"] and r["docente"]["puntaje"] == 100
    assert r["docente"]["pendiente_confirmacion_visual"] == []
    print("E2E TC1 V9: OK · notebook completo ejecutado con servicios reales y revalidado por el docente")


if __name__ == "__main__":
    main()
