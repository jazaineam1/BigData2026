"""Prueba mínima de S15: ejecutar las celdas tal como se distribuyen."""
import json
from pathlib import Path
import shutil
root = Path(__file__).resolve().parents[1]
nb = json.loads((root / "Cuadernos/15_Pipeline_Confiable.ipynb").read_text())
ns = {}
try:
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] == "code":
            exec(compile("".join(cell["source"]), f"S15-celda-{i}", "exec"), ns)
    assert ns["estado"]() == {"validos":7,"rechazos":2,"lotes_confirmados":4}
    assert ns["salida"].is_file()
    print("OK: S15, transacciones, rollback, idempotencia y transferencia")
finally:
    if "carpeta" in ns:
        shutil.rmtree(ns["carpeta"], ignore_errors=True)
