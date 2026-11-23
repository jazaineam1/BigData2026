"""Comprobación mínima para un Codespace recién creado."""
from __future__ import annotations
import sys
from pathlib import Path
import os
import subprocess
import json

import dask
import dask.dataframe as dd
import pandas as pd
import pyarrow
import sklearn
from dask.distributed import Client
from dask_ml.cluster import KMeans as KMeansDask
from sklearn.datasets import make_blobs
import psutil
import inspect
assert "n_clusters" in inspect.signature(KMeansDask).parameters, "La API K-means de Dask-ML cambió"
assert hasattr(psutil.Process(), "memory_info"), "psutil no puede medir RSS"
# Verificar dependencias y forma de entrada sin iniciar otro entrenamiento al abrir Codespaces.
puntos, _ = make_blobs(n_samples=24, n_features=2, centers=4, random_state=42)
assert puntos.shape == (24, 2)
print("Dask-ML KMeans: importación compatible | psutil RSS: OK | muestra numérica: OK")

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv"
CORPUS = ROOT / "Datos/tc2_corpus_2026.json"
assert CSV.is_file() and CORPUS.is_file(), "Archivos de clase ausentes"
mini = pd.DataFrame({"grupo": ["A", "A", "B"], "valor": [10, 20, 30]})
res = dd.from_pandas(mini, npartitions=2).groupby("grupo")["valor"].sum().compute()
assert int(res.loc["A"]) == 30
print("Python:", sys.version.split()[0])
print("pandas:", pd.__version__, "| Dask:", dask.__version__)
print("PyArrow:", pyarrow.__version__, "| scikit-learn:", sklearn.__version__)
print("Datos disponibles:", CSV.relative_to(ROOT), "y", CORPUS.relative_to(ROOT))
print("Dask mínimo: OK | No es una prueba de clúster físico")
if __name__ == "__main__":
    # Smoke real de procesos con 2 lotes, sin espera ni modelos.
    script = ROOT / "Laboratorios/S13_Codespaces/dask_cuando_si.py"
    p = subprocess.run(
        [sys.executable, str(script), "--workers", "1",
         "--tareas", "2", "--modo", "texto"],
        cwd=ROOT, capture_output=True, text=True, timeout=90,
    )
    if p.returncode:
        raise RuntimeError("No se pudo crear un worker Dask:\\n" + p.stderr[-1800:])
    data = next((s.split("RESULTADO_S13_DASK=", 1)[1]
                 for s in p.stdout.splitlines()
                 if s.startswith("RESULTADO_S13_DASK=")), None)
    assert data, "Falta evidencia de ejecución del worker"
    result = json.loads(data)
    assert result["resultados_identicos"] and len(result["workers_reales"]) == 1
    assert result["terminos_distintos_por_lote"], "No se procesaron términos"
    print("Worker real Dask: OK | textos SECOP verificados")
    print("LISTO PARA S13")
