"""Pruebas del verificador externo: no utiliza la lógica de lab.py para validar sus salidas."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import lab
import proyecto
import verificar_independiente as vi


class VerificacionIndependiente(unittest.TestCase):
    def test_wer_con_referencia(self):
        self.assertEqual(vi.tasa_error_palabras("Uno dos tres", "uno cuatro tres"), 1 / 3)
        self.assertEqual(vi.tasa_error_palabras("Hola, mundo", "hola mundo"), 0)
        with self.assertRaises(ValueError):
            vi.tasa_error_palabras("", "algo")

    def test_ocr_real_y_audio_con_referencia(self):
        previo = lab.OUT
        with tempfile.TemporaryDirectory() as temp:
            try:
                lab.OUT = Path(temp)
                lab.preparar()
                lab.ocr(None)
                ficha = lab.cargar_json("origen.json")
                wav = lab.OUT / "voz_simulada.wav"
                lab.guardar_json("asr.json", {
                    "fuente": str(wav), "sha256": vi.huella(wav),
                    "transcripcion": ficha["referencia_asr"],
                    "segmentos": [{"inicio_s": 0, "fin_s": 1, "texto": "Esta es una grabación"}]
                })
                vi.verificar_lab(lab.OUT)
                ocr = lab.cargar_json("ocr.json")
                ocr["sha256"] = "a" * 64
                lab.guardar_json("ocr.json", ocr)
                with self.assertRaisesRegex(AssertionError, "SHA-256 diferente"):
                    vi.verificar_lab(lab.OUT)
            finally:
                lab.OUT = previo

    def test_catalogo_independiente_y_archivo_modificado(self):
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp) / "demo"
            proyecto.crear_proyecto(raiz)
            entrada = raiz / "entradas/textos/acta.txt"
            entrada.write_text("Contrato 12: valor 320000 COP. Fecha 10-11-2026.", encoding="utf-8")
            cfg = proyecto.cargar_config(raiz / "config.json")
            proyecto.ejecutar(raiz, cfg)
            vi.verificar_proyecto(raiz)
            entrada.write_text("La fuente original fue alterada", encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, "SHA-256 diferente"):
                vi.verificar_proyecto(raiz)


if __name__ == "__main__":
    unittest.main()
