#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida la capa final Graph Lab de S06 sin requerir credenciales Aura."""
from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "6_Neo4j_Contexto_Relacional.ipynb"
TUTORIAL = ROOT / "assets" / "tutoriales" / "neo4j-aura-s06-paso-a-paso.html"
CHECKLIST = ROOT / "assets" / "tutoriales" / "s06-laboratorio-guiado.html"


def src(cell: dict) -> str:
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def main() -> None:
    errors: list[str] = []
    for path in (NB, TUTORIAL, CHECKLIST):
        if not path.is_file():
            errors.append(f"Falta {path.relative_to(ROOT)}")
    if errors:
        raise SystemExit("\n".join(errors))

    nb = json.loads(NB.read_text(encoding="utf-8"))
    cells = nb.get("cells", [])
    text = "\n".join(src(cell) for cell in cells)

    if nb.get("nbformat") != 4:
        errors.append("nbformat debe ser 4")
    if len(cells) != 79:
        errors.append(f"La edición Graph Lab debe conservar 79 celdas; hay {len(cells)}")
    if any(not src(cell).strip() for cell in cells):
        errors.append("Hay celdas vacías")
    ids = [cell.get("id") for cell in cells if cell.get("id")]
    if len(ids) != len(set(ids)):
        errors.append("Hay IDs de celda duplicados")

    code_count = 0
    for i, cell in enumerate(cells, 1):
        if cell.get("cell_type") == "code":
            code_count += 1
            try:
                ast.parse(src(cell))
            except SyntaxError as exc:
                errors.append(f"Sintaxis inválida en celda {i}: {exc}")
    if code_count != 38:
        errors.append(f"Se esperaban 38 celdas de código; hay {code_count}")

    required = [
        "USAR_MI_ANCLA_S5",
        "s05_ancla_s06.json",
        'RELACION_PROCESO_PROVEEDOR = "____"',
        "# 4. Graph Lab",
        "Graph / Table / RAW",
        "consulta_graph_basico",
        "grado_adjudicaciones",
        "entidades_conectadas",
        "consulta_wow_global",
        "consulta_wow_ancla",
        "# 5. Ahora sí: H2-R y el contrato pandas",
        "resultado_completo_pd",
        "pandas == Neo4j",
        "p.precio_base",
        "a.valor_adjudicado",
        'OPERADOR_EXCLUSION = "____"',
        "hitos/s06/",
        "s06_contexto_procesos.jsonl",
        "Abre el commit, no solo el archivo",
    ]
    for item in required:
        if item not in text:
            errors.append(f"Falta contenido Graph Lab: {item!r}")

    if "p.valor = fila.precio_base" in text:
        errors.append("La propiedad de Proceso no debe llamarse valor; usa precio_base")
    if text.find("# 4. Graph Lab") > text.find("# 5. Ahora sí: H2-R y el contrato pandas"):
        errors.append("Graph Lab debe aparecer antes de H2-R")

    tutorial = TUTORIAL.read_text(encoding="utf-8")
    tutorial_required = [
        "Graph", "Table", "RAW", "Fit to screen", "WOW 1", "WOW 2",
        "Grado directo", "ADJUDICADO_A", "RETURN camino", "grado_adjudicaciones",
        "entidades_conectadas", "17 de septiembre de 2026",
    ]
    for item in tutorial_required:
        if item not in tutorial:
            errors.append(f"Tutorial visual incompleto: {item!r}")
    slides = tutorial.count('<section class="slide')
    if slides < 19:
        errors.append(f"El tutorial Graph Lab debe tener al menos 19 pantallas; tiene {slides}")
    if "más conexiones no significa" not in tutorial.lower() and "no significa irregularidad" not in tutorial.lower():
        errors.append("El tutorial debe separar conectividad visual de irregularidad")

    checklist = CHECKLIST.read_text(encoding="utf-8")
    try:
        payload = checklist.split("const DATA = ", 1)[1].split(";\nconst DATA2", 1)[0]
        data = json.loads(payload)
        steps = data[0]["pasos"]
        step_ids = {step["id"] for step in steps}
        for required_id in {"graph", "grado", "wow", "wow2", "entrega"}:
            if required_id not in step_ids:
                errors.append(f"Checklist sin paso {required_id}")
        for step in steps:
            if not step.get("instruccion") or not step.get("evidencia"):
                errors.append(f"Paso incompleto en checklist: {step.get('id')}")
    except Exception as exc:
        errors.append(f"No se pudo leer el checklist: {exc}")

    if errors:
        print("Validación Graph Lab fallida:")
        for error in errors:
            print("[ERROR]", error)
        raise SystemExit(1)

    print(f"[OK] Graph Lab final: {len(cells)} celdas / {code_count} de código / {slides} pantallas Aura")
    print("[OK] S5 opcional + respaldo explícito; patrón editable; Graph Lab antes de H2-R")
    print("[OK] Grado directo separado de entidades a dos saltos; WOW global y WOW del ancla")
    print("[OK] Tutorial Query Graph/Table/RAW y checklist sincronizados con entrega privada")


if __name__ == "__main__":
    main()
