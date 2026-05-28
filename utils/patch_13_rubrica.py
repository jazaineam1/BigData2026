# -*- coding: utf-8 -*-
"""
utils/patch_13_rubrica.py
==========================
Actualiza la rubrica del taller 13 para que el componente "Descarga"
permita explicitamente justificacion de limites tecnicos.
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(ROOT, "Cuadernos", "13_Taller_Final_MongoDB_SECOP_Tiempo_Real.ipynb")

with open(path, encoding="utf-8") as f:
    nb = json.load(f)

# Buscar las dos celdas de rubrica (la tabla y la matriz)
count = 0
for cell in nb["cells"]:
    if cell.get("cell_type") != "markdown":
        continue

    src_lines = cell.get("source", [])
    src = "".join(src_lines)

    # Buscar la tabla de "Componentes evaluables"
    if ("| 1 | **Descarga completa desde 2021**" in src and
        "Datos desde `2021-01-01`" in src):

        # Reemplazar esa linea en la fuente
        new_lines = []
        for line in src_lines:
            if "| 1 | **Descarga completa desde 2021**" in line and "Datos desde" in line:
                # Reemplazar solo esa linea especifica
                new_lines.append(
                    "| 1 | **Descarga de datos (desde 2021 o justificado)** | "
                    "Datos desde `2021-01-01` O ventana temporal reducida con justificacion tecnica; "
                    "fecha/hora de descarga, conteos y evidencia de filtros. | 10 |\n"
                )
                count += 1
            else:
                new_lines.append(line)
        cell["source"] = new_lines

if count >= 1:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print(f"[OK] Rubrica actualizada ({count} componente(s) de Descarga)")
else:
    print("[ERROR] No se encontraron componentes de Descarga en la rubrica")
