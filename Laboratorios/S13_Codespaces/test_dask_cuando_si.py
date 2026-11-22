"""Pruebas ligeras del laboratorio Dask. NO levanta clúster ni espera 0,6 s."""
import unittest
from dask_cuando_si import cpus_disponibles, cuota_cpu_cgroup, crear_trabajos, procesar_lote, construir_traza_tareas

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
    def test_transformacion_real_textos(self):
        tareas = crear_trabajos(8, 0.0, "texto", 1000)
        resultados = [procesar_lote(t) for t in tareas]
        self.assertEqual(sum(r["registros"] for r in resultados), 1000)
        self.assertGreater(sum(r["terminos_distintos"] for r in resultados), 0)
        self.assertTrue(all(r["frecuencias"] for r in resultados))
        self.assertEqual(procesar_lote(tareas[0])["frecuencias"],
                         resultados[0]["frecuencias"])

    def test_traza_mide_tareas_reales_sin_arrancar_cluster(self):
        trabajo = {"id": 0, "textos": ["mantenimiento computadores"],
                   "modo": "texto", "espera": 0, "iteraciones": 1000}
        resultado = procesar_lote(trabajo)
        self.assertGreaterEqual(resultado["fin_monotonico_ns"],
                                resultado["inicio_monotonico_ns"])
        traza = construir_traza_tareas([resultado])
        self.assertEqual(len(traza), 1)
        self.assertEqual(traza[0]["lote"], 1)
        self.assertEqual(traza[0]["inicio_ms"], 0)
        self.assertGreaterEqual(traza[0]["duracion_ms"], 0)
        self.assertEqual(traza[0]["registros"], 1)

    def test_traza_ordenada_sin_tiempos_inventados(self):
        muestras = [
            {"id": 2, "worker": "worker-b", "registros": 1,
             "inicio_monotonico_ns": 2_000_000, "fin_monotonico_ns": 4_000_000},
            {"id": 0, "worker": "worker-a", "registros": 2,
             "inicio_monotonico_ns": 1_000_000, "fin_monotonico_ns": 3_000_000},
        ]
        trazas = construir_traza_tareas(muestras)
        self.assertEqual([x["lote"] for x in trazas], [1, 3])
        self.assertEqual([x["inicio_ms"] for x in trazas], [0, 1])
        self.assertEqual([x["duracion_ms"] for x in trazas], [2, 2])
        self.assertEqual([x["worker"] for x in trazas], ["Worker 1", "Worker 2"])

    def test_cuota_cgroup_v2(self):
        self.assertEqual(cuota_cpu_cgroup('400000 100000'), 4)
        self.assertEqual(cuota_cpu_cgroup('150000 100000'), 1)
        self.assertIsNone(cuota_cpu_cgroup('max 100000'))
        self.assertIsNone(cuota_cpu_cgroup('datos no validos'))

    def test_cpu_logicas(self):
        self.assertGreaterEqual(cpus_disponibles(), 1)

if __name__ == "__main__":
    unittest.main()
