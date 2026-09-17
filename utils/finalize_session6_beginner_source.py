#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migración única: consolida el rediseño beginner dentro de las fuentes editoriales S06."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "utils" / "session6_graphlab_enhancements.py"
GENERATOR = ROOT / "utils" / "build_session6_notebook.py"


def patch_enhancements() -> bool:
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

    old_query = '''consulta_propia = """MATCH (e:Entidad {nit:$ancla})-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor {nit:$proveedor})
RETURN count(DISTINCT p) AS procesos"""'''
    new_query = '''consulta_propia = ("MATCH (e:Entidad {nit:$ancla})-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor {nit:$proveedor})\\n"
                    "RETURN count(DISTINCT p) AS procesos")'''
    if old_query in text:
        text = text.replace(old_query, new_query, 1)
        print("[OK] Consulta guiada normalizada sin triple-comillas dobles")
    elif "consulta_propia = (\"MATCH (e:Entidad {nit:$ancla})" in text:
        print("[OK] Consulta guiada ya estaba normalizada")
    else:
        raise SystemExit("No se encontró consulta_propia guiada")

    old_tokens = '''    tokens = [\n        "import urllib.request",'''
    new_tokens = '''    tokens = [\n        "groupby(",\n        "to_dict(\\\"records\\\")",\n        "pd.concat(",\n        "import urllib.request",'''
    if old_tokens in text:
        text = text.replace(old_tokens, new_tokens, 1)
        print("[OK] Regla de ocultamiento ampliada a pandas avanzado")
    elif '        "groupby(",' in text and '        "to_dict(\\"records\\")",' in text:
        print("[OK] Regla de ocultamiento pandas ya estaba ampliada")
    else:
        raise SystemExit("No se encontró la lista de tokens de infraestructura")

    pattern = re.compile(r'def enhance_checklist\(cells\):\n(?:    .*\n?)*?\Z', re.M)
    replacement = '''def enhance_checklist(cells):\n    """Restaura el checklist beginner desde su plantilla canónica."""\n    template = ROOT / "assets" / "tutoriales" / "templates" / "s06-laboratorio-guiado.html"\n    target = ROOT / "assets" / "tutoriales" / "s06-laboratorio-guiado.html"\n    if not template.is_file():\n        raise FileNotFoundError(template)\n    target.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")\n'''
    new_text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit("No se pudo consolidar enhance_checklist")
    text = new_text

    if text != original:
        MODULE.write_text(text, encoding="utf-8")
        print("[OK] Fuente de mejoras beginner consolidada")
        return True
    print("[OK] Fuente de mejoras beginner ya estaba consolidada")
    return False


def patch_generator() -> bool:
    text = GENERATOR.read_text(encoding="utf-8")
    original = text

    old = "    build_checklist(cells)\n    enhance_checklist(cells)\n"
    new = "    # El checklist beginner tiene plantilla canónica; no depende de números de celda.\n    enhance_checklist(cells)\n"
    if old in text:
        text = text.replace(old, new, 1)
        print("[OK] Retirada reconstrucción histórica del checklist")
    elif new in text:
        print("[OK] Generador ya usa solo el checklist beginner canónico")
    else:
        raise SystemExit("No se encontró la llamada histórica build_checklist/enhance_checklist")

    # La recuperación post-receso no debe cambiar la ruta que el estudiante eligió.
    old_origin = 'origen_ancla = "ancla pedagógica versionada incluida en S6"'
    new_origin = 'origen_ancla = globals().get("origen_ancla", "ejemplo del curso")'
    if old_origin in text:
        text = text.replace(old_origin, new_origin)
        print("[OK] Recuperación conserva el origen del ancla elegido")
    elif new_origin in text:
        print("[OK] Recuperación ya conserva el origen del ancla")
    else:
        raise SystemExit("No se encontró la etiqueta histórica de origen del ancla")

    if text != original:
        GENERATOR.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = patch_enhancements() | patch_generator()
    print("[OK] Fuentes beginner actualizadas" if changed else "[OK] Fuentes beginner sin cambios")


if __name__ == "__main__":
    main()
