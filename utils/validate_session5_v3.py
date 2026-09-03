#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida continuidad real S4→S5→S6 y defectos de regeneración ya detectados."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "5_Atlas_Cassandra_Query_First.ipynb"

nb = json.loads(NB.read_text(encoding="utf-8"))
texts = [
    "".join(c.get("source", [])) if isinstance(c.get("source", []), list) else str(c.get("source", ""))
    for c in nb["cells"]
]
text = "\n".join(texts)

required = [
    "Deuda abierta",
    "la clase terminó con datos, no con una decisión",
    "De datos persistidos en Atlas a una consulta operacional con Cassandra",
    "evidencia que ya dejó persistida en Atlas en una bandeja priorizada",
    "Continuidad",
    "prototipo exploratorio",
    "bandeja operacional",
    "s05_ancla_s06.json",
    "Puente hacia la sesión 6",
    "seleccion_ancla",
    "origen_eleccion_s06",
    '"criterio_priorizacion": "entidad en prensa; contratación directa; 0 respuestas"',
    '"origen": "bandeja operacional S05: 1.000→163→77"',
    "Interpretación del ancla elegida",
    "qué relaciones alrededor de su entidad",
    "noticias_entidad",
    "nivel_menciones",
    "contexto Atlas restaurado",
    ".merge(contexto_menciones, on=\"entidad\", how=\"left\", validate=\"many_to_one\")",
    "Cierre",
    "la pregunta de S4 por fin tiene una respuesta operacional",
]
missing = [x for x in required if x not in text]
if missing:
    raise SystemExit("Faltan marcadores S5 v3: " + ", ".join(missing))

if len(nb.get("cells", [])) < 60:
    raise SystemExit("S5 quedó demasiado corta tras la regeneración")

# Un fallo real encontrado en la auditoría: regeneraciones previas acumulaban
# varias celdas idénticas de cierre de conexiones. Debe quedar exactamente una.
close_cells = [t for t in texts if "#@title Cerrar conexiones" in t]
if len(close_cells) != 1:
    raise SystemExit(f"S5 debe tener exactamente una celda de cierre de conexiones; tiene {len(close_cells)}")
if "CERRAR CONEXIONES S05" not in close_cells[0]:
    raise SystemExit("La celda única de cierre perdió su marcador estable")

# La recuperación debe dejar disponibles las columnas que usa la carga Cassandra.
recovery = next((t for t in texts if "# Recuperación" in t), "")
for token in ["contexto_menciones", "noticias_entidad", "nivel_menciones", "merge(contexto_menciones"]:
    if token not in recovery:
        raise SystemExit(f"La recuperación S5 no restaura {token}")

for label in ["**Cómo se lee.**", "**Qué nos dice.**", "**Qué NO permite concluir todavía.**", "**Error frecuente.**"]:
    if text.count(label) < 5:
        raise SystemExit(f"S5 perdió interpretación estructurada: {label}")

print(
    f"[OK] S5 v3 válida: {len(nb['cells'])} celdas; "
    "S4→S5 explícito, recuperación completa, cierre único y puente S6 presentes."
)
