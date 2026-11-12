"""Fuente de datos del visor S11: inventario y descarga verificada de diez voces."""
from __future__ import annotations
import hashlib
import io
import json
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIO_MANIFEST = ROOT / "datos/manifiestos/audios_minds14.json"
PARQUET = ROOT / "datos/minds14_es-ES.parquet"
URL = "https://huggingface.co/datasets/PolyAI/minds14/resolve/main/es-ES/train-00000-of-00001.parquet"
SHA_PARQUET = "989bf2f90676a5eb5852fe785a03b1d9b97763e0febbd0fd0a3f489afd83badf"


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def inventario():
    """Una entrada por acta, foto o voz; PDF y PNG son dos vistas de una misma acta."""
    base = ROOT / "datos/raw"
    manifest = ROOT / "datos/manifiestos/fotos_catalogadas_32.json"
    detalles = {}
    if manifest.is_file():
        for row in json.loads(manifest.read_text(encoding="utf-8"))["registros"]:
            detalles[Path(row["input_path"]).name] = row

    result = []
    for file in sorted((base / "fotos").glob("eltiempo_*")):
        if file.suffix.lower() not in (".jpg", ".webp", ".png"):
            continue
        result.append(dict(grupo="El Tiempo (30)", nombre=file.name, original=file,
                           preview=file, clase="imagen", credito="Por verificar",
                           url="", noticia=""))
    for file in sorted((base / "fotos_catalogadas").glob("*.webp")):
        meta = detalles.get(file.name, {})
        result.append(dict(grupo="Fotografías con ficha (32)", nombre=file.name,
                           original=file, preview=file, clase="imagen",
                           credito=meta.get("credit") or "No consignado",
                           url=meta.get("source_url") or "",
                           noticia=str(meta.get("article_id") or "")))
    for page in sorted((base / "actas").glob("secop_acta_*_pagina1.png")):
        original = base / "actas_pdf" / page.name.replace("_pagina1.png", ".pdf")
        result.append(dict(grupo="Actas SECOP (30)", nombre=page.stem.replace("_pagina1", ""),
                           original=original, preview=page, clase="pdf",
                           credito="Documento SECOP; verificar fuente", url="", noticia=""))
    if AUDIO_MANIFEST.exists():
        info = json.loads(AUDIO_MANIFEST.read_text(encoding="utf-8"))
        for row in info["audios"]:
            original = ROOT / row["pcm16"]
            if original.is_file() and original.resolve().is_relative_to(ROOT):
                result.append(dict(grupo="Voces MINDS-14 (30)", nombre=original.name,
                                   original=original, preview=original, clase="audio",
                                   credito="PolyAI MINDS-14 es-ES; CC BY 4.0",
                                   url=URL, noticia=row["registro"],
                                   referencia=row["referencia"], intencion=row["intencion"]))
    return result


def preparar_audios():
    """Verifica un Parquet con voces humanas reales y selecciona treinta voces por rondas de intención."""
    from urllib.request import Request, urlopen
    import numpy as np
    import pandas as pd
    import soundfile as sf

    PARQUET.parent.mkdir(parents=True, exist_ok=True)
    if not PARQUET.exists():
        temporal = PARQUET.with_suffix(".part")
        try:
            request = Request(URL, headers={"User-Agent": "BigData-UCentral-educativo/1.0"})
            with urlopen(request, timeout=180) as web, temporal.open("wb") as out:
                while True:
                    block = web.read(1024 * 1024)
                    if not block:
                        break
                    out.write(block)
                    if out.tell() > 100_000_000:
                        raise ValueError("Archivo de más de 100 MB")
            temporal.replace(PARQUET)
        except Exception:
            temporal.unlink(missing_ok=True)
            raise
    if sha256(PARQUET) != SHA_PARQUET:
        raise ValueError("El SHA-256 del Parquet MINDS-14 no coincide con la fuente auditada")

    data = pd.read_parquet(PARQUET, columns=["audio", "path", "transcription", "intent_class"])
    # Muestreo reproducible por rondas: cada intención aporta una voz
    # antes de tomar la segunda de cualquiera de ellas.
    data = data.sort_values("path", kind="stable").copy()
    data["ronda"] = data.groupby("intent_class").cumcount()
    escogidas = data.sort_values(["ronda", "intent_class", "path"], kind="stable").head(30)
    rows = [fila for _, fila in escogidas.iterrows()]
    if len(rows) != 30 or len({str(x["path"]) for x in rows}) != 30:
        raise ValueError("No fue posible seleccionar 30 grabaciones distintas")

    original_dir = ROOT / "datos/raw/audios"
    processed_dir = ROOT / "datos/derived/audios"
    original_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for n, row in enumerate(rows, 1):
        obj = row["audio"]
        if not isinstance(obj, dict) or not isinstance(obj.get("bytes"), (bytes, bytearray)):
            raise ValueError("Un audio no contiene los bytes de la fuente")
        raw = bytes(obj["bytes"])
        if not raw.startswith(b"RIFF") or raw[8:12] != b"WAVE":
            raise ValueError("El original no es un contenedor WAV")
        source = original_dir / f"voz_{n:02}_fuente.wav"
        original_hash = hashlib.sha256(raw).hexdigest()
        if source.exists() and sha256(source) != original_hash:
            raise ValueError(f"La fuente {source.name} fue modificada")
        if not source.exists():
            source.write_bytes(raw)

        with sf.SoundFile(io.BytesIO(raw)) as decoder:
            rate = decoder.samplerate
            samples = decoder.read(dtype="float32", always_2d=True)
        if rate < 8000 or samples.shape[0] < rate // 2:
            raise ValueError("Frecuencia o duración inválida")
        mono = samples.mean(axis=1)
        pcm = (np.clip(mono, -1, 1) * 32767).astype("<i2")
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(rate)
            out.writeframes(pcm.tobytes())
        target = processed_dir / f"voz_{n:02}.wav"
        encoded = buffer.getvalue()
        digest = hashlib.sha256(encoded).hexdigest()
        if target.exists() and sha256(target) != digest:
            raise ValueError(f"El derivado {target.name} fue modificado")
        if not target.exists():
            target.write_bytes(encoded)
        records.append(dict(
            registro=str(row["path"]), intencion=int(row["intent_class"]),
            referencia=str(row["transcription"]),
            fuente=str(source.relative_to(ROOT)), sha_fuente=original_hash,
            pcm16=str(target.relative_to(ROOT)), sha_pcm16=digest,
            duracion_s=round(len(mono) / rate, 3)
        ))
    AUDIO_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    AUDIO_MANIFEST.write_text(json.dumps({
        "dataset": "PolyAI/minds14", "subset": "es-ES", "license": "CC BY 4.0",
        "source_url": URL, "sha256_parquet": SHA_PARQUET, "audios": records
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    return len(records)
