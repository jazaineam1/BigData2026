"""Pruebas rápidas y deterministas del laboratorio Codespaces S11."""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
import lab

class LaboratorioS11(unittest.TestCase):
    def test_coseno_matematico(self):
        self.assertAlmostEqual(lab.coseno([1, 0], [1, 0]), 1)
        self.assertAlmostEqual(lab.coseno([1, 0], [0, 1]), 0)
        with self.assertRaises(ValueError):
            lab.coseno([1], [1, 2])

    def test_preparar_y_ocr_reales(self):
        anterior = lab.OUT
        with tempfile.TemporaryDirectory(prefix="s11-codespace-test-") as raiz:
            try:
                lab.OUT = Path(raiz)
                lab.preparar()
                ficha = lab.cargar_json("origen.json")
                self.assertEqual(len(ficha["archivos"]), 2)
                for item in ficha["archivos"]:
                    archivo = lab.OUT / item["archivo"]
                    self.assertTrue(archivo.is_file())
                    self.assertEqual(lab.hash_sha256(archivo), item["sha256"])
                lab.ocr(None)
                resultado = lab.cargar_json("ocr.json")
                self.assertIn("CONTRATOS", resultado["texto_extraido"].upper())
                self.assertIn("12", resultado["texto_extraido"])
                self.assertEqual(resultado["sha256"],
                                 lab.hash_sha256(lab.OUT / "afiche_simulado.png"))
            finally:
                lab.OUT = anterior

if __name__ == "__main__":
    unittest.main()
