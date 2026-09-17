#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Capa editorial S06 para principiantes: Neo4j/Cypher primero, Python oculto."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH_TUTORIAL = "https://jazaineam1.github.io/BigData2026/assets/tutoriales/neo4j-graph-lab-s06.html"
MARKER = "S06-BEGINNER-V1"


def s(cell):
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def put(cell, text):
    cell["source"] = text.strip("\n").splitlines(keepends=True)


def find(cells, needle, starts=False):
    hits = [i for i, c in enumerate(cells) if (s(c).startswith(needle) if starts else needle in s(c))]
    if len(hits) != 1:
        raise ValueError(f"Referencia S06 ambigua {needle!r}: {hits}")
    return hits[0]


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip("\n").splitlines(keepends=True)}


def code(text, hidden=False, title=None):
    text = text.strip("\n").replace('"""', "'''")
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


def hide(cell, title=None):
    meta = cell.setdefault("metadata", {})
    tags = set(meta.get("tags", []))
    tags.add("hide-input")
    meta["tags"] = sorted(tags)
    meta["jupyter"] = {**meta.get("jupyter", {}), "source_hidden": True}
    meta["cellView"] = "form"
    meta["colab"] = {**meta.get("colab", {}), "formView": "both"}
    if title and not s(cell).lstrip().startswith("#@title"):
        cell["source"] = [f'#@title {title} {{ display-mode: "form" }}\n'] + cell.get("source", [])


def simplify_intro(cells):
    i = find(cells, "# Sesión 6 — De la fila priorizada")
    put(cells[i], r'''
# Sesión 6 — De la fila priorizada al contexto relacional con Neo4j

## Universidad Central
> ### Facultad de Ingeniería y Ciencias Básicas
> ### Maestría en Analítica de Datos — BIG DATA (64491093)

**Caso conductor:** Compras Claras

### La pregunta de hoy

En S5 Laura eligió un proceso para revisar. Ese registro candidato **no trae un proveedor adjudicado observado en este extracto**, así que no vamos a inventarlo. En S6 usamos la **entidad que publicó ese proceso** y preguntamos:

> **¿Qué proveedores aparecen en el historial adjudicado de esa entidad y cuáles de ellos también aparecen vinculados con otras entidades?**

Eso sí lo puede responder un grafo: **Entidad → Proceso → Proveedor → otros Procesos → otras Entidades**.

### Lo importante de esta sesión

1. entender qué es un **nodo**, una **relación** y un **camino**;
2. aprender las primeras consultas en **Cypher**;
3. ver los resultados en **Aura Query** como tabla y como grafo;
4. contar conexiones, entender qué es el **grado** y qué significa **hub o nodo concentrador**;
5. encontrar proveedores compartidos entre entidades;
6. explicar qué demuestra el grafo y qué **no** demuestra.

> **No necesitas saber Python.** Python prepara y verifica los datos por detrás. El lenguaje que aprenderás hoy es **Cypher**, el lenguaje de consulta de Neo4j.

### Producto observable

Al terminar tendrás una ficha sencilla con el proceso de S5, la entidad de trabajo, el proveedor explorado, cuántas entidades conecta, una consulta Cypher explicada y un límite interpretativo. El archivo `s06_contexto_procesos.jsonl` queda preparado para S7.
''')

    i = find(cells, "## El hilo del evaluador")
    put(cells[i], r'''
## Del proceso de S5 al grafo de S6

```text
S5: Proceso elegido
        ↓
Entidad que lo publicó
        ↓
procesos históricos adjudicados
        ↓
Proveedores
        ↓
otras Entidades
```

**Importante:** el proceso candidato de S5 sirve como punto de partida para identificar la entidad. Las relaciones con proveedores provienen de los **registros históricos adjudicados** del extracto; no inventamos una adjudicación para el proceso candidato.
''')

    i = find(cells, "## Mapa de la sesión")
    put(cells[i], r'''
## Mapa de la sesión

| Paso | Qué aprenderás | Herramienta | Resultado visible |
|---|---|---|---|
| 1 | recuperar el proceso y la entidad | Colab | ancla clara |
| 2 | nodo, relación, propiedad y camino | cuaderno | modelo mínimo |
| 3 | conectar Aura | AuraDB | `RETURN 1` |
| 4 | cargar el grafo | Colab → Neo4j | nodos y relaciones |
| 5 | aprender Cypher desde cero | Aura Query | consultas 1–6 |
| 6 | interpretar conexiones | Graph + Table | grado, hub y proveedor compartido |
| 7 | profundización opcional | pandas + Neo4j | H2-R y verificación |
| 8 | guardar evidencia | Colab | ficha + JSONL |

- 🧠 **ENTIENDE:** primero lee el ejemplo.
- ▶️ **EJECUTA:** copia/ejecuta la consulta indicada.
- 🔎 **MIRA:** compara lo que esperabas con Graph o Table.
- ✏️ **MODIFICA:** solo cambios pequeños y guiados; no tendrás que adivinar una solución completa.
''')


def simplify_anchor(cells):
    i = find(cells, "## 1. Recuperar el proceso que Laura abrió en S5")
    put(cells[i], r'''
---
## 1. Recuperar el proceso que Laura abrió en S5

### ¿Qué es `s05_ancla_s06.json`?

Es un archivo pequeño que guarda **la selección de S5**. No es una base de datos y **no se carga en Aura**.

Ejemplo:

```json
{
  "id_proceso": "CO1.REQ.2622868",
  "entidad": "FUERZA AEROESPACIAL COLOMBIANA",
  "nit_entidad": "899999102"
}
```

- `id_proceso`: el proceso elegido;
- `entidad`: quién lo publicó;
- `nit_entidad`: el identificador que usaremos para buscar esa entidad en Neo4j.

**Ruta recomendada para la primera vez:** usa **Ejemplo del curso**. Si conservaste el JSON de S5, puedes elegir **Mi archivo de S5**. El código que lee el JSON queda oculto porque hoy no estamos aprendiendo Python.
''')

    i = find(cells, "# El cuaderno trae el ancla pedagógica versionada", starts=True)
    put(cells[i], r'''#@title Elegir el punto de partida { display-mode: "form" }
from pathlib import Path
import json
RUTA_ANCLA = "Ejemplo del curso"  #@param ["Ejemplo del curso", "Mi archivo de S5"]
archivo_s5 = Path("s05_ancla_s06.json")

if RUTA_ANCLA == "Mi archivo de S5":
    if not archivo_s5.is_file():
        try:
            from google.colab import files
            print("Selecciona el archivo s05_ancla_s06.json que descargaste en S5.")
            subidos = files.upload()
            if "s05_ancla_s06.json" not in subidos:
                print("No se seleccionó el archivo esperado. Usaremos el ejemplo del curso.")
                RUTA_ANCLA = "Ejemplo del curso"
            else:
                archivo_s5.write_bytes(subidos["s05_ancla_s06.json"])
        except ImportError:
            print("No se encontró el archivo local. Usaremos el ejemplo del curso.")
            RUTA_ANCLA = "Ejemplo del curso"

if RUTA_ANCLA == "Mi archivo de S5" and archivo_s5.is_file():
    candidato = json.loads(archivo_s5.read_text(encoding="utf-8-sig"))
    faltantes = [k for k in ["id_proceso", "entidad", "nit_entidad"] if not str(candidato.get(k, "")).strip()]
    if faltantes:
        print("El JSON no tiene los campos esperados. Usaremos el ejemplo del curso.")
        ancla_original = dict(manifest["ancla_pedagogica"])
        origen_ancla = "ejemplo del curso"
    else:
        ancla_original = candidato
        origen_ancla = "archivo propio S5"
else:
    ancla_original = dict(manifest["ancla_pedagogica"])
    origen_ancla = "ejemplo del curso"

print("✅ Punto de partida cargado")
print("Proceso:", ancla_original["id_proceso"])
print("Entidad:", ancla_original["entidad"])
print("NIT:", ancla_original["nit_entidad"])
print("Origen:", origen_ancla)
''')
    hide(cells[i], "Elegir ejemplo del curso o mi archivo S5")


def simplify_concepts(cells):
    i = find(cells, "Antes de escribir Cypher, cinco palabras y nada más")
    put(cells[i], r'''
## 3. Antes de Cypher: cuatro ideas y un patrón

No memorices sintaxis todavía. Primero aprende a leer el dibujo.

| Concepto | En palabras simples | En S6 |
|---|---|---|
| **Nodo** | una cosa que queremos representar | una Entidad, un Proceso o un Proveedor |
| **Propiedad** | un dato de ese nodo | `nit`, `nombre`, `precio_base` |
| **Relación** | una conexión con significado | `PUBLICA`, `ADJUDICADO_A` |
| **Camino** | una secuencia de nodos y relaciones | Entidad → Proceso → Proveedor |
| **Patrón** | la forma que queremos encontrar | `(e)-[:PUBLICA]->(p)` |

```text
Entidad → PUBLICA → Proceso → ADJUDICADO_A → Proveedor
```

Cuando veas esto en Cypher:

```cypher
MATCH (e:Entidad)-[:PUBLICA]->(p:Proceso)
```

léelo así:

> **Busca una Entidad que PUBLICA un Proceso.**

Esa traducción de dibujo ↔ patrón es más importante que memorizar símbolos.
''')

    i = find(cells, 'RELACION_PROCESO_PROVEEDOR = "ADJUDICADO_A"', starts=True)
    put(cells[i], r'''RELACION_PROCESO_PROVEEDOR = "ADJUDICADO_A"
patron_estudiante = f"(p:Proceso)-[:{RELACION_PROCESO_PROVEEDOR}]->(v:Proveedor)"
print("✅ Patrón de ejemplo:")
print(patron_estudiante)
print("Se lee: un Proceso fue ADJUDICADO_A un Proveedor.")
''')

    i = find(cells, "### La alternativa que descartamos")
    put(cells[i], s(cells[i]) + r'''

### Por qué `Proceso` es un nodo

No tienes que inventar una justificación. Usa esta idea:

> **Ejemplo de respuesta:** “Proceso es un nodo porque tiene identidad y propiedades propias y queremos recorrer relaciones desde la Entidad hasta el Proveedor pasando por ese proceso.”

Una alternativa sería guardar el proceso como propiedad de una relación directa Entidad→Proveedor. Es más corta, pero perderíamos al proceso como objeto que podemos consultar, inspeccionar y reutilizar en S7.
''')


def improve_contract(cells):
    i = find(cells, "# Ambas métricas usan NIT", starts=True)
    put(cells[i], r'''# Infraestructura de verificación: pandas calcula la referencia sin ser contenido a memorizar.
prov_ancla = hist_ancla.groupby("nit_proveedor")["id_proceso"].nunique().rename("procesos_con_entidad")
prov_global = hist.groupby("nit_proveedor")["nit_entidad"].nunique().rename("entidades_conectadas")
resultado_completo_pd = pd.concat([prov_ancla, prov_global], axis=1).loc[prov_ancla.index].reset_index()
resultado_completo_pd["procesos_con_entidad"] = resultado_completo_pd["procesos_con_entidad"].astype(int)
resultado_completo_pd["proveedor"] = resultado_completo_pd["nit_proveedor"].map(nombres_proveedor)
resultado_completo_pd = resultado_completo_pd.sort_values(
    ["entidades_conectadas", "procesos_con_entidad", "nit_proveedor"],
    ascending=[False, False, True]
).reset_index(drop=True)
esperado_pd = resultado_completo_pd.head(10).copy()
candidatas_hist = hist[hist["es_entidad_candidata_s05"]].copy()
candidatas_hist["conexiones_proveedor"] = candidatas_hist["nit_proveedor"].map(prov_global)
maximos_candidatas = candidatas_hist.groupby("nit_entidad")["conexiones_proveedor"].max()
MEDIANA_H2R = float(maximos_candidatas.median())
if "mediana_maximo_conectadas_por_nit" in manifest:
    assert MEDIANA_H2R == float(manifest["mediana_maximo_conectadas_por_nit"])
proveedor_h2r = resultado_completo_pd.iloc[0].copy()
maximo_h2r = int(proveedor_h2r["entidades_conectadas"])
if uso_respaldo_s06:
    desenlace_h2r_pd = "comparación descriptiva del ejemplo del curso"
elif maximo_h2r > MEDIANA_H2R:
    desenlace_h2r_pd = "conectividad mayor que la mediana de referencia"
else:
    desenlace_h2r_pd = "conectividad igual o menor que la mediana de referencia"
print("Proveedor de mayor conectividad:", proveedor_h2r["proveedor"])
print("Entidades conectadas:", maximo_h2r)
print("Mediana de referencia:", MEDIANA_H2R)
print("Lectura:", desenlace_h2r_pd)
esperado_pd
''')
    hide(cells[i], "Calcular referencia H2-R con pandas (infraestructura)")


def improve_graph_properties(cells):
    i = find(cells, "cols = [", starts=True)
    text = s(cells[i])
    text = text.replace(
        '"nombre_proceso", "descripcion", "precio_base", "modalidad", "proveedor",',
        '"nombre_proceso", "descripcion", "precio_base", "valor_adjudicado", "modalidad", "proveedor",',
    )
    text = text.replace("    p.valor = fila.precio_base,", "    p.precio_base = fila.precio_base,")
    text = text.replace(
        "MERGE (p)-[:ADJUDICADO_A]->(v)",
        "MERGE (p)-[a:ADJUDICADO_A]->(v)\nSET a.valor_adjudicado = fila.valor_adjudicado",
    )
    put(cells[i], text)
    for cell in cells:
        body = s(cell)
        if "p.valor AS precio_base" in body:
            put(cell, body.replace("p.valor AS precio_base", "p.precio_base AS precio_base").replace("ORDER BY entidad, valor DESC", "ORDER BY entidad, precio_base DESC"))


def beginner_lab():
    return [
        md(f'''
---
## 5. Mini curso de Cypher — de cero al proveedor compartido

<!-- {MARKER} -->

**Objetivo:** aprender Neo4j y Cypher, no Python. Las consultas que debes leer están visibles; las celdas Python que preparan datos permanecen plegadas.

**Tutorial corto:** [Mini curso visual de Cypher ↗]({GRAPH_TUTORIAL})
'''),
        code(f"tutorial('{GRAPH_TUTORIAL}', alto=820)", hidden=True, title="Abrir mini curso visual de Cypher"),
        md(r'''
### Primero: Neo4j, AuraDB, Cypher y Aura Query no son lo mismo

| Nombre | Qué es | Analogía |
|---|---|---|
| **Neo4j** | el motor de base de datos de grafos | PostgreSQL |
| **AuraDB** | el servicio en la nube donde corre Neo4j | Supabase administrando PostgreSQL |
| **Cypher** | el lenguaje para consultar el grafo | SQL |
| **Aura Query** | la pantalla donde escribes Cypher y ves resultados | editor SQL web |

En esta sesión trabajas así:

```text
Tú escribes Cypher → Aura Query → Neo4j busca el patrón → Graph/Table muestran el resultado
```
'''),
        md(r'''
### Consulta 0 — comprobar que Aura responde

Ejecuta en **Aura Query**:

```cypher
RETURN 1 AS conexion
```

- `RETURN`: muestra un resultado.
- `1`: es un valor de prueba.
- `AS conexion`: le pone nombre a la columna.

**Qué debes ver en Table:** una columna `conexion` con el valor `1`.
'''),
        md(r'''
### Consulta 1 — ver nodos

```cypher
MATCH (e:Entidad)
RETURN e
LIMIT 5
```

Línea por línea:

- `MATCH`: busca algo en el grafo.
- `(e:Entidad)`: busca nodos con etiqueta `Entidad` y los llama `e`.
- `RETURN e`: devuelve los nodos completos.
- `LIMIT 5`: muestra solo cinco.

**Qué debes ver:** cinco nodos de tipo `Entidad`. Si cambias a **Graph**, verás círculos sin relaciones entre sí porque todavía no pedimos relaciones.
'''),
        md(r'''
### Consulta 2 — una relación

```cypher
MATCH (e:Entidad)-[pub:PUBLICA]->(p:Proceso)
RETURN e, pub, p
LIMIT 5
```

Se lee literalmente:

> **Busca una Entidad que PUBLICA un Proceso.**

```text
Entidad → PUBLICA → Proceso
```

**Qué debes ver en Graph:** pares Entidad→Proceso unidos por una flecha `PUBLICA`.
'''),
        md(r'''
### Consulta 3 — dos relaciones

```cypher
MATCH (e:Entidad)-[pub:PUBLICA]->(p:Proceso)-[adj:ADJUDICADO_A]->(v:Proveedor)
RETURN e, pub, p, adj, v
LIMIT 5
```

Se lee:

> **Busca una Entidad que PUBLICA un Proceso que fue ADJUDICADO_A un Proveedor.**

```text
Entidad → PUBLICA → Proceso → ADJUDICADO_A → Proveedor
```

**Qué debes ver:** tres tipos de nodo y dos tipos de flecha. Haz clic en cada nodo y revisa sus propiedades.
'''),
        md(r'''
### Graph y Table responden la misma consulta

- **Graph** sirve para entender la estructura: quién se conecta con quién.
- **Table** sirve para leer valores y conteos exactos.
- **Raw** muestra la representación cruda del resultado.

> **Regla:** Graph explica la forma; Table confirma los números.

Si una consulta devuelve solo nombres y conteos, la vista útil suele ser Table. Si devuelve nodos, relaciones o un `camino`, Graph puede dibujarlos.
'''),
        code(r'''
consulta_mi_entidad = f"""MATCH (e:Entidad {{nit:\"{nit_deseado}\"}})-[pub:PUBLICA]->(p:Proceso)-[adj:ADJUDICADO_A]->(v:Proveedor)
RETURN e, pub, p, adj, v
LIMIT 15"""
print("Copia esta consulta en Aura Query:\n")
print(consulta_mi_entidad)
''', hidden=True, title="Preparar una consulta para mi Entidad"),
        md(r'''
### ¿Qué es el grado?

El **grado** de un nodo es, en esta práctica, cuántas relaciones directas llegan a ese nodo.

```text
Proceso 1 → Proveedor X
Proceso 2 → Proveedor X
Proceso 3 → Proveedor X
Proceso 4 → Proveedor X
Proceso 5 → Proveedor X
```

Aquí `Proveedor X` tiene **grado 5** respecto de `ADJUDICADO_A`.

Cypher lo mide así:

```cypher
MATCH (p:Proceso)-[r:ADJUDICADO_A]->(v:Proveedor)
RETURN v.nombre AS proveedor,
       count(r) AS grado
ORDER BY grado DESC
LIMIT 5
```

`count(r)` significa **cuenta las relaciones `r`**. No adivines el grado por el tamaño o la posición del círculo en Aura.
'''),
        md(r'''
### ¿Qué es un hub?

Un **hub**, o **nodo concentrador**, es un nodo que reúne muchas conexiones.

Si un proveedor recibe muchas relaciones `ADJUDICADO_A`, puede actuar como un hub de procesos.

Pero “muy conectado” depende de qué contemos:

```text
CASO A: cinco procesos de una sola Entidad → grado 5, entidades distintas 1
CASO B: cinco procesos de cinco Entidades      → grado 5, entidades distintas 5
```

Los dos tienen grado 5, pero el segundo conecta más **entidades diferentes**. Por eso más adelante contamos también `entidades_conectadas`.
'''),
        code(r'''
grado_rel = hist.groupby("nit_proveedor")["id_proceso"].nunique().rename("grado_adjudicaciones")
entidades_2saltos = hist.groupby("nit_proveedor")["nit_entidad"].nunique().rename("entidades_conectadas")
grado_df = pd.concat([grado_rel, entidades_2saltos], axis=1).reset_index()
grado_df["proveedor"] = grado_df["nit_proveedor"].map(nombres_proveedor)
grado_df = grado_df.sort_values(["entidades_conectadas", "grado_adjudicaciones", "nit_proveedor"], ascending=[False, False, True]).head(10).reset_index(drop=True)
grado_df[["nit_proveedor", "proveedor", "grado_adjudicaciones", "entidades_conectadas"]]
''', hidden=True, title="Ver tabla de grado y entidades conectadas"),
        md(r'''
### Vista gráfica 1 — un proveedor con muchas conexiones

Ahora buscamos **un ejemplo claro** de proveedor compartido por varias entidades:

```cypher
MATCH (v:Proveedor)<-[:ADJUDICADO_A]-(p:Proceso)<-[:PUBLICA]-(e:Entidad)
WITH v,
     count(DISTINCT e) AS entidades,
     count(DISTINCT p) AS procesos
ORDER BY entidades DESC, procesos DESC, v.nit ASC
LIMIT 1
MATCH camino=(e:Entidad)-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v)
RETURN camino
LIMIT 40
```

**Qué hace:** encuentra el proveedor que aparece con más entidades distintas y luego devuelve caminos que llegan a él.

**Qué debes ver:** un proveedor compartido en muchas rutas Entidad→Proceso→Proveedor.

**Qué significa:** varias entidades del extracto tienen procesos adjudicados al mismo proveedor.

**Qué NO significa:** que ese proveedor o esas entidades hayan cometido una irregularidad.
'''),
        md(r'''
### ¿Por qué puedo ver varias islas?

Si ejecutas una consulta global con `LIMIT 20`, Neo4j puede devolver coincidencias que **no están conectadas entre sí dentro de ese resultado**. Aura las dibuja como varias islas o componentes.

```text
isla 1: Entidad→Proceso→Proveedor
isla 2: Entidad→Proceso→Proveedor
```

No son dos bases ni dos grafos distintos: es **una sola base** y **un solo resultado** con grupos desconectados. Para aprender, primero usamos consultas centradas en una entidad o proveedor concreto.
'''),
        code(r'''
nit_literal = str(nit_deseado).replace('"', '\\"')
consulta_compartida = f"""MATCH (ancla:Entidad {{nit:\"{nit_literal}\"}})-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v:Proveedor)
WITH ancla, v, count(*) AS procesos_ancla
ORDER BY procesos_ancla DESC, v.nit ASC
LIMIT 1
MATCH camino=(ancla)-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v)<-[:ADJUDICADO_A]-(:Proceso)<-[:PUBLICA]-(otra:Entidad)
WHERE otra.nit <> ancla.nit
RETURN camino
LIMIT 20"""
print("Copia esta consulta en Aura Query:\n")
print(consulta_compartida)
''', hidden=True, title="Preparar la consulta de proveedor compartido"),
        md(r'''
### Vista gráfica 2 — dos entidades conectadas por un proveedor compartido

La consulta preparada arriba busca este camino:

```text
Entidad ancla → Proceso → Proveedor ← Proceso ← otra Entidad
```

**Qué debes hacer en Aura:**

1. ejecuta la consulta preparada;
2. abre **Graph**;
3. elige un camino y síguelo nodo por nodo;
4. haz clic en las dos Entidades y confirma que sus NIT son diferentes;
5. confirma que ambas rutas pasan por el **mismo Proveedor**.

**Qué significa:** esas dos entidades comparten un proveedor en registros adjudicados del extracto.

**Qué NO significa:** coordinación, colusión, favorecimiento, causalidad o irregularidad.
'''),
    ]


def move_contract_and_insert_lab(cells):
    h = find(cells, "## 4. Contrato de resultado: primero pandas")
    block = cells[h:h + 4]
    if len(block) != 4 or "# Ambas métricas" not in s(block[1]):
        raise ValueError("Cambió la estructura del contrato pandas S06")
    del cells[h:h + 4]

    i = find(cells, "## 5. Tutorial visual — AuraDB")
    put(cells[i], s(cells[i]).replace("## 5. Tutorial visual — AuraDB", "## 4. AuraDB — conectar el motor real"))
    i = find(cells, "## 6. Identidad y carga idempotente")
    put(cells[i], s(cells[i]).replace("## 6. Identidad y carga idempotente", "## 4.1 Cargar nodos y relaciones sin duplicarlos"))

    d = find(cells, "## 7. La consulta que justifica Neo4j")
    put(block[0], s(block[0]).replace("## 4. Contrato de resultado: primero pandas", "## 6. Profundización opcional — ¿esta conectividad es alta o baja?") + r'''

Hasta aquí ya aprendiste lo esencial de Neo4j/Cypher. Esta sección añade una comparación estadística; **no es necesaria para entender qué es un grafo**.
''')
    cells[d:d] = beginner_lab() + block

    i = find(cells, "## 7. La consulta que justifica Neo4j")
    put(cells[i], s(cells[i]).replace("## 7. La consulta que justifica Neo4j", "## 7. Verificación final — Neo4j y pandas responden la misma pregunta"))


def simplify_operational_choices(cells):
    for cell in cells:
        body = s(cell)
        if 'modo = input("Enter = Aura; escribe RESPALDO' in body:
            body = body.replace(
                'modo = input("Enter = Aura; escribe RESPALDO si no puedes usar el servicio: ").strip().upper()\nif modo not in ["", "RESPALDO"]:\n    raise ValueError("Usa Enter o RESPALDO.")\nmodo_neo4j = modo != "RESPALDO"',
                'MODO_EJECUCION = "Aura"  #@param ["Aura", "RESPALDO"]\nmodo = "" if MODO_EJECUCION == "Aura" else "RESPALDO"\nmodo_neo4j = MODO_EJECUCION == "Aura"'
            )
            put(cell, body)
            hide(cell, "Elegir Aura o respaldo y conectar")

    for cell in cells:
        body = s(cell)
        if 'sel = int(input("Número de proveedor:' in body:
            body = body.replace('sel = int(input("Número de proveedor: ").strip())', 'sel = 1  # ejemplo guiado: primera opción de la lista')
            body = body.replace('if not 1 <= sel <= len(opciones):\n    raise ValueError("Número fuera de rango")', 'if not 1 <= sel <= len(opciones):\n    sel = 1')
            body = body.replace('proveedor_elegido = opciones.iloc[sel-1]', 'proveedor_elegido = opciones.iloc[sel-1]\nprint("✅ Usaremos como ejemplo:", proveedor_elegido["proveedor"], "| entidades=", int(proveedor_elegido["entidades_conectadas"]))')
            put(cell, body)
            hide(cell, "Elegir automáticamente un proveedor de ejemplo")

    for cell in cells:
        body = s(cell)
        if body.startswith('OPERADOR_EXCLUSION ='):
            body = body.replace('OPERADOR_EXCLUSION = "____"', 'OPERADOR_EXCLUSION = "<>"')
            body = re.sub(r'if OPERADOR_EXCLUSION != "<>":\n\s+raise ValueError\([^\n]+\)\n', '', body)
            body = re.sub(
                r'razon_exploracion = input\([^\n]+\)\.strip\(\)\nif len\(razon_exploracion\) < 25:\n\s+raise ValueError\([^\n]+\)',
                'razon_exploracion = (f"Exploramos {proveedor_elegido[\'proveedor\']} porque conecta "\n                      f"{int(proveedor_elegido[\'entidades_conectadas\'])} entidades en el extracto. "\n                      "Este dato describe conectividad, no irregularidad.")\nprint("Ejemplo de respuesta:", razon_exploracion)',
                body,
                flags=re.S,
            )
            put(cell, body)
            hide(cell, "Contar otras entidades sin adivinar sintaxis")

    i = find(cells, "# Escribe tu consulta entre las comillas triples")
    put(cells[i], r'''#@title Ejecutar la consulta guiada para el par Entidad–Proveedor { display-mode: "form" }
consulta_propia = ("MATCH (e:Entidad {nit:$ancla})-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor {nit:$proveedor})\n"
                    "RETURN count(DISTINCT p) AS procesos")
print("Consulta guiada:\n", consulta_propia)
if modo_neo4j:
    procesos_propios = int(driver.execute_query(
        consulta_propia,
        ancla=nit_deseado,
        proveedor=str(proveedor_elegido["nit_proveedor"])
    ).records[0]["procesos"])
else:
    procesos_propios = int(vecindario_df.loc[vecindario_df["nit_entidad"].eq(nit_deseado), "proceso"].nunique())
    print("En RESPALDO verificamos el número con pandas; ejecuta el Cypher en Aura cuando tengas conexión.")
esperados_propios = int(proveedor_elegido["procesos_con_entidad"])
assert procesos_propios == esperados_propios
print("Procesos para este par Entidad–Proveedor:", procesos_propios)
''')
    hide(cells[i], "Ejecutar consulta Cypher ya preparada")

    i = find(cells, 'autor = input("Autor o alias')
    put(cells[i], r'''#@title Datos mínimos de la ficha { display-mode: "form" }
from pathlib import Path
from datetime import datetime, timezone
AUTOR = "estudiante"  #@param {type:"string"}
autor = AUTOR.strip() or "estudiante"
decision_modelo = "Proceso es nodo porque tiene identidad y propiedades propias y participa en el camino Entidad → Proceso → Proveedor."
limite_estudiante = "Las conexiones observadas no demuestran irregularidad; faltan contexto competitivo, temporal y evidencia adicional del proceso."
alternativa_modelo = "Relación directa Entidad → Proveedor con el proceso guardado como propiedad."
razon_alternativa = "La descartamos porque perderíamos al Proceso como nodo consultable y reutilizable en S7."
fecha_ejecucion = datetime.now(timezone.utc).isoformat()
print("✅ Respuestas modelo cargadas. Puedes explicarlas con tus palabras en clase.")
print("Ejemplo de respuesta — modelo:", decision_modelo)
print("Ejemplo de respuesta — límite:", limite_estudiante)
''')
    hide(cells[i], "Completar autor; respuestas modelo incluidas")


def hide_python_infrastructure(cells):
    tokens = [
        "groupby(",
        "to_dict(\"records\")",
        "pd.concat(",
        "import urllib.request",
        'hist = datos[datos["tipo_registro"]',
        'prov_ancla = hist_ancla.groupby',
        'cols = [',
        'para_carga = datos[cols].copy()',
        'pd.concat([prov_ancla',
        'str(nit_deseado).replace',
    ]
    for cell in cells:
        if cell.get("cell_type") != "code":
            continue
        body = s(cell)
        if any(token in body for token in tokens):
            hide(cell, "Infraestructura automática — ejecutar, no memorizar")


def enhance_cells(cells):
    if any(MARKER in s(c) for c in cells):
        return cells
    simplify_intro(cells)
    simplify_anchor(cells)
    simplify_concepts(cells)
    improve_graph_properties(cells)
    move_contract_and_insert_lab(cells)
    improve_contract(cells)
    simplify_operational_choices(cells)
    hide_python_infrastructure(cells)
    return cells


def enhance_checklist(cells):
    """Restaura el checklist beginner desde su plantilla canónica."""
    template = ROOT / "assets" / "tutoriales" / "templates" / "s06-laboratorio-guiado.html"
    target = ROOT / "assets" / "tutoriales" / "s06-laboratorio-guiado.html"
    if not template.is_file():
        raise FileNotFoundError(template)
    target.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
