#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida S6 sin usar credenciales de Aura."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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
    if len(cells) < 25:
        errors.append(f"S6 tiene pocas celdas: {len(cells)}")
    if any(not src(c).strip() for c in cells):
        errors.append("S6 contiene celdas vacías")

    required = [
        "Laura ya sabe qué proceso revisar primero",
        "s05_ancla_s06.json",
        "ficha relacional de revisión",
        "Entidad)-[:PUBLICA]",
        "ADJUDICADO_A",
        "Contrato de resultado: primero pandas",
        "esperado_pd",
        "pandas == Neo4j",
        "verify_connectivity",
        "CREATE CONSTRAINT entidad_nit IF NOT EXISTS",
        "UNWIND $filas AS fila",
        "MERGE (e:Entidad",
        "S06-DEMO",
        "hito_s06_ficha_relacional.md",
        "s06_contexto_procesos.jsonl",
        "Completo | Parcial | Sin evidencia",
        "Elasticsearch/BM25",
    ]
    for item in required:
        if item not in text:
            errors.append(f"Falta elemento S6: {item!r}")

    for label in ["**Cómo se lee.**", "**Qué nos dice.**", "**Qué NO permite concluir todavía.**", "**Error frecuente.**"]:
        if text.count(label) < 2:
            errors.append(f"El rótulo {label} aparece menos de dos veces")

    if re.search(r"\|\s*Tiempo\s*\|", text, re.I) or "Agenda de 180 minutos" in text:
        errors.append("Los tiempos docentes no deben vivir en el notebook")
    if "quiz_sesiones_1_a_4" in text:
        errors.append("El quiz S1-S4 no debe enlazarse desde S6")

    tutorial = TUTORIAL.read_text(encoding="utf-8")
    for item in ["Fraunces", "IBM Plex Sans", "AuraDB", "Free", "RETURN 1 AS conexion", "representaciones", "Connection URI", "verify_connectivity", "MERGE", "MATCH"]:
        if item not in tutorial:
            errors.append(f"Tutorial Aura incompleto: {item!r}")
    if "captura real" in tutorial.lower():
        errors.append("El tutorial no debe presentar representaciones como capturas reales")

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
    print("[OK] Datos reales, límites explícitos y respaldo pedagógico presentes")
    print("[INFO] CI no prueba Aura autenticado; requiere cuenta autorizada en clase")


if __name__ == "__main__":
    main()
