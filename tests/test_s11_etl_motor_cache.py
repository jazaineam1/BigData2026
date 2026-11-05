"""Regresión del incidente 3530042.wav: Colab cachea un motor S11 obsoleto."""
import contextlib
import inspect
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
CELLS = json.loads((ROOT / "utils/s11_lesson_cells.json").read_text(encoding="utf-8"))
LOAD = next(x["source"] for x in CELLS if x["id"] == "s11-cargar-motor")
LONG = next(x["source"] for x in CELLS if x["id"] == "s11-audio-largo")


class AudioEngineCacheTest(unittest.TestCase):
    def test_cached_legacy_module_gets_refreshed_without_touching_raw(self):
        with tempfile.TemporaryDirectory() as temp:
            cwd = Path(temp)
            root = cwd / "work"
            root.mkdir()
            stale = root / "s11_etl_core.py"
            stale.write_text(
                'ESQUEMA="s11-etl-imagen-audio/v1"\n'
                'def transformar_audios(raiz, entradas, ganancia=1.0): return []\n',
                encoding="utf-8",
            )
            raw = root / "raw" / "audios_alumno" / "3530042.wav"
            raw.parent.mkdir(parents=True)
            raw.write_bytes(b"sample unchanged")
            source = (ROOT / "utils/s11_etl_core.py").read_bytes()
            counter = []
            def fake_urlopen(request, timeout=None):
                counter.append((request.full_url, timeout))
                return io.BytesIO(source)

            context = {"RAIZ": root}
            original_cwd = Path.cwd()
            try:
                os.chdir(cwd)  # Asegura que no hay motor utils/ local.
                with patch("urllib.request.urlopen", side_effect=fake_urlopen):
                    exec(compile(LOAD, "<s11-cargar-motor>", "exec"), context)
            finally:
                os.chdir(original_cwd)
            engine = context["core"]
            self.assertIn("block_seconds", inspect.signature(engine.transformar_audios).parameters)
            self.assertIn("on_block", inspect.signature(engine.transformar_audios).parameters)
            self.assertEqual(raw.read_bytes(), b"sample unchanged")
            self.assertEqual(len(counter), 1, "La firma vieja debe activar UNA descarga de refresco")
            self.assertIn("block_seconds", stale.read_text(encoding="utf-8"))

    def test_compatible_cache_works_without_network(self):
        with tempfile.TemporaryDirectory() as temp:
            cwd = Path(temp)
            root = cwd / "work"
            root.mkdir()
            cached = root / "s11_etl_core.py"
            cached.write_bytes((ROOT / "utils/s11_etl_core.py").read_bytes())
            context = {"RAIZ": root}
            original_cwd = Path.cwd()
            try:
                os.chdir(cwd)
                with patch("urllib.request.urlopen", side_effect=AssertionError("no download allowed")):
                    exec(compile(LOAD, "<s11-cargar-motor>", "exec"), context)
            finally:
                os.chdir(original_cwd)
            self.assertIn("block_seconds", inspect.signature(context["core"].transformar_audios).parameters)

    def test_long_audio_cell_rechecks_signature_and_reuses_existing_wav(self):
        self.assertIn('NOMBRE_WAV_EXISTENTE = "3530042.wav"', LONG)
        self.assertIn('if existente.is_file():', LONG)
        self.assertIn('"block_seconds" not in inspect.signature(core.transformar_audios).parameters', LONG)
        self.assertIn('cargar_motor_s11(forzar_actualizacion=True)', LONG)
        self.assertIn('PROBAR_WAV_PROPIO', LONG)


if __name__ == "__main__":
    unittest.main()
