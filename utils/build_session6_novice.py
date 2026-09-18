#!/usr/bin/env python3
"""Generador canónico S06 para la versión introductoria a Neo4j/Cypher.

Reutiliza el modelo de datos del generador histórico, aplica la capa pedagógica
para principiantes, inserta la progresión zero-to-hero, reordena los bloques
para que ningún concepto avanzado aparezca antes de enseñarse y cierra con un
apéndice avanzado de análisis de ecosistemas contractuales.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.build_session6_notebook import OUTPUT, build_cells
from utils.make_notebook import save, validate
from utils.session6_advanced_ecosystem import append_advanced_ecosystem
from utils.session6_novice_finalize import finalize_cells
from utils.session6_zero_to_hero import apply_zero_to_hero
from utils.session6_zero_to_hero_order import reorder_zero_to_hero


def build_novice_cells():
    cells = finalize_cells(build_cells())
    cells = apply_zero_to_hero(cells)
    cells = reorder_zero_to_hero(cells)
    return append_advanced_ecosystem(cells)


def main() -> None:
    cells = build_novice_cells()
    validate(cells)
    save(cells, OUTPUT)
    print(f"[OK] S6 ZERO-TO-HERO generada: {len(cells)} celdas")


if __name__ == "__main__":
    main()
