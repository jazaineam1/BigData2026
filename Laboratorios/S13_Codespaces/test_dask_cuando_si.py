"""Pruebas ligeras del laboratorio Dask. NO levanta clúster ni espera 0,6 s."""
import unittest
from dask_cuando_si import cpus_disponibles, cuota_cpu_cgroup, crear_trabajos, procesar_lote

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
    def test_transformacion_real_de_titulos(self):
        trabajo={"id":0,"textos":["mantenimiento computadores",
                                  "hospital mantenimiento"],
                 "modo":"datos","espera":0.0,"iteraciones":1000}
        salida=procesar_lote(trabajo)
        self.assertEqual(salida["registros"],2)
        self.assertEqual(salida["palabras"],4)
        self.assertEqual(salida["frecuencias"]["mantenimiento"],2)
        self.assertEqual(salida["frecuencias"]["hospital"],1)
        self.assertEqual(sum(salida["frecuencias"].values()),salida["palabras"])

    def test_modos_mismo_trabajo_sin_esperas(self):
        base={"id":0,"textos":["hospital computadores"],"espera":0,
              "iteraciones":1000}
        real=procesar_lote({**base,"modo":"datos"})
        sim=procesar_lote({**base,"modo":"espera"})
        for clave in ("registros","palabras","frecuencias","sha256"):
            self.assertEqual(real[clave],sim[clave])

    def test_cuota_cgroup_v2(self):
        self.assertEqual(cuota_cpu_cgroup('400000 100000'), 4)
        self.assertEqual(cuota_cpu_cgroup('150000 100000'), 1)
        self.assertIsNone(cuota_cpu_cgroup('max 100000'))
        self.assertIsNone(cuota_cpu_cgroup('datos no validos'))

    def test_cpu_logicas(self):
        self.assertGreaterEqual(cpus_disponibles(), 1)

if __name__ == "__main__":
    unittest.main()
