#!/usr/bin/env python3
"""S11 · motor ETL reutilizable. CLI: iniciar → plan → procesar → indexar → buscar → auditar.

No descarga documentos ajenos; consume únicamente archivos que aporta la persona.
Diseño didáctico: cada etapa es una función reemplazable y las salidas son auditables.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}
AUDIO_EXT = {".wav", ".mp3", ".ogg", ".flac", ".m4a"}
TEXT_EXT = {".txt", ".md"}
PDF_EXT = {".pdf"}
EXT = IMAGE_EXT | AUDIO_EXT | TEXT_EXT | PDF_EXT
MAX_BYTES = 80_000_000
MAX_PIXELS = 40_000_000

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()

def escribir_json(p: Path, data: object) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")

def cargar_config(p: Path) -> dict:
    d = json.loads(p.read_text(encoding="utf-8"))
    for k in ("version", "proyecto", "fuente", "ocr", "asr", "embeddings", "limites"):
        if k not in d:
            raise ValueError(f"Configuración incompleta: {k}")
    if d["version"] != 1:
        raise ValueError("Versión de configuración no compatible (esperada: 1)")
    if not isinstance(d["fuente"], dict) or not d["fuente"].get("nombre"):
        raise ValueError("Falta fuente.nombre")
    modelo = d["asr"].get("modelo", "tiny")
    if modelo not in ("tiny", "base", "small"):
        raise ValueError("Modelo ASR fuera de las opciones didácticas: tiny/base/small")
    if int(d["ocr"].get("psm", 6)) not in (3, 4, 6, 11):
        raise ValueError("psm permitido: 3, 4, 6, 11")
    if int(d["limites"].get("archivos_maximos", 30)) not in range(1, 201):
        raise ValueError("archivos_maximos: entre 1 y 200")
    if int(d["limites"].get("paginas_pdf", 3)) not in range(1, 21):
        raise ValueError("paginas_pdf: entre 1 y 20")
    if not isinstance(d["embeddings"].get("modelo"), str) or not d["embeddings"]["modelo"].strip():
        raise ValueError("Falta embeddings.modelo")
    return d

def crear_proyecto(raiz: Path) -> None:
    if (raiz / "config.json").exists():
        raise FileExistsError(f"Ya existe {raiz / 'config.json'}; no se sobrescribe")
    for carpeta in ("entradas/imagenes", "entradas/audios", "entradas/documentos", "entradas/textos", "salidas"):
        (raiz / carpeta).mkdir(parents=True, exist_ok=True)
    escribir_json(raiz / "config.json", {
        "version": 1, "proyecto": raiz.name,
        "fuente": {
            "nombre": "archivos_aportados_por_usuario",
            "credito": "autor_pendiente_de_verificar",
            "licencia": "verificar_antes_de_compartir"
        },
        "ocr": {"activo": True, "idioma": "spa", "psm": 6},
        "asr": {"activo": True, "idioma": "es", "modelo": "tiny", "beam_size": 1},
        "embeddings": {"modelo": "embeddinggemma-2:270m", "ollama_url": "http://127.0.0.1:11434/api/embed", "lote": 8},
        "limites": {"archivos_maximos": 30, "paginas_pdf": 3, "caracteres_por_fragmento": 700}
    })
    escribir_json(raiz / "metadatos.example.json", {
        "entradas/imagenes/ejemplo.png": {
            "nombre": "fuente_original_verificada",
            "credito": "autor_real",
            "licencia": "condicion_de_uso_verificada"
        }
    })
    print(f"Proyecto creado: {raiz}\n1. Copia archivos autorizados en entradas/\n2. Edita config.json\n3. Ejecuta plan y procesar.")

def inventario(raiz: Path, cfg: dict) -> list[Path]:
    entradas = raiz / "entradas"
    if not entradas.is_dir():
        raise FileNotFoundError(f"No existe {entradas}")
    files = []
    for p in sorted(entradas.rglob("*")):
        if p.is_symlink():
            raise ValueError(f"No se admiten enlaces simbólicos: {p}")
        if p.is_file() and p.suffix.lower() in EXT:
            if p.stat().st_size > MAX_BYTES:
                raise ValueError(f"Supera 80 MB: {p.name}")
            files.append(p)
    if len(files) > int(cfg["limites"]["archivos_maximos"]):
        raise ValueError("Exceso de archivos: aumenta limites.archivos_maximos o reduce el lote")
    return files

def plan(raiz: Path, cfg: dict) -> list[Path]:
    files = inventario(raiz, cfg)
    if not files:
        print("Sin archivos válidos. Copia PNG/JPG/TIFF, WAV/MP3, PDF o TXT en entradas/.")
    for p in files:
        clase = ("imagen" if p.suffix.lower() in IMAGE_EXT else
                 "audio" if p.suffix.lower() in AUDIO_EXT else
                 "pdf" if p.suffix.lower() in PDF_EXT else "texto")
        print(f"{clase:7} | {p.stat().st_size:>9} bytes | {p.relative_to(raiz).as_posix()}")
    print(f"Total: {len(files)} archivo(s). Plan no ejecuta modelos ni modifica originales.")
    return files

def _ocr_imagen(p: Path, cfg: dict) -> str:
    import pytesseract
    from PIL import Image, ImageOps
    Image.MAX_IMAGE_PIXELS = MAX_PIXELS
    with Image.open(p) as im:
        if im.width * im.height > MAX_PIXELS:
            raise ValueError("Imagen excede 40 millones de píxeles")
        img = ImageOps.exif_transpose(im).convert("RGB")
        return pytesseract.image_to_string(img, lang=cfg["ocr"]["idioma"],
                                          config=f'--psm {int(cfg["ocr"]["psm"])}').strip()

def _ocr_pdf(p: Path, cfg: dict) -> tuple[str, int]:
    with tempfile.TemporaryDirectory(prefix="s11-pdf-") as temp:
        destino = Path(temp) / "pagina"
        paginas = int(cfg["limites"]["paginas_pdf"])
        subprocess.run(
            ["pdftoppm", "-f", "1", "-l", str(paginas), "-scale-to", "1600", "-png",
             str(p), str(destino)], check=True, capture_output=True, timeout=150
        )
        page_files = sorted(Path(temp).glob("pagina-*.png"))
        if not page_files:
            raise ValueError("PDF sin páginas rasterizables")
        textos = [f"[PÁGINA {n}]\n{_ocr_imagen(pp, cfg)}"
                  for n, pp in enumerate(page_files, start=1)]
        return "\n\n".join(textos), len(page_files)

def _asr(p: Path, cfg: dict, modelo) -> tuple[str, list[dict]]:
    segmentos, info = modelo.transcribe(
        str(p), language=cfg["asr"]["idioma"],
        beam_size=int(cfg["asr"].get("beam_size", 1)),
        vad_filter=False, condition_on_previous_text=False
    )
    filas = [{"inicio_s": round(float(s.start), 3), "fin_s": round(float(s.end), 3),
              "texto": s.text.strip()} for s in segmentos if s.text.strip()]
    return " ".join(x["texto"] for x in filas), filas

def ejecutar(raiz: Path, cfg: dict) -> None:
    files = inventario(raiz, cfg)
    if not files:
        raise ValueError("No hay archivos para procesar")
    out = raiz / "salidas"
    out.mkdir(parents=True, exist_ok=True)
    asr_model = None
    meta_path = raiz / "metadatos.json"
    metadatos = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    if not isinstance(metadatos, dict):
        raise ValueError("metadatos.json debe contener un objeto: ruta -> fuente/crédito/licencia")
    filas, errores = [], []
    for p in files:
        tipo = ("imagen" if p.suffix.lower() in IMAGE_EXT else
                "audio" if p.suffix.lower() in AUDIO_EXT else
                "pdf" if p.suffix.lower() in PDF_EXT else "texto")
        rel = p.relative_to(raiz).as_posix()
        metadata_archivo = metadatos.get(rel, {})
        if not isinstance(metadata_archivo, dict):
            raise ValueError(f"Metadatos inválidos para {rel}")
        datos_fuente = {**cfg["fuente"], **metadata_archivo}
        if not datos_fuente.get("nombre"):
            raise ValueError(f"Nombre de fuente vacío para {rel}")
        try:
            texto, segments, paginas = "", [], None
            if tipo == "imagen" and cfg["ocr"]["activo"]:
                texto = _ocr_imagen(p, cfg)
            elif tipo == "pdf" and cfg["ocr"]["activo"]:
                texto, paginas = _ocr_pdf(p, cfg)
            elif tipo == "audio" and cfg["asr"]["activo"]:
                if asr_model is None:
                    from faster_whisper import WhisperModel
                    asr_model = WhisperModel(cfg["asr"]["modelo"], device="cpu",
                                            compute_type="int8", cpu_threads=2)
                texto, segments = _asr(p, cfg, asr_model)
            elif tipo == "texto":
                texto = p.read_text(encoding="utf-8-sig")
            filas.append({
                "asset_id": hashlib.sha256(rel.encode()).hexdigest()[:16],
                "path": rel, "tipo": tipo, "size_bytes": p.stat().st_size,
                "sha256": sha256(p), "source_name": datos_fuente["nombre"],
                "credit": datos_fuente.get("credito"),
                "license": datos_fuente.get("licencia"),
                "text_origin": "tesseract" if tipo in ("pdf", "imagen") else
                               "whisper" if tipo == "audio" else "texto_usuario",
                "extracted_text": texto, "segments": segments, "pages_processed": paginas
            })
            print(f"OK {tipo:6} {rel} | caracteres: {len(texto)}")
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as e:
            errores.append({"path": rel, "tipo": tipo, "error": str(e)})
            print(f"ERROR {rel}: {e}", file=sys.stderr)
    with (out / "catalogo.jsonl").open("w", encoding="utf-8") as f:
        for item in filas:
            f.write(json.dumps(item, ensure_ascii=False, allow_nan=False) + "\n")
    # Parquet con PyArrow directo: evita registrar dos veces pandas.period en CI.
    # JSONL conserva segmentos temporales y se considera el registro canónico.
    import pyarrow as pa
    import pyarrow.parquet as pq
    resumen = [{k: v for k, v in item.items() if k != "segments"} for item in filas]
    if resumen:
        tabla = pa.Table.from_pylist(resumen)
        pq.write_table(tabla, out / "catalogo.parquet")
    elif (out / "catalogo.parquet").exists():
        (out / "catalogo.parquet").unlink()
    escribir_json(out / "errores.json", {"errores": errores, "cantidad": len(errores)})
    escribir_json(out / "manifest.json", {
        "version": 1, "proyecto": cfg["proyecto"],
        "fuente": cfg["fuente"], "documentos_ok": len(filas), "documentos_error": len(errores),
        "generado_utc": datetime.now(timezone.utc).isoformat(),
        "archivos": [{"path": x["path"], "sha256": x["sha256"]} for x in filas],
        "sha256_catalogo": sha256(out / "catalogo.jsonl"),
        "nota": "Los contenidos procesados son hipótesis y no certificaciones de hechos."
    })
    print(f"\nResultado: {len(filas)} OK, {len(errores)} con error. Salidas: {out}")
    if errores:
        raise RuntimeError("Proceso parcial: inspecciona salidas/errores.json")

def leer_filas(raiz: Path) -> list[dict]:
    p = raiz / "salidas" / "catalogo.jsonl"
    if not p.is_file():
        raise FileNotFoundError("No existe catalogo.jsonl: ejecuta procesar")
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]

def fragmentar(fila: dict, max_chars: int) -> list[dict]:
    """Divide texto en fragmentos y conserva segundos o página de procedencia."""
    base = {k: fila[k] for k in ("asset_id", "path", "tipo", "sha256", "source_name")}
    fragmentos = []
    unidades = fila.get("segments") if fila.get("tipo") == "audio" and fila.get("segments") else [
        {"texto": fila.get("extracted_text", "")}
    ]
    for n, u in enumerate(unidades):
        texto = u["texto"].strip()
        # El troceo tiene costo pedagógico: palabras muy largas pueden cruzar fronteras.
        for pos in range(0, len(texto), max_chars):
            pedazo = texto[pos:pos + max_chars].strip()
            if pedazo:
                frag = {**base, "fragmento_id": f"{fila['asset_id']}-{n}-{pos}",
                        "texto": pedazo, "titulo": Path(fila["path"]).name}
                for k in ("inicio_s", "fin_s"):
                    if k in u:
                        frag[k] = u[k]
                fragmentos.append(frag)
    return fragmentos

def _embed(entradas: list[str], cfg: dict) -> list[list[float]]:
    import requests
    url = cfg["embeddings"]["ollama_url"]
    if not url.startswith(("http://127.0.0.1:", "http://localhost:")):
        raise ValueError("Por seguridad la clase solo acepta Ollama local")
    r = requests.post(url, json={"model": cfg["embeddings"]["modelo"],
                                  "input": entradas}, timeout=300)
    r.raise_for_status()
    embeddings = r.json().get("embeddings", [])
    if len(embeddings) != len(entradas) or not embeddings:
        raise ValueError("Respuesta de Ollama incompleta")
    dim = len(embeddings[0])
    if dim == 0 or any(len(x) != dim for x in embeddings):
        raise ValueError("Dimensiones inconsistentes del modelo")
    return embeddings

def indexar(raiz: Path, cfg: dict) -> None:
    filas = leer_filas(raiz)
    max_chars = int(cfg["limites"]["caracteres_por_fragmento"])
    if not 100 <= max_chars <= 4000:
        raise ValueError("caracteres_por_fragmento: 100 a 4000")
    docs = [frag for fila in filas for frag in fragmentar(fila, max_chars)]
    if not docs:
        raise ValueError("No hay texto OCR/ASR/documentos para indexar")
    entrada = [f"title: {d['titulo']} | text: {d['texto']}" for d in docs]
    batch = int(cfg["embeddings"].get("lote", 8))
    if not 1 <= batch <= 32:
        raise ValueError("embeddings.lote: entre 1 y 32")
    vectores = []
    for i in range(0, len(entrada), batch):
        vectores.extend(_embed(entrada[i:i+batch], cfg))
        print(f"Vectores: {len(vectores)}/{len(docs)}")
    dim = len(vectores[0])
    if any(len(v) != dim for v in vectores):
        raise ValueError("Dimensiones cambiaron durante el índice")
    for frag, vector in zip(docs, vectores):
        frag["embedding"] = vector
    escribir_json(raiz / "salidas" / "indice.json", {
        "modelo": cfg["embeddings"]["modelo"], "dim": dim, "docs": docs,
        "sha256_catalogo": sha256(raiz / "salidas" / "catalogo.jsonl")
    })
    print(f"Índice listo: {len(docs)} fragmentos x {dim} dimensiones")

def coseno(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("No compares diferentes dimensiones")
    num = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    return num / (na*nb) if na > 0 and nb > 0 else 0.0

def buscar(raiz: Path, cfg: dict, consulta: str, topk: int) -> list[dict]:
    p = raiz / "salidas" / "indice.json"
    idx = json.loads(p.read_text(encoding="utf-8"))
    if idx["modelo"] != cfg["embeddings"]["modelo"]:
        raise ValueError("Modelo cambiado: reconstruye índice")
    if idx["sha256_catalogo"] != sha256(raiz / "salidas" / "catalogo.jsonl"):
        raise ValueError("Catálogo cambió: vuelve a indexar")
    vector = _embed([f"task: search result | query: {consulta}"], cfg)[0]
    if len(vector) != idx["dim"]:
        raise ValueError("Consulta y documentos con distinta dimensión")
    respuestas = sorted(
        [{"similitud_coseno": round(coseno(vector, d["embedding"]), 5),
          **{k: v for k, v in d.items() if k != "embedding"}} for d in idx["docs"]],
        key=lambda d: -d["similitud_coseno"]
    )[:topk]
    for n, d in enumerate(respuestas, 1):
        print(f"{n}. {d['similitud_coseno']:.4f} [{d['tipo']}] {d['path']}\n"
              f"   {d['texto'][:180]} | sha256: {d['sha256'][:16]}…")
    escribir_json(raiz / "salidas" / "ultima_busqueda.json", {
        "consulta": consulta, "modelo": idx["modelo"], "resultados": respuestas,
        "limitacion": "Similitud semántica no implica veracidad ni calidad de OCR/ASR"
    })
    return respuestas

def auditar(raiz: Path) -> bool:
    p = raiz / "salidas" / "manifest.json"
    m = json.loads(p.read_text(encoding="utf-8"))
    errores = []
    for fila in m["archivos"]:
        f = raiz / fila["path"]
        if not f.is_file() or sha256(f) != fila["sha256"]:
            errores.append(fila["path"])
    if sha256(raiz / "salidas" / "catalogo.jsonl") != m["sha256_catalogo"]:
        errores.append("salidas/catalogo.jsonl")
    if errores:
        print("Integridad NO validada:", errores)
        return False
    print(f"Integridad OK: {len(m['archivos'])} fuentes y catálogo, sin validar veracidad.")
    return True

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="accion", required=True)
    ini = sub.add_parser("iniciar", help="Crear plantilla de proyecto, sin sobrescribir")
    ini.add_argument("--destino", type=Path, required=True)
    for cmd in ("plan", "procesar", "indexar", "auditar"):
        sub.add_parser(cmd).add_argument("--config", type=Path, required=True)
    bus = sub.add_parser("buscar")
    bus.add_argument("--config", type=Path, required=True)
    bus.add_argument("--consulta", required=True)
    bus.add_argument("--topk", type=int, default=5)
    args = parser.parse_args()
    try:
        if args.accion == "iniciar":
            crear_proyecto(args.destino.resolve())
            return
        cfg_path = args.config.expanduser().resolve()
        raiz = cfg_path.parent
        if not raiz.is_dir():
            raise FileNotFoundError(raiz)
        cfg = cargar_config(cfg_path)
        if args.accion == "plan":
            plan(raiz, cfg)
        elif args.accion == "procesar":
            ejecutar(raiz, cfg)
        elif args.accion == "indexar":
            indexar(raiz, cfg)
        elif args.accion == "buscar":
            if not 1 <= args.topk <= 50:
                raise ValueError("topk: 1 a 50")
            if not args.consulta.strip():
                raise ValueError("Consulta vacía")
            buscar(raiz, cfg, args.consulta, args.topk)
        elif args.accion == "auditar" and not auditar(raiz):
            sys.exit(2)
    except (FileNotFoundError, FileExistsError, ValueError, OSError,
            RuntimeError, subprocess.SubprocessError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
