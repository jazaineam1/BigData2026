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
    ("elasticsearch", "elasticsearch"),
]:
    if importlib.util.find_spec(modulo) is None:
        paquetes.append(paquete)

if paquetes:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *paquetes])

print("Entorno listo: pandas y cliente oficial de Elasticsearch disponibles.")
''')


def data_cell():
    return code('''
import pandas as pd

documentos = [
    {
        "id": "secop-001",
        "entidad": "Alcaldia de Cali",
        "departamento": "Valle del Cauca",
        "sector": "Tecnologia",
        "valor_millones": 880,
        "anio": 2025,
        "estado": "Adjudicado",
        "objeto": "Implementacion de tablero de seguimiento contractual y analitica publica",
        "descripcion": "Servicios para integrar fuentes de datos, generar indicadores y alertas de gestion contractual.",
    },
    {
        "id": "secop-002",
        "entidad": "Gobernacion de Antioquia",
        "departamento": "Antioquia",
        "sector": "Infraestructura",
        "valor_millones": 1450,
        "anio": 2025,
        "estado": "Adjudicado",
        "objeto": "Interventoria de obras viales con reportes de avance",
        "descripcion": "Seguimiento tecnico, financiero y documental de contratos de infraestructura vial.",
    },
    {
        "id": "secop-003",
        "entidad": "Secretaria de Salud de Bogota",
        "departamento": "Bogota",
        "sector": "Salud",
        "valor_millones": 620,
        "anio": 2026,
        "estado": "En ejecucion",
        "objeto": "Analitica de oportunidad en atencion ciudadana",
        "descripcion": "Procesamiento de solicitudes, tiempos de respuesta y deteccion de demoras en servicios.",
    },
    {
        "id": "secop-004",
        "entidad": "Alcaldia de Cali",
        "departamento": "Valle del Cauca",
        "sector": "Salud",
        "valor_millones": 310,
        "anio": 2026,
        "estado": "Publicado",
        "objeto": "Interoperabilidad de datos sociales y salud publica",
        "descripcion": "Integracion de datos sociales para priorizar poblacion vulnerable y monitorear cobertura.",
    },
    {
        "id": "secop-005",
        "entidad": "Universidad Publica del Caribe",
        "departamento": "Atlantico",
        "sector": "Educacion",
        "valor_millones": 410,
        "anio": 2026,
        "estado": "Adjudicado",
        "objeto": "Plataforma de analitica academica y permanencia estudiantil",
        "descripcion": "Modelos descriptivos para seguimiento de riesgo academico, permanencia y graduacion.",
    },
    {
        "id": "secop-006",
        "entidad": "Empresa de Servicios Publicos de Medellin",
        "departamento": "Antioquia",
        "sector": "Servicios publicos",
        "valor_millones": 990,
        "anio": 2026,
        "estado": "Adjudicado",
        "objeto": "Busqueda documental y trazabilidad de peticiones ciudadanas",
        "descripcion": "Motor de busqueda para expedientes, reclamos, respuestas y trazabilidad de atencion.",
    },
]

df = pd.DataFrame(documentos)
df
''')


def cloud_connection_cells():
    return [
        section_header("4", "Conexion segura a Elastic Cloud desde Colab"),
        md("""
Elastic Cloud permite crear una instancia administrada de Elasticsearch y Kibana. En Colab se recomienda usar el cliente oficial de Python con `cloud_id` y una API key o credenciales temporales.

Este cuaderno no guarda secretos. Si el estudiante no tiene cuenta lista, puede leer la plantilla, revisar el modelo de consulta y ejecutar las secciones conceptuales.
"""),
        ficha(
            "Elasticsearch()",
            "crea un cliente Python para enviar operaciones al cluster.",
            "`cloud_id` y `api_key`, o alternativamente URL y credenciales seguras.",
            "un objeto cliente con metodos como `index`, `search`, `indices.create` y `ping`.",
            "si `client.info()` responde, Colab esta conectado al servicio.",
        ),
        code('''
from getpass import getpass
from elasticsearch import Elasticsearch

ELASTIC_CLOUD_ID = input("Elastic Cloud ID (deja vacio para omitir conexion): ").strip()

if ELASTIC_CLOUD_ID:
    ELASTIC_API_KEY = getpass("Elastic API key: ")
    client = Elasticsearch(cloud_id=ELASTIC_CLOUD_ID, api_key=ELASTIC_API_KEY)
    info = client.info()
    print("Conexion activa con Elasticsearch.")
    print("Cluster:", info.get("cluster_name", "sin nombre visible"))
else:
    client = None
    print("Conexion omitida. Las celdas de consulta quedan como plantilla guiada.")
'''),
        interp(
            "conexion cloud",
            [
                "El `cloud_id` identifica el despliegue administrado; la API key autoriza operaciones.",
                "No debe escribirse la API key directamente en el notebook, porque el cuaderno puede compartirse o subirse al repositorio.",
                "Si no hay conexion en clase, la teoria y las plantillas siguen siendo validas para explicar el flujo.",
            ],
        ),
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
            "valor_millones": {"type": "integer"},
            "anio": {"type": "integer"},
            "objeto": {"type": "text", "analyzer": "texto_espanol_basico"},
            "descripcion": {"type": "text", "analyzer": "texto_espanol_basico"},
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
    ok, errores = bulk(client, acciones, refresh=True)
    print("Documentos cargados:", ok)
    print("Errores:", errores)
else:
    print("Acciones preparadas para bulk:")
    print(acciones[0])
'''),
        interp(
            "carga bulk",
            [
                "La carga masiva es la forma normal de indexar lotes de documentos.",
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

Buscar "analitica ciudadana" no es igual a filtrar `sector = Salud`. La busqueda textual intenta encontrar documentos relevantes por palabras; el filtro exige una condicion exacta.
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
            "query": "analitica ciudadana",
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
consulta_filtrada = {
    "query": {
        "bool": {
            "must": [
                {"match": {"descripcion": "datos"}}
            ],
            "filter": [
                {"term": {"departamento": "Valle del Cauca"}},
                {"range": {"valor_millones": {"gte": 300}}}
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
                "Con pocos documentos solo vemos la mecanica; con SECOP real este patron permite tableros y filtros exploratorios.",
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
Kibana es la interfaz visual del ecosistema Elastic. Para esta sesion interesa usarlo de forma concreta:

1. Abrir Kibana desde Elastic Cloud.
2. Crear un **Data View** sobre el indice `secop_texto_clase`.
3. Explorar documentos en Discover.
4. Crear visualizaciones basicas:
   - conteo por sector,
   - suma de valor por departamento,
   - tabla de entidades con mas documentos,
   - busqueda de texto en `objeto` o `descripcion`.
5. Guardar un dashboard simple.

## Interpretacion docente

Kibana no reemplaza el modelado del indice. Si el mapping esta mal, el dashboard tambien queda limitado. La visualizacion es la ultima capa de una cadena: documento, indice, mapping, consulta, agregacion y lectura.
"""),
        reflection(
            "lectura del dashboard",
            [
                "Que patron se ve por sector?",
                "Que filtro cambia mas el resultado: departamento, estado o texto buscado?",
                "Que no podemos concluir solo con este dashboard?",
            ],
        ),
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
1. Agrega tres documentos nuevos con objetos contractuales parecidos pero sectores distintos.
2. Ejecuta una consulta `multi_match` y observa como cambia el ranking.
3. Crea un filtro por valor superior a 800 millones.
4. Agrega una agregacion por departamento.
5. En Kibana, crea un Data View y una visualizacion de conteo por sector.
6. Escribe una conclusion: que encontro la busqueda textual que un filtro exacto no habria encontrado?
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

## Idea mas importante

Buscar texto no es lo mismo que filtrar columnas. Un motor de busqueda construye indices, analiza lenguaje y ordena resultados por relevancia.

## Errores comunes

- Indexar todo como texto y luego no poder agregar por categorias.
- Creer que el score equivale a importancia institucional.
- Guardar claves o secretos en el cuaderno.
- Crear dashboards sin revisar primero el mapping y la calidad del texto.

## Conexion con el proyecto final

El proyecto final puede usar una base documental para guardar contratos y un motor de busqueda para explorar objetos contractuales, hallazgos, descripciones y alertas por palabras clave. La arquitectura mejora cuando cada herramienta cumple un papel claro.
"""),
        section_header("12", "Referencias"),
        md("""
- Elasticsearch Python client: https://www.elastic.co/docs/reference/elasticsearch/clients/python/
- Elasticsearch Python client - connecting: https://www.elastic.co/docs/reference/elasticsearch/clients/python/connecting
- Elasticsearch mapping: https://www.elastic.co/docs/manage-data/data-store/mapping
- Elasticsearch analysis: https://www.elastic.co/docs/manage-data/data-store/text-analysis
- Elasticsearch query DSL: https://www.elastic.co/docs/explore-analyze/query-filter/languages/querydsl
- Elasticsearch aggregations: https://www.elastic.co/docs/explore-analyze/query-filter/aggregations
- Kibana Data Views: https://www.elastic.co/docs/explore-analyze/find-and-organize/data-views
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
4. Cargar documentos con `bulk`.
5. Ejecutar busquedas `match`, filtros y consultas booleanas.
6. Construir agregaciones para resumen analitico.
7. Entender el papel de Kibana en exploracion y dashboards.
8. Comparar Elasticsearch con MongoDB Atlas Search.
"""),
        md("""
## Agenda sugerida de 3 horas

| Momento | Tiempo | Actividad |
|---|---:|---|
| Apertura | 20 min | Por que busqueda no es lo mismo que filtro |
| Conceptos base | 30 min | Indice, documento, mapping, analyzer |
| Conexion cloud | 20 min | Cliente Python y credenciales seguras |
| Carga de datos | 30 min | Dataset SECOP reducido, mapping y bulk |
| Busquedas | 35 min | Match, filtros, ranking y lectura de resultados |
| Agregaciones | 25 min | Resumen por sector/departamento/valor |
| Kibana | 25 min | Data View, Discover y dashboard basico |
| Cierre | 15 min | Comparacion con Atlas Search y proyecto final |
"""),
        toc([
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
        data_cell(),
        interp(
            "dataset textual",
            [
                "Cada fila representa un documento tipo SECOP reducido.",
                "Los campos `objeto` y `descripcion` son candidatos a busqueda textual.",
                "Los campos `sector`, `departamento`, `estado`, `anio` y `valor_millones` son mejores para filtros o agregaciones.",
            ],
        ),
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
