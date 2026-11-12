"""S13 · smoke test de un Codespace recien creado.

Prueba corta de Dask DataFrame y de un worker como proceso real.
No lee 50.000 registros, no inicia modelos y cierra siempre el cluster.
"""
from __future__ import annotations

import sys
from pathlib import Path

import dask
import dask.dataframe as dd
import pandas as pd
import pyarrow
import sklearn
from distributed import Client, LocalCluster
from dask_cuando_si import cpus_disponibles

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv"
CORPUS = ROOT / "Datos/tc2_corpus_2026.json"


def probar_entorno() -> None:
    assert CSV.is_file() and CORPUS.is_file(), "Faltan archivos versionados S13"
    mini = pd.DataFrame({"grupo": ["A", "A", "B"], "valor": [10, 20, 30]})
    tabla = dd.from_pandas(mini, npartitions=2)
    res = tabla.groupby("grupo")["valor"].sum().compute()
    assert int(res.loc["A"]) == 30
    print("Python:", sys.version.split()[0])
    print("pandas:", pd.__version__, "| Dask:", dask.__version__)
    print("PyArrow:", pyarrow.__version__, "| scikit-learn:", sklearn.__version__)
    print("CPU disponibles (afinidad/cuota orientativas):", cpus_disponibles())
    print("Archivos:", CSV.relative_to(ROOT), "y", CORPUS.relative_to(ROOT))

    # Este bloque comprueba procesos reales, no sólo un scheduler por hilos.
    # La protección __main__ es obligatoria al usar multiprocessing/spawn.
    with LocalCluster(n_workers=1, threads_per_worker=1, processes=True,
                      dashboard_address=None, silence_logs="error") as cluster:
        with Client(cluster) as client:
            assert len(client.scheduler_info()["workers"]) == 1
            futuro = client.submit(sum, [10, 20, 30], pure=False)
            assert futuro.result(timeout=30) == 60
            print("Worker de proceso Dask: OK | 1 worker, 1 hilo")
    print("LISTO PARA S13")


if __name__ == "__main__":
    probar_entorno()
