# -*- coding: utf-8 -*-
"""QA ligero para S14: sin instalar Spark, abrir Databricks ni ejecutar datasets."""
import ast
import json
import re
import sys
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "utils"))
from build_s14_pyspark import BLOQUES  # noqa: E402
from make_notebook import build, md, code  # noqa: E402

NB = ROOT / "Cuadernos/14_PySpark_Compras_Claras.ipynb"
HTML = ROOT / "Presentaciones/s14-de-dask-a-spark.html"

class SlideParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.slide_ids = []
        self.ids = set()
        self.links = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "section" and "slide" in a.get("class", "").split():
            self.slide_ids.append(a.get("id"))
        if tag == "a":
            self.links.append(a.get("href", ""))

def main():
    actual = json.loads(NB.read_text(encoding="utf-8"))
    cells = [md(s) if kind == "markdown" else code(s) for kind, s in BLOQUES]
    assert actual == build(cells), "Generador y notebook S14 no coinciden"
    assert len(cells) >= 40, "Falta profundidad pedagógica"
    codes = [c for c in actual["cells"] if c["cell_type"] == "code"]
    assert len(codes) >= 14
    for i, c in enumerate(codes, 1):
        ast.parse("".join(c["source"]), filename=f"S14 celda {i}")
    txt = "\n".join("".join(c["source"]) for c in actual["cells"])
    for required in ("FILAS", "PROCEDENCIA", "spark.sql", "repartition(", "explain(", "Paridad PySpark/SQL", "Paridad Spark/SQL/Python", "INDICE_UMBRAL", "expediente", "Bronze", "FORMATO_FINAL", "DESCRIBE HISTORY", "saveAsTable", "VERSIONES_DELTA", "pipeline_demo.fit(train_demo)", "modelo_demo.transform(test_demo)", "HashingTF", "s14_demo_bienes_servicios.csv"):
        assert required in txt, f"Falta contenido: {required}"
    page = HTML.read_text(encoding="utf-8")
    parser = SlideParser()
    parser.feed(page)
    assert len(parser.slide_ids) == 24, f"Diapositivas: {len(parser.slide_ids)}"
    assert parser.slide_ids == [f"s{i}" for i in range(1,25)]
    for required in ("case", "op", "parts", "calc", "checks", "route", "prev", "next"):
        assert required in parser.ids, f"Falta control activo {required}"
    assert any("Cuadernos/14_PySpark_Compras_Claras.ipynb" in u for u in parser.links)
    catalog = json.loads((ROOT / "lms/data/course.json").read_text(encoding="utf-8"))
    s14 = next(s for s in catalog["sessions"] if s["n"] == 14)
    assert s14["status"] == "visible"
    assert "Presentaciones/s14-de-dask-a-spark.html#s1" in s14["entry"]["url"]
    s15 = next(s for s in catalog["sessions"] if s["n"] == 15)
    assert s15["status"] == "draft"
    assert "Databricks" not in s15["title"], "Databricks no debe repetirse en S15"
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    assert 'data-n="14"' in index
    assert "Presentaciones/s14-de-dask-a-spark.html#s1" in index
    assert "Cuadernos/14_PySpark_Compras_Claras.ipynb" in index
    print(f"S14 QA estático OK: {len(cells)} celdas, {len(codes)} códigos, 24 diapositivas, enlaces y curso.")

if __name__ == "__main__":
    main()
