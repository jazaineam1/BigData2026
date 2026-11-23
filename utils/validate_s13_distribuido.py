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
    assert sum(c["cell_type"] == "code" for c in celdas) >= 20
    capitulos = [
        int(re.match(r"## (\d+) ·", "".join(c["source"])).group(1))
        for c in celdas
        if c["cell_type"] == "markdown"
        and re.match(r"## \d+ ·", "".join(c["source"]))
    ]
    assert capitulos == list(range(16)), f"Secciones desordenadas: {capitulos}"
    for requerido in ("MuestraRSS", "pico_por_proceso", "memoria_info",
                      "tiempo_total_local", "tiempo_total_dask",
                      "limites_workers", "modelo_distribuido", "centros_iniciales"):
        if requerido == "memoria_info":
            requerido = "limite_memoria_bytes"
        assert requerido in codigo, f"Falta medición K-means: {requerido}"
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
    for vista in ("topologiaViz", "kmeansViz", "memBarra", "s13DemandaSalida"):
        assert f'id="{vista}"' in presentacion, f"Falta visualización: {vista}"
    assert 'kmeansPaso' in presentacion and 'actualizarMemoria' in presentacion
    assert '60 %' in presentacion and '95 %' in presentacion
    # Contrato histórico: las primeras cuatro diapositivas deben permanecer idénticas.
    def fnv_utf16(cadena):
        h = 2166136261
        datos = cadena.encode("utf-16-le")
        for i in range(0, len(datos), 2):
            codigo = int.from_bytes(datos[i:i+2], "little")
            h = ((h ^ codigo) * 16777619) & 0xFFFFFFFF
        return f"{h:08x}"
    referencias = ("2eb6f8c8", "72f73a44", "c0f09536", "8c64b782")
    for n, esperado in enumerate(referencias, start=1):
        bloque = re.search(
            rf'<section class="slide(?: active)?" id="s{n}"[\s\S]*?</section>',
            presentacion
        )
        assert bloque and fnv_utf16(bloque.group(0)) == esperado, (
            f"Se alteró el contenido de la diapositiva {n}"
        )
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
    assert "psutil" in paquetes
    assert "streamlit" not in paquetes
    assert set(perfil["forwardPorts"]) == {8787}
    assert "KMeansDask" in leer("Laboratorios/S13_Codespaces/verificar_entorno.py")
    curso = json.loads(leer("lms/data/course.json"))
    s13 = next(x for x in curso["sessions"] if x["n"] == 13)
    assert s13["status"] == "visible"
    assert "s13-de-una-maquina" in s13["entry"]["url"]
    indice = leer("index.html")
    # Contrato de incorporación: la creación abre main, pero exige elegir S13 manualmente.
    enlace = "https://codespaces.new/jazaineam1/BigData2026/tree/main"
    perfil_exacto = "S13 · Dask, MapReduce y modelos SECOP"
    guía = leer("Laboratorios/S13_Codespaces/README.md")
    for contenido in (presentacion, texto, guía):
        assert enlace in contenido, "Falta el vínculo para entrar al entorno S13"
        assert perfil_exacto in contenido, "No se nombró el perfil exacto"
        assert "Airflow Lab" in contenido, "Falta advertencia sobre el perfil equivocado"
        assert "LISTO PARA S13" in contenido, "Falta la comprobación final del entorno"
    assert enlace in indice and "Crear Codespace S13" in indice
    tarjeta = indice[indice.index('data-n="13"'):].split("</article>", 1)[0]
    assert "TF-IDF" not in tarjeta, "La portada describe un ejercicio retirado"
    assert "K-means" in tarjeta, "La portada no describe el modelo actual"
    assert "WORKERS_DEMO_S13 = min(2, max(1, cpus_disponibles()))" in codigo
    assert "clasificación didáctica" not in texto
    assert "ampliación opcional del final" not in texto
    assert indice.count('data-n="13"') == 1
    assert 'href="Presentaciones/s13-de-una-maquina-a-un-cluster.html#s1"' in indice
    print(f"S13 validada: 24 láminas, {len(celdas)} celdas, 1 cuaderno y K-means numérico")


if __name__ == "__main__":
    main()
