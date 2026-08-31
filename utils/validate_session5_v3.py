#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida las adiciones de continuidad S3→S5→S6."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "5_Atlas_Cassandra_Query_First.ipynb"

nb = json.loads(NB.read_text(encoding="utf-8"))
text = "\n".join(
    "".join(c.get("source", [])) if isinstance(c.get("source", []), list) else str(c.get("source", ""))
    for c in nb["cells"]
)

required = [
    "CONTINUIDAD S03-S05",
    "prototipo exploratorio",
    "bandeja operacional",
    "s05_ancla_s06.json",
    "PUENTE S05-S06",
    "seleccion_ancla",
    "origen_eleccion_s06",
    '"criterio_priorizacion": "entidad en prensa; contratación directa; 0 respuestas"',
    '"origen": "bandeja operacional S05: 1.000→163→77"',
    "Interpretación del ancla elegida",
    "qué relaciones alrededor de su entidad",
    "noticias_entidad",
    "nivel_menciones",
]
missing = [x for x in required if x not in text]
if missing:
    raise SystemExit("Faltan marcadores S5 v3: " + ", ".join(missing))

if len(nb.get("cells", [])) < 60:
    raise SystemExit("S5 quedó demasiado corta tras la regeneración")

for label in ["**Cómo se lee.**", "**Qué nos dice.**", "**Qué NO permite concluir todavía.**", "**Error frecuente.**"]:
    if text.count(label) < 5:
        raise SystemExit(f"S5 perdió interpretación estructurada: {label}")

print(f"[OK] S5 v3 válida: {len(nb['cells'])} celdas; puente S6 individual y explicable presente.")
