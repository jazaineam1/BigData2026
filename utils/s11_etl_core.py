# -*- coding: utf-8 -*-
"""S11 · Motor ETL integral de imágenes y audio, sin video.

Uso: import utils.s11_etl_core as core; entradas=core.extraer_imagenes(RAIZ);
audios=core.extraer_audios(RAIZ); ...  NO descarga de medios de terceros.
Los 32 RAW editoriales fueron adquiridos antes por el docente y están en GitHub.
MINDS-14 es-ES CC BY 4.0; 10 WAV originales verificados por un Parquet con SHA.
"""
from __future__ import annotations
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import io
import json
import math
from pathlib import Path
import tempfile
from time import perf_counter
from urllib.request import Request, urlopen
import wave
import zipfile

BASE = "https://raw.githubusercontent.com/jazaineam1/BigData2026/main/"
MANIFEST_IMAGENES = BASE + "Datos/s10_imagenes_reales/inputs.json"
PARQUET_VOZ = "https://huggingface.co/datasets/PolyAI/minds14/resolve/main/es-ES/train-00000-of-00001.parquet"
SHA_PARQUET = "989bf2f90676a5eb5852fe785a03b1d9b97763e0febbd0fd0a3f489afd83badf"
ESQUEMA = "s11-etl-imagen-audio/v1"
AGENTE = "BigData-UCentral-S11-educativo/1.0"
LIMITE_IMAGEN = 12_000_000
LIMITE_CORPUS = 100_000_000


def sha256(datos: bytes | Path) -> str:
    if isinstance(datos, Path):
        h = hashlib.sha256()
        with datos.open("rb") as flujo:
            for bloque in iter(lambda: flujo.read(1024 * 1024), b""):
                h.update(bloque)
        return h.hexdigest()
    return hashlib.sha256(datos).hexdigest()


def obtener(url: str, limite: int) -> bytes:
    # Solo destinos previstos. Sin credenciales, proxies de medios ni subida de datos.
    if not (url.startswith(BASE + "Datos/s10_imagenes_reales/")
            or url in (MANIFEST_IMAGENES, PARQUET_VOZ)):
        raise ValueError("Origen fuera de las dos fuentes autorizadas")
    solicitud = Request(url, headers={"User-Agent": AGENTE})
    with urlopen(solicitud, timeout=120) as respuesta:
        if respuesta.status != 200:
            raise RuntimeError(f"HTTP {respuesta.status} en fuente autorizada")
        partes, total = [], 0
        while True:
            b = respuesta.read(1024 * 1024)
            if not b:
                break
            total += len(b)
            if total > limite:
                raise ValueError("Fuente supera el límite de bytes")
            partes.append(b)
    return b"".join(partes)


def guardar_sin_sobrescribir(ruta: Path, contenido: bytes, esperado: str) -> None:
    if sha256(contenido) != esperado:
        raise ValueError("SHA-256 del origen/derivado diferente")
    if ruta.exists():
        if sha256(ruta) != esperado:
            raise ValueError(f"Archivo modificado: {ruta}. No se sobrescribe")
        return
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(contenido)
    if sha256(ruta) != esperado:
        raise ValueError("Escritura no verificable")


def extraer_imagenes(raiz: Path, max_imagenes: int = 32) -> list[dict]:
    """Lee el inventario y usa el snapshot ya publicado; nunca visita el periódico."""
    if not 1 <= max_imagenes <= 32:
        raise ValueError("max_imagenes debe estar entre 1 y 32")
    raiz = Path(raiz)
    inventario = json.loads(obtener(MANIFEST_IMAGENES, 500_000).decode("utf-8"))
    if len(inventario) != 32 or len({str(x["article_id"]) for x in inventario}) != 24:
        raise ValueError("El inventario editorial ya no coincide con 32 activos/24 artículos")
    if len({x["input_sha256"] for x in inventario}) != 32:
        raise ValueError("Hay originales duplicados en el inventario")
    salida = []
    for item in inventario[:max_imagenes]:
        subruta = item["input_path"]
        if not subruta.startswith("raw/") or "/" in subruta[4:] or not subruta.endswith(".webp"):
            raise ValueError("Ruta del snapshot no permitida")
        ruta = raiz / "raw" / "imagenes" / Path(subruta).name
        esperado = item["input_sha256"]
        if ruta.exists():
            if sha256(ruta) != esperado:
                raise ValueError("RAW de imagen previamente alterado")
        else:
            datos = obtener(BASE + "Datos/s10_imagenes_reales/" + subruta, LIMITE_IMAGEN)
            guardar_sin_sobrescribir(ruta, datos, esperado)
        salida.append({
            "original_path": ruta.relative_to(raiz).as_posix(),
            "original_sha256": esperado,
            "article_id": str(item["article_id"]),
            "source_record_id": None,
            "source_id": str(item["occurrence_id"]),
            "credit": item.get("credit"),
            "source_kind": "editorial_snapshot_docente",
            "source_url": item["source_url"],
            "license": "derechos_editoriales_no_redistribuir",
        })
    print(f"E · IMÁGENES: {len(salida)} RAW verificados; artículos en selección:",
          len({x["article_id"] for x in salida}))
    return salida


def extraer_audios(raiz: Path, max_audios: int = 10) -> list[dict]:
    """Diez voces auténticas, una por intención; conserva WAV original comprimido."""
    import pandas as pd
    import soundfile as sf
    if not 1 <= max_audios <= 400:
        raise ValueError("max_audios debe estar entre 1 y 400")
    raiz = Path(raiz)
    cache = raiz / "cache" / "minds14_es_ES.parquet"
    if cache.exists():
        if sha256(cache) != SHA_PARQUET:
            raise ValueError("Parquet de voces anterior alterado")
    else:
        datos = obtener(PARQUET_VOZ, LIMITE_CORPUS)
        guardar_sin_sobrescribir(cache, datos, SHA_PARQUET)
    corpus = pd.read_parquet(cache, columns=["audio", "path", "transcription", "intent_class"])
    corpus = corpus.sort_values("path", kind="stable").reset_index(drop=True)
    seleccionados, clases = [], set()
    for _, fila in corpus.iterrows():
        clase = int(fila["intent_class"])
        if clase not in clases:
            seleccionados.append(fila)
            clases.add(clase)
        if len(seleccionados) == max_audios:
            break
    # Los primeros diez conservan la selección de S11: una por intención.
    # Los demás son grabaciones reales distintas, NO copias aumentadas.
    if len(seleccionados) < max_audios:
        usados = {str(x["path"]) for x in seleccionados}
        for _, fila in corpus.iterrows():
            if len(seleccionados) == max_audios:
                break
            identificador = str(fila["path"])
            if identificador not in usados:
                seleccionados.append(fila)
                usados.add(identificador)
    if len(seleccionados) != max_audios:
        raise ValueError(
            f"El corpus auditado contiene menos de {max_audios} voces distintas; "
            f"se pudieron seleccionar {len(seleccionados)}"
        )
    audios, huellas = [], set()
    for n, fila in enumerate(seleccionados, 1):
        contenedor = fila["audio"]
        if not isinstance(contenedor, dict) or not isinstance(contenedor.get("bytes"), (bytes, bytearray)):
            raise ValueError("El audio no está embebido en el Parquet")
        datos = bytes(contenedor["bytes"])
        if not datos.startswith(b"RIFF") or datos[8:12] != b"WAVE":
            raise ValueError("No es WAV auténtico")
        huella = sha256(datos)
        if huella in huellas:
            raise ValueError("Voz duplicada")
        huellas.add(huella)
        ruta = raiz / "raw" / "audios" / f"voz_{n:02d}_fuente.wav"
        guardar_sin_sobrescribir(ruta, datos, huella)
        with sf.SoundFile(io.BytesIO(datos)) as lector:
            tasa = lector.samplerate
            subtipo = lector.subtype
            n_frames = lector.frames
        if not (8000 <= tasa <= 48000 and n_frames >= tasa // 2):
            raise ValueError("Voz corta o frecuencia de muestreo no válida")
        audios.append({
            "original_path": ruta.relative_to(raiz).as_posix(),
            "original_sha256": huella,
            "article_id": None,
            "source_record_id": str(fila["path"]),
            "source_id": str(fila["path"]),
            "source_kind": "PolyAI_MINDS14_es_ES",
            "source_url": PARQUET_VOZ,
            "license": "CC BY 4.0",
            "source_codec": subtipo,
            "source_rate_hz": tasa,
            "transcription_reference": str(fila["transcription"]),
            "intent_class": int(fila["intent_class"]),
        })
    print(f"E · AUDIOS: {len(audios)} voces reales, {len(clases)} intenciones, WAV sin modificar")
    return audios


def transformar_imagenes(raiz: Path, entradas: list[dict], lado: int = 320,
                         perfil: str = "grises") -> list[dict]:
    import numpy as np
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps, UnidentifiedImageError
    if lado not in (160, 320, 640) or perfil not in ("grises", "contraste", "bordes"):
        raise ValueError("Elige lado 160/320/640 y grises/contraste/bordes")
    Image.MAX_IMAGE_PIXELS = 40_000_000
    raiz = Path(raiz)
    salida = []
    t0 = perf_counter()
    for entrada in entradas:
        ruta = raiz / entrada["original_path"]
        if sha256(ruta) != entrada["original_sha256"]:
            raise ValueError("RAW de imagen alterado")
        try:
            with Image.open(ruta) as im:
                im.verify()
            with Image.open(ruta) as im:
                original = ImageOps.exif_transpose(im).convert("RGB")
        except (UnidentifiedImageError, OSError, ValueError) as error:
            raise ValueError("Imagen corrupta o de formato inválido") from error
        ancho, alto = original.size
        if ancho * alto > 40_000_000:
            raise ValueError("Imagen supera el límite seguro de píxeles")
        original.thumbnail((lado, lado), Image.Resampling.LANCZOS)
        if perfil == "grises":
            final = ImageOps.grayscale(original)
        elif perfil == "contraste":
            final = ImageEnhance.Contrast(original).enhance(1.4)
        else:
            final = ImageOps.grayscale(original).filter(ImageFilter.FIND_EDGES)
        grises = np.asarray(ImageOps.grayscale(final), dtype=np.uint8)
        cuentas = np.histogram(grises, bins=8, range=(0, 256))[0].tolist()
        assert sum(cuentas) == grises.size, "Histograma no conserva píxeles"
        buffer = io.BytesIO()
        final.save(buffer, format="PNG")
        datos = buffer.getvalue()
        etiqueta = f"{perfil}_{lado}"
        ruta_der = raiz / "derived" / "imagenes" / f"{entrada['original_sha256'][:16]}_{etiqueta}.png"
        guardar_sin_sobrescribir(ruta_der, datos, sha256(datos))
        metrica = {
            "original_width": ancho, "original_height": alto,
            "width": final.width, "height": final.height,
            "mean_luminance": round(float(grises.mean()), 3),
            "histogram8": cuentas, "bytes_original": ruta.stat().st_size,
            "bytes_derived": len(datos),
        }
        salida.append({**entrada, "modality": "image",
                       "derived_path": ruta_der.relative_to(raiz).as_posix(),
                       "derived_sha256": sha256(datos),
                       "profile": etiqueta, "metrics": metrica})
    print(f"T · IMÁGENES: {len(salida)} derivadas · perfil {perfil} / {lado} px · {perf_counter()-t0:.2f} s")
    return salida


def transformar_audios(raiz: Path, entradas: list[dict],
                       ganancia: float = 1.0, tasa_final: int = 16000) -> list[dict]:
    import numpy as np
    import soundfile as sf
    from scipy.signal import resample_poly
    if ganancia not in (0.5, 1.0, 1.5) or tasa_final != 16000:
        raise ValueError("Ganancia debe ser 0.5, 1.0 o 1.5; salida 16 kHz")
    raiz = Path(raiz)
    salida = []
    t0 = perf_counter()
    for entrada in entradas:
        ruta = raiz / entrada["original_path"]
        if sha256(ruta) != entrada["original_sha256"]:
            raise ValueError("RAW de audio alterado")
        with sf.SoundFile(str(ruta)) as lector:
            fs = lector.samplerate
            muestras = lector.read(dtype="float32", always_2d=True)
        if not 8000 <= fs <= 48000 or len(muestras) < fs // 2 or len(muestras) > fs * 60:
            raise ValueError("Duración o tasa de muestreo fuera de límites")
        mono = np.mean(muestras, axis=1, dtype=np.float32)
        divisor = math.gcd(fs, tasa_final)
        remuestreado = resample_poly(mono, tasa_final // divisor, fs // divisor)
        real = remuestreado.astype(np.float64) * ganancia
        recortes = int(np.count_nonzero(np.abs(real) >= 1.0))
        pcm = np.rint(np.clip(real, -1, 1) * 32767).astype("<i2")
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(tasa_final)
            wav.writeframes(pcm.tobytes())
        datos = buffer.getvalue()
        etiqueta = f"pcm16_{tasa_final}_g{int(ganancia*100)}"
        ruta_der = raiz / "derived" / "audios" / f"{entrada['original_sha256'][:16]}_{etiqueta}.wav"
        guardar_sin_sobrescribir(ruta_der, datos, sha256(datos))
        senal = pcm.astype(np.float64) / 32768
        rms = float(np.sqrt(np.mean(senal * senal)))
        zcr = float(np.mean(np.signbit(senal[:-1]) != np.signbit(senal[1:])))
        segmento = senal[:min(len(senal), tasa_final // 2)]
        espectro = np.abs(np.fft.rfft(segmento * np.hanning(len(segmento))))
        hz = np.fft.rfftfreq(len(segmento), 1 / tasa_final)
        centroide = float(np.sum(hz * espectro) / max(float(np.sum(espectro)), 1e-12))
        metrica = {
            "source_rate_hz": fs, "sample_rate_hz": tasa_final,
            "duration_seconds": round(len(senal) / tasa_final, 3),
            "rms": round(rms, 6), "zero_crossing_rate": round(zcr, 6),
            "spectral_centroid_hz": round(centroide, 2), "clipped_samples": recortes,
            "channels": 1, "pcm_bits": 16,
            "bytes_original": ruta.stat().st_size, "bytes_derived": len(datos),
        }
        salida.append({**entrada, "modality": "audio",
                       "derived_path": ruta_der.relative_to(raiz).as_posix(),
                       "derived_sha256": sha256(datos),
                       "profile": etiqueta, "metrics": metrica})
    print(f"T · AUDIO: {len(salida)} WAV PCM16 mono {tasa_final} Hz · ganancia {ganancia} · {perf_counter()-t0:.2f} s")
    return salida


def cargar_catalogo(raiz: Path, imagenes: list[dict], audios: list[dict],
                    decisiones: dict) -> dict:
    """Un catálogo, dos fuentes. Los audios no reciben article_id inventado."""
    import pandas as pd
    raiz = Path(raiz)
    salida = raiz / "outputs"
    salida.mkdir(parents=True, exist_ok=True)
    if not imagenes or not audios:
        raise ValueError("Se requieren ambas modalidades para el laboratorio completo")
    filas = []
    for item in [*imagenes, *audios]:
        fila = {k: v for k, v in item.items() if k not in ("metrics",)}
        fila.update({
            "schema_version": ESQUEMA,
            "asset_id": item["original_sha256"],
            "status": "ok",
            "metric_name": "mean_luminance" if item["modality"] == "image" else "rms",
            "metric_value": item["metrics"]["mean_luminance" if item["modality"] == "image" else "rms"],
            "metrics_json": json.dumps(item["metrics"], ensure_ascii=False, sort_keys=True),
        })
        filas.append(fila)
    if len({(x["asset_id"], x["profile"]) for x in filas}) != len(filas):
        raise ValueError("Duplicados original/perfil")
    if any(x["article_id"] is not None for x in filas if x["modality"] == "audio"):
        raise ValueError("Las voces MINDS-14 no pertenecen al corpus editorial")
    if any(x["source_record_id"] is not None for x in filas if x["modality"] == "image"):
        raise ValueError("Imagen con identificador falso de voz")
    df = pd.DataFrame(filas)
    (salida / "catalogo.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in filas),
        encoding="utf-8")
    df.to_parquet(salida / "catalogo.parquet", index=False)
    (salida / "decision.json").write_text(json.dumps(decisiones, ensure_ascii=False, indent=2), encoding="utf-8")
    lectura = pd.read_parquet(salida / "catalogo.parquet")
    if len(lectura) != len(filas):
        raise ValueError("Parquet no conserva las filas")
    resumen = {
        "total": len(filas), "imagenes": len(imagenes), "audios": len(audios),
        "articulos": len({x["article_id"] for x in imagenes}),
        "voces": len({x["source_record_id"] for x in audios}),
        "fuentes_cruzadas": 0,
    }
    (salida / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"L · CATÁLOGO: {resumen['total']} filas ({resumen['imagenes']} imágenes + {resumen['audios']} audios)")
    return {"filas": filas, "resumen": resumen, "tabla": df}


def crear_manifiesto(raiz: Path, filas: list[dict]) -> dict:
    raiz = Path(raiz)
    archivos = set()
    for fila in filas:
        archivos.update((fila["original_path"], fila["derived_path"]))
    archivos.update(["outputs/catalogo.jsonl", "outputs/catalogo.parquet",
                     "outputs/decision.json", "outputs/resumen.json"])
    registro = {}
    for rel in sorted(archivos):
        if rel.startswith("/") or ".." in Path(rel).parts:
            raise ValueError("Ruta fuera de la carpeta de trabajo")
        ruta = raiz / rel
        if not ruta.is_file():
            raise FileNotFoundError(ruta)
        registro[rel] = sha256(ruta)
    manifest = {
        "schema": ESQUEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_image": "snapshot_docente_32_imagenes_24_articulos",
        "dataset_audio": "PolyAI/MINDS-14 es-ES, CC BY 4.0",
        "relation_policy": "no_asociar_MINDS14_con_noticias_o_SECOP",
        "rows": len(filas), "images": sum(x["modality"] == "image" for x in filas),
        "audios": sum(x["modality"] == "audio" for x in filas),
        "files": registro,
    }
    (raiz / "manifest_s11.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def verificar(raiz: Path, exigir_completo: bool = True) -> dict:
    import pandas as pd
    raiz = Path(raiz)
    m = json.loads((raiz / "manifest_s11.json").read_text(encoding="utf-8"))
    errores = []
    if m.get("schema") != ESQUEMA:
        errores.append("schema")
    for rel, esperado in m.get("files", {}).items():
        ruta = raiz / rel
        if ".." in Path(rel).parts or not ruta.is_file() or sha256(ruta) != esperado:
            errores.append("archivo:" + rel)
    filas = [json.loads(l) for l in (raiz / "outputs/catalogo.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    tabla = pd.read_parquet(raiz / "outputs/catalogo.parquet")
    if len(filas) != len(tabla) or len(filas) != m["rows"]:
        errores.append("conteos")
    if exigir_completo and (m["images"], m["audios"]) != (32, 10):
        errores.append("lote_incompleto")
    for fila in filas:
        if (sha256(raiz / fila["original_path"]) != fila["original_sha256"]
                or sha256(raiz / fila["derived_path"]) != fila["derived_sha256"]):
            errores.append("activo:" + fila["asset_id"][:12])
        if fila["modality"] == "audio" and fila["article_id"] is not None:
            errores.append("relacion_editorial_falsa")
    return {"ok": not errores, "errores": errores, "filas": len(filas),
            "imagenes": m["images"], "audios": m["audios"]}


def probar_detencion(raiz: Path) -> str:
    """Simula corrupción sobre COPIA temporal; el expediente real permanece intacto."""
    import shutil
    raiz = Path(raiz)
    m = json.loads((raiz / "manifest_s11.json").read_text(encoding="utf-8"))
    primero = next(iter(m["files"]))
    with tempfile.TemporaryDirectory() as d:
        copia = Path(d)
        (copia / "manifest_s11.json").write_bytes((raiz / "manifest_s11.json").read_bytes())
        for rel in m["files"]:
            destino = copia / rel
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(raiz / rel, destino)
        objetivo = copia / primero
        objetivo.write_bytes(objetivo.read_bytes() + b"CORRUPCION_QA")
        resultado = verificar(copia, exigir_completo=False)
        if resultado["ok"] or not any("archivo:" in e for e in resultado["errores"]):
            raise AssertionError("El verificador no detectó el archivo alterado")
    print("QA · CORRUPCIÓN DETECTADA EN COPIA; los originales reales están intactos")
    return "CORRUPCION_DETECTADA"


def empaquetar(raiz: Path) -> Path:
    raiz = Path(raiz)
    control = verificar(raiz)
    if not control["ok"]:
        raise ValueError("No se empaqueta un lote sin verificar: " + repr(control["errores"]))
    m = json.loads((raiz / "manifest_s11.json").read_text(encoding="utf-8"))
    destino = raiz / "expediente_s11_imagenes_audio.zip"
    with zipfile.ZipFile(destino, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for rel in sorted([*m["files"].keys(), "manifest_s11.json"]):
            z.write(raiz / rel, rel)
    with zipfile.ZipFile(destino) as z:
        if z.testzip() is not None:
            raise ValueError("CRC-32 ZIP incorrecto")
    print("ENTREGA · ZIP VERIFICADO:", destino.name, "·", destino.stat().st_size, "bytes")
    return destino


# --- Experimento progresivo S11: no cambia el expediente oficial de 42 filas. ---

def extraer_imagenes_digitos(raiz: Path, max_imagenes: int = 200) -> list[dict]:
    """Imágenes de trazos manuscritos del corpus UCI (test 1797), no noticias.

    La matriz 8×8 contiene intensidades NORMALIZADAS 0–16. Este procedimiento
    materializa el arreglo original como PNG sin pérdida para estudiar ETL.
    NO son fotografías originales de formularios ni de procesos SECOP.
    Fuente: E. Alpaydin & C. Kaynak (1998), UCI doi:10.24432/C50P49,
    disponible vía sklearn.datasets.load_digits; CC BY 4.0 (atribución).
    """
    from sklearn.datasets import load_digits
    from PIL import Image
    import numpy as np

    if not 1 <= max_imagenes <= 1797:
        raise ValueError("max_imagenes debe estar entre 1 y 1797")
    datos = load_digits()
    if len(datos.images) != 1797:
        raise ValueError("La colección de dígitos cambió: revisar fuente")
    raiz = Path(raiz)
    salida = []
    for i in range(max_imagenes):
        raw8 = np.asarray(datos.images[i], dtype=np.float64)
        if raw8.shape != (8, 8) or not np.isfinite(raw8).all():
            raise ValueError("Muestra de escritura inválida")
        pixeles = np.rint(raw8 * 255 / 16).clip(0, 255).astype(np.uint8)
        salida_png = io.BytesIO()
        Image.fromarray(pixeles, mode="L").save(salida_png, format="PNG")
        contenido = salida_png.getvalue()
        ruta = raiz / "raw" / "imagenes_digitos" / f"uci_test_{i:04d}.png"
        esperado = sha256(contenido)
        guardar_sin_sobrescribir(ruta, contenido, esperado)
        salida.append({
            "original_path": ruta.relative_to(raiz).as_posix(),
            "original_sha256": esperado,
            "article_id": None,
            "source_record_id": None,
            "source_id": f"uci_test_{i:04d}",
            "source_kind": "UCI_digits_8x8_normalized_pixels",
            "source_url": "https://doi.org/10.24432/C50P49",
            "credit": "Alpaydin y Kaynak (1998); UCI; sklearn.load_digits",
            "license": "CC BY 4.0",
            "digit_reference": int(datos.target[i]),
            "input_encoding": "PNG 8x8 reconstruido desde matriz UCI 0-16",
        })
    print(f"E · DÍGITOS UCI: {len(salida)} imágenes independientes de trazos manuscritos; NO son noticias")
    return salida


def _fila_escala(item: dict) -> dict:
    """Esquema tabular común sin anidar métricas en Parquet."""
    metrica = item["metrics"]
    clave = "mean_luminance" if item["modality"] == "image" else "rms"
    return {
        **{k: v for k, v in item.items() if k not in ("metrics",)},
        "schema_version": ESQUEMA,
        "asset_id": item["original_sha256"],
        "metric_name": clave,
        "metric_value": metrica[clave],
        "metrics_json": json.dumps(metrica, ensure_ascii=False, sort_keys=True),
        "status": "ok",
    }


def procesar_lotes_escala(raiz: Path, imagenes: list[dict], audios: list[dict],
                         tamano_lote: int = 32, etiqueta: str = "ensayo") -> dict:
    """Procesa POR LOTES reales y guarda particiones, métricas y hashes.

    No carga todos los derivados en RAM ni sobrescribe los outputs oficiales.
    Dos perfiles por imagen (grises/bordes), uno PCM16 por grabación.
    """
    import pandas as pd
    from time import perf_counter
    if tamano_lote not in (8, 16, 32, 64, 128):
        raise ValueError("tamano_lote debe ser 8, 16, 32, 64 o 128")
    if etiqueta not in ("ensayo", "medio", "reto", "qa"):
        raise ValueError("Etiqueta de experimento no admitida")
    if not imagenes or not audios:
        raise ValueError("El reto exige ambas modalidades")
    raiz = Path(raiz)
    lote_id = f"{etiqueta}_i{len(imagenes)}_a{len(audios)}_b{tamano_lote}"
    destino = raiz / "outputs" / "escala" / lote_id
    destino.mkdir(parents=True, exist_ok=True)
    particiones = []
    origenes = {x["original_sha256"]: x for x in [*imagenes, *audios]}
    if len(origenes) != len(imagenes) + len(audios):
        raise ValueError("Orígenes duplicados por SHA-256")
    tareas = []
    for modalidad, origen in [("image", x) for x in imagenes] + [("audio", x) for x in audios]:
        tareas.append((modalidad, origen))
    total = len(tareas)
    print(f"RETO DE ESCALA · {total} RAW distintos; grupos de {tamano_lote} fuentes")
    for inicio in range(0, total, tamano_lote):
        fragmento = tareas[inicio:inicio + tamano_lote]
        im = [x for clase, x in fragmento if clase == "image"]
        au = [x for clase, x in fragmento if clase == "audio"]
        start = perf_counter()
        derivados = []
        if im:
            derivados.extend(transformar_imagenes(raiz, im, lado=160, perfil="grises"))
            derivados.extend(transformar_imagenes(raiz, im, lado=160, perfil="bordes"))
        if au:
            derivados.extend(transformar_audios(raiz, au, ganancia=1.0, tasa_final=16000))
        filas = [_fila_escala(x) for x in derivados]
        secuencia = len(particiones)
        ruta = destino / f"part_{secuencia:04d}.parquet"
        pd.DataFrame(filas).to_parquet(ruta, index=False)
        # Las filas deben reconstruirse desde el archivo, no desde la RAM previa.
        releido = pd.read_parquet(ruta)
        if len(releido) != len(filas):
            raise ValueError("Partición Parquet perdió registros")
        segundos = perf_counter() - start
        part = {
            "name": ruta.name,
            "sha256": sha256(ruta),
            "rows": len(filas),
            "original_sources": len(fragmento),
            "seconds": round(segundos, 6),
            "rows_per_second": round(len(filas) / max(segundos, 1e-6), 2),
            "bytes_raw_referenced": sum((raiz / x["original_path"]).stat().st_size
                                        for _, x in fragmento),
            "bytes_derived": sum((raiz / x["derived_path"]).stat().st_size
                                 for x in derivados),
        }
        particiones.append(part)
        print(f"PARTICIÓN {secuencia + 1:02d} | {part['rows']} derivados | "
              f"{part['seconds']:.3f}s | {part['rows_per_second']} derivados/s")
    fuentes = {x["original_path"]: x["original_sha256"] for x in origenes.values()}
    manifiesto = {
        "schema": "s11-escala-particiones/v1",
        "case": "laura_etl_audio_imagenes",
        "label": etiqueta,
        "batch_size": tamano_lote,
        "total_unique_sources": total,
        "editorial_images": sum(x.get("article_id") is not None for x in imagenes),
        "handwritten_digit_images": sum(x["source_kind"].startswith("UCI_digits") for x in imagenes),
        "real_voices": len(audios),
        "expected_derivatives": len(imagenes) * 2 + len(audios),
        "workers": 1,
        "processing": "secuencial por lotes; NO distribuido",
        "data_policy": "UCI y voces no se asocian con noticias o contratos SECOP",
        "originals": fuentes,
        "partitions": particiones,
    }
    archivo = destino / "escala_manifest.json"
    archivo.write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2), encoding="utf-8")
    control = verificar_lotes_escala(raiz, archivo)
    if not control["ok"]:
        raise ValueError("Lotes de escala fallaron la verificación: " + str(control["errors"][:3]))
    return {
        "manifest_path": archivo,
        "manifest": manifiesto,
        "particiones": pd.DataFrame(particiones),
        "verified": control,
    }


def verificar_lotes_escala(raiz: Path, manifest_path: Path) -> dict:
    """Reabre cada partición y valida identidad, licencias, SHA y cardinalidades."""
    import pandas as pd
    raiz, manifest_path = Path(raiz), Path(manifest_path)
    info = json.loads(manifest_path.read_text(encoding="utf-8"))
    errores = []
    if info.get("schema") != "s11-escala-particiones/v1":
        errores.append("schema")
    if info.get("workers") != 1:
        errores.append("metrica_workers")
    count, seen = 0, set()
    for rel, esperado in info.get("originals", {}).items():
        target = (raiz / rel).resolve()
        if not target.is_relative_to(raiz.resolve()) or not target.is_file() or sha256(target) != esperado:
            errores.append("RAW:" + str(rel))
    for part in info.get("partitions", []):
        path = (manifest_path.parent / part["name"]).resolve()
        if not path.is_relative_to(manifest_path.parent.resolve()):
            errores.append("ruta_particion")
            continue
        if not path.is_file() or sha256(path) != part["sha256"]:
            errores.append("particion:" + part["name"])
            continue
        data = pd.read_parquet(path)
        if len(data) != part["rows"]:
            errores.append("filas:" + part["name"])
        for fila in data.to_dict("records"):
            count += 1
            clave = (str(fila["asset_id"]), str(fila["profile"]))
            if clave in seen:
                errores.append("derivado_duplicado")
            seen.add(clave)
            for k, col in (("original_path", "original_sha256"), ("derived_path", "derived_sha256")):
                target = (raiz / str(fila[k])).resolve()
                if (not target.is_relative_to(raiz.resolve())
                    or not target.is_file() or sha256(target) != fila[col]):
                    errores.append("archivo:" + str(fila[k]))
            if fila["modality"] == "audio" and pd.notna(fila.get("article_id")):
                errores.append("audio_relacionado_con_noticia")
            if str(fila.get("source_kind", "")).startswith("UCI_digits") and pd.notna(fila.get("article_id")):
                errores.append("digito_relacionado_con_noticia")
    if count != info.get("expected_derivatives"):
        errores.append("total_derivados")
    return {"ok": not errores, "errors": errores, "rows": count,
            "partitions": len(info.get("partitions", [])),
            "sources": len(info.get("originals", {}))}


def ejecutar_escala_s11(raiz: Path, modo: str = "ensayo",
                       tamano_lote: int = 32) -> dict:
    """Tres volúmenes medibles. Descarga voces reales una vez y preserva RAW.

    No se ejecuta automáticamente desde el recorrido básico de 42 filas.
    """
    planes = {
        "ensayo": (40, 30),
        "medio": (200, 100),
        "reto": (1000, 400),
    }
    if modo not in planes:
        raise ValueError("Modo no admitido: ensayo / medio / reto")
    digitos_n, voces_n = planes[modo]
    base = extraer_imagenes(raiz, max_imagenes=32)
    digitos = extraer_imagenes_digitos(raiz, digitos_n)
    voces = extraer_audios(raiz, max_audios=voces_n)
    result = procesar_lotes_escala(raiz, [*base, *digitos], voces,
                                  tamano_lote=tamano_lote, etiqueta=modo)
    return result
