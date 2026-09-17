#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regresiones editoriales para la enseñanza visual del grado en S06."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "6_Neo4j_Contexto_Relacional.ipynb"
TUTORIAL = ROOT / "assets" / "tutoriales" / "neo4j-graph-lab-s06.html"
ENH = ROOT / "utils" / "session6_graphlab_enhancements.py"
MARKER = "GRAPH-DEGREE-S06-V1"


def main() -> None:
    errors: list[str] = []
    for path in (NB, TUTORIAL, ENH):
        if not path.is_file():
            errors.append(f"Falta {path.relative_to(ROOT)}")
    if errors:
        raise SystemExit("\n".join(errors))

    nb = json.loads(NB.read_text(encoding="utf-8"))
    notebook_text = "\n".join(
        "".join(c.get("source", [])) if isinstance(c.get("source", []), list) else str(c.get("source", ""))
        for c in nb.get("cells", [])
    )
    tutorial = TUTORIAL.read_text(encoding="utf-8")
    enh = ENH.read_text(encoding="utf-8")

    required_notebook = [
        MARKER,
        "Table mide; Graph explica",
        "count(r) AS grado_adjudicaciones",
        "MATCH (p:Proceso)-[r:ADJUDICADO_A]->(v:Proveedor)",
        "El tamaño, la cercanía o la posición automática",
        "entidades_conectadas",
        "WOW 1",
        "WOW 2",
    ]
    for item in required_notebook:
        if item not in notebook_text:
            errors.append(f"Notebook sin evidencia de grado visual: {item!r}")

    required_tutorial = [
        MARKER,
        "Table mide; Graph explica",
        "count(r) AS grado_adjudicaciones",
        "5.1 · Grado gráfico",
        "Result · Graph",
        "Fit to screen",
        "el tamaño, la posición o la cercanía automática del nodo no codifican grado",
        "Graph",
        "Table",
        "RAW",
    ]
    for item in required_tutorial:
        if item not in tutorial:
            errors.append(f"Tutorial sin evidencia de grado visual: {item!r}")

    if MARKER not in enh:
        errors.append("La mejora de grado debe quedar en la fuente editorial, no solo en artefactos generados")

    graph_pos = notebook_text.find("## 5. Graph Lab")
    degree_pos = notebook_text.find("### Grado ≠ entidades conectadas")
    h2r_pos = notebook_text.find("## 6. Contrato de resultado: ahora sí, primero pandas")
    if min(graph_pos, degree_pos, h2r_pos) < 0 or not (graph_pos < degree_pos < h2r_pos):
        errors.append("El grado visual debe enseñarse dentro de Graph Lab y antes de H2-R")

    if errors:
        print("Validación visual de grado S06 fallida:")
        for error in errors:
            print("[ERROR]", error)
        raise SystemExit(1)

    print("[OK] S06 enseña grado exacto con count(r) y lectura estructural en Graph")
    print("[OK] Table mide; Graph explica; layout no se interpreta como grado")
    print("[OK] Grado directo permanece separado de entidades_conectadas y H2-R")


if __name__ == "__main__":
    main()
