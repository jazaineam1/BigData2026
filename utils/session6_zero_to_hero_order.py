#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reordena S06 para que ningún concepto avanzado aparezca antes de enseñarse."""
from __future__ import annotations

import base64
import json
import re


def src(cell):
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def put(cell, text):
    cell["source"] = text.strip("\n").splitlines(keepends=True)


def find(cells, needle):
    hits = [i for i, cell in enumerate(cells) if needle in src(cell)]
    if len(hits) != 1:
        raise ValueError(f"Referencia ambigua {needle!r}: {hits}")
    return hits[0]


def replace_once(cells, old, new):
    i = find(cells, old)
    put(cells[i], src(cells[i]).replace(old, new, 1))


def renumber_questions(cells):
    pattern = re.compile(r'pregunta_codificada\("([^\"]+)"\)')
    question_cells = []
    for cell in cells:
        if cell.get("cell_type") != "code":
            continue
        m = pattern.search(src(cell))
        if m:
            question_cells.append((cell, m))

    total = len(question_cells)
    for numero, (cell, _) in enumerate(question_cells, 1):
        text = src(cell)
        m = pattern.search(text)
        payload = json.loads(base64.b64decode(m.group(1)).decode("utf-8"))
        payload["numero"] = numero
        payload["total"] = total
        token = base64.b64encode(json.dumps(payload, ensure_ascii=False).encode("utf-8")).decode("ascii")
        text = text[:m.start(1)] + token + text[m.end(1):]
        text = re.sub(r'#@title Autoevaluación \d+', f'#@title Autoevaluación {numero}', text, count=1)
        put(cell, text)


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

    # 3) Numeración visible coherente después de insertar el curso zero-to-hero.
    replace_once(cells, "## 4.2 Transferencia al caso real — cargar el grafo sin duplicar", "## 5. Transferencia al caso real — cargar el grafo sin duplicar")
    replace_once(cells, "## 5. Aplicación guiada — consultar los datos reales en Aura Query", "## 6. Aplicación guiada — consultar los datos reales en Aura Query")
    replace_once(cells, "## 6. Profundización — comparar conectividad con una referencia (H2-R)", "## 7. Profundización — comparar conectividad con una referencia (H2-R)")
    if any("## 7. Verificación — ¿Neo4j y pandas cuentan lo mismo?" in src(c) for c in cells):
        replace_once(cells, "## 7. Verificación — ¿Neo4j y pandas cuentan lo mismo?", "## 8. Verificación — ¿Neo4j y pandas cuentan lo mismo?")
    if any("## 8. Ejemplo guiado — explorar un proveedor" in src(c) for c in cells):
        replace_once(cells, "## 8. Ejemplo guiado — explorar un proveedor", "## 9. Ejemplo guiado — explorar un proveedor")

    # 4) Al mover preguntas entre bloques, sus números también deben seguir el nuevo orden.
    renumber_questions(cells)
    return cells
