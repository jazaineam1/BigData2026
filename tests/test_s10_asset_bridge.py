"""Pruebas negativas y de idempotencia del contrato ZIP S10 v2 (stdlib)."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main
import copy
import io
import json
import zipfile

from utils.s10_asset_bridge import sha256, validar_zip_etl_web, importar_zip_etl_web


def fixture(override=None, catalog_change=False):
    image = b"\x89PNG\r\n\x1a\n" + b"original de prueba"
    derived = b"\x89PNG\r\n\x1a\n" + b"derivado de prueba"
    params = {"lado_maximo": 160, "gris": True}
    metrics = {"luminancia_media": 123.45}
    row = {
        "schema_version": "s10-asset-v2",
        "record_id": "a001", "asset_id": sha256(image),
        "source_kind": "uploaded_by_student", "source_type": "uploaded_by_student", "source_id": None,
        "article_id": None, "source_record_id": None,
        "modality": "image", "modalidad": "image",
        "original_path": "raw/a001_original.png", "raw_path": "raw/a001_original.png",
        "derived_path": "derived/a001_procesado.png", "nombre_original": "autorizada.png",
        "original_sha256": sha256(image), "sha256_original": sha256(image),
        "source_original_sha256": sha256(image), "derived_sha256": sha256(derived),
        "sha256_derivado": sha256(derived), "sha256": sha256(derived),
        "profile": "imagen_160_gris_100_100", "feature_version": "s10-v2",
        "metric_name": "mean_luminance", "metric_value": 123.45,
        "parameters_json": json.dumps(params), "parametros": params,
        "metrics_json": json.dumps(metrics), "metricas": metrics,
        "status": "ok", "bytes_original": len(image), "bytes_derivado": len(derived)
    }
    if override:
        row.update(override)
    manifest = {
        "schema": "bigdata-s10-etl-reactivo/v2", "case_id": "laura_compras_claras_s10",
        "registros": [row], "cantidad": 1
    }
    blob = io.BytesIO()
    with zipfile.ZipFile(blob, "w", compression=zipfile.ZIP_STORED) as z:
        z.writestr(row["original_path"], image)
        z.writestr(row["derived_path"], derived)
        z.writestr("catalogo.jsonl", json.dumps(row, ensure_ascii=False) + "\n" if not catalog_change else "{}\n")
        z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False))
    blob.seek(0)
    return blob


class TestBridge(TestCase):
    def test_valida_y_reimporta_sin_duplicar(self):
        with TemporaryDirectory() as temp:
            package = fixture()
            first = importar_zip_etl_web(package, temp)
            package.seek(0)
            second = importar_zip_etl_web(package, temp)
            self.assertEqual(first["sha_lote"], second["sha_lote"])
            self.assertEqual(first["carpeta"], second["carpeta"])
            self.assertEqual(first["cantidad"], 1)
            self.assertEqual(len(list(Path(temp).rglob("catalogo_importado.jsonl"))), 1)
            self.assertEqual(first["registros"][0]["article_id"], None)

    def test_rechaza_sha_derivado_incorrecto(self):
        with self.assertRaisesRegex(ValueError, "Huellas|SHA-256"):
            validar_zip_etl_web(fixture({"derived_sha256": "0"*64}))

    def test_rechaza_asociacion_editorial_falsa(self):
        with self.assertRaisesRegex(ValueError, "relaciones"):
            validar_zip_etl_web(fixture({"article_id": "3562373"}))

    def test_rechaza_ruta_traversal(self):
        with self.assertRaisesRegex(ValueError, "Ruta"):
            validar_zip_etl_web(fixture({"original_path": "../a001.png", "raw_path": "../a001.png"}))

    def test_rechaza_jsonl_incoherente(self):
        with self.assertRaisesRegex(ValueError, "Catálogo"):
            validar_zip_etl_web(fixture(catalog_change=True))

    def test_rechaza_version_incompatible(self):
        with self.assertRaisesRegex(ValueError, "Versión"):
            validar_zip_etl_web(fixture({"schema_version": "s10-asset-v1"}))


if __name__ == "__main__":
    main()
