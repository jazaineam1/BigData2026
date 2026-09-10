#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera el quiz de fundamentos de Neo4j: 10 tareas sobre el grafo de juguete
que cada estudiante ya construyó en el calentamiento de S6-ALT (película +
red de amigos). No trae el Cypher resuelto: cada tarea es una celda con la
pregunta y sin el código (escalón 3 de AGENTS.md §5), para que la entrega
dependa de la ejecución propia, no de copiar la respuesta de otro.

Basado en el taller de referencia del docente (Cuadernos/Neo4j/Taller_2_Neo4j.ipynb),
ampliado de 5 a 10 tareas y adaptado al grafo del calentamiento en vez de un
grafo nuevo, para que el estudiante no tenga que reconstruir nada.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.make_notebook import code, md, save, validate

OUTPUT = "Cuadernos/Quiz_Neo4j_Fundamentos.ipynb"
COLAB = "https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/Quiz_Neo4j_Fundamentos.ipynb"


def tarea(numero: int, titulo: str, enunciado: str, resultado_esperado: str, scaffold: str) -> list:
    return [
        md(f'''
### Tarea {numero} — {titulo}

{enunciado}

**Resultado que debes reportar:** {resultado_esperado}
'''),
        code(scaffold),
    ]


def build_cells():
    cells = [
        md(f'''<a href="{COLAB}" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Abrir Quiz Neo4j en Colab"></a>'''),
        md('''
# Quiz — Fundamentos de Neo4j

## Universidad Central
> ### Facultad de Ingeniería y Ciencias Básicas
> ### Maestría en Analítica de Datos — BIG DATA (64491093)

**Para qué es este quiz.** Evalúa lo que practicaste en el calentamiento de la Sesión 6: crear nodos y relaciones, actualizar, consultar con filtros y agregaciones, y borrar de forma segura. Usa el **mismo grafo de juguete** (la película The Matrix, sus actores, y la red de amigos Alice/Bob/Peter/Anna) que ya construiste en tu propia instancia de Aura durante la clase.

**Cómo se evalúa.** Cada tarea pide un resultado concreto — un número, un nombre, una lista — producido por tu propia consulta. No hay opción múltiple: si no ejecutaste la consulta correcta en tu instancia, no tienes el resultado que se pide.

**Cómo entregar.** Ejecuta este cuaderno completo con salidas visibles, descárgalo (`Archivo → Descargar → .ipynb`) y súbelo al lugar que indique tu docente.
'''),
        md('''
## Antes de empezar: reconecta a tu instancia

Si vienes directamente del cuaderno de la clase y tu runtime sigue vivo, `driver` ya existe — puedes saltarte la conexión. Si es un cuaderno nuevo, el runtime se reinició, o ya ejecutaste la limpieza del cuaderno de clase, esta celda **reconstruye el grafo de juguete sola** — no necesitas hacer nada especial.
'''),
        code("""
!pip install -q "neo4j>=6,<7"
from getpass import getpass
from neo4j import GraphDatabase

if "driver" not in globals():
    URI = input("Connection URI: ").strip()
    USER = input("User name: ").strip()
    PASSWORD = getpass("Password (no se muestra): ")
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

driver.verify_connectivity()
comprobacion = driver.execute_query(
    "MATCH (n) WHERE n:Movie OR n:Person RETURN count(n) AS nodos_de_juguete",
)
nodos = comprobacion.records[0]["nodos_de_juguete"]

if nodos == 0:
    print("No había grafo de juguete en esta instancia (o ya lo limpiaste). Reconstruyéndolo...")
    driver.execute_query("MERGE (:Movie {title: $title})", title="The Matrix")
    driver.execute_query("MERGE (:Person {name: $name})", name="Keanu Reeves")
    driver.execute_query("MERGE (:Person {name: $name})", name="Carrie-Anne Moss")
    for actor in ["Keanu Reeves", "Carrie-Anne Moss"]:
        driver.execute_query('''
            MATCH (actor:Person {name:$name})
            MATCH (pelicula:Movie {title:$title})
            MERGE (actor)-[:ACTED_IN]->(pelicula)
        ''', name=actor, title="The Matrix")
    driver.execute_query("MATCH (p:Person {name:$name}) SET p.age = $age", name="Keanu Reeves", age=41)

    amigos = [
        {"name": "Alice", "age": 42, "friends": ["Bob", "Peter", "Anna"]},
        {"name": "Bob", "age": 19},
        {"name": "Peter", "age": 50},
        {"name": "Anna", "age": 30},
    ]
    driver.execute_query('''
        UNWIND $filas AS fila
        MERGE (p:Person {name: fila.name})
        SET p.age = fila.age
    ''', filas=amigos)
    con_amigos = [a for a in amigos if a.get("friends")]
    driver.execute_query('''
        UNWIND $filas AS fila
        MATCH (p:Person {name: fila.name})
        UNWIND fila.friends AS nombre_amigo
        MATCH (amigo:Person {name: nombre_amigo})
        MERGE (p)-[:KNOWS]->(amigo)
    ''', filas=con_amigos)

    comprobacion = driver.execute_query(
        "MATCH (n) WHERE n:Movie OR n:Person RETURN count(n) AS nodos_de_juguete",
    )
    nodos = comprobacion.records[0]["nodos_de_juguete"]

print("Conexión verificada. Nodos de juguete disponibles:", nodos)
"""),
    ]

    cells += tarea(
        1, "Contar personas",
        "Cuenta cuántos nodos con label `Person` existen en tu grafo en este momento.",
        "un número entero.",
        '''
resultado_1 = None  # reemplaza con tu consulta y el conteo obtenido

# Escribe aquí tu consulta Cypher (MATCH ... RETURN count(...))

print("Tarea 1 — personas en el grafo:", resultado_1)
''',
    )
    cells += tarea(
        2, "Películas y su elenco",
        "Lista el título de cada película (`Movie`) junto con cuántos actores tiene, usando la relación `ACTED_IN`.",
        "el título de la película y el número de actores.",
        '''
resultado_2 = None  # reemplaza con una lista de tuplas (titulo, num_actores) o un DataFrame

# Escribe aquí tu consulta Cypher

print("Tarea 2 — películas y elenco:", resultado_2)
''',
    )
    cells += tarea(
        3, "Amigos menores de 21",
        "Encuentra quién conoce (`KNOWS`) a alguien menor de 21 años, y reporta ambos nombres: quién conoce y a quién.",
        "el nombre de quien conoce y el nombre de la persona menor de 21.",
        '''
resultado_3 = None  # reemplaza con (quien_conoce, menor_de_21)

# Escribe aquí tu consulta Cypher

print("Tarea 3 — conexión con menor de 21:", resultado_3)
''',
    )
    cells += tarea(
        4, "Actualizar una propiedad",
        "Actualiza la edad de Carrie-Anne Moss a 55 usando `SET`, y **confirma el cambio** con una segunda consulta que lea su edad después de actualizar.",
        "la edad de Carrie-Anne Moss después de tu `SET` (debe ser 55).",
        '''
# Paso 1: actualiza con SET

# Paso 2: confirma con una consulta de lectura
resultado_4 = None  # reemplaza con la edad leída después de actualizar

print("Tarea 4 — edad confirmada de Carrie-Anne Moss:", resultado_4)
''',
    )
    cells += tarea(
        5, "Decisión de modelado: una relación nueva",
        "Crea una relación `KNOWS` nueva entre Bob y Peter. Decide en qué dirección la creas (`Bob -> Peter` o `Peter -> Bob`) y **explica en una frase** cuál alternativa descartaste y por qué.",
        "la dirección que elegiste, tu alternativa descartada, y la razón.",
        '''
# Escribe aquí tu MERGE de la nueva relación KNOWS

decision_direccion = ""  # "Bob -> Peter" o "Peter -> Bob"
alternativa_descartada = ""  # la otra dirección
razon = ""  # por qué elegiste una y no la otra

print("Tarea 5 — decisión:", decision_direccion, "| descartada:", alternativa_descartada, "| razón:", razon)
''',
    )
    cells += tarea(
        6, "Ordenar resultados",
        "Consulta los amigos de Alice (`KNOWS`) ordenados por edad, de mayor a menor.",
        "la lista de nombres en el orden correcto.",
        '''
resultado_6 = None  # reemplaza con la lista ordenada de nombres

# Escribe aquí tu consulta Cypher con ORDER BY

print("Tarea 6 — amigos de Alice, de mayor a menor edad:", resultado_6)
''',
    )
    cells += tarea(
        7, "Contar relaciones salientes",
        "Cuenta cuántas relaciones `KNOWS` salen de Alice (después de la tarea 5, esto puede seguir siendo 3 si la relación nueva no la involucra a ella).",
        "un número entero.",
        '''
resultado_7 = None  # reemplaza con el conteo

# Escribe aquí tu consulta Cypher

print("Tarea 7 — relaciones KNOWS que salen de Alice:", resultado_7)
''',
    )
    cells += tarea(
        8, "Verificar ausencia de relación",
        "Verifica si existe alguna persona (`Person`) que no tenga ninguna relación `KNOWS` ni `ACTED_IN`, en ningún sentido.",
        "sí/no, y el nombre si existe alguna.",
        '''
resultado_8 = None  # reemplaza con la respuesta: nombre(s) o "ninguna"

# Escribe aquí tu consulta Cypher

print("Tarea 8 — personas sin ninguna relación:", resultado_8)
''',
    )
    cells += tarea(
        9, "El límite de DELETE sin DETACH",
        "Intenta borrar el nodo de Bob usando `DELETE` **sin** `DETACH` (a sabiendas de que probablemente falle). Copia el mensaje de error exacto que te devuelve Neo4j, y explica en una frase por qué el motor lo bloquea.",
        "el mensaje de error textual, y tu explicación de por qué ocurre.",
        '''
mensaje_error = ""  # pega aquí el texto exacto del error
explicacion = ""  # por qué Neo4j bloquea este DELETE

try:
    driver.execute_query("MATCH (p:Person {name:$name}) DELETE p", name="Bob")
except Exception as e:
    mensaje_error = str(e)

print("Tarea 9 — error obtenido:", mensaje_error)
print("Tarea 9 — explicación:", explicacion)
''',
    )
    cells += tarea(
        10, "Borrado correcto",
        "Ahora borra a Peter correctamente con `DETACH DELETE`, y confirma con una consulta de lectura que ya no aparece en el grafo.",
        "confirmación de que Peter ya no existe (la consulta debe devolver una lista vacía).",
        '''
# Paso 1: borra con DETACH DELETE

# Paso 2: confirma con una consulta de lectura
resultado_10 = None  # reemplaza con el resultado de la verificación (debe estar vacío)

print("Tarea 10 — Peter sigue en el grafo:", resultado_10)
''',
    )

    cells.append(md('''
---
## Rúbrica

| Criterio | Completo | Parcial | Sin evidencia | Peso |
|---|---|---|---|---:|
| Ejecución (tareas 1-4, 6-8, 10) | las 8 consultas corren y el resultado impreso es correcto | la mayoría corre, 1-2 con error | no ejecuta o resultados vacíos sin explicación | 50 |
| Decisión de modelado (tarea 5) | dirección elegida + alternativa descartada + razón concreta | solo dirección, sin alternativa razonada | no responde o alternativa inventada | 25 |
| Manejo del error (tarea 9) | mensaje de error real + explicación correcta del porqué | solo el mensaje, sin explicación | no lo intenta o inventa el error | 25 |

**Nota.** El resultado de cada tarea debe venir de tu propia ejecución en tu propia instancia — un número o una lista sin la consulta que lo produjo no es evidencia.
'''))

    cells.append(code("""
try:
    driver.close()
    print("Conexión Neo4j cerrada.")
except Exception:
    pass
"""))

    return cells


def main():
    cells = build_cells()
    validate(cells)
    save(cells, OUTPUT)
    print(f"[OK] Quiz Neo4j generado: {len(cells)} celdas")


if __name__ == "__main__":
    main()
