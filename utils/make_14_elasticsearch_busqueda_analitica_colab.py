# -*- coding: utf-8 -*-
"""
Genera Cuadernos/14_Elasticsearch_Busqueda_Analitica_Colab.ipynb

Sesion 14: Elasticsearch para busqueda, relevancia y analitica de texto.
Ruta principal: Colab + Elastic Cloud.
"""

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.make_notebook import md, code, save, validate, uce_header, toc, section_header


OUTPUT = "Cuadernos/14_Elasticsearch_Busqueda_Analitica_Colab.ipynb"


def interp(titulo, puntos):
    return md(
        "### Interpretacion docente -- " + titulo + "\n\n"
        + "\n".join(f"- {p}" for p in puntos)
    )


def ficha(nombre, sirve, parametros, devuelve, interpreta):
    return md(f"""
### Mini ficha: `{nombre}`

| Elemento | Explicacion |
|---|---|
| Funcion o concepto | `{nombre}` |
| Para que sirve | {sirve} |
| Parametros usados | {parametros} |
| Que devuelve | {devuelve} |
| Como interpretar la salida | {interpreta} |
""")


def reflection(titulo, preguntas):
    return md(
        "### Pausa docente -- " + titulo + "\n\n"
        + "\n".join(f"- {p}" for p in preguntas)
    )


def install_cell():
    return code('''
import importlib.util
import subprocess
import sys

paquetes = []
for paquete, modulo in [
    ("pandas", "pandas"),
    ("requests", "requests"),
    ("elasticsearch", "elasticsearch"),
]:
    if importlib.util.find_spec(modulo) is None:
        paquetes.append(paquete)

if paquetes:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *paquetes])

print("Entorno listo: pandas y cliente oficial de Elasticsearch disponibles.")
''')


def elastic_free_tier_cells():
    return [
        md("""
## Verificacion de nivel gratis y costos

Para esta sesion hay una advertencia importante: **Elastic Cloud no debe presentarse como un plan gratuito permanente**. La ruta cloud se debe manejar como **trial/creditos/allowance sujeto a condiciones**, y el profesor debe verificar la cuenta antes de clase.

Segun la documentacion oficial vigente para 2026:

| Opcion | Que permite | Estado para clase | Advertencia |
|---|---|---|---|
| Elastic Cloud Serverless | Elasticsearch + Kibana administrados sin administrar servidores | Ruta recomendada para este tutorial | Puede generar cargos despues del trial o si se exceden condiciones. |
| Trial desde Elastic | Acceso temporal para probar Elastic Cloud | Util para laboratorio corto | Confirmar duracion y restricciones antes de la sesion. |
| AWS Marketplace trial | Trial de 7 dias indicado por Elastic FAQ | Alternativa si se usa AWS Marketplace | Despues del trial, los cargos pasan a la cuenta AWS. |
| Self-managed Basic | Elasticsearch autogestionado con funcionalidades gratuitas | No se usa en este cuaderno | Se omite porque la instruccion del curso fue trabajar solo con Colab y cloud. |

Decision para esta clase: el cuaderno deja **Elastic Cloud como ruta principal si la cuenta esta lista**, pero las celdas estan escritas como plantillas seguras. Si no hay trial activo, la clase puede explicar mapping, queries, bulk, agregaciones y Kibana sin ejecutar contra un cluster.
"""),
        interp(
            "Elastic y facturacion",
            [
                "No se debe pedir a estudiantes crear recursos sin explicar riesgo de costos.",
                "Elasticsearch es el tema del PDA, pero la ejecucion cloud debe prepararse con trial activo o cuenta institucional.",
                "El cuaderno evita servicios locales y credenciales guardadas; por eso la ruta de ejecucion real depende de Elastic Cloud.",
            ],
        ),
    ]


def elastic_platform_tutorial_cells():
    return [
        md("""
## Antes de programar: que cuenta necesito y que clave debo traer

Antes de ejecutar codigo, el estudiante debe salir de Elastic Cloud con dos datos claros. Si esos datos no estan listos, la celda de Python no tiene forma de adivinar la conexion.

| Que necesito antes de ejecutar | Donde se consigue | Como se llama en Elastic | Donde se pega en Colab | Como verifico que funciono |
|---|---|---|---|---|
| Cuenta Elastic Cloud con trial activo o cuenta institucional | https://cloud.elastic.co | Elastic Cloud account | No se pega; solo se usa para entrar al portal | El portal permite abrir el proyecto |
| Proyecto de Elasticsearch listo | Elastic Cloud Console | Serverless project | No se pega; debe estar en estado listo | Kibana abre sin errores |
| Direccion del recurso | Pantalla Getting started o Connection details | Elasticsearch endpoint | Variable `ELASTIC_ENDPOINT` | `client.info()` responde |
| Llave para consultar Elasticsearch | Kibana: Stack Management / API keys, o ruta de API keys del proyecto serverless | Elasticsearch API key | `getpass()` como `ELASTIC_API_KEY` | `client.ping()` y `client.info()` responden |

### Vocabulario minimo antes de pegar claves

| Palabra | Explicacion sin jerga |
|---|---|
| `Endpoint URL` | Direccion web del proyecto Serverless. Suele empezar por `https://...elastic.cloud`. Es el dato que se pega en Colab. |
| `API key` | Llave secreta que autoriza operaciones. Debe copiarse completa y no debe guardarse en el cuaderno. |
| `Kibana` | Interfaz web para administrar, explorar datos y crear visualizaciones. |
| `Data View` | Vista de Kibana que apunta a uno o varios indices para explorarlos en Discover y Lens. |
| `client` | Objeto Python que envia solicitudes a Elasticsearch. Si el cliente no conecta, ninguna busqueda funcionara. |
| `index` | Coleccion de documentos preparada para busqueda. En esta clase se llama `secop_texto_clase`. |
"""),
        md("""
### Tutorial paso a paso: crear el recurso y traer las claves

1. Entra a https://cloud.elastic.co.
2. Crea cuenta o inicia sesion con la cuenta institucional indicada por el profesor.
3. Verifica si tienes trial activo, creditos o permiso institucional. Si la cuenta pide tarjeta, confirma con el profesor antes de crear recursos.
4. Crea un **serverless project** de Elasticsearch.
5. Usa un nombre reconocible, por ejemplo `bigdata-u-central-secops`.
6. Elige una region cercana o la region sugerida por la institucion.
7. Espera hasta que el recurso aparezca como listo. No copies claves mientras el recurso esta creando componentes.
8. Copia el **Elasticsearch endpoint** que empieza por `https://...elastic.cloud`.
9. Copia la **API key** visible en Getting started o entra a la ruta de **API keys** del proyecto y crea una key con permiso para leer/escribir indices del laboratorio.
10. Abre **Kibana** desde el boton del proyecto.
11. Guarda temporalmente el endpoint y la API key en un lugar seguro. En Colab la API key se pega con `getpass()`, por eso no queda visible en pantalla.

### Distincion critica: no todas las llaves sirven para lo mismo

Elastic tiene dos familias de llaves que se confunden facil:

| Llave | Para que sirve | Sirve para `Elasticsearch(endpoint, api_key=...)` en esta clase? |
|---|---|---|
| Elastic Cloud API key | Administrar la organizacion y proyectos desde la API de Elastic Cloud. | No. Esa llave no es la que se usa para consultar documentos desde Python. |
| Elasticsearch API key | Leer, escribir, buscar y administrar indices dentro de Elasticsearch. | Si. Esta es la llave que debe pegarse en Colab. |

Si usas una **Elastic Cloud API key** donde Python espera una **Elasticsearch API key**, el proyecto existe pero la autenticacion falla. Ese error no significa que Elasticsearch este danado; significa que la llave no es la correcta para consultar datos.

### Cual dato pego segun tu pantalla

| Si tu pantalla muestra | Que pegas en Colab | Como conecta Python |
|---|---|---|
| `Elasticsearch endpoint: https://...elastic.cloud` | La URL completa | `Elasticsearch(endpoint, api_key=...)` |
| API key del proyecto | La cadena completa, pegada con `getpass()` | `api_key=ELASTIC_API_KEY` |
"""),
        interp(
            "preparacion antes del codigo",
            [
                "La conexion no empieza en Python: empieza verificando cuenta, proyecto Serverless, endpoint y llave correcta.",
                "Un error de autenticacion casi siempre se resuelve revisando que la llave sea de Elasticsearch, no de administracion de Elastic Cloud.",
                "El estudiante no debe compartir la API key por chat ni dejarla escrita en una celda.",
            ],
        ),
    ]


def data_cell():
    return [
        md("""
## Dataset real de clase: SECOP II - Contratos Electronicos

Para que Elasticsearch tenga sentido pedagogico, trabajaremos con contratos reales publicados en Datos Abiertos Colombia. La fuente es **SECOP II - Contratos Electronicos** (`jbjy-vk9h`), consultada mediante la API publica de Socrata.

La celda descarga al menos **10.000 contratos** con texto contractual real. Usaremos:

| Campo original SECOP II | Campo en el cuaderno | Uso en Elasticsearch |
|---|---|---|
| `id_contrato` | `id` | identificador del documento |
| `nombre_entidad` | `entidad` | filtro/agregacion |
| `departamento` | `departamento` | filtro/agregacion |
| `sector` | `sector` | filtro/agregacion |
| `estado_contrato` | `estado` | filtro/agregacion |
| `valor_del_contrato` | `valor_pesos`, `valor_millones` | metricas y rangos |
| `fecha_de_firma` | `fecha_firma`, `anio` | filtros temporales |
| `objeto_del_contrato` | `objeto` | busqueda textual |
| `descripcion_del_proceso` | `descripcion` | busqueda textual |

Comentario docente: ya no estamos probando con frases inventadas. Ahora el reto real es limpiar campos, controlar nulos, conservar texto util y preparar documentos para busqueda.
"""),
        code('''
import pandas as pd
import requests

SECOP_API = "https://www.datos.gov.co/resource/jbjy-vk9h.json"
N_CONTRATOS_OBJETIVO = 10_000
N_DESCARGA = 30_000

columnas_secop = [
    "id_contrato",
    "nombre_entidad",
    "departamento",
    "sector",
    "estado_contrato",
    "descripcion_del_proceso",
    "objeto_del_contrato",
    "tipo_de_contrato",
    "modalidad_de_contratacion",
    "valor_del_contrato",
    "fecha_de_firma",
    "proveedor_adjudicado",
    "urlproceso",
]

params = {
    "$limit": N_DESCARGA,
    "$select": ",".join(columnas_secop),
    "$where": (
        "fecha_de_firma IS NOT NULL "
        "AND descripcion_del_proceso IS NOT NULL "
        "AND objeto_del_contrato IS NOT NULL "
        "AND valor_del_contrato IS NOT NULL"
    ),
    "$order": "fecha_de_firma DESC",
}

respuesta = requests.get(SECOP_API, params=params, timeout=90)
if not respuesta.ok:
    print("URL consultada:", respuesta.url)
    respuesta.raise_for_status()

datos_json = respuesta.json()
if not isinstance(datos_json, list):
    raise RuntimeError(f"La API no devolvio una lista de contratos: {datos_json}")

raw = pd.DataFrame(datos_json)
print("Registros descargados desde SECOP II:", len(raw))

def columna(nombre, default=""):
    if nombre in raw.columns:
        return raw[nombre]
    return pd.Series([default] * len(raw))

def texto_limpio(serie, default="Sin dato"):
    return (
        serie.fillna(default)
        .astype(str)
        .str.replace(r"\\s+", " ", regex=True)
        .str.strip()
    )

def extraer_url(valor):
    if isinstance(valor, dict):
        return valor.get("url", "")
    if pd.isna(valor):
        return ""
    return str(valor)

ids = texto_limpio(columna("id_contrato"), "")
ids = ids.mask(ids.eq(""), [f"secop-ii-{i}" for i in range(len(ids))])

valor_pesos = pd.to_numeric(columna("valor_del_contrato"), errors="coerce").fillna(0)
fecha_firma = pd.to_datetime(columna("fecha_de_firma"), errors="coerce")
fecha_firma_texto = fecha_firma.dt.strftime("%Y-%m-%d")

df = pd.DataFrame({
    "id": ids,
    "entidad": texto_limpio(columna("nombre_entidad")),
    "departamento": texto_limpio(columna("departamento")),
    "sector": texto_limpio(columna("sector")),
    "estado": texto_limpio(columna("estado_contrato")),
    "valor_pesos": valor_pesos.round(0).astype("int64"),
    "valor_millones": (valor_pesos / 1_000_000).round(2),
    "fecha_firma": fecha_firma_texto.where(fecha_firma_texto.notna(), None),
    "anio": fecha_firma.dt.year.fillna(0).astype("int64"),
    "proveedor": texto_limpio(columna("proveedor_adjudicado")),
    "tipo_contrato": texto_limpio(columna("tipo_de_contrato")),
    "modalidad": texto_limpio(columna("modalidad_de_contratacion")),
    "objeto": texto_limpio(columna("objeto_del_contrato")),
    "descripcion": texto_limpio(columna("descripcion_del_proceso")),
    "urlproceso": columna("urlproceso").apply(extraer_url),
})

df = (
    df[
        (df["id"].str.len() > 0)
        & (df["objeto"].str.len() > 20)
        & (df["descripcion"].str.len() > 20)
    ]
    .drop_duplicates("id")
    .head(N_CONTRATOS_OBJETIVO)
    .reset_index(drop=True)
)

if len(df) < N_CONTRATOS_OBJETIVO:
    raise RuntimeError(
        f"Solo quedaron {len(df)} contratos limpios. "
        "Aumenta N_DESCARGA o revisa disponibilidad de la API."
    )

documentos = df.to_dict("records")

print("Contratos listos para Elasticsearch:", len(documentos))
print("Periodo cubierto:", int(df["anio"].min()), "-", int(df["anio"].max()))
print("Departamentos:", df["departamento"].nunique())
print("Sectores:", df["sector"].nunique())

df[[
    "id",
    "entidad",
    "departamento",
    "sector",
    "estado",
    "valor_millones",
    "anio",
    "objeto",
]].head(10)
'''),
        interp(
            "lectura inicial de SECOP II",
            [
                "Cada fila representa un contrato electronico publicado en SECOP II.",
                "Los campos `objeto` y `descripcion` son texto real: por eso son utiles para busqueda textual.",
                "Los campos `departamento`, `sector`, `estado`, `anio` y `valor_millones` permiten filtros y agregaciones.",
                "Este dataset sirve para ensenar busqueda; no debe leerse como auditoria completa sin controles adicionales de calidad y cobertura.",
            ],
        ),
    ]


def cloud_connection_cells():
    return [
        section_header("4", "Conexion segura a Elastic Cloud desde Colab"),
        md("""
Elastic Cloud Serverless permite crear un proyecto administrado de Elasticsearch y Kibana sin configurar servidores, nodos ni shards. En Colab usaremos el cliente oficial de Python con el **Elasticsearch endpoint** y una **Elasticsearch API key**.

Este cuaderno no guarda secretos. Si el estudiante no tiene cuenta lista, puede leer la plantilla, revisar el modelo de consulta y ejecutar las secciones conceptuales.

En este tutorial usaremos solo la ruta **Serverless**. Si tu pantalla muestra `Elasticsearch endpoint: https://...elastic.cloud`, ese es el valor que debes copiar.
"""),
        md("""
### Antes de ejecutar esta celda

| Que reviso | Como se ve cuando esta bien | Que hago si no esta listo |
|---|---|---|
| Cuenta o trial | Puedo entrar a Elastic Cloud Console | No ejecuto conexion; pido apoyo al profesor |
| Proyecto Serverless | Estado listo y Kibana abre | Espero o reviso facturacion/permisos |
| Elasticsearch endpoint | URL que empieza por `https://...elastic.cloud` | No uso la URL de Kibana |
| Elasticsearch API key | Llave visible en Getting started o creada en API keys del proyecto | No uso una Elastic Cloud API key |

La celda hace dos pruebas:

1. `client.ping()`: pregunta rapido si el servicio responde.
2. `client.info()`: solicita informacion del cluster. Si esta llamada responde, la conexion y la autenticacion funcionan.
"""),
        md("""
### Guia del cliente oficial de Elasticsearch en Python

El cliente `elasticsearch` es un cliente de bajo nivel: expone casi toda la API de Elasticsearch como metodos Python. En palabras simples, `client` es el mensajero entre Colab y Elasticsearch. Conviene aprenderlo por namespaces:

| Pieza del cliente | Que hace | Ejemplo de uso |
|---|---|---|
| `Elasticsearch(...)` | Crea el cliente conectado al proyecto Serverless. | `Elasticsearch(endpoint, api_key=...)` |
| `client.info()` | Consulta informacion del cluster. | Diagnostico inicial de conexion. |
| `client.indices.exists()` | Verifica si un indice existe. | Evitar crear dos veces el mismo indice. |
| `client.indices.create()` | Crea indice con settings y mapping. | Preparar campos `text`, `keyword`, `integer`. |
| `client.indices.delete()` | Elimina un indice. | Reiniciar laboratorio pequeno. |
| `client.index()` | Inserta o reemplaza un documento. | Carga individual. |
| `helpers.bulk()` | Carga muchos documentos. | Carga por lotes para datasets. |
| `client.search()` | Ejecuta busquedas y agregaciones. | `match`, `bool`, `filter`, `aggs`. |
| `client.get()` | Recupera documento por `_id`. | Verificar una carga especifica. |
| `client.update()` | Actualiza parcialmente un documento. | Corregir un campo sin reindexar todo. |
| `client.delete()` | Elimina un documento por `_id`. | Limpieza puntual. |
| `client.options(...)` | Crea una variante del cliente con opciones. | Timeouts, headers o parametros por llamada. |

Lectura clave: `indices.*` administra indices; `index/get/update/delete` trabaja documentos; `search` recupera y resume informacion.
"""),
        ficha(
            "client.search()",
            "envia una consulta de busqueda o agregacion al cluster.",
            "`index`, `query`, `aggs`, `size`, `sort` y otros parametros segun la API.",
            "un diccionario con `hits`, `_score`, `_source`, `aggregations` y metadatos.",
            "los resultados se leen separando documentos recuperados (`hits`) de resumenes calculados (`aggregations`).",
        ),
        ficha(
            "Elasticsearch()",
            "crea un cliente Python para enviar operaciones al cluster.",
            "`endpoint` copiado de la pantalla Getting started y `api_key` creada para Elasticsearch.",
            "un objeto cliente con metodos como `index`, `search`, `indices.create` y `ping`.",
            "si `client.info()` responde, Colab esta conectado al servicio.",
        ),
        code('''
from getpass import getpass
from elasticsearch import Elasticsearch

print("Antes de pegar datos revisa:")
print("1. El recurso de Elastic Cloud esta listo.")
print("2. Tienes el Elasticsearch endpoint que empieza por https://.")
print("3. Tienes una Elasticsearch API key, no una Elastic Cloud API key.")

ELASTIC_ENDPOINT = input("Pega el Elasticsearch endpoint (vacio para omitir conexion): ").strip()

if ELASTIC_ENDPOINT:
    ELASTIC_API_KEY = getpass("Pega la Elasticsearch API key: ").strip()

    try:
        if not ELASTIC_ENDPOINT.startswith("https://"):
            raise ValueError("El endpoint de Serverless debe empezar por https://")

        client = Elasticsearch(
            ELASTIC_ENDPOINT,
            api_key=ELASTIC_API_KEY,
            request_timeout=30,
        )
        ping_ok = client.ping()
        info = client.info()
    except Exception as exc:
        client = None
        print("No se pudo conectar con Elasticsearch.")
        print("Tipo de error:", type(exc).__name__)
        print("Detalle corto:", str(exc)[:500])
        print()
        print("Revision sugerida:")
        print("- Pega el Elasticsearch endpoint, no la URL de Kibana.")
        print("- El endpoint debe empezar por https:// y terminar normalmente en elastic.cloud:443.")
        print("- Si pegaste una Elastic Cloud API key, crea o copia una Elasticsearch API key.")
        print("- Si el proyecto no esta listo o el trial expiro, corrige eso antes de reintentar.")
        print("- Si la key no tiene permisos de indices, crea una key con permisos de lectura/escritura para el laboratorio.")
    else:
        print("Conexion activa con Elasticsearch.")
        print("Tipo de conexion: endpoint URL Serverless")
        print("Ping:", ping_ok)
        print("Cluster:", info.get("cluster_name", "sin nombre visible"))
        print("Version:", info.get("version", {}).get("number"))
else:
    client = None
    print("Conexion omitida. Las celdas de consulta quedan como plantilla guiada.")
'''),
        interp(
            "conexion cloud",
            [
                "Serverless trabaja con endpoint URL; en este tutorial esa es la unica forma de conexion.",
                "La Elasticsearch API key autoriza consultas e indexacion; el endpoint solo indica a que proyecto conectarse.",
                "No debe escribirse la API key directamente en el notebook, porque el cuaderno puede compartirse o subirse al repositorio.",
                "Si no hay conexion en clase, la teoria y las plantillas siguen siendo validas para explicar el flujo.",
            ],
        ),
        md("""
### Si te sale este error en Elastic Cloud

| Mensaje o sintoma | Causa frecuente | Que hacer |
|---|---|---|
| `ValueError` por formato de conexion | Pegaste un dato que no es el endpoint completo | Copia la URL completa del campo Elasticsearch endpoint |
| `El endpoint de Serverless debe empezar por https://` | Pegaste un nombre corto o un dato incompleto | Copia la URL completa del campo Elasticsearch endpoint |
| `AuthenticationException` o `401` | Pegaste una llave incorrecta o incompleta | Crea o copia una Elasticsearch API key nueva y pegala completa |
| `403` o permiso denegado | La llave existe pero no tiene permisos sobre indices | Crea una key con permisos para leer/escribir el indice `secop_texto_clase` |
| `ConnectionError` | Proyecto no esta listo, red temporal o trial vencido | Abre Elastic Cloud Console y verifica estado/facturacion |
| `client.ping()` devuelve `False` | El servicio no respondio a la prueba rapida | Ejecuta `client.info()` para ver detalle o revisa direccion y permisos |
"""),
        code('''
# Plantilla de diagnostico del cliente Elasticsearch.
# Ejecuta esta celda despues de crear `client`.

if client is not None:
    try:
        print("client.ping() =>", client.ping())
        info = client.info()
        print("Nombre del cluster:", info.get("cluster_name"))
        print("Version:", info.get("version", {}).get("number"))
        print("Conexion lista para crear indices y cargar documentos.")
    except Exception as exc:
        print("El cliente existe, pero la prueba fallo.")
        print("Tipo de error:", type(exc).__name__)
        print("Detalle corto:", str(exc)[:500])
else:
    print("No hay cliente conectado. Vuelve a la celda anterior y revisa endpoint, API key y estado del trial.")
'''),
    ]


def index_cells():
    return [
        section_header("5", "Crear indice, mapping y cargar documentos"),
        md("""
## Definicion formal

Un **indice** en Elasticsearch agrupa documentos que comparten una estructura de busqueda. El **mapping** define como se interpretan los campos: texto analizado, palabra clave exacta, numero, fecha, etc.

## Intuicion

No todo texto se busca igual. `objeto` y `descripcion` deben analizarse para buscar palabras relevantes. `entidad`, `sector` y `estado` suelen usarse como filtros exactos. `valor_millones` y `anio` sirven para rangos y agregaciones.
"""),
        ficha(
            "indices.create()",
            "crea un indice con configuracion y mapping.",
            "nombre del indice y cuerpo con tipos de campo.",
            "confirmacion de creacion o error si ya existe.",
            "un mapping correcto evita busquedas lentas, filtros incorrectos y agregaciones mal definidas.",
        ),
        code('''
INDEX_NAME = "secop_texto_clase"

mapping = {
    "settings": {
        "analysis": {
            "analyzer": {
                "texto_espanol_basico": {
                    "type": "standard",
                    "stopwords": "_spanish_"
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "entidad": {"type": "keyword"},
            "departamento": {"type": "keyword"},
            "sector": {"type": "keyword"},
            "estado": {"type": "keyword"},
            "proveedor": {"type": "keyword"},
            "tipo_contrato": {"type": "keyword"},
            "modalidad": {"type": "keyword"},
            "valor_pesos": {"type": "double"},
            "valor_millones": {"type": "double"},
            "fecha_firma": {"type": "date"},
            "anio": {"type": "integer"},
            "objeto": {"type": "text", "analyzer": "texto_espanol_basico"},
            "descripcion": {"type": "text", "analyzer": "texto_espanol_basico"},
            "urlproceso": {"type": "keyword", "index": False},
        }
    }
}

if client is not None:
    if client.indices.exists(index=INDEX_NAME):
        client.indices.delete(index=INDEX_NAME)
    client.indices.create(index=INDEX_NAME, **mapping)
    print("Indice creado:", INDEX_NAME)
else:
    print("Plantilla de mapping lista. Conecta Elastic Cloud para ejecutarla.")
'''),
        interp(
            "mapping",
            [
                "`keyword` permite filtros y agregaciones exactas; `text` permite busqueda por terminos analizados.",
                "El analyzer en espanol elimina palabras vacias frecuentes y prepara el texto para busqueda.",
                "Un error comun es dejar que todo se infiera automaticamente y luego descubrir que una agregacion no funciona como se esperaba.",
            ],
        ),
        ficha(
            "helpers.bulk()",
            "envia muchos documentos al indice en una sola operacion eficiente.",
            "cliente y lista de acciones con `_index`, `_id` y `_source`.",
            "conteo de documentos cargados o errores de carga.",
            "si la carga es correcta, el indice ya puede responder busquedas y agregaciones.",
        ),
        code('''
from elasticsearch.helpers import bulk

acciones = [
    {
        "_index": INDEX_NAME,
        "_id": doc["id"],
        "_source": {k: v for k, v in doc.items() if k != "id"},
    }
    for doc in documentos
]

if client is not None:
    ok, errores = bulk(
        client,
        acciones,
        refresh=True,
        chunk_size=500,
        request_timeout=120,
        raise_on_error=False,
    )
    print("Documentos cargados:", ok)
    print("Errores:", len(errores))
    if errores:
        print("Primer error:", errores[0])
else:
    print("Acciones preparadas para bulk:")
    print(acciones[0])
'''),
        interp(
            "carga bulk",
            [
                "La carga masiva es la forma normal de indexar lotes grandes como los 10.000 contratos de SECOP II.",
                "Indexar no es solo guardar: es preparar estructuras para buscar rapido por texto, filtros y agregaciones.",
                "Todavia no hay conclusion analitica; apenas dejamos el indice listo para preguntar.",
            ],
        ),
    ]


def query_cells():
    return [
        section_header("6", "Busquedas: match, filtros y ranking"),
        md("""
## Definicion formal

Una consulta `match` busca texto analizado. Elasticsearch calcula una puntuacion de relevancia para ordenar resultados. Los filtros restringen el universo sin aportar relevancia textual.

## Intuicion

Buscar "servicios profesionales apoyo gestion" no es igual a filtrar `sector = defensa`. La busqueda textual intenta encontrar documentos relevantes por palabras; el filtro exige una condicion exacta.
"""),
        ficha(
            "search()",
            "ejecuta una busqueda sobre uno o varios indices.",
            "indice y cuerpo de consulta con `query`, `filter`, `aggs` o `sort`.",
            "hits, puntuaciones, total y agregaciones.",
            "los hits se leen como documentos ordenados por relevancia o por el criterio indicado.",
        ),
        code('''
consulta_match = {
    "query": {
        "multi_match": {
            "query": "servicios profesionales apoyo gestion",
            "fields": ["objeto^2", "descripcion"]
        }
    }
}

if client is not None:
    resp = client.search(index=INDEX_NAME, **consulta_match)
    resultados = [
        {
            "score": hit["_score"],
            "entidad": hit["_source"]["entidad"],
            "departamento": hit["_source"]["departamento"],
            "valor_millones": hit["_source"]["valor_millones"],
            "objeto": hit["_source"]["objeto"],
            "sector": hit["_source"]["sector"],
        }
        for hit in resp["hits"]["hits"]
    ]
    pd.DataFrame(resultados)
else:
    consulta_match
'''),
        interp(
            "match y relevancia",
            [
                "El campo `objeto` tiene mas peso con `^2`, porque en este caso resume mejor la intencion del contrato.",
                "La puntuacion no es verdad absoluta; es una medida de coincidencia segun el analizador, los terminos y la estructura de la consulta.",
                "No debemos confundir relevancia textual con importancia financiera o riesgo contractual.",
            ],
        ),
        code('''
departamento_objetivo = df["departamento"].value_counts().index[0]
umbral_valor = float(df["valor_millones"].quantile(0.75))

print("Departamento usado en el filtro:", departamento_objetivo)
print("Umbral de valor en millones:", round(umbral_valor, 2))

consulta_filtrada = {
    "query": {
        "bool": {
            "must": [
                {"match": {"descripcion": "servicios"}}
            ],
            "filter": [
                {"term": {"departamento": departamento_objetivo}},
                {"range": {"valor_millones": {"gte": umbral_valor}}}
            ]
        }
    }
}

if client is not None:
    resp = client.search(index=INDEX_NAME, **consulta_filtrada)
    pd.DataFrame([
        {
            "score": hit["_score"],
                "entidad": hit["_source"]["entidad"],
                "departamento": hit["_source"]["departamento"],
                "valor_millones": hit["_source"]["valor_millones"],
                "objeto": hit["_source"]["objeto"],
            }
        for hit in resp["hits"]["hits"]
    ])
else:
    consulta_filtrada
'''),
        interp(
            "filtros",
            [
                "El filtro por departamento y valor reduce el universo de documentos antes de interpretar resultados.",
                "El `must` textual aporta relevancia; el filtro exacto aporta condiciones de negocio.",
                "Un error comun es usar busqueda textual para campos que realmente requieren filtros exactos.",
            ],
        ),
    ]


def aggregation_cells():
    return [
        section_header("7", "Agregaciones analiticas"),
        md("""
Las agregaciones convierten el indice en una fuente de resumen: conteos por categoria, promedios, sumas, histogramas y combinaciones. Esta capacidad es clave para conectar busqueda con analitica.
"""),
        ficha(
            "aggs",
            "calcula metricas o agrupaciones sobre documentos.",
            "nombre de agregacion, tipo como `terms`, `avg`, `sum` o `range`, y campo.",
            "buckets y metricas calculadas.",
            "cada bucket resume un subconjunto de documentos; no reemplaza una lectura cuidadosa de los casos individuales.",
        ),
        code('''
consulta_aggs = {
    "size": 0,
    "aggs": {
        "por_sector": {
            "terms": {"field": "sector"},
            "aggs": {
                "valor_promedio": {"avg": {"field": "valor_millones"}},
                "valor_total": {"sum": {"field": "valor_millones"}}
            }
        }
    }
}

if client is not None:
    resp = client.search(index=INDEX_NAME, **consulta_aggs)
    pd.DataFrame([
        {
            "sector": bucket["key"],
            "contratos": bucket["doc_count"],
            "valor_promedio": round(bucket["valor_promedio"]["value"], 2),
            "valor_total": bucket["valor_total"]["value"],
        }
        for bucket in resp["aggregations"]["por_sector"]["buckets"]
    ])
else:
    consulta_aggs
'''),
        interp(
            "agregaciones",
            [
                "La agregacion resume los documentos indexados por sector.",
                "Con 10.000 contratos reales, este patron ya permite una exploracion inicial para tableros y filtros.",
                "Una agregacion no prueba causalidad ni desempeno; describe distribuciones dentro del indice.",
            ],
        ),
        reflection(
            "mini-reto de agregaciones",
            [
                "Agrega una agregacion por `estado` dentro de cada sector.",
                "Cambia la metrica para calcular el valor maximo por sector.",
                "Explica que grafico construirias en Kibana con esta agregacion.",
            ],
        ),
    ]


def kibana_cells():
    return [
        section_header("8", "Kibana: Data Views y dashboard basico"),
        md("""
Kibana es la interfaz visual del ecosistema Elastic. En esta clase no se usa como adorno: se usa para comprobar que el indice existe, explorar documentos y construir un tablero inicial.

### Antes de entrar a Kibana

| Que necesito | Donde se consigue | Como se llama en Elastic | Como verifico que funciono |
|---|---|---|---|
| Indice cargado desde Colab | Celda de bulk indexing | `secop_texto_clase` | `client.indices.exists(index=INDEX_NAME)` devuelve `True` |
| Acceso web a Kibana | Boton Open Kibana del proyecto | Kibana | La pantalla principal abre sin error |
| Vista sobre el indice | Kibana > Stack Management > Data Views | Data View | Discover muestra documentos |

### Tutorial paso a paso: crear Data View y explorar

1. En Elastic Cloud Console abre el proyecto Serverless usado en Colab.
2. Haz clic en **Open Kibana**.
3. En Kibana entra a **Stack Management**.
4. Abre **Data Views**.
5. Crea un Data View con el patron `secop_texto_clase`.
6. Si Kibana pide campo de tiempo, selecciona `fecha_firma`.
7. Abre **Discover**.
8. Selecciona el Data View `secop_texto_clase`.
9. Revisa que aparezcan documentos con campos como `entidad`, `sector`, `estado`, `objeto`, `descripcion`, `valor_millones` y `anio`.
10. Prueba una busqueda textual, por ejemplo `servicios profesionales` o `interventoria`.
11. Agrega filtros por `sector` o `estado` para ver como cambia la lista.

### Tutorial paso a paso: visualizacion basica

1. Entra a **Visualize Library** o **Dashboard** y crea una visualizacion nueva con Lens.
2. Usa `secop_texto_clase` como fuente.
3. Crea una barra con conteo de documentos por `sector.keyword` si el mapping creo subcampo keyword, o por `sector` si aparece disponible como categoria.
4. Crea otra visualizacion con suma de `valor_millones` por `departamento`.
5. Agrega una tabla con `entidad` y conteo de documentos.
6. Guarda cada visualizacion con nombres claros, por ejemplo `Conteo por sector - SECOP clase`.
7. Crea un dashboard y agrega las visualizaciones.

## Interpretacion docente

Kibana no reemplaza el modelado del indice. Si el mapping esta mal, el dashboard tambien queda limitado. La visualizacion es la ultima capa de una cadena: documento, indice, mapping, consulta, agregacion y lectura.

### Que se puede y que no se puede concluir

| Lectura del dashboard | Conclusion responsable |
|---|---|
| Un sector tiene mas documentos | Hay mas registros cargados para ese sector en este dataset de clase |
| Un departamento suma mas valor | En los documentos cargados, ese departamento concentra mayor valor registrado |
| Una palabra aparece en varios objetos | Esa palabra es relevante para explorar, pero no prueba causalidad ni irregularidad |
| Un proveedor o entidad aparece varias veces | Puede ser un patron de participacion, no una evidencia por si sola |
"""),
        reflection(
            "lectura del dashboard",
            [
                "Que patron se ve por sector?",
                "Que filtro cambia mas el resultado: departamento, estado o texto buscado?",
                "Que no podemos concluir solo con este dashboard?",
            ],
        ),
        md("""
### Si algo no aparece en Kibana

| Sintoma | Causa frecuente | Accion sugerida |
|---|---|---|
| No aparece el indice | La carga desde Colab no se ejecuto o fallo | Vuelve a la celda de carga y verifica `client.indices.exists()` |
| Discover muestra cero documentos | El Data View apunta a otro patron o hay filtro activo | Revisa el patron y limpia filtros |
| No puedo agrupar por una columna de texto | El campo quedo como `text` sin variante exacta | Usa campos `keyword` para categorias o revisa el mapping |
| Las cifras no coinciden con lo esperado | El dataset es reducido y pedagogico | Interpreta como ejemplo de clase, no como auditoria real |
"""),
    ]


def comparison_cells():
    return [
        section_header("9", "Comparacion con MongoDB Atlas Search"),
        md("""
MongoDB Atlas Search y Elasticsearch pueden resolver busqueda textual, pero nacen de contextos distintos.

| Necesidad | MongoDB Atlas Search | Elasticsearch |
|---|---|---|
| La aplicacion ya vive sobre documentos MongoDB | Muy conveniente | Posible, pero exige sincronizar datos |
| Busqueda textual como producto central | Bueno | Muy fuerte y especializado |
| Observabilidad, dashboards y exploracion en Kibana | No es su foco principal | Es parte natural del ecosistema |
| Arquitectura con indice dedicado de busqueda | Puede hacerse | Es el caso clasico |

La decision depende de arquitectura: si el documento operacional esta en MongoDB y la busqueda es complementaria, Atlas Search puede ser suficiente. Si la busqueda, relevancia, analitica textual y dashboards son el nucleo del producto, Elasticsearch suele ser mas natural.
"""),
        interp(
            "comparacion responsable",
            [
                "No se trata de declarar un ganador universal.",
                "La herramienta correcta depende de donde viven los datos, que tan importante es la busqueda y quien consumira los resultados.",
                "En el proyecto final, MongoDB puede ser la capa documental y Elasticsearch una capa especializada si el producto exige busqueda textual avanzada.",
            ],
        ),
        section_header("10", "Ejercicios guiados"),
        md("""
1. Selecciona tres contratos recuperados por busqueda textual y compara sus `objeto`, `descripcion`, `sector` y `valor_millones`.
2. Ejecuta una consulta `multi_match` con otra frase real, por ejemplo `mantenimiento infraestructura educativa`.
3. Crea un filtro con el departamento mas frecuente y contratos por encima del percentil 90 de valor.
4. Agrega una agregacion por departamento y otra por modalidad.
5. En Kibana, crea un Data View con `fecha_firma` como campo temporal y una visualizacion de conteo por sector.
6. Escribe una conclusion: que encontro la busqueda textual en 10.000 contratos que un filtro exacto no habria encontrado?
"""),
        section_header("11", "Cierre de sesion"),
        md("""
## Recapitulacion

- Elasticsearch organiza documentos en indices preparados para busqueda.
- El mapping define como se comportan los campos.
- Los analyzers transforman texto para hacerlo buscable.
- `match` y `multi_match` trabajan con relevancia textual.
- Los filtros restringen por condiciones exactas.
- Las agregaciones resumen documentos y alimentan tableros.
- Kibana permite explorar, visualizar y comunicar resultados.
- La clase uso datos reales de SECOP II, no ejemplos inventados.

## Idea mas importante

Buscar texto no es lo mismo que filtrar columnas. Un motor de busqueda construye indices, analiza lenguaje y ordena resultados por relevancia.

## Errores comunes

- Indexar todo como texto y luego no poder agregar por categorias.
- Creer que el score equivale a importancia institucional.
- Guardar claves o secretos en el cuaderno.
- Crear dashboards sin revisar primero el mapping y la calidad del texto.
- Concluir irregularidades solo por frecuencia, valor o ranking textual.

## Conexion con el proyecto final

El proyecto final puede usar una base documental para guardar contratos y un motor de busqueda para explorar objetos contractuales, hallazgos, descripciones y alertas por palabras clave. La arquitectura mejora cuando cada herramienta cumple un papel claro.
"""),
        section_header("12", "Referencias"),
        md("""
- Elasticsearch Python client: https://www.elastic.co/docs/reference/elasticsearch/clients/python/
- Elasticsearch Python client - connecting: https://www.elastic.co/docs/reference/elasticsearch/clients/python/connecting
- Elastic Cloud API keys: https://www.elastic.co/docs/deploy-manage/api-keys/elastic-cloud-api-keys
- Elasticsearch mapping: https://www.elastic.co/docs/manage-data/data-store/mapping
- Elasticsearch analysis: https://www.elastic.co/docs/manage-data/data-store/text-analysis
- Elasticsearch query DSL: https://www.elastic.co/docs/explore-analyze/query-filter/languages/querydsl
- Elasticsearch aggregations: https://www.elastic.co/docs/explore-analyze/query-filter/aggregations
- Kibana Data Views: https://www.elastic.co/docs/explore-analyze/find-and-organize/data-views
- Datos Abiertos Colombia - SECOP II Contratos Electronicos: https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h
- Socrata API - SoQL queries: https://dev.socrata.com/docs/queries/
- MongoDB Atlas Search: https://www.mongodb.com/docs/atlas/atlas-search/

Documentacion revisada para la version vigente del curso 2026.
"""),
    ]


def build_cells():
    cells = [
        *uce_header(
            title="Elasticsearch: busqueda, relevancia y analitica de texto",
            session=14,
            github_path="main/Cuadernos/14_Elasticsearch_Busqueda_Analitica_Colab.ipynb",
            nota_plataforma="Google Colab + Elastic Cloud",
        ),
        md("""
## Alcance de la sesion

Esta sesion cubre el tema del PDA sobre implementacion practica de Elasticsearch. La clase esta pensada para Colab y Elastic Cloud: no requiere servicios locales.

El objetivo es entender como un motor de busqueda organiza texto, calcula relevancia y permite construir analitica exploratoria sobre documentos.
"""),
        md("""
## Objetivos de aprendizaje

Al finalizar la clase deberias poder:

1. Explicar que son indice, documento, mapping y analyzer.
2. Conectar Colab con Elastic Cloud sin exponer credenciales.
3. Crear un indice con campos de texto, categorias y metricas.
4. Cargar al menos 10.000 contratos reales de SECOP II con `bulk`.
5. Ejecutar busquedas `match`, filtros y consultas booleanas.
6. Construir agregaciones para resumen analitico.
7. Entender el papel de Kibana en exploracion y dashboards.
8. Comparar Elasticsearch con MongoDB Atlas Search.
"""),
        *elastic_free_tier_cells(),
        *elastic_platform_tutorial_cells(),
        toc([
            "Antes de programar -- Cuenta, endpoint y API key",
            "Seccion 1 -- Por que Elasticsearch importa",
            "Seccion 2 -- Conceptos base",
            "Seccion 3 -- Dataset de clase",
            "Seccion 4 -- Conexion segura a Elastic Cloud",
            "Seccion 5 -- Crear indice, mapping y cargar documentos",
            "Seccion 6 -- Busquedas: match, filtros y ranking",
            "Seccion 7 -- Agregaciones analiticas",
            "Seccion 8 -- Kibana",
            "Seccion 9 -- Comparacion con MongoDB Atlas Search",
            "Seccion 10 -- Ejercicios guiados",
            "Seccion 11 -- Cierre",
        ]),
        section_header("1", "Por que Elasticsearch importa"),
        md("""
## Por que importa

Muchas preguntas reales empiezan con texto: objetos contractuales, quejas ciudadanas, expedientes, observaciones, noticias, reportes tecnicos o correos. Un filtro exacto no basta cuando el usuario busca por palabras, sinonimos, frases incompletas o relevancia.

Elasticsearch aparece como una capa especializada para buscar, ordenar y resumir documentos textuales.

## Ejemplo manual pequeno

Si una persona busca:

```text
demoras en atencion ciudadana
```

El sistema no deberia exigir coincidencia exacta. Deberia encontrar documentos que hablen de tiempos de respuesta, solicitudes, retrasos, servicios y atencion, aunque las palabras no sean identicas.
"""),
        reflection(
            "antes de indexar",
            [
                "Que campos deben buscarse por texto?",
                "Que campos deben filtrarse de forma exacta?",
                "Que metricas se quieren resumir en un tablero?",
            ],
        ),
        section_header("2", "Conceptos base"),
        md("""
## Definicion formal

- **Documento:** unidad JSON que se indexa.
- **Indice:** coleccion logica de documentos buscables.
- **Mapping:** definicion de tipos de campo.
- **Analyzer:** proceso que transforma texto en terminos buscables.
- **Query:** instruccion para recuperar documentos.
- **Relevancia:** puntaje que ordena resultados segun coincidencia textual.
- **Agregacion:** resumen calculado sobre documentos.

## Intuicion

Elasticsearch no guarda texto como una lista simple. Construye estructuras de busqueda para responder rapido: que documentos contienen ciertos terminos, que tan relevantes son y como se resumen por categorias.
"""),
        install_cell(),
        section_header("3", "Dataset de clase"),
        *data_cell(),
        *cloud_connection_cells(),
        *index_cells(),
        *query_cells(),
        *aggregation_cells(),
        *kibana_cells(),
        *comparison_cells(),
    ]
    return cells


if __name__ == "__main__":
    cells = build_cells()
    validate(cells)
    save(cells, OUTPUT)
