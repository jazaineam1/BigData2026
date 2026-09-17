#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regresiones específicas de Graph Lab para S06.

Complementa validate_session6.py con invariantes visuales y de Cypher que no
requieren una conexión autenticada a Aura. Su objetivo es detectar errores de
alias, pérdida del tutorial gráfico o desorden pedagógico antes de publicar.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "6_Neo4j_Contexto_Relacional.ipynb"
GRAPH_TUTORIAL = ROOT / "assets" / "tutoriales" / "neo4j-graph-lab-s06.html"


def source(cell: dict) -> str:
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def main() -> None:
    errors: list[str] = []
    for path in (NB, GRAPH_TUTORIAL):
        if not path.is_file():
            errors.append(f"Falta {path.relative_to(ROOT)}")
    if errors:
        raise SystemExit("\n".join(errors))

    nb = json.loads(NB.read_text(encoding="utf-8"))
    cells = nb.get("cells", [])
    text = "\n".join(source(cell) for cell in cells)

    for i, cell in enumerate(cells, 1):
        if cell.get("cell_type") == "code":
            try:
                ast.parse(source(cell))
            except SyntaxError as exc:
                errors.append(f"Sintaxis Python inválida en celda {i}: {exc}")

    required = [
        "GRAPH-LAB-S06-V2",
        "USAR_MI_ANCLA_S5",
        'RELACION_PROCESO_PROVEEDOR = "____"',
        "Graph Lab — mirar, tocar y entender el grafo",
        "consulta_graph_basico",
        "consulta_wow_global",
        "consulta_wow_ancla",
        "grado_adjudicaciones",
        "entidades_conectadas",
        "p.precio_base AS precio_base",
        "## 6. Contrato de resultado: ahora sí, primero pandas",
    ]
    for item in required:
        if item not in text:
            errors.append(f"Falta en el notebook Graph Lab: {item!r}")

    if "ORDER BY entidad, valor DESC" in text:
        errors.append("Cypher inválido: se ordena por alias 'valor' aunque la consulta devuelve 'precio_base'")
    if "p.valor AS precio_base" in text:
        errors.append("Quedó la propiedad ambigua p.valor; Graph Lab debe usar p.precio_base")

    graph_pos = text.find("Graph Lab — mirar, tocar y entender el grafo")
    contract_pos = text.find("## 6. Contrato de resultado: ahora sí, primero pandas")
    if graph_pos < 0 or contract_pos < 0 or graph_pos > contract_pos:
        errors.append("Graph Lab debe ocurrir antes del contrato/H2-R")

    tutorial = GRAPH_TUTORIAL.read_text(encoding="utf-8")
    tutorial_required = [
        "Graph, Table y RAW",
        "Fit to screen",
        "grado_adjudicaciones",
        "entidades_conectadas",
        "WOW 1",
        "WOW 2",
        "RETURN camino",
        "ADJUDICADO_A",
        "precio_base",
        "valor_adjudicado",
        "el layout",
    ]
    for item in tutorial_required:
        if item not in tutorial:
            errors.append(f"Tutorial Graph Lab incompleto: {item!r}")
    if tutorial.count('<section class="slide') < 10:
        errors.append("El tutorial Graph Lab quedó demasiado corto o mal formado")

    if errors:
        print("Validación Graph Lab fallida:")
        for error in errors:
            print("[ERROR]", error)
        raise SystemExit(1)

    print(f"[OK] Graph Lab: {len(cells)} celdas; Python parsea correctamente")
    print("[OK] S5 opcional, patrón editable, grados, WOW 1/WOW 2 y tutorial visual presentes")
    print("[OK] Alias Cypher del vecindario coherente: precio_base se devuelve y se ordena")


if __name__ == "__main__":
    main()
