# -*- coding: utf-8 -*-
"""
utils/build_eltiempo_dataset.py
================================
Construye el dataset documental de la Sesion 3 a partir de dos fuentes publicas
de El Tiempo, enlazadas entre si:

  1. Sitemap XML mensual  -> https://www.eltiempo.com/sitemap-articles-2026-08.xml
     Da la lista de URLs de articulos del mes. El ID numerico del articulo es el
     ultimo segmento de la URL.

  2. Feed JSON por articulo -> https://www.eltiempo.com/servicios/feeds/articulo/<ID>
     Da el documento completo: titulo, seccion, autores, etiquetas, imagenes y
     el cuerpo como una lista heterogenea de bloques.

Por que estas dos fuentes y no un CSV
-------------------------------------
El CSV de SECOP es rectangular: 59 columnas fijas, sin arreglos ni anidamiento.
Sirve para hablar de columnas vacias, pero no permite demostrar por que existe
un modelo documental. Las noticias si:

  - `tags`    es un ARREGLO de objetos  -> una noticia tiene N etiquetas
  - `authors` es un ARREGLO de objetos  -> una noticia tiene N autores
  - `images`  es un ARREGLO de objetos
  - `content` es un ARREGLO HETEROGENEO -> cada bloque tiene un `type` distinto
  - campos como `subtitle` o `partner` faltan en unos documentos y en otros no

Eso es exactamente lo que no cabe en una tabla sin inventar columnas.

Uso
---
    python utils/build_eltiempo_dataset.py --n 120

Salida
------
    Datos/noticias_eltiempo_2026-08.json   (lista de documentos curados)
    Datos/noticias_eltiempo_2026-08.meta.json (procedencia y conteos)

Cortesia con la fuente
----------------------
Se descarga una sola vez, del lado del docente, con pausa entre peticiones y un
User-Agent identificable. El estudiante lee el JSON ya versionado en el repo:
no queremos diez runtimes golpeando eltiempo.com durante la clase.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

SITEMAP = "https://www.eltiempo.com/sitemap-articles-{mes}.xml"
FEED = "https://www.eltiempo.com/servicios/feeds/articulo/{id}"
UA = "BigData-UCentral-curso/1.0 (material docente; contacto: profesor del curso)"

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Palabras que, apareciendo como palabra completa en el slug de la URL, indican
# que el articulo trata de contratacion publica. Filtrar por el slug permite
# revisar 57.844 articulos del ano con 8 peticiones, y descargar solo los ~995
# que interesan. Sin este filtro habria que pedir 57.844 feeds.
CLAVES_CONTRATACION = [
    "contrato", "contratos", "contratacion", "secop", "licitacion", "licitaciones",
    "adjudicacion", "adjudico", "corrupcion", "sobrecosto", "sobrecostos",
    "peculado", "detrimento", "contraloria", "procuraduria", "interventoria",
    "obra-inconclusa", "elefante-blanco", "carrusel", "coima", "soborno",
]


def limpiar_html(s):
    """Quita etiquetas HTML y entidades del texto de un bloque."""
    import html as _html

    s = re.sub(r"<[^>]+>", "", s or "")
    return re.sub(r"\s+", " ", _html.unescape(s)).strip()


def _get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def leer_sitemap(mes):
    """Devuelve [{id, url, lastmod, seccion_url}, ...] del sitemap de un mes."""
    raw = _get(SITEMAP.format(mes=mes))
    root = ET.fromstring(raw)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    filas = []
    for u in root.findall("s:url", ns):
        loc = u.findtext("s:loc", default="", namespaces=ns)
        lastmod = u.findtext("s:lastmod", default="", namespaces=ns)
        m = re.search(r"-(\d{5,})$", loc)
        if not m:
            continue
        # La seccion se deduce de la ruta: /politica/gobierno/slug-123 -> politica
        partes = [p for p in loc.split("/") if p][2:]
        seccion = partes[0] if partes else ""
        filas.append(
            {"id": int(m.group(1)), "url": loc, "lastmod": lastmod, "seccion_url": seccion}
        )
    return filas


def es_de_contratacion(url):
    """True si el slug de la URL contiene alguna palabra clave completa."""
    slug = url.rsplit("/", 1)[-1]
    return any(re.search(r"(^|-)" + k + r"(-|$)", slug) for k in CLAVES_CONTRATACION)


def curar(data, fila_sitemap):
    """
    Reduce el feed JSON a un documento de clase.

    Se conservan a proposito los tres arreglos y la heterogeneidad del cuerpo:
    son el objeto de estudio de la sesion, no ruido.
    """
    d = data.get("data", data) or {}

    tags = [
        {"id": t.get("id"), "nombre": t.get("name"), "slug": t.get("slug")}
        for t in (d.get("tags") or [])
        if isinstance(t, dict)
    ]
    autores = [
        {
            "nombre": a.get("signature") or a.get("name"),
            "cargo": a.get("cargo") or None,
            "twitter": a.get("twitter") or None,
        }
        for a in (d.get("authors") or [])
        if isinstance(a, dict)
    ]
    imagenes = [
        {"url": i.get("url"), "credito": i.get("credit") or None}
        for i in (d.get("images") or [])
        if isinstance(i, dict)
    ]

    bloques = []
    for b in (d.get("content") or []):
        if not isinstance(b, dict):
            continue
        item = {"tipo": b.get("type")}
        cont = b.get("content")
        # Cada tipo de bloque guarda su `content` de forma distinta: unos texto,
        # otros un objeto anidado. Esa diferencia es el punto pedagogico, no un
        # defecto: es lo que una tabla no puede representar sin inventar columnas.
        if isinstance(cont, str):
            item["texto"] = limpiar_html(cont)
        elif isinstance(cont, dict):
            item["datos"] = {k: v for k, v in cont.items() if isinstance(v, (str, int, float, bool))}
        elif isinstance(cont, list):
            item["items"] = len(cont)
        bloques.append(item)

    texto = " ".join(
        b.get("texto", "") for b in bloques if b.get("tipo") in ("paragraph", "subtitle-h2")
    ).strip()

    doc = {
        "_id": d.get("id") or fila_sitemap["id"],
        "titulo": d.get("title"),
        "seccion": d.get("section") or fila_sitemap["seccion_url"],
        "url": d.get("url") or fila_sitemap["url"],
        "publicado": fila_sitemap["lastmod"],
        "premium": bool(d.get("premium")),
        "etiquetas": tags,
        "autores": autores,
        "imagenes": imagenes,
        "cuerpo": bloques,
        "n_palabras": len(texto.split()),
    }
    # Campos que NO siempre existen: se omiten cuando faltan, a proposito.
    # Esta es la heterogeneidad de nivel superior que el estudiante debe notar.
    opcionales = {
        "subtitulo": d.get("subtitle"),
        "entradilla": limpiar_html(d.get("lead") or ""),
        "descripcion": limpiar_html(d.get("description") or ""),
        "editor": d.get("editor"),
        "categoria": d.get("category"),
        "subcategoria": d.get("subcategory"),
        "firma": d.get("author"),
        "tiene_video": bool(d.get("video")) or None,
        "tiene_audio": bool(d.get("audio_url")) or None,
        "tiene_pdf": bool(d.get("hasPdfFile")) or None,
    }
    for k, v in opcionales.items():
        if v:
            doc[k] = v
    return doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=120, help="tope de articulos a descargar")
    ap.add_argument("--pausa", type=float, default=0.4, help="segundos entre peticiones")
    ap.add_argument(
        "--meses", default="2026-08",
        help="meses separados por coma, por ejemplo 2026-01,2026-02,...,2026-08",
    )
    ap.add_argument(
        "--tema", choices=["muestra", "contratacion"], default="muestra",
        help="'muestra' reparte por seccion; 'contratacion' filtra por el slug",
    )
    ap.add_argument("--salida", default=None, help="nombre base del archivo de salida")
    args = ap.parse_args()

    meses = [m.strip() for m in args.meses.split(",") if m.strip()]
    base = args.salida or (
        "noticias_contratacion_2026" if args.tema == "contratacion"
        else f"noticias_eltiempo_{meses[0]}"
    )
    out = os.path.join(REPO, "Datos", base + ".json")
    out_meta = os.path.join(REPO, "Datos", base + ".meta.json")

    print(f"1/3 Leyendo {len(meses)} sitemap(s)...")
    filas, total_listado = [], 0
    for mes in meses:
        try:
            del_mes = leer_sitemap(mes)
        except Exception as exc:
            print(f"    {mes}: no disponible ({str(exc)[:60]})")
            continue
        total_listado += len(del_mes)
        if args.tema == "contratacion":
            del_mes = [f for f in del_mes if es_de_contratacion(f["url"])]
        filas.extend(del_mes)
        print(f"    {mes}: {len(del_mes)} seleccionados")
    print(f"    Total listado por El Tiempo: {total_listado} articulos")
    print(f"    Candidatos tras el filtro '{args.tema}': {len(filas)}")

    # Un mismo articulo puede aparecer en varios sitemaps mensuales si se
    # actualizo despues de publicarse. Sin este paso el JSON traeria documentos
    # con el mismo _id y `insert_many` fallaria con E11000 Duplicate Key.
    unicos, vistos = [], set()
    for f in filas:
        if f["id"] not in vistos:
            vistos.add(f["id"])
            unicos.append(f)
    if len(unicos) != len(filas):
        print(f"    Duplicados entre meses descartados: {len(filas) - len(unicos)}")
    filas = unicos

    if args.tema == "contratacion":
        seleccion = filas[: args.n]
    else:
        # Muestreo por seccion para que el dataset no quede todo de deportes.
        por_seccion = {}
        for f in filas:
            por_seccion.setdefault(f["seccion_url"], []).append(f)
        print(f"    {len(por_seccion)} secciones distintas")
        seleccion, i = [], 0
        while len(seleccion) < args.n:
            agregado = False
            for sec in sorted(por_seccion):
                if i < len(por_seccion[sec]) and len(seleccion) < args.n:
                    seleccion.append(por_seccion[sec][i])
                    agregado = True
            if not agregado:
                break
            i += 1

    OUT, OUT_META = out, out_meta
    print(f"2/3 Descargando {len(seleccion)} feeds JSON (pausa {args.pausa}s)...")
    docs, fallos = [], []
    for k, fila in enumerate(seleccion, 1):
        try:
            raw = _get(FEED.format(id=fila["id"]))
            docs.append(curar(json.loads(raw.decode("utf-8")), fila))
        except Exception as exc:
            fallos.append({"id": fila["id"], "error": str(exc)[:120]})
        if k % 20 == 0:
            print(f"    {k}/{len(seleccion)}  ok={len(docs)} fallos={len(fallos)}")
        time.sleep(args.pausa)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=1)

    campos = {}
    for d in docs:
        for k in d:
            campos[k] = campos.get(k, 0) + 1

    meta = {
        "generado": datetime.now(timezone.utc).isoformat(),
        "fuente_sitemap": SITEMAP,
        "fuente_feed": FEED,
        "meses": meses,
        "tema": args.tema,
        "claves_filtro": CLAVES_CONTRATACION if args.tema == "contratacion" else None,
        "n_listados_por_eltiempo": total_listado,
        "n_candidatos_tras_filtro": len(filas),
        "n_documentos": len(docs),
        "n_fallos": len(fallos),
        "fallos": fallos[:20],
        "presencia_de_campos": campos,
        "nota": (
            "Datos publicos de El Tiempo descargados una sola vez para uso docente. "
            "El enlace entre las dos fuentes es el ID numerico final de la URL del sitemap."
        ),
    }
    with open(OUT_META, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)

    print(f"3/3 Guardado: {OUT}")
    print(f"    {len(docs)} documentos, {len(fallos)} fallos, {os.path.getsize(OUT)/1024:.0f} KB")
    print("\n    Presencia de campos (asi se ve la heterogeneidad):")
    for k, v in sorted(campos.items(), key=lambda x: -x[1]):
        marca = "" if v == len(docs) else "   <-- NO esta en todos"
        print(f"      {k:14s} {v:4d}/{len(docs)}{marca}")


if __name__ == "__main__":
    sys.exit(main())
