#!/usr/bin/env python3
"""Prueba de ejecución completa S06 en modo RESPALDO.

La prueba no simula Aura. Verifica que un estudiante principiante pueda ejecutar
el cuaderno sin tener que responder cajas abiertas ni escribir Cypher desde cero.
"""
from __future__ import annotations

import ast
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from utils.build_session6_novice import build_novice_cells


class ConfigureForCI(ast.NodeTransformer):
    replacements = {
        "RUTA_EJECUCION": "RESPALDO",
        "USAR_MI_ANCLA_S5": False,
        "AUTOR_ALIAS": "equipo-prueba",
    }

    def visit_Assign(self, node):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in self.replacements:
                node.value = ast.Constant(self.replacements[name])
        return node


def no_input(prompt=""):
    raise AssertionError(f"S06 pidió una entrada abierta inesperada en modo RESPALDO: {prompt!r}")


def main():
    import nbformat

    nb = nbformat.read(ROOT / "Cuadernos/6_Neo4j_Contexto_Relacional.ipynb", as_version=4)
    nbformat.validate(nb)
    cells = build_novice_cells()
    saved = json.loads((ROOT / "Cuadernos/6_Neo4j_Contexto_Relacional.ipynb").read_text(encoding="utf-8"))
    assert saved["cells"] == cells, "Generador final y notebook desincronizados"

    for i, c in enumerate(cells, 1):
        if c["cell_type"] == "code":
            ast.parse("".join(c["source"]))

    previous = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="s06-novato-") as tmp:
        try:
            os.chdir(tmp)
            for name in ["s06_contexto_relacional.csv", "s06_contexto_relacional_manifest.json"]:
                shutil.copyfile(ROOT / "Datos" / name, Path(tmp) / name)

            ns = {"input": no_input}
            executed = 0
            for i, c in enumerate(cells, 1):
                if c["cell_type"] != "code":
                    continue
                source = "".join(c["source"])
                tree = ast.fix_missing_locations(ConfigureForCI().visit(ast.parse(source)))
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        exec(compile(tree, f"<S06 celda {i}>", "exec"), ns)
                except Exception as exc:
                    raise RuntimeError(f"Falló la celda {i}: {source[:160]!r}") from exc
                executed += 1

            assert ns["RUTA_EJECUCION"] == "RESPALDO"
            assert ns["modo_neo4j"] is False
            assert len(ns["rows"]) == 2109
            assert len(ns["rows_proveedor"]) == 2032
            assert len(ns["maximos_candidatas"]) == 28
            assert float(ns["MEDIANA_H2R"]) == 21.0
            assert int(ns["maximo_h2r"]) == 39
            assert int(ns["proveedor_elegido"]["entidades_conectadas"]) >= 1
            assert ns["otras_entidades"] == int(ns["proveedor_elegido"]["entidades_conectadas"]) - 1
            assert ns["procesos_propios"] == int(ns["proveedor_elegido"]["procesos_con_entidad"])
            assert "MATCH" in ns["consulta_propia"] and "count(DISTINCT p)" in ns["consulta_propia"]
            assert "no demuestra irregularidad" in ns["razon_exploracion"].lower()
            assert ns["autor"] == "equipo-prueba"
            assert "identidad" in ns["decision_modelo"].lower()
            assert "no demuestra irregularidad" in ns["limite_estudiante"].lower()

            hito = Path("hito_s06_ficha_relacional.md")
            jsonl = Path("s06_contexto_procesos.jsonl")
            assert hito.is_file() and jsonl.is_file(), "No se generaron los entregables"
            hito_text = hito.read_text(encoding="utf-8")
            assert "equipo-prueba" in hito_text
            assert "pandas == Neo4j: True" not in hito_text
            records = [json.loads(x) for x in jsonl.read_text(encoding="utf-8").splitlines() if x.strip()]
            assert records, "JSONL vacío"
            assert all(r.get("id_proceso") for r in records)

        finally:
            os.chdir(previous)

    print(f"[OK] {executed} celdas de código ejecutadas en RESPALDO sin inputs abiertos")
    print("[OK] 2109 filas / 2032 adjudicaciones; referencia 28 entidades y mediana 21")
    print("[OK] Consulta Cypher guiada, interpretación, ficha y JSONL generados")
    print("[INFO] Aura real no se simula; requiere credenciales propias en clase")


if __name__ == "__main__":
    main()
