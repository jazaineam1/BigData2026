#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migración única: consolida el rediseño beginner dentro de la fuente editorial S06."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "utils" / "session6_graphlab_enhancements.py"


def main() -> None:
    text = MODULE.read_text(encoding="utf-8")
    original = text

    old_order = '''    simplify_intro(cells)\n    simplify_anchor(cells)\n    simplify_concepts(cells)\n    improve_contract(cells)\n    improve_graph_properties(cells)\n    move_contract_and_insert_lab(cells)\n    simplify_operational_choices(cells)\n    hide_python_infrastructure(cells)'''
    new_order = '''    simplify_intro(cells)\n    simplify_anchor(cells)\n    simplify_concepts(cells)\n    improve_graph_properties(cells)\n    move_contract_and_insert_lab(cells)\n    improve_contract(cells)\n    simplify_operational_choices(cells)\n    hide_python_infrastructure(cells)'''
    if old_order in text:
        text = text.replace(old_order, new_order, 1)
        print("[OK] Orden editorial: mover H2-R antes de simplificar su código")
    elif new_order in text:
        print("[OK] Orden editorial ya consolidado")
    else:
        raise SystemExit("No se encontró el bloque enhance_cells esperado")

    pattern = re.compile(r'def enhance_checklist\(cells\):\n(?:    .*\n?)*?\Z', re.M)
    replacement = '''def enhance_checklist(cells):\n    """Restaura el checklist beginner después del build histórico del generador."""\n    template = ROOT / "assets" / "tutoriales" / "templates" / "s06-laboratorio-guiado.html"\n    target = ROOT / "assets" / "tutoriales" / "s06-laboratorio-guiado.html"\n    if not template.is_file():\n        raise FileNotFoundError(template)\n    target.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")\n'''
    new_text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit("No se pudo consolidar enhance_checklist")
    text = new_text

    if text != original:
        MODULE.write_text(text, encoding="utf-8")
        print("[OK] Fuente beginner consolidada")
    else:
        print("[OK] Fuente beginner ya estaba consolidada")


if __name__ == "__main__":
    main()
