#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aplica la edición visual/pedagógica Graph Lab sobre la S06 generada.

El pipeline primero construye y valida la sesión base con sus regresiones históricas.
Después este script restaura los tres artefactos revisados de Graph Lab: notebook,
tutorial Aura y checklist. Los payloads son gzip+base64 para conservar exactamente
el JSON/HTML validado sin depender de una edición manual del .ipynb.
"""
from __future__ import annotations

import base64
import gzip
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "utils" / "s06_graphlab_payload"


def restore(parts: list[str], destination: str) -> None:
    token = "".join((PAYLOAD / part).read_text(encoding="utf-8").strip() for part in parts)
    data = gzip.decompress(base64.b64decode(token))
    output = ROOT / destination
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)
    print(f"[OK] {destination}: {len(data):,} bytes")


def main() -> None:
    restore(
        ["notebook_1.txt", "notebook_2.txt", "notebook_3.txt"],
        "Cuadernos/6_Neo4j_Contexto_Relacional.ipynb",
    )
    restore(
        ["tutorial_1.txt"],
        "assets/tutoriales/neo4j-aura-s06-paso-a-paso.html",
    )
    restore(
        ["checklist_1.txt"],
        "assets/tutoriales/s06-laboratorio-guiado.html",
    )


if __name__ == "__main__":
    main()
