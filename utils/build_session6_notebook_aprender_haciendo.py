#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera S6-ALT: la misma sesión de Neo4j, con ciclos de aprender-haciendo más cortos.

Alternativa de comparación a `Cuadernos/6_Neo4j_Contexto_Relacional.ipynb` — NO lo
reemplaza. Reutiliza los mismos diagramas SVG y helpers de preguntas del generador
original. Diferencias deliberadas de esta versión, por feedback directo del docente:

- No pide ningún archivo de una sesión anterior (los estudiantes que la usan de
  forma independiente no lo tienen): siempre trabaja sobre la ancla pedagógica
  compartida, sin ningún `input()` para eso.
- Ningún concepto nuevo queda sin una acción real inmediatamente después
  (autoevaluación, hueco validado, o ejecución) — pero esas acciones son siempre
  ejercicios verificables (como el resto del curso), nunca una predicción libre
  con `input()`.
- Como todos usan la misma ancla, el desenlace de H2-R no se etiqueta como
  "no evaluable" solo por ser la ancla compartida: se evalúa igual que en el
  original, y el hito declara honestamente que es el caso compartido, no una
  elección personal de S5.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.make_notebook import code, md, save, validate
from utils.build_session6_notebook import (
    hidden, question_cell, svg, INTERACTIVITY,
    WEB, RAW, DATA, MANIFEST, TUTORIAL, LABORATORIO,
)

OUTPUT = "Cuadernos/6_Neo4j_Contexto_Relacional_AprenderHaciendo.ipynb"
COLAB = "https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/6_Neo4j_Contexto_Relacional_AprenderHaciendo.ipynb"


def build_cells():
    return [
        md(f'''<a href="{COLAB}" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Abrir S6-ALT en Colab"></a>

**Acceso público:** [página del curso]({WEB}/) · **Laboratorio guiado (checklist paso a paso):** [ábrelo en otra pestaña ↗]({LABORATORIO})

> **Versión alterna de S6**, con el mismo contenido de fondo que `6_Neo4j_Contexto_Relacional.ipynb` pero en ciclos más cortos de concepto → acción, y trabajando siempre sobre un **caso compartido** (no requiere el archivo de S5). Es una comparación pedagógica, no la versión oficial.'''),
        hidden(code(INTERACTIVITY), "Preparar interactividad"),
        md('''
# Sesión 6 (alterna) — De la fila priorizada al contexto relacional con Neo4j

## Universidad Central
> ### Facultad de Ingeniería y Ciencias Básicas
> ### Maestría en Analítica de Datos — BIG DATA (64491093)

**Caso conductor:** Compras Claras
**Pregunta profesional:** **Laura ya sabe qué proceso revisar primero. Antes de asignarlo a un auditor, ¿qué relaciones alrededor de ese proceso necesita ver para comprender su contexto?**

**Respuesta corta y herramienta:** Laura necesita seguir una cadena de conexiones —entidad → proceso → proveedor → otro proceso → otra entidad— sin perder el hilo en ningún salto. Eso es una pregunta sobre relaciones que se conectan entre sí, y la herramienta que la responde es una **base de datos de grafos: Neo4j**.

### Producto observable

Al terminar tendrás una **ficha relacional de revisión** con:

1. el proceso de trabajo de esta sesión y su contexto de prensa;
2. procesos históricos adjudicados de su entidad;
3. proveedores y otras entidades conectadas cuando el dato lo sostenga;
4. el contraste de H2-R, la hipótesis relacional de hoy (pandas ↔ Neo4j);
5. una decisión de modelado y una alternativa descartada;
6. un límite concreto;
7. `s06_contexto_procesos.jsonl`, entrada de la siguiente sesión.

**OJO — diferencia con la versión original.** Esta versión trabaja siempre sobre la misma entidad (el caso más rico del extracto), no sobre el proceso que elegiste en S5. Ganas comparabilidad entre compañeros; pierdes la individualización total. Tu decisión sobre qué proveedor explorar, tu límite y tu alternativa siguen siendo tuyos.
'''),
        md(f'''
## El hilo del evaluador

{svg("01_hilo_s06", "Cadena S3 evidencia documental, S4 persistencia en Atlas, S5 bandeja priorizada con H1 refutada 0 de 77, S6 contexto relacional con la hipótesis H2-R")}

**Cómo se lee.** Cada sesión entrega el producto que abre la siguiente.

**Qué nos dice.** S6 continúa la misma investigación, no empieza un tema suelto.

**Qué NO permite concluir todavía.** Que exista una cadena de sesiones no significa que ya haya evidencia de algo irregular.

**Error frecuente.** Tratar cada sesión como un capítulo aislado.
'''),
        md('''
## Neo4j: qué es, y por qué aparece aquí

### Qué es, en una frase

**Neo4j guarda la relación misma como un dato** —no como un cálculo que se rehace cada vez que preguntas—, para poder recorrer varios saltos de conexión sin escribir un cruce por cada salto.

### Cómo lo logra

Cada nodo (`Entidad`, `Proceso`, `Proveedor`) y cada relación (`PUBLICA`, `ADJUDICADO_A`) quedan guardados juntos. Preguntar “¿qué hay conectado a esto, y qué hay conectado a eso otro?” es recorrer flechas ya guardadas, no repetir un cruce por cada nivel de la cadena.

### Frente a lo que ya conocías

| Motor | Cómo resuelve “cruzar” | Costo de un salto adicional |
|---|---|---|
| MongoDB (`$lookup`) / SQL (`JOIN`) | recalcula el cruce en cada consulta | crece con cada nivel que agregas |
| Cassandra (S5) | evita el cruce: diseña la tabla para una sola pregunta fija | no aplica — esa pregunta no cambia |
| Neo4j (hoy) | guarda la relación como dato y la recorre | un salto más es una flecha más, no un cruce más |

### ¿Dónde se usa esto en la vida real?

| Sistema que ya conoces | Nodo | Relación | Pregunta que responde |
|---|---|---|---|
| LinkedIn / Facebook | una persona | `ES_AMIGO_DE`, `TRABAJA_EN` | “¿Cuál es el contacto en común entre tú y un desconocido?” |
| Google Maps / Waze | una intersección | `CONECTA_CON` | “¿Cuál es la ruta más corta entre dos puntos?” |
| Netflix / Spotify | un usuario o contenido | `VIO`, `ESCUCHÓ` | “¿Qué otros usuarios con gustos parecidos vieron algo que tú no?” |
| Un banco antifraude | una cuenta | `TRANSFIRIÓ_A` | “¿Esta cuenta está conectada, en pocos saltos, con cuentas ya marcadas?” |

Hoy tu grafo es más pequeño (`Entidad`, `Proceso`, `Proveedor`), pero la pregunta es la misma familia: **quién está conectado con quién, y a través de qué**.
'''),
        question_cell(1, "Motor", "¿Cuál de estos motores recalcula el cruce completo cada vez que preguntas, en vez de guardar la relación como parte del dato?", [
            "Neo4j.",
            "MongoDB (`$lookup`) o SQL (`JOIN`).",
            "Cassandra.",
        ], 1, [
            "Neo4j guarda la relación como dato; por eso no la recalcula.",
            "Correcto. Cada consulta con $lookup o JOIN vuelve a cruzar desde cero.",
            "Cassandra evita el cruce diseñando la tabla para una sola pregunta fija.",
        ]),
        md('''
**PARA LLEVAR.** Neo4j no aparece porque “toca grafos”. Aparece porque la pregunta de Laura —qué hay alrededor de este proceso, y alrededor de eso— ya es, literalmente, una pregunta de relaciones.

## Mapa de la sesión

| Bloque | Rol | Pregunta | Herramienta | Qué queda |
|---|---|---|---|---|
| 1. El caso de trabajo | 🧠 ENTIENDE | ¿qué proceso y qué historial vamos a usar? | Colab | proceso + entidad + prensa |
| 2. H2-R y contexto | 🧠 + ✏️ | ¿qué historial rodea esa entidad? | pandas | tabla de contraste |
| 3. Diseñar | 🧠 + ✏️ | ¿qué es nodo y qué es relación? | papel + cuaderno | Entidad → Proceso → Proveedor |
| 4. Contrato pandas | ▶️ EJECUTA | ¿qué debe responder el grafo? | pandas | resultado esperado |
| 5. AuraDB | ▶️ EJECUTA | ¿cómo levantamos el servicio? | tutorial + Neo4j Aura | conexión real |
| 6. Cypher | ▶️ EJECUTA | ¿cómo cargamos y recorremos relaciones? | Cypher/Neo4j | grafo consultable |
| 7. Verificar | 🧠 + ▶️ | ¿Neo4j conserva la respuesta? | pandas + Neo4j | pandas = Neo4j |
| 8. Hito | ✏️ MODIFICA | ¿qué puede sostener Laura? | Colab | ficha + límite + export |

### Semáforo de código

- 🧠 **ENTIENDE:** debes poder explicarlo con tus palabras.
- ▶️ **EJECUTA:** corre la celda y verifica la salida; **no necesitas escribirla de memoria**.
- ✏️ **MODIFICA/DECIDE:** cambia el dato señalado o responde antes de ver el resultado completo.

**Diferencia con la versión original de S6:** aquí casi todos los bloques mezclan 🧠 y ✏️ en la misma frase — nunca hay dos conceptos seguidos sin una acción entre medio.
'''),
        md('''
---
## 1. El caso de trabajo de esta sesión

Esta versión trabaja siempre sobre la misma entidad: la más rica en relaciones de todo el extracto. No pide ningún archivo de S5 — así cualquiera puede correr este cuaderno de forma independiente.

**OJO.** El hito declara con honestidad que este es el caso compartido, no un proceso que tú elegiste en S5.
'''),
        code(f"""
import json
import urllib.request
import pandas as pd

DATA_URL = {DATA!r}
MANIFEST_URL = {MANIFEST!r}

datos = pd.read_csv(DATA_URL, low_memory=False)
with urllib.request.urlopen(MANIFEST_URL) as r:
    manifest = json.loads(r.read().decode("utf-8"))

ancla_trabajo = dict(manifest["ancla_pedagogica"])
print("Entidad de trabajo:", ancla_trabajo["entidad"])
print(json.dumps(ancla_trabajo, ensure_ascii=False, indent=2))
print("Filas disponibles:", len(datos))
"""),
        md('''
### Cómo se lee la entrada

**Cómo se lee.** El caso de trabajo es un proceso real de SECOP, elegido porque su entidad tiene el historial más rico del extracto — así el ejercicio siempre tiene señal suficiente para explorar.

**Qué nos dice.** Trabajamos sobre datos reales desde la primera celda.

**Qué NO permite concluir todavía.** Tener historial contractual no significa que exista una relación problemática.

**Error frecuente.** Pensar que esta entidad fue elegida por sospecha — se eligió por tener suficiente historial para aprender, nada más.
'''),
        md(f'''
---
## 2. H2-R: la hipótesis relacional de esta sesión

S5 cerró con una hipótesis de prensa: **H1** — ¿aparece literalmente alguno de los 77 IDs de proceso en título o subtítulo de una noticia? El resultado fue `0/77`: **H1 literal refutada**, y la prensa quedó especificada como contexto de entidad, no como evidencia directa de un proceso.

S6 abre una hipótesis distinta, ahora relacional:

> **H2-R.** El proveedor histórico más conectado de la entidad de este caso está conectado con más entidades que la mediana de esa misma conexión entre las 32 entidades candidatas de S5 que tienen historial.

No es una prueba estadística inferencial: es una comparación empírica y falsable sobre este extracto.

### Ejemplo manual pequeño (nombres inventados, para pensar antes de programar)

{svg("02_ejemplo_manual", "La Alcaldía de Ejemplo y la Gobernación de Prueba publican procesos distintos, ambos adjudicados a Constructora Ejemplo S.A.S.")}

Mirando solo este dibujo, sin ninguna tabla: **Constructora Ejemplo S.A.S. aparece conectada con dos entidades distintas** —la Alcaldía de Ejemplo y la Gobernación de Prueba— a través de dos procesos separados. Eso es H2-R con nombres inventados: Constructora Ejemplo S.A.S. es justo el tipo de proveedor que la hipótesis busca — uno adjudicado por más de una entidad.

El proceso de este caso puede no estar adjudicado directamente: **no le inventamos un proveedor**. El historial adjudicado —procesos ya cerrados de la misma entidad— es lo que sí aporta proveedores reales y conexiones observadas.
'''),
        question_cell(2, "H2-R", "Si Constructora Ejemplo S.A.S. aparece adjudicada tanto por la Alcaldía de Ejemplo como por la Gobernación de Prueba, ¿qué puede afirmarse?", [
            "Que Constructora Ejemplo S.A.S. aparece conectada contractualmente con al menos dos entidades en este extracto.",
            "Que Constructora Ejemplo S.A.S. es sospechosa de irregularidad.",
            "Que las dos entidades coordinaron la adjudicación entre sí.",
        ], 0, [
            "Correcto. Eso es exactamente lo que el grafo describe: una estructura registrada, no una conclusión sobre conducta.",
            "La conectividad por sí sola no prueba irregularidad.",
            "La conectividad por sí sola no prueba coordinación.",
        ]),
        code("""
nit_deseado = str(ancla_trabajo.get("nit_entidad", "")).strip()
hist = datos[datos["tipo_registro"].eq("historico_adjudicado")].copy()
hist_ancla = hist[hist["nit_entidad"].astype(str).str.strip().eq(nit_deseado)]

print("Entidad de trabajo:", ancla_trabajo["entidad"])
print("Procesos históricos:", hist_ancla["id_proceso"].nunique())
print("Proveedores distintos:", hist_ancla["nit_proveedor"].nunique())
"""),
        md('''
### Interpretación del contexto histórico

**Cómo se lee.** Los conteos corresponden al historial adjudicado disponible para la entidad de trabajo, no al proceso candidato aislado.

**Qué nos dice.** Hay material relacional suficiente para preguntar por proveedores y conexiones entre procesos.

**Qué NO permite concluir todavía.** Más procesos o proveedores no equivalen a mayor riesgo.

**Error frecuente.** Usar el número de contratos como una puntuación de sospecha.
'''),
        question_cell(3, "Modelo", "Acabas de ver el historial de esta entidad. ¿Por qué el proceso de trabajo no necesita todavía una relación hacia un proveedor?", [
            "Porque Neo4j no soporta proveedores en procesos recientes.",
            "Porque puede no estar adjudicado directamente; sirve como ancla y el historial aporta proveedores reales.",
            "Porque los proveedores pertenecen a Elasticsearch.",
        ], 1, [
            "Neo4j sí soporta esa relación; el límite está en la evidencia.",
            "Exacto. No fabricamos una relación que el dato no sostiene.",
            "Elasticsearch resolverá otra pregunta: búsqueda textual y relevancia.",
        ]),
        md(f'''
---
## 3. Diseñar el grafo antes de escribir la consulta final

Antes de escribir Cypher, cinco palabras y nada más.

| Concepto | Qué es | Ejemplo (Constructora Ejemplo S.A.S.) |
|---|---|---|
| Nodo | una entidad del dominio | el proveedor mismo |
| Label | la categoría del nodo | `Proveedor` |
| Propiedad | un dato guardado en el nodo | `nit: "900123456"` |
| Relación | un hecho dirigido entre dos nodos | `ADJUDICADO_A` |
| Camino | una secuencia de nodos y relaciones | Entidad → Proceso → Proveedor |

**Los mismos 5 conceptos, en LinkedIn:** Nodo = una persona · Label = `Persona` o `Empresa` · Propiedad = `nombre: "Ana"` · Relación = `ES_CONTACTO_DE` · Camino = la cadena de contactos que te conecta con alguien que nunca has visto.
'''),
        code('''
# EJERCICIO — identifica las tres piezas del patrón (v:Proveedor {nit:"900123456"})
variable = "____"   # una sola letra: la variable con la que nombras el nodo
label = "____"      # la categoria (el label) del nodo
propiedad = "____"  # el par clave:valor, tal cual aparece entre llaves

if variable != "v":
    raise ValueError('La variable es la letra justo despues del parentesis: v')
if label != "Proveedor":
    raise ValueError('El label es la categoria despues de los dos puntos: Proveedor')
if propiedad != \'nit:"900123456"\':
    raise ValueError(\'La propiedad es el par completo entre llaves: nit:"900123456"\')
print("Correcto: variable=v, label=Proveedor, propiedad=nit:\\"900123456\\"")
'''),
        md('''
### Cómo se lee `(e:Entidad {nit:"123"})`

- `e` — variable con la que nombras este nodo en el resto de la consulta.
- `Entidad` — el label: la categoría a la que pertenece.
- `{nit:"123"}` — una propiedad que identifica cuál Entidad exactamente.

Con eso ya puedes leer un patrón completo: `(e:Entidad)-[:PUBLICA]->(p:Proceso)` es "un nodo Entidad conectado, mediante la relación PUBLICA, a un nodo Proceso".

### EJERCICIO S06-PATRON — identifica la relación

Lee el nombre de la relación entre un proceso histórico y el proveedor al que fue adjudicado.

**Qué debe verse:** `(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor)`.
**Error común:** confundir el ID de un proceso con el nombre de la relación. El ID identifica el nodo; `ADJUDICADO_A` nombra la flecha.

<details><summary><strong>Recuperación si te atascaste</strong></summary>
La relación se llama <code>ADJUDICADO_A</code>; el cuaderno ya la deja preparada.
</details>
'''),
        code("""
RELACION_PROCESO_PROVEEDOR = "ADJUDICADO_A"
patron_estudiante = f"(p:Proceso)-[:{RELACION_PROCESO_PROVEEDOR}]->(v:Proveedor)"
print(patron_estudiante)

print("Patrón correcto: ADJUDICADO_A expresa una adjudicación observada.")
"""),
        md(f'''
### Modelo mínimo que usaremos

{svg("03_modelo_minimo", "Entidad publica un Proceso, que es adjudicado a un Proveedor")}

`(e:Entidad)-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor)` — así se escribe ese mismo dibujo en Cypher.

| Elemento | Identificador | Decisión |
|---|---|---|
| `Entidad` | NIT | actor que publica |
| `Proceso` | ID SECOP | nodo con texto, valor, modalidad y URL |
| `Proveedor` | NIT | actor adjudicado que puede conectar procesos |
| `PUBLICA` | relación | quién publica el proceso |
| `ADJUDICADO_A` | relación | a quién se adjudicó un proceso histórico |

### La alternativa que descartamos

| Opción | Cómo se vería | Por qué no la usamos hoy |
|---|---|---|
| **Proceso como nodo** (la que usamos) | `(e)-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v)` | `Proceso` participa en caminos propios y S7 reutiliza su texto |
| Proceso como propiedad de una relación directa | `(e:Entidad)-[:CONTRATO {{id_proceso:"...", valor:...}}]->(v:Proveedor)` | más simple, pero un proceso deja de ser algo que puedas recorrer o conectar con otra cosa por sí mismo |

### Función usada: `MERGE`

- **Para qué sirve:** encuentra un nodo o relación que ya existe con esa identidad, o lo crea si no existe — nunca lo duplica.
- **Por qué aparece:** el runtime de Colab se reinicia solo, y el receso pasa a mitad de sesión. Sin `MERGE`, volver a ejecutar la carga crearía un segundo `Proceso 2024-001` idéntico al primero.
- **Intuición en palabras:** es como decir “busca esta persona por su cédula; si no está, regístrala — pero nunca la registres dos veces”.
- **Error frecuente:** usar `CREATE` en su lugar y terminar con varios nodos duplicados del mismo proceso.

### Cypher mínimo

| Construcción | Para qué sirve | Qué devuelve/cambia | Error frecuente |
|---|---|---|---|
| `MERGE` | encuentra o crea un patrón | nodos/relaciones persistidos | creer que siempre crea otro nodo |
| `MATCH` | busca patrones | filas con coincidencias | leerlo como un `SELECT *` sin relaciones |
| `WHERE` | filtra | menos coincidencias | filtrar antes de entender el patrón |
| `WITH` | encadena etapas | variables para la etapa siguiente | olvidar qué variables siguen vivas |
| `RETURN` | define la salida | columnas del resultado | confundir salida con persistencia |
| `ORDER BY` / `LIMIT` | ordena y acota | resultado priorizado | asumir orden si no se pidió |

**PARA LLEVAR.** La flecha es parte de la consulta: no es decoración visual.
'''),
        question_cell(4, "Cypher", "¿Por qué usaremos MERGE y restricciones únicas?", [
            "Para poder repetir la carga sin fabricar duplicados del mismo identificador.",
            "Porque CREATE no puede crear relaciones.",
            "Porque MERGE decide el modelo por nosotros.",
        ], 0, [
            "Correcto. La identidad explícita hace la carga repetible.",
            "CREATE sí puede crear relaciones.",
            "El modelo sigue siendo una decisión humana.",
        ]),
        md('''
---
## 4. Contrato de resultado: primero pandas

Antes de usar Neo4j calculamos qué proveedores de la entidad de trabajo también aparecen en otras entidades del extracto. Luego exigiremos a Neo4j la misma respuesta.
'''),
        code("""
prov_ancla = (
    hist_ancla.groupby(["nit_proveedor", "proveedor"], dropna=False)["id_proceso"]
    .nunique().rename("procesos_con_entidad").reset_index()
)
prov_global = (
    hist.groupby(["nit_proveedor", "proveedor"], dropna=False)["nit_entidad"]
    .nunique().rename("entidades_conectadas").reset_index()
)
esperado_pd = (
    prov_ancla.merge(prov_global, on=["nit_proveedor", "proveedor"], how="left")
    .sort_values(["entidades_conectadas", "procesos_con_entidad", "nit_proveedor"], ascending=[False, False, True])
    .head(10).reset_index(drop=True)
)

MEDIANA_H2R = float(manifest.get("mediana_maximo_conectadas_candidatas", 0))
if esperado_pd.empty:
    desenlace_h2r_pd = "no evaluable con esta ancla"
elif esperado_pd["entidades_conectadas"].max() > MEDIANA_H2R:
    desenlace_h2r_pd = "conexión más fuerte que la mediana de las candidatas de S5"
else:
    desenlace_h2r_pd = "conexión igual o menor que la mediana de las candidatas de S5"

print("Mediana de referencia (candidatas S5):", MEDIANA_H2R)
print("Desenlace H2-R (pandas):", desenlace_h2r_pd)
esperado_pd
"""),
        md('''
### Interpretación del contrato pandas y del desenlace H2-R

**Cómo se lee.** `procesos_con_entidad` cuenta procesos adjudicados de la entidad de trabajo; `entidades_conectadas` cuenta entidades distintas asociadas al mismo NIT de proveedor. El desenlace H2-R compara el máximo contra la mediana de esa misma métrica entre las 32 entidades candidatas de S5 que tienen historial.

**Qué nos dice.** Ya sabemos qué salida debería reproducir el grafo, y ya tenemos un desenlace declarado para H2-R.

**Qué NO permite concluir todavía.** Repetición o conectividad no equivale a favorecimiento, colusión ni irregularidad.

**Error frecuente.** Llamar “sospechoso” al proveedor que queda primero, o llamar “aceptada”/“rechazada” al desenlace de H2-R.
'''),
        md('''
### RECUPERACIÓN S06 — si Colab reinició antes de Aura

Ejecuta la siguiente celda siempre que vuelvas del receso. Si el estado sigue vivo, solo lo confirma. Si se perdió, reconstruye todo desde cero automáticamente — sin pedirte ningún archivo.
'''),
        hidden(code(f"""
# RECUPERACIÓN S06
if "pregunta_codificada" not in globals() or "tutorial" not in globals():
    exec({INTERACTIVITY!r})

estado_necesario = ["datos", "manifest", "ancla_trabajo", "hist", "hist_ancla", "esperado_pd", "nit_deseado", "desenlace_h2r_pd"]
if not all(nombre in globals() for nombre in estado_necesario):
    import json, urllib.request
    import pandas as pd

    DATA_URL = {DATA!r}
    MANIFEST_URL = {MANIFEST!r}
    datos = pd.read_csv(DATA_URL, low_memory=False)
    with urllib.request.urlopen(MANIFEST_URL) as r:
        manifest = json.loads(r.read().decode("utf-8"))

    ancla_trabajo = dict(manifest["ancla_pedagogica"])
    nit_deseado = str(ancla_trabajo.get("nit_entidad", "")).strip()
    hist = datos[datos["tipo_registro"].eq("historico_adjudicado")].copy()
    hist_ancla = hist[hist["nit_entidad"].astype(str).str.strip().eq(nit_deseado)]

    prov_ancla = (
        hist_ancla.groupby(["nit_proveedor", "proveedor"], dropna=False)["id_proceso"]
        .nunique().rename("procesos_con_entidad").reset_index()
    )
    prov_global = (
        hist.groupby(["nit_proveedor", "proveedor"], dropna=False)["nit_entidad"]
        .nunique().rename("entidades_conectadas").reset_index()
    )
    esperado_pd = (
        prov_ancla.merge(prov_global, on=["nit_proveedor", "proveedor"], how="left")
        .sort_values(["entidades_conectadas", "procesos_con_entidad", "nit_proveedor"], ascending=[False, False, True])
        .head(10).reset_index(drop=True)
    )

    MEDIANA_H2R = float(manifest.get("mediana_maximo_conectadas_candidatas", 0))
    if esperado_pd.empty:
        desenlace_h2r_pd = "no evaluable con esta ancla"
    elif esperado_pd["entidades_conectadas"].max() > MEDIANA_H2R:
        desenlace_h2r_pd = "conexión más fuerte que la mediana de las candidatas de S5"
    else:
        desenlace_h2r_pd = "conexión igual o menor que la mediana de las candidatas de S5"
    print("Estado S6 reconstruido desde archivos versionados.")
else:
    print("Estado S6 sigue en memoria; no fue necesario reconstruirlo.")

print("Entidad de trabajo:", ancla_trabajo["entidad"])
print("Filas contrato pandas:", len(esperado_pd))
print("Desenlace H2-R (pandas):", desenlace_h2r_pd)
"""), "Recuperar estado S6"),
        md('''
---
## receso
'''),
        md('''
## 5. Tutorial visual — AuraDB

**HAZ ESTO AHORA.** Vuelve cuando `RETURN 1 AS conexion` funcione en Query y tengas URI, usuario y contraseña.

El HTML es **instrumental**: muestra el camino de interfaz. Las pantallas dibujadas están rotuladas como representaciones; no se presentan como capturas autenticadas.
'''),
        hidden(code(f'tutorial({TUTORIAL!r})'), "Abrir tutorial Neo4j Aura"),
        code("""
!pip install -q "neo4j>=6,<7"
from getpass import getpass
from neo4j import GraphDatabase

URI = input("Connection URI: ").strip()
USER = input("User name: ").strip()
PASSWORD = getpass("Password (no se muestra): ")
if not URI or not USER or not PASSWORD:
    raise ValueError("URI, usuario y contraseña son obligatorios.")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
driver.verify_connectivity()
print("Conexión Neo4j verificada.")
"""),
        md('''
---
## Antes de cargar los datos reales: un grafo de juguete

**Calentamiento; no es evidencia de tu hito.** Antes de cargar 2.109 filas de Compras Claras, practica los mismos movimientos de Cypher con un grafo mínimo y conocido: una película, tres actores, y una red de amigos. Si algo falla aquí, es mucho más fácil de diagnosticar que si falla con el dataset real.

### 1. Crear un nodo — `MERGE`

Ya conoces `MERGE` de la mini-ficha anterior. Ahora lo usas por primera vez contra Aura, con un ejemplo mínimo.
'''),
        code("""
driver.execute_query("MERGE (:Movie {title: $title})", title="The Matrix")
driver.execute_query("MERGE (:Person {name: $name})", name="Keanu Reeves")
driver.execute_query("MERGE (:Person {name: $name})", name="Carrie-Anne Moss")
driver.execute_query("MERGE (:Person {name: $name})", name="Laurence Fishburne")
print("Nodos de juguete creados: 1 Movie, 3 Person.")
"""),
        md('''
### 2. Crear una relación — patrón `MATCH` + `MATCH` + `MERGE`

Para conectar dos nodos que ya existen, primero los *encuentras* con `MATCH` (uno por cada lado) y luego creas el puente entre ellos con `MERGE`.
'''),
        code("""
for actor in ["Keanu Reeves", "Carrie-Anne Moss", "Laurence Fishburne"]:
    driver.execute_query('''
        MATCH (actor:Person {name:$name})
        MATCH (pelicula:Movie {title:$title})
        MERGE (actor)-[:ACTED_IN]->(pelicula)
    ''', name=actor, title="The Matrix")
print("Relaciones ACTED_IN creadas para los 3 actores.")
"""),
        md('''
**Cómo se lee.** Cada `MATCH` encuentra un nodo que ya existía; `MERGE` no vuelve a crearlo, solo agrega la flecha entre los dos.

**Qué nos dice.** Es el mismo patrón de tres pasos (encontrar, encontrar, conectar) que usarás con Entidad → Proceso → Proveedor.

**Qué NO permite concluir todavía.** Que dos nodos estén conectados no dice nada sobre la calidad de esa conexión — apenas estamos practicando la mecánica.

**Error frecuente.** Usar `MERGE` también para los dos `MATCH` — eso arriesga crear un actor o película duplicados si el nombre no coincide exactamente.

**HAZ ESTO AHORA.** Ejecuta la siguiente celda: va a **dibujar el grafo aquí mismo, en Colab** — nodos y flechas de verdad, con los datos que tú acabas de crear. No necesitas salir a Aura para esto.
'''),
        code("""
import networkx as nx
import matplotlib.pyplot as plt

resultado_grafo = driver.execute_query('''
    MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
    RETURN p.name AS persona, m.title AS pelicula
''')

G = nx.DiGraph()
for r in resultado_grafo.records:
    G.add_edge(r["persona"], r["pelicula"])

plt.figure(figsize=(6, 4))
pos = nx.spring_layout(G, seed=7)
colores = ["#c9a227" if n == "The Matrix" else "#175c3c" for n in G.nodes()]
nx.draw(G, pos, with_labels=True, node_color=colores, font_color="white", font_size=9, font_weight="bold", node_size=2400, edgecolors="black")
nx.draw_networkx_edge_labels(G, pos, edge_labels={e: "ACTED_IN" for e in G.edges()}, font_size=8)
plt.title("Tu primer grafo dibujado: actores → película")
plt.axis("off")
plt.show()
"""),
        md('''
**OJO.** Son apenas 4 nodos — el "poder" de un grafo no está en que se vea bonito con pocos datos, está en que la MISMA consulta, sin cambiar una palabra, funcionaría igual de bien con 3 millones de actores y películas. Eso es justo lo que vas a comprobar más adelante con 2.109 filas reales.

### 3. Actualizar una propiedad — `SET`

`SET` agrega o cambia una propiedad de un nodo que ya existe. No crea nada nuevo.
'''),
        code("""
driver.execute_query("MATCH (p:Person {name:$name}) SET p.age = $age", name="Keanu Reeves", age=41)
driver.execute_query("MATCH (p:Person {name:$name}) SET p.age = $age", name="Laurence Fishburne", age=52)
print("Edad asignada a dos actores.")
"""),
        md('''
### 4. Consultar — `MATCH` + `RETURN`, con filtros y conteo

Cuatro consultas, cada una agregando algo nuevo.
'''),
        code("""
r1 = driver.execute_query("MATCH (p:Person) RETURN p.name AS name")
print("Todas las personas:", [r["name"] for r in r1.records])

r2 = driver.execute_query("MATCH (p:Person {age:$age}) RETURN p.name AS name", age=41)
print("Personas de 41 años:", [r["name"] for r in r2.records])

r3 = driver.execute_query('''
    MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
    RETURN p.name AS actor, m.title AS pelicula
''')
print("Quién actuó en qué:", [r.data() for r in r3.records])

r4 = driver.execute_query("MATCH (p:Person) WHERE p.age > 40 RETURN count(p) AS mayores_40")
print("Personas mayores de 40:", r4.records[0]["mayores_40"])
"""),
        md('''
**Cómo se lee.** Cada consulta agrega una pieza: filtrar por propiedad, recorrer una relación, contar con una condición.

**Qué nos dice.** Con las mismas piezas (`MATCH`, `WHERE`, recorrer una relación, `count()`) vas a construir la consulta real de Compras Claras más adelante.

**Qué NO permite concluir todavía.** Nada — este grafo es de juguete y no representa ningún caso real.

**Error frecuente.** Olvidar que `age` es un número, no un texto: `age:"41"` no encontraría nada.

### 5. Borrar — `DETACH DELETE`

Borrar un nodo que tiene relaciones falla con `DELETE` a secas — hay que borrar también sus relaciones en el mismo paso, con `DETACH DELETE`.
'''),
        code("""
driver.execute_query("MATCH (p:Person {name:$name}) DETACH DELETE p", name="Laurence Fishburne")
check = driver.execute_query("MATCH (p:Person {name:$name}) RETURN p.name AS name", name="Laurence Fishburne")
print("¿Sigue existiendo Laurence Fishburne?", len(check.records) > 0)
"""),
        md('''
**Cómo se lee.** `DETACH DELETE` borra el nodo y, en el mismo paso, todas sus relaciones — aquí, su `ACTED_IN` hacia The Matrix.

**Qué nos dice.** La consulta de verificación debe devolver una lista vacía: el nodo ya no está.

**Qué NO permite concluir todavía.** No aplica — es un borrado de práctica, no una decisión sobre datos reales.

**Error frecuente.** Usar `DELETE p` sin `DETACH` cuando el nodo todavía tiene relaciones — Neo4j lo rechaza con un error explícito en vez de borrar a medias.

### 6. Carga masiva desde Python — el mismo patrón `UNWIND` que usarás con 2.109 filas

Hasta ahora creaste nodos uno por uno. Cuando los datos ya viven en una lista de Python, `UNWIND` los recorre todos en una sola consulta — exactamente lo que vas a hacer con el extracto real en un momento.
'''),
        code("""
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

print("Red de amigos cargada: 4 personas, relaciones KNOWS desde Alice.")
"""),
        md('''
**Cómo se lee.** El primer `UNWIND` crea las 4 personas de una vez; el segundo recorre, para cada persona, su lista de amigos y crea la relación `KNOWS`.

**Qué nos dice.** Es exactamente la misma mecánica que usarás para cargar 2.109 filas de Compras Claras en un momento — la única diferencia es el tamaño de la lista.

**Qué NO permite concluir todavía.** Nada — sigue siendo el grafo de juguete.

**Error frecuente.** Anidar `UNWIND` dentro de `UNWIND` sin distinguir bien las variables — aquí `fila` y `nombre_amigo` son cosas distintas, no las confundas.

### Extra: una consulta que una tabla no responde tan fácil — "amigos de amigos"

En SQL esto pide un `JOIN` de la tabla contra sí misma. En Cypher es una flecha más en el mismo patrón.
'''),
        code("""
r5 = driver.execute_query('''
    MATCH (yo:Person {name:$name})-[:KNOWS]->(amigo)-[:KNOWS]->(amigo_de_amigo)
    WHERE amigo_de_amigo <> yo
    RETURN DISTINCT amigo_de_amigo.name AS nombre
''', name="Alice")
print("Amigos de amigos de Alice (2 saltos):", [r["nombre"] for r in r5.records])
"""),
        md('''
**Cómo se lee.** La consulta recorre dos flechas `KNOWS` seguidas: de Alice a su amigo, y de ese amigo a los suyos.

**Qué nos dice.** Como en este grafo nadie tiene un segundo salto todavía (Bob, Peter y Anna no tienen amigos propios cargados), la lista sale vacía — y eso también es una lectura válida: el patrón está bien escrito, simplemente el dato no lo sostiene.

**Qué NO permite concluir todavía.** Nada nuevo — sigue siendo el grafo de juguete.

**Error frecuente.** Pensar que una lista vacía significa que la consulta está mal. Antes de asumir un error, confirma si el patrón realmente tiene datos que lo satisfagan.

**HAZ ESTO AHORA.** Dibuja el grafo completo de amigos, aquí mismo en Colab:
'''),
        code("""
resultado_amigos = driver.execute_query('''
    MATCH (p:Person)-[:KNOWS]-(otra:Person)
    RETURN p.name AS persona, otra.name AS otra_persona
''')

G_amigos = nx.Graph()
for r in resultado_amigos.records:
    G_amigos.add_edge(r["persona"], r["otra_persona"])

plt.figure(figsize=(6, 4))
pos = nx.spring_layout(G_amigos, seed=3)
colores_amigos = ["#c9a227" if n == "Alice" else "#3b5bab" for n in G_amigos.nodes()]
nx.draw(G_amigos, pos, with_labels=True, node_color=colores_amigos, font_color="white", font_size=9, font_weight="bold", node_size=2200, edgecolors="black")
plt.title("Red de amigos completa (KNOWS)")
plt.axis("off")
plt.show()
"""),
        md('''
**PARA LLEVAR.** Con solo 7 nodos ya viste tres formas distintas de "preguntar por relaciones": contar cuántas salen de alguien, seguir dos saltos seguidos, y dibujar el grafo completo. Esas mismas tres formas son las que vas a usar en Compras Claras, con miles de nodos en vez de 7.

### Limpieza antes del caso real

Antes de cargar Compras Claras, borra el grafo de juguete completo para que no se mezcle con Entidad/Proceso/Proveedor.
'''),
        code("""
driver.execute_query("MATCH (n) WHERE n:Movie OR n:Person DETACH DELETE n")
check = driver.execute_query("MATCH (n) WHERE n:Movie OR n:Person RETURN count(n) AS restantes")
print("Nodos de juguete restantes (debe ser 0):", check.records[0]["restantes"])
"""),
        md('''
---
## 6. Identidad y carga idempotente

Primero creamos restricciones. Después `UNWIND` recibe una lista de filas desde Python y `MERGE` reutiliza nodos ya existentes.
'''),
        code("""
constraints = [
    "CREATE CONSTRAINT entidad_nit IF NOT EXISTS FOR (e:Entidad) REQUIRE e.nit IS UNIQUE",
    "CREATE CONSTRAINT proceso_id IF NOT EXISTS FOR (p:Proceso) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT proveedor_nit IF NOT EXISTS FOR (v:Proveedor) REQUIRE v.nit IS UNIQUE",
]
for q in constraints:
    driver.execute_query(q)
print("Restricciones listas.")
"""),
        md('''
### Función usada: `UNWIND`

- **Para qué sirve:** convierte una lista (de filas, de diccionarios) en filas individuales que Cypher procesa una por una dentro de la misma consulta.
- **Por qué aparece:** vas a cargar miles de filas de una sola vez desde Python; sin `UNWIND` tendrías que enviar una consulta por fila.
- **Intuición en palabras:** es como decir “toma esta lista de invitados y preséntamelos uno por uno”, para hacer lo mismo con cada uno.
- **Ejemplo manual:** con `filas = [{"id":"P1"}, {"id":"P2"}, {"id":"P3"}]`, `UNWIND $filas AS fila` hace que la consulta se ejecute tres veces: una con `fila.id = "P1"`, otra con `"P2"`, otra con `"P3"`.
- **Error frecuente:** usar `filas` (la lista completa) en vez de `fila` (el elemento actual) dentro del patrón.
'''),
        code("""
cols = [
    "entidad", "nit_entidad", "departamento_entidad", "id_proceso", "referencia",
    "nombre_proceso", "descripcion", "precio_base", "modalidad", "proveedor",
    "nit_proveedor", "departamento_proveedor", "noticias_entidad", "nivel_menciones",
    "url_secop", "es_proceso_candidato_s05", "es_entidad_candidata_s05",
]
rows = datos[cols].where(pd.notna(datos[cols]), None).to_dict("records")

query_base = '''
UNWIND $filas AS fila
MERGE (e:Entidad {nit: toString(fila.nit_entidad)})
SET e.nombre = fila.entidad,
    e.departamento = fila.departamento_entidad,
    e.es_candidata_s05 = fila.es_entidad_candidata_s05,
    e.noticias_entidad = fila.noticias_entidad,
    e.nivel_menciones = fila.nivel_menciones
MERGE (p:Proceso {id: fila.id_proceso})
SET p.referencia = fila.referencia,
    p.nombre = fila.nombre_proceso,
    p.descripcion = fila.descripcion,
    p.valor = fila.precio_base,
    p.modalidad = fila.modalidad,
    p.url = fila.url_secop,
    p.es_candidato_s05 = fila.es_proceso_candidato_s05
MERGE (e)-[:PUBLICA]->(p)
'''
driver.execute_query(query_base, filas=rows)

rows_proveedor = [r for r in rows if r.get("nit_proveedor")]
query_proveedor = '''
UNWIND $filas AS fila
MATCH (p:Proceso {id: fila.id_proceso})
MERGE (v:Proveedor {nit: toString(fila.nit_proveedor)})
SET v.nombre = fila.proveedor, v.departamento = fila.departamento_proveedor
MERGE (p)-[:ADJUDICADO_A]->(v)
'''
driver.execute_query(query_proveedor, filas=rows_proveedor)
print("Carga lista:", len(rows), "filas;", len(rows_proveedor), "adjudicaciones.")
"""),
        md('''
### Antes de la consulta completa: qué agrega cada salto

Antes de la consulta final, mira qué cambia cuando agregas una flecha más al patrón.
'''),
        code("""
r0 = driver.execute_query("MATCH (e:Entidad) RETURN e.nombre AS entidad LIMIT 5")
print("0 relaciones -- solo nodos Entidad:")
print(pd.DataFrame([r.data() for r in r0.records]))

r1 = driver.execute_query("MATCH (e:Entidad)-[:PUBLICA]->(p:Proceso) RETURN e.nombre AS entidad, p.id AS proceso LIMIT 5")
print("\\n1 relacion (PUBLICA) -- que publico cada entidad:")
print(pd.DataFrame([r.data() for r in r1.records]))
"""),
        code("""
r2 = driver.execute_query('''
MATCH (e:Entidad)-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor)
RETURN e.nombre AS entidad, p.id AS proceso, v.nombre AS proveedor
LIMIT 5
''')
print("2 relaciones (PUBLICA + ADJUDICADO_A) -- a quien se adjudico:")
pd.DataFrame([r.data() for r in r2.records])
"""),
        md('''
| Saltos | Qué responde | Ejemplo de pregunta |
|---|---|---|
| 0 | qué entidades existen | ¿qué entidades cargamos? |
| 1 (`PUBLICA`) | qué publicó cada entidad | ¿qué procesos abrió esta entidad? |
| 2 (`PUBLICA`+`ADJUDICADO_A`) | a quién se le adjudicó lo publicado | ¿a qué proveedor llegó este proceso? |

La consulta que sigue agrega un tercer salto: desde ese proveedor, vuelve a **todas** las entidades conectadas.
'''),
        md('''
---
## 7. La consulta que justifica Neo4j

Ahora recorremos el patrón Entidad → Proceso → Proveedor y, desde ese proveedor, contamos otras entidades conectadas.
'''),
        code("""
query_contexto = '''
MATCH (e:Entidad {nit:$nit})-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor)
WITH v, count(DISTINCT p) AS procesos_con_entidad
MATCH (otra:Entidad)-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v)
RETURN v.nit AS nit_proveedor,
       v.nombre AS proveedor,
       procesos_con_entidad,
       count(DISTINCT otra) AS entidades_conectadas
ORDER BY entidades_conectadas DESC, procesos_con_entidad DESC, nit_proveedor ASC
LIMIT 10
'''
neo = driver.execute_query(query_contexto, nit=nit_deseado)
neo_df = pd.DataFrame([r.data() for r in neo.records])
neo_df
"""),
        code("""
def normalizar_nit(serie):
    # "123.0" y "123" deben tratarse como el mismo NIT (una conversión de
    # tipo intermedia puede volver flotante un entero antes de cargarlo).
    return serie.astype(str).str.strip().str.replace(r"\\.0$", "", regex=True)

cols_cmp = ["nit_proveedor", "procesos_con_entidad", "entidades_conectadas"]
pd_cmp = esperado_pd[cols_cmp].copy()
neo_cmp = neo_df[cols_cmp].copy()
pd_cmp["nit_proveedor"] = normalizar_nit(pd_cmp["nit_proveedor"])
neo_cmp["nit_proveedor"] = normalizar_nit(neo_cmp["nit_proveedor"])
coinciden = pd_cmp.reset_index(drop=True).equals(neo_cmp.reset_index(drop=True))
print("pandas == Neo4j:", coinciden)

if not coinciden:
    print("\\nFilas esperadas (pandas):")
    print(pd_cmp.reset_index(drop=True))
    print("\\nFilas obtenidas (Neo4j):")
    print(neo_cmp.reset_index(drop=True))
    if len(neo_cmp) < len(pd_cmp):
        print("\\nNeo4j devolvió MENOS filas que pandas — la carga de 2.109 filas probablemente no terminó.")
        print("Vuelve a ejecutar la celda 'Carga lista: ...' y espera a que termine antes de continuar.")

assert coinciden, "La respuesta Neo4j no coincide con el contrato pandas."
"""),
        md('''
### Interpretación pandas ↔ Neo4j

**Cómo se lee.** Comparamos NIT y las dos métricas en el mismo orden.

**Qué nos dice.** El grafo reproduce el patrón calculado previamente.

**Qué NO permite concluir todavía.** Es una prueba de corrección, no un benchmark de velocidad ni evidencia de irregularidad.

**Error frecuente.** Confundir “la consulta coincide” con “Neo4j es más rápido”.
'''),
        question_cell(5, "Interpretación", "Un proveedor aparece conectado con cuatro entidades. ¿Qué puede afirmar Laura?", [
            "Que existe una relación contractual observada con procesos de cuatro entidades dentro del extracto.",
            "Que las cuatro entidades coordinaron sus adjudicaciones.",
            "Que el proveedor incurrió en una irregularidad.",
        ], 0, [
            "Correcto. El grafo describe estructura registrada.",
            "La conectividad por sí sola no prueba coordinación.",
            "La conectividad por sí sola no prueba irregularidad.",
        ]),
        md('''
---
## Lo que un grafo puede hacer y una tabla no: el camino más corto

Hasta ahora contaste conexiones. Ahora vas a preguntar algo distinto: **¿cuál es el camino más corto entre tu entidad y otra, sin importar cuántos proveedores intermedios haga falta recorrer?** En SQL esto exige escribir un `JOIN` distinto por cada número de saltos que quieras probar, sin saber de antemano cuántos hacen falta. En Cypher es una sola palabra: `shortestPath`.
'''),
        code("""
if neo_df.empty:
    print("No hay proveedores conectados para calcular un camino.")
else:
    top_nit_proveedor = str(neo_df.iloc[0]["nit_proveedor"])
    otra_entidad = driver.execute_query('''
        MATCH (otra:Entidad)-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v:Proveedor {nit:$nit_proveedor})
        WHERE otra.nit <> $nit_propio
        RETURN otra.nit AS nit, otra.nombre AS nombre
        LIMIT 1
    ''', nit_proveedor=top_nit_proveedor, nit_propio=nit_deseado)

    if not otra_entidad.records:
        print("No se encontró otra entidad conectada para comparar caminos.")
    else:
        nit_destino_camino = str(otra_entidad.records[0]["nit"])
        nombre_destino_camino = otra_entidad.records[0]["nombre"]
        camino = driver.execute_query('''
            MATCH (origen:Entidad {nit:$nit_origen}), (destino:Entidad {nit:$nit_destino})
            MATCH ruta = shortestPath((origen)-[*..6]-(destino))
            RETURN [n IN nodes(ruta) | coalesce(n.nombre, n.id)] AS pasos, length(ruta) AS saltos
        ''', nit_origen=nit_deseado, nit_destino=nit_destino_camino)
        if camino.records:
            r = camino.records[0]
            print(f"Camino más corto hasta \\"{nombre_destino_camino}\\": {r['saltos']} saltos")
            print(" -> ".join(str(p) for p in r["pasos"]))
        else:
            print("No se encontró un camino en 6 saltos o menos.")
"""),
        md('''
**Cómo se lee.** `shortestPath` explora el grafo por ti y devuelve la ruta más corta que conecta los dos nodos, sin que tengas que decidir de antemano cuántos saltos probar.

**Qué nos dice.** Existe al menos una cadena de relaciones registradas entre tu entidad y la otra — a través de procesos y proveedores intermedios.

**Qué NO permite concluir todavía.** Un camino corto no es lo mismo que una relación sospechosa. Conecta datos registrados; no mide intención ni coordinación.

**Error frecuente.** Confundir "camino más corto" con "relación más fuerte" — `shortestPath` no pesa las relaciones, solo cuenta saltos.

**HAZ ESTO AHORA.** Pega esto en la pestaña Query de tu instancia Aura para ver el camino dibujado, nodo por nodo:
'''),
        code("""
print(f'''
MATCH origen = (e:Entidad {{nit:"{nit_deseado}"}})
MATCH ruta = shortestPath((e)-[*..6]-(destino:Entidad))
WHERE destino.nit <> "{nit_deseado}"
RETURN ruta
LIMIT 1
''')
"""),
        md('''
---
## Demostración guiada — el vecindario más rico del extracto

Ya calculaste el vecindario de esta misma entidad en pandas y en Neo4j. Ahora lo vas a **ver dibujado**, con nodos y flechas de verdad, en Aura.
'''),
        code("""
nit_ancla_demo = str(manifest["ancla_pedagogica"]["nit_entidad"]).strip()

query_demo_top = '''
MATCH (e:Entidad {nit:$nit})-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor)
WITH v, count(DISTINCT p) AS procesos_con_entidad
MATCH (otra:Entidad)-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v)
WITH v, procesos_con_entidad, count(DISTINCT otra) AS entidades_conectadas
WHERE entidades_conectadas > 1
RETURN v.nit AS nit_proveedor, v.nombre AS proveedor, procesos_con_entidad, entidades_conectadas
ORDER BY entidades_conectadas DESC, procesos_con_entidad DESC, nit_proveedor ASC
LIMIT 5
'''
neo_demo_df = pd.DataFrame([r.data() for r in driver.execute_query(query_demo_top, nit=nit_ancla_demo).records])
neo_demo_df
"""),
        code("""
top_demo = neo_demo_df.iloc[0]
nit_proveedor_demo = str(top_demo["nit_proveedor"])

query_visual_demo = f'''
MATCH camino_ancla = (e:Entidad {{nit:"{nit_ancla_demo}"}})-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v:Proveedor {{nit:"{nit_proveedor_demo}"}})
WITH v, collect(camino_ancla)[0] AS camino_ancla
MATCH camino_otras = (otra:Entidad)-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v)
WHERE otra.nit <> "{nit_ancla_demo}"
WITH camino_ancla, otra, collect(camino_otras)[0] AS camino_otras
RETURN camino_ancla, camino_otras
LIMIT 8
'''
print(query_visual_demo)
"""),
        md('''
**HAZ ESTO AHORA.** La siguiente celda dibuja este vecindario **aquí mismo en Colab**, con el mismo proveedor y hasta 8 entidades conectadas.
'''),
        code("""
otras_entidades_demo = driver.execute_query('''
    MATCH (otra:Entidad)-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v:Proveedor {nit:$nit_proveedor})
    WHERE otra.nit <> $nit_ancla
    RETURN DISTINCT otra.nombre AS nombre
    LIMIT 8
''', nit_proveedor=nit_proveedor_demo, nit_ancla=nit_ancla_demo)

G_demo = nx.Graph()
nombre_ancla_demo = str(manifest["ancla_pedagogica"]["entidad"])
nombre_proveedor_demo = str(top_demo["proveedor"])
G_demo.add_edge(nombre_ancla_demo, nombre_proveedor_demo)
for r in otras_entidades_demo.records:
    G_demo.add_edge(r["nombre"], nombre_proveedor_demo)

plt.figure(figsize=(9, 7))
pos = nx.spring_layout(G_demo, seed=11, k=1.3)
colores_demo = []
for n in G_demo.nodes():
    if n == nombre_proveedor_demo:
        colores_demo.append("#c9a227")
    elif n == nombre_ancla_demo:
        colores_demo.append("#175c3c")
    else:
        colores_demo.append("#3b5bab")
nx.draw(G_demo, pos, with_labels=True, node_color=colores_demo, font_color="white", font_size=8, font_weight="bold", node_size=2600, edgecolors="black")
plt.title(f"Vecindario real de Compras Claras: {nombre_proveedor_demo}")
plt.axis("off")
plt.show()
"""),
        md(f'''
**Cómo se lee.** El punto dorado es el proveedor; el verde es tu entidad ancla; los azules son las demás entidades conectadas al mismo proveedor.

**Opcional — verlo interactivo en Aura.** Si quieres poder arrastrar los nodos y hacer zoom, copia la consulta que imprimió la celda anterior, ve a tu instancia AuraDB → pestaña **Query** (no Colab), pégala y ejecútala ahí. Debería verse parecido a esto:

{svg("04_demo_vecindario", "Representación conceptual: la entidad ancla y otras entidades llegan al mismo proveedor, cada una por su propio proceso")}

**OJO.** El grafo muestra hasta 8 de las entidades conectadas con este proveedor — se acota para que se pueda leer, no porque las demás no existan.

### Antes de seguir, dos preguntas para el salón

1. En el grafo que acabas de ver, ¿cuál es el nodo puente entre las distintas entidades?
2. ¿Qué representa cada camino que dibujó Aura, y qué NO demuestra por sí solo?

**PARA LLEVAR.** Más conexiones no es lo mismo que una conexión anómala.
'''),
        md('''
---
## 8. CRUD seguro y tu propio vecindario

El CRUD usa `S06-DEMO`; no modificamos un proceso real. Después eliges uno de los **5 proveedores con más entidades conectadas** — esa elección sí es tuya, aunque la entidad de trabajo sea compartida.
'''),
        code("""
driver.execute_query('''
MERGE (e:Entidad {nit:'S06-E'}) SET e.nombre='Entidad demo'
MERGE (p:Proceso {id:'S06-DEMO'}) SET p.nombre='Proceso demo'
MERGE (v:Proveedor {nit:'S06-V'}) SET v.nombre='Proveedor demo'
MERGE (e)-[:PUBLICA]->(p)
MERGE (p)-[:ADJUDICADO_A]->(v)
''')
r = driver.execute_query("MATCH (p:Proceso {id:'S06-DEMO'}) SET p.estado_revision='revisado' RETURN p.estado_revision AS estado")
assert r.records[0]["estado"] == "revisado"
driver.execute_query("MATCH (n) WHERE n.nit IN ['S06-E','S06-V'] OR n.id='S06-DEMO' DETACH DELETE n")
print("CRUD demo completado y limpiado.")
"""),
        code("""
if neo_df.empty:
    raise ValueError("No hay proveedores para elegir.")
opciones = neo_df.head(5)
for i, row in opciones.iterrows():
    print(f"{i+1:>2}. {row['proveedor']} | entidades={row['entidades_conectadas']}")
sel = int(input("Número de proveedor: ").strip())
if not 1 <= sel <= len(opciones):
    raise ValueError("Número fuera de rango")
proveedor_elegido = opciones.iloc[sel-1]

vec = driver.execute_query('''
MATCH (e:Entidad)-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor {nit:$nit})
RETURN e.nombre AS entidad, p.id AS proceso, p.nombre AS nombre_proceso, p.valor AS valor
ORDER BY entidad, valor DESC
''', nit=str(proveedor_elegido["nit_proveedor"]))
vecindario_df = pd.DataFrame([r.data() for r in vec.records])

print("Tamaño observable de tu vecindario:")
print("  Procesos con la entidad de trabajo:", int(proveedor_elegido["procesos_con_entidad"]))
print("  Entidades conectadas:", int(proveedor_elegido["entidades_conectadas"]))
print("  Procesos visibles en el vecindario:", len(vecindario_df))
vecindario_df
"""),
        md('''
### Interpretación de tu vecindario

**Cómo se lee.** Cada fila es un proceso conectado al proveedor que elegiste; una misma entidad puede aportar varios procesos.

**Qué nos dice.** Puedes observar qué entidades y procesos del extracto comparten ese actor contractual.

**Qué NO permite concluir todavía.** Compartir proveedor no demuestra coordinación, favorecimiento ni irregularidad.

**Error frecuente.** Convertir el número de conexiones en un “score de riesgo” sin modelo ni denominador.
'''),
        md('''
### La evidencia no termina en el grafo

**OJO — esta versión no te pregunta el límite ni la alternativa.** Quedan fijos en el texto de abajo (revísalos, son reales para este caso), y por eso la rúbrica ya no los evalúa como criterio individual — lo que sigue midiendo tu propia ejecución es el proveedor que elegiste y el desenlace de H2-R.
'''),
        code("""
if neo_df.empty:
    desenlace_h2r_neo = "no evaluable con esta ancla"
elif neo_df["entidades_conectadas"].max() > MEDIANA_H2R:
    desenlace_h2r_neo = "conexión más fuerte que la mediana de las candidatas de S5"
else:
    desenlace_h2r_neo = "conexión igual o menor que la mediana de las candidatas de S5"

assert desenlace_h2r_neo == desenlace_h2r_pd, "El desenlace H2-R debería coincidir: ya vimos pandas == Neo4j."
print("Desenlace H2-R (Neo4j):", desenlace_h2r_neo)
"""),
        code("""
from pathlib import Path

limite_estudiante = "El extracto no incluye fechas de pago ni historial de cumplimiento contractual previo del proveedor."
alternativa_modelo = "Proceso como propiedad de la relación Entidad-Proveedor"
razon_alternativa = "Porque necesitamos que Proceso sea un nodo recorrible para S7, no solo un atributo"

export = vecindario_df.merge(
    datos[["id_proceso", "descripcion", "modalidad", "url_secop"]].drop_duplicates("id_proceso"),
    left_on="proceso", right_on="id_proceso", how="left"
)
export.to_json("s06_contexto_procesos.jsonl", orient="records", lines=True, force_ascii=False)

hito = f'''# Hito S06 (alterna) — Ficha relacional de revisión\\n\\n- Caso de trabajo: ancla pedagógica compartida (no una elección personal de S5)\\n- Entidad: {ancla_trabajo.get("entidad", "")}\\n- Proceso: {ancla_trabajo.get("id_proceso", "")}\\n- Noticias / nivel: {ancla_trabajo.get("noticias_entidad", "")} / {ancla_trabajo.get("nivel_menciones", "")}\\n- H1 (S5): 0/77 → refutada literalmente\\n- H2-R (S6), desenlace pandas: {desenlace_h2r_pd}\\n- H2-R (S6), desenlace Neo4j: {desenlace_h2r_neo}\\n- pandas == Neo4j: {coinciden}\\n- Proveedor elegido: {proveedor_elegido["proveedor"]}\\n- Entidades conectadas: {int(proveedor_elegido["entidades_conectadas"])}\\n- Procesos en el vecindario: {len(vecindario_df)}\\n\\n## Límite\\n{limite_estudiante}\\n\\n## Decisión de modelado\\nProceso se modeló como nodo porque participa en caminos y su texto será reutilizado en la siguiente sesión.\\n\\n### Alternativa descartada\\n{alternativa_modelo}\\n\\nRazón: {razon_alternativa}\\n'''
Path("hito_s06_ficha_relacional.md").write_text(hito, encoding="utf-8")
print(hito)

try:
    from google.colab import files
    files.download("hito_s06_ficha_relacional.md")
    files.download("s06_contexto_procesos.jsonl")
except Exception:
    print("Archivos generados en el runtime.")
"""),
        md('''
## Rúbrica S06

| Criterio | Completo | Parcial | Sin evidencia | Peso |
|---|---|---|---|---:|
| Continuidad | identifica la entidad de trabajo y su historial | solo entidad | no ejecuta la celda | 15 |
| Modelo | resuelve el hueco `ADJUDICADO_A` y el ejercicio de vocabulario correctamente | solo uno de los dos | copia el patrón sin resolverlo | 20 |
| Ejecución | vecindario propio ejecutado | solo consulta común | no hay salida | 20 |
| Verificación | `pandas == Neo4j` comprobado | muestra ambos | solo uno | 15 |
| Evidencia propia | proveedor elegido + entidades + procesos + desenlace H2-R declarado | incompleta | genérica | 30 |

**OJO.** En esta versión el límite y la alternativa de modelado del hito vienen fijos en el cuaderno (no son texto del estudiante), así que no se califican como criterio individual — la evidencia propia se concentra en qué proveedor eligió cada quien y en su desenlace de H2-R.

Las autoevaluaciones son formativas. El hito es la evidencia revisable de la sesión.
'''),
        md(f'''
---
## Hoja de trucos y puente

```text
UNWIND → convierte una lista en filas
MERGE  → encuentra o crea
MATCH  → busca patrón
WHERE  → filtra
WITH   → encadena
SET    → modifica una propiedad
RETURN → salida
DETACH DELETE → elimina nodo y relaciones
```

{svg("03_modelo_minimo", "Entidad publica un Proceso, que es adjudicado a un Proveedor")}

**Idea central.** Cassandra organizó datos para una pregunta repetitiva conocida. Neo4j hace de las relaciones una parte explícita de la pregunta.

### Lo que sigue

Laura ya puede ver el vecindario, pero ahora tiene muchos nombres y descripciones de procesos. La nueva pregunta será:

> **¿Cuáles de esos procesos son más relevantes para una búsqueda textual concreta?**

`s06_contexto_procesos.jsonl` será la entrada de Elasticsearch/BM25.
'''),
        code("""
try:
    driver.close()
    print("Conexión Neo4j cerrada.")
except Exception:
    pass
"""),
    ]


def main():
    cells = build_cells()
    validate(cells)
    save(cells, OUTPUT)
    print(f"[OK] S6-ALT generada: {len(cells)} celdas")


if __name__ == "__main__":
    main()
