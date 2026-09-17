#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida datos, sintaxis, sincronía y seguridad de S06 sin credenciales Aura."""
from __future__ import annotations

import ast
import base64
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.notebook_checks import check_question_widget_renders

NB = ROOT / "Cuadernos" / "6_Neo4j_Contexto_Relacional.ipynb"
DATA = ROOT / "Datos" / "s06_contexto_relacional.csv"
MANIFEST = ROOT / "Datos" / "s06_contexto_relacional_manifest.json"
AURA = ROOT / "assets" / "tutoriales" / "neo4j-aura-s06-paso-a-paso.html"
GRAPH = ROOT / "assets" / "tutoriales" / "neo4j-graph-lab-s06.html"
CHECKLIST = ROOT / "assets" / "tutoriales" / "s06-laboratorio-guiado.html"
GEN = ROOT / "utils" / "build_session6_notebook.py"
DATA_GEN = ROOT / "utils" / "build_session6_graph_data.py"


def src(cell):
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def main():
    errors: list[str] = []
    for path in (NB, DATA, MANIFEST, AURA, GRAPH, CHECKLIST, GEN, DATA_GEN):
        if not path.is_file():
            errors.append(f"Falta {path.relative_to(ROOT)}")
    if errors:
        raise SystemExit("\n".join(errors))

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected_manifest = {
        "candidatos_s05": 77,
        "historicos_adjudicados": 2032,
        "entidades_candidatas_con_historial_por_nit": 28,
        "mediana_maximo_conectadas_por_nit": 21,
    }
    for key, expected in expected_manifest.items():
        if manifest.get(key) != expected:
            errors.append(f"Manifest {key}: esperado {expected}, obtenido {manifest.get(key)}")
    if manifest.get("proveedores_compartidos_entre_entidades", 0) <= 0:
        errors.append("Falta el patrón relacional central: proveedores compartidos entre entidades")
    if not manifest.get("ancla_pedagogica", {}).get("id_proceso"):
        errors.append("Falta ancla pedagógica")

    size_mb = DATA.stat().st_size / 1024 / 1024
    if size_mb > 60:
        errors.append(f"El extracto pesa {size_mb:.1f} MB; demasiado para la práctica")

    nb = json.loads(NB.read_text(encoding="utf-8"))
    cells = nb.get("cells", [])
    if nb.get("nbformat") != 4:
        errors.append("nbformat debe ser 4")
    if len(cells) < 35:
        errors.append(f"S6 tiene pocas celdas: {len(cells)}")
    if any(not src(c).strip() for c in cells):
        errors.append("S6 contiene celdas vacías")

    # El notebook guardado debe ser exactamente lo que produce el generador.
    from utils.build_session6_notebook import build_cells
    try:
        generated = build_cells()
        if cells != generated:
            errors.append("Generador y cuaderno S6 desincronizados")
    except Exception as exc:
        errors.append(f"build_cells() falló: {exc}")

    # Todas las celdas Python deben parsear.
    questions = []
    for i, cell in enumerate(cells, 1):
        if cell.get("cell_type") != "code":
            continue
        body = src(cell)
        try:
            ast.parse(body)
        except SyntaxError as exc:
            errors.append(f"Sintaxis inválida en celda {i}: {exc}")
        match_q = re.search(r'^pregunta_codificada\("([^\"]+)"\)', body, re.M)
        if match_q:
            try:
                q = json.loads(base64.b64decode(match_q.group(1)))
                questions.append(q)
                if len(q.get("opciones", [])) != 4 or len(q.get("retro", [])) != 4:
                    errors.append(f"Pregunta {q.get('numero')} sin cuatro opciones/retroalimentaciones")
                if not q.get("contexto") or not 0 <= q.get("correcta", -1) < 4:
                    errors.append(f"Pregunta {q.get('numero')} sin contexto o respuesta válida")
            except Exception as exc:
                errors.append(f"No se pudo decodificar pregunta en celda {i}: {exc}")

    if [q.get("numero") for q in questions] != list(range(1, 11)):
        errors.append("Se esperan diez preguntas consecutivas")
    if questions and any(q.get("total") != len(questions) for q in questions):
        errors.append("Contador de preguntas incorrecto")

    # El motor del widget también debe seguir renderizando.
    generator_text = GEN.read_text(encoding="utf-8")
    match = re.search(r"INTERACTIVITY = r'''(.*?)'''", generator_text, re.S)
    if not match:
        errors.append("No se encontró INTERACTIVITY en el generador")
    else:
        errors.extend(check_question_widget_renders(match.group(1)))

    # Los tres apoyos web deben ser HTML completos y legibles en móvil.
    for path in (AURA, GRAPH, CHECKLIST):
        html = path.read_text(encoding="utf-8")
        for required in ("<!doctype html>", 'lang="es"', 'name="viewport"'):
            if required not in html.lower() if required == "<!doctype html>" else required not in html:
                errors.append(f"{path.name} incompleto: falta {required}")
        if "<title>" not in html.lower():
            errors.append(f"{path.name} sin título")

    text = "\n".join(src(c) for c in cells)
    secret_patterns = [
        r"neo4j\+s://[A-Za-z0-9.-]+\.databases\.neo4j\.io",
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        r"github_pat_[A-Za-z0-9_]{20,}",
    ]
    for pattern in secret_patterns:
        if re.search(pattern, text):
            errors.append("Posible secreto o endpoint personal publicado")

    if errors:
        print("Validación S6 fallida:")
        for error in errors:
            print("[ERROR]", error)
        raise SystemExit(1)

    print(f"[OK] S6 estructuralmente válida: {len(cells)} celdas; datos {size_mb:.1f} MB")
    print("[OK] Notebook sincronizado con generador; preguntas y Python parsean")
    print("[OK] 77 candidatos / 2032 adjudicaciones / 28 entidades / mediana 21")
    print("[INFO] La pedagogía para principiantes se valida en validate_session6_beginner.py")


if __name__ == "__main__":
    main()
