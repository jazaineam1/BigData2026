"""S10: importa paquetes ZIP del ETL reactivo web sin instalar bibliotecas adicionales.

Contrato v2: cada fila conserva raw, derived, procedencia y SHA-256. No crea
relaciones con noticias de El Tiempo ni registros SECOP: source_id/article_id
permanecen vacíos salvo que exista comprobación independiente.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import zipfile

SCHEMA = "bigdata-s10-etl-reactivo/v2"
ASSET_SCHEMA = "s10-asset-v2"
MAX_ARCHIVE_BYTES = 120 * 1024 * 1024
MAX_ASSET_BYTES = 8 * 1024 * 1024
MAX_FILES = 6
REQUIRED = (
    "record_id", "asset_id", "source_kind", "modality", "original_path",
    "derived_path", "original_sha256", "derived_sha256", "sha256",
    "profile", "feature_version", "metric_name", "metric_value",
    "metrics_json", "parameters_json", "status",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _valid_path(path: str, folder: str, record_id: str) -> bool:
    return bool(re.fullmatch(rf"{folder}/{record_id}_(original|procesado)\.[a-z0-9]{{1,5}}", path))


def validar_zip_etl_web(archivo) -> dict:
    """Comprueba integridad, contrato y seguridad ANTES de escribir a disco.

    Acepta ruta o archivo abierto. No extrae entradas arbitrarias del ZIP.
    """
    if isinstance(archivo, (str, Path)):
        size = Path(archivo).stat().st_size
        if size > MAX_ARCHIVE_BYTES:
            raise ValueError("ZIP demasiado grande (máximo 120 MiB)")
    with zipfile.ZipFile(archivo, "r") as z:
        info = z.infolist()
        if not 4 <= len(info) <= 2 * MAX_FILES + 2:
            raise ValueError("Cantidad de archivos ZIP incompatible")
        names = [entry.filename for entry in info]
        if len(set(names)) != len(names):
            raise ValueError("Entradas repetidas en ZIP")
        if any(entry.is_dir() or entry.file_size > 16 * 1024 * 1024
               or (entry.external_attr >> 16) & 0o170000 == 0o120000
               for entry in info):
            raise ValueError("Entrada ZIP no admitida")
        if sum(entry.file_size for entry in info) > MAX_ARCHIVE_BYTES:
            raise ValueError("ZIP supera límite de bytes descomprimidos")
        if not {"catalogo.jsonl", "manifest.json"} <= set(names):
            raise ValueError("Falta catálogo JSONL o manifiesto")
        manifest = json.loads(z.read("manifest.json").decode("utf-8"))
        if manifest.get("schema") != SCHEMA:
            raise ValueError("Versión de manifiesto incompatible")
        if manifest.get("case_id") != "laura_compras_claras_s10":
            raise ValueError("Caso del paquete no reconocido")
        rows = manifest.get("registros")
        if not isinstance(rows, list) or not (1 <= len(rows) <= MAX_FILES):
            raise ValueError("Cantidad de registros inválida")
        parsed = [json.loads(line) for line in z.read("catalogo.jsonl").decode("utf-8").splitlines()
                  if line.strip()]
        if parsed != rows:
            raise ValueError("Catálogo JSONL y manifiesto no coinciden")
        expected_paths = {"catalogo.jsonl", "manifest.json"}
        files: dict[str, bytes] = {}
        seen = set()
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("Registro no es objeto JSON")
            if any(field not in row for field in REQUIRED):
                raise ValueError("Faltan campos del contrato s10-asset-v2")
            identifier = row["record_id"]
            if not isinstance(identifier, str) or not re.fullmatch(r"a\d{3}", identifier):
                raise ValueError("Identificador de activo inválido")
            if identifier in seen:
                raise ValueError("ID repetido")
            seen.add(identifier)
            if row.get("schema_version") != ASSET_SCHEMA:
                raise ValueError("Versión de activo incorrecta")
            if row["modality"] not in ("image", "audio") or row.get("modalidad") != row["modality"]:
                raise ValueError("Modalidad inválida")
            if row["source_kind"] not in ("uploaded_by_student", "generated_for_course"):
                raise ValueError("Procedencia sin clasificar")
            if row.get("article_id") is not None or row.get("source_record_id") is not None:
                raise ValueError("No se admiten relaciones editoriales/voz inventadas")
            if row["status"] != "ok":
                raise ValueError("Estado distinto de ok")
            if sha := row.get("source_original_sha256"):
                if sha != row["original_sha256"]:
                    raise ValueError("SHA-256 del origen no coincide")
            if (row.get("sha256_original") != row["original_sha256"]
                or row.get("sha256_derivado") != row["derived_sha256"]
                or row["sha256"] != row["derived_sha256"]
                or row["asset_id"] != row["original_sha256"]):
                raise ValueError("Huellas internas incompatibles")
            if not (isinstance(row["profile"], str) and len(row["profile"]) < 100):
                raise ValueError("Perfil inválido")
            params = json.loads(row["parameters_json"])
            metrics = json.loads(row["metrics_json"])
            if params != row.get("parametros") or metrics != row.get("metricas"):
                raise ValueError("Parámetros o métricas no coinciden")
            raw, derived = row["original_path"], row["derived_path"]
            if not (_valid_path(raw, "raw", identifier) and _valid_path(derived, "derived", identifier)
                    and row.get("raw_path") == raw and raw != derived):
                raise ValueError("Ruta no permitida, posible traversal")
            for path, hash_field, size_field in (
                (raw, "original_sha256", "bytes_original"),
                (derived, "derived_sha256", "bytes_derivado"),
            ):
                if path not in names or path in files:
                    raise ValueError("Entrada ausente o duplicada: " + path)
                data = z.read(path)  # zipfile valida CRC-32
                if sha256(data) != row[hash_field] or len(data) != row[size_field]:
                    raise ValueError("SHA-256 o tamaño incorrecto: " + path)
                if path == raw and len(data) > MAX_ASSET_BYTES:
                    raise ValueError("Original excede 8 MiB")
                files[path] = data
                expected_paths.add(path)
        if set(names) != expected_paths:
            raise ValueError("Archivos adicionales o faltantes en el ZIP")
    return {"manifest": manifest, "rows": rows, "files": files}


def importar_zip_etl_web(archivo, destino) -> dict:
    """Importa paquete validado bajo lote estable, sin duplicar ni sobrescribir bytes.

    Devuelve carpeta, ruta del catálogo y filas. El catálogo puede cargarse con
    pandas.read_json(..., lines=True) y exportarse a Parquet en Colab.
    """
    paquete = validar_zip_etl_web(archivo)
    firma = hashlib.sha256(
        json.dumps(paquete["manifest"]["registros"], sort_keys=True, ensure_ascii=False)
        .encode("utf-8")).hexdigest()[:16]
    folder = Path(destino) / "importaciones_web" / firma
    for rel, data in paquete["files"].items():
        path = folder / rel
        if path.exists():
            if sha256(path.read_bytes()) != sha256(data):
                raise ValueError("Archivo existente con contenido distinto: " + rel)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    folder.mkdir(parents=True, exist_ok=True)
    rows = []
    for row in paquete["rows"]:
        record = dict(row)
        record["original_path"] = str((folder / row["original_path"]).relative_to(Path(destino)))
        record["derived_path"] = str((folder / row["derived_path"]).relative_to(Path(destino)))
        record["raw_path"] = record["original_path"]
        rows.append(record)
    catalog_path = folder / "catalogo_importado.jsonl"
    data = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n"
    if catalog_path.exists() and catalog_path.read_text(encoding="utf-8") != data:
        raise ValueError("Catálogo ya existente cambió inesperadamente")
    catalog_path.write_text(data, encoding="utf-8")
    return {"carpeta": str(folder), "catalogo": str(catalog_path),
            "cantidad": len(rows), "registros": rows, "sha_lote": firma,
            "verificacion": "PAQUETE WEB VERIFICADO"}
