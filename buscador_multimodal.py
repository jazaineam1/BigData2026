"""Búsqueda semántica de evidencia MULTIMODAL de S11.

Embeddings recuperan candidatos; NO redactan hechos ni interpretan píxeles solos.
OCR, texto PDF y ASR proporcionan los textos y las citas rastreables.
No hay descargas ni inferencias automáticas al importar este módulo.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
CATALOGO = OUT / "evidencias_multimodales.json"
INDICE = OUT / "indice_evidencias_440m.json"
MODELO = "embeddinggemma-2:440m"
API = "http://127.0.0.1:11434/api/embed"


def huella(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def guardar_json(path: Path, payload: object) -> None:
    """Escritura atómica: una interrupción no rompe un índice anterior."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def leer_json(path: Path) -> object:
    if not path.is_file():
        raise FileNotFoundError(f"No existe {path}. Ejecuta primero 'preparar'.")
    return json.loads(path.read_text(encoding="utf-8"))


def trozos(text: str, ancho: int = 850, solape: int = 110) -> list[str]:
    """Fragmentos de texto OCR/ASR para no perder pasajes al indexar."""
    if not 100 <= ancho <= 3000 or not 0 <= solape < ancho:
        raise ValueError("Tamaño/solape de fragmentos inválidos")
    limpio = text.strip()
    if not limpio:
        return []
    partes = []
    inicio = 0
    while inicio < len(limpio):
        fin = min(inicio + ancho, len(limpio))
        if fin < len(limpio):
            corte = limpio.rfind(" ", inicio + ancho // 2, fin)
            if corte > inicio:
                fin = corte
        partes.append(limpio[inicio:fin].strip())
        if fin >= len(limpio):
            break
        inicio = max(inicio + 1, fin - solape)
    return [p for p in partes if p]


def coseno(a: list[float], b: list[float]) -> float:
    if not a or len(a) != len(b):
        raise ValueError("Vectores incompatibles")
    x = math.sqrt(sum(v * v for v in a))
    y = math.sqrt(sum(v * v for v in b))
    if not x or not y:
        raise ValueError("Vector de norma cero")
    return sum(xi * yi for xi, yi in zip(a, b)) / (x * y)


def incrustar(entrada: str | dict, modelo: str = MODELO) -> list[float]:
    """Llamada real solo por acción explícita. input SIEMPRE es lista."""
    import requests
    try:
        r = requests.post(API, json={"model": modelo, "input": [entrada]}, timeout=240)
    except requests.RequestException as e:
        raise RuntimeError("Ollama no responde: usa bash preparar_embeddinggemma.sh") from e
    if not r.ok:
        raise RuntimeError(f"Ollama HTTP {r.status_code}: {r.text[:900]}")
    emb = r.json().get("embeddings", [])
    if len(emb) != 1 or len(emb[0]) != 768:
        raise ValueError("La API no devolvió un vector de 768 componentes")
    return emb[0]


def extraer_pdf(path: Path, paginas: int = 1, hacer_ocr: bool = False) -> list[dict]:
    """Todas las páginas si paginas=0; nunca atribuir OCR al PDF sin ejecutarlo."""
    from ocr_documental import pdf_paginas, texto_integrado_pdf, renderizar_pagina
    total = pdf_paginas(path)
    max_p = total if paginas == 0 else min(total, paginas)
    rows = []
    for page in range(1, max_p + 1):
        text = texto_integrado_pdf(path, page)
        method = "texto_integrado_pdf" if text else "sin_texto"
        if len(text.strip()) < 35 and hacer_ocr:
            import pytesseract
            from PIL import Image
            raw = renderizar_pagina(str(path), page)
            with Image.open(io.BytesIO(raw)) as img:
                text = pytesseract.image_to_string(img, lang="spa", config="--psm 3")
            method = "tesseract_ocr_psm3"
        rows.append({"pagina": page, "texto": text, "metodo": method,
                     "pendiente": not bool(text.strip()), "total_paginas": total})
    return rows


def extraer_foto(path: Path, hacer_ocr: bool = False) -> dict:
    text = ""
    if hacer_ocr:
        import pytesseract
        from PIL import Image
        with Image.open(path) as img:
            text = pytesseract.image_to_string(img, lang="spa", config="--psm 11")
    return {"texto": text, "metodo": "tesseract_ocr_psm11" if hacer_ocr else "pendiente",
            "pendiente": not hacer_ocr}


def transcribir_voz(path: Path, modelo=None) -> list[dict]:
    """Whisper real: debe ejecutarse explícitamente y muestra sus segmentos."""
    if modelo is None:
        from faster_whisper import WhisperModel
        modelo = WhisperModel("tiny", device="cpu", compute_type="int8", cpu_threads=2)
    segmentos, _ = modelo.transcribe(str(path), language="es", beam_size=2)
    return [{"inicio_s": round(s.start, 2), "fin_s": round(s.end, 2),
             "texto": s.text.strip()} for s in segmentos]


def preparar(*, n_fotos: int = 4, n_actas: int = 1, n_audios: int = 1,
             paginas: int = 1, hacer_ocr: bool = False, hacer_asr: bool = False) -> list[dict]:
    """Extraer primero; indexar DESPUÉS por elección explícita."""
    from fuentes import (ROOT as root, inventario, seleccionar_fotos_muestra)
    if not (0 <= n_fotos <= 62 and 0 <= n_actas <= 30 and 0 <= n_audios <= 30):
        raise ValueError("Los límites superan el corpus del laboratorio")
    if paginas < 0:
        raise ValueError("Usa paginas=0 para todas, o 1,2,...")
    records = []
    items = inventario()
    fotos = [x for x in items if x["clase"] == "imagen"]
    seleccion = seleccionar_fotos_muestra([x["original"] for x in fotos], 62)[:n_fotos]
    metadatos = {str(x["original"]): x for x in fotos}
    for foto in seleccion:
        meta = metadatos[str(foto)]
        info = extraer_foto(foto, hacer_ocr)
        records.append({"id": "imagen:" + foto.name, "modalidad": "imagen",
                        "fuente": str(foto.relative_to(root)), "sha256": huella(foto),
                        "credito": meta["credito"], "url_fuente": meta.get("url", ""),
                        "texto": info["texto"], "origen_texto": info["metodo"],
                        "ocr_pendiente": info["pendiente"],
                        "pagina": None, "segmentos": [], "referencia_humana": ""})
    docs = [x for x in items if x["clase"] == "pdf"]
    docs.sort(key=lambda x: (x["original"].name != "secop_acta_728704921.pdf",
                             x["original"].name))
    for x in docs[:n_actas]:
        path = x["original"]
        for page in extraer_pdf(path, paginas, hacer_ocr):
            # Vista visual disponible de la primera página, si existe.
            # Los PNG derivados no se cuentan como nuevos contratos.
            preview = root / "datos/raw/actas" / (
                path.stem + "_pagina" + str(page["pagina"]) + ".png")
            vista = str(preview.relative_to(root)) if preview.is_file() else ""
            sha_vista = huella(preview) if preview.is_file() else ""
            records.append({"id": "contrato:" + path.name + ":p" + str(page["pagina"]),
                            "modalidad": "contrato", "fuente": str(path.relative_to(root)),
                            "sha256": huella(path), "credito": x["credito"], "url_fuente": x.get("url", ""),
                            "pagina": page["pagina"], "total_paginas": page["total_paginas"],
                            "vista": vista, "sha256_vista": sha_vista,
                            "texto": page["texto"], "origen_texto": page["metodo"],
                            "ocr_pendiente": page["pendiente"], "segmentos": [],
                            "referencia_humana": ""})
    audios = [x for x in items if x["clase"] == "audio"]
    if n_audios and len(audios) < n_audios:
        print("AVISO: faltan audios. Ejecuta preparar_audios() en el cuaderno o visor.")
    whisper = None
    if hacer_asr and audios[:n_audios]:
        from faster_whisper import WhisperModel
        whisper = WhisperModel("tiny", device="cpu", compute_type="int8", cpu_threads=2)
    # El inventario ofrece el PCM16 para reproducir, pero la fuente de voz
    # original está identificada separadamente en el manifiesto.
    from fuentes import AUDIO_MANIFEST
    audio_info = {}
    if AUDIO_MANIFEST.exists():
        for fila in json.loads(AUDIO_MANIFEST.read_text(encoding="utf-8"))["audios"]:
            audio_info[Path(fila["pcm16"]).name] = fila
    for x in audios[:n_audios]:
        path = x["original"]  # derivado PCM16 de trabajo
        fila = audio_info.get(path.name, {})
        fuente_real = root / fila["fuente"] if fila.get("fuente") else path
        if not fuente_real.is_file():
            raise FileNotFoundError(f"Falta la voz original: {fuente_real}")
        segs = transcribir_voz(path, whisper) if hacer_asr else []
        raw_text = " ".join(z["texto"] for z in segs)
        ref = x.get("referencia", "")
        records.append({"id": "audio:" + path.name, "modalidad": "audio",
                        "fuente": str(fuente_real.relative_to(root)),
                        "sha256": huella(fuente_real),
                        "derivado": str(path.relative_to(root)),
                        "sha256_derivado": huella(path),
                        "credito": x["credito"], "url_fuente": x.get("url", ""),
                        "pagina": None, "texto": raw_text if hacer_asr else ref,
                        "origen_texto": "whisper_tiny_asr" if hacer_asr else "referencia_humana_no_asr",
                        "ocr_pendiente": False, "segmentos": segs,
                        "referencia_humana": ref, "intencion": x.get("intencion", "")})
    guardar_json(CATALOGO, {"version": 1, "modelo_indice": MODELO,
                            "advertencia": "No vincular fotos, contratos y voces por cercanía semántica.",
                            "registros": records})
    print(f"Catálogo: {len(records)} fragmentos de página/foto/audio → {CATALOGO}")
    return records


def crear_indice(records: list[dict], *, n_max: int = 12) -> dict:
    """Vectores de imagen y fragmentos textuales con caché por contenido y modelo."""
    if not 1 <= n_max <= 5000:
        raise ValueError("Límite de vectores fuera de rango")
    index = leer_json(INDICE) if INDICE.exists() else {"version": 1, "modelo": MODELO, "vectores": {}}
    if index.get("modelo") != MODELO:
        raise ValueError("Caché de un modelo diferente; no se mezclarán vectores")
    cache = index["vectores"]
    needed = []
    for r in records:
        source = ROOT / r["fuente"]
        if not source.is_file() or huella(source) != r["sha256"]:
            raise ValueError("Fuente ausente o modificada: " + r["fuente"])
        # Una foto puede recuperarse aunque OCR no vea letras.
        if r["modalidad"] == "imagen":
            key = "imagen|" + MODELO + "|" + r["sha256"]
            needed.append((key, r["id"], "imagen", source, None))
        elif r["modalidad"] == "contrato" and r.get("vista"):
            # Visión DOCUMENTAL: vector de PNG de página, además de OCR.
            vista = ROOT / r["vista"]
            if not vista.is_file() or huella(vista) != r.get("sha256_vista"):
                raise ValueError("Vista PNG ausente o modificada: " + r["vista"])
            key = "imagen_documento|" + MODELO + "|" + r["sha256_vista"]
            needed.append((key, r["id"], "imagen_documento", vista, None))
        for i, frag in enumerate(trozos(r["texto"])):
            key = "texto|" + MODELO + "|" + hashlib.sha256(frag.encode("utf-8")).hexdigest()
            needed.append((key, r["id"], "texto", source, frag))
    unique = {v[0]: v for v in needed}
    todo = [v for k, v in unique.items() if k not in cache]
    if len(todo) > n_max:
        raise ValueError(f"Se necesitan {len(todo)} vectores nuevos (límite {n_max}). "
                         "Sube --max-vectores conscientemente o reduce la muestra.")
    for i, (key, rid, mode, path, frag) in enumerate(todo, 1):
        print(f"Inferencia {i}/{len(todo)}: {mode}, {rid}")
        entrada = ({"image": base64.b64encode(path.read_bytes()).decode("ascii")}
                   if mode in ("imagen", "imagen_documento") else frag)
        cache[key] = incrustar(entrada)
        guardar_json(INDICE, index)
    # No devolver resultados antiguos que no corresponden al catálogo actual.
    index["entradas"] = [{"clave": k, "registro_id": rid, "canal": mode, "fragmento": frag or ""}
                          for k, rid, mode, path, frag in needed]
    guardar_json(INDICE, index)
    print(f"Listos {len(needed)} candidatos; nuevas inferencias: {len(todo)}.")
    return index


def buscar(pregunta: str, records: list[dict], index: dict, k: int = 5) -> list[dict]:
    """Recupera los registros pertinentes sin generar un resumen inventado."""
    if not pregunta.strip():
        raise ValueError("Escribe una consulta no vacía")
    if not 1 <= k <= 50:
        raise ValueError("k debe estar entre 1 y 50")
    query_vector = incrustar("task: search result | query: " + pregunta.strip())
    by_id = {r["id"]: r for r in records}
    results = []
    for entry in index["entradas"]:
        rid = entry["registro_id"]
        if rid not in by_id:
            continue
        vec = index["vectores"].get(entry["clave"])
        if vec is None:
            continue
        score = coseno(query_vector, vec)
        results.append({"puntaje_coseno": round(score, 5), "canal": entry["canal"],
                        "fragmento": entry["fragmento"], "registro": by_id[rid]})
    results.sort(key=lambda x: x["puntaje_coseno"], reverse=True)
    ordered = []
    seen = set()
    for r in results:
        if r["registro"]["id"] not in seen:
            ordered.append(r)
            seen.add(r["registro"]["id"])
        if len(ordered) == k:
            break
    return ordered


def presentar(resultados: list[dict], completo: bool = False) -> None:
    if not resultados:
        print("No hay resultados indexados. Comprueba OCR/ASR y el índice.")
        return
    for pos, hit in enumerate(resultados, 1):
        rec = hit["registro"]
        print(f"\n#{pos} [{rec['modalidad']}] coseno={hit['puntaje_coseno']:.3f} "
              f"canal={hit['canal']}\nARCHIVO: {rec['fuente']}")
        print(f"SHA-256: {rec['sha256']}; página: {rec.get('pagina') or 'N/A'}")
        print(f"Origen del texto: {rec['origen_texto']}; crédito: {rec['credito']}")
        print("Fragmento relevante:", hit["fragmento"][:420] or "(coincidencia visual, ver fotografía)")
        if completo:
            print("TEXTO EXTRAÍDO COMPLETO:", rec["texto"] or
                  "(No existe texto extraído: abrir la imagen original.)")
            if rec["segmentos"]:
                print("SEGMENTOS CON TIEMPOS:", json.dumps(rec["segmentos"], ensure_ascii=False))
            if rec.get("referencia_humana"):
                print("REFERENCIA HUMANA:", rec["referencia_humana"])
        print("AVISO: similitud no es verdad; verificar la fuente antes de citar.")


def main() -> None:
    p = argparse.ArgumentParser(description="S11 · Búsqueda multimodal trazable")
    sub = p.add_subparsers(dest="accion", required=True)
    prep = sub.add_parser("preparar", help="Extrae evidencias; sin inferencia de embeddings")
    prep.add_argument("--fotos", type=int, default=4)
    prep.add_argument("--actas", type=int, default=1)
    prep.add_argument("--audios", type=int, default=1)
    prep.add_argument("--paginas", type=int, default=1, help="0: todas las páginas")
    prep.add_argument("--ocr", action="store_true", help="Ejecuta Tesseract explícitamente")
    prep.add_argument("--asr", action="store_true", help="Ejecuta Whisper explícitamente")
    idx = sub.add_parser("indexar", help="Calcula SOLO vectores faltantes: requiere Ollama")
    idx.add_argument("--max-vectores", type=int, default=12)
    search = sub.add_parser("buscar", help="Consulta el índice ya preparado")
    search.add_argument("pregunta")
    search.add_argument("--k", type=int, default=5)
    search.add_argument("--completo", action="store_true")
    args = p.parse_args()
    if args.accion == "preparar":
        preparar(n_fotos=args.fotos, n_actas=args.actas, n_audios=args.audios,
                 paginas=args.paginas, hacer_ocr=args.ocr, hacer_asr=args.asr)
    elif args.accion == "indexar":
        crear_indice(leer_json(CATALOGO)["registros"], n_max=args.max_vectores)
    else:
        results = buscar(args.pregunta, leer_json(CATALOGO)["registros"], leer_json(INDICE), args.k)
        presentar(results, args.completo)


if __name__ == "__main__":
    main()
