"""Verifica rutas y pares reales que el visor presenta al alumnado."""
import json
import unittest
from pathlib import Path

from fuentes import ROOT, inventario, preparar_audios, sha256


class VisorFuentesTest(unittest.TestCase):
    def test_92_registros_visual_documentales(self):
        registros = inventario()
        grupos = {g: [x for x in registros if x["grupo"] == g]
                  for g in ["El Tiempo (30)", "Fotografías con ficha (32)", "Actas SECOP (30)"]}
        self.assertEqual([len(v) for v in grupos.values()], [30, 32, 30])
        for item in registros:
            self.assertTrue(item["original"].is_file(), item["nombre"])
            self.assertTrue(item["preview"].is_file(), item["nombre"])
        for doc in grupos["Actas SECOP (30)"]:
            self.assertEqual(doc["original"].suffix, ".pdf")
            self.assertTrue(doc["preview"].name.endswith("_pagina1.png"))
        self.assertEqual(len({x["nombre"] for x in grupos["Actas SECOP (30)"]}), 30)

    def test_metadatos_y_hashes(self):
        fotos = [x for x in inventario() if x["grupo"] == "Fotografías con ficha (32)"]
        self.assertTrue(any(x["credito"] and x["url"] and x["noticia"] for x in fotos))
        foto = fotos[0]["original"]
        self.assertEqual(len(sha256(foto)), 64)

    def test_30_voces_cuando_estan_preparadas(self):
        from fuentes import AUDIO_MANIFEST
        if not AUDIO_MANIFEST.exists():
            self.skipTest("Audio de HF se descarga en integración; no requiere red en test local")
        data = json.loads(AUDIO_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(len(data["audios"]), 30)
        self.assertEqual(len({x["registro"] for x in data["audios"]}), 30)
        audios = [x for x in inventario() if x["grupo"] == "Voces MINDS-14 (30)"]
        self.assertEqual(len(audios), 30)
        for item in audios:
            self.assertTrue(item["original"].is_file())


if __name__ == "__main__":
    unittest.main()
