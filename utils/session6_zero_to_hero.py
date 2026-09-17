#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Capa final S06: enseña Neo4j/Cypher antes de usar sintaxis avanzada.

Secuencia pedagógica:
problema -> nodos -> relaciones -> MATCH/WHERE -> agregaciones -> grado/hub ->
CREATE/MERGE -> constraints -> SET -> UNWIND/parámetros -> carga real.
"""
from __future__ import annotations

MARKER = "S06-ZERO-TO-HERO-V1"
GRAPH_TUTORIAL = "https://jazaineam1.github.io/BigData2026/assets/tutoriales/neo4j-graph-lab-s06.html"


def src(cell):
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def put(cell, text):
    cell["source"] = text.strip("\n").splitlines(keepends=True)


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip("\n").splitlines(keepends=True)}


def code(text, hidden=False, title=None):
    text = text.strip("\n")
    if title:
        text = f'#@title {title} {{ display-mode: "form" }}\n' + text
    cell = {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": text.splitlines(keepends=True)}
    if hidden:
        cell["metadata"] = {
            "tags": ["hide-input"],
            "jupyter": {"source_hidden": True},
            "cellView": "form",
            "colab": {"formView": "both"},
        }
    return cell


def find(cells, needle, cell_type=None):
    hits = []
    for i, cell in enumerate(cells):
        if cell_type and cell.get("cell_type") != cell_type:
            continue
        if needle in src(cell):
            hits.append(i)
    if len(hits) != 1:
        raise ValueError(f"Referencia ambigua {needle!r}: {hits}")
    return hits[0]


def zero_to_hero_block():
    return [
        md(f'''
---
## 4. Laboratorio zero-to-hero — construye tu primer grafo a mano

<!-- {MARKER} -->

Antes de cargar los **2.109 registros reales** vamos a construir un grafo diminuto directamente en **Aura Query**. Aquí no interviene Python: copiarás Cypher, ejecutarás y mirarás el resultado.

**Objetivo:** que cuando aparezcan `MERGE`, `CONSTRAINT`, `UNWIND` o `WITH` en la carga real ya sepas qué problema resuelven.

**Tutorial completo:** [Neo4j y Cypher de cero al caso Compras Claras ↗]({GRAPH_TUTORIAL})

### El ejemplo de juguete

Construiremos esto:

```text
Alcaldía Norte ──PUBLICA──> P1 ──ADJUDICADO_A──> Tecnología Uno SAS
                                                        ▲
                                                        │
Gobernación Sur ──PUBLICA──> P2 ──ADJUDICADO_A─────────┘
```

Al final podrás explicar por qué dos entidades pueden estar conectadas **sin tener una relación directa entre ellas**.
'''),
        md('''
### 4.1 Primer nodo: `CREATE`, label, variable y propiedades

Copia en Aura Query:

```cypher
CREATE (e:EntidadDemo {
  nit: "E1",
  nombre: "Alcaldía Norte"
})
RETURN e
```

**Léelo así:**

- `CREATE`: crea algo nuevo.
- `( ... )`: representa un nodo.
- `e`: variable temporal para referirse al nodo dentro de la consulta.
- `:EntidadDemo`: label o tipo del nodo.
- `{nit: ..., nombre: ...}`: propiedades.
- `RETURN e`: devuelve el nodo para verlo.

**Qué debes ver:** un círculo. Haz clic en él y comprueba `nit = E1` y `nombre = Alcaldía Norte`.
'''),
        md('''
### 4.2 Crea un Proceso y conéctalo

```cypher
CREATE (p:ProcesoDemo {
  id: "P1",
  nombre: "Compra de computadores"
})
RETURN p
```

Ahora relaciona los dos nodos:

```cypher
MATCH (e:EntidadDemo {nit:"E1"})
MATCH (p:ProcesoDemo {id:"P1"})
CREATE (e)-[:PUBLICA]->(p)
RETURN e, p
```

`MATCH` busca nodos existentes. `[:PUBLICA]` es el tipo de relación y `->` indica su dirección.

**Qué debes ver:** `EntidadDemo ──PUBLICA──> ProcesoDemo`.
'''),
        md('''
### 4.3 Agrega un Proveedor y completa el primer camino

```cypher
CREATE (v:ProveedorDemo {
  nit: "V1",
  nombre: "Tecnología Uno SAS"
})
RETURN v
```

```cypher
MATCH (p:ProcesoDemo {id:"P1"})
MATCH (v:ProveedorDemo {nit:"V1"})
CREATE (p)-[:ADJUDICADO_A]->(v)
RETURN p, v
```

Ya tienes:

```text
EntidadDemo → ProcesoDemo → ProveedorDemo
```

Eso es un **camino**: una secuencia de nodos y relaciones.
'''),
        md('''
### 4.4 Consulta lo que acabas de construir: `MATCH`, `RETURN`, `WHERE`, `LIMIT`

Primero devuelve nodos completos:

```cypher
MATCH (e:EntidadDemo)-[:PUBLICA]->(p:ProcesoDemo)-[:ADJUDICADO_A]->(v:ProveedorDemo)
RETURN e, p, v
```

Ahora devuelve propiedades concretas:

```cypher
MATCH (e:EntidadDemo)-[:PUBLICA]->(p:ProcesoDemo)
RETURN e.nombre AS entidad, p.id AS proceso
LIMIT 5
```

Y filtra:

```cypher
MATCH (e:EntidadDemo)
WHERE e.nit = "E1"
RETURN e
```

- `AS` cambia el nombre de una columna de salida.
- `WHERE` filtra coincidencias.
- `LIMIT` limita cuántas filas se muestran.
'''),
        md('''
### 4.5 Añade una segunda entidad que comparta proveedor

```cypher
CREATE (e2:EntidadDemo {nit:"E2", nombre:"Gobernación Sur"})
CREATE (p2:ProcesoDemo {id:"P2", nombre:"Compra de servidores"})
MATCH (v:ProveedorDemo {nit:"V1"})
CREATE (e2)-[:PUBLICA]->(p2)
CREATE (p2)-[:ADJUDICADO_A]->(v)
RETURN e2, p2, v
```

Ahora consulta el camino completo:

```cypher
MATCH camino=(a:EntidadDemo)-[:PUBLICA]->(:ProcesoDemo)-[:ADJUDICADO_A]->(v:ProveedorDemo)
             <-[:ADJUDICADO_A]-(:ProcesoDemo)<-[:PUBLICA]-(b:EntidadDemo)
WHERE a.nit <> b.nit
RETURN camino
```

`<>` significa **distinto de**.

**Qué debes ver:** Alcaldía Norte y Gobernación Sur llegan al mismo ProveedorDemo pasando por procesos diferentes.
'''),
        md('''
### 4.6 Contar conexiones: `count`, `AS`, `ORDER BY`, `DESC`

```cypher
MATCH (p:ProcesoDemo)-[r:ADJUDICADO_A]->(v:ProveedorDemo)
RETURN v.nombre AS proveedor,
       count(r) AS grado
ORDER BY grado DESC
```

- `r` es la variable de la relación.
- `count(r)` cuenta relaciones.
- `grado` es un alias para ese conteo.
- `ORDER BY ... DESC` ordena de mayor a menor.

En el ejemplo, `Tecnología Uno SAS` tiene grado 2 respecto de `ADJUDICADO_A` porque recibe dos relaciones de procesos.

Un **hub** o **nodo concentrador** es simplemente un nodo con muchas conexiones según una métrica definida. No significa fraude ni riesgo.
'''),
        md('''
### 4.7 `DISTINCT`: contar entidades, no caminos repetidos

Supón que una misma entidad tuviera dos procesos con el mismo proveedor. `count(e)` podría contarla dos veces.

```cypher
MATCH (e:EntidadDemo)-[:PUBLICA]->(:ProcesoDemo)-[:ADJUDICADO_A]->(v:ProveedorDemo)
RETURN v.nombre AS proveedor,
       count(e) AS filas,
       count(DISTINCT e) AS entidades_distintas
```

`DISTINCT` significa: **cuenta cada entidad una sola vez**.

Esta diferencia será esencial en Compras Claras: `grado` y `entidades_conectadas` no son la misma métrica.
'''),
        md('''
### 4.8 `WITH`: terminar una etapa y continuar con otra

```cypher
MATCH (p:ProcesoDemo)-[r:ADJUDICADO_A]->(v:ProveedorDemo)
WITH v, count(r) AS grado
ORDER BY grado DESC
LIMIT 1
MATCH (p:ProcesoDemo)-[r:ADJUDICADO_A]->(v)
RETURN v, r, p, grado
```

Léelo como una tubería:

```text
MATCH → contar → WITH conserva v y grado → otro MATCH → RETURN
```

`WITH` **no crea una tabla permanente**. Solo pasa variables y resultados a la siguiente etapa de la misma consulta.
'''),
        md('''
### 4.9 El problema de identidad: `CREATE` vs `MERGE`

`CREATE` significa **créalo siempre**. Si ejecutaras varias veces una creación con el mismo NIT, podrías terminar con nodos duplicados.

`MERGE` significa: **búscalo por este patrón; si existe reutilízalo, si no existe créalo**.

```cypher
MERGE (e:EntidadDemo {nit:"E3"})
SET e.nombre = "Entidad de Prueba"
RETURN e
```

Ejecuta esa consulta dos veces. Debe seguir existiendo un solo nodo `EntidadDemo` con `nit = E3`.

Regla de modelado:

```text
MERGE → identidad estable
SET   → atributos que pueden cambiar
```
'''),
        md('''
### 4.10 `CONSTRAINT`: protege la identidad

Si el NIT identifica a una Entidad, no queremos dos nodos `EntidadDemo` con el mismo NIT.

```cypher
CREATE CONSTRAINT demo_entidad_nit IF NOT EXISTS
FOR (e:EntidadDemo)
REQUIRE e.nit IS UNIQUE
```

También puedes proteger Proceso y Proveedor:

```cypher
CREATE CONSTRAINT demo_proceso_id IF NOT EXISTS
FOR (p:ProcesoDemo)
REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT demo_proveedor_nit IF NOT EXISTS
FOR (v:ProveedorDemo)
REQUIRE v.nit IS UNIQUE;
```

Compruébalas:

```cypher
SHOW CONSTRAINTS
```

**Importante:** `IS UNIQUE` evita valores repetidos cuando la propiedad existe; no significa automáticamente que todos los nodos estén obligados a tener esa propiedad. Una constraint tampoco fusiona duplicados que ya existían: si los datos ya violan la regla, crearla puede fallar.
'''),
        md('''
### 4.11 `SET`: identidad y atributos no son lo mismo

Evita usar propiedades cambiantes dentro de la identidad de `MERGE`.

**Mejor:**

```cypher
MERGE (e:EntidadDemo {nit:"E1"})
SET e.nombre = "Alcaldía Norte Actualizada"
RETURN e
```

Interpretación:

```text
nit    → identidad → MERGE
nombre → atributo  → SET
```

Esto permite actualizar un nombre sin crear otro nodo para la misma entidad.
'''),
        md('''
### 4.12 `UNWIND`: de una lista a muchas filas, todavía sin Python

```cypher
UNWIND [
  {id:"P10", nombre:"Proceso A"},
  {id:"P11", nombre:"Proceso B"},
  {id:"P12", nombre:"Proceso C"}
] AS fila
RETURN fila.id AS id, fila.nombre AS nombre
```

`UNWIND` toma una lista y entrega sus elementos uno por uno como filas.

Ahora úsalo para cargar varios nodos:

```cypher
UNWIND [
  {id:"P10", nombre:"Proceso A"},
  {id:"P11", nombre:"Proceso B"},
  {id:"P12", nombre:"Proceso C"}
] AS fila
MERGE (p:ProcesoDemo {id:fila.id})
SET p.nombre = fila.nombre
RETURN p
```

La carga real hará exactamente lo mismo, pero la lista llegará desde Python mediante `$filas`.
'''),
        md('''
### 4.13 Parámetros: por qué ves `$filas`, `$nit` o `$proveedor`

En Cypher, un nombre con `$` es un **parámetro**: el valor llega desde afuera de la consulta.

```cypher
MATCH (e:Entidad {nit:$nit})
RETURN e
```

Aquí la consulta describe la forma; Python envía el valor concreto de `$nit`.

En la carga real:

```cypher
UNWIND $filas AS fila
```

significa: “recibe una lista llamada `filas` y procésala elemento por elemento”.

No necesitas aprender `driver.execute_query()` hoy; ese driver es solo el puente entre Python y Neo4j.
'''),
        md('''
### 4.14 Limpieza del ejemplo · opcional

Cuando termines el ejemplo de juguete puedes borrar **solo** sus labels de demostración:

```cypher
MATCH (n)
WHERE n:EntidadDemo OR n:ProcesoDemo OR n:ProveedorDemo
DETACH DELETE n
```

`DETACH DELETE` elimina el nodo y sus relaciones. **No ejecutes una variante genérica sobre datos reales.**

### Lo que ya sabes antes de cargar Compras Claras

```text
CREATE      → crear siempre
MATCH       → buscar un patrón
WHERE       → filtrar
RETURN      → mostrar resultados
count       → contar
DISTINCT    → evitar duplicar identidades en un conteo
WITH        → pasar resultados a otra etapa
MERGE       → encontrar o crear por identidad
CONSTRAINT  → impedir estados de identidad inválidos
SET         → actualizar propiedades
UNWIND      → convertir una lista en filas
$parametro  → recibir un valor desde afuera
```

Ahora sí pasamos al extracto real.
'''),
    ]


def apply_zero_to_hero(cells):
    text = "\n".join(src(c) for c in cells)
    if MARKER in text:
        return cells

    load_idx = find(cells, "## 4.1 Cargar el grafo sin duplicar", "markdown")
    cells[load_idx:load_idx] = zero_to_hero_block()

    # La sección posterior ya no es el mini curso: es la transferencia a datos reales.
    old_idx = find(cells, "## 5. Mini curso de Cypher en Aura Query", "markdown")
    put(cells[old_idx], src(cells[old_idx]).replace(
        "## 5. Mini curso de Cypher en Aura Query",
        "## 5. Aplicación guiada — consultar los datos reales en Aura Query"
    ).replace(
        "Aquí empieza el aprendizaje central de la sesión.",
        "Aquí aplicas al extracto real lo que ya construiste en el laboratorio zero-to-hero."
    ))

    load_idx = find(cells, "## 4.1 Cargar el grafo sin duplicar", "markdown")
    put(cells[load_idx], '''
## 4.2 Transferencia al caso real — cargar el grafo sin duplicar

Ya construiste un grafo de juguete. La carga real repite las mismas ideas a mayor escala.

### Identidad del modelo real

| Nodo | Propiedad que usamos como identidad |
|---|---|
| `Entidad` | `nit` |
| `Proceso` | `id` |
| `Proveedor` | `nit` |

Por eso el orden es:

```text
CONSTRAINT → protege la identidad
UNWIND     → convierte la lista de registros en filas
MERGE      → reutiliza o crea el nodo por su identidad
SET        → actualiza propiedades descriptivas
MERGE      → crea la relación si todavía no existe
```

**Qué debe verse:** tres restricciones y una carga que puede repetirse sin multiplicar el mismo NIT/ID.

**Qué no hace una constraint:** no limpia duplicados antiguos y `IS UNIQUE` no equivale a “propiedad obligatoria”.
''')

    # Después de crear constraints, muestra evidencia observable en el motor.
    constraint_idx = find(cells, "constraints = [", "code")
    verify = [
        md('''
### Comprueba que las constraints existen

No confíes solo en “Restricciones listas”. En Aura Query puedes ejecutar:

```cypher
SHOW CONSTRAINTS
```

Busca las reglas asociadas a `Entidad.nit`, `Proceso.id` y `Proveedor.nit`.
'''),
        code('''if modo_neo4j:
    r_constraints = driver.execute_query("SHOW CONSTRAINTS")
    constraints_df = pd.DataFrame([r.data() for r in r_constraints.records])
    display(constraints_df)
else:
    print("SHOW CONSTRAINTS pendiente: estás en modo RESPALDO.")''', hidden=True, title="Verificar constraints en Neo4j"),
    ]
    cells[constraint_idx + 1:constraint_idx + 1] = verify

    unwind_idx = find(cells, "### Función usada: `UNWIND`", "markdown")
    put(cells[unwind_idx], '''
### Del ejemplo de juguete a la carga real: `UNWIND`

En el tutorial ya ejecutaste `UNWIND` sobre una lista escrita directamente en Cypher. Aquí la diferencia es solo el origen de la lista:

```text
Ejemplo de juguete     → UNWIND [ {...}, {...} ] AS fila
Carga real desde Python → UNWIND $filas AS fila
```

`$filas` es un parámetro enviado por el driver. A partir de ahí, cada `fila` se procesa igual:

```text
fila → MERGE identidad → SET atributos → MERGE relación
```

**Error frecuente:** usar `filas` como si fuera una fila individual; dentro de la carga trabajamos con `fila`.
''')

    return cells
