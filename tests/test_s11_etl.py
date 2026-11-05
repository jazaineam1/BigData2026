"""Pruebas de extremo a extremo SIN red del ETL S11: 32 imágenes + 10 voces.

Los datos de QA son fixtures creados en memoria y NO se presentan como
las fotografías editoriales ni las voces reales del laboratorio.
"""
import io
import json
from pathlib import Path
import tempfile
import unittest
import wave
from unittest import mock
import zipfile

import numpy as np
import pandas as pd
from PIL import Image
from utils import s11_etl_core as core


def crear_datos():
    inventario, contenido = [], {}
    for n in range(32):
        im = Image.new("RGB", (80 + n, 40 + n), (n * 6 % 256, n * 13 % 256, 140))
        buf = io.BytesIO()
        im.save(buf, format="WEBP")
        raw = buf.getvalue()
        trabajo = f"imagen_{n:02}.webp"
        path = "raw/" + trabajo
        contenido[core.BASE + "Datos/s10_imagenes_reales/" + path] = raw
        inventario.append({
            "article_id": str(3500000 + (n % 24)),
            "occurrence_id": f"3500000:{n}",
            "credit": "fixture_generado_QA",
            "source_url": "https://example.invalid/solo_fixture",
            "input_path": path,
            "input_sha256": core.sha256(raw),
        })
    contenido[core.MANIFEST_IMAGENES] = json.dumps(inventario).encode("utf-8")
    voces = []
    for n in range(40):
        rate = 8000
        t = np.arange(rate * 2) / rate
        muestras = (np.sin(2 * np.pi * (180 + 30 * n) * t) * 5000).astype("<i2")
        b = io.BytesIO()
        with wave.open(b, "wb") as f:
            f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate)
            f.writeframes(muestras.tobytes())
        voces.append({
            "audio": {"bytes": b.getvalue(), "path": f"es-ES/qa_{n:02}.wav"},
            "path": f"es-ES/qa_{n:02}.wav",
            "intent_class": n % 14,
            "transcription": f"ejemplo de voz QA {n}",
        })
    salida = io.BytesIO()
    pd.DataFrame(voces).to_parquet(salida, index=False)
    contenido[core.PARQUET_VOZ] = salida.getvalue()
    return contenido


class TestS11EtL(unittest.TestCase):
    def test_lote_completo_idempotente_y_verificable(self):
        contenido = crear_datos()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with mock.patch.object(core, "obtener", side_effect=lambda url, limite: contenido[url]), \
                 mock.patch.object(core, "SHA_PARQUET", core.sha256(contenido[core.PARQUET_VOZ])):
                imagenes = core.extraer_imagenes(root)
                voces = core.extraer_audios(root)
                self.assertEqual((len(imagenes), len(voces)), (32, 10))
                self.assertEqual(len({x["article_id"] for x in imagenes}), 24)
                self.assertTrue(all(x["article_id"] is None for x in voces))
                img_t = core.transformar_imagenes(root, imagenes, 320, "grises")
                aud_t = core.transformar_audios(root, voces, 1.0)
                self.assertEqual(sum(img_t[0]["metrics"]["histogram8"]),
                                 img_t[0]["metrics"]["width"]*img_t[0]["metrics"]["height"])
                self.assertEqual(aud_t[0]["metrics"]["sample_rate_hz"], 16000)
                self.assertEqual(aud_t[0]["metrics"]["channels"], 1)
                decisions = {"image_profile": "grises", "alternative": 1, "limit": 2}
                result = core.cargar_catalogo(root, img_t, aud_t, decisions)
                self.assertEqual(result["resumen"]["total"], 42)
                self.assertEqual(result["resumen"]["fuentes_cruzadas"], 0)
                core.crear_manifiesto(root, result["filas"])
                self.assertTrue(core.verificar(root)["ok"])
                self.assertEqual(core.probar_detencion(root), "CORRUPCION_DETECTADA")
                archive = core.empaquetar(root)
                with zipfile.ZipFile(archive) as z:
                    self.assertIsNone(z.testzip())
                    self.assertIn("outputs/catalogo.parquet", z.namelist())
                    self.assertIn("manifest_s11.json", z.namelist())
                    self.assertEqual(sum(n.startswith("raw/") for n in z.namelist()), 42)
                again_images = core.transformar_imagenes(root, core.extraer_imagenes(root), 320, "grises")
                again_audio = core.transformar_audios(root, core.extraer_audios(root), 1.0)
                self.assertEqual([x["derived_sha256"] for x in again_images],
                                 [x["derived_sha256"] for x in img_t])
                self.assertEqual([x["derived_sha256"] for x in again_audio],
                                 [x["derived_sha256"] for x in aud_t])
                another_profile = core.transformar_imagenes(root, imagenes, 160, "bordes")
                self.assertNotEqual(another_profile[0]["derived_sha256"], img_t[0]["derived_sha256"])
                self.assertTrue(core.verificar(root)["ok"])
                # Corrupción real: se detecta en la verificación, nunca se acepta.
                altered = root / img_t[0]["derived_path"]
                altered.write_bytes(altered.read_bytes() + b"qa")
                self.assertFalse(core.verificar(root)["ok"])

    def test_escala_real_40_voces_y_digitos_uci_por_particiones(self):
        """El reto utiliza nuevas fuentes verificadas, no duplica 32 fotos."""
        contenido = crear_datos()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with mock.patch.object(core, "obtener", side_effect=lambda url, limite: contenido[url]), \
                 mock.patch.object(core, "SHA_PARQUET", core.sha256(contenido[core.PARQUET_VOZ])):
                prensa=core.extraer_imagenes(root)
                manuscritos=core.extraer_imagenes_digitos(root,12)
                voces=core.extraer_audios(root,max_audios=30)
                self.assertEqual(len(manuscritos),12)
                self.assertEqual(len({x["original_sha256"] for x in manuscritos}),12)
                self.assertEqual(len(voces),30)
                self.assertTrue(all(x["article_id"] is None for x in manuscritos+voces))
                esperado=2*(32+12)+30
                primero=core.procesar_lotes_escala(root,prensa+manuscritos,voces,
                                                   tamano_lote=8,etiqueta="qa")
                self.assertEqual(primero["verified"]["rows"],esperado)
                self.assertEqual(primero["verified"]["sources"],32+12+30)
                self.assertEqual(len(primero["particiones"]),10)
                # Misma entrada y configuración -> mismo SHA en particiones y mismos resultados.
                huellas=[x["sha256"] for x in primero["manifest"]["partitions"]]
                segundo=core.procesar_lotes_escala(root,prensa+manuscritos,voces,
                                                   tamano_lote=8,etiqueta="qa")
                self.assertEqual(huellas,[x["sha256"] for x in segundo["manifest"]["partitions"]])
                self.assertTrue(core.verificar_lotes_escala(root,segundo["manifest_path"])["ok"])
                # Fallo controlado: alterar UN derivado debe invalidar el manifiesto del reto.
                import pandas as pd
                parti=Path(segundo["manifest_path"]).parent/segundo["manifest"]["partitions"][0]["name"]
                fila=pd.read_parquet(parti).iloc[0]
                derivado=root/fila["derived_path"]
                respaldo=derivado.read_bytes()
                derivado.write_bytes(b"corrupcion intencional del test")
                self.assertFalse(core.verificar_lotes_escala(root,segundo["manifest_path"])["ok"])
                derivado.write_bytes(respaldo)
                self.assertTrue(core.verificar_lotes_escala(root,segundo["manifest_path"])["ok"])

    def test_parametros_incorrectos_se_rechazan(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "lado"):
                core.transformar_imagenes(Path(tmp), [], 7, "grises")
            with self.assertRaisesRegex(ValueError, "Ganancia"):
                core.transformar_audios(Path(tmp), [], 9.0)
            with self.assertRaisesRegex(ValueError, "max_audios"):
                core.extraer_audios(Path(tmp), 15)
            with self.assertRaisesRegex(ValueError, "max_imagenes"):
                core.extraer_imagenes(Path(tmp), 0)


if __name__ == "__main__":
    unittest.main()
