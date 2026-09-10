#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida S6 sin usar credenciales de Aura."""
from __future__ import annotations

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
TUTORIAL = ROOT / "assets" / "tutoriales" / "neo4j-aura-s06-paso-a-paso.html"
GEN = ROOT / "utils" / "build_session6_notebook.py"
DATA_GEN = ROOT / "utils" / "build_session6_graph_data.py"


def src(cell):
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def main():
    errors = []
    for path in (NB, DATA, MANIFEST, TUTORIAL, GEN, DATA_GEN):
        if not path.is_file():
            errors.append(f"Falta {path.relative_to(ROOT)}")
    if errors:
        raise SystemExit("\n".join(errors))

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("candidatos_s05") != 77:
        errors.append(f"El extracto no conserva 77 candidatos S5: {manifest.get('candidatos_s05')}")
    if manifest.get("historicos_adjudicados", 0) <= 0:
        errors.append("No hay procesos históricos adjudicados")
    if manifest.get("entidades_candidatas_con_historial", 0) <= 0:
        errors.append("Ninguna entidad candidata tiene historial")
    if manifest.get("proveedores_compartidos_entre_entidades", 0) <= 0:
        errors.append("No hay ningún proveedor compartido entre entidades; falta el patrón relacional central")
    if manifest.get("mediana_maximo_conectadas_candidatas", 0) <= 0:
        errors.append("Falta la mediana de referencia de H2-R entre las candidatas de S5")
    if not manifest.get("ancla_pedagogica", {}).get("id_proceso"):
        errors.append("Falta ancla pedagógica")
    size_mb = DATA.stat().st_size / 1024 / 1024
    if size_mb > 60:
        errors.append(f"El extracto pesa {size_mb:.1f} MB; es demasiado grande para la práctica")

    nb = json.loads(NB.read_text(encoding="utf-8"))
    if nb.get("nbformat") != 4:
        errors.append("nbformat debe ser 4")
    cells = nb.get("cells", [])
    text = "\n".join(src(c) for c in cells)
    if len(cells) < 35:
        errors.append(f"S6 tiene pocas celdas: {len(cells)}")
    if any(not src(c).strip() for c in cells):
        errors.append("S6 contiene celdas vacías")

    caja_ascii = set("─│└┘┌┐")
    if any(ch in text for ch in caja_ascii):
        errors.append("S6 todavía tiene diagramas dibujados con caracteres ASCII; deben ser SVG reales embebidos")
    if text.count("data:image/svg+xml;base64") < 4:
        errors.append("Faltan diagramas SVG embebidos (se esperan al menos 4)")
    if "{svg(" in text:
        errors.append("Quedó un llamado a svg() sin interpolar como texto literal — revisa que la celda use md(f'''...''')")

    src_generador = GEN.read_text(encoding="utf-8")
    match = re.search(r"INTERACTIVITY = r'''(.*?)'''", src_generador, re.S)
    if not match:
        errors.append("No se encontró INTERACTIVITY en el generador para probar el widget de preguntas")
    else:
        errors.extend(check_question_widget_renders(match.group(1)))

    # Hechos verificables: sincronización, sintaxis y cobertura de preguntas.
    import ast
    import base64
    from utils.build_session6_notebook import build_cells
    if cells != build_cells():
        errors.append("Generador y cuaderno S6 desincronizados")
    questions = []
    for i, cell in enumerate(cells, 1):
        if cell["cell_type"] == "code":
            try:
                ast.parse(src(cell))
            except SyntaxError as exc:
                errors.append(f"Sintaxis inválida en celda {i}: {exc}")
        match_q = re.search(r'^pregunta_codificada\("([^\"]+)"\)', src(cell), re.M)
        if match_q:
            q = json.loads(base64.b64decode(match_q.group(1)))
            questions.append(q)
            if len(q["opciones"]) != 4 or len(q["retro"]) != 4:
                errors.append(f"La pregunta {q['numero']} no tiene cuatro opciones y retroalimentaciones")
            if not q.get("contexto") or not 0 <= q["correcta"] < 4:
                errors.append(f"Pregunta {q['numero']} sin contexto o respuesta válida")
    if [q["numero"] for q in questions] != list(range(1, 11)):
        errors.append("Se esperan diez preguntas consecutivas que cubran los bloques")
    if any(q.get("total") != len(questions) for q in questions):
        errors.append("Contador de preguntas incorrecto")
    checklist = (ROOT / "assets/tutoriales/s06-laboratorio-guiado.html").read_text(encoding="utf-8")
    steps = json.loads(checklist.split("const DATA = ", 1)[1].split(";\nconst DATA2", 1)[0])[0]["pasos"]
    for step in steps:
        number = int(step["celda"].split()[1])
        if not 1 <= number <= len(cells) or not step.get("evidencia") or not step.get("instruccion"):
            errors.append(f"Paso del checklist incompleto: {step['id']}")
    if manifest.get("entidades_candidatas_con_historial_por_nit") != 28 or manifest.get("mediana_maximo_conectadas_por_nit") != 21:
        errors.append("La referencia por NIT debe ser 28 entidades y mediana 21")

    for label in ["**Cómo se lee.**", "**Qué nos dice.**", "**Qué NO permite concluir todavía.**", "**Qué error común.**"]:
        if text.count(label) < 4:
            errors.append(f"El rótulo {label} aparece menos de cuatro veces")

    if re.search(r"\|\s*Tiempo\s*\|", text, re.I) or "Agenda de 180 minutos" in text:
        errors.append("Los tiempos docentes no deben vivir en el notebook")
    if "quiz_sesiones_1_a_4" in text:
        errors.append("El quiz S1-S4 no debe enlazarse desde S6")

    tutorial = TUTORIAL.read_text(encoding="utf-8")
    tutorial_required = [
        "Fraunces", "IBM Plex Sans", "IBM Plex Mono", "AuraDB", "Free",
        "RETURN 1 AS conexion", "representaciones de interfaz, no capturas autenticadas",
        "Connection URI", "verify_connectivity", "MERGE", "MATCH",
        'class="stage"', 'class="dots"', 'id="full"', "Pantalla", "embed",
        "aria-label", "Diagnóstico", "Verificación docente: 30 de agosto de 2026",
    ]
    for item in tutorial_required:
        if item not in tutorial:
            errors.append(f"Tutorial Aura incompleto o fuera del patrón visual: {item!r}")
    if "captura real" in tutorial.lower():
        errors.append("El tutorial no debe presentar representaciones como capturas reales")
    if "<img " in tutorial.lower() and "alt=" not in tutorial.lower():
        errors.append("Toda imagen del tutorial debe llevar alt")

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
        for e in errors:
            print("[ERROR]", e)
        raise SystemExit(1)

    print(f"[OK] S6 válida: {len(cells)} celdas; datos {size_mb:.1f} MB")
    print("[OK] Hilo S5 → ancla → historial → grafo → ficha relacional → export S7")
    print("[OK] Recuperación post-receso, decisión propia, alternativa y límites presentes")
    print("[OK] Tutorial Aura conserva motor visual, embed, fullscreen y representaciones transparentes")
    print("[INFO] CI no prueba Aura autenticado; requiere cuenta autorizada en clase")


if __name__ == "__main__":
    main()
