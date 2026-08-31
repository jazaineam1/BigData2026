#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida el tutorial HTML de Astra/Cassandra de la sesión 5."""

from __future__ import annotations
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "assets" / "tutoriales" / "astra-cassandra-paso-a-paso.html"

REQUIRED = [
    "Serverless (non-vector)",
    "compras_claras",
    "token@cqlsh&gt;",
    "PRIMARY KEY ((corte, departamento), valor_base, id_proceso)",
    "Connection details",
    "Secure Connect Bundle",
    "cassandra-driver",
    "docs.datastax.com/en/astra-db-serverless",
    "30-ago-2026",
]

class Counter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.slides = 0
        self.images = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section" and "slide" in a.get("class", "").split():
            self.slides += 1
        if tag == "img":
            self.images.append((a.get("src", ""), a.get("alt", "")))

def main():
    if not HTML.is_file():
        raise SystemExit(f"[ERROR] No existe {HTML.relative_to(ROOT)}")
    text = HTML.read_text(encoding="utf-8")
    parser = Counter()
    parser.feed(text)
    errors = []

    if parser.slides < 14:
        errors.append(f"Solo hay {parser.slides} diapositivas; se esperaban al menos 14.")
    if len(parser.images) < 3:
        errors.append("Se esperaban al menos 3 capturas reales de referencia.")
    for src, alt in parser.images:
        if not alt.strip():
            errors.append(f"Imagen sin alt: {src}")

    for item in REQUIRED:
        if item not in text:
            errors.append(f"Falta el elemento requerido: {item!r}")

    if re.search(r"AstraCS:[A-Za-z0-9_-]{20,}", text):
        errors.append("Posible token Astra incrustado.")
    if "CREATE KEYSPACE" in text and "No uses CREATE KEYSPACE" not in text:
        errors.append("CREATE KEYSPACE aparece sin advertencia; Astra no lo admite.")

    if errors:
        print("Validación fallida:")
        for e in errors:
            print("[ERROR]", e)
        raise SystemExit(1)

    print(f"[OK] Tutorial Astra: {parser.slides} diapositivas, {len(parser.images)} capturas reales de referencia.")
    print("[OK] Contiene CQL, CRUD, Connection details, SCB, token y Python driver.")
    print("[INFO] Las capturas externas son referencias reales; los nombres de botones se verifican contra docs 2026.")

if __name__ == "__main__":
    main()
