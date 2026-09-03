#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pasada final reproducible de S5, ejecutada después del constructor base."""

from __future__ import annotations

import ast
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "5_Atlas_Cassandra_Query_First.ipynb"


def src(cell: dict) -> str:
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def put(cell: dict, text: str) -> None:
    cell["source"] = text.strip()


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip()}


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.strip(),
    }


def find(cells: list[dict], needle: str) -> int:
    for i, cell in enumerate(cells):
        if needle in src(cell):
            return i
    raise RuntimeError(f"No se encontró {needle!r}")


def insert_once(cells: list[dict], anchor: str, marker: str, new_cells: list[dict], *, after: bool) -> None:
    if any(marker in src(c) for c in cells):
        return
    i = find(cells, anchor)
    pos = i + 1 if after else i
    cells[pos:pos] = new_cells


def encode_questions(cells: list[dict]) -> None:
    helper = src(cells[0])
    if "def pregunta_interactiva_codificada" not in helper:
        helper += '''


def pregunta_interactiva_codificada(payload_b64):
    payload = json.loads(base64.b64decode(payload_b64).decode("utf-8"))
    pregunta_interactiva(
        payload["numero"], payload["tema"], payload["pregunta"],
        payload["opciones"], payload["correcta"], payload["retro"]
    )
'''
        put(cells[0], helper)

    for cell in cells:
        text = src(cell)
        if cell.get("cell_type") != "code":
            continue
        if "pregunta_interactiva(" not in text or "def pregunta_interactiva" in text:
            continue
        if "pregunta_interactiva_codificada(" in text:
            continue

        tree = ast.parse(text)
        call = next(
            (
                node for node in ast.walk(tree)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "pregunta_interactiva"
            ),
            None,
        )
        if call is None or len(call.args) != 6:
            raise RuntimeError("No se pudo codificar una pregunta de S5")
        vals = [ast.literal_eval(a) for a in call.args]
        payload = {
            "numero": vals[0], "tema": vals[1], "pregunta": vals[2],
            "opciones": vals[3], "correcta": vals[4], "retro": vals[5],
        }
        token = base64.b64encode(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        ).decode("ascii")
        title = text.splitlines()[0] if text.startswith("#@title") else "#@title Autoevaluación"
        put(cell, f'{title}\npregunta_interactiva_codificada("{token}")')


def main() -> None:
    data = json.loads(NB.read_text(encoding="utf-8"))
    cells = data["cells"]

    # Reactivación: ayuda mínima si se perdió la URI, sin repetir S4.
    put(cells[find(cells, "## 1. Reactivar sin repetir la sesión 4")], '''
---
## 1. Reactivar sin repetir la sesión 4

Antes de entrar a consultas, verifica el estado esperado:

<div align="center"><a href="https://github.com/jazaineam1/BigData2026/blob/main/assets/diagrams/session5/02_atlas_coleccion.svg" target="_blank"><img src="https://raw.githubusercontent.com/jazaineam1/BigData2026/main/assets/diagrams/session5/02_atlas_coleccion.png" width="420" alt="Coleccion compras_claras en Atlas: noticias y entidades_noticias"></a></div>

La siguiente celda solo recupera la conexión. La contraseña se pide con `getpass()` y no queda escrita.

<details>
<summary><strong>Si no conservas la URI de S4</strong></summary>

1. En Atlas abre tu clúster → **Connect / Drivers**.
2. Selecciona **Python** y copia la URI con `<db_username>` y `<db_password>`.
3. Vuelve aquí. **No crees otra base ni otro clúster.**

Si tampoco recuerdas el camino, usa `assets/tutoriales/atlas-guia-conexion.html` solo como recuperación.
</details>
''')

    put(cells[find(cells, 'uri_pegada = input("Pega tu URI de Atlas')], '''
!pip install -q pymongo dnspython

from getpass import getpass
from urllib.parse import quote_plus
from pymongo import MongoClient

uri_pegada = input("Pega tu URI de Atlas (Connect / Drivers): ").strip()
if not uri_pegada:
    raise ValueError("La URI está vacía. Recupera la URI de tu clúster de S4.")

uri = uri_pegada
if "<db_username>" in uri or "<db_password>" in uri:
    usuario = input("Usuario de base de datos: ").strip()
    contrasena = quote_plus(getpass("Contraseña (no se muestra): "))
    uri = uri.replace("<db_username>", quote_plus(usuario))
    uri = uri.replace("<db_password>", contrasena)

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=7000)
    client.admin.command("ping")
    db = client["compras_claras"]
    motor_atlas = "Atlas real"
    print("Conectado.")
    print("noticias:", db["noticias"].count_documents({}))
    print("entidades_noticias:", db["entidades_noticias"].count_documents({}))
except Exception as error:
    db = None
    motor_atlas = "respaldo por archivos"
    print("No se pudo conectar:", type(error).__name__)
    print("La clase puede continuar con respaldo; eso NO sustituye haber creado la vista en Atlas.")

print("Modo:", motor_atlas)
''')

    # Atlas: teoría mínima que habilita la vista útil.
    put(cells[find(cells, "## 2. Consulta, pipeline, pipeline guardado y vista")], '''
## 2. De documentos a una vista que sí usaremos

| Objeto | Pregunta mental | ¿Guarda datos nuevos? |
|---|---|---|
| filtro / `find()` | ¿qué documentos quiero ver? | no |
| pipeline | ¿qué transformaciones quiero encadenar? | no |
| pipeline guardado | ¿quiero conservar la receta? | no |
| vista | ¿quiero consultar el resultado como objeto de solo lectura? | no |

La historia necesita una transformación: convertir menciones por entidad en una señal explicable.

| Etapa | Para qué sirve aquí | Qué debes mirar |
|---|---|---|
| `$set` | agrega `nivel_menciones` | crea un campo |
| `$switch` | aplica los cortes 20 y 5 | primera condición verdadera gana |
| `$project` | deja los campos útiles | reduce ruido |
| `$sort` | ordena la salida | la hace legible |

| `noticias` | nivel esperado |
|---:|---|
| 4 | baja |
| 5 | media |
| 19 | media |
| 20 | alta |

**PARA LLEVAR.** El pipeline es la receta; la vista publica esa receta como salida consultable de solo lectura.
''')

    put(cells[find(cells, "## 3. Tutorial visual 1")], '''
---
## 3. Tutorial visual 1 — Atlas: construir la vista que sí viaja

**HAZ ESTO AHORA.** Trabaja en Atlas y vuelve a este mismo cuaderno.

No repetimos registro, clúster, carga, filtros de calentamiento ni pipelines que no se consumen después.

Al regresar deben existir:

- pipeline guardado `clasificar-menciones-v1`;
- vista **`menciones_clasificadas`**;
- control `6 alta + 25 media + 111 baja = 142`.

**MÁS ADELANTE.** `resumen-secciones-v1` y `clasificar-noticias-v1` quedan como ampliación para recuperar tiempo de laboratorio.
''')
    i = find(cells, "Tutorial 1 — Atlas")
    put(cells[i], src(cells[i]).replace(
        "atlas-s05-pipelines-vistas.html", "atlas-s05-pipelines-vistas-v2.html"
    ).replace("Tutorial 1 — Atlas con capturas reales", "Tutorial 1 — Atlas: vista paso a paso"))

    # La vista aporta campos que viajan a la bandeja; no queda como ejercicio decorativo.
    put(cells[find(cells, 'secop = pd.read_csv(')], '''
import pandas as pd

secop = pd.read_csv(
    "https://raw.githubusercontent.com/jazaineam1/BigData2026/main/Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv",
    low_memory=False,
)
print("Procesos SECOP:", len(secop))
assert len(secop) == 1000

contexto_menciones = pd.DataFrame(menciones)[["entidad", "noticias", "nivel_menciones"]].copy()
assert contexto_menciones["entidad"].is_unique
contexto_menciones = contexto_menciones.rename(columns={"noticias": "noticias_entidad"})

entidades_en_prensa = set(contexto_menciones["entidad"])
paso1 = secop[secop["entidad"].isin(entidades_en_prensa)]
paso2 = paso1[
    paso1["modalidad_de_contratacion"].str.contains("directa", case=False, na=False)
]
respuestas = pd.to_numeric(paso2["respuestas_al_procedimiento"], errors="coerce")
paso3 = paso2[respuestas.eq(0)]

candidatos = (
    paso3
    .merge(contexto_menciones, on="entidad", how="left", validate="many_to_one")
    .sort_values(["precio_base", "id_del_proceso"], ascending=[False, True])
    .reset_index(drop=True)
)

print("1) total                       :", len(secop))
print("2) entidad coincide con prensa :", len(paso1))
print("3) + modalidad directa         :", len(paso2))
print("4) + cero respuestas           :", len(paso3))
print("Candidatos finales             :", len(candidatos))
print("Contexto de menciones en los 77:", candidatos["nivel_menciones"].value_counts().to_dict())

assert len(paso1) == 163
assert len(candidatos) == 77
assert candidatos["nivel_menciones"].notna().all()
''')

    insert_once(cells, "### El detalle estadístico que importa", "Interpretación del embudo", [md('''
### Interpretación del embudo

**Cómo se lee, filtro por filtro (cada uno reduce al anterior, no son listas aparte):**

- **1.000 procesos SECOP** — el total del corte, antes de aplicar cualquier regla.
- **→ 163** — Filtro 1: la `entidad` del proceso aparece en la vista de prensa `menciones_clasificadas`.
- **→ 81** — Filtro 2: de esos 163, la `modalidad_de_contratacion` contiene "directa".
- **→ 77** — Filtro 3: de esos 81, `respuestas_al_procedimiento` es igual a 0.

Los tres filtros van encadenados con **Y** (AND): un proceso solo llega a los 77 si cumple los tres a la vez, no si cumple cualquiera de ellos. Cada uno de esos 77 candidatos conserva además `noticias_entidad` y `nivel_menciones` de la vista, pero eso es **contexto que viaja con la fila**, no un cuarto filtro que decida quién entra.

**Qué nos dice.** La vista aporta contexto explicable a cada fila que Laura recibirá.

**Qué NO permite concluir todavía.** `nivel_menciones` no es criterio de selección ni probabilidad de riesgo; todavía no sabemos si una noticia menciona el contrato particular.

**Error frecuente.** Creer que “alta” empujó un proceso dentro de los 77. El nivel viaja como contexto, no como filtro.
''')], after=False)

    put(cells[find(cells, 'print("Primer candidato")')], '''
primero = candidatos.iloc[0]

print("Primer candidato")
print("ID                :", primero["id_del_proceso"])
print("Entidad           :", primero["entidad"])
print("Valor             : $", f'{primero["precio_base"]:,.0f}')
print("Noticias entidad  :", int(primero["noticias_entidad"]))
print("Nivel de menciones:", primero["nivel_menciones"])

assert primero["id_del_proceso"] == "CO1.REQ.5407319"
assert primero["entidad"] == "MINISTERIO DEL DEPORTE"
assert int(primero["precio_base"]) == 168750000
''')

    # Resultado individual antes de la nube: permite seguir aunque Astra falle.
    insert_once(cells, "### Recuperación", "Contrato de resultado", [
        md('''
### Contrato de resultado — fija primero qué debería devolver Cassandra

Elige un departamento mediante número. pandas calcula el top 5 esperado; después Cassandra debe devolver los mismos IDs y en el mismo orden.
'''),
        code('''
conteo_departamentos = candidatos["departamento_entidad"].dropna().astype(str).value_counts()
opciones_departamento = conteo_departamentos.index.tolist()

print("Elige un departamento para tu evidencia individual:")
for i, d in enumerate(opciones_departamento, start=1):
    print(f"{i:>2}. {d} ({conteo_departamentos[d]} candidatos)")

seleccion = int(input("Número de departamento: ").strip())
if not 1 <= seleccion <= len(opciones_departamento):
    raise ValueError("El número no corresponde a la lista mostrada.")

departamento_elegido = opciones_departamento[seleccion - 1]
top5_esperado_pd = (
    candidatos[candidatos["departamento_entidad"].astype(str) == departamento_elegido]
    .sort_values(["precio_base", "id_del_proceso"], ascending=[False, True])
    .head(5)
)
ids_esperados_pd = top5_esperado_pd["id_del_proceso"].astype(str).tolist()

print("Departamento elegido:", departamento_elegido)
print("IDs esperados por pandas:", ids_esperados_pd)
'''),
    ], after=False)

    # Recuperación post-receso también restaura el contexto de la vista.
    i = find(cells, "# Recuperación")
    r = src(cells[i])
    if "noticias_entidad" not in r:
        r = r.replace(
            'entidades_en_prensa = {m["entidad"] for m in menciones}\n    paso1 = secop[secop["entidad"].isin(entidades_en_prensa)]',
            'contexto_menciones = pd.DataFrame(menciones)[["entidad", "noticias", "nivel_menciones"]].rename(columns={"noticias": "noticias_entidad"})\n    entidades_en_prensa = set(contexto_menciones["entidad"])\n    paso1 = secop[secop["entidad"].isin(entidades_en_prensa)]',
        )
        r = r.replace(
            'candidatos = paso2[respuestas.eq(0)].sort_values(\n        ["precio_base", "id_del_proceso"], ascending=[False, True]\n    ).reset_index(drop=True)',
            'candidatos = (\n        paso2[respuestas.eq(0)]\n        .merge(contexto_menciones, on="entidad", how="left", validate="many_to_one")\n        .sort_values(["precio_base", "id_del_proceso"], ascending=[False, True])\n        .reset_index(drop=True)\n    )',
        )
        put(cells[i], r)

    # Astra: guía visual honesta, sin afirmar capturas inexistentes.
    put(cells[find(cells, "## 8. Tutorial visual 2")], '''
---
## 8. Tutorial visual 2 — Astra DB y CQL, paso a paso

- el **cuaderno** explica modelo y decisión;
- el **tutorial HTML** reproduce la ruta de interfaz y los nombres de los controles;
- tú ejecutas cada paso en Astra;
- vuelves con una tabla real.

**Transparencia visual.** Donde no existe una captura autenticada de una cuenta del curso usamos una **representación de interfaz claramente rotulada**, no una fotografía fingida.

Ruta del grupo: Astra DB Serverless **non-vector** + CQL Console. No instalamos Cassandra en Windows ni en Colab.

Ruta contrastada con documentación oficial vigente el **31 de agosto de 2026**. `Connection details` es el nombre vigente para bases non-vector.
''')
    i = find(cells, "Tutorial 2 — Astra/Cassandra")
    put(cells[i], src(cells[i]).replace(
        "astra-cassandra-paso-a-paso.html", "astra-cassandra-paso-a-paso-v2.html"
    ).replace("Tutorial 2 — Astra/Cassandra con capturas", "Tutorial 2 — Astra/Cassandra: guía visual"))

    # Driver: mini ficha y validación de archivos/credenciales.
    insert_once(cells, "!pip install -q cassandra-driver", "Ficha del driver", [md('''
### Ficha del driver

| Objeto | Para qué sirve | Qué recibe | Qué deja |
|---|---|---|---|
| `Cluster(...)` | configura la conexión | SCB + autenticación | cliente del driver |
| `cluster.connect()` | abre la sesión | `Cluster` | `Session` |
| `session.prepare()` | prepara CQL parametrizado | sentencia con `?` | consulta reutilizable |
| `session.execute()` | envía CQL | sentencia + valores | filas o escritura |

**Error frecuente.** Aquí `Cluster` es un objeto del driver Python; no significa crear otro recurso en Astra.
''')], after=False)

    put(cells[find(cells, "Sube el Secure Connect Bundle")], '''
from getpass import getpass
from datetime import date
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

try:
    from google.colab import files
    print("Sube UN solo Secure Connect Bundle (.zip) de ESTA base:")
    subidos = files.upload()
    if len(subidos) != 1:
        raise ValueError("Debes subir exactamente un archivo SCB .zip.")
    scb = next(iter(subidos))
except ImportError:
    scb = input("Ruta al Secure Connect Bundle (.zip): ").strip()

if not scb.lower().endswith(".zip"):
    raise ValueError("El Secure Connect Bundle debe conservarse como .zip.")

token_astra = getpass("Application token de Astra (no se muestra): ").strip()
if not token_astra:
    raise ValueError("El token está vacío.")

cluster = Cluster(
    cloud={"secure_connect_bundle": scb},
    auth_provider=PlainTextAuthProvider("token", token_astra),
)
session = cluster.connect()
row = session.execute("SELECT release_version FROM system.local").one()
print("Conectado. Cassandra:", row[0] if row else "versión no disponible")
''')

    put(cells[find(cells, "cql_tabla = '''")], """
cql_tabla = '''
CREATE TABLE IF NOT EXISTS compras_claras.prioridades_por_corte_departamento (
    corte date,
    departamento text,
    valor_base bigint,
    id_proceso text,
    entidad text,
    noticias_entidad int,
    nivel_menciones text,
    estado_revision text,
    url_secop text,
    criterio text,
    PRIMARY KEY ((corte, departamento), valor_base, id_proceso)
) WITH CLUSTERING ORDER BY (valor_base DESC, id_proceso ASC);
'''
session.execute(cql_tabla)
print("Tabla lista.")
""")

    put(cells[find(cells, "def texto_seguro")], """
def texto_seguro(valor, defecto="No definido"):
    if pd.isna(valor):
        return defecto
    texto = str(valor).strip()
    return texto if texto else defecto

insertar = session.prepare('''
INSERT INTO compras_claras.prioridades_por_corte_departamento
(corte, departamento, valor_base, id_proceso, entidad,
 noticias_entidad, nivel_menciones, estado_revision, url_secop, criterio)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''')

CORTE_CLASE = date(2026, 9, 3)

# 77 escrituras síncronas: claridad didáctica; NO es benchmark de carga masiva.
for _, f in candidatos.iterrows():
    session.execute(insertar, (
        CORTE_CLASE,
        texto_seguro(f.get("departamento_entidad")),
        int(f["precio_base"]),
        str(f["id_del_proceso"]),
        str(f["entidad"]),
        int(f["noticias_entidad"]),
        str(f["nivel_menciones"]),
        "pendiente",
        texto_seguro(f.get("urlproceso"), ""),
        "entidad en prensa; contratación directa; 0 respuestas",
    ))
print("Insertadas/actualizadas:", len(candidatos), "filas del corte", CORTE_CLASE)
""")

    put(cells[find(cells, "consulta = '''")], """
consulta = '''
SELECT id_proceso, entidad, valor_base, noticias_entidad, nivel_menciones, estado_revision
FROM compras_claras.prioridades_por_corte_departamento
WHERE corte = %s AND departamento = %s
LIMIT 5
'''

bogota = "Distrito Capital de Bogotá"
top5 = list(session.execute(consulta, (CORTE_CLASE, bogota)))
print("Top 5 —", bogota)
for f in top5:
    print(
        f.id_proceso, "|", f.entidad, "| $", f"{f.valor_base:,}",
        "| prensa:", f.noticias_entidad, f.nivel_menciones,
        "|", f.estado_revision,
    )
if not top5:
    print("No aparecieron filas. Revisa el nombre exacto del departamento.")
""")

    i = find(cells, "### Evidencia individual")
    put(cells[i], '''
### Evidencia individual — compara dos motores

Ya fijaste el top 5 esperado con pandas. Ahora pregunta lo mismo a Cassandra. La evidencia es una prueba de **corrección**, no un benchmark de velocidad.
''')
    if i + 1 >= len(cells):
        raise RuntimeError("Falta celda de evidencia individual")
    put(cells[i + 1], '''
if "departamento_elegido" not in globals() or "ids_esperados_pd" not in globals():
    raise RuntimeError("Ejecuta primero Contrato de resultado.")

top5_propio = list(session.execute(consulta, (CORTE_CLASE, departamento_elegido)))
ids_cql = [str(f.id_proceso) for f in top5_propio]
coinciden_cql_pd = ids_cql == ids_esperados_pd

print("Departamento     :", departamento_elegido)
print("Esperado pandas :", ids_esperados_pd)
print("Devuelto CQL    :", ids_cql)
print("¿Coinciden?     :", "SÍ" if coinciden_cql_pd else "NO")

if not coinciden_cql_pd:
    raise AssertionError("Revisa corte, departamento, carga y orden: los dos resultados no coinciden.")
''')

    insert_once(cells, "coinciden_cql_pd = ids_cql == ids_esperados_pd", "Interpretación del resultado CQL", [md('''
### Interpretación del resultado CQL

**Cómo se lee.** Comparamos, en orden, los IDs del top 5 calculado con pandas y el servido por Cassandra.

**Qué nos dice.** Si coinciden, la tabla query-first está sirviendo correctamente esa pregunta sobre los datos cargados.

**Qué NO permite concluir todavía.** No demuestra que Cassandra sea más rápido ni necesario para 77 filas; no hicimos una prueba de rendimiento o escala.

**Error frecuente.** Convertir una prueba de corrección en una afirmación de performance.
''')], after=True)

    put(cells[find(cells, "# UPDATE: cambiamos el estado")], """
# UPDATE: cambiamos el estado y después lo volvemos a leer.
if top5:
    objetivo = top5[0]
    session.execute('''
    UPDATE compras_claras.prioridades_por_corte_departamento
    SET estado_revision = %s
    WHERE corte = %s AND departamento = %s AND valor_base = %s AND id_proceso = %s
    ''', ("en_revision", CORTE_CLASE, bogota, int(objetivo.valor_base), objetivo.id_proceso))

    verificacion = session.execute('''
    SELECT estado_revision
    FROM compras_claras.prioridades_por_corte_departamento
    WHERE corte = %s AND departamento = %s AND valor_base = %s AND id_proceso = %s
    ''', (CORTE_CLASE, bogota, int(objetivo.valor_base), objetivo.id_proceso)).one()

    assert verificacion is not None and verificacion.estado_revision == "en_revision"
    print("UPDATE verificado:", objetivo.id_proceso, "→", verificacion.estado_revision)
""")

    put(cells[find(cells, "## 10. Consistencia ajustable")], '''
---
<details>
<summary><strong>MÁS ADELANTE — Consistencia ajustable</strong></summary>

Cassandra replica datos. ¿Cuántas confirmaciones esperamos antes de responder? Esa decisión intercambia latencia y garantía inmediata.

No configuramos niveles hoy: primero debe quedar firme `consulta → partición → clustering`. Astra Serverless además aplica guardrails propios.
</details>
''')

    # Hito más resistente a copia y con alternativa razonada.
    put(cells[find(cells, 'alternativa = input(')], """
alternativa = input("Alternativa de diseño descartada: ").strip()
razon_alternativa = input("¿Por qué la descartaste para la consulta de Laura?: ").strip()
consulta_no_soportada = input("Una consulta profesional que esta tabla NO soporta bien: ").strip()
nueva_particion = input("Si fuera frecuente, ¿qué dato(s) usarías para localizar la nueva partición?: ").strip()

departamento_hito = globals().get("departamento_elegido", "No seleccionado")
ids_pd_hito = globals().get("ids_esperados_pd", [])
ids_cql_hito = globals().get("ids_cql", [])
coincidencia_hito = globals().get("coinciden_cql_pd", False)
primer_id = str(candidatos.iloc[0]["id_del_proceso"])
primer_entidad = str(candidatos.iloc[0]["entidad"])
primer_valor = int(candidatos.iloc[0]["precio_base"])
primer_noticias = int(candidatos.iloc[0]["noticias_entidad"])
primer_nivel = str(candidatos.iloc[0]["nivel_menciones"])

candidatos.to_csv("s05_priorizacion.csv", index=False, encoding="utf-8")

hito = f'''# Hito S05 — De la priorización al servicio

## Resultado propio de Atlas
- Fuente: {"vista real de Atlas" if vista_real else "respaldo; falta evidencia de vista real"}
- Alta / media / baja: {niveles.get("alta", 0)} / {niveles.get("media", 0)} / {niveles.get("baja", 0)}

## Regla de priorización
- Procesos iniciales: {len(secop)}
- Coincidencias por entidad: {len(paso1)}
- Candidatos: {len(candidatos)}
- Primer candidato: {primer_id} — {primer_entidad} — $ {primer_valor:,}
- Contexto desde Atlas: {primer_noticias} noticias — nivel {primer_nivel}

## Límite
Referencias de proceso citadas literalmente en prensa: {con_referencia} de {len(candidatos)}.
La evidencia periodística usada es por entidad; no demuestra irregularidad del contrato específico.

## Query-first
PRIMARY KEY ((corte, departamento), valor_base, id_proceso)
CLUSTERING ORDER BY (valor_base DESC, id_proceso ASC)

## Evidencia individual de corrección
- Departamento: {departamento_hito}
- Top esperado con pandas: {ids_pd_hito}
- Top devuelto por Cassandra: {ids_cql_hito if ids_cql_hito else "NO VERIFICADO EN ASTRA"}
- Coincidencia exacta de IDs y orden: {"sí" if coincidencia_hito else "no verificada"}

## Alternativa descartada
{alternativa or "PENDIENTE"}

Razón: {razon_alternativa or "PENDIENTE"}

## Consulta no soportada
{consulta_no_soportada or "PENDIENTE"}

Nueva localización de partición si fuera frecuente: {nueva_particion or "PENDIENTE"}

## Decisión
MongoDB transforma documentos; pandas materializa una regla auditable; Cassandra sirve una proyección para una consulta repetitiva conocida.
'''

with open("hito_s05_servicio_prioridades.md", "w", encoding="utf-8") as f:
    f.write(hito)
print(hito)
print("\\nArchivos creados: s05_priorizacion.csv, hito_s05_servicio_prioridades.md")
""")

    put(cells[find(cells, "## Rúbrica de calidad del hito")], '''
## Rúbrica de calidad del hito

| Criterio | Completo | Parcial | Sin evidencia | Peso |
|---|---|---|---|---:|
| Vista Atlas | vista real + 142 / 6-25-111 | respaldo declarado | números sin fuente | 15 |
| Regla + límite | 1.000→163→77 y explica 0/77 | números sin límite concreto | llama “irregulares” a los 77 | 20 |
| Query-first | PK/clustering explicados desde la consulta | copia diseño sin justificar | clave no sirve esa consulta | 20 |
| Evidencia individual | departamento + top pandas + top CQL + coincidencia | top pandas y contingencia Astra declarada | no hay resultado propio | 20 |
| Alternativa | alternativa + razón de descarte | alternativa sin razón | no hay alternativa | 15 |
| Consulta no soportada | consulta distinta + nueva localización | consulta sin rediseño | afirma que cualquier filtro funciona | 10 |

Las autoevaluaciones son **formativas**. La evidencia revisable es el hito producido por la ejecución.
''')

    i = find(cells, "# Cierre")
    close = src(cells[i])
    if "verifiqué que dos motores" not in close:
        close = close.replace(
            "4. cuando apareció una consulta operacional repetitiva, **diseñé el almacenamiento desde esa pregunta**;\n5. comprobé que una tabla optimizada para una consulta **no es una tabla universal**.",
            "4. cuando apareció una consulta operacional repetitiva, **diseñé el almacenamiento desde esa pregunta**;\n5. **verifiqué que dos motores devolvieran el mismo top 5** antes de confiar en el servicio;\n6. comprobé que una tabla optimizada para una consulta **no es una tabla universal**.",
        )
        put(cells[i], close)

    encode_questions(cells)

    all_text = "\n".join(src(c) for c in cells)
    if "quiz_sesiones_1_a_4" in all_text:
        raise RuntimeError("El quiz S1–S4 debe permanecer fuera de los enlaces de S5")

    NB.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    json.loads(NB.read_text(encoding="utf-8"))
    print(f"[OK] S5 v2 aplicada: {len(cells)} celdas; JSON válido.")
    print("[OK] Vista→bandeja→Cassandra conectados; pandas↔CQL valida corrección.")
    print("[OK] Preguntas codificadas y quiz S1–S4 fuera de enlaces.")


if __name__ == "__main__":
    main()
