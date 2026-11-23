"""S13: QA de bajo costo; no importa Dask ni inicia workers."""
from __future__ import annotations

import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Laboratorios/S13_Codespaces/kmeans_dask_s13.py"


class TestKMeansS13Estatico(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.codigo = SCRIPT.read_text(encoding="utf-8")
        cls.arbol = ast.parse(cls.codigo)

    def test_funciones_y_algoritmo_real(self):
        funciones = {n.name for n in ast.walk(self.arbol) if isinstance(n, ast.FunctionDef)}
        self.assertTrue({"cargar_secop", "preparar_vectores", "ejecutar", "main"} <= funciones)
        for termino in ("dask_ml.cluster", "LocalCluster", "get_task_stream",
                        "TruncatedSVD", "TfidfVectorizer", "adjusted_rand_score"):
            self.assertIn(termino, self.codigo)

    def test_carga_acotada_y_no_acciones_costosas(self):
        self.assertIn("TAMANOS = (250, 1000, 10000, 20000)", self.codigo)
        self.assertIn("S13_PERMITIR_AMPLIACION", self.codigo)
        self.assertIn("threads_per_worker=1", self.codigo)
        self.assertIn('dashboard_address=None', self.codigo)
        self.assertIn("sha256_ids", self.codigo)
        self.assertIn("pipeline_dask_sin_guardado", self.codigo)


if __name__ == "__main__":
    unittest.main()
