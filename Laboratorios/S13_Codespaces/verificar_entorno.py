"""Comprobación mínima para un Codespace recién creado."""
from __future__ import annotations
import sys
from pathlib import Path

import dask
import dask.dataframe as dd
import pandas as pd
import pyarrow
import sklearn
from dask.distributed import Client

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
print("LISTO PARA S13")
