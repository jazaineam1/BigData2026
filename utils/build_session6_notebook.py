#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera S6: contexto relacional del proceso priorizado por Laura.

S6 parte del producto de S5 (`s05_ancla_s06.json`). Neo4j aparece porque Laura
ya sabe qué revisar primero, pero necesita entender qué relaciones existen alrededor
del proceso antes de asignarlo a un auditor.

AuraDB y driver oficial verificados contra documentación vigente: 30-08-2026.
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.make_notebook import code, md, save, validate

OUTPUT = "Cuadernos/6_Neo4j_Contexto_Relacional.ipynb"
WEB = "https://jazaineam1.github.io/BigData2026"
RAW = "https://raw.githubusercontent.com/jazaineam1/BigData2026/main"
COLAB = "https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/6_Neo4j_Contexto_Relacional.ipynb"
DATA = f"{RAW}/Datos/s06_contexto_relacional.csv"
MANIFEST = f"{RAW}/Datos/s06_contexto_relacional_manifest.json"
TUTORIAL = f"{WEB}/assets/tutoriales/neo4j-aura-s06-paso-a-paso.html"

INTERACTIVITY = r'''
import base64, json, html as html_lib
from IPython.display import display, HTML

def pregunta_codificada(token):
    p = json.loads(base64.b64decode(token).decode("utf-8"))
    uid = f"s06-p{p['numero']}"
    opts = "".join(
        f'<label style="display:block;margin:8px 0"><input type="radio" name="{uid}" value="{i}"> {html_lib.escape(op)}</label>'
        for i, op in enumerate(p["opciones"])
    )
    retro = json.dumps(p["retro"], ensure_ascii=False)
    box = (
        f'<div style="border:2px solid #175c3c;background:#f4faf6;color:#172019;border-radius:12px;padding:15px;margin:14px 0">'
        f'<strong>Pregunta {p["numero"]} · {html_lib.escape(p["tema"])}</strong>'
        f'<p>{html_lib.escape(p["pregunta"])}</p>{opts}'
        f'<button onclick="(function(){{const e=document.querySelector(\'input[name={uid}]:checked\');'
        f'const s=document.getElementById(\'r-{uid}\');if(!e){{s.textContent=\'Selecciona una opción.\';return;}}'
        f'const i=Number(e.value),r={retro};const ok=i==={p["correcta"]};'
        f's.innerHTML=\'<div style=&quot;margin-top:8px;padding:8px;border-radius:7px;background:#ffffff;color:#172019;border:1px solid #c7d8cd&quot;><strong>\'+(ok?\'Correcto. \':\'Revisa. \')+\'</strong>\'+r[i]+\'</div>\';}})()" '
        f'style="background:#175c3c;color:white;border:0;border-radius:7px;padding:8px 12px">Verificar</button>'
        f'<div id="r-{uid}" aria-live="polite"></div></div>'
    )
    display(HTML(box))

def tutorial(url, alto=720):
    box = f'<iframe src="{url}?embed=1" width="100%" height="{alto}" style="border:0;border-radius:10px;background:#faf7ef"></iframe>'
    box += f'<p><a href="{url}" target="_blank">Abrir tutorial en pantalla completa ↗</a></p>'
    display(HTML(box))

print("Soporte S6 listo.")
'''


def hidden(cell, title: str):
    cell["source"] = [f'#@title {title} {{ display-mode: "form" }}\n'] + cell["source"]
    cell["metadata"] = {
        "tags": ["hide-input"],
        "jupyter": {"source_hidden": True},
        "cellView": "form",
        "colab": {"formView": "both"},
    }
    return cell


def question_cell(numero, tema, pregunta, opciones, correcta, retro):
    payload = base64.b64encode(json.dumps({
        "numero": numero, "tema": tema, "pregunta": pregunta,
        "opciones": opciones, "correcta": correcta, "retro": retro,
    }, ensure_ascii=False).encode("utf-8")).decode("ascii")
    return hidden(code(f'pregunta_codificada("{payload}")'), f"Autoevaluación {numero} — {tema}")


def build_cells():
    return [
        md(f'''<a href="{COLAB}" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Abrir S6 en Colab"></a>\n\n**Acceso público:** [página del curso]({WEB}/)'''),
        md('''
# Sesión 6 — De la fila priorizada al contexto relacional con Neo4j

## Universidad Central
> ### Facultad de Ingeniería y Ciencias Básicas
> ### Maestría en Analítica de Datos — BIG DATA (64491093)

**Caso conductor:** Compras Claras
**Pregunta profesional:** **Laura ya sabe qué proceso revisar primero. Antes de asignarlo a un auditor, ¿qué relaciones alrededor de ese proceso necesita ver para comprender su contexto?**

**Respuesta corta y herramienta:** Laura necesita seguir una cadena de conexiones —entidad → proceso → proveedor → otro proceso → otra entidad— sin perder el hilo en ningún salto. Eso es una pregunta sobre relaciones que se conectan entre sí, y la herramienta que la responde es una **base de datos de grafos: Neo4j**. El resto de la sesión explica por qué esa herramienta y no otra de las que ya conoces.

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
        md('''
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

### Para qué sirve, y para cuál no

| Sirve muy bien para… | No es la herramienta para… |
|---|---|
| preguntas de **varios saltos** entre entidades conectadas (quién comparte proveedor con quién) | agregaciones masivas sobre una pregunta fija y repetida — eso ya lo resolvió Cassandra en S5 |
| explorar el **vecindario** concreto alrededor de un caso | búsqueda de texto libre por relevancia — eso llega en S7 con Elasticsearch |

### Frente a lo que ya conocías

| Motor | Cómo resuelve “cruzar” | Costo de un salto adicional |
|---|---|---|
| MongoDB (`$lookup`) / SQL (`JOIN`) | recalcula el cruce en cada consulta | crece con cada nivel que agregas |
| Cassandra (S5) | evita el cruce: diseña la tabla para una sola pregunta fija | no aplica — esa pregunta no cambia |
| Neo4j (hoy) | guarda la relación como dato y la recorre | un salto más es una flecha más, no un cruce más |

**PARA LLEVAR.** Neo4j no aparece porque “toca grafos”. Aparece porque la pregunta de Laura —qué hay alrededor de este proceso, y alrededor de eso— ya es, literalmente, una pregunta de relaciones.
'''),
        md('''
## Mapa de la sesión

| Bloque | Rol | Pregunta | Herramienta | Qué queda |
|---|---|---|---|---|
| 1. Recuperar el ancla | 🧠 ENTIENDE | ¿qué proceso llega desde S5? | Colab + JSON de S5 | proceso + entidad + prensa |
| 2. Preparar contexto | 🧠 ENTIENDE | ¿qué historial rodea esa entidad? | pandas | tabla de contraste |
| 3. Diseñar | 🧠 ENTIENDE | ¿qué es nodo y qué es relación? | papel + cuaderno | Entidad → Proceso → Proveedor |
| 4. Contrato pandas | ▶️ EJECUTA | ¿qué debe responder el grafo? | pandas | resultado esperado |
| 5. AuraDB | ▶️ EJECUTA | ¿cómo levantamos el servicio? | tutorial + Neo4j Aura | conexión real |
| 6. Cypher | ▶️ EJECUTA | ¿cómo cargamos y recorremos relaciones? | Cypher/Neo4j | grafo consultable |
| 7. Verificar | 🧠 + ▶️ | ¿Neo4j conserva la respuesta? | pandas + Neo4j | pandas = Neo4j |
| 8. Hito | ✏️ MODIFICA | ¿qué puede sostener Laura? | Colab | ficha + límite + export |

### Semáforo de código

- 🧠 **ENTIENDE:** debes poder explicarlo con tus palabras.
- ▶️ **EJECUTA:** corre la celda y verifica la salida; **no necesitas escribirla de memoria**.
- ✏️ **MODIFICA:** cambia únicamente el dato señalado y observa qué ocurre.
'''),
        hidden(code(INTERACTIVITY), "Preparar interactividad"),
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
## H2-R: la hipótesis relacional de esta sesión

S5 cerró con una hipótesis de prensa: **H1** — ¿aparece literalmente alguno de los 77 IDs de proceso en título o subtítulo de una noticia? El resultado fue `0/77`: **H1 literal refutada**, y la prensa quedó especificada como contexto de entidad, no como evidencia directa de un proceso.

S6 abre una hipótesis distinta, ahora relacional:

> **H2-R.** El proveedor histórico más conectado de la entidad del proceso elegido en S5 está conectado con más entidades que la mediana de esa misma conexión entre las 32 entidades candidatas de S5 que sí tienen historial.

No es una prueba estadística inferencial: es una comparación empírica y falsable sobre este extracto — el resultado depende de qué proceso elegiste en S5, y varía de una persona a otra.

| Sabemos (llega de S5) | No sabemos todavía |
|---|---|
| proceso, entidad, valor, modalidad | proveedores históricos de esa entidad |
| contexto de prensa (H1 ya refutada) | otras entidades conectadas por el mismo proveedor |
| que el proceso sobrevivió la regla `1.000→163→77` | caminos relacionales entre entidades |

Lo que sigue, con nombres inventados, es exactamente H2-R en miniatura.
'''),
        md('''
---
## 2. El candidato y el historial cumplen funciones distintas

### Ejemplo manual pequeño (nombres inventados, para pensar antes de programar)

```text
Alcaldía de Ejemplo ──PUBLICA──> Proceso 2024-001 ──ADJUDICADO_A──> Constructora Ejemplo S.A.S.
                                                                              ▲
Gobernación de Prueba ──PUBLICA──> Proceso 2023-045 ──ADJUDICADO_A───────────┘
```

Mirando solo este dibujo, sin ninguna tabla: **Constructora Ejemplo S.A.S. aparece conectada con dos entidades distintas** —la Alcaldía de Ejemplo y la Gobernación de Prueba— a través de dos procesos separados. Verlo así, de un vistazo, es exactamente lo que un grafo deja hacer y una tabla plana no. Esto es H2-R con nombres inventados: Constructora Ejemplo S.A.S. es justo el tipo de proveedor que la hipótesis busca — uno conectado con más de una entidad.

El proceso candidato que trae S5 puede no estar adjudicado todavía: **no le inventamos un proveedor**. El historial adjudicado —procesos ya cerrados de la misma entidad— es lo que sí aporta proveedores reales y conexiones observadas.
'''),
        question_cell(1, "H2-R", "Si Constructora Ejemplo S.A.S. aparece adjudicada tanto por la Alcaldía de Ejemplo como por la Gobernación de Prueba, ¿qué puede afirmarse?", [
            "Que Constructora Ejemplo S.A.S. aparece conectada contractualmente con al menos dos entidades en este extracto.",
            "Que Constructora Ejemplo S.A.S. es sospechosa de irregularidad.",
            "Que las dos entidades coordinaron la adjudicación entre sí.",
        ], 0, [
            "Correcto. Eso es exactamente lo que el grafo describe: una estructura registrada, no una conclusión sobre conducta.",
            "La conectividad por sí sola no prueba irregularidad.",
            "La conectividad por sí sola no prueba coordinación.",
        ]),
        question_cell(2, "Modelo", "¿Por qué el candidato de S5 no necesita todavía una relación hacia un proveedor?", [
            "Porque Neo4j no soporta proveedores en procesos recientes.",
            "Porque puede no estar adjudicado; sirve como ancla y el historial aporta proveedores reales.",
            "Porque los proveedores pertenecen a Elasticsearch.",
        ], 1, [
            "Neo4j sí soporta esa relación; el límite está en la evidencia.",
            "Exacto. No fabricamos una relación que el dato no sostiene.",
            "Elasticsearch resolverá otra pregunta: búsqueda textual y relevancia.",
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

### Cómo se lee `(e:Entidad {nit:"123"})`

- `e` — variable con la que nombras este nodo en el resto de la consulta.
- `Entidad` — el label: la categoría a la que pertenece.
- `{nit:"123"}` — una propiedad que identifica cuál Entidad exactamente.

Con eso ya puedes leer un patrón completo: `(e:Entidad)-[:PUBLICA]->(p:Proceso)` es "un nodo Entidad conectado, mediante la relación PUBLICA, a un nodo Proceso".
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

`Proceso` queda como nodo porque hoy participa en caminos y la siguiente sesión reutilizará su texto.
'''),
        md('''
### Función usada: `MERGE`

- **Para qué sirve:** encuentra un nodo o relación que ya existe con esa identidad, o lo crea si no existe — nunca lo duplica.
- **Por qué aparece:** el runtime de Colab se reinicia solo, y el receso pasa a mitad de sesión. Sin `MERGE`, volver a ejecutar la carga crearía un segundo `Proceso 2024-001` idéntico al primero.
- **Intuición en palabras:** es como decir “busca esta persona por su cédula; si no está, regístrala — pero nunca la registres dos veces”.
- **Ejemplo manual:** `MERGE (p:Proceso {id:"2024-001"})` la primera vez crea el nodo; ejecutado otra vez, lo encuentra y no crea uno nuevo.
- **Cómo se interpreta la salida:** si el número de nodos no crece al repetir la carga, `MERGE` funcionó como esperado.
- **Error frecuente:** usar `CREATE` en su lugar y terminar con varios nodos duplicados del mismo proceso.
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
        question_cell(3, "Cypher", "¿Por qué usaremos MERGE y restricciones únicas?", [
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

**Cómo se lee.** `procesos_con_entidad` cuenta procesos adjudicados de la entidad ancla; `entidades_conectadas` cuenta entidades distintas asociadas al mismo NIT de proveedor. El desenlace H2-R compara tu máximo contra la mediana de esa misma métrica entre las 32 entidades candidatas de S5 que tienen historial — no contra el universo completo de proveedores, que es demasiado disperso para discriminar.

**Qué nos dice.** Ya sabemos qué salida debería reproducir el grafo, y ya tenemos un desenlace declarado para H2-R con tu propio ancla.

**Qué NO permite concluir todavía.** Repetición o conectividad no equivale a favorecimiento, colusión ni irregularidad. Faltarían evidencia sobre competencia, temporalidad, propiedad/representación y criterios de adjudicación.

**Error frecuente.** Llamar “sospechoso” al proveedor que queda primero, o llamar “aceptada”/“rechazada” al desenlace de H2-R — es una comparación descriptiva, no una prueba estadística.
'''),
        md('''
### RECUPERACIÓN S06 — si Colab reinició antes de Aura

Ejecuta la siguiente celda siempre que vuelvas del receso. Si el estado sigue vivo, solo lo confirma. Si se perdió, reconstruye datos, ancla de trabajo, historial y contrato pandas.

**OJO.** Después de un reinicio también se recuperan los helpers de las autoevaluaciones y del tutorial. El respaldo pedagógico queda declarado; no se presenta como evidencia propia de S5.
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

**Qué debe verse:** tres restricciones válidas y una carga que puede repetirse sin multiplicar el mismo NIT/ID.  
**Error probable:** autenticación o conectividad antes de ejecutar Cypher. Eso es un problema instrumental, no un problema del modelo; usa el diagnóstico del tutorial.
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
- **Cómo se interpreta la salida:** cada elemento de la lista produce, como mínimo, un nodo o relación tocado por `MERGE`.
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

La consulta que sigue agrega un tercer salto: desde ese proveedor, vuelve a **todas** las entidades conectadas — eso es justo lo que una tabla plana no muestra de un vistazo.
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
        question_cell(4, "Interpretación", "Un proveedor aparece conectado con cuatro entidades. ¿Qué puede afirmar Laura?", [
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

**Demostración guiada; no es tu evidencia individual.** Antes de trabajar con tu propio resultado, vas a ver dibujado — con nodos y flechas de verdad, en Aura — el vecindario más conectado de todo el extracto: el de la misma entidad que usa el respaldo pedagógico. Sirve para que veas, una vez, en grande, lo que hasta ahora solo viste en tablas.
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

**Qué nos dice.** Esta demostración usa deliberadamente la entidad más rica en relaciones — por eso el grafo que verás enseguida es notorio.

**Qué NO permite concluir todavía.** Esta demostración usa la ancla pedagógica, no la tuya. Tu propio resultado (bloque anterior) puede ser más modesto y sigue siendo una respuesta válida a H2-R.

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

Deberías ver algo con esta forma (representación conceptual, no una captura de Aura):

```text
                     Entidad 2
                         │
                      Proceso
                         │
                         ▼
   Entidad ancla ──Proceso──▶ PROVEEDOR ◀──Proceso── Entidad 3
                         ▲
                      Proceso
                         │
                     Entidad 4   (...hasta 8 entidades)
```

**OJO.** El grafo muestra hasta 8 de las entidades conectadas con este proveedor — se acota para que se pueda leer, no porque las demás no existan.

### Antes de seguir, dos preguntas para el salón

1. En el grafo que acabas de ver, ¿cuál es el nodo puente entre las distintas entidades?
2. ¿Qué representa cada camino que dibujó Aura, y qué NO demuestra por sí solo?

**PARA LLEVAR.** Más conexiones no es lo mismo que una conexión anómala. Un proveedor muy conectado suele ser, sencillamente, uno que opera en un mercado amplio (logística, insumos, papelería…). Para saber si una conexión es inusual haría falta un denominador o un patrón esperado con el que compararla — eso todavía no lo tenemos.
'''),
        md('''
---
## 8. CRUD seguro y tu propio vecindario

Ya viste, en la demostración guiada, el grafo más rico posible del extracto. Ahora repites el ejercicio con **tu propio resultado** de la sección 7 — puede ser más modesto, y eso también es una respuesta válida a H2-R.

El CRUD usa `S06-DEMO`; no modificamos un proceso real. Después eliges uno de los **5 proveedores con más entidades conectadas** de tu propio resultado (o todos los disponibles, si tu tabla tiene menos de 5) y abres su vecindario.

**Qué debe verse:** una tabla con entidades y procesos relacionados con el proveedor elegido.
**Error probable:** escoger un número fuera de las opciones mostradas. Significa que tu decisión no corresponde al resultado ejecutado.
**Recuperación:** vuelve a ejecutar y elige un número de la lista; no inventes un NIT.
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

**Qué NO permite concluir todavía.** Compartir proveedor no demuestra coordinación, favorecimiento ni irregularidad. Faltan, como mínimo, cronología comparable, condiciones de competencia y vínculos de propiedad/representación cuando la hipótesis los requiera.

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

hito = f'''# Hito S06 — Ficha relacional de revisión\n\n- Origen del ancla: {origen_ancla}\n- Proceso elegido en S5: {ancla_original.get("id_proceso", "")}\n- Proceso/entidad usados para el grafo: {ancla_trabajo.get("id_proceso", "")} — {ancla_trabajo.get("entidad", "")}\n- Noticias / nivel: {ancla_trabajo.get("noticias_entidad", "")} / {ancla_trabajo.get("nivel_menciones", "")}\n- Respaldo pedagógico: {uso_respaldo_s06}\n- H1 (S5): 0/77 → refutada literalmente\n- H2-R (S6), desenlace pandas: {desenlace_h2r_pd}\n- H2-R (S6), desenlace Neo4j: {desenlace_h2r_neo}\n- pandas == Neo4j: {coinciden}\n- Proveedor elegido: {proveedor_elegido["proveedor"]}\n- Entidades conectadas: {int(proveedor_elegido["entidades_conectadas"])}\n- Procesos en el vecindario: {len(vecindario_df)}\n\n## Límite\n{limite_estudiante}\n\n## Decisión de modelado\nProceso se modeló como nodo porque participa en caminos y su texto será reutilizado en la siguiente sesión.\n\n### Alternativa descartada\n{alternativa_modelo}\n\nRazón: {razon_alternativa}\n'''
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

Las autoevaluaciones son formativas. El hito es la evidencia revisable de la sesión.
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
    print(f"[OK] S6 generada: {len(cells)} celdas")


if __name__ == "__main__":
    main()
