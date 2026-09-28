#!/usr/bin/env python3
"""Higiene del repositorio: que no vuelvan a entrar artefactos generados ni archivos enormes.

Por qué: un archivo que entra a Git se copia en cada clon y sigue en el historial aunque se borre
(bajar el peso real exige reescribir la historia). Las guardias van ANTES de que entre.

Dos reglas:
1. Nada generado: cachés de Python, logs, WAL, .env, node_modules.
2. Ningún archivo versionado supera MAX_MB, salvo los ya existentes de GRANDFATHERED, que
   declaran su razón. La lista solo puede ENCOGER: si un archivo deja de existir y sigue en la
   lista, la guardia falla para que se borre la excepción.

Uso: python utils/check_repo_hygiene.py
"""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAX_MB = 25

FORBIDDEN = [
    (re.compile(r"(^|/)__pycache__/"), "caché de Python"),
    (re.compile(r"\.py[cod]$"), "bytecode de Python"),
    (re.compile(r"^Airflow/logs/"), "logs generados por Airflow"),
    (re.compile(r"\.duckdb\.wal$"), "WAL de DuckDB"),
    (re.compile(r"(^|/)\.env$"), "archivo .env (usa .env.example)"),
    (re.compile(r"(^|/)node_modules/"), "dependencias de Node (usa package-lock.json)"),
    (re.compile(r"(^|/)\.ipynb_checkpoints/"), "checkpoints de Jupyter"),
    (re.compile(r"(^|/)(test-results|playwright-report)/"), "salidas de Playwright"),
]

# Archivos que ya superaban el límite cuando se creó esta guardia. Cada uno tiene su razón y su salida.
GRANDFATHERED = {
    "Cuadernos/datos/secop_chunks/secop_chunk_0000000.csv":
        "datos SECOP que descargan varios cuadernos desde main; moverlos exige actualizar sus enlaces y comprobar cada URL",
    "Cuadernos/datos/secop_chunks/secop_chunk_0100000.csv": "ídem",
    "Cuadernos/datos/secop_chunks/secop_chunk_0200000.csv": "ídem",
    "infraestructura/dask/jobs/benchmark_data/part_04.csv":
        "dato de benchmark que se puede regenerar con el script del job; retirar cuando se confirme cuál lo genera",
    "Airflow/dw.duckdb":
        "el compose lo monta como archivo y DuckDB rechaza un archivo vacío; cambiar el montaje a un directorio requiere probar con Docker",
}


def tracked():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout
    return [f for f in out.decode("utf-8", "replace").split("\0") if f]


errors, warnings = [], []
files = tracked()
present = set(files)

for rel in files:
    for rx, what in FORBIDDEN:
        if rx.search(rel):
            errors.append(f"versionado {what}: {rel}  (quítalo con `git rm --cached` y agrégalo a .gitignore)")
            break

for rel in files:
    p = ROOT / rel
    if not p.is_file():
        continue
    mb = p.stat().st_size / 1048576
    if mb > MAX_MB and rel not in GRANDFATHERED:
        errors.append(f"archivo de {mb:.1f} MB (> {MAX_MB} MB): {rel}  "
                      "(publícalo como GitHub Release o fuente externa y deja en Git un manifiesto con URL, SHA256 y el script que lo genera)")

for rel, why in GRANDFATHERED.items():
    if rel not in present:
        errors.append(f"GRANDFATHERED obsoleto: {rel} ya no está versionado; bórralo de la lista")
    else:
        warnings.append(f"pendiente ({(ROOT / rel).stat().st_size / 1048576:.0f} MB): {rel} — {why}")

pend_mb = sum((ROOT / r).stat().st_size for r in GRANDFATHERED if r in present) / 1048576
print(f"Revisados {len(files)} archivos versionados. Límite por archivo: {MAX_MB} MB.")
if warnings:
    print(f"\nPENDIENTES conocidos ({pend_mb:.0f} MB en total, solo pueden disminuir):")
    for w in warnings:
        print("  -", w)
if errors:
    print("\nHIGIENE: FAIL")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("\nHIGIENE: OK")
