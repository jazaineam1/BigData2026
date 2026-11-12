"""Pruebas reproducibles del laboratorio S13."""
import unittest
from analisis import (
    leer_corpus, leer_etiquetados, preparar_clasificacion,
    contraste_mapreduce, comparar_pandas_dask, entrenar_y_evaluar,
    escribir_resultados, recuperacion_demostrativa, tarea_con_fallo, experimentos_distribuidos,
)

class Sesion13Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tabla = leer_etiquetados()

    def test_fuentess(self):
        self.assertEqual(len(leer_corpus()), 200)
        self.assertEqual(len(self.tabla), 1000)
        self.assertEqual(self.tabla["id_del_proceso"].nunique(), 1000)

    def test_dos_clases(self):
        seleccion = preparar_clasificacion(self.tabla)
        self.assertEqual(seleccion["modalidad_de_contratacion"].nunique(), 2)
        self.assertGreater(len(seleccion), 700)

    def test_mapreduce_correcto(self):
        salida = contraste_mapreduce()
        self.assertAlmostEqual(salida["correcto"], 370 / 107)
        self.assertNotAlmostEqual(salida["incorrecto"], salida["correcto"])

    def test_pandas_dask_coinciden(self):
        salida = comparar_pandas_dask(self.tabla, 4)
        self.assertTrue(salida["coinciden"])
        self.assertEqual(sum(salida["conteos"].values()), 1000)

    def test_modelo_supervisado_real(self):
        salida = entrenar_y_evaluar(self.tabla)
        self.assertGreaterEqual(salida["f1_macro"], 0.0)
        self.assertLessEqual(salida["f1_macro"], 1.0)
        self.assertGreater(salida["entrenamiento"], salida["prueba"])

    def test_experimentos_distribuidos(self):
        resultado = experimentos_distribuidos(self.tabla, n_workers=2)
        self.assertEqual(resultado["workers_en_un_codespace"], 2)
        self.assertEqual(len(resultado["configuraciones"]), 3)
        self.assertGreaterEqual(resultado["f1_prueba_final"], 0.0)

    def test_parquet_releible(self):
        salida = escribir_resultados(self.tabla)
        self.assertEqual(salida["filas"], 1000)
        self.assertEqual(len(salida["sha256_fuente"]), 64)

    def test_fallo_controlado(self):
        with self.assertRaises(ValueError):
            tarea_con_fallo(-1)
        salida = recuperacion_demostrativa()
        self.assertEqual(salida["reintento"], 8)

if __name__ == "__main__":
    unittest.main()
