#!/usr/bin/env python3
"""Validación rápida (offline, stdlib) del proyecto final S14.

NO ejecuta Dask, Spark, OCR, modelos, API, ni pruebas de navegador;
no descarga datos y no activa servicios de pago.
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "Cuadernos/Proyecto_Final_Compras_Claras.ipynb"
EXPLORER = ROOT / "docs/borradores/proyecto-final-explorer.html"
PLAN = ROOT / "docs/PROYECTO_FINAL_S14_2026_PLAN.md"
VIABILIDAD = ROOT / "docs/PROYECTO_FINAL_S14_VIABILIDAD.md"
GENERADOR = ROOT / "Laboratorios/Proyecto_Final_2026/generar_observatorio.py"
OFFSET = ROOT / "utils/proyecto_final_offset.py"
OFFSET_TEST = ROOT / "tests/test_proyecto_final_offset.py"


def comprobar() -> None:
    for archivo in (NOTEBOOK, EXPLORER, PLAN, VIABILIDAD, GENERADOR, OFFSET, OFFSET_TEST):
        assert archivo.is_file(), f"Falta archivo: {archivo}"
        assert archivo.stat().st_size < 250_000, f"Material excesivo: {archivo}"

    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert nb["nbformat"] == 4 and len(nb["cells"]) >= 16
    codigos = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
    textos = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "markdown"]
    codigo = "\n".join(codigos)
    for n, celda in enumerate(codigos, start=1):
        ast.parse(celda, filename=f"proyecto_final_codigo_{n}.py")
    texto = "\n".join(textos)

    for n in range(8):
        assert re.search(r"## E" + str(n) + r"\b", texto), f"Falta etapa E{n}"
    for token in ("descarga_offset.ejecutar", "requests.get",
                  "S13.leer_etiquetados", "S13.separar_muestra",
                  "from distributed import Client", "compute()",
                  "S13.experimentos_distribuidos", "spark.table(TABLA_SUBIDA)",
                  "saveAsTable", "Tokenizer", "HashingTF", "IDF",
                  "LogisticRegression", "F1_MACRO", "manifest_final.json"):
        assert token in codigo, f"Falta mecanismo ejecutable: {token}"

    offset_src = OFFSET.read_text(encoding="utf-8")
    for token in ("ThreadPoolExecutor", "max_workers=2", "Retry-After",
                  "OFFSET", "$offset", "$limit", ":id ASC", "A_descarga.json"):
        assert token in offset_src, f"Falta mecanismo OFFSET: {token}"
    assert 'if "dbutils" not in globals():' in codigo, "Separar Codespaces de Databricks"
    assert not re.search(r"\b(OPENAI_API_KEY|AWS_SECRET_ACCESS_KEY)\s*=\s*['\"]\w", codigo)

    # Siete microintervenciones que exigen un resultado propio por fase,
    # sin nuevos modelos, fuentes ni tecnología extra.
    microretos = ["E1.1", "E2.1", "E3.1", "E4.1", "E5.1", "E6.1", "E7.1"]
    for reto in microretos:
        assert any(f"### {reto} ·" in t for t in textos), (
            f"Falta microejercicio pedagógico {reto}")
    assert '"H_microretos.json"' in codigo
    assert "manifiesto[\"microretos\"] = resultados_microretos" in codigo
    assert codigo.count("= ____") == 7, (
        "Debe haber exactamente una expresión guiada por E1, E2, E3, E4, E5, E6 y E7.")
    assert "referencia = S13.entrenar_y_evaluar(tabla_curada)" in codigo
    assert "resultado_dask = S13.experimentos_distribuidos(tabla_curada, n_workers=2)" in codigo
    assert not any(line.lstrip().startswith((",assert ", ",resultado_dask=", ",evidencia_d="))
                   for line in codigo.splitlines()), (
        "E4 conserva una coma al inicio y romperá el cuaderno.")

    for titulo in ("Cómo se lee", "Qué nos dice", "Qué NO permite concluir", "Qué error común"):
        assert texto.count(titulo) >= 7, f"Interpretación insuficiente: {titulo}"

    html = EXPLORER.read_text(encoding="utf-8")
    for n in range(1, 15):
        assert f"S{n:02d} ·" in html, f"Falta ficha S{n:02d}"
    for token in ('id="ruta"', 'id="conceptos"', 'id="dask"',
                  'id="busqueda"', 'id="databricks"', 'localStorage',
                  'aria-live='):
        assert token in html, f"Falta componente HTML: {token}"
    assert '<meta name="robots" content="noindex,nofollow">' in html
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
    # No copiar borradores al sitio mientras el usuario lo mantiene en revisión.
    assert not (ROOT / "Presentaciones/proyecto-final-explorer.html").exists()
    pages = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
    assert "Cuadernos/Proyecto_Final_Compras_Claras.ipynb" not in pages, "El cuaderno se publicó en Pages"
    assert "proyecto-final-explorer.html" not in pages, "Explorer no debe estar en artefacto Pages"
    portada = (ROOT / "index.html").read_text(encoding="utf-8")
    lms = (ROOT / "lms/data/course.json").read_text(encoding="utf-8")
    for texto_publicacion in ("proyecto-final-explorer.html", "Proyecto_Final_Compras_Claras.ipynb"):
        assert texto_publicacion not in portada, "El proyecto aún no debe aparecer en portada"
        assert texto_publicacion not in lms, "El proyecto aún no debe aparecer en LMS"
    cod_generador = GENERADOR.read_text(encoding="utf-8")
    for token in ("csv.DictReader", "observatorio.html", "predicciones", "replace", "textContent"):
        assert token in cod_generador, f"Generador incompleto: {token}"
    assert "observatorio.html" in codigo and "generar_observatorio" in codigo
    assert "____" in codigo, "Falta reto de código evaluable"
    assert "GitHub Free" in VIABILIDAD.read_text(encoding="utf-8")
    assert "810" in codigo, "Falta conjunto docente depurado"
    assert "tabla_curada" in codigo and "S13.experimentos_distribuidos(tabla_curada" in codigo
    print("Proyecto final S14: ruta, producto offline, cuota, rúbrica y NO publicación OK (offline).")


if __name__ == "__main__":
    comprobar()
