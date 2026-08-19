#!/usr/bin/env python3
"""Valida estructura, metadatos de Colab y recursos locales de la sesión 2."""

from __future__ import annotations

import json
import re
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "Cuadernos" / "2_Sesion_Arquitectura_BPM_Ciclo_Analitico.ipynb"
LEGACY_NOTEBOOK = ROOT / "Cuadernos" / "2_Definiciones_gcp.ipynb"
VISUAL_BASES = [
    ROOT / "assets" / "diagrams" / "session2" / name
    for name in [
        "01_hilo_decision",
        "02_proceso_as_is",
        "05_arquitectura_to_be",
        "06_ciclo_nist",
        "07_estados_git",
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
    question_numbers = sorted(
        int(match)
        for cell in questions
        for match in re.findall(r"# Pregunta (\d+) de 7", "".join(cell.get("source", [])))
    )
    references = re.findall(r'(?:src|href)="(\.\./(?:assets|Images)/[^"]+)', source)
    missing = [
        reference
        for reference in references
        if not (NOTEBOOK.parent / reference).resolve().exists()
    ]

    errors = []
    if not LEGACY_NOTEBOOK.is_file():
        errors.append("falta la copia de compatibilidad Cuadernos/2_Definiciones_gcp.ipynb")
    elif NOTEBOOK.read_bytes() != LEGACY_NOTEBOOK.read_bytes():
        errors.append("la ruta canónica y la copia histórica del cuaderno no están sincronizadas")
    if len(cells) < 35:
        errors.append(f"se esperaba una clase robusta y solo se encontraron {len(cells)} celdas")
    if len(questions) != 7:
        errors.append(f"se esperaban 7 preguntas y se encontraron {len(questions)}")
    if question_numbers != list(range(1, 8)):
        errors.append(f"numeración de preguntas inesperada: {question_numbers}")
    if len(hidden) != len(code_cells):
        errors.append(
            f"solo {len(hidden)} de {len(code_cells)} celdas de código tienen metadatos de plegado"
        )
    for index, cell in enumerate(code_cells):
        cell_source = "".join(cell.get("source", []))
        if not cell_source.startswith("#@title") or 'display-mode: "form"' not in cell_source.splitlines()[0]:
            errors.append(f"la celda de código {index} no tiene un título de formulario plegado")
        try:
            compile(cell_source, f"notebook-cell-{index}", "exec")
        except SyntaxError as exc:
            errors.append(f"la celda de código {index} no compila: {exc.msg}")
    if empty:
        errors.append(f"hay celdas vacías en los índices {empty}")
    if missing:
        errors.append("faltan recursos locales: " + ", ".join(missing))
    if "flowchart " in source or "```mermaid" in source:
        errors.append("el cuaderno todavía contiene Mermaid visible")
    required_snippets = [
        "Sesión 2 — De una necesidad empresarial a una decisión apoyada por datos",
        "VERSIÓN VIGENTE EN COLAB — 14 de agosto de 2026",
        "Administración de procesos de negocio: comprender antes de cambiar",
        "Casos de uso de Big Data en las organizaciones",
        "Inteligencia de negocios tradicional y con Big Data",
        "Arquitectura empresarial: conectar el propósito con la solución",
        "Ciclo de vida de la analítica de Big Data",
        "GitHub como puente para construir el mismo proyecto",
        "base: main",
        "compare: hito/s02-negocio",
        "No pulses **Merge pull request**",
        "hitos/s02/01_decision_proceso.md",
        "hitos/s02/02_caso_arquitectura_accion.md",
        "No debes programar",
        "TOTAL_QUESTIONS = 7",
        "https://raw.githubusercontent.com/jazaineam1/BigData2026/main/assets/diagrams/session2/01_hilo_decision.png",
    ]
    for snippet in required_snippets:
        if snippet not in source:
            errors.append(f"falta el apoyo pedagógico obligatorio: {snippet}")

    for forbidden in [
        "ETL — Extract, Transform, Load",
        "## OLTP —",
        "## Data Warehouse",
        "## Correspondencia con los cuadernos de referencia",
        "# Sesiones 2 y 3",
        "hito/s02-03-negocio",
        "Presentación relámpago",
        "| flujo Git, commits, PR y revisión |",
        "Matriz RACI",
        "Product Owner",
        "patrocinador",
        "data owner",
        "arquitecto de solución",
        "analytics engineer",
        "ML engineer",
        "MLOps",
        "DevOps",
        "SRE",
        "Kafka",
        "Spark",
        "DuckDB",
        "Airflow",
        "git status",
        "git add",
        "git push",
        "working tree",
        "staging",
        "Profundización opcional",
    ]:
        if forbidden in source:
            errors.append(f"el cuaderno contiene texto fuera del alcance estudiantil acordado: {forbidden}")

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
