#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida S5 v7: menor carga cognitiva sin reducir herramientas."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "5_Atlas_Cassandra_Query_First.ipynb"
ASTRA = ROOT / "assets" / "tutoriales" / "astra-cassandra-paso-a-paso-v3.html"


def csrc(cell: dict) -> str:
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


nb = json.loads(NB.read_text(encoding="utf-8"))
text = "\n".join(csrc(c) for c in nb.get("cells", []))
astra = ASTRA.read_text(encoding="utf-8")

required_nb = [
    "Contrato de éxito — tres productos, las mismas herramientas",
    "guía paso a paso",
    "bandeja SECOP",
    "tabla operativa",
    "CRUD + comparación",
    "**1 · Vista Atlas**",
    "**2 · Bandeja explicable**",
    "**3 · Consulta operacional**",
    "Semáforo de código",
    "🧠 **ENTIENDE**",
    "▶️ **EJECUTA**",
    "✏️ **MODIFICA**",
    "Microejemplo en papel",
    "Traducción de la PK en tres pasos",
    "PRODUCTO 3 · Tramo A",
    "Checkpoint",
    "PRODUCTO 3 · Tramo B",
    "No es un cuarto producto ni otro motor",
    "Checkpoint de los tres productos",
    "Python automatiza lo que ya comprendiste en CQL",
    "SCB/token",
    "cassandra-driver",
    "session.execute",
    "menciones_clasificadas",
    "1.000 → 163 → 77",
    "Contraste de hipótesis",
    "s05_ancla_s06.json",
]
missing = [x for x in required_nb if x not in text]
if missing:
    raise SystemExit("Faltan marcadores S5 v7: " + ", ".join(missing))

# No se deben presentar nuevamente nueve elementos como nueve productos separados.
if "### Producto observable de hoy" in text:
    raise SystemExit("S5 v7 volvió a mostrar la lista antigua de productos")

# Deben permanecer las herramientas que el docente pidió conservar.
for tool_marker in [
    "MongoDB Atlas", "pandas", "Astra/CQL", "Colab / Python",
    "Secure Connect Bundle", "Application token", "Cluster", "Session",
]:
    if tool_marker not in text:
        raise SystemExit(f"Se perdió herramienta o componente técnico: {tool_marker}")

required_astra = [
    "Resuélvelo en papel antes de tocar Cassandra",
    "Tres pasos antes de leer la PRIMARY KEY",
    "MISMO PRODUCTO 3 · Tramo B",
    "▶ EJECUTA",
    "🧠 ENTIENDE",
    "✏ MODIFICA",
    "Serverless (non-vector)",
    "CQL console",
    "token@cqlsh&gt;",
    "PRIMARY KEY ((corte, departamento), valor_base, id_proceso)",
    "Connection details",
    "Secure Connect Bundle",
    "Application token",
    "PlainTextAuthProvider",
    "ALLOW FILTERING",
]
missing_astra = [x for x in required_astra if x not in astra]
if missing_astra:
    raise SystemExit("Tutorial Astra v3 incompleto tras v7: " + ", ".join(missing_astra))

# Los dos nuevos apoyos visuales y la transición Python deben existir una sola vez.
for marker in [
    "Resuélvelo en papel antes de tocar Cassandra",
    "Tres pasos antes de leer la PRIMARY KEY",
    "MISMO PRODUCTO 3 · Tramo B",
]:
    if astra.count(marker) != 1:
        raise SystemExit(f"El marcador Astra {marker!r} aparece {astra.count(marker)} veces")

if len(nb.get("cells", [])) < 70:
    raise SystemExit("S5 v7 perdió demasiado material")

print(
    f"[OK] S5 v7 válida: {len(nb['cells'])} celdas; tres productos, mismas herramientas, "
    "roles cognitivos y tutorial Astra progresivo presentes."
)
