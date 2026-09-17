#!/usr/bin/env python3
"""Regresiones de grado/hub para S06."""
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
        "**Grado** significa cuántas relaciones directas",
        "count(r) AS grado",
        "Un **hub**, o **nodo concentrador**",
        "No significa “sospechoso” ni “anómalo”",
        "count(DISTINCT e) AS entidades_conectadas",
        "Table mide; Graph explica",
    ]
    for x in required:
        if x not in text and x not in graph: errors.append(f"Falta enseñanza de grado/hub: {x!r}")
    g = text.find("Consulta 4 — qué es el grado")
    h = text.find("Consulta 5 — qué es un hub")
    c = text.find("Hub por procesos ≠ proveedor compartido por muchas entidades")
    if min(g,h,c) < 0 or not (g < h < c): errors.append("Hub debe aparecer después de grado y antes de comparar entidades")
    if "grado_adjudicaciones" in graph: errors.append("El tutorial inicial debe usar primero el término simple 'grado'")
    if errors:
        print("Validación grado/hub fallida:")
        for e in errors: print("[ERROR]", e)
        raise SystemExit(1)
    print("[OK] Grado se define con ejemplo antes de hub")
    print("[OK] Hub se presenta como nodo concentrador, no como riesgo")
    print("[OK] Grado y entidades_conectadas permanecen separados")

if __name__ == "__main__": main()
