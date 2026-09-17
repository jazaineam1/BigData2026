#!/usr/bin/env python3
"""Regresión S06: ejecuta el flujo guiado en RESPALDO sin entradas abiertas."""
from __future__ import annotations

import ast
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from utils.build_session6_notebook import build_cells, CONTRACT_PANDAS, PREPARE_HIST


def main():
    import nbformat

    nb = nbformat.read(ROOT / "Cuadernos/6_Neo4j_Contexto_Relacional.ipynb", as_version=4)
    nbformat.validate(nb)
    cells = build_cells()
    saved = json.loads((ROOT / "Cuadernos/6_Neo4j_Contexto_Relacional.ipynb").read_text(encoding="utf-8"))
    assert saved["cells"] == cells, "Generador y notebook desincronizados"

    for cell in cells:
        if cell["cell_type"] == "code":
            ast.parse("".join(cell["source"]))

    replacements = {
        "MODO_EJECUCION": "RESPALDO",
        "RUTA_ANCLA": "Ejemplo del curso",
        "AUTOR": "equipo-prueba",
    }

    class GuidedMode(ast.NodeTransformer):
        def visit_Assign(self, node):
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                name = node.targets[0].id
                if name in replacements:
                    node.value = ast.Constant(replacements[name])
            return node

    def unexpected_input(prompt):
        raise AssertionError(f"S06 guiada no debería pedir esta entrada en RESPALDO: {prompt}")

    times = []
    previous = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="s06-beginner-check-") as tmp:
        try:
            os.chdir(tmp)
            for name in ["s06_contexto_relacional.csv", "s06_contexto_relacional_manifest.json"]:
                shutil.copyfile(ROOT / "Datos" / name, Path(tmp) / name)

            ns = {"input": unexpected_input}
            for i, cell in enumerate(cells, 1):
                if cell["cell_type"] != "code":
                    continue
                source = "".join(cell["source"])
                tree = ast.fix_missing_locations(GuidedMode().visit(ast.parse(source)))
                start = time.perf_counter()
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        exec(compile(tree, f"<S6 celda {i}>", "exec"), ns)
                except Exception as exc:
                    raise RuntimeError(f"Falló celda {i}: {source[:120]}") from exc
                times.append((time.perf_counter() - start, i))

            assert ns["modo_neo4j"] is False
            assert ns["RUTA_ANCLA"] == "Ejemplo del curso"
            assert ns["origen_ancla"] == "ejemplo del curso"
            assert len(ns["rows"]) == 2109
            assert len(ns["rows_proveedor"]) == 2032
            assert all(r["tipo_registro"] == "historico_adjudicado" and r["nit_proveedor"] for r in ns["rows_proveedor"])
            json.dumps(ns["rows"], allow_nan=False)

            assert len(ns["maximos_candidatas"]) == 28
            assert ns["MEDIANA_H2R"] == 21
            assert ns["maximo_h2r"] == 39
            assert int(ns["proveedor_elegido"]["entidades_conectadas"]) >= 1
            assert ns["otras_entidades"] == int(ns["proveedor_elegido"]["entidades_conectadas"]) - 1
            assert "MATCH (e:Entidad {nit:$ancla})" in ns["consulta_propia"]
            assert "count(DISTINCT p) AS procesos" in ns["consulta_propia"]
            assert ns["decision_modelo"].startswith("Proceso es nodo porque")
            assert "no demuestran irregularidad" in ns["limite_estudiante"]

            hito = Path("hito_s06_ficha_relacional.md").read_text(encoding="utf-8")
            assert "PENDIENTE" in hito and "pandas == Neo4j: True" not in hito
            assert "Máximo H2-R: 39" in hito and "Mediana H2-R: 21.0" in hito
            assert "equipo-prueba" in hito

            records = [json.loads(line) for line in Path("s06_contexto_procesos.jsonl").read_text(encoding="utf-8").splitlines()]
            assert records
            assert len(records) == ns["vecindario_df"]["proceso"].nunique()
            assert all(r["id_proceso"] and r["descripcion"] and "precio_base" in r and "valor" not in r for r in records)

            # Conservamos una comprobación independiente de las 28 entidades de referencia.
            hist = ns["hist"]
            edges = list(hist[["nit_entidad", "id_proceso", "nit_proveedor"]].drop_duplicates().itertuples(index=False, name=None))
            entities = {}
            for entity, process, provider in edges:
                entities.setdefault(provider, set()).add(entity)
            anchors = ns["datos"][ns["datos"]["tipo_registro"].eq("candidato_s05")].drop_duplicates("nit_entidad")
            tested = 0
            for _, anchor in anchors.iterrows():
                if anchor.nit_entidad not in set(hist.nit_entidad):
                    continue
                current = dict(
                    ns,
                    ancla_original={"id_proceso": anchor.id_proceso, "nit_entidad": anchor.nit_entidad, "entidad": anchor.entidad},
                    origen_ancla="archivo propio S5",
                )
                with contextlib.redirect_stdout(io.StringIO()):
                    exec(PREPARE_HIST, current)
                    exec(CONTRACT_PANDAS, current)
                local = {}
                for entity, process, provider in edges:
                    if entity == anchor.nit_entidad:
                        local.setdefault(provider, set()).add(process)
                expected = sorted(
                    [(v, len(procs), len(entities[v])) for v, procs in local.items()],
                    key=lambda row: (-row[2], -row[1], row[0]),
                )[:10]
                actual = list(current["esperado_pd"][["nit_proveedor", "procesos_con_entidad", "entidades_conectadas"]].itertuples(index=False, name=None))
                assert actual == expected, anchor.nit_entidad
                tested += 1
            assert tested == 28
        finally:
            os.chdir(previous)

    slow, cell = max(times)
    print(f"[OK] {len(times)} celdas ejecutadas en RESPALDO sin preguntas abiertas ni credenciales.")
    print("[OK] 2109 filas / 2032 adjudicaciones; mediana H2-R 21; máximo 39; 28 anclas contrastadas.")
    print("[OK] Consulta guiada, ficha y JSONL coherentes; Aura permanece PENDIENTE en la prueba local.")
    print(f"[INFO] Celda local más lenta: {cell}, {slow:.3f} s.")


if __name__ == "__main__":
    main()
