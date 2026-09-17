#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regresiones pedagógicas S06 para estudiantes sin experiencia en Neo4j/Cypher."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "6_Neo4j_Contexto_Relacional.ipynb"
GRAPH = ROOT / "assets" / "tutoriales" / "neo4j-graph-lab-s06.html"
AURA = ROOT / "assets" / "tutoriales" / "neo4j-aura-s06-paso-a-paso.html"
CHECKLIST = ROOT / "assets" / "tutoriales" / "s06-laboratorio-guiado.html"


def src(cell: dict) -> str:
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def hidden(cell: dict) -> bool:
    meta = cell.get("metadata", {})
    tags = set(meta.get("tags", []))
    return "hide-input" in tags or meta.get("cellView") == "form" or meta.get("jupyter", {}).get("source_hidden") is True


def positions(text: str, needles: list[str]) -> list[int]:
    return [text.find(n) for n in needles]


def main() -> None:
    errors: list[str] = []
    for path in (NB, GRAPH, AURA, CHECKLIST):
        if not path.is_file():
            errors.append(f"Falta {path.relative_to(ROOT)}")
    if errors:
        raise SystemExit("\n".join(errors))

    nb = json.loads(NB.read_text(encoding="utf-8"))
    cells = nb.get("cells", [])
    text = "\n".join(src(c) for c in cells)
    graph = GRAPH.read_text(encoding="utf-8")
    aura = AURA.read_text(encoding="utf-8")
    checklist = CHECKLIST.read_text(encoding="utf-8")

    required_nb = [
        "S06-ZERO-TO-HERO-V1",
        "Laboratorio zero-to-hero",
        "Primer nodo: `CREATE`, label, variable y propiedades",
        "Crea un Proceso y conéctalo",
        "MATCH", "WHERE", "count(r) AS grado", "DISTINCT", "WITH",
        "CREATE` vs `MERGE", "CONSTRAINT", "SHOW CONSTRAINTS", "SET", "UNWIND",
        "$filas", "$nit", "DETACH DELETE",
        "Transferencia al caso real",
        "Aplicación guiada — consultar los datos reales",
        "Profundización — comparar conectividad con una referencia (H2-R)",
        "Entidad ancla → Proceso → Proveedor ← Proceso ← otra Entidad",
    ]
    for item in required_nb:
        if item not in text:
            errors.append(f"Notebook sin elemento zero-to-hero: {item!r}")

    forbidden = [
        "WOW 1", "WOW 2", "consulta_wow_global", "consulta_wow_ancla",
        'input("Número de proveedor:', 'input("Con tus números:',
        'input("Justifica por qué Proceso', 'input("Límite concreto',
        'input("Alternativa de modelado', 'RELACION_PROCESO_PROVEEDOR = "____"',
    ]
    for item in forbidden:
        if item in text:
            errors.append(f"Notebook conserva carga cognitiva innecesaria: {item!r}")

    # Orden macro: primero se enseña, luego se carga/aplica, H2-R queda después.
    macro = positions(text, [
        "## 4. Laboratorio zero-to-hero",
        "### 4.1 Primer nodo",
        "### 4.6 Contar conexiones",
        "### 4.8 `WITH`",
        "### 4.9 El problema de identidad",
        "### 4.10 `CONSTRAINT`",
        "### 4.12 `UNWIND`",
        "## 5. Transferencia al caso real",
        "## 6. Aplicación guiada — consultar los datos reales",
        "## H2-R: la hipótesis relacional de esta sesión",
        "## 7. Profundización — comparar conectividad con una referencia (H2-R)",
    ])
    if any(p < 0 for p in macro) or macro != sorted(macro):
        errors.append("Orden incorrecto: enseñar → cargar → aplicar → H2-R")

    # El primer uso didáctico de sintaxis avanzada debe estar dentro del zero-to-hero.
    hero_start = text.find("## 4. Laboratorio zero-to-hero")
    transfer_start = text.find("## 5. Transferencia al caso real")
    for token in ["MERGE", "CONSTRAINT", "UNWIND", "WITH"]:
        first = text.find(token)
        if first < hero_start:
            errors.append(f"{token} aparece antes de enseñarse en zero-to-hero")
        if not (hero_start <= text.find(token, hero_start) < transfer_start):
            errors.append(f"{token} no está explicado dentro del laboratorio antes de la carga real")

    complex_tokens = ["groupby(", "str(nit_deseado).replace", "to_dict(\"records\")", "pd.concat("]
    for i, cell in enumerate(cells, 1):
        if cell.get("cell_type") != "code":
            continue
        body = src(cell)
        if any(tok in body for tok in complex_tokens) and not hidden(cell):
            errors.append(f"Celda {i}: Python de infraestructura visible para el estudiante")
        if "input(" in body and not hidden(cell):
            errors.append(f"Celda {i}: input() visible; usar formulario guiado o infraestructura oculta")

    required_graph = [
        "Neo4j y Cypher de cero al caso Compras Claras",
        "Nivel 0", "Nivel 1", "Nivel 2", "Nivel 3", "Nivel 4", "Nivel 5", "Nivel 6",
        "CREATE (e:EntidadDemo", "CREATE (p:ProcesoDemo", "CREATE (v:ProveedorDemo",
        "MATCH (e:EntidadDemo", "WHERE e.nit", "count(r) AS grado", "count(DISTINCT e)",
        "WITH v, count(r) AS grado", "MERGE (e:EntidadDemo", "CREATE CONSTRAINT demo_entidad_nit",
        "SHOW CONSTRAINTS", "SET e.nombre", "UNWIND [", "UNWIND $filas AS fila",
        "DETACH DELETE", "Table mide; Graph explica", "Pregunta profesional",
    ]
    for item in required_graph:
        if item not in graph:
            errors.append(f"Graph Lab incompleto: {item!r}")
    if "WOW" in graph:
        errors.append("Graph Lab todavía usa WOW como si fuera un concepto técnico")

    graph_order = positions(graph, [
        "Tu primer grafo de juguete",
        "Buscar, devolver y filtrar",
        "Contar conexiones sin saltos conceptuales",
        "De un ejemplo manual a una carga reproducible",
        "Transfiere lo aprendido a Compras Claras",
        "H2-R: después de entender el grafo",
    ])
    if any(p < 0 for p in graph_order) or graph_order != sorted(graph_order):
        errors.append("Graph Lab no progresa construir → consultar → analizar → cargar → caso real → H2-R")

    required_aura = [
        "Neo4j", "AuraDB", "Cypher", "Aura Query", "RETURN 1 AS conexion",
        "crear manualmente un nodo", "No subas el JSON de S5 a Aura",
    ]
    for item in required_aura:
        if item not in aura:
            errors.append(f"Tutorial Aura sin paso básico: {item!r}")

    required_check = [
        "Crea tu primer nodo", "Crea una relación", "Completa el camino", "Consulta y filtra",
        "Comparte un proveedor", "Cuenta relaciones", "Entiende hub, DISTINCT y WITH",
        "Protege la identidad", "SHOW CONSTRAINTS", "Carga varias filas",
        "Carga Compras Claras", "Responde la pregunta profesional",
    ]
    for item in required_check:
        if item not in checklist:
            errors.append(f"Checklist sin paso observable: {item!r}")
    if "WOW" in checklist:
        errors.append("Checklist todavía usa WOW")

    if errors:
        print("Validación S06 zero-to-hero fallida:")
        for error in errors:
            print("[ERROR]", error)
        raise SystemExit(1)

    print("[OK] S06 enseña CREATE → MATCH/WHERE → count/DISTINCT/WITH → MERGE/CONSTRAINT/SET → UNWIND")
    print("[OK] La carga real aparece después del laboratorio manual y H2-R queda como profundización")
    print("[OK] Graph Lab, Aura y checklist están alineados con la misma ruta zero-to-hero")


if __name__ == "__main__":
    main()
