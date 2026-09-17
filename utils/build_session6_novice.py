#!/usr/bin/env python3
"""Generador canónico S06 para la versión introductoria a Neo4j/Cypher.

Reutiliza el modelo de datos del generador histórico, aplica la capa pedagógica
y evita reescribir los tutoriales HTML desde el notebook.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.build_session6_notebook import OUTPUT, build_cells
from utils.make_notebook import save, validate
from utils.session6_novice_finalize import finalize_cells


def build_novice_cells():
    return finalize_cells(build_cells())


def main() -> None:
    cells = build_novice_cells()
    validate(cells)
    save(cells, OUTPUT)
    print(f"[OK] S6 NOVATOS generada: {len(cells)} celdas")


if __name__ == "__main__":
    main()
