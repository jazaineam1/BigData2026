"""Pruebas ligeras y reproducibles de los retos del proyecto final.

No usa red, Codespaces, Dask, Spark, modelos ni GitHub Actions.
Ejecuta: python -m unittest discover -s tests -p 'test_proyecto_final_aprendizaje.py' -v
Las pruebas pandas requieren pandas (ya instalado en el entorno del curso).
"""
from __future__ import annotations

import ast
import hashlib
import csv
import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "utils"))
import proyecto_final_offset as descarga_offset  # no realiza solicitudes al importar

NB_PATH = ROOT / "Cuadernos/Proyecto_Final_Compras_Claras.ipynb"
DATA = ROOT / "Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv"

SOLUCIONES = {
    "E1.1": 'descarga_offset.PAGE_SIZE',
    "E2.1": 'len(base[(base["split"] == "test") & (base["modalidad"] == "Contratación directa")])',
    "E3.1": 'conteos_dask == conteos_pandas',
    "E4.1": 'resultado_dask["mejor_C"]',
    "E5.1": 'sum(int(fila["registros"]) for fila in filas_gold)',
    "E6.1": 'matriz_test[0][1] + matriz_test[1][0]',
    "E7.1": 'int((predicciones["modalidad_real"] != predicciones["modalidad_predicha"]).sum())',
}


def cargar_cuaderno():
    return json.loads(NB_PATH.read_text(encoding="utf-8"))


def codigo_de(etiqueta):
    for celda in cargar_cuaderno()["cells"]:
        if celda["cell_type"] != "code":
            continue
        fuente = "".join(celda["source"])
        if fuente.startswith("# " + etiqueta + " ·"):
            return fuente
    raise AssertionError("Falta bloque de código " + etiqueta)


class PruebasAprendizaje(unittest.TestCase):
    def test_todas_las_celdas_python_compilan(self):
        codigos = [c for c in cargar_cuaderno()["cells"] if c["cell_type"] == "code"]
        self.assertGreaterEqual(len(codigos), 15)
        for i, celda in enumerate(codigos):
            with self.subTest(celda=i):
                ast.parse("".join(celda["source"]), filename="celda_" + str(i))

    def test_siete_retos_una_expresion_y_sin_nuevas_fuentes(self):
        cuaderno = cargar_cuaderno()
        total = 0
        for etiqueta in SOLUCIONES:
            with self.subTest(etiqueta=etiqueta):
                codigo = codigo_de(etiqueta)
                self.assertEqual(codigo.count("= ____"), 1)
                self.assertIn("assert ", codigo)
                total += 1
        self.assertEqual(total, 7)
        texto = "\n".join("".join(c["source"]) for c in cuaderno["cells"])
        self.assertIn("datos reales", texto.lower())
        self.assertIn("observatorio.html", texto)
        self.assertNotIn("Elección de dataset", texto)

    def test_reto_offset_real_sin_http(self):
        ns = {"descarga_offset": descarga_offset}
        codigo = codigo_de("E1.1").replace("____", SOLUCIONES["E1.1"], 1)
        exec(compile(codigo, "reto_e1", "exec"), ns)
        self.assertEqual(ns["offset_segunda_pagina"], 20)

    def test_retos_dask_con_trazas_controladas(self):
        ns = {"conteos_dask": {"directa": 2, "especial": 3},
              "conteos_pandas": {"directa": 2, "especial": 3},
              "trabajadores": [{"id": 0}, {"id": 1}]}
        exec(codigo_de("E3.1").replace("____", SOLUCIONES["E3.1"], 1), ns)
        self.assertTrue(ns["coinciden_los_resultados"])
        configs = [{"C": 0.1, "f1_cv": .4}, {"C": 1.0, "f1_cv": .8},
                   {"C": 10.0, "f1_cv": .5}]
        ns = {"resultado_dask": {"configuraciones": configs, "mejor_C": 1.0},
              "evidencia_d": {"mejor_C": 1.0}}
        exec(codigo_de("E4.1").replace("____", SOLUCIONES["E4.1"], 1), ns)
        self.assertEqual(ns["C_seleccionado"], 1.0)

    def test_retos_databricks_sin_usar_databricks(self):
        ns = {"evidencia_e": {"filas": 6},
              "filas_gold": [{"registros": 2}, {"registros": 4}]}
        exec(codigo_de("E5.1").replace("____", SOLUCIONES["E5.1"], 1), ns)
        self.assertEqual(ns["total_gold"], 6)
        ns = {"evidencia_f": {"prueba": 6,
             "matriz_real_0_1_pred_0_1": [[2, 1], [1, 2]]}}
        exec(codigo_de("E6.1").replace("____", SOLUCIONES["E6.1"], 1), ns)
        self.assertEqual(ns["errores_spark"], 2)

    @unittest.skipUnless(importlib.util.find_spec("pandas"), "requiere pandas")
    def test_retos_con_dataframe_real_de_prueba(self):
        import numpy as np
        import pandas as pd
        ns = {"base": pd.DataFrame([
            {"split": "test", "modalidad": "Contratación directa"},
            {"split": "test", "modalidad": "Contratación régimen especial"},
            {"split": "train", "modalidad": "Contratación directa"}
        ]), "np": np}
        exec(codigo_de("E2.1").replace("____", SOLUCIONES["E2.1"], 1), ns)
        self.assertEqual(ns["n_directa_en_test"], 1)
        ns = {"predicciones": pd.DataFrame([
            {"modalidad_real": "directa", "modalidad_predicha": "directa"},
            {"modalidad_real": "especial", "modalidad_predicha": "directa"}
        ]), "np": np}
        exec(codigo_de("E7.1").replace("____", SOLUCIONES["E7.1"], 1), ns)
        self.assertEqual(ns["errores_del_producto"], 1)

    def test_e4_ejecuta_con_trazas_dask_inyectadas(self):
        class S13Simulado:
            @staticmethod
            def entrenar_y_evaluar(tabla):
                return {"f1_macro": .79, "f1_control": .33,
                        "matriz_confusion": [[2, 1], [1, 2]]}

            @staticmethod
            def experimentos_distribuidos(tabla, n_workers):
                assert n_workers == 2
                return {"workers_en_un_codespace": 2,
                        "configuraciones": [{"C": .1, "f1_cv": .7},
                                           {"C": 1., "f1_cv": .75},
                                           {"C": 10., "f1_cv": .6}],
                        "mejor_C": 1., "f1_prueba_final": .8}
        with tempfile.TemporaryDirectory() as td:
            ns = {"S13": S13Simulado(), "tabla_curada": object(),
                  "directorio": Path(td), "json": json}
            exec(codigo_de("E4"), ns)
            resultados = json.loads((Path(td) / "D_modelo_dask.json").read_text())
            self.assertEqual(resultados["workers"], 2)
            self.assertEqual(len(resultados["configuraciones"]), 3)
            self.assertEqual(resultados["mejor_C"], 1.0)
            self.assertEqual(resultados["f1_prueba_final"], .8)

    def test_el_manifiesto_recoge_microrretos_y_respeta_pendientes(self):
        codigo_cierre = next("".join(c["source"]) for c in cargar_cuaderno()["cells"]
                            if c["cell_type"] == "code"
                            and "".join(c["source"]).startswith("# Cierre · una sola traza"))
        with tempfile.TemporaryDirectory() as temporal:
            ns = {
                "offset_segunda_pagina": 20, "n_directa_en_test": 43,
                "coinciden_los_resultados": True, "C_seleccionado": 1.0,
                "errores_del_producto": 9,
                "directorio": Path(temporal), "manifiesto": {"estados": {}},
                "hashlib": hashlib, "json": json,
            }
            exec(codigo_cierre, ns)
            salida = json.loads((Path(temporal) / "manifest_final.json").read_text())
            self.assertEqual(salida["microretos"]["E1.1_offset"], 20)
            self.assertEqual(salida["microretos"]["E7.1_errores_observatorio"], 9)
            self.assertIsNone(salida["microretos"]["E5.1_registros_Gold"])
            self.assertIsNone(salida["microretos"]["E6.1_errores_Spark"])
            self.assertEqual(salida["estados"]["H_microretos.json"]["estado"], "presente")

    def test_fuente_1000_y_curaduria_810_con_stdlib(self):
        with DATA.open(newline="", encoding="utf-8") as f:
            original = list(csv.DictReader(f))
        self.assertEqual(len(original), 1000)
        self.assertEqual(len(original[0]), 59)
        etiquetas = {"Contratación directa", "Contratación régimen especial"}
        filas = [r for r in original if r["modalidad_de_contratacion"] in etiquetas]
        self.assertEqual(len(filas), 830)
        sin_marcador = [r for r in filas if r["descripci_n_del_procedimiento"]
                        .strip().casefold() != "no definido"]
        self.assertEqual(len(sin_marcador), 811)
        texts = {}
        for r in sin_marcador:
            clave = re.sub(r"\s+", " ", r["descripci_n_del_procedimiento"].strip().lower())
            texts.setdefault(clave, r)
        self.assertEqual(len(texts), 810)
        clases = [r["modalidad_de_contratacion"] for r in texts.values()]
        self.assertEqual(clases.count("Contratación directa"), 435)
        self.assertEqual(clases.count("Contratación régimen especial"), 375)

    def test_no_esta_publicado_en_pages_o_lms(self):
        pages = (ROOT / ".github/workflows/pages.yml").read_text()
        portada = (ROOT / "index.html").read_text()
        curso = (ROOT / "lms/data/course.json").read_text()
        for text in [pages, portada, curso]:
            self.assertNotIn("Proyecto_Final_Compras_Claras.ipynb", text)
            self.assertNotIn("proyecto-final-explorer.html", text)


if __name__ == "__main__":
    unittest.main()
