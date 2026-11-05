#!/usr/bin/env python3
"""Genera S11 a partir de utils/s11_lesson_cells.json, sin editar el ipynb a mano.

python utils/build_session11_etl_audio_imagenes.py --check
python utils/build_session11_etl_audio_imagenes.py --write

La fuente editable es un JSON de celdas con IDs estables; este script construye
el contrato Jupyter con metadatos reproducibles. En --check compara estructura
y TODO el texto, sin exigir un formato de sangría específico a JSON.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "utils" / "s11_lesson_cells.json"
TARGET = REPO / "Cuadernos" / "11_ETL_Audio_Imagenes.ipynb"


def generar():
    datos = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert isinstance(datos, list) and len(datos) >= 20
    ids = [d["id"] for d in datos]
    assert len(ids) == len(set(ids)), "ID de celda duplicado"
    celdas = []
    for d in datos:
        tipo = d["type"]
        assert tipo in ("code", "markdown")
        texto = d["source"].rstrip("\n") + "\n"
        if not texto.strip():
            raise ValueError("Celda vacía")
        c = {
            "cell_type": tipo,
            "id": d["id"],
            "metadata": {},  # Código SIEMPRE visible; controles @param siguen editables.
            "source": texto.splitlines(keepends=True),
        }
        if tipo == "code":
            compile(texto, f"<S11:{d['id']}>", "exec")
            c["execution_count"] = None
            c["outputs"] = []
        celdas.append(c)
    return {
        "cells": celdas,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
            "colab": {"name": "11_ETL_Audio_Imagenes.ipynb", "provenance": []},
        },
        "nbformat": 4, "nbformat_minor": 5,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    p.add_argument("--write", action="store_true")
    a = p.parse_args()
    generado = generar()
    if a.write:
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_text(json.dumps(generado, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("CUADERNO S11 GENERADO:",len(generado["cells"]),"celdas")
    else:
        actual = json.loads(TARGET.read_text(encoding="utf-8"))
        assert actual == generado, "El cuaderno S11 no coincide con la fuente editable"
        # Contrato pedagógico: E→T→L→QA→entrega.
        ids = [c["id"] for c in generado["cells"]]
        for clave in ("s11-extraer-imagenes","s11-extraer-audios",
                      "s11-transformar-imagenes","s11-transformar-audios",
                      "s11-cargar","s11-calidad","s11-empaquetar","s11-autocomprobar"):
            assert clave in ids
        assert ids.index("s11-extraer-imagenes") < ids.index("s11-extraer-audios") < ids.index("s11-transformar-imagenes") < ids.index("s11-transformar-audios") < ids.index("s11-cargar") < ids.index("s11-calidad")
        print("CUADERNO S11 SINCRONIZADO:",len(ids),"celdas",len([x for x in generado["cells"] if x["cell_type"]=="code"]),"ejecutables")


if __name__ == "__main__":
    main()
