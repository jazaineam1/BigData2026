#!/usr/bin/env python3
"""Regresiones de grado/hub para S06 zero-to-hero."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "6_Neo4j_Contexto_Relacional.ipynb"
GRAPH = ROOT / "assets" / "tutoriales" / "neo4j-graph-lab-s06.html"


def main():
    nb = json.loads(NB.read_text(encoding="utf-8"))
    text = "\n".join("".join(c.get("source", [])) for c in nb["cells"])
    graph = GRAPH.read_text(encoding="utf-8")
    errors = []
    required = [
        "Contar conexiones: `count`, `AS`, `ORDER BY`, `DESC`",
        "count(r) AS grado",
        "hub** o **nodo concentrador",
        "No significa fraude ni riesgo",
        "count(DISTINCT e)",
        "grado` y `entidades_conectadas` no son la misma métrica",
        "Table mide; Graph explica",
    ]
    for x in required:
        if x not in text and x not in graph: errors.append(f"Falta enseñanza de grado/hub: {x!r}")

    g = text.find("### 4.6 Contar conexiones")
    d = text.find("### 4.7 `DISTINCT`")
    w = text.find("### 4.8 `WITH`")
    if min(g, d, w) < 0 or not (g < d < w):
        errors.append("Grado debe enseñarse antes de DISTINCT y WITH")

    graph_g = graph.find("11. Cuenta relaciones")
    graph_h = graph.find("13. ¿Qué es un hub?")
    graph_d = graph.find("14. DISTINCT")
    if min(graph_g, graph_h, graph_d) < 0 or not (graph_g < graph_h < graph_d):
        errors.append("En Graph Lab: grado → hub → DISTINCT")

    if "grado_adjudicaciones" in graph:
        errors.append("El tutorial inicial debe usar primero el término simple 'grado'")

    if errors:
        print("Validación grado/hub fallida:")
        for e in errors: print("[ERROR]", e)
        raise SystemExit(1)
    print("[OK] Grado se construye desde count(r) antes de introducir hub")
    print("[OK] Hub se presenta como nodo concentrador según una métrica, no como riesgo")
    print("[OK] DISTINCT separa filas/caminos de entidades distintas")

if __name__ == "__main__": main()
