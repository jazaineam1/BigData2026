#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normaliza marcadores para que las pasadas históricas de S5 sean idempotentes.

El constructor histórico de S5 transforma el notebook publicado en lugar de
reconstruirlo desde cero. Esta capa restaura únicamente los marcadores que las
pasadas v2-v6 y la propia v7 esperan encontrar. La pasada v7 vuelve a aplicar
al final la presentación vigente de tres productos y el semáforo cognitivo.
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

        # v3 y v5 todavía usan el encabezado histórico como ancla. Si el
        # notebook ya fue publicado por v7, restauramos solo el encabezado de
        # forma temporal; v7 vuelve a generar el contrato de tres productos.
        if "### CONTRATO DE ÉXITO S05 — tres productos, las mismas herramientas" in text:
            text = text.replace(
                "### CONTRATO DE ÉXITO S05 — tres productos, las mismas herramientas",
                "### Producto observable de hoy",
                1,
            )

        # v7 renombra la parte Python como tramo B. En una reconstrucción,
        # restauramos el ancla histórica y v7 la vuelve a presentar al final.
        if "## 9. PRODUCTO 3 · Tramo B — la misma tabla, ahora desde Python" in text:
            text = text.replace(
                "## 9. PRODUCTO 3 · Tramo B — la misma tabla, ahora desde Python",
                "## 9. La misma tabla, ahora desde Python",
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

        # v3 convierte el cierre histórico en "Lo que sigue". Antes de volver a
        # aplicar v2 restauramos el marcador que esa pasada usa como ancla.
        if text.lstrip().startswith("## Lo que sigue"):
            text = text.replace("## Lo que sigue", "# Cierre", 1)

        cell["source"] = text

    NB.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    json.loads(NB.read_text(encoding="utf-8"))
    print("[OK] Marcadores S5 normalizados para reaplicar auditorías v2-v7.")


if __name__ == "__main__":
    main()
