#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normaliza marcadores para que la pasada S5 v2 sea idempotente.

El constructor histórico de S5 transforma el notebook publicado en lugar de
reconstruirlo desde cero. Esta capa restaura únicamente los marcadores que la
pasada v2 reemplaza, de modo que la secuencia build -> normalize -> improve
pueda repetirse sin fallar ni depender del estado anterior del notebook.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "5_Atlas_Cassandra_Query_First.ipynb"


def src(cell: dict) -> str:
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def main() -> None:
    data = json.loads(NB.read_text(encoding="utf-8"))
    cells = data["cells"]

    for cell in cells:
        text = src(cell)

        if "## 2. De documentos a una vista que sí usaremos" in text:
            text = text.replace(
                "## 2. De documentos a una vista que sí usaremos",
                "## 2. Consulta, pipeline, pipeline guardado y vista",
                1,
            )

        # improve_session5_v2.py busca este texto histórico para reemplazar
        # después toda la celda de conexión de forma determinista.
        if "Sube UN solo Secure Connect Bundle" in text and "Sube el Secure Connect Bundle" not in text:
            text = text.replace(
                "Sube UN solo Secure Connect Bundle",
                "Sube el Secure Connect Bundle",
                1,
            )

        if "MÁS ADELANTE — Consistencia ajustable" in text and "## 10. Consistencia ajustable" not in text:
            text = text.replace(
                "<details>",
                "## 10. Consistencia ajustable\n\n<details>",
                1,
            )

        cell["source"] = text

    NB.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    json.loads(NB.read_text(encoding="utf-8"))
    print("[OK] Marcadores S5 normalizados para reaplicar la auditoría v2.")


if __name__ == "__main__":
    main()
