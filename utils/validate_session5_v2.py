#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida la base S5 después de la auditoría docente/estudiante.

Los tutoriales vigentes v3 se validan en validate_session5_v4.py. Este validador
conserva los controles históricos de datos, hilo, interpretación y assets v2,
pero no obliga al notebook a seguir enlazando una versión visual anterior.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "5_Atlas_Cassandra_Query_First.ipynb"
BASE = ROOT / "utils" / "build_session5_notebook.py"
IMPROVE = ROOT / "utils" / "improve_session5_v2.py"
ATLAS = ROOT / "assets" / "tutoriales" / "atlas-s05-pipelines-vistas-v2.html"
ASTRA = ROOT / "assets" / "tutoriales" / "astra-cassandra-paso-a-paso-v2.html"
QUIZ = ROOT / "evaluaciones" / "quiz_sesiones_1_a_4_borrador.md"


def csrc(cell: dict) -> str:
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def main() -> None:
    errors: list[str] = []

    for path in (NB, BASE, IMPROVE, ATLAS, ASTRA, QUIZ):
        if not path.is_file():
            errors.append(f"No existe {path.relative_to(ROOT)}")
    if errors:
        raise SystemExit("\n".join("[ERROR] " + e for e in errors))

    data = json.loads(NB.read_text(encoding="utf-8"))
    cells = data.get("cells", [])
    sources = [csrc(c) for c in cells]
    text = "\n".join(sources)

    if data.get("nbformat") != 4:
        errors.append("nbformat debe ser 4")
    if len(cells) < 55:
        errors.append(f"S5 tiene solo {len(cells)} celdas; se perdió material")
    if any(not s.strip() for s in sources):
        errors.append("Hay celdas vacías")

    required = [
        "menciones_clasificadas",
        "noticias_entidad",
        "nivel_menciones",
        "Interpretación del embudo",
        "Contrato de resultado",
        "ids_esperados_pd",
        "coinciden_cql_pd",
        "Interpretación del resultado CQL",
        "Ficha del driver",
        "UPDATE verificado",
        "PRIMARY KEY ((corte, departamento), valor_base, id_proceso)",
        "CLUSTERING ORDER BY",
        "Recuperación",
        "Ejercicio",
        "Diagnóstico",
        "Hoja de trucos",
        "Completo | Parcial | Sin evidencia",
        "hito_s05_servicio_prioridades.md",
        "casefold()",
    ]
    for item in required:
        if item not in text:
            errors.append(f"Falta elemento S5: {item!r}")

    for prohibited in [
        "https://jazaineam1.github.io/BigData2026/assets/tutoriales/atlas-s05-pipelines-vistas.html",
        "https://jazaineam1.github.io/BigData2026/assets/tutoriales/astra-cassandra-paso-a-paso.html",
        "quiz_sesiones_1_a_4_borrador",
    ]:
        if prohibited in text:
            errors.append(f"S5 enlaza un recurso que debe quedar fuera: {prohibited}")

    for stale in ["capturas reales de referencia", "Tutorial 2 — Astra/Cassandra con capturas"]:
        if stale in text:
            errors.append(f"Quedó texto visual engañoso: {stale!r}")

    qcalls = text.count("pregunta_interactiva_codificada(") - text.count("def pregunta_interactiva_codificada")
    if qcalls != 3:
        errors.append(f"Se esperaban 3 autoevaluaciones codificadas y hay {qcalls}")
    if "¿Cuál afirmación describe mejor una vista" in text:
        errors.append("La primera autoevaluación sigue visible en crudo")
    if "¿Cuál afirmación puede sostener Laura" in text:
        errors.append("La segunda autoevaluación sigue visible en crudo")

    for label in ["**Cómo se lee.**", "**Qué nos dice.**", "**Qué NO permite concluir todavía.**", "**Error frecuente.**"]:
        if text.count(label) < 4:
            errors.append(f"El rótulo {label} aparece menos de 4 veces")

    for fact in [
        '"baja": 111', '"media": 25', '"alta": 6',
        "assert len(paso1) == 163", "assert len(candidatos) == 77", "assert con_referencia == 0",
        "fillna(0).eq(0)",
    ]:
        if fact not in text:
            errors.append(f"Falta control reproducible: {fact}")

    secret_patterns = {
        "token Astra": r"AstraCS:[A-Za-z0-9_-]{20,}",
        "token GitHub": r"(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}",
        "clave privada": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    }
    for label, pattern in secret_patterns.items():
        if re.search(pattern, text):
            errors.append(f"Posible secreto publicado: {label}")

    atlas = ATLAS.read_text(encoding="utf-8")
    for item in [
        "Atlas: una vista que sí viaja",
        "menciones-clasificadas-v1.json",
        "clasificar-menciones-v1",
        "menciones_clasificadas",
        "Save → Save as",
        "Save → Create view",
        "6 + 25 + 111 = 142",
        "Representación, no captura",
        "Pantalla",
    ]:
        if item not in atlas:
            errors.append(f"Tutorial Atlas v2 incompleto: {item!r}")
    if "Paso 2 · calentamiento" in atlas or (
        "Abre Aggregations en modo Texto" in atlas and "resumen-secciones-v1" in atlas
    ):
        errors.append("Tutorial Atlas v2 conserva la ruta larga de S4")

    astra = ASTRA.read_text(encoding="utf-8")
    for item in [
        "Fraunces", "IBM Plex Sans", "Serverless (non-vector)", "token@cqlsh&gt;",
        "noticias_entidad int", "nivel_menciones text", "Connection details",
        "Download SCB", "Generate token", "representación", "mismos IDs y orden que pandas",
        "3,'baja','pendiente'", "Pantalla",
    ]:
        if item not in astra:
            errors.append(f"Tutorial Astra v2 incompleto: {item!r}")
    for bad_host in ("docs.vectorize.io", "miro.medium.com", "learn.microsoft.com"):
        if bad_host in astra:
            errors.append(f"Tutorial Astra usa imagen externa no controlada: {bad_host}")
    if "entidad en prensa; contratación directa; 0 respuestas');" in astra and "'entidad en prensa; contratación directa; 0 respuestas'" not in astra:
        errors.append("El criterio del INSERT Astra quedó sin comillas CQL")

    quiz = QUIZ.read_text(encoding="utf-8")
    if "NO ENLAZAR EN LA PÁGINA DEL CURSO" not in quiz:
        errors.append("El borrador del quiz perdió su regla de no enlace")

    if errors:
        print("Validación S5 base fallida:")
        for e in errors:
            print("[ERROR]", e)
        raise SystemExit(1)

    print(f"[OK] S5 base válida: {len(cells)} celdas; JSON válido y sin celdas vacías.")
    print("[OK] Hilo: vista Atlas → bandeja enriquecida → contrato pandas → Cassandra → verificación cruzada.")
    print("[OK] Cuatro rótulos de interpretación, hito individual y rúbrica observable presentes.")
    print("[OK] Assets v2 históricos siguen íntegros; enlaces vigentes se validan en S5 v4.")
    print("[OK] Quiz S1–S4 sigue en el repo, pero fuera de enlaces de S5.")
    print("[INFO] Astra real requiere prueba manual con cuenta autorizada; CI no usa credenciales.")


if __name__ == "__main__":
    main()
