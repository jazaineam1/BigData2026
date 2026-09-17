#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rediseño pedagógico S06 para principiantes en Neo4j/Cypher.

Objetivo editorial:
- Python de infraestructura oculto; Cypher y su interpretación visibles.
- Secuencia: nodo -> relación -> camino -> grado -> hub -> proveedor compartido.
- Sin retos de texto libre sin ejemplo ni placeholders que parezcan errores.
- H2-R queda como profundización posterior a comprender el grafo.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH_TUTORIAL = "https://jazaineam1.github.io/BigData2026/assets/tutoriales/neo4j-graph-lab-s06.html"
MARKER = "S06-NOVATOS-V3"


def s(cell):
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def put(cell, text):
    cell["source"] = text.strip("\n").splitlines(keepends=True)


def find(cells, needle, starts=False):
    hits = [i for i, cell in enumerate(cells) if (s(cell).startswith(needle) if starts else needle in s(cell))]
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


def beginner_intro(cells):
    i = find(cells, "# Sesión 6 — De la fila priorizada al contexto relacional con Neo4j")
    put(cells[i], f'''
# Sesión 6 — Entender relaciones con Neo4j y Cypher

<!-- {MARKER} -->
## Universidad Central
> ### Facultad de Ingeniería y Ciencias Básicas
> ### Maestría en Analítica de Datos — BIG DATA (64491093)

**Caso conductor:** Compras Claras

### La pregunta de hoy, sin rodeos

El proceso priorizado en S5 pertenece a una entidad. En el extracto de S6 ese proceso candidato **no tiene un proveedor adjudicado observado**, así que no vamos a inventarlo. La pregunta real es:

> **¿Qué proveedores aparecen en el historial adjudicado de la entidad del proceso y cuáles de esos proveedores también aparecen conectados con otras entidades?**

Seguiremos este camino:

`Entidad → Proceso histórico → Proveedor ← Proceso histórico ← otra Entidad`

### Qué vas a aprender

1. qué es un **nodo**, una **relación** y un **camino**;
2. qué son **Neo4j**, **AuraDB**, **Aura Query** y **Cypher**;
3. cómo leer seis consultas Cypher muy pequeñas;
4. qué significa **grado** y qué significa **hub (nodo concentrador)**;
5. cómo ver un proveedor compartido entre entidades en **Graph**;
6. qué demuestra ese grafo y qué **no** demuestra.

> **Importante:** esta no es una clase de Python. Las celdas Python preparan datos y credenciales; no debes memorizarlas. El lenguaje que debes aprender hoy es **Cypher**.

### Producto observable

Al final tendrás una ficha que resume el proveedor explorado, cuántas entidades conecta, el camino observado y el límite interpretativo, además del archivo `s06_contexto_procesos.jsonl` que alimentará S7.
''')

    i = find(cells, "## Mapa de la sesión")
    put(cells[i], '''
## Mapa de la sesión

| Paso | Qué aprendes | Qué haces |
|---|---|---|
| 1 | cuál es la entidad de trabajo | cargas el ejemplo del curso o tu JSON de S5 |
| 2 | nodo, relación y camino | lees un ejemplo pequeño |
| 3 | Neo4j / AuraDB / Cypher | ubicas cada herramienta |
| 4 | Cypher básico | ejecutas 6 consultas guiadas |
| 5 | grado y hub | cuentas conexiones y ves el nodo concentrador |
| 6 | proveedor compartido | recorres el camino entre dos entidades |
| 7 | verificación | comparas Graph, Table y pandas |
| 8 | profundización | interpretas H2-R sin confundirla con riesgo |
| 9 | entrega | descargas ficha + JSONL |

### Cómo usar las celdas

- 🧠 **ENTIENDE:** lee el ejemplo y explícalo con tus palabras.
- ▶️ **EJECUTA:** corre la celda; no debes escribirla de memoria.
- ✏️ **MODIFICA:** cambia solo el valor indicado; siempre verás un ejemplo válido primero.
- 🌐 **AURA:** copia Cypher en Aura Query y mira Graph/Table.
''')


def anchor(cells):
    i = find(cells, "## 1. Recuperar el proceso que Laura abrió en S5")
    put(cells[i], '''
---
## 1. Elegir el punto de partida

S6 puede comenzar de dos formas:

### Opción A — ejemplo del curso · recomendado para la primera vez
No subes nada. El cuaderno usa un proceso versionado para que todos puedan seguir el tutorial.

### Opción B — mi archivo de S5
Si conservaste `s05_ancla_s06.json`, puedes cargarlo.

### ¿Qué es ese JSON?
Es un archivo pequeño que guarda **qué proceso elegiste** y **qué entidad lo publicó**. Por ejemplo:

```json
{
  "id_proceso": "CO1.REQ.2622868",
  "entidad": "FUERZA AEROESPACIAL COLOMBIANA",
  "nit_entidad": "899999102"
}
```

- `id_proceso`: identifica el proceso elegido.
- `entidad`: nombre de quien lo publicó.
- `nit_entidad`: identificador que usaremos para buscar su historial en Neo4j.

> Si es tu primera vez, deja **USAR_MI_ANCLA_S5 = False** y continúa. No tienes que entender el Python de la siguiente celda.
''')

    i = find(cells, "# El cuaderno trae el ancla pedagógica versionada", starts=True)
    put(cells[i], r'''#@title Elegir ejemplo del curso o mi JSON de S5 { display-mode: "form" }
from pathlib import Path
import json
USAR_MI_ANCLA_S5 = False  #@param {type:"boolean"}
archivo_s5 = Path("s05_ancla_s06.json")
if USAR_MI_ANCLA_S5 and not archivo_s5.is_file():
    try:
        from google.colab import files
        print("Selecciona s05_ancla_s06.json")
        subidos = files.upload()
        if "s05_ancla_s06.json" not in subidos:
            raise ValueError("Debes seleccionar s05_ancla_s06.json o desactivar USAR_MI_ANCLA_S5.")
        archivo_s5.write_bytes(subidos["s05_ancla_s06.json"])
    except ImportError:
        raise FileNotFoundError("Copia s05_ancla_s06.json junto al cuaderno o usa el ejemplo del curso.")
if USAR_MI_ANCLA_S5:
    ancla_original = json.loads(archivo_s5.read_text(encoding="utf-8-sig"))
    faltantes = [k for k in ["id_proceso", "entidad", "nit_entidad"] if not str(ancla_original.get(k, "")).strip()]
    if faltantes:
        raise ValueError(f"El JSON no contiene estos campos obligatorios: {faltantes}")
    origen_ancla = "archivo propio S5"
else:
    ancla_original = dict(manifest["ancla_pedagogica"])
    origen_ancla = "ejemplo versionado del curso"
print("✅ Punto de partida listo")
print("Proceso:", ancla_original["id_proceso"])
print("Entidad:", ancla_original["entidad"])
print("NIT:", ancla_original["nit_entidad"])
print("Origen:", origen_ancla)
''')


def concepts(cells):
    i = find(cells, "Antes de escribir Cypher, cinco palabras y nada más")
    put(cells[i], '''
## 3. Antes de Cypher: tres ideas y tres palabras auxiliares

### 1. Nodo = una cosa que queremos representar
Ejemplos de hoy: `Entidad`, `Proceso`, `Proveedor`.

### 2. Relación = una flecha que une dos nodos

```text
Entidad ──PUBLICA──> Proceso ──ADJUDICADO_A──> Proveedor
```

- `PUBLICA`: la Entidad publica el Proceso.
- `ADJUDICADO_A`: el Proceso fue adjudicado al Proveedor.

### 3. Camino = varios nodos y relaciones seguidos

```text
Entidad → Proceso → Proveedor ← Proceso ← otra Entidad
```

Ese camino responde la pregunta de hoy: **¿qué otra entidad llega al mismo proveedor?**

### Tres palabras auxiliares

| Palabra | Significa | Ejemplo |
|---|---|---|
| **Label** | tipo de nodo | `:Entidad` |
| **Propiedad** | dato guardado en un nodo o relación | `nit`, `nombre`, `precio_base` |
| **Patrón** | forma que quieres encontrar | `(e)-[:PUBLICA]->(p)` |

### Cómo leer una pieza de Cypher

```cypher
(e:Entidad)-[:PUBLICA]->(p:Proceso)
```

Se lee literalmente: **“una Entidad `e` publica un Proceso `p`”**.

> No memorices símbolos aislados. Lee siempre la forma completa como una oración.
''')

    i = find(cells, 'RELACION_PROCESO_PROVEEDOR = "ADJUDICADO_A"', starts=True)
    put(cells[i], '''# Ejemplo guiado: la respuesta ya está escrita para que observes la sintaxis.
RELACION_PROCESO_PROVEEDOR = "ADJUDICADO_A"
patron_estudiante = f"(p:Proceso)-[:{RELACION_PROCESO_PROVEEDOR}]->(v:Proveedor)"
print("✅ Patrón:", patron_estudiante)
print("Se lee: el Proceso p fue ADJUDICADO_A el Proveedor v.")
''')

    i = find(cells, "### La alternativa que descartamos")
    put(cells[i], s(cells[i]) + '''

### Una decisión de modelado, explicada sin reto

Usamos `Proceso` como nodo porque tiene **identidad propia**, **propiedades propias** y participa en las relaciones entre Entidad y Proveedor.

Una respuesta modelo válida es:

> “Proceso es un nodo porque tiene un identificador y propiedades propias y necesitamos recorrer el camino Entidad → Proceso → Proveedor.”

Más adelante la ficha usará esta explicación como valor por defecto; no tendrás que adivinar qué escribir.
''')


def connection_mode(cells):
    for cell in cells:
        text = s(cell)
        if 'modo = input("Enter = Aura; escribe RESPALDO' in text:
            old = 'modo = input("Enter = Aura; escribe RESPALDO si no puedes usar el servicio: ").strip().upper()\nif modo not in ["", "RESPALDO"]:\n    raise ValueError("Usa Enter o RESPALDO.")\nmodo_neo4j = modo != "RESPALDO"'
            new = 'RUTA_EJECUCION = "AURA"  #@param ["AURA", "RESPALDO"]\nmodo = "" if RUTA_EJECUCION == "AURA" else "RESPALDO"\nmodo_neo4j = RUTA_EJECUCION == "AURA"'
            if old not in text:
                raise ValueError("Cambió el selector Aura/RESPALDO")
            put(cell, text.replace(old, new))
            return
    raise ValueError("No se encontró selector Aura/RESPALDO")


def contract(cells):
    i = find(cells, "# Ambas métricas usan NIT", starts=True)
    put(cells[i], r'''# Infraestructura de verificación: no necesitas memorizar este pandas.
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
proveedor_h2r = resultado_completo_pd.iloc[0].copy()
maximo_h2r = int(proveedor_h2r["entidades_conectadas"])
if uso_respaldo_s06:
    desenlace_h2r_pd = "ejemplo descriptivo; no es una conclusión individual de S5"
elif maximo_h2r > MEDIANA_H2R:
    desenlace_h2r_pd = "por encima de la mediana de referencia"
else:
    desenlace_h2r_pd = "igual o por debajo de la mediana de referencia"
print("Entidades de referencia:", len(maximos_candidatas))
print("Mediana de referencia:", MEDIANA_H2R)
print("Proveedor con mayor conectividad institucional:", proveedor_h2r["proveedor"])
print("Entidades conectadas:", maximo_h2r)
print("Lectura H2-R:", desenlace_h2r_pd)
esperado_pd
''')


def graph_props(cells):
    i = find(cells, "cols = [", starts=True)
    text = s(cells[i])
    if '"valor_adjudicado"' not in text.split("rows =", 1)[0]:
        text = text.replace('"nombre_proceso", "descripcion", "precio_base", "modalidad", "proveedor",', '"nombre_proceso", "descripcion", "precio_base", "valor_adjudicado", "modalidad", "proveedor",')
    text = text.replace("    p.valor = fila.precio_base,", "    p.precio_base = fila.precio_base,")
    text = text.replace("MERGE (p)-[:ADJUDICADO_A]->(v)", "MERGE (p)-[a:ADJUDICADO_A]->(v)\nSET a.valor_adjudicado = fila.valor_adjudicado")
    put(cells[i], text)
    for cell in cells:
        if "p.valor AS precio_base" in s(cell):
            put(cell, s(cell).replace("p.valor AS precio_base", "p.precio_base AS precio_base").replace("ORDER BY entidad, valor DESC", "ORDER BY entidad, precio_base DESC"))


def graphlab():
    return [
        md(f'''
---
## 5. Mini curso de Cypher en Aura Query

<!-- {MARKER} -->

Aquí empieza el aprendizaje central de la sesión. **No hay “WOW” ni retos ocultos.** Cada consulta responde una sola pregunta y dice exactamente qué debes ver.

**Tutorial visual complementario:** [Mini curso visual de Cypher ↗]({GRAPH_TUTORIAL})
'''),
        code(f"tutorial('{GRAPH_TUTORIAL}', alto=820)", hidden=True, title="Abrir mini curso visual de Cypher"),
        md('''
### Antes de consultar: cuatro nombres que no debes confundir

| Nombre | Qué es |
|---|---|
| **Neo4j** | el motor de base de datos de grafos |
| **AuraDB** | el servicio en la nube donde corre Neo4j |
| **Aura Query** | la pantalla donde escribes y ejecutas consultas |
| **Cypher** | el lenguaje con el que consultas Neo4j |

Piensa en: **PostgreSQL : SQL :: Neo4j : Cypher**.
'''),
        md('''
### Consulta 0 — comprobar que Aura responde

Copia en **Aura → Query**:

```cypher
RETURN 1 AS conexion
```

**Qué hace:** devuelve un valor de prueba.  
**Qué debes ver en Table:** una columna `conexion` con valor `1`.  
**Si funciona:** Aura y tu instancia están listas.
'''),
        md('''
### Consulta 1 — ver nodos Entidad

```cypher
MATCH (e:Entidad)
RETURN e
LIMIT 5
```

- `MATCH`: busca una forma en el grafo.
- `(e:Entidad)`: busca nodos con label `Entidad` y los llama `e`.
- `RETURN e`: devuelve los nodos completos.
- `LIMIT 5`: muestra solo cinco.

**Qué debes ver en Graph:** hasta cinco círculos de tipo `Entidad`. Haz clic en uno y busca `nit` y `nombre`.
'''),
        md('''
### Consulta 2 — una relación

```cypher
MATCH (e:Entidad)-[pub:PUBLICA]->(p:Proceso)
RETURN e, pub, p
LIMIT 5
```

Se lee: **“una Entidad publica un Proceso”**.

**Qué debes ver en Graph:** `Entidad ──PUBLICA──> Proceso`.  
**Qué debes revisar:** haz clic en la flecha `PUBLICA` y luego en el nodo `Proceso`.
'''),
        md('''
### Consulta 3 — dos relaciones

```cypher
MATCH (e:Entidad)-[pub:PUBLICA]->(p:Proceso)-[adj:ADJUDICADO_A]->(v:Proveedor)
RETURN e, pub, p, adj, v
LIMIT 10
```

Se lee: **“una Entidad publica un Proceso y ese Proceso fue adjudicado a un Proveedor”**.

**Qué debes ver:** varias cadenas `Entidad → Proceso → Proveedor`. Si aparecen varias “islas”, no son varias bases: son componentes distintos del mismo resultado.
'''),
        md('''
### Consulta 4 — qué es el grado

**Grado** significa cuántas relaciones directas tiene un nodo para la relación que estamos contando.

```text
Proceso 1 ─┐
Proceso 2 ─┤
Proceso 3 ─┼──> Proveedor X
Proceso 4 ─┤
Proceso 5 ─┘
```

Aquí el proveedor tiene **grado 5** respecto de `ADJUDICADO_A`.

```cypher
MATCH (p:Proceso)-[r:ADJUDICADO_A]->(v:Proveedor)
RETURN v.nit AS nit_proveedor,
       v.nombre AS proveedor,
       count(r) AS grado
ORDER BY grado DESC
LIMIT 10
```

> **Table mide; Graph explica.** El número exacto sale de `count(r)`, no del tamaño o la posición del círculo.
'''),
        md('''
### Consulta 5 — qué es un hub

Un **hub**, o **nodo concentrador**, es un nodo con muchas conexiones respecto de una métrica.

No significa “sospechoso” ni “anómalo”. Solo significa **muy conectado**.

```cypher
MATCH (p:Proceso)-[r:ADJUDICADO_A]->(v:Proveedor)
WITH v, count(r) AS grado
ORDER BY grado DESC, v.nit ASC
LIMIT 1
MATCH (p:Proceso)-[r:ADJUDICADO_A]->(v)
RETURN v, r, p
LIMIT 40
```

**Qué debes ver:** un Proveedor y varios Procesos conectados alrededor. Haz clic en el Proveedor y confirma `nit` y `nombre`.
'''),
        md('''
### Hub por procesos ≠ proveedor compartido por muchas entidades

```text
Proveedor X: 5 procesos, todos de Entidad A  →  grado 5, entidades 1
Proveedor Y: 5 procesos, de A/B/C/D/E        →  grado 5, entidades 5
```

Por eso también contamos entidades distintas:

```cypher
MATCH (e:Entidad)-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v:Proveedor)
RETURN v.nombre AS proveedor,
       count(DISTINCT e) AS entidades_conectadas
ORDER BY entidades_conectadas DESC
LIMIT 10
```

`DISTINCT` evita contar varias veces la misma entidad.
'''),
        code(r'''# Infraestructura oculta: prepara la consulta personalizada con el NIT de trabajo.
nit_literal = str(nit_deseado).replace('"', '\\"')
consulta_camino_compartido = f''' + "'''" + r'''
MATCH camino=(ancla:Entidad {{nit:"{nit_literal}"}})-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v:Proveedor)
             <-[:ADJUDICADO_A]-(:Proceso)<-[:PUBLICA]-(otra:Entidad)
WHERE otra.nit <> ancla.nit
RETURN camino
LIMIT 30
''' + "'''" + r'''
print("Copia esta consulta en Aura Query:\n")
print(consulta_camino_compartido)
''', hidden=True, title="Preparar consulta 6 con mi entidad"),
        md('''
### Consulta 6 — responder la pregunta profesional

La celda anterior imprimió una consulta con el NIT de tu entidad. Cópiala en Aura Query.

```text
Entidad ancla → Proceso → Proveedor ← Proceso ← otra Entidad
```

**Qué debes comprobar, literalmente:**

1. el nodo de la izquierda es tu Entidad;
2. ambos extremos tienen NIT diferentes;
3. los dos caminos llegan al **mismo Proveedor**;
4. cada lado pasa por un nodo `Proceso`;
5. en Graph puedes hacer clic en cada nodo y verificar propiedades.

**Sí demuestra:** esos registros comparten un proveedor.  
**No demuestra:** coordinación, colusión, favorecimiento, causalidad o irregularidad.
'''),
    ]


def guided_interactions(cells):
    for cell in cells:
        text = s(cell)
        if "if resultado_contexto.empty:" in text and 'input("Número de proveedor:' in text:
            head, tail = text.split("if modo_neo4j:", 1)
            replacement = r'''if resultado_contexto.empty:
    raise ValueError("No hay proveedores disponibles en el extracto.")
opciones = resultado_contexto.head(5).reset_index(drop=True)
print("Cinco proveedores de ejemplo, ordenados por conectividad:")
for i, row in opciones.iterrows():
    print(f"{i+1}. {row['proveedor']} | entidades={int(row['entidades_conectadas'])}")
proveedor_elegido = opciones.iloc[0]
print("\n✅ Proveedor explorado automáticamente:", proveedor_elegido["proveedor"])
print("Entidades conectadas:", int(proveedor_elegido["entidades_conectadas"]))

if modo_neo4j:
'''
            put(cell, replacement + tail)
            break

    for cell in cells:
        text = s(cell)
        if 'OPERADOR_EXCLUSION = "____"' in text:
            text = text.replace('OPERADOR_EXCLUSION = "____"', 'OPERADOR_EXCLUSION = "<>"  # significa "diferente de"')
            text = text.replace('if OPERADOR_EXCLUSION != "<>":\n    raise ValueError("En Cypher, distinto se escribe <>.")\n', '')
            old = 'razon_exploracion = input("Con tus números: ¿por qué explorar este proveedor y cuál de la lista descartaste?: ").strip()\nif len(razon_exploracion) < 25:\n    raise ValueError("Nombra tu elección, otra opción y un dato de tu salida.")'
            new = 'razon_exploracion = f"Exploro {proveedor_elegido[\'proveedor\']} porque conecta {int(proveedor_elegido[\'entidades_conectadas\'])} entidades en el extracto. Esta conectividad describe estructura; no demuestra irregularidad."\nprint("Ejemplo de interpretación:", razon_exploracion)'
            if old in text:
                text = text.replace(old, new)
            put(cell, text)
            break

    for cell in cells:
        if s(cell).startswith("# Escribe tu consulta entre las comillas triples"):
            put(cell, r'''# Consulta modelo ya completa. Lee cada línea; no necesitas escribirla desde cero.
consulta_propia = ''' + "'''" + r'''
MATCH (e:Entidad {nit:$ancla})-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor {nit:$proveedor})
RETURN count(DISTINCT p) AS procesos
''' + "'''" + r'''
print("✅ Consulta guiada lista. Pregunta: ¿cuántos procesos de la entidad fueron adjudicados al proveedor explorado?")
print(consulta_propia)
''')
            break

    for cell in cells:
        text = s(cell)
        if 'autor = input("Autor o alias de equipo' in text:
            old = '''autor = input("Autor o alias de equipo (guardar solo en repositorio privado): ").strip()
decision_modelo = input("Justifica por qué Proceso debe ser nodo para tu pregunta: ").strip()
if not autor or len(decision_modelo) < 20:
    raise ValueError("Registra autor y justificación de modelado.")
fecha_ejecucion = datetime.now(timezone.utc).isoformat()
limite_estudiante = input("Límite concreto y dato faltante: ").strip()
alternativa_modelo = input("Alternativa de modelado descartada: ").strip()
razon_alternativa = input("¿Por qué la descartaste para esta pregunta?: ").strip()

if len(limite_estudiante) < 25:
    raise ValueError("Nombra la conclusión que no puedes sostener y el dato que falta.")
if len(alternativa_modelo) < 5 or len(razon_alternativa) < 15:
    raise ValueError("Nombra una alternativa real y explica por qué no sirve igual de bien para esta pregunta.")'''
            new = '''AUTOR_ALIAS = "equipo-01"  #@param {type:"string"}
autor = AUTOR_ALIAS.strip() or "equipo-01"
decision_modelo = "Proceso es un nodo porque tiene identidad y propiedades propias y necesitamos recorrer Entidad → Proceso → Proveedor."
fecha_ejecucion = datetime.now(timezone.utc).isoformat()
limite_estudiante = "El grafo demuestra relaciones contractuales registradas, pero no demuestra irregularidad; faltan datos sobre competencia, contexto y comportamiento fuera del extracto."
alternativa_modelo = "Modelar Entidad y Proveedor como un único nodo Organización con roles."
razon_alternativa = "Es una alternativa válida, pero se mantiene el modelo por roles separados para que un principiante lea con claridad quién publica y quién recibe la adjudicación."
print("✅ La ficha usa respuestas modelo explícitas. Cambia solo AUTOR_ALIAS si lo necesitas.")'''
            if old not in text:
                raise ValueError("Cambió bloque de ficha final")
            put(cell, text.replace(old, new))
            break


def move_contract_after_graph(cells):
    h = find(cells, "## 4. Contrato de resultado: primero pandas")
    block = cells[h:h+4]
    if len(block) != 4 or "# Infraestructura de verificación" not in s(block[1]):
        raise ValueError("Cambió estructura del contrato pandas S06")
    del cells[h:h+4]

    i = find(cells, "## 5. Tutorial visual — AuraDB")
    put(cells[i], s(cells[i]).replace("## 5. Tutorial visual — AuraDB", "## 4. AuraDB — abrir el motor real"))
    i = find(cells, "## 6. Identidad y carga idempotente")
    put(cells[i], s(cells[i]).replace("## 6. Identidad y carga idempotente", "## 4.1 Cargar el grafo sin duplicar"))

    d = find(cells, "## 7. La consulta que justifica Neo4j")
    put(block[0], '''
## 6. Profundización — comparar conectividad con una referencia (H2-R)

Ya sabes leer el grafo. Ahora hacemos una pregunta adicional: **¿la cantidad de entidades conectadas al proveedor principal es alta comparada con otras entidades candidatas de S5?**

Esta sección usa pandas como verificación. No necesitas memorizar su código.
''')
    cells[d:d] = graphlab() + block


def delivery(cells):
    i = find(cells, "### Comprueba tu entrega")
    put(cells[i], s(cells[i]) + '''

### Entrega sin adivinanzas

La ficha ya incluye respuestas modelo para decisión de modelado y límite interpretativo. Tú solo debes:

1. cambiar `AUTOR_ALIAS` por tu alias/equipo;
2. ejecutar la celda de exportación;
3. descargar `hito_s06_ficha_relacional.md` y `s06_contexto_procesos.jsonl`;
4. subir ambos a `hitos/s06/` en tu repositorio privado;
5. entregar la URL exacta del commit.
''')


def enhance_cells(cells):
    if any(MARKER in s(cell) for cell in cells):
        return cells
    beginner_intro(cells)
    anchor(cells)
    concepts(cells)
    connection_mode(cells)
    contract(cells)
    graph_props(cells)
    guided_interactions(cells)
    move_contract_after_graph(cells)
    delivery(cells)
    return cells


def enhance_checklist(cells):
    return None
