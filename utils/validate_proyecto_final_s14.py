#!/usr/bin/env python3
"""Validación rápida (offline, stdlib) del proyecto final S14.

NO ejecuta Dask, Spark, OCR, modelos, API, ni pruebas de navegador;
no descarga datos y no activa servicios de pago.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "Cuadernos/Proyecto_Final_Compras_Claras.ipynb"
EXPLORER = ROOT / "Presentaciones/proyecto-final-explorer.html"
PLAN = ROOT / "docs/PROYECTO_FINAL_S14_2026_PLAN.md"


def comprobar() -> None:
    for archivo in (NOTEBOOK, EXPLORER, PLAN):
        assert archivo.is_file(), f"Falta archivo: {archivo}"
        assert archivo.stat().st_size < 250_000, f"Material excesivo: {archivo}"

    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert nb["nbformat"] == 4 and len(nb["cells"]) >= 16
    codigos = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
    textos = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "markdown"]
    codigo = "\n".join(codigos)
    texto = "\n".join(textos)

    for n in range(8):
        assert re.search(r"## E" + str(n) + r"\b", texto), f"Falta etapa E{n}"
    for token in ("ThreadPoolExecutor", "requests.get", "Retry-After",
                  "S13.leer_etiquetados", "S13.separar_muestra",
                  "from distributed import Client", "compute()",
                  "S13.experimentos_distribuidos", "spark.table(TABLA_SUBIDA)",
                  "saveAsTable", "Tokenizer", "HashingTF", "IDF",
                  "LogisticRegression", "F1_MACRO", "manifest_final.json"):
        assert token in codigo, f"Falta mecanismo ejecutable: {token}"

    assert 'max_workers=2' in codigo, "La descarga educativa debe usar dos hilos"
    assert "OFFSETS = [0, 20]" in codigo and "20" in codigo
    assert 'if "dbutils" not in globals():' in codigo, "Separar Codespaces de Databricks"
    assert not re.search(r"\b(OPENAI_API_KEY|AWS_SECRET_ACCESS_KEY)\s*=\s*['\"]\w", codigo)

    for titulo in ("Cómo se lee", "Qué nos dice", "Qué NO permite concluir", "Qué error común"):
        assert texto.count(titulo) >= 7, f"Interpretación insuficiente: {titulo}"

    html = EXPLORER.read_text(encoding="utf-8")
    for n in range(1, 15):
        assert f"S{n:02d} ·" in html, f"Falta ficha S{n:02d}"
    for token in ('id="ruta"', 'id="conceptos"', 'id="dask"',
                  'id="busqueda"', 'id="databricks"', 'localStorage',
                  'aria-live='):
        assert token in html, f"Falta componente HTML: {token}"
    assert "sintética" in html.lower() and "no es una ejecución dask" in html.lower(), (
        "No confundir simulación con ejecución real")

    plan = PLAN.read_text(encoding="utf-8")
    assert "No se modela fraude" in plan
    assert "1.000" in plan
    assert "10.000" in plan and "NO" in plan
    assert "pendiente" in plan.lower()
    puntos = [
        int(m.group(1))
        for line in plan.splitlines()
        if line.startswith("| ") and re.search(r"\| (\d+) \|", line)
        for m in [re.search(r"\| (\d+) \|", line)]
    ]
    assert sum(puntos) == 100, f"Rúbrica debe sumar 100 (encontrado {sum(puntos)})"
    print("Proyecto final S14: estructura, ruta, alcance, rúbrica y HTML OK (offline).")


if __name__ == "__main__":
    comprobar()
