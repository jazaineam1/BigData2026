#!/usr/bin/env python3
"""Regresiones de runtime/editoriales para S06 zero-to-hero."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "6_Neo4j_Contexto_Relacional.ipynb"
GRAPH = ROOT / "assets" / "tutoriales" / "neo4j-graph-lab-s06.html"
CHECKLIST = ROOT / "assets" / "tutoriales" / "s06-laboratorio-guiado.html"
AURA = ROOT / "assets" / "tutoriales" / "neo4j-aura-s06-paso-a-paso.html"


def text_of_notebook():
    nb = json.loads(NB.read_text(encoding="utf-8"))
    parts = []
    for c in nb["cells"]:
        value = c.get("source", [])
        parts.append("".join(value) if isinstance(value, list) else str(value))
    return nb, "\n".join(parts)


def main():
    errors = []
    for p in (NB, GRAPH, CHECKLIST, AURA):
        if not p.is_file(): errors.append(f"Falta {p.relative_to(ROOT)}")
    if errors: raise SystemExit("\n".join(errors))

    nb, text = text_of_notebook()
    graph = GRAPH.read_text(encoding="utf-8")
    checklist = CHECKLIST.read_text(encoding="utf-8")
    aura = AURA.read_text(encoding="utf-8")

    required = [
        "S06-ZERO-TO-HERO-V1",
        "Laboratorio zero-to-hero",
        "CREATE (e:EntidadDemo",
        "MATCH (e:EntidadDemo",
        "count(r) AS grado",
        "count(DISTINCT e)",
        "WITH v, count(r) AS grado",
        "MERGE (e:EntidadDemo",
        "CREATE CONSTRAINT demo_entidad_nit",
        "SHOW CONSTRAINTS",
        "UNWIND [",
        "UNWIND $filas AS fila",
        "Aplicación guiada — consultar los datos reales",
        "AUTOR_ALIAS",
        "Consulta guiada — contar procesos del par entidad–proveedor",
    ]
    for item in required:
        if item not in text: errors.append(f"Notebook sin {item!r}")

    forbidden = [
        "WOW 1", "WOW 2",
        'RELACION_PROCESO_PROVEEDOR = "____"',
        'OPERADOR_EXCLUSION = "____"',
        'input("Número de proveedor', 'input("Con tus números',
        'input("Justifica por qué Proceso', 'input("Límite concreto',
        'input("Alternativa de modelado',
        "Escribe tu consulta entre las comillas triples",
        "EJERCICIO S06-CONSULTA", "EJERCICIO S06-EXCLUIR",
    ]
    for item in forbidden:
        if item in text or item in graph or item in checklist:
            errors.append(f"Contenido no apto para novatos todavía presente: {item!r}")

    order = [
        text.find("## 4. Laboratorio zero-to-hero"),
        text.find("### 4.1 Primer nodo"),
        text.find("### 4.6 Contar conexiones"),
        text.find("### 4.8 `WITH`"),
        text.find("### 4.10 `CONSTRAINT`"),
        text.find("### 4.12 `UNWIND`"),
        text.find("## 5. Transferencia al caso real"),
        text.find("## 6. Aplicación guiada — consultar los datos reales"),
        text.find("## H2-R: la hipótesis relacional de esta sesión"),
    ]
    if any(x < 0 for x in order) or order != sorted(order):
        errors.append("La progresión zero-to-hero → carga real → aplicación → H2-R está rota")

    infra = [c for c in nb["cells"] if "nit_literal = str(nit_deseado)" in "".join(c.get("source", []))]
    if len(infra) != 1 or "hide-input" not in infra[0].get("metadata", {}).get("tags", []):
        errors.append("El Python que personaliza la consulta Cypher debe estar oculto")

    for item in [
        "Neo4j y Cypher de cero al caso Compras Claras", "Tu primer grafo de juguete",
        "CREATE (e:EntidadDemo", "SHOW CONSTRAINTS", "UNWIND [", "UNWIND $filas AS fila",
        "Table mide; Graph explica",
    ]:
        if item not in graph: errors.append(f"Curso visual sin {item!r}")
    if "WOW" in graph: errors.append("El curso visual no debe usar WOW como concepto")

    for item in [
        "Checklist zero-to-hero", "Crea tu primer nodo", "Crea una relación",
        "Protege la identidad", "Carga varias filas", "Responde la pregunta profesional",
    ]:
        if item not in checklist: errors.append(f"Checklist sin {item!r}")

    for item in ["Acceso · no teoría", "RETURN 1 AS conexion", "Connection URI", "User name", "Password", "crear manualmente un nodo"]:
        if item not in aura: errors.append(f"Tutorial Aura sin {item!r}")

    if errors:
        print("Validación S06 zero-to-hero fallida:")
        for e in errors: print("[ERROR]", e)
        raise SystemExit(1)
    print("[OK] S06 separa infraestructura Python del aprendizaje de Cypher")
    print("[OK] Progresión: construir → consultar → analizar → proteger/cargar → caso real → H2-R")
    print("[OK] Sin WOW ni respuestas abiertas a ciegas")

if __name__ == "__main__": main()
