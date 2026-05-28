# -*- coding: utf-8 -*-
"""
Genera Cuadernos/13_NoSQL_Grafos_Columnar_Colab.ipynb

Sesion 13: NoSQL con grafos, columnares y conexion con documental.
Ruta principal: Colab + servicios cloud gratuitos o paquetes instalables con pip.
"""

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.make_notebook import md, code, save, validate, uce_header, toc, section_header


OUTPUT = "Cuadernos/13_NoSQL_Grafos_Columnar_Colab.ipynb"


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
    ("kuzu", "kuzu"),
    ("neo4j", "neo4j"),
    ("cassandra-driver", "cassandra"),
]:
    if importlib.util.find_spec(modulo) is None:
        paquetes.append(paquete)

if paquetes:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *paquetes])

print("Entorno listo: pandas, KuzuDB, Neo4j driver y Cassandra driver disponibles.")
''')


def free_tier_cells():
    return [
        md("""
## Verificacion de niveles gratis para esta clase

Antes de pedir cuentas a estudiantes, conviene separar **gratis permanente**, **plan free con limites** y **creditos/trial**. Revisado con documentacion oficial vigente para 2026:

| Herramienta | Que se puede usar en clase | Estado del nivel gratis | Advertencia docente |
|---|---|---|---|
| KuzuDB | Practica local en Colab con `pip install kuzu` | Libre y open source, licencia MIT | No requiere cuenta ni servicio cloud. |
| Neo4j AuraDB | Base de grafos administrada | Tiene plan Free para aprender y prototipar | Tiene limites de nodos/relaciones; bases Free inactivas pueden eliminarse. |
| Astra DB Serverless | Cassandra/Astra como servicio | Tiene plan Free con creditos mensuales | Al consumir creditos la base puede hibernar; maximo 5 bases serverless en Free. |

Decision para esta sesion: **KuzuDB sera la practica garantizada en Colab**. Neo4j Aura y Astra DB se usan como rutas cloud opcionales para ver clientes reales administrados.
"""),
        interp(
            "costos y ejecucion en clase",
            [
                "La practica no depende de tarjeta de credito: KuzuDB cubre el laboratorio ejecutable en Colab.",
                "Aura y Astra son valiosos para conocer clientes reales, pero deben prepararse antes de clase y revisar limites actuales.",
                "Si una cuenta gratuita hiberna, se elimina o bloquea operaciones por creditos, el aprendizaje no se pierde: se continua con la ruta local y la plantilla del cliente.",
            ],
        ),
    ]


def data_cell():
    return code('''
import pandas as pd

contratos = pd.DataFrame([
    {
        "contrato_id": "C-001",
        "entidad": "Alcaldia de Cali",
        "proveedor": "Analitica Publica SAS",
        "sector": "Tecnologia",
        "valor_millones": 880,
        "estado": "Adjudicado",
        "objeto": "Implementacion de tablero de seguimiento contractual",
        "anio": 2025,
    },
    {
        "contrato_id": "C-002",
        "entidad": "Gobernacion de Antioquia",
        "proveedor": "Infraestructura Datos LTDA",
        "sector": "Infraestructura",
        "valor_millones": 1450,
        "estado": "Adjudicado",
        "objeto": "Servicios de interventoria y analitica territorial",
        "anio": 2025,
    },
    {
        "contrato_id": "C-003",
        "entidad": "Secretaria de Salud de Bogota",
        "proveedor": "Salud Digital SAS",
        "sector": "Salud",
        "valor_millones": 620,
        "estado": "En ejecucion",
        "objeto": "Analitica de oportunidad en atencion ciudadana",
        "anio": 2026,
    },
    {
        "contrato_id": "C-004",
        "entidad": "Alcaldia de Cali",
        "proveedor": "Salud Digital SAS",
        "sector": "Salud",
        "valor_millones": 310,
        "estado": "Publicado",
        "objeto": "Soporte para interoperabilidad de datos sociales",
        "anio": 2026,
    },
    {
        "contrato_id": "C-005",
        "entidad": "Universidad Publica del Caribe",
        "proveedor": "Analitica Publica SAS",
        "sector": "Educacion",
        "valor_millones": 410,
        "estado": "Adjudicado",
        "objeto": "Plataforma de analitica academica y permanencia estudiantil",
        "anio": 2026,
    },
])

contratos
''')


def kuzu_client_guide_cells():
    return [
        md("""
### Guia del cliente KuzuDB en Python

KuzuDB es una base de grafos embebida: el proceso de Python abre la base directamente, sin servidor intermedio. Eso la hace muy conveniente para Colab y para aprender el modelo de grafos antes de usar una plataforma administrada.

| Pieza del cliente | Que hace | Cuando la usamos |
|---|---|---|
| `kuzu.Database(ruta)` | Crea o abre una base de datos embebida. | Al inicio de la practica local. |
| `kuzu.Connection(db)` | Abre un canal de ejecucion contra la base. | Antes de crear tablas, cargar nodos o consultar. |
| `conn.execute(cypher, parametros)` | Ejecuta Cypher con parametros opcionales. | Para DDL, carga y consultas. |
| `QueryResult.get_as_df()` | Convierte el resultado a Pandas. | Cuando queremos interpretar una tabla en clase. |
| `QueryResult.get_all()` | Devuelve todas las filas como lista. | Para inspecciones pequenas o depuracion. |
| `QueryResult.has_next()` / `get_next()` | Lee resultados fila por fila. | Util cuando no queremos materializar todo. |

La idea clave: **KuzuDB se usa como una libreria Python**, pero internamente ejecuta Cypher sobre un modelo de grafo.
"""),
        ficha(
            "conn.execute(cypher, parametros)",
            "envia una instruccion Cypher a KuzuDB.",
            "texto Cypher y, opcionalmente, un diccionario de parametros como `{'nombre': entidad}`.",
            "un `QueryResult` si la instruccion produce filas, o una confirmacion interna si modifica el grafo.",
            "si devuelve filas, conviene pasarlas a `get_as_df()` para leerlas como tabla; si modifica datos, conviene imprimir una confirmacion y luego consultar.",
        ),
        md("""
#### Flujo mental del cliente Kuzu

1. **Abrir base:** `db = kuzu.Database(ruta)`.
2. **Abrir conexion:** `conn = kuzu.Connection(db)`.
3. **Definir esquema:** `CREATE NODE TABLE`, `CREATE REL TABLE`.
4. **Cargar datos:** `MERGE` para cargas pequenas re-ejecutables o `COPY` para volumenes grandes.
5. **Consultar patrones:** `MATCH ... RETURN ...`.
6. **Interpretar:** convertir resultados a DataFrame y leerlos con una pregunta de negocio.

En esta clase usamos `MERGE` porque el dataset es pequeno y porque ayuda a que la celda sea re-ejecutable. Para cargas masivas, la documentacion de Kuzu recomienda `COPY` o cargas desde archivos.
"""),
        code('''
# Plantilla minima de uso del cliente KuzuDB.
# Esta celda es de lectura: resume el patron que usaremos abajo.

plantilla_kuzu = {
    "abrir_base": "db = kuzu.Database(ruta)",
    "abrir_conexion": "conn = kuzu.Connection(db)",
    "crear_tabla_nodo": "conn.execute('CREATE NODE TABLE Entidad(nombre STRING, PRIMARY KEY(nombre))')",
    "crear_tabla_relacion": "conn.execute('CREATE REL TABLE CONTRATA(FROM Entidad TO Proveedor, contrato_id STRING)')",
    "insertar_o_reusar": "conn.execute('MERGE (:Entidad {nombre: $nombre})', {'nombre': 'Alcaldia'})",
    "consultar": "conn.execute('MATCH (e:Entidad) RETURN e.nombre AS entidad').get_as_df()",
}

plantilla_kuzu
'''),
        interp(
            "cliente KuzuDB",
            [
                "La conexion no apunta a una URL externa; apunta a una base embebida en el entorno de Colab.",
                "Los parametros evitan construir strings manualmente y hacen mas claro que datos cambian en cada ejecucion.",
                "`get_as_df()` no es la consulta: solo transforma el resultado para leerlo mejor en clase.",
            ],
        ),
    ]


def kuzu_cells():
    return [
        section_header("4", "Practica de grafos en Colab con KuzuDB"),
        md("""
KuzuDB permite practicar el modelo de grafos desde Colab sin levantar servicios externos. La idea no es reemplazar una plataforma empresarial, sino comprender el lenguaje mental del grafo: nodos, relaciones y recorridos.

En esta practica convertiremos la tabla de contratos en un grafo:

| Tipo | Significado |
|---|---|
| `Entidad` | comprador o entidad publica |
| `Proveedor` | organizacion contratista |
| `Sector` | dominio tematico del contrato |
| `CONTRATA` | relacion entre entidad y proveedor |
| `TRABAJA_EN` | relacion entre proveedor y sector |

La pregunta cambia: ya no queremos solo contar filas. Queremos encontrar caminos, proveedores compartidos y concentraciones relacionales.
"""),
        *kuzu_client_guide_cells(),
        ficha(
            "kuzu.Database()",
            "crea o abre una base de grafos embebida.",
            "ruta local temporal del proyecto de clase.",
            "un objeto base de datos que puede recibir conexiones.",
            "si la base se crea correctamente, ya existe un espacio donde definir nodos y relaciones.",
        ),
        ficha(
            "conn.execute()",
            "ejecuta instrucciones Cypher en KuzuDB.",
            "texto de consulta Cypher.",
            "un resultado consultable o una confirmacion de ejecucion.",
            "cada consulta debe leerse como una pregunta sobre patrones de relacion.",
        ),
        code('''
import os
import shutil
import tempfile
import kuzu

base_dir = os.path.join(tempfile.gettempdir(), "kuzu_secop_clase")
if os.path.exists(base_dir):
    shutil.rmtree(base_dir)

db = kuzu.Database(base_dir)
conn = kuzu.Connection(db)

conn.execute("CREATE NODE TABLE Entidad(nombre STRING, PRIMARY KEY(nombre))")
conn.execute("CREATE NODE TABLE Proveedor(nombre STRING, PRIMARY KEY(nombre))")
conn.execute("CREATE NODE TABLE Sector(nombre STRING, PRIMARY KEY(nombre))")
conn.execute(
    "CREATE REL TABLE CONTRATA("
    "FROM Entidad TO Proveedor, "
    "contrato_id STRING, "
    "valor_millones INT64, "
    "estado STRING, "
    "anio INT64)"
)
conn.execute("CREATE REL TABLE TRABAJA_EN(FROM Proveedor TO Sector)")

print("Esquema de grafo creado.")
'''),
        interp(
            "esquema de grafo",
            [
                "El esquema separa actores y relaciones; esto evita repetir la entidad o el proveedor en cada fila como si todo fuera una tabla plana.",
                "La relacion `CONTRATA` guarda propiedades del vinculo, no solo de los nodos. Ese detalle es clave en grafos: una relacion tambien puede tener datos.",
                "Todavia no hemos probado ninguna hipotesis; solo preparamos una representacion adecuada para preguntas relacionales.",
            ],
        ),
        code('''
entidades = sorted(contratos["entidad"].unique())
proveedores = sorted(contratos["proveedor"].unique())
sectores = sorted(contratos["sector"].unique())

for entidad in entidades:
    conn.execute("MERGE (:Entidad {nombre: $nombre})", {"nombre": entidad})

for proveedor in proveedores:
    conn.execute("MERGE (:Proveedor {nombre: $nombre})", {"nombre": proveedor})

for sector in sectores:
    conn.execute("MERGE (:Sector {nombre: $nombre})", {"nombre": sector})

for fila in contratos.to_dict("records"):
    conn.execute(
        "MATCH (e:Entidad {nombre: $entidad}), (p:Proveedor {nombre: $proveedor}) "
        "MERGE (e)-[:CONTRATA {"
        "contrato_id: $contrato_id, "
        "valor_millones: $valor_millones, "
        "estado: $estado, "
        "anio: $anio"
        "}]->(p)",
        fila,
    )
    conn.execute(
        "MATCH (p:Proveedor {nombre: $proveedor}), (s:Sector {nombre: $sector}) "
        "MERGE (p)-[:TRABAJA_EN]->(s)",
        fila,
    )

print("Datos cargados al grafo.")
'''),
        interp(
            "carga de nodos y relaciones",
            [
                "El mismo dataset ahora permite hacer preguntas de red: quien conecta con quien, a traves de que proveedor y en que sector.",
                "La instruccion `MERGE` evita duplicar la relacion proveedor-sector cuando el proveedor aparece en varios contratos del mismo sector.",
                "Un error comun es cargar todo como nodos sin pensar las relaciones. En grafos, la relacion suele ser la parte analitica mas valiosa.",
            ],
        ),
        code('''
resultado = conn.execute(
    "MATCH (e:Entidad)-[c:CONTRATA]->(p:Proveedor) "
    "RETURN e.nombre AS entidad, "
    "p.nombre AS proveedor, "
    "count(*) AS contratos, "
    "sum(c.valor_millones) AS valor_total_millones "
    "ORDER BY valor_total_millones DESC"
)

resultado.get_as_df()
'''),
        interp(
            "consulta agregada en grafo",
            [
                "La tabla resultante resume vinculos, no solo registros. Cada fila dice que una entidad y un proveedor estan conectados por contratos.",
                "El mayor valor total no implica irregularidad; solo senala una relacion relevante para mirar con mas contexto.",
                "No podemos concluir riesgo sin comparar competencia, modalidad, duracion, historial y objeto contractual.",
            ],
        ),
        code('''
compartidos = conn.execute(
    "MATCH (e1:Entidad)-[:CONTRATA]->(p:Proveedor)<-[:CONTRATA]-(e2:Entidad) "
    "WHERE e1.nombre < e2.nombre "
    "RETURN e1.nombre AS entidad_1, "
    "e2.nombre AS entidad_2, "
    "p.nombre AS proveedor_compartido "
    "ORDER BY proveedor_compartido"
)

compartidos.get_as_df()
'''),
        interp(
            "proveedores compartidos",
            [
                "Esta consulta no es natural en una tabla plana, porque pregunta por un patron de dos entidades conectadas al mismo proveedor.",
                "Un proveedor compartido puede ser normal si es especializado, pero tambien puede indicar concentracion de mercado.",
                "La lectura responsable es descriptiva: identificamos conexiones, no culpables.",
            ],
        ),
        reflection(
            "mini-reto de grafos",
            [
                "Modifica la consulta para encontrar proveedores que trabajen en mas de un sector.",
                "Agrega una condicion para mostrar solo contratos con valor superior a 500 millones.",
                "Explica que pregunta de negocio responde mejor un grafo que una tabla.",
            ],
        ),
    ]


def neo4j_cells():
    return [
        section_header("5", "Ruta cloud: Neo4j Aura y Cypher"),
        md("""
Neo4j Aura permite trabajar con un motor de grafos administrado. En Colab se usa el driver oficial de Python y credenciales temporales. Esta ruta es util cuando se quiere practicar con una base real de grafos, explorar visualmente los nodos y conectar la clase con herramientas usadas en industria.

En esta seccion no se dejan credenciales en el cuaderno. El estudiante las pega durante la ejecucion.
"""),
        md("""
### Guia del cliente Neo4j en Python

El driver oficial de Neo4j trabaja con tres ideas:

| Pieza del cliente | Que hace | Lectura docente |
|---|---|---|
| `GraphDatabase.driver(uri, auth=...)` | Crea el objeto principal de conexion. | No ejecuta consultas por si solo; prepara el canal hacia Aura. |
| `driver.verify_connectivity()` | Prueba que las credenciales y la red funcionen. | Es una celda de diagnostico antes de cargar datos. |
| `driver.session()` | Abre una sesion de trabajo contra la base. | La sesion es el canal por donde viajan consultas Cypher. |
| `session.run(cypher, **params)` | Ejecuta una consulta dentro de la sesion. | En clase sirve para cargar y consultar patrones. |
| `driver.execute_query(...)` | Ejecuta consultas simples con transaccion automatica. | Es comodo para consultas puntuales; `session.run` deja ver mejor el flujo pedagogico. |
| `record.data()` | Convierte un registro Neo4j en diccionario Python. | Facilita construir DataFrames con resultados. |
| `driver.close()` | Cierra recursos del cliente. | Buena practica al final de scripts largos. |

En Aura, el cliente no guarda datos localmente: envia Cypher a un servicio administrado. Por eso hay que cuidar credenciales, red y permisos.
"""),
        ficha(
            "GraphDatabase.driver()",
            "crea una conexion hacia una instancia Neo4j.",
            "URI de Aura, usuario y contrasena solicitados en tiempo de ejecucion.",
            "un driver reutilizable para abrir sesiones y ejecutar consultas.",
            "si `verify_connectivity()` responde sin error, la instancia esta accesible desde Colab.",
        ),
        code('''
from getpass import getpass
from neo4j import GraphDatabase

NEO4J_URI = input("Neo4j Aura URI (deja vacio para omitir esta practica): ").strip()

if NEO4J_URI:
    NEO4J_USER = input("Usuario Neo4j: ").strip()
    NEO4J_PASSWORD = getpass("Password Neo4j: ")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    driver.verify_connectivity()
    print("Conexion a Neo4j Aura verificada.")
else:
    driver = None
    print("Practica cloud omitida. Continua con la practica local de KuzuDB.")
'''),
        interp(
            "diagnostico de conexion Neo4j",
            [
                "`GraphDatabase.driver()` construye el cliente; `verify_connectivity()` confirma que realmente puede comunicarse con Aura.",
                "La contrasena se solicita con `getpass()` para que no quede escrita en el cuaderno.",
                "Si esta celda falla, no significa que el modelo de grafos este mal; suele ser un problema de URI, credenciales o permisos.",
            ],
        ),
        md("""
La siguiente celda muestra el patron recomendado: crear constraints, cargar nodos con `MERGE` y cargar relaciones con propiedades. Si se omitio la conexion, la celda no hace cambios.
"""),
        code('''
if driver is not None:
    with driver.session() as session:
        session.run("CREATE CONSTRAINT entidad_nombre IF NOT EXISTS FOR (e:Entidad) REQUIRE e.nombre IS UNIQUE")
        session.run("CREATE CONSTRAINT proveedor_nombre IF NOT EXISTS FOR (p:Proveedor) REQUIRE p.nombre IS UNIQUE")
        session.run("CREATE CONSTRAINT sector_nombre IF NOT EXISTS FOR (s:Sector) REQUIRE s.nombre IS UNIQUE")

        for fila in contratos.to_dict("records"):
            session.run(
                "MERGE (e:Entidad {nombre: $entidad}) "
                "MERGE (p:Proveedor {nombre: $proveedor}) "
                "MERGE (s:Sector {nombre: $sector}) "
                "MERGE (p)-[:TRABAJA_EN]->(s) "
                "MERGE (e)-[c:CONTRATA {contrato_id: $contrato_id}]->(p) "
                "SET c.valor_millones = $valor_millones, "
                "c.estado = $estado, "
                "c.anio = $anio",
                **fila,
            )
    print("Datos cargados en Neo4j Aura.")
else:
    print("Sin conexion Aura: no se ejecuto carga cloud.")
'''),
        md("""
### Como leer resultados desde Neo4j

Cuando una consulta devuelve filas, Neo4j entrega objetos `Record`. Para llevarlos a Pandas se suele hacer:

```python
with driver.session() as session:
    resultado = session.run("MATCH (p:Proveedor) RETURN p.nombre AS proveedor")
    filas = [record.data() for record in resultado]
    pd.DataFrame(filas)
```

La parte importante no es Pandas: es que cada `record` representa una fila de la respuesta Cypher. `record.data()` la vuelve diccionario para que sea facil de inspeccionar.
"""),
        code('''
if driver is not None:
    with driver.session() as session:
        resultado = session.run(
            "MATCH (e:Entidad)-[c:CONTRATA]->(p:Proveedor) "
            "RETURN e.nombre AS entidad, p.nombre AS proveedor, c.valor_millones AS valor "
            "ORDER BY valor DESC"
        )
        filas = [record.data() for record in resultado]
        neo4j_resumen = pd.DataFrame(filas)
        display(neo4j_resumen)
else:
    print("Sin conexion Aura: revisa el patron record.data() como plantilla.")
'''),
        interp(
            "Neo4j Aura",
            [
                "La ruta Aura permite pasar de una practica local a una base administrada y consultable desde una interfaz de grafos.",
                "El codigo usa `MERGE` porque en grafos reales es comun cargar incrementalmente y evitar duplicados.",
                "La diferencia principal frente a KuzuDB aqui no es conceptual, sino operacional: Aura mantiene el servicio, usuarios, seguridad y visualizacion.",
            ],
        ),
    ]


def columnar_cells():
    return [
        section_header("6", "Bases columnares y wide-column"),
        md("""
## Definicion formal

Una base **wide-column** organiza datos en tablas distribuidas por clave de particion y columnas agrupadas por claves de ordenamiento. Apache Cassandra es el ejemplo clasico en el PDA: no se modela empezando por entidades normalizadas, sino por las consultas que el sistema debe responder a gran escala.

## Intuicion

En una base relacional se pregunta: "que entidades tengo y como las normalizo?". En Cassandra se pregunta: "que consulta debe responder rapido el sistema y cual sera la clave que reparte los datos?". Por eso una misma informacion puede duplicarse en varias tablas si cada tabla sirve una consulta distinta.

## Error comun

Intentar hacer joins analiticos arbitrarios en Cassandra como si fuera SQL tradicional. Cassandra premia lecturas predecibles por particion; no esta pensada para exploracion flexible estilo data warehouse.
"""),
        md("""
### Ejemplo manual pequeno

Supongamos que necesitamos consultar contratos por entidad y ano:

```sql
CREATE TABLE contratos_por_entidad_anio (
    entidad text,
    anio int,
    contrato_id text,
    proveedor text,
    valor_millones int,
    estado text,
    PRIMARY KEY ((entidad, anio), contrato_id)
);
```

Lectura:

- `(entidad, anio)` es la **clave de particion compuesta**: decide donde quedan los datos.
- `contrato_id` es clave de ordenamiento dentro de la particion.
- La tabla responde muy bien: "dame contratos de una entidad en un ano".
- No responde bien: "dame todos los contratos de todos los anos y ordenalos por valor" si eso no se modelo.
"""),
        ficha(
            "PRIMARY KEY ((particion), clustering)",
            "define como se distribuyen y ordenan los datos en Cassandra.",
            "columnas de particion y columnas de clustering.",
            "una regla fisica de organizacion de datos.",
            "una buena clave reduce lecturas dispersas; una mala clave crea particiones enormes o consultas imposibles.",
        ),
        code('''
contratos_columnar = contratos.copy()
contratos_columnar["particion"] = (
    contratos_columnar["entidad"].str.lower().str.replace(" ", "_")
    + "#"
    + contratos_columnar["anio"].astype(str)
)

vista_columnar = (
    contratos_columnar
    .sort_values(["particion", "contrato_id"])
    [["particion", "contrato_id", "entidad", "anio", "proveedor", "valor_millones", "estado"]]
)

vista_columnar
'''),
        interp(
            "simulacion de particiones",
            [
                "La columna `particion` representa la llave que agruparia fisicamente los contratos por entidad y ano.",
                "Esta vista no convierte Pandas en Cassandra; solo permite visualizar la decision de modelado.",
                "Si la consulta principal cambia, probablemente necesitaremos otra tabla orientada a esa consulta.",
            ],
        ),
        code('''
consulta_cali_2026 = vista_columnar[vista_columnar["particion"] == "alcaldia_de_cali#2026"]
consulta_cali_2026
'''),
        interp(
            "consulta por particion",
            [
                "La consulta es eficiente conceptualmente porque conoce la particion exacta.",
                "El resultado no busca en toda la base: va al grupo logico `Alcaldia de Cali + 2026`.",
                "En Cassandra real, este tipo de patron evita escaneos amplios y hace la lectura predecible.",
            ],
        ),
        reflection(
            "diseno wide-column",
            [
                "Si la consulta frecuente fuera por proveedor y ano, que clave de particion propondrias?",
                "Que riesgo aparece si una sola entidad concentra millones de contratos en el mismo ano?",
                "Por que duplicar una tabla puede ser aceptable en Cassandra pero peligroso si no se gobierna?",
            ],
        ),
        section_header("7", "Ruta cloud: Astra DB y CQL"),
        md("""
DataStax Astra DB permite practicar Cassandra como servicio administrado. La idea para Colab es descargar el **secure connect bundle** desde la consola de Astra y usar el driver de Python. Esta ruta requiere cuenta gratuita y credenciales temporales.

La celda siguiente es una plantilla segura: no contiene secretos. Si no tienes credenciales durante la clase, estudia el flujo y continua con la practica local de modelado.
"""),
        md("""
### Guia del cliente Cassandra/Astra en Python

El driver de Cassandra se usa distinto a un cliente SQL tradicional porque el modelo esta orientado a consultas por clave.

| Pieza del cliente | Que hace | Para que importa |
|---|---|---|
| `PlainTextAuthProvider(client_id, client_secret)` | Prepara autenticacion con token de Astra. | Separa credenciales del codigo. |
| `Cluster(cloud=..., auth_provider=...)` | Crea el objeto cluster usando el Secure Connect Bundle. | El SCB contiene informacion de conexion segura. |
| `cluster.connect()` | Abre una sesion CQL. | A partir de aqui se ejecutan comandos. |
| `session.set_keyspace(...)` | Selecciona el espacio logico de tablas. | Evita repetir el keyspace en cada consulta. |
| `session.execute(cql)` | Ejecuta CQL. | Sirve para DDL, inserciones y consultas pequenas. |
| `session.prepare(cql)` | Precompila una consulta parametrizada. | Recomendado para consultas repetidas con distintos valores. |
| `cluster.shutdown()` | Cierra conexiones. | Buena practica en scripts y notebooks largos. |

El concepto clave es que `session.execute()` no debe usarse para explorar cualquier cosa sin clave. En Cassandra, la consulta debe respetar el diseno de particiones.
"""),
        ficha(
            "Cluster(cloud={...}, auth_provider=...)",
            "crea una conexion del driver Cassandra hacia Astra DB.",
            "ruta del secure connect bundle, client id y client secret.",
            "un objeto cluster desde el cual se abre una sesion CQL.",
            "si la sesion abre, puedes crear keyspaces/tablas y ejecutar CQL desde Colab.",
        ),
        code('''
from getpass import getpass

usar_astra = input("Tienes secure connect bundle de Astra DB? (si/no): ").strip().lower()

if usar_astra == "si":
    from cassandra.cluster import Cluster
    from cassandra.auth import PlainTextAuthProvider

    bundle_path = input("Ruta del secure connect bundle subido a Colab: ").strip()
    client_id = input("Client ID: ").strip()
    client_secret = getpass("Client Secret: ")

    cloud_config = {"secure_connect_bundle": bundle_path}
    auth_provider = PlainTextAuthProvider(client_id, client_secret)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    print("Conexion a Astra DB abierta.")
else:
    session = None
    print("Ruta Astra omitida. Se mantiene la practica conceptual/local.")
'''),
        interp(
            "conexion Astra",
            [
                "El Secure Connect Bundle no es un dataset; es un paquete de configuracion y certificados para conectarse de forma segura.",
                "`cluster.connect()` abre la sesion CQL. Desde ese momento, el cuaderno puede enviar instrucciones a Astra.",
                "Si la conexion falla, revisa que el bundle corresponda a la base correcta y que el token tenga permisos.",
            ],
        ),
        code('''
if session is not None:
    session.execute(
        "CREATE KEYSPACE IF NOT EXISTS bigdata_uce "
        "WITH replication = {'class': 'NetworkTopologyStrategy'}"
    )
    session.set_keyspace("bigdata_uce")
    session.execute(
        "CREATE TABLE IF NOT EXISTS contratos_por_entidad_anio ("
        "entidad text, "
        "anio int, "
        "contrato_id text, "
        "proveedor text, "
        "valor_millones int, "
        "estado text, "
        "PRIMARY KEY ((entidad, anio), contrato_id)"
        ")"
    )
    print("Keyspace y tabla preparados.")
else:
    print("Sin sesion Astra: revisa el CQL como plantilla de diseno.")
'''),
        md("""
### Prepared statements en Cassandra

Cuando una consulta se ejecuta muchas veces con distintos valores, se recomienda prepararla:

```python
stmt = session.prepare(
    "SELECT * FROM contratos_por_entidad_anio WHERE entidad=? AND anio=?"
)
filas = session.execute(stmt, ["Alcaldia de Cali", 2026])
```

La consulta se define una vez y luego solo cambian los valores. Esto reduce parseo repetido y deja mas claro que la consulta esta disenada para una clave concreta.
"""),
        code('''
if session is not None:
    consulta = session.prepare(
        "SELECT contrato_id, proveedor, valor_millones, estado "
        "FROM contratos_por_entidad_anio "
        "WHERE entidad=? AND anio=?"
    )
    print("Prepared statement creado para consultar por entidad y anio.")
    # Ejecucion esperada:
    # filas = session.execute(consulta, ["Alcaldia de Cali", 2026])
    # pd.DataFrame(list(filas))
else:
    print("Plantilla prepared statement: WHERE entidad=? AND anio=?")
'''),
        interp(
            "Astra y CQL",
            [
                "La ruta cloud convierte el ejercicio de modelado en una base wide-column real.",
                "La tabla se disena para una consulta concreta: contratos por entidad y ano.",
                "El objetivo de clase no es memorizar CQL, sino entender que la clave primaria es una decision de arquitectura.",
            ],
        ),
    ]


def comparison_cells():
    return [
        section_header("8", "Comparacion final: documental, grafo y columnar"),
        md("""
| Pregunta de negocio | Modelo mas natural | Por que |
|---|---|---|
| Ver el contrato completo con campos anidados | Documental | El documento agrupa datos heterogeneos del contrato |
| Encontrar proveedores compartidos entre entidades | Grafo | La relacion es el centro de la pregunta |
| Consultar rapido contratos por entidad y ano | Wide-column | La clave de particion anticipa la consulta |
| Explorar texto libre por relevancia | Motor de busqueda | Se necesitan analizadores, ranking y busqueda textual |

La decision no es religiosa. En arquitecturas reales pueden convivir: MongoDB para documentos operacionales, Neo4j/Kuzu para relaciones, Cassandra/Astra para lecturas masivas por clave y Elasticsearch para busqueda textual.
"""),
        reflection(
            "cierre aplicado",
            [
                "Que modelo usarias para detectar concentracion de proveedores entre varias alcaldias?",
                "Que modelo usarias para servir una API que consulta historico por entidad y ano?",
                "Que modelo usarias para guardar un contrato con adiciones, observaciones y documentos relacionados?",
            ],
        ),
        section_header("9", "Ejercicios guiados"),
        md("""
1. Agrega dos contratos nuevos al DataFrame inicial: uno con un proveedor ya existente y otro con una entidad nueva.
2. Recarga el grafo local y consulta que proveedores conectan mas de una entidad.
3. Disena una tabla wide-column para la consulta: "contratos por proveedor y estado".
4. Explica que campos pondrias en la clave de particion y cuales como clustering keys.
5. Redacta una conclusion descriptiva: que aprendiste sobre relaciones, particiones y documentos?
"""),
        section_header("10", "Cierre de sesion"),
        md("""
## Recapitulacion

- NoSQL no significa "sin estructura"; significa estructuras distintas para necesidades distintas.
- MongoDB documental sirve bien cuando el contrato completo se consulta como documento.
- Los grafos sirven cuando el valor esta en las conexiones: entidad, proveedor, sector, contrato.
- Cassandra/Astra sirve cuando se conocen consultas masivas y repetidas que deben responder por clave.

## Idea mas importante

El modelo de datos se decide desde la pregunta de negocio y el patron de acceso. En Big Data, guardar datos no basta: hay que guardarlos de forma que la pregunta importante pueda responderse.

## Errores comunes

- Usar grafos solo para dibujar redes bonitas, sin pregunta relacional.
- Llevar normalizacion relacional directamente a Cassandra.
- Pensar que documental, grafo y columnar compiten siempre; muchas arquitecturas los combinan.
- Interpretar una conexion o concentracion como causalidad o irregularidad sin evidencia adicional.

## Proxima sesion

La siguiente clase toma una necesidad complementaria: buscar texto por relevancia. Ahi aparece Elasticsearch como motor especializado para indices, analizadores, filtros, ranking y agregaciones.
"""),
        section_header("11", "Referencias"),
        md("""
- Neo4j Python Driver Manual: https://neo4j.com/docs/python-manual/current/
- Neo4j Aura - Connecting applications: https://neo4j.com/docs/aura/connecting-applications/overview/
- KuzuDB Python API: https://docs.kuzudb.com/client-apis/python/
- Apache Cassandra - Data modeling: https://cassandra.apache.org/doc/latest/cassandra/developing/data-modeling/intro.html
- Apache Cassandra - CREATE TABLE: https://cassandra.apache.org/doc/latest/cassandra/reference/cql-commands/create-table.html
- DataStax Astra DB - Connect with Python: https://docs.datastax.com/en/astra-db-classic/databases/connect-python.html
- MongoDB Manual - Data modeling: https://www.mongodb.com/docs/manual/data-modeling/

Documentacion revisada para la version vigente del curso 2026.
"""),
    ]


def build_cells():
    cells = [
        *uce_header(
            title="NoSQL aplicado: grafos, columnares y conexion con documental",
            session=13,
            github_path="main/Cuadernos/13_NoSQL_Grafos_Columnar_Colab.ipynb",
            nota_plataforma="Google Colab + servicios cloud gratuitos",
        ),
        md("""
## Alcance de la sesion

Esta sesion completa el bloque NoSQL del PDA. MongoDB documental ya fue trabajado en la clase anterior; ahora estudiaremos las otras dos familias que el programa exige: bases de **grafos** y bases **columnares/wide-column**.

El objetivo no es aprender muchas marcas de memoria, sino distinguir que problema resuelve cada modelo y como se traduce una pregunta de negocio en una estructura de datos.
"""),
        md("""
## Objetivos de aprendizaje

Al finalizar la clase deberias poder:

1. Diferenciar modelo documental, grafo y wide-column.
2. Representar entidades, proveedores y contratos como grafo.
3. Escribir consultas Cypher basicas para encontrar patrones relacionales.
4. Explicar por que Cassandra/Astra modela por consultas y no por normalizacion relacional.
5. Disenar una clave de particion y clustering key para una consulta frecuente.
6. Elegir responsablemente entre documental, grafo y columnar para un caso aplicado.
"""),
        md("""
## Agenda sugerida de 3 horas

| Momento | Tiempo | Actividad |
|---|---:|---|
| Apertura y conexion con MongoDB | 20 min | Que queda cubierto del PDA y por que faltan grafos/columnares |
| Modelo de grafos | 45 min | Teoria breve, ejemplo manual y practica KuzuDB |
| Neo4j Aura | 25 min | Ruta cloud, credenciales seguras y plantilla de carga |
| Descanso corto | 10 min | Pausa |
| Modelo wide-column | 45 min | Cassandra/Astra, particiones, clustering y CQL |
| Caso aplicado | 25 min | Contratos publicos vistos desde tres modelos |
| Cierre | 10 min | Comparacion, errores comunes y preparacion para Elasticsearch |
"""),
        *free_tier_cells(),
        toc([
            "Seccion 1 -- Por que NoSQL no es una sola tecnologia",
            "Seccion 2 -- Repaso documental: lo que ya cubrio MongoDB",
            "Seccion 3 -- Modelo de grafos",
            "Seccion 4 -- Practica de grafos en Colab con KuzuDB",
            "Seccion 5 -- Ruta cloud: Neo4j Aura y Cypher",
            "Seccion 6 -- Bases columnares y wide-column",
            "Seccion 7 -- Ruta cloud: Astra DB y CQL",
            "Seccion 8 -- Comparacion final",
            "Seccion 9 -- Ejercicios guiados",
            "Seccion 10 -- Cierre",
        ]),
        section_header("1", "Por que NoSQL no es una sola tecnologia"),
        md("""
## Por que importa

En Big Data aparecen fuentes heterogeneas, relaciones complejas, lecturas masivas y texto no estructurado. Una sola tabla universal rara vez responde bien a todos esos usos. Por eso el PDA pide estudiar bases documentales, de grafos y columnares: cada una organiza los datos para una forma distinta de preguntar.

## Definicion formal

**NoSQL** agrupa sistemas de gestion de datos que no dependen exclusivamente del modelo relacional tabular. Suelen optimizar flexibilidad de esquema, escalabilidad horizontal, distribucion, disponibilidad o consultas especializadas.

## Intuicion

NoSQL no significa "me olvido del diseno". Significa que el diseno se hace desde el patron de acceso:

- Si consulto documentos completos, pienso documental.
- Si busco conexiones, pienso grafo.
- Si leo por claves masivas y predecibles, pienso wide-column.
- Si busco texto por relevancia, pienso motor de busqueda.
"""),
        reflection(
            "antes de modelar",
            [
                "Cual es la pregunta de negocio?",
                "La pregunta depende mas del documento, de la relacion, de la clave de consulta o del texto?",
                "Que consulta debe responder rapido el sistema?",
            ],
        ),
        section_header("2", "Repaso documental: lo que ya cubrio MongoDB"),
        md("""
MongoDB ya cubrio el modelo documental: documentos BSON/JSON, campos anidados, arreglos, agregaciones, indices, geodatos, series de tiempo y busqueda moderna. En esta clase no repetimos ese cuaderno; lo usamos como punto de comparacion.

## Ejemplo manual pequeno

Un contrato documental podria guardarse asi:

```json
{
  "contrato_id": "C-001",
  "entidad": {"nombre": "Alcaldia de Cali", "territorio": "Valle del Cauca"},
  "proveedor": {"nombre": "Analitica Publica SAS"},
  "valor_millones": 880,
  "objetos": ["tablero", "seguimiento contractual"],
  "adiciones": [{"fecha": "2026-02-01", "valor_millones": 120}]
}
```

El documento es natural cuando la aplicacion necesita leer el contrato con su contexto cercano. Pero si la pregunta es "que proveedores conectan varias entidades?", el documento empieza a sentirse incomodo. Ahi entran los grafos.
"""),
        interp(
            "repaso documental",
            [
                "El documento agrupa contexto; esa es su fortaleza.",
                "El documento no desaparece por estudiar grafos o columnares. En una arquitectura real puede seguir siendo la capa operacional.",
                "La pregunta que viene ahora no es 'que contiene el contrato?', sino 'como se relacionan los actores?'.",
            ],
        ),
        section_header("3", "Modelo de grafos"),
        md("""
## Definicion formal

Una base de grafos representa informacion como **nodos**, **relaciones** y **propiedades**. Los nodos son entidades; las relaciones conectan nodos y tambien pueden tener atributos.

## Intuicion

Si el dato importante vive en la conexion, el grafo suele ser mas natural que una tabla. En contratacion publica, por ejemplo, interesan patrones como:

- Entidades que comparten proveedores.
- Proveedores que aparecen en varios sectores.
- Caminos entre entidad, proveedor, sector y contrato.
- Concentracion de relaciones en pocos actores.

## Ejemplo manual pequeno

```text
(Alcaldia de Cali)-[:CONTRATA {valor: 880}]->(Analitica Publica SAS)
(Analitica Publica SAS)-[:TRABAJA_EN]->(Tecnologia)
```

La lectura no es una fila: es un camino.
"""),
        install_cell(),
        data_cell(),
        interp(
            "dataset de clase",
            [
                "El dataset es pequeno a proposito: permite ver la estructura antes de pensar en volumen.",
                "Cada fila parece un contrato, pero tambien contiene entidades, proveedores, sectores y relaciones posibles.",
                "No estamos probando causalidad; estamos preparando datos para aprender modelos NoSQL.",
            ],
        ),
        *kuzu_cells(),
        *neo4j_cells(),
        *columnar_cells(),
        *comparison_cells(),
    ]
    return cells


if __name__ == "__main__":
    cells = build_cells()
    validate(cells)
    save(cells, OUTPUT)
