"""Valida contrato y navegación de la sesión S13 (sin bibliotecas externas)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

def main():
    nb = json.loads(read("Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb"))
    assert nb["nbformat"] == 4
    cells = nb["cells"]
    assert len(cells) >= 40
    assert sum(c["cell_type"] == "code" for c in cells) >= 15
    text = "\n".join("".join(c["source"]) for c in cells)
    for needed in ("MapReduce", "Codespaces", "HDFS", "Dask", "TF-IDF", "Parquet", "F1 macro"):
        assert needed in text, f"Falta material pedagógico: {needed}"
    html = read("Presentaciones/s13-de-una-maquina-a-un-cluster.html")
    slides = re.findall(r'<section class="slide(?: active)?" id="s(\d+)"', html)
    assert len(slides) == 60
    assert slides == [str(i) for i in range(1, 61)]
    for required in ("id=\"decisionBox\"", "id=\"hdfsGrid\"", "id=\"quizFinal\"", "S12", "Codespaces"):
        assert required in html, f"Falta en presentación: {required}"
    config = json.loads(read(".devcontainer/s13-distribuido/devcontainer.json"))
    assert "S13" in config["name"]
    assert config["portsAttributes"]["8787"]["visibility"] == "private"
    assert "S13_Codespaces/requirements.txt" in config["postCreateCommand"]
    course = json.loads(read("lms/data/course.json"))
    c13 = next(x for x in course["sessions"] if x["n"] == 13)
    c12 = next(x for x in course["sessions"] if x["n"] == 12)
    assert c13["status"] == "visible"
    assert "s13-de-una-maquina" in c13["entry"]["url"]
    assert c12["assessment"]["due_at"] == "2026-11-15T23:59:59-05:00"
    # Detecta errores de sintaxis en la interacción ANTES de ejecutar Playwright.
    import shutil
    import subprocess
    import tempfile
    script = re.search(r"<script>(.*?)</script>", html, re.DOTALL)
    assert script, "Falta script interactivo"
    if shutil.which("node"):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", encoding="utf-8") as temporal:
            temporal.write(script.group(1))
            temporal.flush()
            subprocess.run(["node", "--check", temporal.name], check=True)
    assert "modelo_distribuido_20k.py" in text
    assert "ACTIVAR_MODELO_26K" in text
    assert "xgboost.dask" in text
    assert "26.000" in html
    assert "id=\"s39\"" in html
    assert config["portsAttributes"]["8502"]["visibility"] == "private"
    index = read("index.html")
    assert index.count('data-n="13"') == 1
    assert index.count('data-session="13"') == 1
    assert 'href="Presentaciones/s13-de-una-maquina-a-un-cluster.html#s1"' in index
    assert not any("____" in "".join(c["source"]) for c in cells if c["cell_type"] == "code")
    print("S13 QA estático: OK · 60 diapositivas ·", len(cells), "celdas · Codespaces · LMS")

if __name__ == "__main__":
    main()
