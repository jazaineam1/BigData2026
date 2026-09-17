#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inserta el módulo Graph Lab en el generador principal S06 de forma idempotente."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "utils" / "build_session6_notebook.py"


def main() -> None:
    text = GEN.read_text(encoding="utf-8")
    original = text

    import_line = "from utils.session6_graphlab_enhancements import enhance_cells, enhance_checklist"
    if import_line not in text:
        anchor = "from utils.make_notebook import code, md, save, validate"
        if anchor not in text:
            raise RuntimeError("No encuentro el import base del generador S06")
        text = text.replace(anchor, anchor + "\n" + import_line, 1)

    if "cells = enhance_cells(cells)" not in text:
        anchor = "    # Numeración calculada: una sola pregunta por celda, payload oculto al vistazo."
        if anchor not in text:
            raise RuntimeError("No encuentro el punto de inserción antes de numerar preguntas")
        text = text.replace(anchor, "    cells = enhance_cells(cells)\n\n" + anchor, 1)

    if "enhance_checklist(cells)" not in text:
        anchor = "    build_checklist(cells)\n"
        if anchor not in text:
            raise RuntimeError("No encuentro la llamada a build_checklist")
        text = text.replace(anchor, anchor + "    enhance_checklist(cells)\n", 1)

    if text != original:
        GEN.write_text(text, encoding="utf-8")
        print("[OK] Generador S06 actualizado con Graph Lab V2")
    else:
        print("[OK] Generador S06 ya tenía Graph Lab V2")


if __name__ == "__main__":
    main()
