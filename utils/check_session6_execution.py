#!/usr/bin/env python3
"""Regresiones S6: ejecuta RESPALDO en limpio y contrasta las 28 anclas por NIT.

No sustituye Aura ni Colab. Completa los tres ejercicios con respuestas de prueba;
las consultas Cypher se conservan como pendientes, nunca como motor simulado.
Requiere pandas, IPython y nbformat. No lee credenciales ni escribe fuera del temporal.
"""
from __future__ import annotations

import ast
import base64
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
    import pandas as pd

    nb = nbformat.read(ROOT / "Cuadernos/6_Neo4j_Contexto_Relacional.ipynb", as_version=4)
    nbformat.validate(nb)
    cells = build_cells()
    saved = json.loads((ROOT / "Cuadernos/6_Neo4j_Contexto_Relacional.ipynb").read_text(encoding="utf-8"))
    assert saved["cells"] == cells, "Generador y notebook desincronizados"
    for c in cells:
        if c["cell_type"] == "code":
            ast.parse("".join(c["source"]))
    query = "MATCH (e:Entidad {nit:$ancla})-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor {nit:$proveedor}) RETURN count(DISTINCT p) AS procesos"
    replacements = {
        "RELACION_PROCESO_PROVEEDOR": "ADJUDICADO_A",
        "OPERADOR_EXCLUSION": "<>",
        "consulta_propia": query,
    }

    class StudentAnswers(ast.NodeTransformer):
        def visit_Assign(self, node):
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in replacements:
                node.value = ast.Constant(replacements[node.targets[0].id])
            return node

    def answer(prompt):
        if prompt.startswith("Ruta"): return ""
        if prompt.startswith("Enter = Aura"): return "RESPALDO"
        if prompt.startswith("Número de proveedor"): return "5"
        if prompt.startswith("Autor"): return "equipo-prueba"
        if prompt.startswith("Justifica"): return "Proceso debe ser nodo porque necesito consultar sus adjudicaciones y reutilizar su descripción."
        if prompt.startswith("Con tus números"): return "Exploro el quinto con 19 conexiones y descarto el primero de 39 para revisar un contexto menos amplio."
        if prompt.startswith("Límite"): return "No puedo afirmar irregularidad: faltan condiciones de competencia de cada proceso."
        if prompt.startswith("Alternativa"): return "Relación directa entre entidad y proveedor"
        if prompt.startswith("¿Por qué"): return "Perdería al proceso como unidad conectable y su texto para la búsqueda."
        raise AssertionError(f"Entrada inesperada: {prompt}")

    times = []
    previous = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="s06-check-") as tmp:
        try:
            os.chdir(tmp)
            for name in ["s06_contexto_relacional.csv", "s06_contexto_relacional_manifest.json"]:
                shutil.copyfile(ROOT / "Datos" / name, Path(tmp) / name)
            ns = {"input": answer}
            for i, c in enumerate(cells, 1):
                if c["cell_type"] != "code": continue
                src = "".join(c["source"])
                tree = ast.fix_missing_locations(StudentAnswers().visit(ast.parse(src)))
                start = time.perf_counter()
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        exec(compile(tree, f"<S6 celda {i}>", "exec"), ns)
                except Exception as exc:
                    raise RuntimeError(f"Falló celda {i}: {src[:90]}") from exc
                times.append((time.perf_counter()-start, i))
            assert ns["modo_neo4j"] is False and ns["neo_df"] is None and ns["coinciden"] is None
            assert ns["carga_repetida"] is None and "PENDIENTE" in ns["desenlace_h2r_neo"]
            assert len(ns["rows"]) == 2109 and len(ns["rows_proveedor"]) == 2032
            assert all(r["tipo_registro"] == "historico_adjudicado" and r["nit_proveedor"] for r in ns["rows_proveedor"])
            json.dumps(ns["rows"], allow_nan=False)
            assert len(ns["maximos_candidatas"]) == 28 and ns["MEDIANA_H2R"] == 21
            assert ns["proveedor_h2r"]["nit_proveedor"] != ns["proveedor_elegido"]["nit_proveedor"]
            assert ns["maximo_h2r"] == 39 and int(ns["proveedor_elegido"]["entidades_conectadas"]) == 19
            assert ns["otras_entidades"] == 18
            hito = Path("hito_s06_ficha_relacional.md").read_text(encoding="utf-8")
            assert "PENDIENTE" in hito and "pandas == Neo4j: True" not in hito
            assert "Máximo H2-R: 39" in hito and "Mediana H2-R: 21.0" in hito
            records = [json.loads(line) for line in Path("s06_contexto_procesos.jsonl").read_text(encoding="utf-8").splitlines()]
            assert len(records) == ns["vecindario_df"]["proceso"].nunique()
            assert all(r["id_proceso"] and r["descripcion"] and "precio_base" in r and "valor" not in r for r in records)

            # Identidad independiente del contrato: pares únicos y conjuntos, no el mismo groupby.
            hist = ns["hist"]
            edges = list(hist[["nit_entidad", "id_proceso", "nit_proveedor"]].drop_duplicates().itertuples(index=False, name=None))
            entities = {}
            for entity, process, provider in edges:
                entities.setdefault(provider, set()).add(entity)
            anclas = ns["datos"][ns["datos"]["tipo_registro"].eq("candidato_s05")].drop_duplicates("nit_entidad")
            tested = 0
            for _, anchor in anclas.iterrows():
                if anchor.nit_entidad not in set(hist.nit_entidad): continue
                current = dict(ns, ancla_original={"id_proceso": anchor.id_proceso, "nit_entidad": anchor.nit_entidad, "entidad": anchor.entidad}, origen_ancla="archivo propio S5")
                with contextlib.redirect_stdout(io.StringIO()):
                    exec(PREPARE_HIST, current)
                    exec(CONTRACT_PANDAS, current)
                local = {}
                for entity, process, provider in edges:
                    if entity == anchor.nit_entidad: local.setdefault(provider, set()).add(process)
                expected = sorted([(v, len(procs), len(entities[v])) for v, procs in local.items()], key=lambda row: (-row[2], -row[1], row[0]))[:10]
                actual = list(current["esperado_pd"][["nit_proveedor", "procesos_con_entidad", "entidades_conectadas"]].itertuples(index=False, name=None))
                assert actual == expected, anchor.nit_entidad
                if anchor.nit_entidad == "830063506":
                    assert current["esperado_pd"].set_index("nit_proveedor").loc["860039988", "entidades_conectadas"] == 8
                tested += 1
            assert tested == 28
            # El ejercicio de exclusión debe resolver también un vecindario sin otras entidades.
            ns["proveedor_elegido"] = {"nit_proveedor": "test", "entidades_conectadas": 1}
            ns["vecindario_df"] = pd.DataFrame([{"nit_entidad": ns["nit_deseado"], "proceso": "test"}])
            exclusion = next("".join(c["source"]) for c in cells if "".join(c["source"]).startswith("OPERADOR_EXCLUSION ="))
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(ast.fix_missing_locations(StudentAnswers().visit(ast.parse(exclusion))), "<exclusión cero>", "exec"), ns)
            assert ns["otras_entidades"] == 0
        finally:
            os.chdir(previous)
    slow, cell = max(times)
    print(f"[OK] {len(times)} celdas de código ejecutadas en RESPALDO, incluidos widgets y recuperación; ejercicios completados con respuestas de prueba.")
    print(f"[OK] 2109 filas / 2032 adjudicaciones sin NaN; 28 anclas contrastadas con conjuntos; mediana 21; Transmilenio/HDI = 8.")
    print("[OK] Proveedor H2-R distinto del explorado; exclusión 18 y cero; ficha y JSONL coherentes; Aura permanece PENDIENTE.")
    print(f"[INFO] Celda local más lenta: {cell}, {slow:.3f} s. No es medición de Colab ni Aura.")


if __name__ == "__main__":
    main()
