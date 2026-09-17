#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Limpieza final de S06 después de build_cells().

El generador histórico conserva algunos bloques avanzados. Esta capa los alinea
con la experiencia principiante sin volver a pedir respuestas abiertas.
"""
from __future__ import annotations

import base64
import json
import re


def src(cell):
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def put(cell, text):
    cell["source"] = text.strip("\n").splitlines(keepends=True)


def hide(cell, title=None):
    text = src(cell)
    if title and not text.startswith("#@title"):
        text = f'#@title {title} {{ display-mode: "form" }}\n' + text
        put(cell, text)
    metadata = dict(cell.get("metadata", {}))
    tags = list(metadata.get("tags", []))
    if "hide-input" not in tags:
        tags.append("hide-input")
    metadata.update({
        "tags": tags,
        "jupyter": {"source_hidden": True},
        "cellView": "form",
        "colab": {"formView": "both"},
    })
    cell["metadata"] = metadata


def replace_markdown(cells, needle, replacement):
    hits = [c for c in cells if c.get("cell_type") == "markdown" and needle in src(c)]
    if len(hits) != 1:
        raise ValueError(f"Markdown ambiguo {needle!r}: {len(hits)}")
    put(hits[0], replacement)


def rewrite_guided_query(cells):
    hits = [c for c in cells if c.get("cell_type") == "code" and "Consulta modelo ya completa" in src(c)]
    if len(hits) != 1:
        raise ValueError(f"Consulta guiada ambigua: {len(hits)}")
    put(hits[0], r'''#@title Ejecutar consulta guiada del proveedor explorado { display-mode: "form" }
# La consulta Cypher está explicada en el bloque anterior; esta celda solo la ejecuta/verifica.
consulta_propia = ''' + "'''" + r'''
MATCH (e:Entidad {nit:$ancla})-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor {nit:$proveedor})
RETURN count(DISTINCT p) AS procesos
''' + "'''" + r'''
if modo_neo4j:
    procesos_propios = int(driver.execute_query(
        consulta_propia,
        ancla=nit_deseado,
        proveedor=str(proveedor_elegido["nit_proveedor"])
    ).records[0]["procesos"])
else:
    procesos_propios = int(
        vecindario_df.loc[vecindario_df["nit_entidad"].eq(nit_deseado), "proceso"].nunique()
    )
    print("Cypher pendiente de ejecución en Aura; el número se verifica con pandas.")
esperados_propios = int(proveedor_elegido["procesos_con_entidad"])
assert procesos_propios == esperados_propios
print("✅ Procesos del par entidad–proveedor:", procesos_propios)
print("Esperado según la tabla:", esperados_propios)
''')
    hide(hits[0])


def rewrite_question(cells):
    pattern = re.compile(r'pregunta_codificada\("([^\"]+)"\)')
    changed = 0
    for cell in cells:
        if cell.get("cell_type") != "code":
            continue
        text = src(cell)
        match = pattern.search(text)
        if not match:
            continue
        try:
            payload = json.loads(base64.b64decode(match.group(1)).decode("utf-8"))
        except Exception:
            continue
        if payload.get("tema") != "El proveedor explorado y H2-R":
            continue
        payload.update({
            "tema": "Qué demuestra el grafo",
            "pregunta": "Si dos entidades llegan al mismo proveedor mediante procesos observados, ¿qué conclusión sí está respaldada?",
            "opciones": [
                "Que el proveedor cometió una irregularidad.",
                "Que esas entidades comparten un proveedor en los registros observados.",
                "Que un grado alto demuestra colusión.",
                "Que el nodo más centrado en Graph tiene mayor riesgo."
            ],
            "correcta": 1,
            "retro": [
                "La relación observada no prueba irregularidad.",
                "Correcto: el grafo sostiene la conexión registrada y nada más.",
                "El grado mide conexiones, no colusión.",
                "El layout de Aura busca legibilidad; posición y tamaño no son riesgo."
            ],
            "contexto": "La consulta muestra Entidad → Proceso → Proveedor ← Proceso ← otra Entidad."
        })
        token = base64.b64encode(json.dumps(payload, ensure_ascii=False).encode("utf-8")).decode("ascii")
        put(cell, text[:match.start(1)] + token + text[match.end(1):])
        changed += 1
    if changed != 1:
        raise ValueError(f"Se esperaba reescribir una autoevaluación, se cambiaron {changed}")


def finalize_cells(cells):
    replace_markdown(cells, "## 7. La consulta que justifica Neo4j", '''
## 7. Verificación — ¿Neo4j y pandas cuentan lo mismo?

Ya aprendiste el patrón en Cypher. Esta sección **no introduce sintaxis nueva**: comprueba que Neo4j y pandas respondan la misma pregunta con los mismos conteos.

> Ejecuta las celdas y concéntrate en las salidas. El Python de apoyo está plegado cuando solo prepara datos o consultas.
''')

    replace_markdown(cells, "**HAZ ESTO AHORA.** Si estás en Aura, copia la consulta que acabas de imprimir", '''
### Visualización adicional · opcional

La celda técnica anterior prepara otra consulta de caminos para una entidad de demostración muy conectada. Está pensada para el docente o para quien quiera practicar más en Aura.

**No necesitas ejecutarla para completar el núcleo de S06.** Si la pruebas, recuerda:

- el nodo central no es automáticamente “sospechoso”;
- el límite visual no representa el total de conexiones;
- Graph sirve para explicar estructura y Table para comprobar números.
''')

    replace_markdown(cells, "## 8. CRUD seguro y tu propio vecindario", '''
---
## 8. Ejemplo guiado — explorar un proveedor

El cuaderno toma automáticamente el primer proveedor de la tabla ordenada por conectividad. **No tienes que escoger un número ni inventar un NIT.**

La celda siguiente muestra hasta cinco proveedores para que veas el contexto y después declara cuál se usará en el ejemplo.

**Qué debes mirar:** nombre del proveedor, número de entidades conectadas y tabla de procesos del vecindario.

> El CRUD con nodos `S06-DEMO` es una demostración segura: crea, modifica y elimina únicamente datos de juguete.
''')

    replace_markdown(cells, "### EJERCICIO S06-EXCLUIR", '''
### Ejemplo guiado — excluir la entidad ancla

`entidades_conectadas` incluye la entidad que estamos estudiando. Para contar solo **otras entidades**, Cypher usa `<>`, que significa **“distinto de”**.

```cypher
MATCH (otra:Entidad)-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v:Proveedor {nit:$proveedor})
WHERE otra.nit <> $ancla
RETURN count(DISTINCT otra) AS otras_entidades
```

**Ejemplo:** si un proveedor conecta 19 entidades incluyendo la ancla, quedan 18 otras entidades. Si conecta solo la ancla, el resultado correcto es 0.

La celda siguiente ya contiene `<>`; ejecútala y verifica el número.
''')

    replace_markdown(cells, "### EJERCICIO S06-CONSULTA", '''
### Consulta guiada — contar procesos del par entidad–proveedor

No tienes que escribirla desde cero. Esta es la consulta completa:

```cypher
MATCH (e:Entidad {nit:$ancla})-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor {nit:$proveedor})
RETURN count(DISTINCT p) AS procesos
```

**Qué pregunta responde:** “¿cuántos procesos distintos de mi entidad fueron adjudicados al proveedor explorado?”

- `$ancla`: NIT de la entidad.
- `$proveedor`: NIT del proveedor.
- `DISTINCT p`: evita contar dos veces el mismo proceso.

La celda siguiente ejecuta/verifica esta consulta automáticamente.
''')

    replace_markdown(cells, "### La evidencia no termina en el grafo", '''
### La ficha final ya trae respuestas modelo

Para una primera sesión de Neo4j no vas a adivinar una redacción. La ficha usa ejemplos explícitos:

- **Por qué Proceso es nodo:** tiene identidad y propiedades propias y participa en el camino Entidad → Proceso → Proveedor.
- **Límite:** compartir proveedor no demuestra irregularidad; faltan datos de competencia, contexto y comportamiento fuera del extracto.
- **Alternativa:** una organización única con roles Entidad/Proveedor sería válida, pero aquí se mantienen roles separados para facilitar la lectura inicial.

Solo cambia `AUTOR_ALIAS` si necesitas identificar tu equipo.
''')

    rewrite_guided_query(cells)
    rewrite_question(cells)

    # Python de infraestructura: ejecutable, pero no parte del contenido que debe memorizar el estudiante.
    hide_targets = [
        ("# Infraestructura de verificación", "Calcular referencia H2-R"),
        ("query_demo_top =", "Preparar demostración adicional"),
        ("query_visual_demo =", "Preparar consulta visual adicional"),
        ("Cinco proveedores de ejemplo", "Preparar proveedor de demostración"),
        ("OPERADOR_EXCLUSION = \"<>\"", "Verificar otras entidades"),
    ]
    for needle, title in hide_targets:
        hits = [c for c in cells if c.get("cell_type") == "code" and needle in src(c)]
        if len(hits) == 1:
            hide(hits[0], title)

    return cells
