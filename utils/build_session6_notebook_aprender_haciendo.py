#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera S6-ALT: la misma sesión de Neo4j, con ciclos de aprender-haciendo más cortos.

Alternativa de comparación a `Cuadernos/6_Neo4j_Contexto_Relacional.ipynb` — NO lo
reemplaza. Mismo dato, mismo caso, mismas consultas Cypher y misma demostración
guiada; la diferencia es puramente de secuencia: aquí ningún concepto nuevo se
queda sin una acción (predicción, micro-ejercicio, hueco o autoevaluación) antes
de que llegue el siguiente concepto. Reutiliza los helpers de preguntas/tutorial
del generador original para no duplicar esa lógica.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.make_notebook import code, md, save, validate
from utils.build_session6_notebook import (
    hidden, question_cell, INTERACTIVITY,
    WEB, RAW, DATA, MANIFEST, TUTORIAL, LABORATORIO,
)

OUTPUT = "Cuadernos/6_Neo4j_Contexto_Relacional_AprenderHaciendo.ipynb"
COLAB = "https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/6_Neo4j_Contexto_Relacional_AprenderHaciendo.ipynb"


def build_cells():
    return [
        md(f'''<a href="{COLAB}" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Abrir S6-ALT en Colab"></a>

**Acceso público:** [página del curso]({WEB}/) · **Laboratorio guiado (checklist paso a paso):** [ábrelo en otra pestaña ↗]({LABORATORIO})

> **Versión alterna de S6**, con el mismo contenido que `6_Neo4j_Contexto_Relacional.ipynb` pero en ciclos más cortos de predecir → hacer → confirmar. Es una comparación pedagógica, no la versión oficial.'''),
        hidden(code(INTERACTIVITY), "Preparar interactividad"),
        md('''
# Sesión 6 (alterna) — De la fila priorizada al contexto relacional con Neo4j

## Universidad Central
> ### Facultad de Ingeniería y Ciencias Básicas
> ### Maestría en Analítica de Datos — BIG DATA (64491093)

**Caso conductor:** Compras Claras
**Pregunta profesional:** **Laura ya sabe qué proceso revisar primero. Antes de asignarlo a un auditor, ¿qué relaciones alrededor de ese proceso necesita ver para comprender su contexto?**

### Producto observable

Al terminar tendrás una **ficha relacional de revisión** con:

1. el proceso que llega desde S5;
2. el contexto de prensa heredado;
3. procesos históricos adjudicados de su entidad;
4. proveedores y otras entidades conectadas cuando el dato lo sostenga;
5. el contraste de H2-R, la hipótesis relacional de hoy (pandas ↔ Neo4j);
6. una decisión de modelado y una alternativa descartada;
7. un límite concreto;
8. `s06_contexto_procesos.jsonl`, entrada de la siguiente sesión.
'''),
        code('''
tu_prediccion = input("Antes de leer la respuesta: ¿qué tipo de herramienta imaginas que hace falta para ver relaciones entre muchas entidades conectadas? ").strip()
print("Guardaste tu predicción:", tu_prediccion or "(en blanco)")
print("Sigue leyendo para comparar con la respuesta real.")
'''),
        md('''
**Respuesta corta y herramienta:** Laura necesita seguir una cadena de conexiones —entidad → proceso → proveedor → otro proceso → otra entidad— sin perder el hilo en ningún salto. Eso es una pregunta sobre relaciones que se conectan entre sí, y la herramienta que la responde es una **base de datos de grafos: Neo4j**. ¿Tu predicción se parecía? El resto de la sesión explica por qué esa herramienta y no otra de las que ya conoces.

## El hilo del evaluador

```text
S3  evidencia documental
 ↓
S4  persistencia compartida en Atlas
 ↓
S5  qué revisar primero → bandeja operacional + ancla elegida
    H1 (prensa): 0/77 → refutada literalmente
 ↓
S6  qué hay alrededor de lo que Laura va a revisar
    H2-R (relacional): ¿el proveedor más conectado del ancla supera
                        la mediana de sus pares (las candidatas de S5)?
```
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
| 1. Recuperar el ancla | 🧠 ENTIENDE | ¿qué proceso llega desde S5? | Colab + JSON de S5 | proceso + entidad + prensa |
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
- ✏️ **MODIFICA/DECIDE:** cambia el dato señalado, predice, o responde antes de ver el resultado.

**Diferencia con la versión original de S6:** aquí casi todos los bloques mezclan 🧠 y ✏️ en la misma frase — la idea es que nunca leas dos conceptos seguidos sin hacer algo entre medio.
'''),
        md('''
---
## 1. Recuperar el proceso que Laura abrió en S5

S5 dejó `s05_ancla_s06.json`. Súbelo al panel **Archivos** de Colab y escribe su ruta. Si lo perdiste, la clase no se bloquea: el dataset trae una **ancla pedagógica real** con historial útil.

**OJO.** El respaldo permite aprender Neo4j, pero el hito declara que no se usó el archivo propio.
'''),
        code(f"""
import json
import urllib.request
from pathlib import Path
import pandas as pd

DATA_URL = {DATA!r}
MANIFEST_URL = {MANIFEST!r}

datos = pd.read_csv(DATA_URL, low_memory=False)
with urllib.request.urlopen(MANIFEST_URL) as r:
    manifest = json.loads(r.read().decode("utf-8"))

ruta = input("Ruta de s05_ancla_s06.json (Enter = respaldo): ").strip()
if ruta and Path(ruta).is_file():
    ancla_original = json.loads(Path(ruta).read_text(encoding="utf-8"))
    origen_ancla = "archivo propio S5"
else:
    ancla_original = dict(manifest["ancla_pedagogica"])
    origen_ancla = "ancla pedagógica versionada"

print("Origen:", origen_ancla)
print(json.dumps(ancla_original, ensure_ascii=False, indent=2))
print("Filas disponibles:", len(datos))
"""),
        md('''
### Cómo se lee la entrada

**Cómo se lee.** El ancla identifica un proceso que ya sobrevivió a la regla de S5. El extracto histórico añade hechos adjudicados sin cambiar por qué ese proceso fue priorizado.

**Qué nos dice.** S6 continúa una decisión ya tomada.

**Qué NO permite concluir todavía.** Tener historial contractual no significa que exista una relación problemática.

**Error frecuente.** Volver a construir los 77 candidatos. Eso repetiría S5.
'''),
        md('''
---
## 2. H2-R: la hipótesis relacional de esta sesión

S5 cerró con una hipótesis de prensa: **H1** — ¿aparece literalmente alguno de los 77 IDs de proceso en título o subtítulo de una noticia? El resultado fue `0/77`: **H1 literal refutada**, y la prensa quedó especificada como contexto de entidad, no como evidencia directa de un proceso.

S6 abre una hipótesis distinta, ahora relacional:

> **H2-R.** El proveedor histórico más conectado de la entidad del proceso elegido en S5 está conectado con más entidades que la mediana de esa misma conexión entre las 32 entidades candidatas de S5 que sí tienen historial.

No es una prueba estadística inferencial: es una comparación empírica y falsable sobre este extracto.
'''),
        code('''
tu_prediccion_proveedor = input("Antes de ver el ejemplo: ¿qué tipo de proveedor esperarías que conecte a dos entidades DIFERENTES? (una palabra o frase corta) ").strip()
print("Guardaste:", tu_prediccion_proveedor or "(en blanco)")
'''),
        md('''
### Ejemplo manual pequeño (nombres inventados, para pensar antes de programar)

```text
Alcaldía de Ejemplo ──PUBLICA──> Proceso 2024-001 ──ADJUDICADO_A──> Constructora Ejemplo S.A.S.
                                                                              ▲
Gobernación de Prueba ──PUBLICA──> Proceso 2023-045 ──ADJUDICADO_A───────────┘
```

Mirando solo este dibujo, sin ninguna tabla: **Constructora Ejemplo S.A.S. aparece conectada con dos entidades distintas** —la Alcaldía de Ejemplo y la Gobernación de Prueba— a través de dos procesos separados. Compara con lo que acabas de predecir: Constructora Ejemplo es justo el tipo de proveedor que la hipótesis busca — uno adjudicado por más de una entidad.

El proceso candidato que trae S5 puede no estar adjudicado todavía: **no le inventamos un proveedor**. El historial adjudicado —procesos ya cerrados de la misma entidad— es lo que sí aporta proveedores reales y conexiones observadas.
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
nit_deseado = str(ancla_original.get("nit_entidad", "")).strip()
hist = datos[datos["tipo_registro"].eq("historico_adjudicado")].copy()
hist_ancla = hist[hist["nit_entidad"].astype(str).str.strip().eq(nit_deseado)]

if hist_ancla.empty:
    print("Tu ancla no tiene historial suficiente en este extracto. Usamos respaldo pedagógico.")
    ancla_trabajo = dict(manifest["ancla_pedagogica"])
    nit_deseado = str(ancla_trabajo["nit_entidad"]).strip()
    hist_ancla = hist[hist["nit_entidad"].astype(str).str.strip().eq(nit_deseado)]
    uso_respaldo_s06 = True
else:
    ancla_trabajo = ancla_original
    uso_respaldo_s06 = origen_ancla != "archivo propio S5"

print("Entidad de trabajo:", ancla_trabajo["entidad"])
print("Procesos históricos:", hist_ancla["id_proceso"].nunique())
print("Proveedores distintos:", hist_ancla["nit_proveedor"].nunique())
"""),
        md('''
### Interpretación del contexto histórico

**Cómo se lee.** Los conteos corresponden al historial adjudicado disponible para la entidad de trabajo, no al proceso candidato aislado.

**Qué nos dice.** Hay material relacional suficiente para preguntar por proveedores y conexiones entre procesos.

**Qué NO permite concluir todavía.** Más procesos o proveedores no equivalen a mayor riesgo. Faltan criterios sobre competencia, temporalidad y comportamiento esperado de la entidad.

**Error frecuente.** Usar el número de contratos como una puntuación de sospecha.
'''),
        question_cell(3, "Modelo", "Acabas de ver que tu entidad puede tener historial sin que el proceso candidato de S5 esté adjudicado. ¿Por qué el candidato no necesita todavía una relación hacia un proveedor?", [
            "Porque Neo4j no soporta proveedores en procesos recientes.",
            "Porque puede no estar adjudicado; sirve como ancla y el historial aporta proveedores reales.",
            "Porque los proveedores pertenecen a Elasticsearch.",
        ], 1, [
            "Neo4j sí soporta esa relación; el límite está en la evidencia.",
            "Exacto. No fabricamos una relación que el dato no sostiene.",
            "Elasticsearch resolverá otra pregunta: búsqueda textual y relevancia.",
        ]),
        md('''
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
'''),
        code('''
respuesta_variable = input("En (v:Proveedor {nit:'900123456'}), ¿qué letra es la VARIABLE con la que nombras el nodo? ").strip()
respuesta_label = input("¿Qué palabra es el LABEL (la categoría)? ").strip()
respuesta_propiedad = input("¿Qué par clave:valor es la PROPIEDAD? ").strip()

print("Tus respuestas:", {"variable": respuesta_variable, "label": respuesta_label, "propiedad": respuesta_propiedad})
print("Compara: variable = v | label = Proveedor | propiedad = nit:'900123456'")
print("Con eso ya puedes leer un patrón completo: (e:Entidad)-[:PUBLICA]->(p:Proceso) es 'un nodo Entidad conectado, mediante la relación PUBLICA, a un nodo Proceso'.")
'''),
        md('''
### EJERCICIO S06-PATRON — un solo hueco

Completa **solo** el nombre de la relación entre un proceso histórico y el proveedor al que fue adjudicado.

**Qué debe verse si salió bien:** `(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor)`.
**Error probable:** dejar `____` o inventar un verbo que no representa el hecho del dato.
**Qué significa:** el modelo aún no expresa la semántica contractual que luego recorrerá `MATCH`.

<details><summary><strong>Recuperación si te atascaste</strong></summary>
La relación se llama <code>ADJUDICADO_A</code>. Cámbiala y vuelve a ejecutar.
</details>
'''),
        code("""
RELACION_PROCESO_PROVEEDOR = "____"  # reemplaza únicamente ____
patron_estudiante = f"(p:Proceso)-[:{RELACION_PROCESO_PROVEEDOR}]->(v:Proveedor)"
print(patron_estudiante)

if RELACION_PROCESO_PROVEEDOR != "ADJUDICADO_A":
    raise ValueError("Revisa el hecho contractual que conecta Proceso con Proveedor.")
print("Patrón correcto: la relación expresa una adjudicación observada.")
"""),
        md('''
### Modelo mínimo que usaremos

```text
(e:Entidad)-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor)
```

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
| Proceso como propiedad de una relación directa | `(e:Entidad)-[:CONTRATO {id_proceso:"...", valor:...}]->(v:Proveedor)` | más simple, pero un proceso deja de ser algo que puedas recorrer o conectar con otra cosa por sí mismo |
'''),
        code('''
mi_eleccion_modelo = input("Antes de seguir: ¿tú cuál elegirías, 'nodo' o 'propiedad'? ").strip().lower()
print("Anotado:", mi_eleccion_modelo)
print("Compara: este cuaderno eligió 'nodo' porque Proceso participa en caminos propios y S7 reutilizará su texto.")
'''),
        md('''
### Función usada: `MERGE`

- **Para qué sirve:** encuentra un nodo o relación que ya existe con esa identidad, o lo crea si no existe — nunca lo duplica.
- **Por qué aparece:** el runtime de Colab se reinicia solo, y el receso pasa a mitad de sesión. Sin `MERGE`, volver a ejecutar la carga crearía un segundo `Proceso 2024-001` idéntico al primero.
- **Intuición en palabras:** es como decir “busca esta persona por su cédula; si no está, regístrala — pero nunca la registres dos veces”.
- **Error frecuente:** usar `CREATE` en su lugar y terminar con varios nodos duplicados del mismo proceso.
'''),
        code('''
prediccion_merge = input('Si ejecutas MERGE (p:Proceso {id:"X"}) dos veces seguidas, ¿cuántos nodos Proceso con id "X" existirán al final: 1 o 2? ').strip()
print("Tu predicción:", prediccion_merge, "— la comprobamos más adelante, cuando carguemos el grafo de verdad.")
'''),
        md('''
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

Antes de usar Neo4j calculamos qué proveedores de la entidad ancla también aparecen en otras entidades del extracto. Luego exigiremos a Neo4j la misma respuesta.
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
if uso_respaldo_s06 or esperado_pd.empty:
    desenlace_h2r_pd = "no evaluable con mi ancla"
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

**Cómo se lee.** `procesos_con_entidad` cuenta procesos adjudicados de la entidad ancla; `entidades_conectadas` cuenta entidades distintas asociadas al mismo NIT de proveedor. El desenlace H2-R compara tu máximo contra la mediana de esa misma métrica entre las 32 entidades candidatas de S5 que tienen historial.

**Qué nos dice.** Ya sabemos qué salida debería reproducir el grafo, y ya tenemos un desenlace declarado para H2-R con tu propio ancla.

**Qué NO permite concluir todavía.** Repetición o conectividad no equivale a favorecimiento, colusión ni irregularidad.

**Error frecuente.** Llamar “sospechoso” al proveedor que queda primero, o llamar “aceptada”/“rechazada” al desenlace de H2-R.
'''),
        md('''
### RECUPERACIÓN S06 — si Colab reinició antes de Aura

Ejecuta la siguiente celda siempre que vuelvas del receso. Si el estado sigue vivo, solo lo confirma. Si se perdió, reconstruye datos, ancla de trabajo, historial y contrato pandas.
'''),
        hidden(code(f"""
# RECUPERACIÓN S06
if "pregunta_codificada" not in globals() or "tutorial" not in globals():
    exec({INTERACTIVITY!r})

estado_necesario = ["datos", "manifest", "ancla_original", "hist", "hist_ancla", "ancla_trabajo", "esperado_pd", "nit_deseado", "desenlace_h2r_pd"]
if not all(nombre in globals() for nombre in estado_necesario):
    import json, urllib.request
    from pathlib import Path
    import pandas as pd

    DATA_URL = {DATA!r}
    MANIFEST_URL = {MANIFEST!r}
    datos = pd.read_csv(DATA_URL, low_memory=False)
    with urllib.request.urlopen(MANIFEST_URL) as r:
        manifest = json.loads(r.read().decode("utf-8"))

    ruta_recuperacion = input("Ruta de s05_ancla_s06.json (Enter = respaldo): ").strip()
    if ruta_recuperacion and Path(ruta_recuperacion).is_file():
        ancla_original = json.loads(Path(ruta_recuperacion).read_text(encoding="utf-8"))
        origen_ancla = "archivo propio S5"
    else:
        ancla_original = dict(manifest["ancla_pedagogica"])
        origen_ancla = "ancla pedagógica versionada"

    nit_deseado = str(ancla_original.get("nit_entidad", "")).strip()
    hist = datos[datos["tipo_registro"].eq("historico_adjudicado")].copy()
    hist_ancla = hist[hist["nit_entidad"].astype(str).str.strip().eq(nit_deseado)]
    if hist_ancla.empty:
        ancla_trabajo = dict(manifest["ancla_pedagogica"])
        nit_deseado = str(ancla_trabajo["nit_entidad"]).strip()
        hist_ancla = hist[hist["nit_entidad"].astype(str).str.strip().eq(nit_deseado)]
        uso_respaldo_s06 = True
    else:
        ancla_trabajo = ancla_original
        uso_respaldo_s06 = origen_ancla != "archivo propio S5"

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
    if uso_respaldo_s06 or esperado_pd.empty:
        desenlace_h2r_pd = "no evaluable con mi ancla"
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
'''),
        code('''
prediccion_unwind = input("Si UNWIND recibe una lista de 2109 filas, ¿la consulta se ejecuta 1 vez o 2109 veces (una por fila)? ").strip()
print("Tu predicción:", prediccion_unwind, "— la comprobamos en la carga que sigue.")
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
print()
print("Vuelve a ejecutar esta celda: si predijiste que MERGE no duplicaría nodos, verás que 'Carga lista' reporta el mismo número de filas otra vez, no el doble.")
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
cols_cmp = ["nit_proveedor", "procesos_con_entidad", "entidades_conectadas"]
pd_cmp = esperado_pd[cols_cmp].copy()
neo_cmp = neo_df[cols_cmp].copy()
pd_cmp["nit_proveedor"] = pd_cmp["nit_proveedor"].astype(str)
neo_cmp["nit_proveedor"] = neo_cmp["nit_proveedor"].astype(str)
coinciden = pd_cmp.reset_index(drop=True).equals(neo_cmp.reset_index(drop=True))
print("pandas == Neo4j:", coinciden)
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
## Demostración guiada — el vecindario más rico del extracto

**Demostración guiada; no es tu evidencia individual.** Antes de trabajar con tu propio resultado, vas a ver dibujado — con nodos y flechas de verdad, en Aura — el vecindario más conectado de todo el extracto.
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
        md('''
**Cómo se lee.** Cada fila es un proveedor de la entidad más conectada del extracto, ordenado por cuántas otras entidades también lo adjudicaron.

**Qué nos dice.** Esta demostración usa deliberadamente la entidad más rica en relaciones.

**Qué NO permite concluir todavía.** Esta demostración usa la ancla pedagógica, no la tuya. Tu propio resultado puede ser más modesto y sigue siendo una respuesta válida a H2-R.

**Error frecuente.** Pensar que tu propia ancla “debería” verse igual de conectada que esta demostración.
'''),
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
**HAZ ESTO AHORA.** Copia la consulta que acabas de imprimir, ve a tu instancia AuraDB → pestaña **Query** (no Colab), pégala y ejecútala ahí. Aura dibuja nodos y flechas automáticamente cuando devuelves caminos (`RETURN camino`).

**OJO.** El grafo muestra hasta 8 de las entidades conectadas con este proveedor — se acota para que se pueda leer, no porque las demás no existan.

### Antes de seguir, dos preguntas para el salón

1. En el grafo que acabas de ver, ¿cuál es el nodo puente entre las distintas entidades?
2. ¿Qué representa cada camino que dibujó Aura, y qué NO demuestra por sí solo?

**PARA LLEVAR.** Más conexiones no es lo mismo que una conexión anómala.
'''),
        md('''
---
## 8. CRUD seguro y tu propio vecindario

Ya viste, en la demostración guiada, el grafo más rico posible del extracto. Ahora repites el ejercicio con **tu propio resultado** de la sección 7.

El CRUD usa `S06-DEMO`; no modificamos un proceso real. Después eliges uno de los **5 proveedores con más entidades conectadas** de tu propio resultado (o todos los disponibles, si tu tabla tiene menos de 5) y abres su vecindario.
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
print("  Procesos con mi entidad:", int(proveedor_elegido["procesos_con_entidad"]))
print("  Entidades conectadas:", int(proveedor_elegido["entidades_conectadas"]))
print("  Procesos visibles en el vecindario:", len(vecindario_df))
vecindario_df
"""),
        md('''
### Interpretación de tu vecindario

**Cómo se lee.** Cada fila es un proceso conectado al proveedor que elegiste; una misma entidad puede aportar varios procesos. Este vecindario es, literalmente, la evidencia visual del desenlace de H2-R que vas a declarar enseguida.

**Qué nos dice.** Puedes observar qué entidades y procesos del extracto comparten ese actor contractual y abrir casos concretos para revisión.

**Qué NO permite concluir todavía.** Compartir proveedor no demuestra coordinación, favorecimiento ni irregularidad.

**Error frecuente.** Convertir el número de conexiones en un “score de riesgo” sin modelo ni denominador.
'''),
        md('''
### La evidencia no termina en el grafo

Ahora registra dos decisiones que una respuesta genérica no puede inventar por ti:

1. un límite que nombre **qué dato faltaría** antes de una afirmación de riesgo/irregularidad;
2. una alternativa de modelado que descartaste y por qué.
'''),
        code("""
if uso_respaldo_s06 or neo_df.empty:
    desenlace_h2r_neo = "no evaluable con mi ancla"
elif neo_df["entidades_conectadas"].max() > MEDIANA_H2R:
    desenlace_h2r_neo = "conexión más fuerte que la mediana de las candidatas de S5"
else:
    desenlace_h2r_neo = "conexión igual o menor que la mediana de las candidatas de S5"

assert desenlace_h2r_neo == desenlace_h2r_pd, "El desenlace H2-R debería coincidir: ya vimos pandas == Neo4j."
print("Desenlace H2-R (Neo4j):", desenlace_h2r_neo)
"""),
        code("""
from pathlib import Path
limite_estudiante = input("Límite concreto y dato faltante: ").strip()
alternativa_modelo = input("Alternativa de modelado descartada: ").strip()
razon_alternativa = input("¿Por qué la descartaste para esta pregunta?: ").strip()

if len(limite_estudiante) < 25:
    raise ValueError("Nombra la conclusión que no puedes sostener y el dato que falta.")
if len(alternativa_modelo) < 5 or len(razon_alternativa) < 15:
    raise ValueError("Nombra una alternativa real y explica por qué no sirve igual de bien para esta pregunta.")

export = vecindario_df.merge(
    datos[["id_proceso", "descripcion", "modalidad", "url_secop"]].drop_duplicates("id_proceso"),
    left_on="proceso", right_on="id_proceso", how="left"
)
export.to_json("s06_contexto_procesos.jsonl", orient="records", lines=True, force_ascii=False)

hito = f'''# Hito S06 (alterna) — Ficha relacional de revisión\n\n- Origen del ancla: {origen_ancla}\n- Proceso elegido en S5: {ancla_original.get("id_proceso", "")}\n- Proceso/entidad usados para el grafo: {ancla_trabajo.get("id_proceso", "")} — {ancla_trabajo.get("entidad", "")}\n- Noticias / nivel: {ancla_trabajo.get("noticias_entidad", "")} / {ancla_trabajo.get("nivel_menciones", "")}\n- Respaldo pedagógico: {uso_respaldo_s06}\n- H1 (S5): 0/77 → refutada literalmente\n- H2-R (S6), desenlace pandas: {desenlace_h2r_pd}\n- H2-R (S6), desenlace Neo4j: {desenlace_h2r_neo}\n- pandas == Neo4j: {coinciden}\n- Proveedor elegido: {proveedor_elegido["proveedor"]}\n- Entidades conectadas: {int(proveedor_elegido["entidades_conectadas"])}\n- Procesos en el vecindario: {len(vecindario_df)}\n\n## Límite\n{limite_estudiante}\n\n## Decisión de modelado\nProceso se modeló como nodo porque participa en caminos y su texto será reutilizado en la siguiente sesión.\n\n### Alternativa descartada\n{alternativa_modelo}\n\nRazón: {razon_alternativa}\n'''
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
| Continuidad | identifica proceso S5 y declara respaldo | solo entidad | no conecta con S5 | 15 |
| Modelo | justifica nodos/relaciones + alternativa descartada | describe sin alternativa | copia el patrón | 20 |
| Ejecución | vecindario propio ejecutado | solo consulta común | no hay salida | 20 |
| Verificación | `pandas == Neo4j` comprobado | muestra ambos | solo uno | 15 |
| Evidencia propia | proveedor + entidades + procesos + desenlace H2-R declarado | incompleta | genérica | 15 |
| Límite | conclusión inválida + dato específico faltante | genérico | afirma irregularidad | 15 |

Las autoevaluaciones y las predicciones son formativas. El hito es la evidencia revisable de la sesión.
'''),
        md('''
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

Entidad -PUBLICA-> Proceso -ADJUDICADO_A-> Proveedor
```

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
