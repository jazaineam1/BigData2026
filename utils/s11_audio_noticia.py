# -*- coding: utf-8 -*-
"""S11 · Información de audio de noticia: metadatos, texto, entidades y evidencias.

No descarga material periodístico, no requiere API comercial ni inventa uniones
con SECOP, con fotos o con el corpus de voces MINDS-14. El ASR opcional del
cuaderno entrega TEXTO; este módulo extrae candidatos y guarda trazabilidad.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import re
import unicodedata

SCHEMA = "s11-informacion-audio/v1"
TOPICOS = {
    "precios": r"\bpreci(?:o|os|os|os)\b|\bfijaci[oó]n\b",
    "competencia": r"\bcompetencia\b|\bmercado\b|\binfracci[oó]n(?:es)?\b",
    "proteccion_consumidor": r"\bconsumidor(?:es)?\b|\bderechos?\b",
    "requerimientos": r"\brequerimientos?\b|\binformaci[oó]n\b|\bsolicit(?:a|aron|ud)\b",
    "promociones": r"\bdescuentos?\b|\bofertas?\b|\bpromociones?\b",
}
ENTIDADES = {
    "Superintendencia de Industria y Comercio": r"\b(?:superintendencia\s+de\s+industria\s+y\s+comercio|SIC)\b",
    "Fenalco": r"\bfenalco\b",
    "ANDI": r"\b(?:andi|asociaci[oó]n\s+nacional\s+de\s+empresarios)\b",
    "Panamericana": r"\bpanamericana\b",
    "Olímpica": r"\bol[ií]mpica\b",
    "Cielo Rusinque": r"\bcielo\s+rusinque\b",
}
CANTIDADES = [
    r"\b(?:m[aá]s\s+de\s+)?(?:cincuenta|50)\s+compa[nñ][ií]as\b",
    r"(?<!\\w)(?:\\d{1,3}(?:[.,]\\d+)?\\s*%|\\d{1,3}(?:[.,]\\d+)?\\s+por\\s+ciento|veintitr[eé]s\\s+por\\s+ciento)(?!\\w)",
    r"\b(?:cuarenta\s+mil|40[ .]?000)\s+referencias\b",
    r"\b(?:cinco|5)\s+requerimientos\b",
    r"\b(?:dos\s+mil\s+veinticinco|2025)\b",
]
STOP = set("que para como esta este estas estos sobre entre donde cuando hasta unas unos ellos ellas desde donde".
           split())


def inspeccionar_audio(ruta: Path) -> dict:
    """Extrae metadatos sin confiar en la extensión. La lectura no modifica bytes."""
    import soundfile as sf
    ruta = Path(ruta)
    if not ruta.is_file():
        raise FileNotFoundError(ruta)
    info = sf.info(str(ruta))
    h = sha256()
    with ruta.open("rb") as entrada:
        for chunk in iter(lambda: entrada.read(1024 * 1024), b""):
            h.update(chunk)
    formato = str(info.format)
    subtipo = str(info.subtype)
    # sf.info reporta MPEG-1/2 Audio para MP3, aunque la extensión sea .wav.
    if "MPEG" in formato.upper() or "MP3" in subtipo.upper():
        codificacion = "MP3"
    elif "WAV" in formato.upper():
        codificacion = "WAV"
    else:
        codificacion = formato
    return {
        "filename": ruta.name,
        "extension": ruta.suffix.lower(),
        "real_format": formato,
        "codec": subtipo,
        "encoding_label": codificacion,
        "extension_matches_encoding": not (
            ruta.suffix.lower() == ".wav" and codificacion == "MP3"
        ),
        "duration_s": round(float(info.duration), 3),
        "sample_rate_hz": int(info.samplerate),
        "channels": int(info.channels),
        "original_bytes": ruta.stat().st_size,
        "original_sha256": h.hexdigest(),
        "is_audio": True,
    }


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _segmentos_con_posiciones(text: str, segmentos: list[dict] | None) -> list[dict]:
    """Relaciona segmentos ASR y texto normalizado sin inventar tiempos de palabras."""
    if not segmentos:
        return []
    posiciones, cursor = [], 0
    for registro in segmentos:
        parte = _clean(registro.get("text", ""))
        if not parte:
            continue
        indice = text.find(parte, cursor)
        if indice < 0:
            raise ValueError("Segmentos ASR no coinciden con el texto analizado")
        inicio, fin = float(registro["start_s"]), float(registro["end_s"])
        if not (0 <= inicio <= fin):
            raise ValueError("Tiempo ASR inválido")
        posiciones.append({"start_char": indice, "end_char": indice + len(parte),
                           "start_s": inicio, "end_s": fin})
        cursor = indice + len(parte)
    return posiciones


def _evidence(text: str, match: re.Match, radius: int = 75,
              timeline: list[dict] | None = None) -> dict:
    raw = text[max(0, match.start() - radius):min(len(text), match.end() + radius)]
    evidencia = {
        "matched_text": match.group(0),
        "context": _clean(raw),
        "start_char": match.start(),
        "end_char": match.end(),
    }
    segmentos = [s for s in (timeline or []) if s["start_char"] < match.end()
                 and s["end_char"] > match.start()]
    if segmentos:
        evidencia["audio_interval_s"] = {
            "start": round(min(s["start_s"] for s in segmentos), 2),
            "end": round(max(s["end_s"] for s in segmentos), 2),
            "precision": "segmento_asr_no_palabra",
        }
    return evidencia


def extraer_informacion(texto: str, *, origen: str = "asr",
                       segmentos: list[dict] | None = None) -> dict:
    """Convierte texto en candidatos con pruebas localizables, NO hechos certificados.

    origen debe distinguir 'asr', 'transcripcion_aportada' o 'parafrasis_demo'.
    No identifica automáticamente la relación entre el audio y una noticia.
    """
    if origen not in ("asr", "transcripcion_aportada", "parafrasis_demo"):
        raise ValueError("Origen textual ambiguo")
    texto = _clean(texto)
    if not texto:
        raise ValueError("No hay texto para extraer información")
    if segmentos and origen != "asr":
        raise ValueError("Solo el ASR real permite asignar tiempos")
    timeline = _segmentos_con_posiciones(texto, segmentos)
    entidades = []
    for nombre, patron in ENTIDADES.items():
        for m in list(re.finditer(patron, texto, flags=re.I))[:4]:
            entidades.append({"candidate": nombre, **_evidence(texto, m, timeline=timeline)})
    cifras = []
    for patron in CANTIDADES:
        for m in list(re.finditer(patron, texto, flags=re.I))[:4]:
            cifras.append({"kind": "number_or_quantity", **_evidence(texto, m, timeline=timeline)})
    topicos = []
    for etiqueta, patron in TOPICOS.items():
        found = re.search(patron, texto, flags=re.I)
        if found:
            topicos.append({"topic": etiqueta, **_evidence(texto, found, timeline=timeline)})
    palabras = re.findall(r"[a-záéíóúñ]{4,}", texto.lower())
    freq = Counter(w for w in palabras if w not in STOP).most_common(8)
    return {
        "schema": SCHEMA, "text_origin": origen,
        "character_count": len(texto), "word_count": len(texto.split()),
        "entities_candidates": entidades, "quantity_candidates": cifras,
        "topic_candidates": topicos, "frequent_terms": freq,
        "excerpt_for_review": texto[:220],
        "limitations": [
            "ASR puede transcribir mal nombres, números y negaciones.",
            "Un patrón regex identifica menciones posibles, no valida los hechos.",
            "No se infiere una relación noticia-audio solo por el nombre del archivo.",
            "MINDS-14 es un corpus bancario independiente, no noticias.",
        ],
    }


def verificar_candidatos(texto: str, analisis: dict) -> dict:
    """Prueba que cada evidencia coincide con un fragmento REAL del texto dado."""
    errores = []
    for group in ("entities_candidates", "quantity_candidates", "topic_candidates"):
        for item in analisis[group]:
            a, b = item["start_char"], item["end_char"]
            if not (0 <= a < b <= len(_clean(texto))) or _clean(texto)[a:b] != item["matched_text"]:
                errores.append(group)
    return {"ok": not errores, "errors": errores}


def guardar_informe(raiz: Path, metadatos_audio: dict, analisis: dict,
                    *, source_type: str, reference_text: bool = False) -> Path:
    """Produce JSON compartible sin volcar la transcripción periodística completa."""
    if source_type not in ("audio_usuario", "minds14", "ejemplo_sin_audio"):
        raise ValueError("Fuente de audio no identificada")
    if source_type == "audio_usuario" and not metadatos_audio.get("original_sha256"):
        raise ValueError("Audio de usuario sin SHA de procedencia")
    salida = {
        "schema": SCHEMA, "audio_source_type": source_type,
        "audio_metadata": metadatos_audio,
        "analysis": analisis,
        "reference_text_not_asr": bool(reference_text),
        "editorial_article_link_verified": False,
        "note": "Candidatos para revisión; no prueba automática de relación con artículo o contrato.",
    }
    base = Path(raiz) / "outputs" / "reto_audio_noticia"
    base.mkdir(parents=True, exist_ok=True)
    path = base / "ficha_audio.json"
    path.write_text(json.dumps(salida, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
