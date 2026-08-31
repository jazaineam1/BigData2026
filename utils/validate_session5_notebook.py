#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida estructura, continuidad pedagógica y hechos verificables de S5."""

from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "5_Atlas_Cassandra_Query_First.ipynb"
ATLAS = ROOT / "assets" / "tutoriales" / "atlas-s05-pipelines-vistas.html"
ASTRA = ROOT / "assets" / "tutoriales" / "astra-cassandra-paso-a-paso.html"
BUILDER = ROOT / "utils" / "build_session5_notebook.py"

REQUIRED = [
    "Sesión 5 — De una vista de Atlas a una consulta operacional con Cassandra",
    "atlas-s05-pipelines-vistas.html",
    "astra-cassandra-paso-a-paso.html",
    "menciones_clasificadas",
    '"baja": 111',
    '"media": 25',
    '"alta": 6',
    "assert len(paso1) == 163",
    "assert len(candidatos) == 77",
    "assert con_referencia == 0",
    "PRIMARY KEY ((corte, departamento), valor_base, id_proceso)",
    "CLUSTERING ORDER BY",
    "cassandra-driver",
    "Secure Connect Bundle",
    "Connection details",
    "RECUPERACIÓN S05",
    "EJERCICIO S05-PK",
    "EVIDENCIA INDIVIDUAL S05",
    "CHULETA CQL S05",
    "HOJA DE TRUCOS S05",
    "DIAGNÓSTICO ASTRA S05",
    "departamento_elegido",
    "hito_s05_servicio_prioridades.md",
]

SECRET_PATTERNS = {
    "token Astra": r"AstraCS:[A-Za-z0-9_-]{20,}",
    "token GitHub": r"(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}",
    "clave privada": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
}


def cell_source(cell: dict) -> str:
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def main() -> None:
    errors: list[str] = []
    for p in (NB, ATLAS, ASTRA, BUILDER):
        if not p.is_file():
            errors.append(f"No existe {p.relative_to(ROOT)}")

    if errors:
        for e in errors:
            print("[ERROR]", e)
        raise SystemExit(1)

    data = json.loads(NB.read_text(encoding="utf-8"))
    cells = data.get("cells", [])
    sources = [cell_source(c) for c in cells]
    text = "\n".join(sources)

    if data.get("nbformat") != 4:
        errors.append("nbformat debe ser 4.")
    if len(cells) < 40:
        errors.append(f"El cuaderno tiene solo {len(cells)} celdas; faltan ejercicios/recuperación.")
    if any(not s.strip() for s in sources):
        errors.append("Hay al menos una celda vacía.")

    for required in REQUIRED:
        if required not in text:
            errors.append(f"Falta el elemento requerido: {required!r}")

    if "atlas-laboratorio-consultas.html" in text:
        errors.append("S5 todavía apunta al tutorial Atlas completo de S4.")

    questions = text.count("pregunta_interactiva(") - 1
    if questions != 3:
        errors.append(f"Se esperaban 3 preguntas formativas y hay {questions}.")

    if "0 de 77" not in text and "0/77" not in text:
        errors.append("Falta el límite explícito 0 de 77.")
    if "fillna(0).eq(0)" not in text:
        errors.append("Falta el contraejemplo que distingue faltante de cero.")
    if ".casefold()" not in text:
        errors.append("La búsqueda literal debe normalizar mayúsculas/minúsculas con casefold().")

    for label, pattern in SECRET_PATTERNS.items():
        if re.search(pattern, text):
            errors.append(f"Posible secreto publicado: {label}.")

    atlas = ATLAS.read_text(encoding="utf-8")
    for item in [
        "solo lo que falta",
        "14-atlas-data-explorer-colecciones.png",
        "16-atlas-filtros-regex.png",
        "18-atlas-pipeline-resumen.png",
        "menciones_clasificadas",
        "clasificar-noticias-v1",
        "ampliación",
    ]:
        if item not in atlas:
            errors.append(f"Tutorial Atlas S5 incompleto: falta {item!r}.")

    astra = ASTRA.read_text(encoding="utf-8")
    for item in [
        "Fraunces",
        "IBM Plex Sans",
        "Serverless (non-vector)",
        "token@cqlsh",
        "CQL mínimo",
        "Connection details",
        "Diagnóstico",
        "SCB",
    ]:
        if item not in astra:
            errors.append(f"Tutorial Astra incompleto: falta {item!r}.")
    if any(host in astra for host in ("docs.vectorize.io", "miro.medium.com", "learn.microsoft.com")):
        errors.append("El tutorial Astra conserva capturas externas contradictorias.")

    if errors:
        print("Validación fallida:")
        for e in errors:
            print("[ERROR]", e)
        raise SystemExit(1)

    print(f"[OK] Sesión 5 válida: {len(cells)} celdas, 3 preguntas formativas.")
    print("[OK] Atlas S5 reducido, Astra alineado visualmente, recuperación de runtime y evidencia individual presentes.")
    print("[OK] Hechos esperados: 142 entidades; 111/25/6; 1000→163→77; 0/77.")
    print("[INFO] La validación automática no sustituye iniciar sesión y probar Astra con una cuenta real.")


if __name__ == "__main__":
    main()
