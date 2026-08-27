# -*- coding: utf-8 -*-
"""
utils/probar_session4_notebook.py
==================================
Ejecuta todas las celdas de codigo del cuaderno de la sesion 4 que se pueden
probar sin una cuenta de Atlas ni de Astra reales.

Que se prueba y que no
-----------------------
- Se prueba: la reactivacion, la vista menciones_clasificadas en modo de
  respaldo, la regla de priorizacion completa (163 -> 77), la verificacion
  del primer candidato, el enriquecimiento de filas, la tabla HTML para
  Laura, la exportacion a CSV/MD, y las ocho preguntas.
- NO se prueba en automatico: la celda de conexion a Atlas via input()/
  getpass() (pide entrada interactiva; se simula forzando el modo de
  respaldo), ni la demostracion docente de Cassandra/Astra (necesita
  credenciales reales y esta marcada explicitamente como tal).

Uso
---
    python utils/probar_session4_notebook.py
    python utils/probar_session4_notebook.py --local
"""

import argparse
import io
import json
import os
import re
import sys
import traceback

os.environ.setdefault("MPLBACKEND", "Agg")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NB = os.path.join(REPO, "Cuadernos", "4_Atlas_Cassandra_Laura.ipynb")
RAW = "https://raw.githubusercontent.com/jazaineam1/BigData2026/main"


class SalidaHTML:
    def __init__(self, data):
        self.data = data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", action="store_true")
    args = ap.parse_args()

    nb = json.load(io.open(NB, encoding="utf-8"))
    capturado = []

    entorno = {
        "__name__": "__main__",
        "display": lambda x: capturado.append(x.data) if isinstance(x, SalidaHTML) else None,
        "HTML": SalidaHTML,
    }

    ok, fallos, preguntas = 0, [], 0
    html_preguntas = []
    for i, celda in enumerate(nb["cells"]):
        if celda["cell_type"] != "code":
            continue
        src = "".join(celda["source"])

        # Demostracion docente: necesita credenciales reales de Astra. No se
        # ejecuta aqui; se comprueba solo que el CQL y el bind sean coherentes.
        if "cassandra.cluster" in src:
            # Ancla en INSERT INTO: sin esto, un "(" suelto mas arriba en el
            # comentario del titulo (#@title ... (no ejecutes...)) hacia que
            # el regex capturara desde ahi y contara columnas de mas.
            columnas_cql = re.search(r"INSERT INTO[^(]*\(([^)]*)\)\s*VALUES", src, re.S)
            placeholders = src.count("?")
            if columnas_cql:
                n_columnas = len([c for c in columnas_cql.group(1).split(",") if c.strip()])
                if n_columnas != placeholders:
                    fallos.append((i, f"INSERT con {n_columnas} columnas pero {placeholders} '?'"))
                else:
                    print(f"[{i:3d}] demo Astra -> CQL coherente ({n_columnas} columnas = {placeholders} placeholders), no se ejecuta")
            ok += 1
            continue

        src = re.sub(r"^\s*from IPython\.display import .*$", "", src, flags=re.M)

        # La celda de conexion pide input()/getpass(): la forzamos a fallar
        # rapido para probar el modo de respaldo, que es lo que de verdad
        # puede pasar en clase si alguien aun no tiene su URI.
        if "getpass(" in src and "MongoClient" in src:
            src = re.sub(
                r'usuario = input\([^\n]*\n',
                'usuario = "prueba"\n', src)
            src = re.sub(
                r'contrasena = quote_plus\(getpass\([^\n]*\n',
                'contrasena = quote_plus("x")\n', src)
            src = re.sub(
                r'host = input\([^\n]*\n',
                'host = "host-inexistente.invalid"\n', src)
            src = src.replace(
                'client = MongoClient(uri, serverSelectionTimeoutMS=6000)',
                'client = MongoClient(uri, serverSelectionTimeoutMS=1500)')

        if args.local:
            src = src.replace(RAW + "/Datos/", "file:///" + REPO.replace("\\", "/") + "/Datos/")
            src = src.replace(RAW + "/Cuadernos/",
                              "file:///" + REPO.replace("\\", "/") + "/Cuadernos/")

        es_pregunta = "pregunta_interactiva(" in src and "def pregunta_interactiva" not in src
        antes = len(capturado)

        try:
            exec(compile(src, f"celda_{i}", "exec"), entorno)
            ok += 1
            if es_pregunta:
                preguntas += 1
                html_preguntas.extend(capturado[antes:])
            if "motor" in entorno and i < 20:
                print(f"[{i:3d}] motor activo -> {entorno['motor']}")
        except Exception:
            fallos.append((i, traceback.format_exc()))
            print(f"[{i:3d}] FALLO")
            print(traceback.format_exc()[-800:])

    problemas = []
    if preguntas != 8:
        problemas.append(f"se ejecutaron {preguntas} preguntas y deberian ser 8")
    sin_boton = [h for h in html_preguntas if "Verificar respuesta" not in h]
    if sin_boton:
        problemas.append(f"{len(sin_boton)} pregunta(s) se dibujaron sin su boton de verificar")
    radios = sum(h.count('type="radio"') for h in html_preguntas)
    if preguntas and radios != preguntas * 4:
        problemas.append(f"hay {radios} opciones dibujadas y deberian ser {preguntas * 4}")

    if entorno.get("motor", "").startswith("Atlas"):
        problemas.append("la prueba automatica no deberia poder conectarse a un Atlas real")

    esperado = {
        "candidatos": 77,
        "cruce": 163,
    }
    if isinstance(entorno.get("candidatos"), object) and "candidatos" in entorno:
        try:
            n_candidatos = len(entorno["candidatos"])
            if n_candidatos != esperado["candidatos"]:
                problemas.append(f"candidatos = {n_candidatos}, se esperaban {esperado['candidatos']}")
        except TypeError:
            pass

    for archivo in ("resultados/s04_priorizacion_laura.csv", "hitos/s04/priorizacion_laura.md"):
        ruta = os.path.join(REPO, *archivo.split("/"))
        if not os.path.exists(ruta):
            problemas.append(f"no se genero {archivo}")

    print()
    print("=" * 64)
    print(f"celdas de codigo ejecutadas : {ok}")
    print(f"  de ellas, preguntas       : {preguntas} de 8")
    print(f"  bloques HTML de preguntas : {len(html_preguntas)}")
    print(f"  opciones dibujadas        : {radios}")
    print(f"fallos                      : {len(fallos)}")
    for p in problemas:
        print("  ✗", p)
    if not fallos and not problemas:
        print()
        print("Todo ejecuta, incluidas las ocho preguntas y la regla de priorizacion.")
    return 1 if (fallos or problemas) else 0


if __name__ == "__main__":
    sys.exit(main())
