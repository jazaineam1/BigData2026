# -*- coding: utf-8 -*-
"""S11: lectura de noticia y fotografía del corpus editorial descargado.

Une solo por article_id del inventario S10. No enlaza voces MINDS-14
a noticias ni a procesos SECOP. Nunca visita el sitio de El Tiempo.
Solo guarda fragmentos breves y metadatos, no el artículo íntegro.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen
import json
import re
import unicodedata

CORPUS = ("https://raw.githubusercontent.com/jazaineam1/"
          "BigData2026/main/Datos/noticias_contratacion_2026.json")
MAX_BYTES = 16_000_000
ESQUEMA = "s11-reto-noticia-imagen/v1"
STOP = {"esta","este","estos","estas","para","sobre","entre","desde","hasta",
        "porque","pero","como","tambien","segun","cuando","donde","dentro",
        "despues","antes","tiene","tienen","fueron","habia","habria",
        "unos","unas","algunos","las","los","una","uno","con","por","que",
        "del","sus","mas","han","era","son","fue","ser","se","sin",
        "de","la","el","al","lo","un","en","su"}
MONTO = re.compile(r"(?:\$\s*[\d][\d.,]*\s*(?:mil\s+millones|millones|pesos)?|"
                   r"[\d][\d.,]*\s*(?:mil\s+millones|millones)\s+de\s+pesos)",
                   re.IGNORECASE)


def descargar_corpus() -> bytes:
    req = Request(CORPUS, headers={"User-Agent": "BigData2026-S11-educativo/1.0"})
    with urlopen(req, timeout=120) as response:
        partes, total = [], 0
        while True:
            b = response.read(1024 * 1024)
            if not b:
                break
            total += len(b)
            if total > MAX_BYTES:
                raise ValueError("Corpus editorial demasiado grande")
            partes.append(b)
    return b"".join(partes)


def cargar_noticias(raiz: Path) -> tuple[list[dict], dict]:
    """Descarga UNA sola vez el JSON ya alojado en el repositorio."""
    raiz = Path(raiz)
    destino = raiz / "cache" / "noticias_contratacion_2026.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    if not destino.exists():
        raw = descargar_corpus()
        json.loads(raw)
        temporal = destino.with_suffix(".json.nuevo")
        temporal.write_bytes(raw)
        temporal.replace(destino)
    if destino.stat().st_size > MAX_BYTES:
        raise ValueError("Caché de noticias excede el límite")
    raw = destino.read_bytes()
    corpus = json.loads(raw)
    if isinstance(corpus, dict):
        corpus = corpus.get("noticias", corpus.get("documentos", corpus.get("items", [])))
    if not isinstance(corpus, list) or not corpus:
        raise ValueError("No se encontró una lista de noticias")
    noticias = [x for x in corpus if isinstance(x, dict)]
    return noticias, {"path": destino.relative_to(raiz).as_posix(),
                      "sha256": sha256(raw).hexdigest(), "count": len(noticias),
                      "source_url": CORPUS}


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def _paragraphs(value: object) -> list[str]:
    if isinstance(value, str):
        cleaned = _clean(value)
        return [cleaned] if len(cleaned) >= 18 else []
    if isinstance(value, list):
        return [v for x in value for v in _paragraphs(x)]
    if isinstance(value, dict):
        keys = ("texto", "text", "content", "contenido", "html",
                "parrafo", "paragraph", "body", "p", "cuerpo")
        return [v for k in keys if k in value for v in _paragraphs(value[k])]
    return []


def buscar_noticia_por_imagen(imagen: dict, noticias: list[dict]) -> dict:
    """Usa ID editorial verificado; no inventa cruce audio/contrato."""
    article_id = str(imagen.get("article_id", ""))
    if not article_id.isdigit():
        raise ValueError("La imagen no tiene article_id válido")
    found = [n for n in noticias if str(n.get("_id", n.get("id", n.get("article_id")))) == article_id]
    if len(found) != 1:
        raise ValueError(f"Artículo {article_id} tiene {len(found)} coincidencias, se esperaba 1")
    row = found[0]
    titulo = _clean(str(row.get("titulo") or ""))
    if not titulo:
        raise ValueError("El artículo descargado no tiene título")
    subtitulo = _clean(str(row.get("subtitulo") or row.get("descripcion") or ""))
    cuerpo = _paragraphs(row.get("cuerpo", row.get("body", "")))
    texto = "\n\n".join(cuerpo)
    entrada = " ".join([titulo, subtitulo, texto])
    palabras = [re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", w.lower()))
                for w in re.findall(r"\b[\wáéíóúñÁÉÍÓÚÑ]{4,}\b", entrada)]
    palabras = [w for w in palabras if len(w) >= 4 and w not in STOP]
    return {"article_id": article_id, "titulo": titulo,
            "subtitulo": subtitulo, "url": row.get("url"),
            "publicado": row.get("publicado"), "seccion": row.get("seccion"),
            "autores": row.get("autores"),
            "texto_lectura": texto, "n_parrafos": len(cuerpo),
            "n_palabras_extraidas": len(entrada.split()),
            "palabras_frecuentes": Counter(palabras).most_common(8),
            "posibles_cifras_en_texto": list(dict.fromkeys(MONTO.findall(entrada)))[:8],
            "image_original_path": imagen["original_path"],
            "image_original_sha256": imagen["original_sha256"],
            "image_credit": imagen.get("credit"), "image_source_url": imagen.get("source_url"),
            "relation": "article_id del inventario editorial S10",
            "not_related_to_MINDS14": True}


CATEGORIAS_VISUALES = (
    "personas", "edificacion", "vehiculos", "texto_visible",
    "paisaje", "otros_objetos", "no_determinado",
)
LIMITES_VISUALES = (
    "la_foto_no_demuestra_la_noticia",
    "no_permita_identificar_personas",
    "no_corrobora_las_cifras",
)


def validar_evidencia_visual(evidencia: dict) -> dict:
    """Rechaza texto libre: dos decisiones distintas y un límite verificable."""
    campos = {"categoria_principal", "alternativa_descartada", "limite"}
    if not isinstance(evidencia, dict) or set(evidencia) != campos:
        raise ValueError("La evidencia visual debe contener tres decisiones cerradas")
    categoria = evidencia["categoria_principal"]
    alternativa = evidencia["alternativa_descartada"]
    limite = evidencia["limite"]
    if categoria not in CATEGORIAS_VISUALES or alternativa not in CATEGORIAS_VISUALES:
        raise ValueError("Categoría visual fuera de las opciones admitidas")
    if categoria == alternativa:
        raise ValueError("La alternativa descartada debe ser distinta de la categoría elegida")
    if limite not in LIMITES_VISUALES:
        raise ValueError("Límite visual fuera de las opciones admitidas")
    return dict(evidencia)


def guardar_ficha(raiz: Path, noticia: dict, evidencia_visual: dict,
                 ocr_texto: str, ocr_fuente: str) -> Path:
    """Producto del estudiante; conserva una cita breve, no todo el artículo."""
    raiz = Path(raiz)
    imagen = raiz / noticia["image_original_path"]
    if not imagen.is_file() or sha256(imagen.read_bytes()).hexdigest() != noticia["image_original_sha256"]:
        raise ValueError("El RAW de la foto no coincide con su SHA-256")
    evidencia_visual = validar_evidencia_visual(evidencia_visual)
    if ocr_fuente not in ("imagen_real", "no_disponible"):
        raise ValueError("Fuente de OCR inválida")
    ficha = {
        "schema": ESQUEMA, "article_id": noticia["article_id"],
        "titulo": noticia["titulo"], "url_noticia": noticia["url"],
        "publicado": noticia["publicado"], "seccion": noticia["seccion"],
        "fuente_texto": CORPUS, "relacion_verificada": noticia["relation"],
        "image_original_path": noticia["image_original_path"],
        "image_sha256": noticia["image_original_sha256"],
        "image_credit": noticia["image_credit"],
        "evidencia_visual_estructurada": evidencia_visual,
        "ocr_texto_en_imagen": ocr_texto[:1000],
        "ocr_fuente": ocr_fuente,
        "palabras_frecuentes": noticia["palabras_frecuentes"],
        "posibles_cifras_no_verificadas": noticia["posibles_cifras_en_texto"],
        "fragmento_breve": noticia["texto_lectura"][:220],
        "limite": "Observar texto o personas en una imagen no demuestra la noticia ni un contrato",
        "no_asociar_audios_MINDS14": True,
    }
    dest = raiz / "outputs" / "reto_noticia_imagen" / f"ficha_{noticia['article_id']}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8")
    return dest
