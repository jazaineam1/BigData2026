#!/usr/bin/env python3
"""Valida estructura, metadatos de Colab y recursos locales de la sesión 2."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "Cuadernos" / "2_Definiciones_gcp.ipynb"


def main() -> None:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    cells = notebook["cells"]
    code_cells = [cell for cell in cells if cell["cell_type"] == "code"]
    questions = [
        cell
        for cell in code_cells
        if "pregunta-interactiva" in cell.get("metadata", {}).get("tags", [])
    ]
    empty = [
        index
        for index, cell in enumerate(cells)
        if not "".join(cell.get("source", [])).strip()
    ]
    hidden = [
        cell
        for cell in code_cells
        if cell.get("metadata", {}).get("cellView") == "form"
        and cell.get("metadata", {}).get("jupyter", {}).get("source_hidden") is True
        and cell.get("metadata", {}).get("colab", {}).get("formView") == "both"
    ]
    source = "\n".join("".join(cell.get("source", [])) for cell in cells)
    references = re.findall(r'(?:src|href)="(\.\./(?:assets|Images)/[^"]+)', source)
    missing = [
        reference
        for reference in references
        if not (NOTEBOOK.parent / reference).resolve().exists()
    ]

    errors = []
    if len(cells) != 67:
        errors.append(f"se esperaban 67 celdas y se encontraron {len(cells)}")
    if len(questions) != 12:
        errors.append(f"se esperaban 12 preguntas y se encontraron {len(questions)}")
    if len(hidden) != len(code_cells):
        errors.append(
            f"solo {len(hidden)} de {len(code_cells)} celdas de código tienen metadatos de plegado"
        )
    if empty:
        errors.append(f"hay celdas vacías en los índices {empty}")
    if missing:
        errors.append("faltan recursos locales: " + ", ".join(missing))
    if "flowchart " in source or "```mermaid" in source:
        errors.append("el cuaderno todavía contiene Mermaid visible")
    if "GitHub Classroom" in source:
        errors.append("el cuaderno todavía menciona GitHub Classroom")

    if errors:
        raise SystemExit("[ERROR] " + "\n[ERROR] ".join(errors))

    print(
        "[OK] Sesión 2:",
        f"{len(cells)} celdas,",
        f"{len(questions)} preguntas,",
        f"{len(hidden)} celdas de código plegadas,",
        f"{len(references)} referencias locales verificadas.",
    )


if __name__ == "__main__":
    main()
