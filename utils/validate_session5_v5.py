#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida que S5 trate 0/77 como contraste de hipótesis, no como titular."""
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
    "contraste de hipótesis",
    "CONTRASTE DE HIPÓTESIS S05",
    "Hipótesis de trabajo H1",
    "no es un test estadístico inferencial",
    "unidad observada en prensa",
    "unidad que Laura revisa",
    "HIPÓTESIS REVISADA S05",
    "H2:",
    "formular mejores hipótesis de revisión",
    '"alcance_prensa": "contexto a nivel de entidad; sin referencia exacta del proceso en título/subtítulo"',
    '"hipotesis_h1": "no apoyada por búsqueda literal de referencia exacta en título/subtítulo"',
    "0/77 → refinar alcance de la prensa",
]
missing = [x for x in required if x not in text]
if missing:
    raise SystemExit("Faltan marcadores S5 v5: " + ", ".join(missing))

# El producto ya no debe vender 0/77 como hito central.
if "4. el límite analítico `0 de 77`" in text:
    raise SystemExit("El producto observable todavía presenta 0/77 como titular central")

# Debe conservarse el baseline reproducible: cambia la interpretación, no los datos.
for marker in ["assert con_referencia == 0", "assert len(candidatos) == 77"]:
    if marker not in text:
        raise SystemExit(f"Se perdió baseline reproducible: {marker}")

print(f"[OK] S5 v5 válida: {len(nb['cells'])} celdas; hipótesis, operacionalización y alcance de prensa explícitos.")
