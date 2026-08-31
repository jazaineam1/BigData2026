#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida la estructura y los hechos verificables de la sesión 5."""

from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "5_Atlas_Cassandra_Query_First.ipynb"

REQUIRED = [
    "Sesión 5 — De una vista de Atlas a una consulta operacional con Cassandra",
    "atlas-laboratorio-consultas.html",
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
    "hito_s05_servicio_prioridades.md",
]

SECRET_PATTERNS = {
    "token Astra": r"AstraCS:[A-Za-z0-9_-]{20,}",
    "token GitHub": r"(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}",
    "clave privada": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
}

def main() -> None:
    if not NB.is_file():
        raise SystemExit(f"[ERROR] No existe {NB.relative_to(ROOT)}")

    data = json.loads(NB.read_text(encoding="utf-8"))
    cells = data.get("cells", [])
    text = "\n".join("".join(c.get("source", [])) for c in cells)

    errors = []
    if data.get("nbformat") != 4:
        errors.append("nbformat debe ser 4.")
    if len(cells) < 35:
        errors.append(f"El cuaderno tiene solo {len(cells)} celdas; se esperaba una sesión completa.")

    for required in REQUIRED:
        if required not in text:
            errors.append(f"Falta el elemento requerido: {required!r}")

    questions = text.count("pregunta_interactiva(") - 1
    if questions != 3:
        errors.append(f"Se esperaban 3 preguntas formativas y hay {questions}.")

    if "0 de 77" not in text and "0/77" not in text:
        errors.append("Falta el límite explícito 0 de 77.")

    if "fillna(0).eq(0)" not in text:
        errors.append("Falta el contraejemplo que distingue faltante de cero.")

    for label, pattern in SECRET_PATTERNS.items():
        if re.search(pattern, text):
            errors.append(f"Posible secreto publicado: {label}.")

    if errors:
        print("Validación fallida:")
        for e in errors:
            print("[ERROR]", e)
        raise SystemExit(1)

    print(f"[OK] Sesión 5 válida: {len(cells)} celdas, 3 preguntas formativas.")
    print("[OK] Hechos esperados presentes: 142 entidades; 111/25/6; 1000→163→77; 0/77.")
    print("[OK] Dos tutoriales embebidos: Atlas y Astra/Cassandra.")
    print("[INFO] El validador no sustituye la prueba manual en Colab ni la ejecución real en Astra.")

if __name__ == "__main__":
    main()
