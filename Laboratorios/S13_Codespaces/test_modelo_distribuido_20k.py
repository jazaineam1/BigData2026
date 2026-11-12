"""Pruebas: no se inventan datos, no hay fuga por IDs y las métricas son coherentes."""
import unittest
import numpy as np
import pandas as pd
from modelo_distribuido_20k import (
    cargar_procesos, crear_variables, variables_estructuradas,
    evaluar, OBJETIVO, ENTRENAMIENTO_MINIMO, COLUMNAS,
)


class Modelo26kTests(unittest.TestCase):
    def test_fuente_autentica_no_generada(self):
        tabla, manifiesto = cargar_procesos(objetivo=100)
        self.assertEqual(len(tabla), 100)
        self.assertTrue(tabla["id_del_proceso"].is_unique)
        self.assertTrue((tabla["precio_objetivo"] > 0).all())
        self.assertTrue(manifiesto["archivos_fuente"])
        self.assertTrue(all("secop_chunk_" in path for path in manifiesto["archivos_fuente"]))

    def test_features_no_filtran_objetivo(self):
        tabla, _ = cargar_procesos(objetivo=100)
        datos = crear_variables(tabla)
        Xtr, Xte, nombres, _ = variables_estructuradas(datos.iloc[:80], datos.iloc[80:])
        self.assertEqual(len(Xtr), 80)
        self.assertEqual(len(Xte), 20)
        self.assertTrue(np.isfinite(Xtr).all())
        self.assertEqual(Xtr.shape[1], Xte.shape[1])
        self.assertTrue(all("precio_base" not in n and
                            "precio_objetivo" not in n and
                            "adjudicacion" not in n for n in nombres))

    def test_metrica_factor_dos(self):
        y=np.log1p(np.array([100., 200., 300.]))
        m=evaluar(y,y)
        self.assertAlmostEqual(m["mae_log"],0)
        self.assertAlmostEqual(m["factor_error_mediano"],1)
        self.assertAlmostEqual(m["porcentaje_dentro_factor_2"],100)

    def test_umbral_tiene_20000_entrenamiento(self):
        self.assertGreaterEqual(int(OBJETIVO*0.8), ENTRENAMIENTO_MINIMO)
        self.assertIn("precio_base", COLUMNAS)
        self.assertNotIn("valor_total_adjudicacion", COLUMNAS)
        self.assertNotIn("adjudicado", COLUMNAS)
        self.assertNotIn("conteo_de_respuestas_a_ofertas", COLUMNAS)


if __name__=="__main__":
    unittest.main()
