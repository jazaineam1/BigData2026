"""Prueba offline y ligera del generador del producto final.

Uso manual: python -m unittest -v tests/test_proyecto_final_observatorio.py
No requiere pandas, modelos, red ni motor de navegador.
"""
from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Laboratorios/Proyecto_Final_2026"))
from generar_observatorio import generar


class ProductoFinalTests(unittest.TestCase):
    def test_generar_html_sin_servidor_y_con_ids_de_test(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            datos = base / "secop_final.csv"
            pred = base / "predicciones.csv"
            met = base / "D_modelo_dask.json"
            salida = base / "observatorio.html"
            with datos.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["id_del_proceso","texto","modalidad","split"])
                w.writeheader()
                w.writerow({"id_del_proceso":"abc-1","texto":"mantenimiento de computadores",
                            "modalidad":"Contratación directa","split":"train"})
                w.writerow({"id_del_proceso":"abc-2","texto":"<img src=x onerror=alert(1)>",
                            "modalidad":"Contratación régimen especial","split":"test"})
            with pred.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["id_del_proceso","modalidad_real",
                             "modalidad_predicha","probabilidad_clase_predicha"])
                w.writeheader()
                w.writerow({"id_del_proceso":"abc-2",
                            "modalidad_real":"Contratación régimen especial",
                            "modalidad_predicha":"Contratación directa",
                            "probabilidad_clase_predicha":"0.5"})
            met.write_text(json.dumps({"f1_prueba_final":0.25,"f1_dummy":0.5,
                 "mejor_C":0.1,"workers":2}),encoding="utf-8")
            info=generar(datos,pred,met,salida)
            pagina=salida.read_text(encoding="utf-8")
            self.assertEqual(info["filas"],2)
            self.assertEqual(info["test"],1)
            self.assertIn("abc-2",pagina)
            self.assertIn("filtrados()",pagina)
            self.assertIn("Observatorio de modalidad SECOP II",pagina)
            self.assertNotIn("<img src=x onerror=alert(1)>",pagina)
            self.assertIn("\\u003cimg",pagina)

    def test_rechaza_predicciones_incompletas(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            (base/"x.csv").write_text("id_del_proceso,texto,modalidad,split\n1,ok,a,test\n",
                                      encoding="utf-8")
            (base/"p.csv").write_text("id_del_proceso,modalidad_predicha\n2,a\n",
                                      encoding="utf-8")
            (base/"m.json").write_text("{}",encoding="utf-8")
            with self.assertRaises(ValueError):
                generar(base/"x.csv",base/"p.csv",base/"m.json",base/"out.html")


if __name__=="__main__":
    unittest.main()
