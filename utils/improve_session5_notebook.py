#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Segunda pasada reproducible sobre la Sesión 5.

Se ejecuta DESPUÉS de ``build_session5_notebook.py`` y corrige hallazgos de la
auditoría docente/estudiante sin editar el JSON del notebook a mano.

Objetivos de esta pasada:
- quitar pasos Atlas que no alimentan la historia de S5;
- hacer que la vista de Atlas viaje de verdad hasta la bandeja y Cassandra;
- añadir interpretación con los cuatro rótulos de la casa;
- crear una evidencia individual independiente de la disponibilidad de Astra;
- comparar el resultado pandas ↔ Cassandra como prueba de corrección;
- robustecer SCB/token/UPDATE y el hito;
- convertir la rúbrica en niveles observables;
- codificar las autoevaluaciones para que GitHub no revele la respuesta a simple vista.
"""

from __future__ import annotations

import ast
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "5_Atlas_Cassandra_Query_First.ipynb"


def source(cell: dict) -> str:
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def set_source(cell: dict, text: str) -> None:
    cell["source"] = text.strip()


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip()}


def code(text: str, *, hidden: bool = False, title: str | None = None) -> dict:
    metadata = {}
    body = text.strip()
    if hidden:
        metadata = {
            "tags": ["hide-input"],
            "jupyter": {"source_hidden": True},
            "cellView": "form",
            "colab": {"formView": "both"},
        }
        if title and not body.startswith("#@title"):
            body = f'#@title {title} {{ display-mode: "form" }}\n' + body
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": metadata,
        "outputs": [],
        "source": body,
    }


def find(cells: list[dict], needle: str) -> int:
    for i, cell in enumerate(cells):
        if needle in source(cell):
            return i
    raise RuntimeError(f"No se encontró el marcador: {needle!r}")


def insert_once(
    cells: list[dict], anchor: str, marker: str, new_cells: list[dict], *, after: bool = True
) -> None:
    if any(marker in source(c) for c in cells):
        return
    i = find(cells, anchor)
    pos = i + 1 if after else i
    cells[pos:pos] = new_cells


def codificar_autoevaluaciones(cells: list[dict]) -> None:
    """Oculta enunciado/opciones/clave en GitHub, manteniendo el widget en Colab."""

    helper = source(cells[0])
    if "def pregunta_interactiva_codificada" not in helper:
        helper += '''


def pregunta_interactiva_codificada(payload_b64):
    payload = json.loads(base64.b64decode(payload_b64).decode("utf-8"))
    pregunta_interactiva(
        payload["numero"], payload["tema"], payload["pregunta"],
        payload["opciones"], payload["correcta"], payload["retro"]
    )
'''
        set_source(cells[0], helper)

    for cell in cells:
        s = source(cell)
        if (
            cell.get("cell_type") != "code"
            or "pregunta_interactiva(" not in s
            or "def pregunta_interactiva" in s
            or "pregunta_interactiva_codificada(" in s
        ):
            continue

        tree = ast.parse(s)
        llamada = None
        for nodo in ast.walk(tree):
            if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name):
                if nodo.func.id == "pregunta_interactiva":
                    llamada = nodo
                    break
        if llamada is None or len(llamada.args) != 6:
            raise RuntimeError("No se pudo codificar una autoevaluación de S5.")

        valores = [ast.literal_eval(a) for a in llamada.args]
        payload = {
            "numero": valores[0],
            "tema": valores[1],
            "pregunta": valores[2],
            "opciones": valores[3],
            "correcta": valores[4],
            "retro": valores[5],
        }
        token = base64.b64encode(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        ).decode("ascii")
        primera = s.splitlines()[0] if s.startswith("#@title") else "#@title Autoevaluación"
        set_source(cell, f'{primera}\npregunta_interactiva_codificada("{token}")')


def main() -> None:
    data = json.loads(NB.read_text(encoding="utf-8"))
    cells = data["cells"]

    # 1) Inicio: continuidad real y recuperación mínima de URI, sin repetir S4.
    i = find(cells, "## 1. Reactivar sin repetir la sesión 4")
    set_source(cells[i], '''
---
## 1. Reactivar sin repetir la sesión 4

Antes de entrar a consultas, verifica el estado esperado:

```text
Atlas
└── compras_claras
    ├── noticias               → 987 documentos
    └── entidades_noticias     → 142 documentos
```

La siguiente celda solo recupera la conexión. La contraseña se pide con `getpass()` y no queda escrita.

<details>
<summary><strong>Si no conservas la URI de S4</strong></summary>

1. En Atlas abre tu clúster → **Connect / Drivers**.
2. Selecciona **Python** y copia la URI que contiene `<db_username>` y `<db_password>`.
3. Vuelve aquí. **No crees otra base ni otro clúster.**

Si tampoco recuerdas el camino, usa el tutorial de conexión de S4 solo como recuperación:
`assets/tutoriales/atlas-guia-conexion.html`.
</details>
''')

    # La URI puede venir ya completa: no pedir usuario/clave si no hay placeholders.
    i = find(cells, 'uri_pegada = input("Pega tu URI de Atlas')
    set_source(cells[i], '''
!pip install -q pymongo dnspython

from getpass import getpass
from urllib.parse import quote_plus
from pymongo import MongoClient

uri_pegada = input("Pega tu URI de Atlas (Connect / Drivers): ").strip()
if not uri_pegada:
    raise ValueError("La URI está vacía. Recupera la URI de tu clúster de S4 antes de continuar.")

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

    # 2) Teoría Atlas: solo lo que habilita la vista que sí se consumirá.
    i = find(cells, "## 2. Consulta, pipeline, pipeline guardado y vista")
    set_source(cells[i], '''
## 2. De documentos a una vista que sí usaremos

| Objeto | Pregunta mental | ¿Guarda datos nuevos? |
|---|---|---|
| filtro / `find()` | ¿qué documentos quiero ver? | no |
| pipeline | ¿qué transformaciones quiero encadenar? | no |
| pipeline guardado | ¿quiero conservar la receta? | no |
| vista | ¿quiero consultar el resultado como objeto de solo lectura? | no |

Hoy la historia necesita una sola transformación útil: convertir `noticias` por entidad en una señal explicable.

### Las etapas del pipeline de hoy

| Etapa | Para qué sirve aquí | Qué debes mirar |
|---|---|---|
| `$set` | agrega `nivel_menciones` | crea un campo sin borrar el documento |
| `$switch` | aplica los cortes 20 y 5 | primera condición verdadera gana |
| `$project` | deja los campos que necesita Laura | reduce ruido de salida |
| `$sort` | ordena por número de noticias y entidad | hace legible el resultado |

Ejemplo manual antes de abrir Atlas:

| `noticias` | nivel esperado |
|---:|---|
| 4 | baja |
| 5 | media |
| 19 | media |
| 20 | alta |

**PARA LLEVAR.** El pipeline es la receta; la vista publica esa receta como una salida consultable de solo lectura.
''')

    # 3) Tutorial Atlas: eliminar pasos que no alimentan la historia.
    i = find(cells, "## 3. Tutorial visual 1")
    set_source(cells[i], '''
---
## 3. Tutorial visual 1 — Atlas: construir la vista que sí viaja

**HAZ ESTO AHORA.** Trabaja en tu pestaña de Atlas y vuelve a este mismo cuaderno.

No repetimos registro, clúster, carga, filtros de calentamiento ni pipelines que no se consumen después.

Al regresar deben existir:

- pipeline guardado `clasificar-menciones-v1`;
- vista **`menciones_clasificadas`**;
- control `6 alta + 25 media + 111 baja = 142`.

**MÁS ADELANTE.** `resumen-secciones-v1` y `clasificar-noticias-v1` quedan como ampliación; quitarlos de la ruta obligatoria recupera tiempo para Cassandra.
''')
    i = find(cells, "Tutorial 1 — Atlas")
    s = source(cells[i]).replace(
        "atlas-s05-pipelines-vistas.html", "atlas-s05-pipelines-vistas-v2.html"
    ).replace("Tutorial 1 — Atlas con capturas reales", "Tutorial 1 — Atlas: vista paso a paso")
    set_source(cells[i], s)

    # 4) La vista debe viajar realmente: enriquecer cada candidato con su señal.
    i = find(cells, 'secop = pd.read_csv(')
    set_source(cells[i], '''
import pandas as pd

secop = pd.read_csv(
    "https://raw.githubusercontent.com/jazaineam1/BigData2026/main/Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv",
    low_memory=False,
)
print("Procesos SECOP:", len(secop))
assert len(secop) == 1000

contexto_menciones = pd.DataFrame(menciones)[["entidad", "noticias", "nivel_menciones"]].copy()
assert contexto_menciones["entidad"].is_unique, "Se esperaba una fila por entidad en la vista."
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
print("Contexto de menciones en los 77:")
print(candidatos["nivel_menciones"].value_counts(dropna=False).to_dict())

assert len(paso1) == 163
assert len(candidatos) == 77
assert candidatos["nivel_menciones"].notna().all()
''')

    insert_once(
        cells,
        "### El detalle estadístico que importa",
        "INTERPRETACIÓN EMBUDO S05",
        [md('''
### INTERPRETACIÓN EMBUDO S05

**Cómo se lee.** Partimos de 1.000 procesos, 163 pertenecen a entidades presentes en la fuente de noticias y 77 sobreviven a las condiciones de modalidad directa y cero respuestas. Cada candidato conserva además `noticias_entidad` y `nivel_menciones` provenientes de la vista de Atlas.

**Qué nos dice.** La vista ya no es un ejercicio aislado: aporta contexto explicable a cada fila de la bandeja que Laura recibirá.

**Qué NO permite concluir todavía.** `nivel_menciones` no es un criterio de selección ni una probabilidad de riesgo. Todavía no sabemos si una noticia menciona el contrato particular.

**Error frecuente.** Creer que “alta” empujó un proceso dentro de los 77. La regla selecciona por presencia de la entidad, modalidad y respuestas; el nivel viaja como contexto.
''')],
        after=False,
    )

    i = find(cells, 'print("Primer candidato")')
    set_source(cells[i], '''
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

    # 5) Evidencia individual ANTES de depender de Astra: contrato de resultado con pandas.
    insert_once(
        cells,
        "### RECUPERACIÓN S05",
        "CONTRATO DE RESULTADO S05",
        [
            md('''
### CONTRATO DE RESULTADO S05 — primero sabemos qué debería devolver Cassandra

Antes de tocar Astra, usa la bandeja que ya tienes para fijar un resultado esperado. Elige un departamento mediante número, no copiando un nombre largo.

La idea profesional es una prueba de contrato:

> **si Cassandra sirve bien la misma pregunta, debe devolver los mismos IDs y en el mismo orden que pandas.**
'''),
            code('''
conteo_departamentos = (
    candidatos["departamento_entidad"].dropna().astype(str).value_counts()
)
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
print("IDs esperados por pandas:")
for x in ids_esperados_pd:
    print(" -", x)
'''),
        ],
        after=False,
    )

    # La recuperación también debe conservar los campos que viajan desde Atlas.
    i = find(cells, "# RECUPERACIÓN S05")
    s = source(cells[i])
    if "noticias_entidad" not in s:
        s = s.replace(
            'entidades_en_prensa = {m["entidad"] for m in menciones}\n    paso1 = secop[secop["entidad"].isin(entidades_en_prensa)]',
            'contexto_menciones = pd.DataFrame(menciones)[["entidad", "noticias", "nivel_menciones"]].rename(columns={"noticias": "noticias_entidad"})\n    entidades_en_prensa = set(contexto_menciones["entidad"])\n    paso1 = secop[secop["entidad"].isin(entidades_en_prensa)]',
        )
        s = s.replace(
            'candidatos = paso2[respuestas.eq(0)].sort_values(\n        ["precio_base", "id_del_proceso"], ascending=[False, True]\n    ).reset_index(drop=True)',
            'candidatos = (\n        paso2[respuestas.eq(0)]\n        .merge(contexto_menciones, on="entidad", how="left", validate="many_to_one")\n        .sort_values(["precio_base", "id_del_proceso"], ascending=[False, True])\n        .reset_index(drop=True)\n    )',
        )
        set_source(cells[i], s)

    # 6) Tutorial Astra: no llamar "captura real" a una representación de UI.
    i = find(cells, "## 8. Tutorial visual 2")
    set_source(cells[i], '''
---
## 8. Tutorial visual 2 — Astra DB y CQL, paso a paso

Aquí se mantiene la misma separación de responsabilidades:

- el **cuaderno** explica el modelo y la decisión;
- el **tutorial HTML** reproduce la ruta de interfaz y nombra exactamente qué control buscar;
- tú ejecutas cada paso en Astra;
- vuelves con una tabla real.

**Transparencia visual.** Las pantallas de Astra que no tenemos capturadas desde una cuenta del curso se muestran como **representaciones de interfaz**, no como fotografías. No vamos a fingir capturas.

**Ruta del grupo:** Astra DB Serverless **non-vector** + CQL Console. No instalamos un servidor Cassandra en Windows ni en Colab.

Ruta contrastada con documentación oficial vigente el **31 de agosto de 2026**. `Connection details` es el nombre vigente para conexión de bases non-vector.
''')
    i = find(cells, "Tutorial 2 — Astra/Cassandra")
    s = source(cells[i]).replace(
        "astra-cassandra-paso-a-paso.html", "astra-cassandra-paso-a-paso-v2.html"
    ).replace("Tutorial 2 — Astra/Cassandra con capturas", "Tutorial 2 — Astra/Cassandra: guía visual")
    set_source(cells[i], s)

    # 7) Python driver: mini ficha y conexión defensiva.
    insert_once(
        cells,
        "!pip install -q cassandra-driver",
        "MINI FICHA DRIVER S05",
        [md('''
### MINI FICHA DRIVER S05 — cuatro objetos antes del código

| Objeto | Para qué sirve | Qué recibe hoy | Qué devuelve / deja |
|---|---|---|---|
| `Cluster(...)` | configura cómo llegar a Astra | SCB + autenticación | cliente de conexión |
| `cluster.connect()` | abre la sesión de trabajo | configuración del `Cluster` | `Session` |
| `session.prepare()` | prepara CQL parametrizado | sentencia con `?` | consulta preparada reutilizable |
| `session.execute()` | envía CQL | sentencia + valores | filas o confirmación de escritura |

**Error frecuente.** Confundir `Cluster` con la base de datos. Aquí `Cluster` es el objeto del **driver Python**, no un recurso que tengas que crear otra vez en el portal.
''')],
        after=False,
    )

    i = find(cells, "Sube el Secure Connect Bundle")
    set_source(cells[i], '''
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
    raise ValueError("El Secure Connect Bundle debe conservarse como archivo .zip.")

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

    # 8) La tabla Cassandra conserva el contexto producido por Atlas.
    i = find(cells, "cql_tabla = '''")
    set_source(cells[i], '''
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
) WITH CLUSTERING ORDER BY (
    valor_base DESC,
    id_proceso ASC
);
'''
session.execute(cql_tabla)
print("Tabla lista.")
''')

    i = find(cells, "def texto_seguro")
    set_source(cells[i], '''
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

# 77 escrituras síncronas: suficiente para aprender el flujo; NO es un benchmark de carga masiva.
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
''')

    i = find(cells, "consulta = '''")
    set_source(cells[i], '''
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
    print("No aparecieron filas. Revisa el nombre exacto del departamento en tu muestra.")
''')

    # Reemplaza el ejercicio de copiar un nombre largo por una prueba pandas ↔ Cassandra.
    i = find(cells, "### EVIDENCIA INDIVIDUAL S05")
    set_source(cells[i], '''
### EVIDENCIA INDIVIDUAL S05 — compara el resultado entre dos motores

Ya elegiste el departamento y fijaste los IDs esperados con pandas. Ahora pregunta lo mismo a Cassandra.

No estás comprobando “qué motor es más rápido” con cinco filas. Estás comprobando algo más básico y profesional: **que el servicio devuelve la misma respuesta que la regla que lo alimentó**.
''')
    if i + 1 >= len(cells) or "departamentos_disponibles" not in source(cells[i + 1]):
        raise RuntimeError("No se encontró la celda de evidencia individual esperada.")
    set_source(cells[i + 1], '''
if "departamento_elegido" not in globals() or "ids_esperados_pd" not in globals():
    raise RuntimeError("Ejecuta primero CONTRATO DE RESULTADO S05 antes del tutorial de Astra.")

top5_propio = list(session.execute(consulta, (CORTE_CLASE, departamento_elegido)))
ids_cql = [str(f.id_proceso) for f in top5_propio]
coinciden_cql_pd = ids_cql == ids_esperados_pd

print("Departamento:", departamento_elegido)
print("Esperado pandas :", ids_esperados_pd)
print("Devuelto CQL    :", ids_cql)
print("¿Coinciden?     :", "SÍ" if coinciden_cql_pd else "NO")

if not coinciden_cql_pd:
    raise AssertionError(
        "Cassandra no devolvió el mismo top 5 que pandas. Revisa corte, departamento, carga y orden."
    )
''')

    insert_once(
        cells,
        "coinciden_cql_pd = ids_cql == ids_esperados_pd",
        "INTERPRETACIÓN CQL S05",
        [md('''
### INTERPRETACIÓN CQL S05

**Cómo se lee.** Los IDs devueltos por Cassandra para tu departamento se comparan, en orden, con el top 5 calculado antes con pandas.

**Qué nos dice.** Si coinciden, la tabla query-first está sirviendo correctamente esa pregunta sobre los datos que cargamos.

**Qué NO permite concluir todavía.** No demuestra que Cassandra sea “más rápido” que pandas ni que sea necesario para 77 filas; no hicimos una prueba de rendimiento ni de escala.

**Error frecuente.** Convertir una prueba de corrección en una afirmación de performance.
''')],
        after=True,
    )

    # UPDATE debe releer la fila: imprimir "Actualizado" no prueba que ocurrió.
    i = find(cells, "# UPDATE: cambiamos el estado")
    set_source(cells[i], '''
# UPDATE: cambiamos el estado de la primera fila de Bogotá y lo volvemos a leer.
if top5:
    objetivo = top5[0]
    session.execute('''
    UPDATE compras_claras.prioridades_por_corte_departamento
    SET estado_revision = %s
    WHERE corte = %s AND departamento = %s AND valor_base = %s AND id_proceso = %s
    ''', (
        "en_revision",
        CORTE_CLASE,
        bogota,
        int(objetivo.valor_base),
        objetivo.id_proceso,
    ))

    verificacion = session.execute('''
    SELECT estado_revision
    FROM compras_claras.prioridades_por_corte_departamento
    WHERE corte = %s AND departamento = %s AND valor_base = %s AND id_proceso = %s
    ''', (
        CORTE_CLASE,
        bogota,
        int(objetivo.valor_base),
        objetivo.id_proceso,
    )).one()

    assert verificacion is not None and verificacion.estado_revision == "en_revision"
    print("UPDATE verificado:", objetivo.id_proceso, "→", verificacion.estado_revision)
''')

    # 9) Consistencia: conservar como ampliación, no competir con el laboratorio central.
    i = find(cells, "## 10. Consistencia ajustable")
    set_source(cells[i], '''
---
<details>
<summary><strong>MÁS ADELANTE — Consistencia ajustable (mapa conceptual)</strong></summary>

Cassandra replica datos. Simplificando:

```text
escritura
  ├── copia A ✓
  ├── copia B ✓
  └── copia C ...
```

¿Cuántas confirmaciones esperamos antes de responder? Esa decisión intercambia latencia y garantía inmediata.

No configuramos niveles de consistencia hoy: primero debe quedar firme `consulta → partición → clustering`. Astra Serverless además aplica guardrails propios, por lo que no todas las opciones de Cassandra autogestionado están expuestas igual.
</details>
''')

    # 10) Hito: resultado individual + comparación + alternativa con razón + rediseño.
    i = find(cells, 'alternativa = input(')
    set_source(cells[i], '''
alternativa = input(
    "Alternativa de diseño que descartaste (ej. particionar solo por entidad): "
).strip()
razon_alternativa = input(
    "¿Por qué la descartaste para la consulta de Laura?: "
).strip()
consulta_no_soportada = input(
    "Una consulta profesional que esta tabla NO soporta bien: "
).strip()
nueva_particion = input(
    "Si esa consulta se volviera frecuente, ¿qué dato(s) usarías para localizar su nueva partición?: "
).strip()

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
- Fuente de menciones: {"vista real de Atlas" if vista_real else "respaldo; falta evidencia de vista real"}
- Alta: {niveles.get("alta", 0)}
- Media: {niveles.get("media", 0)}
- Baja: {niveles.get("baja", 0)}

## Regla de priorización
- Procesos iniciales: {len(secop)}
- Coincidencias por entidad: {len(paso1)}
- Candidatos: {len(candidatos)}
- Primer candidato: {primer_id} — {primer_entidad} — $ {primer_valor:,}
- Contexto que viajó desde Atlas: {primer_noticias} noticias — nivel {primer_nivel}

## Límite
Referencias de proceso citadas literalmente en prensa: {con_referencia} de {len(candidatos)}.
La evidencia periodística usada es por entidad; no demuestra irregularidad del contrato específico.

## Consulta que Cassandra debe servir
Para un corte y un departamento, devolver primero los procesos de mayor valor.

## Diseño elegido
PRIMARY KEY ((corte, departamento), valor_base, id_proceso)
CLUSTERING ORDER BY (valor_base DESC, id_proceso ASC)

## Evidencia individual de corrección
- Departamento: {departamento_hito}
- Top esperado con pandas: {ids_pd_hito}
- Top devuelto por Cassandra: {ids_cql_hito if ids_cql_hito else "NO VERIFICADO EN ASTRA"}
- Coincidencia exacta de IDs y orden: {"sí" if coincidencia_hito else "no verificada"}

## Alternativa descartada
{alternativa or "PENDIENTE"}

**Razón:** {razon_alternativa or "PENDIENTE"}

## Consulta que este modelo no responde bien
{consulta_no_soportada or "PENDIENTE"}

**Si fuera frecuente, nueva localización de partición:** {nueva_particion or "PENDIENTE"}

## Decisión
MongoDB conserva y transforma documentos flexibles; pandas materializa una regla auditable; Cassandra sirve una proyección desnormalizada para una consulta repetitiva conocida de antemano.
'''

with open("hito_s05_servicio_prioridades.md", "w", encoding="utf-8") as f:
    f.write(hito)

print(hito)
print("\nArchivos creados: s05_priorizacion.csv, hito_s05_servicio_prioridades.md")
''')

    i = find(cells, "## Rúbrica de calidad del hito")
    set_source(cells[i], '''
## Rúbrica de calidad del hito

| Criterio | Completo | Parcial | Sin evidencia | Peso |
|---|---|---|---|---:|
| Vista Atlas | identifica vista real y conserva 142 / 6-25-111 | usa respaldo y lo declara explícitamente | presenta números sin fuente | 15 |
| Regla + límite | reproduce 1.000→163→77 y explica por qué 0/77 limita la afirmación | reproduce números pero el límite es genérico | llama “irregulares” a los 77 o no registra el control | 20 |
| Query-first | PK y clustering responden `corte + departamento → top 5` y explica el orden | copia el diseño sin relacionarlo con la consulta | la clave no permite localizar esa consulta | 20 |
| Evidencia individual | registra departamento, top pandas, top CQL y coincidencia exacta | registra top pandas pero Astra no pudo verificarse y declara la contingencia | no hay resultado propio | 20 |
| Alternativa descartada | nombra una alternativa y explica por qué no sirve para esta consulta | nombra alternativa sin razón observable | no hay alternativa | 15 |
| Consulta no soportada | propone una consulta distinta y qué dato(s) localizarían otra partición | identifica la consulta pero no el rediseño | afirma que la tabla responde cualquier filtro | 10 |

Las autoevaluaciones son **formativas**. La evidencia que se revisa es el hito producido por la ejecución.
''')

    # Cierre: incorporar la prueba cruzada como parte de la historia.
    i = find(cells, "# Cierre")
    s = source(cells[i])
    if "verifiqué que dos motores" not in s:
        s = s.replace(
            "4. cuando apareció una consulta operacional repetitiva, **diseñé el almacenamiento desde esa pregunta**;\n5. comprobé que una tabla optimizada para una consulta **no es una tabla universal**.",
            "4. cuando apareció una consulta operacional repetitiva, **diseñé el almacenamiento desde esa pregunta**;\n5. **verifiqué que dos motores devolvieran el mismo top 5** antes de confiar en el servicio;\n6. comprobé que una tabla optimizada para una consulta **no es una tabla universal**.",
        )
        set_source(cells[i], s)

    # 11) Nunca enlazar el quiz de S1–S4 desde S5.
    texto = "\n".join(source(c) for c in cells)
    if "quiz_sesiones_1_a_4" in texto:
        raise RuntimeError("El quiz S1–S4 debe permanecer fuera de los enlaces de S5.")

    # 12) Codificar autoevaluaciones al final, cuando ya no habrá más transformaciones.
    codificar_autoevaluaciones(cells)

    NB.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    json.loads(NB.read_text(encoding="utf-8"))
    print(f"[OK] Mejora S5 aplicada: {len(cells)} celdas. JSON válido.")
    print("[OK] Vista Atlas viaja a la bandeja; pandas↔Cassandra queda como prueba de corrección.")
    print("[OK] Autoevaluaciones codificadas; quiz S1–S4 permanece fuera de enlaces.")


if __name__ == "__main__":
    main()
