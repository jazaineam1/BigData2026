"""Pruebas rápidas y deterministas del laboratorio Codespaces S11."""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
import lab

class LaboratorioS11(unittest.TestCase):
    def test_wer_referencia_conocida_y_origen_coincidente(self):
        from unittest.mock import patch
        anterior = lab.OUT
        with tempfile.TemporaryDirectory(prefix="s11-wer-") as raiz:
            try:
                lab.OUT = Path(raiz)
                lab.preparar()
                origen = lab.cargar_json("origen.json")
                wav = lab.OUT / "voz_simulada.wav"
                lab.guardar_json("asr.json", {
                    "sha256": lab.hash_sha256(wav),
                    "transcripcion": origen["referencia_asr"],
                })
                lab.evaluar_asr()
                self.assertEqual(lab.cargar_json("evaluacion_asr.json")["wer"], 0)
                lab.guardar_json("asr.json", {"sha256": "x" * 64,
                                           "transcripcion": "No corresponde"})
                with self.assertRaisesRegex(ValueError, "no corresponde"):
                    lab.evaluar_asr()
            finally:
                lab.OUT = anterior

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

    def test_extraer_e_indexar_con_voces_y_ocr_simulados(self):
        """Prueba estructura y ranking con vectores deterministas, sin red ni modelos."""
        from unittest.mock import patch
        anterior = lab.OUT
        with tempfile.TemporaryDirectory(prefix="s11-codespace-unidad-") as raiz:
            try:
                lab.OUT = Path(raiz)
                lab.guardar_json("ocr.json", {
                    "texto_extraido": "FECHA: 10-11-2026\nCONTRATOS: 12\nVALOR: 320 MILLONES",
                    "fuente": "/ejemplo/afiche.png", "sha256": "a" * 64
                })
                lab.guardar_json("asr.json", {
                    "transcripcion": "Se registraron cinco requerimientos de información.",
                    "segmentos": [{"inicio_s": 0.0, "fin_s": 3.5,
                                  "texto": "Se registraron cinco requerimientos de información."}],
                    "fuente": "/ejemplo/voz.wav", "sha256": "b" * 64
                })
                lab.extraer()
                info = lab.cargar_json("extraccion.json")
                self.assertTrue(info["audio"]["auditoria_fragmentos"]["ok"])
                self.assertEqual(info["imagen"]["fecha_candidata"], ["10-11-2026"])
                self.assertIn("12", info["imagen"]["cifras_candidatas"])
                def fake_embed(items, model):
                    return [[1.0] * 768 for _ in items]
                with patch.object(lab, "incrustar", side_effect=fake_embed):
                    lab.indexar()
                    indice = lab.cargar_json("indice.json")
                    self.assertEqual(indice["dimension"], 768)
                    self.assertGreaterEqual(len(indice["documentos"]), 4)
                    lab.buscar("¿cuántos contratos?")
            finally:
                lab.OUT = anterior

if __name__ == "__main__":
    unittest.main()
