#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida que S5 v4 conserve hilo, pedagogía y tutoriales v3."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "5_Atlas_Cassandra_Query_First.ipynb"
ATLAS = ROOT / "assets" / "tutoriales" / "atlas-s05-pipelines-vistas-v3.html"
ASTRA = ROOT / "assets" / "tutoriales" / "astra-cassandra-paso-a-paso-v3.html"

nb = json.loads(NB.read_text(encoding="utf-8"))
text = "\n".join(
    "".join(c.get("source", [])) if isinstance(c.get("source", []), list) else str(c.get("source", ""))
    for c in nb.get("cells", [])
)

required = [
    "MICROEJEMPLO SWITCH S05",
    "regla pedagógica versionada",
    "MODELO MENTAL VISTA S05",
    "MICROEJEMPLO MERGE S05",
    'validate="many_to_one"',
    "FUNDAMENTO REGLA S05",
    "heurística pedagógica versionada",
    "probabilidad de irregularidad",
    "impacto económico potencial",
    "MICROEJEMPLO NAN S05",
    "ESCENA OPERACIONAL CASSANDRA S05",
    "GET /prioridades?corte=2026-09-03",
    "MICROEJEMPLO PARTICIONES S05",
    "Partition key",
    "Clustering",
    "MODELO MENTAL ASTRA S05",
    "Serverless (non-vector)",
    "keyspace",
    "MODELO CONEXIÓN PYTHON S05",
    "lugares reservados",
    "UPSERT S05",
    "Cambiar de motor no debería cambiar la decisión de negocio",
    "atlas-s05-pipelines-vistas-v3.html",
    "astra-cassandra-paso-a-paso-v3.html",
]
missing = [x for x in required if x not in text]
if missing:
    raise SystemExit("Faltan marcadores S5 v4: " + ", ".join(missing))

# El control textual puede conservar el rótulo v4 o haber sido refinado por v5.
if "PRECISIÓN 0/77 S05" not in text and "CONTRASTE DE HIPÓTESIS S05" not in text:
    raise SystemExit("Falta el bloque que interpreta el control textual de 0/77")

for path in (ATLAS, ASTRA):
    if not path.exists():
        raise SystemExit(f"Falta tutorial v3: {path}")

atlas = ATLAS.read_text(encoding="utf-8")
astra = ASTRA.read_text(encoding="utf-8")

for marker in [
    "Fraunces", "IBM Plex Sans", "IBM Plex Mono", "embed", "requestFullscreen",
    "aria-label", "Representación, no captura", "menciones_clasificadas",
    "4→baja", "5→media", "20→alta", "no es una segunda copia",
]:
    if marker not in atlas:
        raise SystemExit(f"Tutorial Atlas v3 perdió: {marker}")

for marker in [
    "Fraunces", "IBM Plex Sans", "IBM Plex Mono", "embed", "requestFullscreen",
    "aria-label", "representación", "Serverless (non-vector)", "keyspace",
    "token@cqlsh&gt;", "PRIMARY KEY ((corte, departamento), valor_base, id_proceso)",
    "upsert", "Connection details", "Secure Connect Bundle", "PlainTextAuthProvider",
    "ALLOW FILTERING", "pandas",
]:
    if marker not in astra:
        raise SystemExit(f"Tutorial Astra v3 perdió: {marker}")

if len(nb.get("cells", [])) < 70:
    raise SystemExit("S5 v4 perdió demasiados bloques pedagógicos")

print(f"[OK] S5 v4 válida: {len(nb['cells'])} celdas; microejemplos, negocio y tutoriales v3 presentes.")
