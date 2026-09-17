#!/usr/bin/env python3
"""Regresiones pedagógicas S06 para una audiencia principiante."""
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
        src = c.get("source", [])
        parts.append("".join(src) if isinstance(src, list) else str(src))
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
        "S06-NOVATOS-V3",
        "esta no es una clase de Python",
        "¿Qué es ese JSON?",
        "Mini curso de Cypher en Aura Query",
        "Consulta 0 — comprobar que Aura responde",
        "Consulta 1 — ver nodos Entidad",
        "Consulta 2 — una relación",
        "Consulta 3 — dos relaciones",
        "Consulta 4 — qué es el grado",
        "Consulta 5 — qué es un hub",
        "Consulta 6 — responder la pregunta profesional",
        "Table mide; Graph explica",
        "AUTOR_ALIAS",
        "Consulta guiada — contar procesos del par entidad–proveedor",
        "Ejecutar consulta guiada del proveedor explorado",
    ]
    for item in required:
        if item not in text: errors.append(f"Notebook sin {item!r}")

    forbidden = [
        "WOW 1", "WOW 2",
        'RELACION_PROCESO_PROVEEDOR = "____"',
        'OPERADOR_EXCLUSION = "____"',
        'input("Número de proveedor',
        'input("Con tus números',
        'input("Justifica por qué Proceso',
        'input("Límite concreto',
        'input("Alternativa de modelado',
        "Escribe tu consulta entre las comillas triples",
        "EJERCICIO S06-CONSULTA",
        "EJERCICIO S06-EXCLUIR",
    ]
    for item in forbidden:
        if item in text or item in graph or item in checklist:
            errors.append(f"Contenido no apto para novatos todavía presente: {item!r}")

    order = [
        "Consulta 1 — ver nodos Entidad",
        "Consulta 2 — una relación",
        "Consulta 3 — dos relaciones",
        "Consulta 4 — qué es el grado",
        "Consulta 5 — qué es un hub",
        "Consulta 6 — responder la pregunta profesional",
        "Profundización — comparar conectividad",
    ]
    pos = [text.find(x) for x in order]
    if any(x < 0 for x in pos) or pos != sorted(pos):
        errors.append("La progresión nodo→relación→camino→grado→hub→proveedor compartido→H2-R está rota")

    infra = [c for c in nb["cells"] if "nit_literal = str(nit_deseado)" in "".join(c.get("source", []))]
    if len(infra) != 1 or "hide-input" not in infra[0].get("metadata", {}).get("tags", []):
        errors.append("El Python que personaliza la consulta Cypher debe estar oculto")

    for item in ["Neo4j", "AuraDB", "Aura Query", "Cypher", "¿Qué es un hub?", "count(r) AS grado", "count(DISTINCT e)"]:
        if item not in graph: errors.append(f"Mini curso visual sin {item!r}")
    if "WOW" in graph: errors.append("El mini curso visual no debe usar WOW como concepto")

    for item in ["Checklist para no perderse", "Ve cinco Entidades", "Mide el grado", "Ve el hub", "Responde la pregunta"]:
        if item not in checklist: errors.append(f"Checklist sin {item!r}")
    if "WOW" in checklist: errors.append("El checklist no debe usar WOW")

    for item in ["Acceso · no teoría", "RETURN 1 AS conexion", "Connection URI", "User name", "Password"]:
        if item not in aura: errors.append(f"Tutorial Aura sin {item!r}")

    if errors:
        print("Validación S06 principiantes fallida:")
        for e in errors: print("[ERROR]", e)
        raise SystemExit(1)
    print("[OK] S06 separa infraestructura Python del aprendizaje de Cypher")
    print("[OK] Progresión: nodo → relación → camino → grado → hub → proveedor compartido → H2-R")
    print("[OK] Sin WOW ni respuestas abiertas a ciegas; tutoriales tienen funciones separadas")

if __name__ == "__main__": main()
