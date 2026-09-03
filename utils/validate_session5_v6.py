#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida el cierre epistemológico de S5 y su puente a S6/S7."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "5_Atlas_Cassandra_Query_First.ipynb"
nb = json.loads(NB.read_text(encoding="utf-8"))
text = "\n".join(
    "".join(c.get("source", [])) if isinstance(c.get("source", []), list) else str(c.get("source", ""))
    for c in nb.get("cells", [])
)

required = [
    "Antes de afirmar: formula una hipótesis que pueda fallar",
    "0/77 → H1 literal refutada",
    "la prensa queda mejor especificada",
    "formular hipótesis",
    "pedir la siguiente evidencia correcta",
    "## Contraste de hipótesis de prensa",
    "Resultado observado: {con_referencia}/77",
    "| Regla + contraste |",
    "H1 + operacionalización + conclusión correcta",
    "una hipótesis refutada produce una pregunta mejor",
    "S6 — especificidad relacional",
    "S7 — especificidad textual",
    "probar una nueva hipótesis con evidencia relacional",
]
missing = [x for x in required if x not in text]
if missing:
    raise SystemExit("Faltan marcadores S5 v6: " + ", ".join(missing))

# No debe reaparecer la cadena antigua donde 0/77 era un resultado central equivalente a 77.
old = "→ 77 candidatos con contratación directa y 0 respuestas\n→ 0/77 referencias de proceso citadas literalmente en títulos/subtítulos"
if old in text:
    raise SystemExit("El cierre antiguo todavía presenta 0/77 como hito central")

print(f"[OK] S5 v6 válida: {len(nb['cells'])} celdas; hipótesis integrada en contenido, hito, rúbrica y puente S6/S7.")
