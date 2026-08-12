#!/usr/bin/env python3
"""Valida estructura, metadatos de Colab y recursos locales de la sesión 2."""

from __future__ import annotations

import json
import re
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "Cuadernos" / "2_Definiciones_gcp.ipynb"
VISUAL_BASES = [
    ROOT / "assets" / "diagrams" / "session2" / name
    for name in [
        "01_hilo_decision",
        "02_proceso_as_is",
        "03_puente_analitico",
        "04_arquitectura_to_be",
        "05_ciclo_nist",
        "06_estados_git",
    ]
] + [
    ROOT / "assets" / "session2" / "git" / name
    for name in [
        "01_entorno_gratuito",
        "02_status_diff",
        "03_pull_request",
        "04_actions",
    ]
]


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        signature = handle.read(24)
    if signature[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"firma PNG inválida: {path}")
    return struct.unpack(">II", signature[16:24])


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
    if len(cells) != 70:
        errors.append(f"se esperaban 70 celdas y se encontraron {len(cells)}")
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
    required_snippets = [
        "ETL — Extract, Transform, Load",
        "ELT — Extract, Load, Transform",
        "el orden y el lugar de la T",
        "Apoyo de terminal — cuatro ideas antes de usar Git",
    ]
    for snippet in required_snippets:
        if snippet not in source:
            errors.append(f"falta el apoyo pedagógico obligatorio: {snippet}")

    for base in VISUAL_BASES:
        svg_path = base.with_suffix(".svg")
        png_path = base.with_suffix(".png")
        if not svg_path.exists() or not png_path.exists():
            errors.append(f"falta una versión SVG o PNG de {base.relative_to(ROOT)}")
            continue
        svg = svg_path.read_text(encoding="utf-8")
        if 'viewBox="0 0 1600 900"' not in svg:
            errors.append(f"lienzo SVG inesperado: {svg_path.relative_to(ROOT)}")
        if "<title" not in svg or "<desc" not in svg:
            errors.append(f"faltan título o descripción accesible: {svg_path.relative_to(ROOT)}")
        if "foreignObject" in svg or "flowchart" in svg:
            errors.append(f"la lámina conserva una dependencia o fuente impropia: {svg_path.relative_to(ROOT)}")
        try:
            dimensions = png_dimensions(png_path)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            if dimensions != (1600, 900):
                errors.append(
                    f"PNG {png_path.relative_to(ROOT)} mide {dimensions}, se esperaba (1600, 900)"
                )

    if errors:
        raise SystemExit("[ERROR] " + "\n[ERROR] ".join(errors))

    print(
        "[OK] Sesión 2:",
        f"{len(cells)} celdas,",
        f"{len(questions)} preguntas,",
        f"{len(hidden)} celdas de código plegadas,",
        f"{len(references)} referencias locales y {len(VISUAL_BASES)} láminas SVG/PNG verificadas.",
    )


if __name__ == "__main__":
    main()
