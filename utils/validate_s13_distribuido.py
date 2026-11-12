"""Contrato técnico-pedagógico ligero de S13, sin instalar bibliotecas."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")

def main() -> None:
    notebook=json.loads(text("Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb"))
    assert notebook["nbformat"] == 4
    cells=notebook["cells"]
    assert len(cells) == 54, f"Esperadas 45 celdas principales + 9 opcionales: {len(cells)}"
    raw=["".join(c["source"]) for c in cells]
    mark=next(i for i,v in enumerate(raw) if v.startswith("## Ampliación opcional"))
    assert mark == 45, f"Ruta principal debe terminar en celda 45, llegó a {mark}"
    main_text="\n".join(raw[:mark])
    all_text="\n".join(raw)
    assert "WORKERS_DEMO_S13 = 2" in main_text
    assert 'for modo in ("datos", "espera")' in main_text
    assert "mediciones_s13" in main_text
    assert "tabla_tfidf_a" in main_text
    assert "OPCIONES_ARQUITECTURA" in main_text and "OPCIONES_LIMITE" in main_text
    assert "LinearSVC" not in main_text and "LogisticRegression" not in main_text
    assert "EJECUTAR_AMPLIACION_S13 = False" in all_text
    assert "mantenimiento computadores" in main_text
    assert "infraestructura computadores" in main_text
    assert "hospital mantenimiento" in main_text
    assert not any("____" in "".join(c["source"]) for c in cells if c["cell_type"]=="code")
    for cell in cells:
        if cell["cell_type"] == "code":
            compile("".join(cell["source"]), "celda_s13", "exec")

    html=text("Presentaciones/s13-de-una-maquina-a-un-cluster.html")
    slides=re.findall(r'<section class="slide(?: active)?" id="s(\d+)"',html)
    assert slides == [str(i) for i in range(1,25)], "Presentación: exactamente 24 láminas consecutivas"
    for code in ["unitJump","decisionBox","hdfsGrid","quizPrompt","tfidfToyRun",
                 "tfidfToyTable","cosRun","mapRun","costRun","workerRun",
                 "scenarioWorkers"]:
        assert f'id="{code}"' in html, f"Control perdido: {code}"
    assert "--modo datos" in html and "--modo espera" in html
    assert "streamlit run Laboratorios/S13_Codespaces/app_tfidf_unspsc.py" in html
    assert "if __name__ == \"__main__\":" in html
    assert not re.search(r"(?i)(?:HP del estudiante|tu HP|en mi HP|mi portátil HP)",html)
    assert '1 / 24' in html
    if shutil.which("node"):
        script=re.search(r"<script>(.*?)</script>",html,re.DOTALL)
        assert script
        with tempfile.NamedTemporaryFile(mode="w",suffix=".js",encoding="utf-8") as temp:
            temp.write(script.group(1))
            temp.flush()
            subprocess.run(["node","--check",temp.name],check=True)

    app=text("Laboratorios/S13_Codespaces/app_tfidf_unspsc.py")
    assert app.count("with tabs[") == 7
    assert '["datos","espera"]' in app
    assert 'st.toggle("Activar clasificación opcional"' in app
    assert "s13_ejecuciones" in app
    assert "infraestructura computadores" in app
    assert "s13_dask_2_casos.json" in app
    demo=text("Laboratorios/S13_Codespaces/dask_cuando_si.py")
    for key in ["top_terminos","segundos_preparacion_entrada",
                "segundos_dask_cluster_caliente","resultados_identicos"]:
        assert key in demo
    assert 'choices=["espera", "datos", "cpu"]' in demo
    base=text("Laboratorios/S13_Codespaces/requirements.txt")
    assert "xgboost" not in base.lower(), "XGBoost es extensión opcional"
    assert "xgboost" in text("Laboratorios/S13_Codespaces/requirements-extras.txt").lower()

    config=json.loads(text(".devcontainer/s13-distribuido/devcontainer.json"))
    assert "S13" in config["name"]
    for port in ("8503","8787"):
        assert config["portsAttributes"][port]["visibility"]=="private"
    assert "verificar_entorno.py" in config["postCreateCommand"]
    smoke=text("Laboratorios/S13_Codespaces/verificar_entorno.py")
    assert "processes=True" in smoke and "client.submit(" in smoke
    course=json.loads(text("lms/data/course.json"))
    s13=next(x for x in course["sessions"] if x["n"]==13)
    assert s13["status"]=="visible"
    assert "s13-de-una-maquina" in s13["entry"]["url"]
    index=text("index.html")
    assert index.count('data-n="13"')==1
    assert 'href="Presentaciones/s13-de-una-maquina-a-un-cluster.html#s1"' in index
    assert "24 diapositivas interactivas" in index
    assert not (ROOT / "docs/S13_PLAN_MEJORA_DASK.md").exists()
    print("S13 QA: 24 diapositivas, 45 celdas principales, 9 opcionales, Dask real y simulación declarada: OK")

if __name__ == "__main__":
    main()
