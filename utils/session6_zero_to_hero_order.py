#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reordena S06 para que ningún concepto avanzado aparezca antes de enseñarse."""
from __future__ import annotations


def src(cell):
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def find(cells, needle):
    hits = [i for i, cell in enumerate(cells) if needle in src(cell)]
    if len(hits) != 1:
        raise ValueError(f"Referencia ambigua {needle!r}: {hits}")
    return hits[0]


def reorder_zero_to_hero(cells):
    # 1) H2-R deja de aparecer antes de aprender grafos/Cypher.
    h2_start = find(cells, "## H2-R: la hipótesis relacional de esta sesión")
    concepts_start = find(cells, "## 3. Antes de Cypher")
    if h2_start >= concepts_start:
        raise ValueError("No se reconoció el bloque H2-R temprano")
    h2_block = cells[h2_start:concepts_start]
    del cells[h2_start:concepts_start]

    h2_target = find(cells, "## 6. Profundización — comparar conectividad con una referencia (H2-R)")
    cells[h2_target:h2_target] = h2_block

    # 2) MERGE y la mini referencia de cláusulas se explican después del laboratorio manual.
    merge_start = find(cells, "### Función usada: `MERGE`")
    mini_ref = find(cells, "| `MERGE` | encuentra o crea un patrón")
    if mini_ref != merge_start + 1:
        raise ValueError("Cambió el bloque MERGE/referencia")
    merge_block = cells[merge_start:mini_ref + 1]
    del cells[merge_start:mini_ref + 1]

    transfer = find(cells, "## 4.2 Transferencia al caso real — cargar el grafo sin duplicar")
    cells[transfer:transfer] = merge_block

    return cells
