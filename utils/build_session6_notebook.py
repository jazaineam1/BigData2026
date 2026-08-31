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

### Producto observable

Al terminar tendrás una **ficha relacional de revisión** con:

1. el proceso que llega desde S5;
2. el contexto de prensa heredado;
3. procesos históricos adjudicados de su entidad;
4. proveedores y otras entidades conectadas cuando el dato lo sostenga;
5. una comprobación pandas ↔ Neo4j;
6. un límite concreto;
7. `s06_contexto_procesos.jsonl`, entrada de la siguiente sesión.
'''),
        md('''
## El hilo del evaluador

```text
S3  evidencia documental
 ↓
S4  persistencia compartida en Atlas
 ↓
S5  qué revisar primero → bandeja operacional
 ↓
S6  qué hay alrededor de lo que Laura va a revisar
```

**PARA LLEVAR.** Neo4j no aparece porque “toca grafos”. Aparece porque la relación entre actores ya forma parte de la pregunta.
'''),
        md('''
## Mapa de la sesión

| Bloque | Pregunta | Qué queda |
|---|---|---|
| 1. Recuperar el ancla | ¿qué proceso llega desde S5? | proceso + entidad + prensa |
| 2. Preparar contexto | ¿qué historial rodea esa entidad? | tabla de contraste |
| 3. Diseñar | ¿qué es nodo y qué es relación? | Entidad → Proceso → Proveedor |
| 4. Contrato pandas | ¿qué debe responder el grafo? | resultado esperado |
| 5. AuraDB | ¿cómo levantamos el servicio? | conexión real |
| 6. Cypher | ¿cómo cargamos y recorremos relaciones? | grafo consultable |
| 7. Verificar | ¿Neo4j conserva la respuesta? | pandas = Neo4j |
| 8. Hito | ¿qué puede sostener Laura? | ficha + límite + export |
'''),
        hidden(code("""
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
        f's.innerHTML=\'<div><strong>\'+(ok?\'Correcto. \':\'Revisa. \')+\'</strong>\'+r[i]+\'</div>\';}})()" '
        f'style="background:#175c3c;color:white;border:0;border-radius:7px;padding:8px 12px">Verificar</button>'
        f'<div id="r-{uid}" aria-live="polite"></div></div>'
    )
    display(HTML(box))

def tutorial(url, alto=720):
    box = f'<iframe src="{url}?embed=1" width="100%" height="{alto}" style="border:0;border-radius:10px;background:#faf7ef"></iframe>'
    box += f'<p><a href="{url}" target="_blank">Abrir tutorial en pantalla completa ↗</a></p>'
    display(HTML(box))

print("Soporte S6 listo.")
"""), "Preparar interactividad"),
        md('''
---
## 1. Recuperar el proceso que Laura abrió en S5

S5 dejó `s05_ancla_s06.json`. Súbelo al panel **Archivos** de Colab y escribe su ruta. Si lo perdiste, la clase no se bloquea: el dataset trae una **ancla pedagógica real** con historial útil.

**OJO.** El respaldo permite aprender Neo4j, pero el hito declara que no se usó el archivo propio.
'''),
        code(f"""
import json
from pathlib import Path
import pandas as pd

DATA_URL = {DATA!r}
MANIFEST_URL = {MANIFEST!r}

datos = pd.read_csv(DATA_URL, low_memory=False)
with __import__("urllib.request").request.urlopen(MANIFEST_URL) as r:
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
## 2. El candidato y el historial cumplen funciones distintas

```text
                    ┌─ Proceso histórico ─→ Proveedor A
                    │
Proceso candidato ← Entidad
                    │
                    └─ Proceso histórico ─→ Proveedor B ─← otra Entidad
```

El candidato puede no estar adjudicado: **no inventamos un proveedor**. El historial adjudicado aporta las relaciones reales.
'''),
        question_cell(1, "Modelo", "¿Por qué el candidato de S5 no necesita una relación ADJUDICADO_A?", [
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
    uso_respaldo_s06 = False

print("Entidad de trabajo:", ancla_trabajo["entidad"])
print("Procesos históricos:", hist_ancla["id_proceso"].nunique())
print("Proveedores distintos:", hist_ancla["nit_proveedor"].nunique())
"""),
        md('''
---
## 3. Diseñar el grafo antes de escribir Cypher

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

`Proceso` queda como nodo porque hoy participa en caminos y la próxima sesión reutilizará su texto.
'''),
        md('''
### Cypher mínimo

| Construcción | Para qué sirve | Error frecuente |
|---|---|---|
| `MERGE` | encuentra o crea | creer que siempre crea otro nodo |
| `MATCH` | busca patrones | ignorar las relaciones del patrón |
| `WHERE` | filtra | usarlo sin comprender qué se conectó |
| `WITH` | encadena etapas | olvidar variables |
| `RETURN` | define la salida | confundir salida con persistencia |
| `ORDER BY` | orden explícito | asumir que el motor ya ordenó |
'''),
        question_cell(2, "Cypher", "¿Por qué usaremos MERGE y restricciones únicas?", [
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
esperado_pd
"""),
        md('''
### Interpretación del contrato pandas

**Cómo se lee.** `procesos_con_entidad` cuenta procesos adjudicados de la entidad ancla; `entidades_conectadas` cuenta entidades distintas asociadas al mismo NIT de proveedor.

**Qué nos dice.** Ya sabemos qué salida debería reproducir el grafo.

**Qué NO permite concluir todavía.** Repetición o conectividad no equivale a favorecimiento, colusión ni irregularidad. Faltarían evidencia sobre competencia, temporalidad, propiedad/representación y criterios de adjudicación.

**Error frecuente.** Llamar “sospechoso” al proveedor que queda primero.
'''),
        md('''
---
## 5. Tutorial visual — AuraDB

**HAZ ESTO AHORA.** Vuelve cuando `RETURN 1 AS conexion` funcione en Query y tengas URI, usuario y contraseña.
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
        question_cell(3, "Interpretación", "Un proveedor aparece conectado con cuatro entidades. ¿Qué puede afirmar Laura?", [
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
## 8. CRUD seguro y evidencia individual

El CRUD usa `S06-DEMO`; no modificamos un proceso real. Después eliges un proveedor de tu resultado y abres su vecindario.
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
for i, row in neo_df.iterrows():
    print(f"{i+1:>2}. {row['proveedor']} | entidades={row['entidades_conectadas']}")
sel = int(input("Número de proveedor: ").strip())
if not 1 <= sel <= len(neo_df):
    raise ValueError("Número fuera de rango")
proveedor_elegido = neo_df.iloc[sel-1]

vec = driver.execute_query('''
MATCH (e:Entidad)-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor {nit:$nit})
RETURN e.nombre AS entidad, p.id AS proceso, p.nombre AS nombre_proceso, p.valor AS valor
ORDER BY entidad, valor DESC
''', nit=str(proveedor_elegido["nit_proveedor"]))
vecindario_df = pd.DataFrame([r.data() for r in vec.records])
vecindario_df
"""),
        md('''
### La evidencia no termina en el grafo

Escribe un límite que nombre **qué dato faltaría** antes de convertir la conexión observada en una afirmación de riesgo o irregularidad. “Faltan datos” no es suficiente.
'''),
        code("""
from pathlib import Path
limite_estudiante = input("Límite concreto y dato faltante: ").strip()
if len(limite_estudiante) < 25:
    raise ValueError("Nombra la conclusión que no puedes sostener y el dato que falta.")

export = vecindario_df.merge(
    datos[["id_proceso", "descripcion", "modalidad", "url_secop"]].drop_duplicates("id_proceso"),
    left_on="proceso", right_on="id_proceso", how="left"
)
export.to_json("s06_contexto_procesos.jsonl", orient="records", lines=True, force_ascii=False)

hito = f'''# Hito S06 — Ficha relacional de revisión\n\n- Origen del ancla: {origen_ancla}\n- Proceso S5: {ancla_original.get("id_proceso", "")}\n- Entidad de trabajo: {ancla_trabajo.get("entidad", "")}\n- Noticias / nivel: {ancla_trabajo.get("noticias_entidad", "")} / {ancla_trabajo.get("nivel_menciones", "")}\n- Respaldo pedagógico: {uso_respaldo_s06}\n- pandas == Neo4j: {coinciden}\n- Proveedor elegido: {proveedor_elegido["proveedor"]}\n- Entidades conectadas: {int(proveedor_elegido["entidades_conectadas"])}\n- Procesos en el vecindario: {len(vecindario_df)}\n\n## Límite\n{limite_estudiante}\n\n## Decisión de modelado\nProceso es nodo porque participa en caminos y su texto será reutilizado en S7.\n'''
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
| Modelo | justifica nodos y relaciones | describe sin justificar | copia el patrón | 20 |
| Ejecución | vecindario propio ejecutado | solo consulta común | no hay salida | 20 |
| Verificación | `pandas == Neo4j` comprobado | muestra ambos | solo uno | 15 |
| Evidencia propia | proveedor + entidades + procesos | incompleta | genérica | 15 |
| Límite | conclusión inválida + dato específico faltante | genérico | afirma irregularidad | 15 |
'''),
        md('''
---
## Hoja de trucos y puente

```text
MERGE  → encuentra o crea
MATCH  → busca patrón
WHERE  → filtra
WITH   → encadena
RETURN → salida

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
