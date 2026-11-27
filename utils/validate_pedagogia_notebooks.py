"""QA ligera: rutas incrustadas, generadores y ejercicios Python sin nube."""
from pathlib import Path
import ast
import copy
import json
import importlib.util
from integrar_ruta_notebook import integrar_ruta, BEGIN
ROOT=Path(__file__).resolve().parents[1]
cfg=json.loads((ROOT/"assets/pedagogia/rutas.json").read_text(encoding="utf-8"))
ids={"01","02","03","04","05","06","07","09","10","14","14A"}
for r in cfg["routes"]:
    ast.parse(r["code"], filename="S"+r["id"])
    if r["id"] in ids:
        nb=json.loads((ROOT/r["nb"]).read_text(encoding="utf-8"))
        assert sum(BEGIN in "".join(c["source"]) for c in nb["cells"] if c["cell_type"]=="markdown")==1, r["id"]
        assert integrar_ruta(copy.deepcopy(nb["cells"]),r["id"])==nb["cells"], r["id"]
# Solo los experimentos pequeños; Spark necesita el entorno S14.
for r in cfg["routes"]:
    if r["id"]=="14": continue
    if r["id"]=="01" and importlib.util.find_spec("pandas") is None:
        print("S01 omitida: pandas no instalado"); continue
    print("Experimento S"+r["id"])
    exec(compile(r["code"],"S"+r["id"],"exec"),{})
for name in ("build_session1_notebook.py","build_session2_notebook.py",
             "build_session3_notebook.py","build_session4_notebook.py",
             "build_session5_notebook.py","improve_session5_v7.py",
             "build_session6_novice.py","build_session9_notebook.py","build_s14_pyspark.py",
             "integrar_ruta_notebook.py"):
    ast.parse((ROOT/"utils"/name).read_text(encoding="utf-8"), filename=name)
print("OK: guías idempotentes, experimentos ligeros y sintaxis de generadores; S14 Spark no ejecutado.")
