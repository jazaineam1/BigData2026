#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera S6: contexto relacional del proceso priorizado por Laura.

La sesión parte del producto de S5 (`s05_ancla_s06.json`). Neo4j aparece porque
Laura ya sabe qué revisar primero, pero necesita ver las relaciones alrededor del
proceso antes de asignarlo a un auditor.

Plataforma gestionada verificada: Neo4j AuraDB Free, 30-08-2026.
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


def hidden(cell, title: str):
    cell["source"] = [f'#@title {title} {{ display-mode: "form" }}\n'] + cell["source"]
    cell["metadata"] = {
        "tags": ["hide-input"], "jupyter": {"source_hidden": True},
        "cellView": "form", "colab": {"formView": "both"},
    }
    return cell


def question_cell(numero: int, tema: str, pregunta: str, opciones: list[str], correcta: int, retro: list[str]):
    payload = base64.b64encode(json.dumps({
        "numero": numero, "tema": tema, "pregunta": pregunta,
        "opciones": opciones, "correcta": correcta, "retro": retro,
    }, ensure_ascii=False).encode("utf-8")).decode("ascii")
    return hidden(code(f'pregunta_codificada("{payload}")'), f"Autoevaluación {numero} — {tema}")


def build_cells():
    cells = [
        md(f'''<a href="{COLAB}" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Abrir S6 en Colab"></a>\n\n**Acceso público:** [página del curso]({WEB}/)'''),
        md('''
# Sesión 6 — De la fila priorizada al contexto relacional con Neo4j

## Universidad Central
> ### Facultad de Ingeniería y Ciencias Básicas
> ### Maestría en Analítica de Datos — BIG DATA (64491093)

**Caso conductor:** Compras Claras  
**Pregunta profesional:** **Laura ya sabe qué proceso revisar primero. Antes de asignarlo a un auditor, ¿qué relaciones alrededor de ese proceso necesita ver para comprender su contexto?**

### Producto observable

Al terminar tendrás una **ficha relacional de revisión** que contiene:

1. el proceso que llega desde la bandeja operacional de S5;
2. el contexto de prensa heredado (`noticias_entidad`, `nivel_menciones`);
3. procesos históricos adjudicados de la entidad;
4. proveedores vinculados y, cuando existan, otras entidades conectadas a esos proveedores;
5. una comprobación pandas ↔ Neo4j sobre el mismo patrón;
6. una interpretación y un límite explícito;
7. `s06_contexto_procesos.jsonl`, que será la entrada textual de la siguiente sesión.
'''),
        md('''
## El hilo del evaluador hasta hoy

```text
S3  evidencia documental: ¿qué se está diciendo sobre las entidades?
 ↓
S4  persistencia compartida: las colecciones viven en Atlas
 ↓
S5  triage operacional: ¿qué revisa Laura primero? → 77 candidatos
 ↓
S6  contexto relacional: ¿qué hay alrededor del proceso que Laura abrió?
```

**PARA LLEVAR.** Neo4j no aparece porque “toca grafos”. Aparece porque la nueva pregunta ya no es solo por una fila: la relación entre actores forma parte de la respuesta.
'''),
        md('''
## Mapa de la sesión

| Bloque | Pregunta | Qué queda |
|---|---|---|
| 1. Recuperar el ancla | ¿qué proceso llega desde S5? | proceso + entidad + contexto de prensa |
| 2. Preparar el vecindario | ¿qué datos históricos rodean esa entidad? | tabla relacional de contraste |
| 3. Diseñar el grafo | ¿qué debe ser nodo y qué relación? | Entidad → Proceso → Proveedor |
| 4. Contrato pandas | ¿qué debería responder el grafo? | resultado esperado |
| 5. AuraDB | ¿cómo levantamos el servicio? | instancia + conexión |
| 6. Cargar y consultar | ¿cómo se expresa la relación en Cypher? | grafo + MATCH |
| 7. Verificar | ¿Neo4j conserva la misma respuesta? | pandas = Neo4j |
| 8. Hito y puente | ¿qué puede sostener Laura y qué falta? | ficha + export textual |
'''),
        hidden(code('''
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
    display(HTML(f'''<div style="border:2px solid #175c3c;background:#f4faf6;color:#172019;border-radius:12px;padding:15px;margin:14px 0">
    <strong>Pregunta {p['numero']} · {html_lib.escape(p['tema'])}</strong><p>{html_lib.escape(p['pregunta'])}</p>{opts}
    <button onclick="(function(){{const e=document.querySelector('input[name={uid}]:checked');const s=document.getElementById('r-{uid}');if(!e){{s.textContent='Selecciona una opción.';return;}}const i=Number(e.value),r={retro};const ok=i==={p['correcta']};s.innerHTML='<div style=&quot;margin-top:8px;padding:8px;border-radius:7px;background:'+(ok?'#d1e7dd;color:#0f5132':'#f8d7da;color:#842029')+'&quot;><strong>'+(ok?'Correcto. ':'Revisa. ')+'</strong>'+r[i]+'</div>';}})()" style="background:#175c3c;color:white;border:0;border-radius:7px;padding:8px 12px">Verificar</button>
    <div id="r-{uid}" aria-live="polite"></div></div>'''))

def tutorial(url, alto=720):
    display(HTML(f'<iframe src="{url}?embed=1" width="100%" height="{alto}" style="border:0;border-radius:10px;background:#faf7ef"></iframe><p><a href="{url}" target="_blank">Abrir tutorial en pantalla completa ↗</a></p>'))

print("Soporte S6 listo.")
'''), "Preparar interactividad"),
        md('''
---
## 1. Recuperar el proceso que Laura abrió en S5

S5 dejó `s05_ancla_s06.json`. Si lo conservas, súbelo al panel **Archivos** de Colab y escribe su ruta en la celda. Si no lo tienes, la sesión no se bloquea: el dataset trae una **ancla pedagógica real** escogida por tener historial útil.

**OJO.** Usar la ancla pedagógica permite aprender Neo4j, pero en el hito debes declarar si no trabajaste con tu propio archivo S5.
'''),
        code(f'''
import json
from pathlib import Path
import pandas as pd

DATA_URL = {DATA!r}
MANIFEST_URL = {MANIFEST!r}

datos = pd.read_csv(DATA_URL, low_memory=False)
manifest = pd.read_json(MANIFEST_URL, typ="series").to_dict()

ruta = input("Ruta de s05_ancla_s06.json (Enter = usar ancla pedagógica): ").strip()
if ruta and Path(ruta).is_file():
    ancla_original = json.loads(Path(ruta).read_text(encoding="utf-8"))
    origen_ancla = "archivo propio S5"
else:
    ancla_original = dict(manifest["ancla_pedagogica"])
    origen_ancla = "ancla pedagógica versionada"

print("Origen:", origen_ancla)
print(json.dumps(ancla_original, ensure_ascii=False, indent=2))
print("Filas de contexto disponibles:", len(datos))
'''),
        md('''
### Cómo leer la entrada

**Cómo se lee.** El ancla identifica un proceso que ya sobrevivió a la regla S5. El archivo relacional añade registros históricos adjudicados sin cambiar por qué ese proceso fue priorizado.

**Qué nos dice.** S6 parte de una decisión ya tomada y busca contexto alrededor de ella.

**Qué NO permite concluir todavía.** Tener historial contractual no significa que haya una relación problemática; aún no hemos definido qué patrón observar.

**Error frecuente.** Volver a filtrar los 1.000 procesos. Eso repetiría S5 en vez de continuarla.
'''),
        md('''
---
## 2. El candidato y el historial cumplen funciones distintas

El candidato S5 puede no tener proveedor adjudicado. No lo inventamos.

```text
                    ┌─ Proceso histórico ─→ Proveedor A
                    │
Proceso candidato ← Entidad
                    │
                    └─ Proceso histórico ─→ Proveedor B ─← otra Entidad
```

- **Proceso candidato:** explica por qué Laura abrió esta entidad hoy.
- **Proceso histórico adjudicado:** aporta relaciones contractuales observadas.
- **Otra entidad:** aparece solo si comparte un proveedor real del historial.
'''),
        question_cell(1, "Modelo", "¿Por qué el candidato de S5 no necesita una relación ADJUDICADO_A?", [
            "Porque Neo4j no soporta proveedores en procesos nuevos.",
            "Porque el candidato puede no estar adjudicado; sirve como ancla y el historial aporta proveedores reales.",
            "Porque los proveedores solo se modelan en Elasticsearch.",
        ], 1, [
            "Neo4j sí puede modelar proveedores; el problema es la evidencia disponible.",
            "Exacto: no fabricamos una relación que el dato todavía no sostiene.",
            "Elasticsearch no reemplaza las relaciones contractuales del grafo.",
        ]),
        code('''
# Recuperación automática: si tu ancla no tiene historial suficiente,
# usamos la ancla pedagógica y conservamos la tuya como evidencia del límite.
nit_deseado = str(ancla_original.get("nit_entidad", "")).strip()
hist = datos[datos["tipo_registro"].eq("historico_adjudicado")].copy()

hist_ancla = hist[hist["nit_entidad"].astype(str).str.strip().eq(nit_deseado)]
if hist_ancla.empty:
    print("Tu ancla no tiene historial adjudicado suficiente en el extracto.")
    ancla_trabajo = dict(manifest["ancla_pedagogica"])
    nit_deseado = str(ancla_trabajo["nit_entidad"]).strip()
    hist_ancla = hist[hist["nit_entidad"].astype(str).str.strip().eq(nit_deseado)]
    uso_respaldo_s06 = True
else:
    ancla_trabajo = ancla_original
    uso_respaldo_s06 = False

print("Entidad de trabajo:", ancla_trabajo["entidad"])
print("Procesos históricos adjudicados:", hist_ancla["id_proceso"].nunique())
print("Proveedores distintos:", hist_ancla["nit_proveedor"].nunique())
'''),
        md('''
---
## 3. Diseñar el grafo antes de escribir Cypher

Modelo mínimo:

```text
(e:Entidad)-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor)
```

| Elemento | Identificador | Por qué es nodo/relación |
|---|---|---|
| `Entidad` | NIT | actor que publica procesos |
| `Proceso` | `id_proceso` | tiene texto, valor, modalidad y será reutilizado en búsqueda |
| `Proveedor` | NIT | actor adjudicado que puede conectar procesos/entidades |
| `PUBLICA` | relación | expresa quién publica el proceso |
| `ADJUDICADO_A` | relación | expresa a quién fue adjudicado un proceso histórico |

**Decisión de diseño.** `Proceso` queda como nodo, no como simple propiedad, porque necesitamos recorrerlo hoy y reutilizar su nombre/descripción en la siguiente sesión.
'''),
        md('''
### Cypher mínimo de hoy

| Construcción | Para qué sirve | Error frecuente |
|---|---|---|
| `MERGE` | encuentra o crea un patrón | creer que siempre crea otro nodo |
| `MATCH` | busca patrones existentes | leerlo como un `SELECT *` sin relaciones |
| `WHERE` | filtra el patrón | usarlo antes de saber qué se está conectando |
| `WITH` | encadena una etapa con la siguiente | olvidar qué variables siguen disponibles |
| `RETURN` | define la salida | confundir salida con persistencia |
| `ORDER BY` / `LIMIT` | ordena y acota | asumir orden si no lo pediste |

**PARA LLEVAR.** Una flecha en Cypher no es decoración: expresa una relación que debe existir en los datos.
'''),
        question_cell(2, "Cypher", "¿Por qué la carga principal usa MERGE y no CREATE para cada nodo?", [
            "Porque MERGE permite repetir la carga sin fabricar duplicados del mismo identificador.",
            "Porque CREATE no puede crear relaciones.",
            "Porque MERGE convierte automáticamente una tabla en grafo.",
        ], 0, [
            "Sí. Las restricciones únicas refuerzan la misma idea de identidad.",
            "CREATE sí puede crear nodos y relaciones; el problema aquí es la repetibilidad.",
            "El modelo y las relaciones siguen siendo decisiones explícitas.",
        ]),
        md('''
---
## 4. Fijar primero la respuesta esperada con pandas

Antes de abrir Aura, calculamos qué proveedores de la entidad ancla también aparecen en otras entidades del extracto. Ese resultado será el **contrato de corrección** de Neo4j.
'''),
        code('''
# Proveedores usados por la entidad ancla.
prov_ancla = (
    hist_ancla.groupby(["nit_proveedor", "proveedor"], dropna=False)["id_proceso"]
    .nunique().rename("procesos_con_entidad").reset_index()
)

# Cuántas entidades distintas aparecen con cada proveedor en todo el contexto.
prov_global = (
    hist.groupby(["nit_proveedor", "proveedor"], dropna=False)["nit_entidad"]
    .nunique().rename("entidades_conectadas").reset_index()
)

esperado_pd = (
    prov_ancla.merge(prov_global, on=["nit_proveedor", "proveedor"], how="left")
    .sort_values(["entidades_conectadas", "procesos_con_entidad", "nit_proveedor"], ascending=[False, False, True])
    .head(10).reset_index(drop=True)
)

esperado_pd
'''),
        md('''
### Interpretación del contrato pandas

**Cómo se lee.** Cada fila es un proveedor observado en procesos adjudicados de la entidad ancla; `entidades_conectadas` cuenta en cuántas entidades distintas aparece ese mismo NIT dentro del extracto.

**Qué nos dice.** Ya conocemos la respuesta que el grafo debería reproducir después de cargar los mismos hechos.

**Qué NO permite concluir todavía.** Repetición o conexión no equivale a favorecimiento, colusión ni irregularidad. Para sostener algo así faltarían, entre otros, criterios de competencia, temporalidad, propiedad/representación y evidencia del proceso de adjudicación.

**Error frecuente.** Llamar “sospechoso” al proveedor que aparece primero. El orden solo resume conectividad observada.
'''),
        md('''
---
## 5. Tutorial visual — crear/reutilizar AuraDB y obtener la conexión

**HAZ ESTO AHORA.** Sigue el tutorial instrumental. Vuelve al mismo notebook cuando `RETURN 1 AS conexion` funcione en Query y conserves URI, usuario y contraseña.
'''),
        hidden(code(f'tutorial({TUTORIAL!r})'), "Abrir tutorial Neo4j Aura"),
        md('''
### Mini ficha del driver

- **Para qué sirve:** conectar Python con AuraDB.
- **Entradas:** URI, usuario y contraseña de la instancia.
- **Comprobación:** `driver.verify_connectivity()`.
- **Error frecuente:** publicar la contraseña o asumir que un fallo de conexión es un error de Cypher.
'''),
        code('''
!pip install -q "neo4j>=6,<7"

from getpass import getpass
from neo4j import GraphDatabase

URI = input("Connection URI de Aura: ").strip()
USER = input("User name de Aura: ").strip()
PASSWORD = getpass("Password (no se muestra): ")
if not URI or not USER or not PASSWORD:
    raise ValueError("URI, usuario y contraseña son obligatorios.")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
driver.verify_connectivity()
print("Conexión Neo4j verificada.")
'''),
        md('''
---
## 6. Crear identidad antes de cargar relaciones

Las restricciones hacen explícito qué propiedad identifica a cada actor. Se crean antes de `MERGE`.
'''),
        code('''
constraints = [
    "CREATE CONSTRAINT entidad_nit IF NOT EXISTS FOR (e:Entidad) REQUIRE e.nit IS UNIQUE",
    "CREATE CONSTRAINT proceso_id IF NOT EXISTS FOR (p:Proceso) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT proveedor_nit IF NOT EXISTS FOR (v:Proveedor) REQUIRE v.nit IS UNIQUE",
]
for q in constraints:
    driver.execute_query(q)
print("Restricciones listas.")
'''),
        md('''
### Carga idempotente

`UNWIND` convierte la lista enviada desde Python en filas para Cypher. `MERGE` reutiliza los nodos identificados por NIT/ID cuando ya existen.
'''),
        code('''
# Convertimos NaN de pandas a None antes de enviar parámetros.
cols = [
    "tipo_registro", "entidad", "nit_entidad", "departamento_entidad",
    "id_proceso", "referencia", "nombre_proceso", "descripcion", "precio_base",
    "modalidad", "proveedor", "nit_proveedor", "departamento_proveedor",
    "noticias_entidad", "nivel_menciones", "url_secop",
    "es_proceso_candidato_s05", "es_entidad_candidata_s05",
]
rows = datos[cols].where(pd.notna(datos[cols]), None).to_dict("records")

query_base = """
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
"""
driver.execute_query(query_base, filas=rows)

rows_proveedor = [r for r in rows if r.get("nit_proveedor")]
query_proveedor = """
UNWIND $filas AS fila
MATCH (p:Proceso {id: fila.id_proceso})
MERGE (v:Proveedor {nit: toString(fila.nit_proveedor)})
SET v.nombre = fila.proveedor,
    v.departamento = fila.departamento_proveedor
MERGE (p)-[:ADJUDICADO_A]->(v)
"""
driver.execute_query(query_proveedor, filas=rows_proveedor)
print("Carga lista:", len(rows), "procesos/filas de contexto;", len(rows_proveedor), "adjudicaciones.")
'''),
        md('''
### Comprueba que el candidato sigue siendo distinguible

El grafo no borra la historia de S5. El proceso ancla debe conservar `es_candidato_s05 = true` aunque no tenga proveedor.
'''),
        code('''
res = driver.execute_query(
    "MATCH (e:Entidad)-[:PUBLICA]->(p:Proceso {id:$id}) RETURN e.nombre AS entidad, p.id AS proceso, p.es_candidato_s05 AS candidato",
    id=str(ancla_trabajo["id_proceso"]),
)
print([r.data() for r in res.records])
'''),
        md('''
---
## 7. La consulta que justifica el grafo

Buscamos proveedores de la entidad ancla y contamos en cuántas entidades distintas aparece cada uno.
'''),
        code('''
query_contexto = """
MATCH (e:Entidad {nit:$nit})-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor)
WITH v, count(DISTINCT p) AS procesos_con_entidad
MATCH (otra:Entidad)-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v)
RETURN v.nit AS nit_proveedor,
       v.nombre AS proveedor,
       procesos_con_entidad,
       count(DISTINCT otra) AS entidades_conectadas
ORDER BY entidades_conectadas DESC, procesos_con_entidad DESC, nit_proveedor ASC
LIMIT 10
"""
neo = driver.execute_query(query_contexto, nit=nit_deseado)
neo_df = pd.DataFrame([r.data() for r in neo.records])
neo_df
'''),
        code('''
# Contrato de corrección: mismos NIT y métricas, en el mismo orden.
cols_cmp = ["nit_proveedor", "procesos_con_entidad", "entidades_conectadas"]
pd_cmp = esperado_pd[cols_cmp].copy()
pd_cmp["nit_proveedor"] = pd_cmp["nit_proveedor"].astype(str)
neo_cmp = neo_df[cols_cmp].copy()
neo_cmp["nit_proveedor"] = neo_cmp["nit_proveedor"].astype(str)

coinciden = pd_cmp.reset_index(drop=True).equals(neo_cmp.reset_index(drop=True))
print("pandas == Neo4j:", coinciden)
assert coinciden, "Neo4j no reprodujo el contrato pandas; revisa carga, identidad u orden."
'''),
        md('''
### Interpretación pandas ↔ Neo4j

**Cómo se lee.** Comparamos NIT, número de procesos con la entidad ancla y número de entidades conectadas, respetando el mismo orden.

**Qué nos dice.** El grafo cargado reproduce el patrón que calculamos antes con pandas.

**Qué NO permite concluir todavía.** Esta igualdad valida corrección de la respuesta, no demuestra que Neo4j sea más rápido que pandas ni que la conexión tenga relevancia jurídica.

**Error frecuente.** Llamar “benchmark” a una comprobación funcional con un extracto de clase.
'''),
        question_cell(3, "Interpretación", "Un proveedor aparece conectado con cuatro entidades. ¿Qué puede afirmar Laura?", [
            "Que existe una relación contractual observada con procesos de cuatro entidades dentro del extracto.",
            "Que las cuatro entidades coordinaron sus adjudicaciones.",
            "Que el proveedor incurrió en una irregularidad.",
        ], 0, [
            "Correcto. El grafo describe estructura registrada; la interpretación causal requiere otra evidencia.",
            "La conectividad por sí sola no prueba coordinación.",
            "No existe evidencia suficiente para afirmar irregularidad.",
        ]),
        md('''
---
## 8. CRUD seguro con una fila centinela

El CRUD se practica con `S06-DEMO`; nunca modificamos un proceso real del caso.
'''),
        code('''
# CREATE / MERGE
q = """
MERGE (e:Entidad {nit:'S06-E'}) SET e.nombre='Entidad demo'
MERGE (p:Proceso {id:'S06-DEMO'}) SET p.nombre='Proceso demo'
MERGE (v:Proveedor {nit:'S06-V'}) SET v.nombre='Proveedor demo'
MERGE (e)-[:PUBLICA]->(p)
MERGE (p)-[:ADJUDICADO_A]->(v)
"""
driver.execute_query(q)

# READ
r = driver.execute_query("MATCH (e)-[:PUBLICA]->(p:Proceso {id:'S06-DEMO'})-[:ADJUDICADO_A]->(v) RETURN e.nombre,p.id,v.nombre")
print([x.data() for x in r.records])

# UPDATE + verificación
r = driver.execute_query("MATCH (p:Proceso {id:'S06-DEMO'}) SET p.estado_revision='revisado' RETURN p.estado_revision AS estado")
assert r.records[0]["estado"] == "revisado"
print("UPDATE verificado.")

# DELETE de la demo
driver.execute_query("MATCH (n) WHERE n.nit IN ['S06-E','S06-V'] OR n.id='S06-DEMO' DETACH DELETE n")
print("Demo eliminada.")
'''),
        md('''
---
## 9. Evidencia individual — abre un proveedor de tu resultado

Elige un proveedor de `neo_df`. El resultado debe mostrar **qué entidades y procesos producen esa conexión**.
'''),
        code('''
if neo_df.empty:
    raise ValueError("No hay proveedores para elegir en esta ancla.")
print("Elige un proveedor:")
for i, row in neo_df.iterrows():
    print(f"{i+1:>2}. {row['proveedor']} | entidades={row['entidades_conectadas']} | procesos con ancla={row['procesos_con_entidad']}")
sel = int(input("Número: ").strip())
if not 1 <= sel <= len(neo_df):
    raise ValueError("Número fuera de rango")
proveedor_elegido = neo_df.iloc[sel-1]

vec = driver.execute_query("""
MATCH (e:Entidad)-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor {nit:$nit})
RETURN e.nombre AS entidad, p.id AS proceso, p.nombre AS nombre_proceso, p.valor AS valor
ORDER BY entidad, valor DESC
""", nit=str(proveedor_elegido["nit_proveedor"]))
vecindario_df = pd.DataFrame([r.data() for r in vec.records])
vecindario_df
'''),
        md('''
### El límite forma parte de la ficha

Antes de descargar, escribe una frase que responda:

> ¿Qué relación observaste y qué dato adicional necesitarías antes de convertirla en una afirmación de riesgo o irregularidad?

No vale “faltan datos”. Nombra el dato: por ejemplo competencia del proceso, cronología, propietarios/representantes, criterios de adjudicación o universo comparable.
'''),
        code('''
limite_estudiante = input("Límite concreto (incluye el dato que falta): ").strip()
if len(limite_estudiante) < 25:
    raise ValueError("Escribe un límite concreto y nombra el dato faltante.")

# Export textual para S7: procesos del vecindario elegido.
export = vecindario_df.merge(
    datos[["id_proceso", "descripcion", "modalidad", "url_secop"]].drop_duplicates("id_proceso"),
    left_on="proceso", right_on="id_proceso", how="left"
)
export.to_json("s06_contexto_procesos.jsonl", orient="records", lines=True, force_ascii=False)

hito = f'''# Hito S06 — Ficha relacional de revisión\n\n- Origen del ancla: {origen_ancla}\n- Proceso S5: {ancla_original.get("id_proceso", "")}\n- Entidad de trabajo: {ancla_trabajo.get("entidad", "")}\n- Noticias / nivel heredado: {ancla_trabajo.get("noticias_entidad", "")} / {ancla_trabajo.get("nivel_menciones", "")}\n- Se usó respaldo pedagógico: {uso_respaldo_s06}\n- pandas == Neo4j: {coinciden}\n- Proveedor elegido: {proveedor_elegido["proveedor"]}\n- Entidades conectadas: {int(proveedor_elegido["entidades_conectadas"])}\n- Procesos observados en el vecindario: {len(vecindario_df)}\n\n## Límite\n{limite_estudiante}\n\n## Decisión de modelado\nProceso se modeló como nodo porque hoy participa en los caminos y en S7 su texto será recuperable como documento.\n'''
Path("hito_s06_ficha_relacional.md").write_text(hito, encoding="utf-8")
print(hito)

try:
    from google.colab import files
    files.download("hito_s06_ficha_relacional.md")
    files.download("s06_contexto_procesos.jsonl")
except Exception:
    print("Archivos generados en el runtime.")
'''),
        md('''
## Rúbrica del hito S06

| Criterio | Completo | Parcial | Sin evidencia | Peso |
|---|---|---|---|---:|
| Continuidad | identifica proceso/ancla S5 y declara si usó respaldo | menciona solo entidad | no conecta con S5 | 15 |
| Modelo | justifica Entidad–Proceso–Proveedor y por qué Proceso es nodo | describe sin justificar | copia el patrón | 20 |
| Ejecución | muestra consulta propia y vecindario real | solo consulta común | no hay salida | 20 |
| Verificación | `pandas == Neo4j` comprobado | muestra ambos sin comprobar | solo uno | 15 |
| Evidencia individual | proveedor + entidades + procesos propios | resultado incompleto | resultado genérico | 15 |
| Límite | nombra conclusión inválida y dato específico faltante | límite genérico | afirma irregularidad | 15 |

**Total: 100.**
'''),
        md('''
---
## Hoja de trucos S06

```text
MERGE  → encuentra o crea
MATCH  → busca un patrón
WHERE  → filtra
WITH   → pasa resultados a la siguiente etapa
RETURN → define la salida

Entidad -PUBLICA-> Proceso -ADJUDICADO_A-> Proveedor
```

### Lo más importante

Cassandra en S5 organizó datos para una **pregunta repetitiva conocida**. Neo4j en S6 hace que las **relaciones sean parte explícita de la pregunta**.

### Lo que sigue

Laura ya puede abrir un proceso y ver su vecindario. Ahora aparecen nombres y descripciones largas de varios procesos. La siguiente pregunta será:

> **“Entre todos estos procesos, ¿cuáles son más relevantes para lo que estoy investigando cuando escribo una consulta textual?”**

`s06_contexto_procesos.jsonl` será la entrada de esa búsqueda. Ahí aparecerá Elasticsearch/BM25.
'''),
        code('''
try:
    driver.close()
    print("Conexión Neo4j cerrada.")
except Exception:
    pass
'''),
    ]
    return cells


def main():
    cells = build_cells()
    validate(cells)
    save(cells, OUTPUT)
    print(f"[OK] S6 generada con {len(cells)} celdas")


if __name__ == "__main__":
    main()
