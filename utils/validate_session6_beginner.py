#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regresiones pedagógicas de S06 para estudiantes sin experiencia en Neo4j/Cypher."""
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
        "S06-BEGINNER-V1",
        "No necesitas saber Python",
        "Neo4j",
        "AuraDB",
        "Cypher",
        "Aura Query",
        "RETURN 1 AS conexion",
        "Consulta 1 — ver nodos",
        "Consulta 2 — una relación",
        "Consulta 3 — dos relaciones",
        "¿Qué es el grado?",
        "¿Qué es un hub?",
        "nodo concentrador",
        "Vista gráfica 1 — un proveedor con muchas conexiones",
        "Vista gráfica 2 — dos entidades conectadas por un proveedor compartido",
        "¿Por qué puedo ver varias islas?",
        "Profundización opcional",
        "RUTA_ANCLA",
        "Ejemplo del curso",
        "Mi archivo de S5",
        "Ejemplo de respuesta",
    ]
    for item in required_nb:
        if item not in text:
            errors.append(f"Notebook sin elemento para principiantes: {item!r}")

    forbidden = [
        "WOW 1",
        "WOW 2",
        "consulta_wow_global",
        "consulta_wow_ancla",
        'input("Número de proveedor:',
        'input("Con tus números:',
        'input("Justifica por qué Proceso',
        'input("Límite concreto',
        'input("Alternativa de modelado',
    ]
    for item in forbidden:
        if item in text:
            errors.append(f"Notebook conserva carga cognitiva innecesaria: {item!r}")

    order = [
        text.find("Consulta 1 — ver nodos"),
        text.find("Consulta 2 — una relación"),
        text.find("Consulta 3 — dos relaciones"),
        text.find("¿Qué es el grado?"),
        text.find("¿Qué es un hub?"),
        text.find("Vista gráfica 1 — un proveedor con muchas conexiones"),
        text.find("Vista gráfica 2 — dos entidades conectadas por un proveedor compartido"),
        text.find("Profundización opcional"),
    ]
    if any(p < 0 for p in order) or order != sorted(order):
        errors.append("La progresión debe ser nodo → relación → camino → grado → hub → vistas gráficas → profundización")

    complex_tokens = ["groupby(", "str(nit_deseado).replace", "to_dict(\"records\")", "pd.concat("]
    for i, cell in enumerate(cells, 1):
        if cell.get("cell_type") != "code":
            continue
        body = src(cell)
        if any(tok in body for tok in complex_tokens) and not hidden(cell):
            errors.append(f"Celda {i}: Python de infraestructura visible para el estudiante")
        if "input(" in body and not hidden(cell):
            errors.append(f"Celda {i}: input() visible; usar formulario guiado o infraestructura oculta")

    if 'RELACION_PROCESO_PROVEEDOR = "____"' in text:
        errors.append("El patrón contractual no debe comenzar con una respuesta en blanco para adivinar")
    if "raise ValueError(\"La flecha Proceso" in text:
        errors.append("El ejercicio introductorio no debe fallar con ValueError como retroalimentación")

    required_graph = [
        "Mini curso visual de Cypher",
        "¿Qué es un nodo?",
        "¿Qué es una relación?",
        "¿Qué es el grado?",
        "¿Qué es un hub?",
        "RETURN 1 AS conexion",
        "MATCH (e:Entidad)",
        "count(r)",
        "Vista gráfica 1",
        "Vista gráfica 2",
        "Qué debes ver",
        "Qué significa",
        "Qué NO significa",
        "varias islas",
    ]
    for item in required_graph:
        if item not in graph:
            errors.append(f"Graph Lab sin explicación básica: {item!r}")
    if "WOW" in graph:
        errors.append("Graph Lab todavía usa WOW como si fuera un concepto técnico")

    required_aura = ["Neo4j", "AuraDB", "Cypher", "Aura Query", "RETURN 1 AS conexion", "No subas el JSON de S5 a Aura"]
    for item in required_aura:
        if item not in aura:
            errors.append(f"Tutorial Aura sin paso básico: {item!r}")

    required_check = [
        "Vi cinco nodos Entidad",
        "Vi Entidad → Proceso",
        "Vi Entidad → Proceso → Proveedor",
        "Calculé el grado",
        "Puedo explicar qué es un hub",
        "Vi dos entidades compartiendo un proveedor",
        "Sé qué demuestra y qué no demuestra el grafo",
    ]
    for item in required_check:
        if item not in checklist:
            errors.append(f"Checklist sin paso observable: {item!r}")
    if "WOW" in checklist:
        errors.append("Checklist todavía usa WOW")

    if errors:
        print("Validación S06 principiantes fallida:")
        for error in errors:
            print("[ERROR]", error)
        raise SystemExit(1)

    print("[OK] S06 inicia desde cero: nodo → relación → camino → grado → hub → proveedor compartido")
    print("[OK] Python complejo oculto; Cypher visible y explicado; no hay respuestas abiertas para adivinar")
    print("[OK] Graph Lab, Aura y checklist tienen funciones distintas y coherentes")


if __name__ == "__main__":
    main()
