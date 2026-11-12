"""Pruebas ligeras del laboratorio Dask. NO levanta clúster ni espera 0,6 s."""
import unittest
from dask_cuando_si import cpus_disponibles, crear_trabajos, procesar_lote

class PruebaS13Dask(unittest.TestCase):
    def test_lotes_secop_igual_total(self):
        trabajos = crear_trabajos(8, 0.0, "espera", 1000)
        self.assertEqual(len(trabajos), 8)
        self.assertGreater(sum(len(t["textos"]) for t in trabajos), 0)
        self.assertLessEqual(sum(len(t["textos"]) for t in trabajos), 1000)
    def test_misma_funcion_es_determinista(self):
        tarea = {"id": 0, "textos": ["compra computadores", "mantenimiento"],
                 "modo": "espera", "espera": 0.0, "iteraciones": 1000}
        a, b = procesar_lote(tarea), procesar_lote(tarea)
        for campo in ("id", "registros", "palabras", "sha256"):
            self.assertEqual(a[campo], b[campo])
        self.assertEqual(a["palabras"], 3)
    def test_cpu_logicas(self):
        self.assertGreaterEqual(cpus_disponibles(), 1)

if __name__ == "__main__":
    unittest.main()
