#!/usr/bin/env python3
"""S11 · OCR, transcripción real y búsqueda semántica. Datos iniciales simulados."""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / "salidas"
MODELO_TEXTO = "embeddinggemma-2:270m"
MODELO_IMAGEN = "embeddinggemma-2:440m"
OLLAMA_URL = "http://127.0.0.1:11434/api/embed"

def hash_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def guardar_json(nombre: str, data: dict) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / nombre
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Guardado: {p.relative_to(BASE)}")
    return p

def cargar_json(nombre: str) -> dict:
    p = OUT / nombre
    if not p.is_file():
        raise FileNotFoundError(f"Falta {p}. Ejecuta los pasos previos.")
    return json.loads(p.read_text(encoding="utf-8"))

def preparar() -> None:
    """Genera una fotografía textual ficticia y voz sintética local (NO noticia real)."""
    from PIL import Image, ImageDraw, ImageFont
    OUT.mkdir(parents=True, exist_ok=True)
    png = OUT / "afiche_simulado.png"
    img = Image.new("RGB", (1300, 560), "white")
    draw = ImageDraw.Draw(img)
    fuente = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 47)
    campos = [
        "SIMULACION PEDAGOGICA", "ENTIDAD: COMPRAS CLARAS", "CONTRATOS: 12",
        "VALOR: 320 MILLONES", "FECHA: 10-11-2026",
    ]
    for i, linea in enumerate(campos):
        draw.text((40, 35 + 102 * i), linea, fill="black", font=fuente)
    img.save(png)
    wav = OUT / "voz_simulada.wav"
    frase = ("Esta es una grabación sintética para practicar transcripción. "
             "La entidad de ejemplo registró doce contratos. "
             "El valor declarado fue de trescientos veinte millones.")
    subprocess.run(["espeak-ng", "-v", "es", "-s", "125", "-w", str(wav), frase], check=True)
    guardar_json("origen.json", {
        "tipo": "simulacion_pedagogica",
        "aviso": "Frases e importes inventados; no corresponden a noticias reales.",
        "archivos": [
            {"archivo": png.name, "sha256": hash_sha256(png), "generador": "Pillow"},
            {"archivo": wav.name, "sha256": hash_sha256(wav), "generador": "espeak-ng"}
        ]
    })
    print("Datos locales preparados: ninguna noticia ni audio editorial descargado.")

def ocr(archivo: Path | None) -> None:
    import pytesseract
    from PIL import Image
    path = (archivo or OUT / "afiche_simulado.png").expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"No existe {path}; usa preparar o --archivo.")
    with Image.open(path) as im:
        texto = pytesseract.image_to_string(im, lang="spa", config="--psm 6").strip()
    guardar_json("ocr.json", {
        "tarea": "OCR (reconocimiento óptico de caracteres)",
        "fuente": str(path), "sha256": hash_sha256(path),
        "texto_extraido": texto, "motor": "Tesseract spa",
        "limite": "Texto probable: verificar contra imagen; no demuestra veracidad."
    })
    print("OCR:\n", texto or "[sin texto recuperado]")

def asr(archivo: Path | None) -> None:
    from faster_whisper import WhisperModel
    path = (archivo or OUT / "voz_simulada.wav").expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"No existe {path}; usa preparar o --archivo.")
    print("Whisper tiny CPU (primera ejecución descarga modelo).")
    modelo = WhisperModel("tiny", device="cpu", compute_type="int8", cpu_threads=2)
    segmentos, info = modelo.transcribe(
        str(path), language="es", beam_size=1,
        vad_filter=False, condition_on_previous_text=False,
    )
    filas = [
        {"inicio_s": round(s.start, 2), "fin_s": round(s.end, 2), "texto": s.text.strip()}
        for s in segmentos
    ]
    texto = " ".join(s["texto"] for s in filas).strip()
    guardar_json("asr.json", {
        "tarea": "ASR (reconocimiento automático del habla)",
        "fuente": str(path), "sha256": hash_sha256(path),
        "duracion_s": round(info.duration, 2), "idioma_forzado": "es",
        "modelo": "faster-whisper tiny/int8/CPU",
        "transcripcion": texto, "segmentos": filas,
        "limite": "Sin referencia humana no se conoce WER; comprobar palabras contra audio."
    })
    print("TRANSCRIPCIÓN:\n", texto or "[sin voz recuperada]")

def incrustar(inputs: list[str | dict], modelo: str) -> list[list[float]]:
    import requests
    try:
        r = requests.post(OLLAMA_URL, json={"model": modelo, "input": inputs}, timeout=300)
        r.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError("Ollama no disponible. Desde la raíz ejecuta "
                           "bash Laboratorios/S11_Codespaces/iniciar_ollama.sh. "
                           f"Detalle: {e}") from e
    vectors = r.json().get("embeddings", [])
    if len(vectors) != len(inputs) or not all(v and len(v) == len(vectors[0]) for v in vectors):
        raise ValueError("Ollama devolvió cantidad o dimensión de vectores inesperada.")
    return vectors

def coseno(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("No se comparan embeddings de distinta dimensión.")
    numerator = sum(x * y for x, y in zip(a, b))
    norma_a = math.sqrt(sum(x * x for x in a))
    norma_b = math.sqrt(sum(x * x for x in b))
    return numerator / (norma_a * norma_b) if norma_a and norma_b else 0.0

def indexar() -> None:
    imagen, voz = cargar_json("ocr.json"), cargar_json("asr.json")
    docs = [
        {"id": "foto_ocr", "titulo": "Texto extraído de una imagen",
         "texto": imagen["texto_extraido"], "fuente": imagen["fuente"], "sha256": imagen["sha256"]},
        {"id": "voz_asr", "titulo": "Transcripción de una grabación",
         "texto": voz["transcripcion"], "fuente": voz["fuente"], "sha256": voz["sha256"]},
    ]
    entradas = [f"title: {d['titulo']} | text: {d['texto']}" for d in docs]
    vectores = incrustar(entradas, MODELO_TEXTO)
    for doc, v in zip(docs, vectores):
        doc["embedding"] = v
    guardar_json("indice.json", {
        "modelo": MODELO_TEXTO, "dimension": len(vectores[0]), "documentos": docs,
        "nota": "Índice JSON didáctico. Producción requiere seguridad y vector DB."
    })
    print(f"Indexadas {len(docs)} evidencias de {len(vectores[0])} dimensiones.")

def buscar(consulta: str) -> None:
    if not consulta.strip():
        raise ValueError("Consulta vacía.")
    indice = cargar_json("indice.json")
    q = incrustar([f"task: search result | query: {consulta}"], indice["modelo"])[0]
    if len(q) != indice["dimension"]:
        raise ValueError("Cambió dimensión: recrea índice.")
    ranking = sorted(indice["documentos"], key=lambda d: -coseno(q, d["embedding"]))
    for pos, doc in enumerate(ranking, 1):
        print(f"{pos}. {doc['titulo']} | similitud {coseno(q, doc['embedding']):.4f}")
        print(f"   Fuente: {doc['fuente']} | SHA-256: {doc['sha256'][:14]}…")
        print(f"   Fragmento: {doc['texto'][:170]}")
    print("La similitud relativa NO comprueba veracidad de fuentes.")

def imagen_semantica(consulta: str, archivo: Path | None) -> None:
    path = (archivo or OUT / "afiche_simulado.png").expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"No existe {path}")
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    vec_imagen, vec_q = incrustar(
        [{"image": b64}, f"task: search result | query: {consulta}"], MODELO_IMAGEN,
    )
    print(f"Similitud imagen-consulta: {coseno(vec_imagen, vec_q):.4f}")
    print("Imagen sin OCR: comparar significado visual, NO exactitud de cifras.")

def fuentes_repo(imagenes: int, audios: int) -> None:
    """Usa el motor de S11 y los dos corpus auditados ya presentes en el curso."""
    import sys
    raiz_repo = BASE.parents[1]
    if str(raiz_repo) not in sys.path:
        sys.path.insert(0, str(raiz_repo))
    from utils import s11_etl_core as core
    raiz = OUT / "fuentes_repositorio"
    entradas_img = core.extraer_imagenes(raiz, max_imagenes=imagenes)
    entradas_voz = core.extraer_audios(raiz, max_audios=audios)
    entradas = entradas_img + entradas_voz
    guardar_json("fuentes_repo.json", {
        "schema": "s11-repositorio-ocr-asr-v1",
        "registros": entradas,
        "imagenes": imagenes,
        "audios": audios,
        "advertencias": [
            "Fotografías editoriales: no redistribuir; respetar créditos y fuente.",
            "MINDS-14 son audios bancarios independientes, no audios de noticias.",
            "No unir article_id y source_record_id sin documentación explícita."
        ]
    })
    print("\nFuentes listas. Ejecuta uno de los comandos siguientes:")
    print(f"python lab.py ocr --archivo {raiz / entradas_img[0]['original_path']}")
    print(f"python lab.py asr --archivo {raiz / entradas_voz[0]['original_path']}")
    print("Después ejecuta: python lab.py indexar y python lab.py buscar --consulta 'tu consulta'.")

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="accion", required=True)
    sub.add_parser("preparar")
    for nombre in ("ocr", "asr"):
        cmd = sub.add_parser(nombre)
        cmd.add_argument("--archivo", type=Path)
    fuentes = sub.add_parser("fuentes-repo")
    fuentes.add_argument("--imagenes", type=int, default=2, choices=range(1, 33), metavar="1..32")
    fuentes.add_argument("--audios", type=int, default=2, choices=range(1, 11), metavar="1..10")
    sub.add_parser("indexar")
    bus = sub.add_parser("buscar")
    bus.add_argument("--consulta", required=True)
    img = sub.add_parser("imagen")
    img.add_argument("--consulta", required=True)
    img.add_argument("--archivo", type=Path)
    a = p.parse_args()
    try:
        if a.accion == "preparar": preparar()
        elif a.accion == "ocr": ocr(a.archivo)
        elif a.accion == "asr": asr(a.archivo)
        elif a.accion == "fuentes-repo": fuentes_repo(a.imagenes, a.audios)
        elif a.accion == "indexar": indexar()
        elif a.accion == "buscar": buscar(a.consulta)
        elif a.accion == "imagen": imagen_semantica(a.consulta, a.archivo)
    except (FileNotFoundError, RuntimeError, ValueError, subprocess.CalledProcessError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
