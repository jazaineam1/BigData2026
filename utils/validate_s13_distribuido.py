"""Valida S13 sin instalar dependencias ni iniciar entrenamientos."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def leer(ruta: str) -> str:
    return (ROOT / ruta).read_text(encoding="utf-8")


def main():
    cuaderno = json.loads(leer("Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb"))
    assert cuaderno["nbformat"] == 4
    celdas = cuaderno["cells"]
    assert 45 <= len(celdas) <= 55, f"Cuaderno inesperado: {len(celdas)} celdas"
    codigo = "\n".join("".join(c["source"]) for c in celdas if c["cell_type"] == "code")
    texto = "\n".join("".join(c["source"]) for c in celdas)
    assert sum(c["cell_type"] == "code" for c in celdas) >= 16
    for celda in celdas:
        if celda["cell_type"] == "code":
            compile("".join(celda["source"]), "S13_celda", "exec")
            assert not celda.get("outputs"), "No guardar salidas grandes en el notebook"
    for esperado in (
        "DEMO_DASK_EN_RUN_ALL", "WORKERS_DEMO_S13", "prueba_texto",
        "MapReduce", "Parquet", "LocalCluster", "make_blobs",
        "KMeansDask", "KMeansLocal", "REGISTROS", "VARIABLES",
        "get_task_stream", "OPCIONES_ARQUITECTURA", "OPCIONES_LIMITE",
    ):
        assert esperado in texto, f"Falta el tema o ejemplo: {esperado}"
    assert not re.search(r"(?i)TF-IDF|TfidfVectorizer|UNSPSC|ngram", texto)
    assert "kmeans_dask_s13.py" not in texto
    assert "streamlit run" not in texto
    assert not (ROOT / "Laboratorios/S13_Codespaces/kmeans_dask_s13.py").exists()
    assert not (ROOT / "Laboratorios/S13_Codespaces/test_kmeans_s13_estatico.py").exists()

    presentacion = leer("Presentaciones/s13-de-una-maquina-a-un-cluster.html")
    diapositivas = re.findall(r'<section class="slide(?: active)?" id="s(\d+)"', presentacion)
    assert diapositivas == [str(i) for i in range(1, 25)]
    for x in ('id="decisionBox"', 'id="hdfsGrid"', 'id="quizPrompt"',
              'id="mapRun"', 'id="costRun"', 'id="workerRun"',
              'id="scenarioWorkers"', "K-means", "Codespaces"):
        assert x in presentacion, x
    assert not re.search(r"(?i)TF-IDF|tfidfToyRun|kmeans_dask_s13\.py|streamlit run", presentacion)
    assert 'id="s21"' in presentacion
    assert "REGISTROS" in presentacion and "WORKERS_MODELO" in presentacion
    assert not re.search(r"(?i)(hp del estudiante|tu hp|en mi hp)", presentacion)

    scripts = re.search(r"<script>(.*?)</script>", presentacion, re.DOTALL)
    assert scripts, "Falta interactividad de la presentación"
    if shutil.which("node"):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", encoding="utf-8") as archivo:
            archivo.write(scripts.group(1))
            archivo.flush()
            subprocess.run(["node", "--check", archivo.name], check=True)

    perfil = json.loads(leer(".devcontainer/s13-distribuido/devcontainer.json"))
    assert "S13" in perfil["name"]
    assert "S13_Codespaces/requirements.txt" in perfil["postCreateCommand"]
    paquetes = leer("Laboratorios/S13_Codespaces/requirements.txt")
    assert "dask-ml==2025.1.0" in paquetes
    curso = json.loads(leer("lms/data/course.json"))
    s13 = next(x for x in curso["sessions"] if x["n"] == 13)
    assert s13["status"] == "visible"
    assert "s13-de-una-maquina" in s13["entry"]["url"]
    indice = leer("index.html")
    assert indice.count('data-n="13"') == 1
    assert 'href="Presentaciones/s13-de-una-maquina-a-un-cluster.html#s1"' in indice
    print(f"S13 validada: 24 láminas, {len(celdas)} celdas, 1 cuaderno y K-means numérico")


if __name__ == "__main__":
    main()
