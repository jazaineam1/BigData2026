"""S11 · ETL autónomo de imágenes y audio: Laura / Compras Claras.

E: snapshot de imágenes ya curadas del repositorio + MINDS-14 es-ES autorizado.
T: perfiles de imagen y audio, inspección numérica, quality gates.
L: RAW inmutable, JSONL + Parquet, manifiesto SHA-256, relectura e idempotencia.
No procesa video. No atribuye voces bancarias a noticias ni contratos SECOP.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import os
import shutil
import tempfile
import time
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
import soundfile as sf
from PIL import Image, ImageEnhance, ImageOps

ROOT_URL = "https://raw.githubusercontent.com/jazaineam1/BigData2026/main"
VOICE_URL = "https://huggingface.co/datasets/PolyAI/minds14/resolve/main/es-ES/train-00000-of-00001.parquet"
VOICE_SHA = "989bf2f90676a5eb5852fe785a03b1d9b97763e0febbd0fd0a3f489afd83badf"
LICENSE = "CC-BY-4.0"
SCHEMA = "s11-etl-media-v1"


def digest(value: bytes | Path) -> str:
    data = value.read_bytes() if isinstance(value, Path) else value
    return hashlib.sha256(data).hexdigest()


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def store_original(path: Path, raw: bytes, expected_sha: str | None = None) -> str:
    sha = digest(raw)
    if expected_sha is not None and sha != expected_sha:
        raise ValueError(f"SHA-256 no coincide para {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if digest(path) != sha:
            raise ValueError(f"RAW alterado; no se sobrescribe: {path}")
    else:
        path.write_bytes(raw)
    return sha


def _get(url: str, limit: int = 65_000_000) -> bytes:
    req = Request(url, headers={"User-Agent": "BigData2026-S11-educational/1.0"})
    with urlopen(req, timeout=120) as response:
        length = response.headers.get("Content-Length")
        if length and int(length) > limit:
            raise ValueError("El origen excede el límite autorizado")
        chunks, total = [], 0
        while True:
            part = response.read(1024 * 1024)
            if not part:
                break
            total += len(part)
            if total > limit:
                raise ValueError("La descarga excedió el límite autorizado")
            chunks.append(part)
    return b"".join(chunks)


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def download_sources(root: Path, image_count: int = 4, voice_count: int = 10) -> dict:
    """Descarga un snapshot, nunca rastrea páginas editoriales.

    El dataset de voz se descarga UNA sola vez y se verifica con SHA-256.
    Las imágenes tienen checksum individual fijado en el inventario existente.
    """
    if not 2 <= image_count <= 8 or not 2 <= voice_count <= 10:
        raise ValueError("Usa 2–8 imágenes y 2–10 audios reales")
    root.mkdir(parents=True, exist_ok=True)
    meta = json.loads(_get(f"{ROOT_URL}/Datos/s10_imagenes_reales/inputs.json", 150_000))
    if len(meta) != 32 or len({str(m["article_id"]) for m in meta}) != 24:
        raise ValueError("El snapshot editorial cambió; no inventar una equivalencia")
    picked = sorted(meta, key=lambda m: (m["article_id"], m["job_id"]))[:image_count]
    images = []
    for m in picked:
        name = str(m["job_id"]) + ".webp"
        raw_path = root / "raw" / "images" / name
        if raw_path.exists():
            if digest(raw_path) != m["input_sha256"]:
                raise ValueError("Imagen RAW previamente alterada: " + name)
        else:
            content = _get(f"{ROOT_URL}/Datos/s10_imagenes_reales/raw/{name}", 8_000_000)
            store_original(raw_path, content, m["input_sha256"])
        with Image.open(raw_path) as im:
            im.verify()
        images.append({
            "source_kind": "eltiempo_snapshot", "source_id": m["job_id"],
            "article_id": str(m["article_id"]),
            "source_record_id": None, "source_url": m["source_url"],
            "credit": m.get("credit", ""), "license": "uso educativo condicionado a derechos editoriales",
            "original_path": _relative(root, raw_path), "original_sha256": m["input_sha256"],
            "modality": "image",
        })
    cache = root / "cache" / "minds14_es-ES_train.parquet"
    if cache.exists():
        if digest(cache) != VOICE_SHA:
            raise ValueError("Cache MINDS-14 incompatible con la fuente auditada")
    else:
        source = _get(VOICE_URL, 100_000_000)
        store_original(cache, source, VOICE_SHA)
    voices = pd.read_parquet(cache, columns=["audio", "path", "intent_class"])
    voices = voices.sort_values("path", kind="stable").reset_index(drop=True)
    selected, categories = [], set()
    for index, row in voices.iterrows():
        cls = int(row["intent_class"])
        if cls not in categories:
            selected.append((index, row))
            categories.add(cls)
        if len(selected) == voice_count:
            break
    if len(selected) != voice_count:
        raise ValueError("No se pudieron seleccionar las categorías de voz requeridas")
    audio = []
    for i, (source_index, row) in enumerate(selected, 1):
        buf = row["audio"]
        if not isinstance(buf, dict) or not isinstance(buf.get("bytes"), (bytes, bytearray)):
            raise ValueError("Fuente MINDS-14 sin audio embebido")
        raw = bytes(buf["bytes"])
        if not raw.startswith(b"RIFF") or raw[8:12] != b"WAVE":
            raise ValueError("WAV de origen inválido")
        source_id = str(row["path"])
        raw_path = root / "raw" / "audio" / f"voz_{i:02d}_fuente.wav"
        sha = store_original(raw_path, raw)
        audio.append({
            "source_kind": "PolyAI_MINDS14_es-ES", "source_id": source_id,
            "article_id": None, "source_record_id": source_id,
            "source_url": VOICE_URL, "credit": "PolyAI / MINDS-14",
            "license": LICENSE, "original_path": _relative(root, raw_path),
            "original_sha256": sha, "modality": "audio",
            "intent_class": int(row["intent_class"]), "source_row": int(source_index)
        })
    return {"images": images, "audio": audio, "selection": {
        "images": "primeros por article_id/job_id; el conteo se controla en notebook",
        "audio": "una por intención diferente ordenada por path",
        "image_catalog_count": 32, "distinct_article_count": 24,
        "voice_parquet_sha256": VOICE_SHA,
    }}


def _image_metrics(im: Image.Image) -> dict:
    arr = np.asarray(im.convert("L"), dtype=np.uint8)
    hist = np.bincount(arr.ravel(), minlength=256).reshape(16, 16).sum(axis=1)
    return {
        "width_px": int(im.width), "height_px": int(im.height),
        "mean_luminance": round(float(arr.mean()), 4),
        "std_luminance": round(float(arr.std()), 4),
        "dark_fraction": round(float((arr < 50).mean()), 6),
        "histogram_16_bins": hist.tolist(),
    }


def image_etl(root: Path, entry: dict, *, max_side: int, grayscale: bool, contrast: float = 1.0) -> dict:
    if max_side not in (160, 320, 640) or not (0.5 <= contrast <= 2.0):
        raise ValueError("Perfil de imagen no admitido")
    raw_path = root / entry["original_path"]
    if digest(raw_path) != entry["original_sha256"]:
        raise ValueError("La imagen fuente fue modificada")
    with Image.open(raw_path) as raw_im:
        original_metrics = _image_metrics(raw_im)
        im = raw_im.convert("RGB")
    im.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    if grayscale:
        im = ImageOps.grayscale(im)
    im = ImageEnhance.Contrast(im).enhance(contrast)
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=False)
    raw_out = buf.getvalue()
    name = f"{entry['source_id']}_{max_side}_{'gris' if grayscale else 'color'}_{int(contrast*100)}.png"
    dest = root / "derived" / "images" / name
    store_original(dest, raw_out)
    metrics = _image_metrics(im)
    passed = bool(metrics["width_px"] > 0 and metrics["height_px"] > 0 and
                  max(metrics["width_px"], metrics["height_px"]) <= max_side and
                  sum(metrics["histogram_16_bins"]) == metrics["width_px"] * metrics["height_px"])
    return _row(root, entry, dest, f"image_{max_side}_{'gray' if grayscale else 'rgb'}_c{int(contrast*100)}",
                {"max_side": max_side, "grayscale": grayscale, "contrast": contrast},
                metrics, original_metrics, passed)


def _mono_float(raw: bytes) -> tuple[np.ndarray, int, str]:
    with sf.SoundFile(io.BytesIO(raw)) as decoder:
        data = decoder.read(dtype="float32", always_2d=True)
        rate = decoder.samplerate
        codec = decoder.subtype
    if not 8000 <= rate <= 48000 or not 0.2 <= len(data) / rate <= 300:
        raise ValueError("Frecuencia o duración fuera de límites didácticos")
    return data.mean(axis=1), rate, codec


def _audio_metrics(samples: np.ndarray, rate: int) -> dict:
    if not len(samples):
        raise ValueError("Audio vacío")
    # Dominio temporal y centroide espectral con ventana Hann (no transcripción).
    rms = float(np.sqrt(np.mean(samples.astype(np.float64)**2)))
    peak = float(np.max(np.abs(samples)))
    zero = float(np.mean(np.diff(np.signbit(samples).astype(np.int8)) != 0) * rate) if len(samples) > 1 else 0.0
    win = samples[:min(len(samples), 4096)].astype(np.float64)
    spectrum = np.abs(np.fft.rfft(win * np.hanning(len(win))))
    hz = np.fft.rfftfreq(len(win), 1 / rate)
    centroid = float(np.sum(spectrum * hz) / (np.sum(spectrum) + 1e-12))
    return {
        "duration_s": round(len(samples) / rate, 4), "sample_rate_hz": rate,
        "rms": round(rms, 6), "peak": round(peak, 6),
        "zero_crossings_per_s": round(zero, 2),
        "spectral_centroid_hz": round(centroid, 2),
        "clipping_fraction": round(float(np.mean(np.abs(samples) >= 0.999)), 6)
    }


def audio_etl(root: Path, entry: dict, *, target_rate: int, gain: float, start_s: float = 0.0,
              seconds: float | None = None) -> dict:
    if target_rate not in (8000, 16000) or not (0 <= gain <= 1.5) or start_s < 0:
        raise ValueError("Parámetros de audio no admitidos")
    src = root / entry["original_path"]
    raw = src.read_bytes()
    if digest(raw) != entry["original_sha256"]:
        raise ValueError("El audio fuente fue modificado")
    data, rate, codec = _mono_float(raw)
    start = round(start_s * rate)
    if start >= len(data):
        raise ValueError("El inicio está fuera de la grabación")
    end = min(len(data), start + round(seconds * rate)) if seconds else len(data)
    segment = data[start:end]
    out_n = max(1, int(round(len(segment) * target_rate / rate)))
    positions = np.arange(out_n) * (rate / target_rate)
    re_sampled = np.interp(positions, np.arange(len(segment)), segment)
    gained = np.clip(re_sampled * gain, -1.0, 1.0).astype(np.float32)
    buf = io.BytesIO()
    sf.write(buf, gained, target_rate, format="WAV", subtype="PCM_16")
    name = f"{entry['original_sha256'][:12]}_{target_rate}_{int(gain*100)}.wav"
    dest = root / "derived" / "audio" / name
    store_original(dest, buf.getvalue())
    original_metrics = _audio_metrics(data, rate)
    metrics = _audio_metrics(gained, target_rate)
    metrics["source_codec"] = codec
    passed = bool(metrics["duration_s"] > 0 and metrics["rms"] <= 1.0 and
                  metrics["sample_rate_hz"] == target_rate)
    return _row(root, entry, dest, f"audio_pcm16_{target_rate}_gain{int(gain*100)}",
                {"target_rate": target_rate, "gain": gain, "start_s": start_s,
                 "seconds": seconds}, metrics, original_metrics, passed)


def _row(root: Path, source: dict, derived: Path, profile: str,
         params: dict, metrics: dict, initial: dict, passed: bool) -> dict:
    src_path = root / source["original_path"]
    return {
        "schema_version": SCHEMA,
        "asset_id": source["original_sha256"],
        "derived_id": f"{source['original_sha256'][:16]}_{profile}",
        "modality": source["modality"], "source_kind": source["source_kind"],
        "source_id": source["source_id"], "article_id": source["article_id"],
        "source_record_id": source["source_record_id"],
        "source_url": source["source_url"], "credit": source["credit"],
        "license": source["license"], "original_path": source["original_path"],
        "derived_path": _relative(root, derived),
        "original_bytes": src_path.stat().st_size, "derived_bytes": derived.stat().st_size,
        "original_sha256": source["original_sha256"], "derived_sha256": digest(derived),
        "profile": profile, "parameters_json": json.dumps(params, sort_keys=True),
        "metrics_json": json.dumps(metrics, sort_keys=True),
        "original_metrics_json": json.dumps(initial, sort_keys=True),
        "status": "ok" if passed else "quality_failed",
    }


def save_outputs(root: Path, rows: list[dict], selection: dict) -> dict:
    if not rows:
        raise ValueError("El ETL no generó filas")
    unique = {(r["asset_id"], r["profile"]) for r in rows}
    if len(unique) != len(rows):
        raise ValueError("Se intentó guardar un derivado duplicado")
    for row in rows:
        if row["modality"] == "audio" and row["article_id"] is not None:
            raise ValueError("Audio MINDS-14 asociado artificialmente a noticias")
        if row["modality"] == "image" and row["source_record_id"] is not None:
            raise ValueError("Imagen atribuida a la voz MINDS-14")
    out = root / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    rows_sorted = sorted(rows, key=lambda r: (r["modality"], r["asset_id"], r["profile"]))
    jlines = "".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n"
                     for row in rows_sorted)
    (out / "catalogo_s11.jsonl").write_text(jlines, encoding="utf-8")
    pd.DataFrame(rows_sorted).to_parquet(out / "catalogo_s11.parquet", index=False)
    report = {
        "schema": SCHEMA, "rows": len(rows_sorted),
        "images": sum(r["modality"] == "image" for r in rows_sorted),
        "audio": sum(r["modality"] == "audio" for r in rows_sorted),
        "quality_passed": sum(r["status"] == "ok" for r in rows_sorted),
        "source_selection": selection,
        "files": {
            r["original_path"]: r["original_sha256"] for r in rows_sorted
        } | {
            r["derived_path"]: r["derived_sha256"] for r in rows_sorted
        },
        "catalog_sha256": digest(out / "catalogo_s11.jsonl"),
        "no_editorial_audio_links": True,
    }
    _write_json(out / "manifest_s11.json", report)
    return report


def verify_outputs(root: Path) -> dict:
    out = root / "outputs"
    manifest = json.loads((out / "manifest_s11.json").read_text(encoding="utf-8"))
    if manifest["schema"] != SCHEMA:
        raise ValueError("Versión de manifiesto inválida")
    cat = out / "catalogo_s11.jsonl"
    if digest(cat) != manifest["catalog_sha256"]:
        raise ValueError("Catálogo alterado")
    rows = [json.loads(line) for line in cat.read_text(encoding="utf-8").splitlines() if line]
    parquet = pd.read_parquet(out / "catalogo_s11.parquet")
    if len(rows) != manifest["rows"] or len(parquet) != len(rows):
        raise ValueError("Conteos de catálogo incompatibles")
    if set(manifest["files"]) != set([r["original_path"] for r in rows] +
                                     [r["derived_path"] for r in rows]):
        raise ValueError("Manifiesto de archivos incompleto")
    for path, sha in manifest["files"].items():
        full = (root / path).resolve()
        if not full.is_relative_to(root.resolve()) or not full.is_file():
            raise ValueError("Ruta insegura o archivo faltante: " + path)
        if digest(full) != sha:
            raise ValueError("SHA-256 alterado: " + path)
    if not all(row["status"] == "ok" for row in rows):
        raise ValueError("Hay filas que no superaron la calidad")
    return {
        "ok": True, "rows": len(rows), "images": manifest["images"],
        "audio": manifest["audio"], "sha_catalog": manifest["catalog_sha256"],
        "files": len(manifest["files"])
    }


def run_s11(root: Path, image_count: int = 4, audio_count: int = 10,
            image_side: int = 320, image_gray: bool = True,
            audio_rate: int = 16000, audio_gain: float = 1.0) -> tuple[pd.DataFrame, dict]:
    """Ejecuta desde cero; repetir con los mismos parámetros preserva los SHA."""
    start = time.perf_counter()
    sources = download_sources(root, image_count, audio_count)
    rows = []
    for im in sources["images"]:
        rows.append(image_etl(root, im, max_side=image_side, grayscale=image_gray))
        rows.append(image_etl(root, im, max_side=160, grayscale=False))
    for wave in sources["audio"]:
        rows.append(audio_etl(root, wave, target_rate=audio_rate, gain=audio_gain))
    report = save_outputs(root, rows, sources["selection"])
    proof = verify_outputs(root)
    frame = pd.DataFrame(rows)
    print(f"EXTRACCIÓN: {len(sources['images'])} imágenes reales y {len(sources['audio'])} voces reales")
    print(f"TRANSFORMACIÓN: {len(rows)} derivados; {sum(r['status'] == 'ok' for r in rows)} controles válidos")
    print(f"CARGA: JSONL + PARQUET + MANIFIESTO; SHA: {proof['sha_catalog'][:16]}")
    print(f"PAQUETE S11 VERIFICADO: {proof['rows']} filas; {proof['files']} archivos")
    print(f"TIEMPO TOTAL: {time.perf_counter()-start:.3f} s (incluye descarga y disco; no es benchmark distribuido)")
    return frame, proof
