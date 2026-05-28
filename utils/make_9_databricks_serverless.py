# -*- coding: utf-8 -*-
"""
Genera Cuadernos/9_Databricks_Serverless_Completo.ipynb

Sesion 9: primera introduccion guiada a Databricks Free/Community Edition serverless.
"""

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.make_notebook import md, code, save, validate, uce_header, section_header


TOTAL_Q = 12


def pregunta(num, tema, contexto, pregunta_texto, opciones, correcta, explicacion):
    opciones_html = "\n".join(
        f'<label style="display:block; margin:8px 0;"><input type="radio" name="q{num}" value="{chr(65+i)}"> {chr(65+i)}. {op}</label>'
        for i, op in enumerate(opciones)
    )
    return code(f"""
# Pregunta interactiva {num} de {TOTAL_Q}
# Estilo IRdisplay adaptado a Databricks/Python: caja HTML con displayHTML.
html = '''
<div style="border:2px solid #2563eb; background:#eff6ff; border-radius:8px; padding:16px; margin:12px 0; font-family:Arial, sans-serif;">
  <h3 style="margin:0 0 10px 0; color:#1d4ed8;">Pregunta {num} de {TOTAL_Q} -- {tema}</h3>
  <div style="background:#fef3c7; border-left:5px solid #f59e0b; padding:10px; margin:10px 0;">
    <strong>Contexto.</strong> {contexto}
  </div>
  <p><strong>{pregunta_texto}</strong></p>
  {opciones_html}
  <button onclick="
    var marcado = document.querySelector('input[name=q{num}]:checked');
    var out = document.getElementById('fb_q{num}');
    if (!marcado) {{
      out.innerHTML = 'Selecciona una opcion antes de verificar.';
      out.style.background = '#fef3c7';
      out.style.color = '#92400e';
      return;
    }}
    if (marcado.value === '{correcta}') {{
      out.innerHTML = 'Correcto. {explicacion}';
      out.style.background = '#dcfce7';
      out.style.color = '#166534';
    }} else {{
      out.innerHTML = 'Incorrecto. {explicacion}';
      out.style.background = '#fee2e2';
      out.style.color = '#991b1b';
    }}
  " style="background:#2563eb; color:white; border:0; border-radius:6px; padding:8px 12px; cursor:pointer;">
    Verificar respuesta
  </button>
  <div id="fb_q{num}" style="margin-top:10px; padding:10px; border-radius:6px;"></div>
</div>
'''

try:
    displayHTML(html)
except NameError:
    from IPython.display import HTML, display
    display(HTML(html))
    """, warn_on_triple_quotes=False)


def interp(titulo, puntos):
    return md(
        "### Como interpretar el resultado -- " + titulo + "\n\n" +
        "\n".join(f"- {p}" for p in puntos)
    )


def _proposito():
    return md("""
## Proposito pedagogico

Esta sesion es una **primera introduccion guiada a Databricks Free Edition / Community 2026** despues
de haber estudiado Hadoop, YARN y Spark en la sesion anterior. La meta no es
memorizar comandos aislados: la meta es entender donde viven los datos, como se
ejecuta Spark dentro de Databricks y como se construye un flujo reproducible.

## Alcance de la sesion

Trabajaremos con Databricks en su edicion gratuita 2026, que usa computo
serverless y Unity Catalog. El punto de entrada de la clase sera el objeto
`spark`: con el leeremos tablas, ejecutaremos SQL, crearemos DataFrames y
guardaremos resultados. Tambien veremos Volumes cuando esten disponibles,
Parquet y Delta Lake.

## Agenda sugerida

1. Entender la interfaz de Databricks gratuito/serverless.
2. Aprender comandos magicos, `dbutils`, Unity Catalog y Volumes.
3. Leer, transformar y escribir datos con CSV, JSON, Parquet y Delta.
4. Comprender Spark: schemas, SQL, funciones, lazy evaluation y planes.
5. Comparar Spark con Pandas y Dask.
6. Introducir Delta Lake, Lakeflow y Workflows.
7. Cerrar con un taller aplicado.

## Por que importa

Databricks permite pasar de un notebook exploratorio a una plataforma de datos:
tablas gobernadas, permisos, lineage, ejecuciones programadas, optimizacion y
pipelines. Ese cambio es central en Big Data moderno.
    """)


def _toc():
    return md("""
## Contenido

- 0. Databricks Free/Community 2026: serverless y plataforma moderna
- 1. Magic commands y dbutils
- 2. SparkSession y el objeto spark
- 3. Catalogos, tablas y Volumes
- 4. Spark SQL completo: TempViews, DDL y DML
- 5. Tipos de datos y schemas
- 6. Lectura y escritura: CSV, JSON, Parquet y Delta
- 7. Lazy evaluation, Catalyst, Jobs, Stages y repartition
- 8. Photon y Liquid Clustering
- 9. Funciones de cadenas, fechas y colecciones
- 10. Transformaciones completas de la API PySpark
- 11. Por que Spark sobre Pandas, y cuando no
- 12. Por que Spark sobre Dask, y cuando no
- 13. Delta Lake avanzado
- 14. Lakeflow / Delta Live Tables
- 15. Databricks Workflows y Jobs
- 16. Taller end-to-end
    """)


def _correspondencia():
    return md("""
## Correspondencia con la sesion anterior

| Sesion 7 | En esta sesion |
|---|---|
| Hadoop y YARN explican la administracion de recursos | Databricks serverless abstrae gran parte de esa administracion |
| Spark como motor distribuido | Spark se usa con SQL, DataFrames y PySpark |
| Clusters y ejecucion distribuida | SparkSession, SparkSession, Jobs, Stages y Tasks |
| Archivos y almacenamiento | Unity Catalog, Volumes y tablas administradas |

Conservamos la idea de procesamiento distribuido de la sesion 7, pero la llevamos al flujo
actual de Databricks.
    """)


def _seccion_0():
    return [
        section_header("0", "Databricks Free/Community 2026: serverless y plataforma moderna"),
        md("""
## Definicion formal

**Databricks Free Edition** es la version gratuita actual de Databricks para
estudiantes, docentes y personas que estan aprendiendo. En 2026 reemplaza a la
antigua Community Edition y funciona en un entorno **serverless**, con cuotas y
algunas limitaciones.

## Explicacion paso a paso

En este entorno no administramos nodos manualmente. El estudiante abre un
notebook y Databricks conecta compute serverless. Esto hace mas simple la clase,
pero exige usar patrones modernos: DataFrames, Spark SQL, Unity Catalog, tablas
y Volumes cuando esten disponibles.

| Aspecto | Databricks Free/Community 2026 |
|---|---|
| Compute | Serverless administrado |
| Infraestructura | No se eligen nodos manualmente |
| Archivos | Preferir Volumes, tablas o archivos del workspace |
| DBFS root / FileStore | Legacy o acceso limitado |
| Observabilidad | Query Profile / query insights |

## Ecosistema actual

Databricks hoy no es solo "Spark en la nube". Incluye notebooks, SQL, Workflows,
Unity Catalog, Volumes, Delta Lake, Photon, Liquid Clustering, Lakeflow, Model
Serving y herramientas AI/BI como Genie. En la edicion gratuita pueden existir
cuotas o funciones limitadas, pero el modelo mental moderno es el mismo.
        """),
        code("""
# Deteccion inicial del entorno Databricks
import sys

print(f"Python: {sys.version}")
print(f"Spark : {spark.version}")

IS_SERVERLESS = False
HAS_UNITY_CATALOG = False

try:
    current_cat = "hive_metastore"
    current_schema = "default"
    current_cat = spark.sql("SELECT current_catalog()").first()[0]
    current_schema = spark.sql("SELECT current_schema()").first()[0]
    HAS_UNITY_CATALOG = current_cat not in ("", None, "hive_metastore")
    print(f"Catalogo actual: {current_cat}")
    print(f"Schema actual  : {current_schema}")
    print(f"Unity Catalog : {HAS_UNITY_CATALOG}")
except Exception as exc:
    print(f"No fue posible detectar catalogo: {exc}")

try:
    photon = spark.conf.get("spark.databricks.photon.enabled", "false")
except Exception:
    photon = "no detectable"

print(f"Catalogo detectado: {current_cat}")
print(f"Schema detectado  : {current_schema}")
print(f"Unity Catalog     : {HAS_UNITY_CATALOG}")
print(f"Photon            : {photon}")

def nombre_tabla(nombre):
    if HAS_UNITY_CATALOG:
        return f"{current_cat}.{current_schema}.{nombre}"
    return f"{current_schema}.{nombre}"
        """),
        interp("deteccion del entorno", [
            "El catalogo indica el espacio principal donde Databricks organiza datos.",
            "El schema es una carpeta logica dentro del catalogo; alli viven tablas, vistas y otros objetos.",
            "Durante la clase usaremos el objeto `spark` para consultar y crear datos sin entrar en detalles internos del motor."
        ]),
        md("""
## Nota sobre instalacion de librerias

En esta primera introduccion no instalaremos paquetes externos. Databricks ya
incluye Spark, PySpark y Delta Lake para los objetivos de la sesion.

En notebooks de proyecto, si necesitas una libreria adicional, usa el gestor de
paquetes del notebook. Evita instalar desde comandos de shell, porque puede
instalar en un entorno distinto al interprete activo.
        """),
    ]


def _seccion_1():
    return [
        section_header("1", "Magic commands y dbutils"),
        md("""
## Definicion formal

Los **magic commands** son comandos especiales de notebook que cambian el modo de
ejecucion de una celda. `dbutils` es una utilidad propia de Databricks para
interactuar con archivos, widgets, secretos y ejecuciones de notebooks.

| Magic | Uso |
|---|---|
| `%python` | Ejecutar Python |
| `%sql` | Ejecutar SQL |
| `%md` | Escribir texto formateado dentro del notebook |
| `%pip` | Instalar librerias en el entorno del notebook |
| `%run` | Incluir otro notebook |
| `%fs` | Comandos de archivos Databricks |
| `%sh` | Shell del entorno; puede estar limitado en serverless |

## Explicacion paso a paso

Un notebook de Databricks no es solo una hoja para escribir codigo. Es una mezcla
de explicacion, consultas, resultados y pequenas herramientas de ejecucion.

- Si una celda empieza con `%python`, Databricks interpreta el contenido como Python.
- Si empieza con `%sql`, interpreta el contenido como una consulta SQL.
- Si empieza con `%md`, la celda se vuelve texto enriquecido: titulos, tablas,
  listas, enlaces y explicaciones.
- Si no escribimos ningun magic, normalmente la celda usa el lenguaje por defecto
  del notebook.

En este cuaderno usaremos sobre todo Python y `spark.sql(...)`, porque asi el
estudiante ve una forma uniforme de ejecutar SQL desde Python sin saltar entre
lenguajes todo el tiempo.
        """),
        code("""
# SQL desde Python: equivalente portable a una celda %sql
consulta = spark.sql('''
SELECT
  current_catalog() AS catalogo,
  current_schema()  AS schema,
  current_date()    AS fecha_actual
''')
consulta.show(truncate=False)
        """),
        interp("magic SQL desde Python", [
            "La salida confirma el catalogo y schema activos.",
            "`spark.sql` permite usar SQL multi-linea dentro de una celda Python.",
            "Mas adelante usaremos SQL para tres cosas distintas: crear objetos, insertar datos y escribir consultas mas legibles.",
            "DDL significa lenguaje para definir objetos de datos, por ejemplo crear una tabla.",
            "DML significa lenguaje para modificar o insertar datos, por ejemplo agregar filas a una tabla.",
            "Una CTE es una consulta temporal con nombre dentro de un `WITH`; ayuda a dividir una consulta larga en pasos."
        ]),
        md("""
## Que es `dbutils`

`dbutils` significa **Databricks Utilities**. Es un conjunto de herramientas que
Databricks entrega dentro del notebook para resolver tareas practicas que no son
exactamente transformaciones de datos.

No debes memorizar todos sus modulos al inicio. Lo importante es reconocer para
que tipo de problema sirve cada uno:

| Modulo | Para que sirve |
|---|---|
| `dbutils.fs` | Trabajar con archivos que Databricks puede ver. En serverless puede tener limites; para datos gobernados se prefieren tablas y Volumes. |
| `dbutils.widgets` | Crear parametros visibles en la parte superior del notebook. Sirven para cambiar valores sin editar el codigo. |
| `dbutils.secrets` | Leer credenciales guardadas de forma segura. Se usa para no escribir claves o tokens directamente en el notebook. |
| `dbutils.notebook` | Ejecutar otro notebook o terminar el notebook actual devolviendo un resultado. Es util en workflows. |

En Databricks Free/Community 2026 el compute es serverless. El acceso a DBFS
root o FileStore puede estar limitado, por eso el patron recomendado es:
tablas, Volumes de Unity Catalog o archivos del workspace.

En esta primera clase solo veremos ejemplos simples. La idea es que, cuando veas
`dbutils.widgets`, entiendas que se esta parametrizando el notebook; cuando veas
`dbutils.secrets`, entiendas que se esta evitando exponer credenciales; y cuando
veas `dbutils.fs`, recuerdes que no todas las rutas estan disponibles en
serverless.
        """),
        code("""
# Explorar ubicaciones de forma segura en Databricks serverless
# Evitamos listar dbfs:/FileStore o /Volumes/ directamente porque pueden fallar
# por permisos o por las limitaciones del compute serverless.

print("Catalogo y schema actuales:")
spark.sql("SELECT current_catalog() AS catalogo, current_schema() AS schema").show(truncate=False)

print("Tablas visibles en el schema actual:")
spark.sql("SHOW TABLES").show(truncate=False)

try:
    catalogo_actual = spark.sql("SELECT current_catalog()").first()[0]
    schema_actual = spark.sql("SELECT current_schema()").first()[0]
    print(f"Volumes disponibles en {catalogo_actual}.{schema_actual}:")
    spark.sql(f"SHOW VOLUMES IN {catalogo_actual}.{schema_actual}").show(truncate=False)
except Exception as exc:
    print("No se pudieron listar Volumes en este schema.")
    print("Esto puede pasar si no hay Volumes creados o si faltan permisos.")
    print(f"Detalle: {type(exc).__name__}: {exc}")

print("\\nPatrones recomendados:")
print("- Tabla administrada: catalog.schema.mi_tabla")
print("- Volume si existe: /Volumes/<catalog>/<schema>/<volume>/<archivo>")
print("- Archivo del workspace para ejemplos pequenos")
        """),
        code("""
# Widgets: parametros simples para notebooks y jobs
dbutils.widgets.text("catalogo_param", "samples", "Catalogo")
dbutils.widgets.dropdown("modo_ejecucion", "demo", ["demo", "produccion"], "Modo")

catalogo_param = dbutils.widgets.get("catalogo_param")
modo_ejecucion = dbutils.widgets.get("modo_ejecucion")

print(f"catalogo_param={catalogo_param}")
print(f"modo_ejecucion={modo_ejecucion}")
        """),
        code("""
# Secrets y ejecucion de notebooks: patrones seguros
try:
    scopes = dbutils.secrets.listScopes()
    print("Secret scopes disponibles:")
    for s in scopes:
        print(" ", s.name)
except Exception as exc:
    print(f"No fue posible listar secret scopes: {exc}")

print("\\nPatron correcto para credenciales:")
print("token = dbutils.secrets.get(scope='mi_scope', key='mi_token')")
print("\\nPatron para invocar otro notebook desde un workflow:")
print("dbutils.notebook.run('/Repos/proyecto/otro_notebook', 300, {'fecha': '2026-01-01'})")
        """),
    ]


def _seccion_2():
    return [
        section_header("2", "SparkSession y el objeto spark"),
        md("""
## Que es `spark`

En Databricks, el objeto `spark` ya viene creado cuando abres un notebook con
compute conectado. Ese objeto es una **SparkSession**.

Una SparkSession es la entrada principal para trabajar con Spark desde Python.
Con `spark` podemos hacer cuatro cosas fundamentales:

| Necesidad | Ejemplo |
|---|---|
| Ejecutar SQL | `spark.sql("SELECT 1")` |
| Leer una tabla | `spark.read.table("samples.nyctaxi.trips")` |
| Crear un DataFrame pequeno | `spark.createDataFrame([...], columnas)` |
| Crear rangos de prueba | `spark.range(10)` |

## Como pensar en Spark dentro de Databricks

Cuando escribes codigo PySpark, Python no procesa todas las filas una por una en
tu navegador. Python construye instrucciones de alto nivel: leer esta tabla,
filtrar estas filas, crear esta columna, agrupar por esta variable. Spark toma
esas instrucciones, arma un plan de ejecucion y lo ejecuta en el compute de
Databricks.

Por eso, en esta clase trabajaremos con tres herramientas principales:

- `spark`, para entrar a Spark.
- DataFrames, para representar tablas dentro de PySpark.
- Spark SQL, para escribir consultas en lenguaje SQL.

No necesitamos usar APIs internas ni antiguas para aprender Databricks.
        """),
        code("""
# Lo que funciona bien: SparkSession, SQL y DataFrames
from pyspark.sql import functions as F

df = spark.range(10).withColumn("cuadrado", F.col("id") * F.col("id"))
df.show()

spark.sql("SELECT 1 + 1 AS suma").show()

# Crear un DataFrame pequeno directamente desde datos escritos en Python
df_local = spark.createDataFrame([(1,), (2,), (3,)], ["valor"])
df_local.show()
        """),
        interp("SparkSession y el objeto spark", [
            "El ejemplo muestra tres patrones compatibles: `spark.range`, `spark.sql` y `spark.createDataFrame`.",
            "La salida de `show()` no significa que Python guardo todas las filas localmente; significa que Spark ejecuto una accion y mostro una muestra.",
            "A partir de aqui, cuando aparezca `spark`, debe leerse como la entrada principal al motor Spark dentro de Databricks."
        ]),
        md("""
## Funciones de `pyspark.sql.functions`

La linea:

```python
from pyspark.sql import functions as F
```

importa muchas funciones nativas de Spark para trabajar con columnas. Usamos el
alias `F` para escribir expresiones como `F.col("fare_amount")`, `F.avg(...)`,
`F.hour(...)` o `F.when(...)`.

Estas funciones son preferibles a escribir bucles de Python porque Spark puede
entenderlas, optimizarlas y ejecutarlas dentro de su motor distribuido.
        """),
        code("""
# Inventario de funciones disponibles en pyspark.sql.functions
from pyspark.sql import functions as F

funciones_f = sorted([
    nombre for nombre in dir(F)
    if not nombre.startswith("_")
])

print(f"Total de nombres disponibles en F: {len(funciones_f)}")

(
    spark.createDataFrame(
        [(i + 1, nombre) for i, nombre in enumerate(funciones_f)],
        ["n", "funcion"]
    )
    .show(300, truncate=False)
)
        """),
    ]


def _seccion_3():
    return [
        section_header("3", "Catalogos, tablas y Volumes"),
        md("""
## Definicion formal

Databricks organiza los datos con una jerarquia parecida a una biblioteca:

- Un **catalogo** es el nivel mas alto. Agrupa datos de una organizacion,
  proyecto o entorno.
- Un **schema** es una division dentro del catalogo. En otros sistemas tambien
  puede llamarse base de datos.
- Una **tabla** es un conjunto de datos estructurado con filas y columnas.
- Una **vista** es una consulta guardada que se comporta como una tabla logica.
- Un **Volume** es una ubicacion gobernada para archivos, no necesariamente
  tablas: CSV, JSON, Parquet, imagenes, documentos u otros archivos.

Cuando una tabla se escribe como `catalog.schema.table`, cada parte responde una
pregunta:

| Parte | Pregunta que responde | Ejemplo |
|---|---|---|
| `catalog` | En que gran espacio de datos estoy trabajando | `samples` |
| `schema` | En que grupo o tema dentro del catalogo | `nyctaxi` |
| `table` | Que tabla concreta quiero leer | `trips` |

```
catalog
  schema
    table | view | function | volume
```

## Como usar esta idea en la clase

En un notebook local uno suele pensar en rutas como `C:\\Users\\...` o
`Downloads\\archivo.csv`. En Databricks esa no es la forma correcta de razonar.
El notebook corre dentro de Databricks, no dentro del disco del estudiante.

Por eso, antes de leer datos, hacemos estas preguntas:

1. Si el dato ya esta como tabla: cual es su nombre completo.
2. Si el dato es un archivo: en que Volume o ubicacion del workspace fue subido.
3. Si el dato es temporal: si basta con crearlo como DataFrame dentro del notebook.

En esta sesion usaremos principalmente la tabla `samples.nyctaxi.trips`, que esta
visible en el catalogo de ejemplo de Databricks. Tambien mostraremos la forma de
consultar Volumes, pero no asumiremos que todos los estudiantes tengan Volumes
creados.
        """),
        code("""
# Explorar catalogos, schema y tablas de ejemplo
spark.sql("SHOW CATALOGS").show(truncate=False)

CATALOG = spark.sql("SELECT current_catalog()").first()[0]
SCHEMA = spark.sql("SELECT current_schema()").first()[0]
print(f"Catalogo activo: {CATALOG}")
print(f"Schema activo  : {SCHEMA}")

spark.sql("SHOW TABLES IN samples.nyctaxi").show(truncate=False)
        """),
        code("""
# Leer y validar el schema real de samples.nyctaxi.trips
from pyspark.sql import functions as F

TAXI_TABLE = "samples.nyctaxi.trips"
sdf = spark.read.table(TAXI_TABLE)

columnas_esperadas = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "trip_distance",
    "fare_amount",
    "pickup_zip",
    "dropoff_zip",
]
columnas_reales = sdf.columns
columnas_faltantes = [c for c in columnas_esperadas if c not in columnas_reales]

print(f"Tabla: {TAXI_TABLE}")
print(f"Columnas reales: {columnas_reales}")

if columnas_faltantes:
    raise ValueError(f"Faltan columnas esperadas en {TAXI_TABLE}: {columnas_faltantes}")

sdf = sdf.select(*columnas_esperadas)

sdf.createOrReplaceTempView("taxi_source_v")

def leer_taxi():
    return spark.table("taxi_source_v")

print(f"Filas: {sdf.count():,}")
print(f"Columnas: {len(sdf.columns)}")
sdf.printSchema()

print("Metadatos del catalogo:")
spark.sql(f"DESCRIBE TABLE {TAXI_TABLE}").show(truncate=False)
        """),
        interp("tabla de muestra", [
            "La tabla oficial `samples.nyctaxi.trips` tiene 6 columnas en Databricks Free/Community 2026.",
            "El schema nos dice tipos de columnas antes de transformar datos.",
            "Todas las transformaciones posteriores se basan solo en esas columnas verificadas."
        ]),
        code("""
# Volumes y rutas modernas
try:
    spark.sql("SHOW VOLUMES IN samples.nyctaxi").show(truncate=False)
except Exception as exc:
    print("No hay Volumes visibles en samples.nyctaxi o faltan permisos.")
    print(f"Detalle: {exc}")

print("Ruta de Volume en Databricks:")
print("/Volumes/<catalog>/<schema>/<volume>/<archivo>")
print("Ejemplo: /Volumes/main/bronze/raw_files/ventas.parquet")
        """),
        md("""
## Error comun

No uses `C:\\Users\\estudiante\\Downloads\\archivo.csv` dentro de Databricks.
Esa ruta existe en el computador local, no en el compute de Databricks. Primero
sube el archivo a un Volume, a archivos del workspace o crea una tabla.
        """),
    ]


def _seccion_4():
    return [
        section_header("4", "Spark SQL completo: TempViews, DDL y DML"),
        md("""
## Definicion formal

**Spark SQL** permite consultar DataFrames y tablas usando SQL. Una **TempView**
es una vista temporal de sesion creada desde un DataFrame. **DDL** crea o modifica
objetos; **DML** inserta, actualiza o elimina datos.

| Concepto | Ejemplo |
|---|---|
| TempView | `df.createOrReplaceTempView('v')` |
| DDL | `CREATE TABLE`, `DROP TABLE`, `DESCRIBE TABLE` |
| DML | `INSERT INTO`, `MERGE`, `DELETE`, `UPDATE` |

Para compartir resultados entre sesiones, prefiere tablas en el metastore
(`catalog.schema.mi_tabla` cuando Unity Catalog esta disponible). En este
cuaderno usaremos una pequeña ayuda interna para construir nombres compatibles
con el entorno, pero el concepto importante para el estudiante es el nombre
organizado de la tabla.
        """),
        code("""
# Crear TempView desde un DataFrame y consultarla con SQL
taxi_sample = (
    leer_taxi()
    .select("tpep_pickup_datetime", "fare_amount", "trip_distance", "pickup_zip", "dropoff_zip")
    .where("fare_amount > 0 AND trip_distance > 0")
    .withColumn("tarifa_por_milla", F.col("fare_amount") / F.col("trip_distance"))
    .limit(10000)
)

taxi_sample.createOrReplaceTempView("taxi_sample_v")

spark.sql('''
SELECT
  COUNT(*) AS viajes,
  ROUND(AVG(fare_amount), 2) AS tarifa_promedio,
  ROUND(AVG(tarifa_por_milla), 2) AS tarifa_por_milla_promedio
FROM taxi_sample_v
''').show()
        """),
        interp("TempView", [
            "La vista temporal no crea una tabla permanente.",
            "Permite mezclar PySpark y SQL sin duplicar datos.",
            "Desaparece al terminar la sesion del notebook."
        ]),
        code("""
# DDL: crear, describir y eliminar una tabla de practica
SQL_TABLE = nombre_tabla("sesion9_sql_demo")

spark.sql(f"DROP TABLE IF EXISTS {SQL_TABLE}")
spark.sql(f'''
CREATE TABLE IF NOT EXISTS {SQL_TABLE} (
  id BIGINT,
  ciudad STRING,
  valor DOUBLE
)
USING DELTA
''')

if HAS_UNITY_CATALOG:
    spark.sql(f"SHOW TABLES IN {CATALOG}.{SCHEMA}").show(truncate=False)
else:
    spark.sql(f"SHOW TABLES IN {SCHEMA}").show(truncate=False)
spark.sql(f"DESCRIBE TABLE {SQL_TABLE}").show(truncate=False)
        """),
        code("""
# DML: INSERT INTO y consultas de verificacion
spark.sql(f'''
INSERT INTO {SQL_TABLE} VALUES
  (1, 'Bogota', 120.5),
  (2, 'Cali', 95.0),
  (3, 'Medellin', 150.0)
''')

spark.sql(f"SELECT * FROM {SQL_TABLE} ORDER BY id").show()
spark.sql(f"SHOW COLUMNS IN {SQL_TABLE}").show(truncate=False)
spark.sql(f"SHOW CREATE TABLE {SQL_TABLE}").show(truncate=False)
        """),
        code("""
# CTEs: consultas legibles en varios pasos
spark.sql(f'''
WITH base AS (
  SELECT ciudad, valor
  FROM {SQL_TABLE}
  WHERE valor > 0
),
resumen AS (
  SELECT ciudad, COUNT(*) AS n, ROUND(AVG(valor), 2) AS promedio
  FROM base
  GROUP BY ciudad
)
SELECT *
FROM resumen
ORDER BY promedio DESC
''').show()
        """),
    ]


def _seccion_5():
    return [
        section_header("5", "Tipos de datos y schemas"),
        md("""
## Definicion formal

Un **schema** describe las columnas de un DataFrame: nombre, tipo y nulabilidad.
Spark puede inferirlo, pero en pipelines reales conviene declararlo.

| Tipo | Uso |
|---|---|
| `IntegerType`, `LongType` | Enteros |
| `DoubleType` | Numeros decimales |
| `StringType` | Texto |
| `BooleanType` | Verdadero/falso |
| `DateType`, `TimestampType` | Fechas y tiempos |
| `ArrayType`, `MapType`, `StructType` | Datos semiestructurados |

## Explicacion paso a paso

El schema es el contrato del dato. Si el contrato cambia sin control, los
resultados dejan de ser confiables.
        """),
        code("""
# Schema explicito con StructType
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType,
    DoubleType, DateType, TimestampType
)
from pyspark.sql import functions as F

schema_ventas = StructType([
    StructField("ciudad", StringType(), False),
    StructField("categoria", StringType(), True),
    StructField("valor", DoubleType(), True),
    StructField("unidades", IntegerType(), True),
    StructField("fecha_txt", StringType(), True),
])

datos_ventas = [
    ("Bogota", "tecnologia", 1200000.0, 2, "2026-01-05"),
    ("Cali", "hogar", 380000.0, 1, "2026-01-06"),
    ("Medellin", "salud", 210000.0, 3, "2026-01-07"),
]

ventas = spark.createDataFrame(datos_ventas, schema_ventas)
ventas.printSchema()
print(ventas.schema)
print(ventas.dtypes)
ventas.show()
        """),
        code("""
# Conversiones con cast, to_date, to_timestamp y try_cast en SQL
ventas_cast = (
    ventas
    .withColumn("valor_int", F.col("valor").cast("long"))
    .withColumn("fecha", F.to_date("fecha_txt"))
    .withColumn("fecha_ts", F.to_timestamp("fecha_txt"))
)
ventas_cast.show()

ventas_cast.createOrReplaceTempView("ventas_cast_v")
spark.sql('''
SELECT
  ciudad,
  valor,
  try_cast(valor AS INT) AS valor_try_int,
  try_cast('texto_no_numerico' AS INT) AS ejemplo_falla_controlada
FROM ventas_cast_v
''').show()
        """),
        interp("schemas y conversiones", [
            "`printSchema` permite verificar el contrato antes de analizar.",
            "`cast` transforma tipos; `try_cast` evita que una conversion imposible rompa toda la consulta.",
            "En pipelines reales, declarar schema reduce errores silenciosos."
        ]),
        code("""
# Schema enforcement en Delta: escribir con contrato controlado
SCHEMA_TABLE = nombre_tabla("sesion9_schema_demo")

spark.sql(f"DROP TABLE IF EXISTS {SCHEMA_TABLE}")
ventas_cast.write.format("delta").mode("overwrite").saveAsTable(SCHEMA_TABLE)

print("Tabla inicial:")
spark.read.table(SCHEMA_TABLE).printSchema()

ventas_extra = ventas_cast.withColumn("canal", F.lit("online"))

try:
    ventas_extra.write.format("delta").mode("append").saveAsTable(SCHEMA_TABLE)
except Exception as exc:
    print("Append con columna extra fallo por schema enforcement.")
    print(f"Detalle: {type(exc).__name__}: {exc}")

print("Para evolucion controlada del schema se usa mergeSchema u operaciones ALTER TABLE.")
        """),
    ]


def _seccion_6():
    return [
        section_header("6", "Lectura y escritura: CSV, JSON, Parquet y Delta"),
        md("""
## Definicion formal

Spark puede leer y escribir multiples formatos. Para una introduccion, los mas
importantes son CSV, JSON, Parquet y Delta.

| Formato | Uso tipico |
|---|---|
| CSV | Intercambio simple, datos pequenos o fuentes legacy |
| JSON | Datos semiestructurados |
| Parquet | Analitica columnar eficiente |
| Delta | Tablas ACID sobre Parquet con historial |

## Modos de escritura

`overwrite` reemplaza, `append` agrega, `ignore` no hace nada si existe,
`error` falla si ya existe.
        """),
        code("""
# Crear datasets sinteticos para mostrar lectura/escritura sin depender de archivos locales
from pyspark.sql import functions as F

io_base = spark.createDataFrame([
    (1, "Bogota", "2026-01-01", 120.0),
    (2, "Cali", "2026-01-02", 90.5),
    (3, "Medellin", "2026-01-03", 150.2),
], ["id", "ciudad", "fecha_txt", "valor"])

io_base = io_base.withColumn("fecha", F.to_date("fecha_txt")).drop("fecha_txt")
io_base.show()
        """),
        code("""
# Parquet en Volume si existe permiso; si no, seguir con tabla administrada
VOLUME_NAME = "sesion9_archivos"
BASE_IO_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME_NAME}"
PARQUET_PATH = f"{BASE_IO_PATH}/io_demo_parquet"
JSON_PATH = f"{BASE_IO_PATH}/io_demo_json"
CSV_PATH = f"{BASE_IO_PATH}/io_demo_csv"

try:
    spark.sql(f"CREATE VOLUME IF NOT EXISTS {CATALOG}.{SCHEMA}.{VOLUME_NAME}")
    io_base.write.mode("overwrite").parquet(PARQUET_PATH)
    io_base.write.mode("overwrite").json(JSON_PATH)
    io_base.write.mode("overwrite").option("header", True).csv(CSV_PATH)

    print("Lectura Parquet:")
    spark.read.parquet(PARQUET_PATH).show()

    print("Lectura JSON:")
    spark.read.json(JSON_PATH).show()

    print("Lectura CSV con opciones:")
    spark.read.option("header", True).option("inferSchema", True).csv(CSV_PATH).show()
except Exception as exc:
    print("No fue posible crear o escribir en un Volume.")
    print("Seguimos con tablas administradas, que funcionan bien para la clase.")
    print(f"Detalle: {type(exc).__name__}: {exc}")
    PARQUET_TABLE = nombre_tabla("sesion9_parquet_demo")
    io_base.write.format("parquet").mode("overwrite").saveAsTable(PARQUET_TABLE)
    print(f"Tabla Parquet administrada creada: {PARQUET_TABLE}")
    spark.read.table(PARQUET_TABLE).show()
        """),
        interp("datos locales, Volumes y formatos", [
            "Databricks no lee directamente `C:\\Users`; necesita rutas accesibles al workspace.",
            "Parquet conserva schema y es columnar; CSV necesita opciones e inferencia.",
            "En serverless, Volumes o tablas administradas son mas seguros que depender de DBFS legacy."
        ]),
        md("""
## `saveAsTable()` vs `write.save()`

- `saveAsTable("catalog.schema.tabla")` crea una tabla gobernada.
- `write.save("/Volumes/...")` escribe archivos en un Volume.
- Para analitica repetible, prefiere tablas Delta.
        """),
        code("""
# Leer, transformar y escribir como tabla Delta
DESTINO_IO = nombre_tabla("sesion9_io_delta")

resultado_io = (
    io_base
    .withColumn("valor_con_iva", F.round(F.col("valor") * 1.19, 2))
    .withColumn("anio", F.year("fecha"))
)

(
    resultado_io.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(DESTINO_IO)
)

spark.read.table(DESTINO_IO).show()
        """),
        code("""
# COPY INTO y Auto Loader: patrones de ingesta
print("COPY INTO para ingesta incremental desde archivos:")
print(f'''
COPY INTO {DESTINO_IO}
FROM '/Volumes/<catalog>/<schema>/<volume>/nuevos_archivos/'
FILEFORMAT = PARQUET
COPY_OPTIONS ('mergeSchema' = 'true')
''')

print("Auto Loader para streaming de archivos:")
print('''
df_stream = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .load("/Volumes/<catalog>/<schema>/<volume>/raw/")
)
''')
        """),
    ]


def _seccion_7():
    return [
        section_header("7", "Lazy evaluation, Catalyst, Jobs, Stages y repartition"),
        md("""
## Definicion formal

Spark usa **lazy evaluation**: las transformaciones construyen un plan, pero no
ejecutan trabajo hasta que aparece una accion. **Catalyst** optimiza ese plan.

```
Codigo PySpark -> Logical plan -> Optimized plan -> Physical plan -> Jobs/Stages/Tasks
```

## Explicacion paso a paso

Cuando escribes `filter`, `select` o `withColumn`, Spark todavia esta planeando.
Cuando escribes `count`, `show`, `collect`, `toPandas` o `write`, Spark ejecuta.
        """),
        code("""
# Lazy evaluation: construir un plan es rapido porque aun no lee todos los datos
import time
from pyspark.sql import functions as F

t0 = time.perf_counter()
pipeline = (
    sdf
    .filter(F.col("fare_amount") > 0)
    .filter(F.col("trip_distance") > 0.1)
    .withColumn("pickup_hour", F.hour("tpep_pickup_datetime"))
    .withColumn("tarifa_por_milla", F.col("fare_amount") / F.col("trip_distance"))
)
print(f"Construir plan: {(time.perf_counter() - t0) * 1000:.2f} ms")
print(pipeline)
        """),
        code("""
# explain en varios modos
print("PLAN SIMPLE")
pipeline.explain(False)

print("\\nPLAN EXTENDED")
pipeline.explain("extended")

print("\\nPLAN FORMATTED")
pipeline.explain("formatted")
        """),
        interp("planes de Spark", [
            "`Project` suele indicar seleccion o columnas derivadas.",
            "`Filter` representa filtros.",
            "`Exchange` normalmente indica shuffle, una redistribucion costosa."
        ]),
        md("""
## Jobs, Stages y Tasks

- Una **accion** dispara normalmente un Job.
- Un **Stage** es una secuencia de operaciones que puede ejecutarse sin shuffle.
- Un **Task** es la unidad de trabajo paralela sobre una particion.
- Cada `Exchange` suele partir el DAG en nuevos stages.
        """),
        code("""
# Predicate pushdown: seleccionar columnas y filtrar temprano
plan_con_filtro = (
    leer_taxi()
    .select("fare_amount", "trip_distance", "pickup_zip")
    .filter(F.col("fare_amount").between(10, 50))
    .filter(F.col("trip_distance") > 1)
)

plan_con_filtro.explain("formatted")
print(f"Filas resultantes: {plan_con_filtro.count():,}")
        """),
        code("""
# repartition vs coalesce sin usar APIs RDD
# En serverless evitamos APIs de bajo nivel de RDD.
pequeno = spark.range(0, 1000)

reparticionado = pequeno.repartition(8)
coalescido = reparticionado.coalesce(1)

print("Plan con repartition(8): busca Exchange, porque repartition hace shuffle.")
reparticionado.explain("formatted")

print("\\nPlan con coalesce(1): reduce particiones con menor costo, pero puede desbalancear.")
coalescido.explain("formatted")

print("\\nValidacion con acciones simples:")
print("Filas reparticionado:", reparticionado.count())
print("Filas coalescido    :", coalescido.count())
        """),
        code("""
# Cache: demo conceptual compatible con entornos donde cache puede estar limitado
base = pipeline.select("pickup_hour", "fare_amount", "tarifa_por_milla")

try:
    base.cache()
    print("Primera accion materializa cache:")
    print(base.count())
    print("Segunda accion puede reutilizar cache:")
    base.groupBy("pickup_hour").count().show(5)
    base.unpersist()
except Exception as exc:
    print("Cache no disponible o limitado en este compute.")
    print("En algunos entornos administrados pueden existir restricciones de cache DataFrame/SQL.")
    print(f"Detalle: {type(exc).__name__}: {exc}")
        """),
    ]


def _seccion_8():
    return [
        section_header("8", "Photon y Liquid Clustering"),
        md("""
## Photon

**Photon** es un motor de ejecucion vectorizado de Databricks. Acelera muchas
consultas SQL/DataFrame sin cambiar el codigo.

## Liquid Clustering

**Liquid Clustering** organiza tablas Delta segun columnas de consulta frecuentes.
Es el reemplazo moderno de muchos patrones basados en `PARTITION BY` y `ZORDER`.
        """),
        code("""
# Crear tabla Delta con Liquid Clustering
LC_TABLE = nombre_tabla("taxi_liquid_sesion9")

try:
    spark.sql(f'''
    CREATE OR REPLACE TABLE {LC_TABLE}
    CLUSTER BY (tpep_pickup_datetime, fare_amount)
    AS
    SELECT *
    FROM taxi_source_v
    WHERE fare_amount > 0
    ''')
except Exception as exc:
    print("Liquid Clustering no esta disponible en este entorno; creando tabla Delta normal.")
    print(f"Detalle: {type(exc).__name__}: {exc}")
    spark.sql(f'''
    CREATE OR REPLACE TABLE {LC_TABLE}
    USING DELTA
    AS
    SELECT *
    FROM taxi_source_v
    WHERE fare_amount > 0
    ''')

spark.sql(f"DESCRIBE DETAIL {LC_TABLE}").select(
    "format", "clusteringColumns", "numFiles", "sizeInBytes"
).show(truncate=False)
        """),
        code("""
# OPTIMIZE aplica fisicamente la organizacion
try:
    spark.sql(f"OPTIMIZE {LC_TABLE}")
except Exception as exc:
    print("OPTIMIZE no esta disponible en este entorno o runtime.")
    print(f"Detalle: {type(exc).__name__}: {exc}")

spark.sql(f"DESCRIBE HISTORY {LC_TABLE}").select(
    "version", "timestamp", "operation"
).show(5, truncate=False)
        """),
        md("""
## Predictive Optimization

En workspaces que lo tienen habilitado, Databricks puede ejecutar mantenimiento
como `OPTIMIZE` y `VACUUM` automaticamente segun patrones de uso.
        """),
    ]


def _seccion_9():
    return [
        section_header("9", "Funciones de cadenas, fechas y colecciones"),
        md("""
## Definicion formal

`pyspark.sql.functions` contiene funciones nativas que Spark puede optimizar.
Para una primera introduccion, es mejor preferir estas funciones antes que UDFs.
        """),
        code("""
# Funciones de cadenas
from pyspark.sql import functions as F

texto_df = spark.createDataFrame([
    (1, "  Bogota Norte  ", "factura-2026-0001"),
    (2, "cali sur", "factura-2026-0002"),
    (3, "MEDELLIN centro", "recibo-2025-0099"),
], ["id", "zona", "documento"])

texto_res = (
    texto_df
    .withColumn("zona_limpia", F.trim("zona"))
    .withColumn("zona_upper", F.upper("zona_limpia"))
    .withColumn("largo", F.length("zona_limpia"))
    .withColumn("tipo_doc", F.regexp_extract("documento", r"^([a-z]+)", 1))
    .withColumn("anio_doc", F.regexp_extract("documento", r"(\\d{4})", 1))
    .withColumn("zona_partes", F.split(F.lower("zona_limpia"), " "))
    .withColumn("etiqueta", F.concat_ws(" | ", "zona_upper", "documento"))
)
texto_res.show(truncate=False)
        """),
        code("""
# Funciones de fechas y tiempo
fechas_df = spark.createDataFrame([
    ("2026-01-05 08:30:00",),
    ("2026-02-10 14:45:00",),
    ("2026-03-20 23:05:00",),
], ["ts_txt"])

fechas_res = (
    fechas_df
    .withColumn("ts", F.to_timestamp("ts_txt"))
    .withColumn("fecha", F.to_date("ts"))
    .withColumn("anio", F.year("ts"))
    .withColumn("mes", F.month("ts"))
    .withColumn("dia", F.dayofmonth("ts"))
    .withColumn("hora", F.hour("ts"))
    .withColumn("fecha_mas_7", F.date_add("fecha", 7))
    .withColumn("inicio_mes", F.date_trunc("month", "ts"))
    .withColumn("dias_desde_hoy", F.datediff(F.current_date(), F.col("fecha")))
)
fechas_res.show(truncate=False)
        """),
        code("""
# Arrays y maps
colecciones = spark.createDataFrame([
    (1, ["spark", "delta", "spark"], {"nivel": "intro", "motor": "spark"}),
    (2, ["sql", "parquet"], {"nivel": "intro", "motor": "sql"}),
], ["id", "temas", "meta"])

colecciones_res = (
    colecciones
    .withColumn("n_temas", F.size("temas"))
    .withColumn("temas_unicos", F.array_distinct("temas"))
    .withColumn("incluye_spark", F.array_contains("temas", "spark"))
    .withColumn("meta_keys", F.map_keys("meta"))
    .withColumn("meta_values", F.map_values("meta"))
)
colecciones_res.show(truncate=False)

colecciones_res.select("id", F.explode("temas_unicos").alias("tema")).show()
        """),
        code("""
# Operaciones de conjuntos entre DataFrames
a = spark.createDataFrame([(1, "A"), (2, "B"), (3, "C")], ["id", "letra"])
b = spark.createDataFrame([(3, "C"), (4, "D"), (5, "E")], ["id", "letra"])

print("unionByName")
a.unionByName(b).show()

print("intersect")
a.intersect(b).show()

print("subtract")
a.subtract(b).show()

print("distinct despues de union")
a.unionByName(b).distinct().show()
        """),
        interp("funciones nativas", [
            "Las funciones nativas permanecen dentro del plan de Spark.",
            "Spark puede optimizar filtros, proyecciones y expresiones mejor que una UDF Python.",
            "Estas funciones cubren gran parte del trabajo cotidiano de limpieza."
        ]),
    ]


def _seccion_10():
    return [
        section_header("10", "Transformaciones completas de la API PySpark"),
        md("""
## Mapa mental

| Tipo | Operaciones |
|---|---|
| Narrow | `select`, `filter`, `withColumn`, `drop` |
| Wide | `groupBy`, `join`, `distinct`, `orderBy` |
| Analiticas | `Window`, `pivot`, percentiles |
| Calidad | `na.drop`, `na.fill`, `dropDuplicates` |
        """),
        code("""
# Base enriquecida para el tour PySpark
from pyspark.sql.window import Window

enriquecido = (
    sdf
    .select(
        "tpep_pickup_datetime", "tpep_dropoff_datetime",
        "fare_amount", "trip_distance", "pickup_zip", "dropoff_zip"
    )
    .filter(F.col("fare_amount").between(1, 200))
    .filter(F.col("trip_distance") > 0)
    .withColumn("pickup_hour", F.hour("tpep_pickup_datetime"))
    .withColumn(
        "duracion_min",
        (F.unix_timestamp("tpep_dropoff_datetime") - F.unix_timestamp("tpep_pickup_datetime")) / 60
    )
    .withColumn("tarifa_por_milla", F.col("fare_amount") / F.col("trip_distance"))
    .withColumn(
        "categoria_viaje",
        F.when(F.col("trip_distance") < 1, "micro")
         .when(F.col("trip_distance") < 3, "corto")
         .when(F.col("trip_distance") < 10, "medio")
         .otherwise("largo")
    )
    .filter(F.col("duracion_min").between(1, 180))
)
enriquecido.show(5, truncate=False)
        """),
        code("""
# groupBy + agg
metricas = (
    enriquecido
    .groupBy("pickup_hour", "categoria_viaje")
    .agg(
        F.count("*").alias("viajes"),
        F.round(F.avg("fare_amount"), 2).alias("tarifa_prom"),
        F.round(F.avg("tarifa_por_milla"), 2).alias("tarifa_por_milla_prom"),
        F.round(F.stddev("fare_amount"), 2).alias("tarifa_std"),
        F.round(F.percentile_approx("fare_amount", 0.9), 2).alias("tarifa_p90"),
    )
    .orderBy("pickup_hour", "categoria_viaje")
)
metricas.show(10, truncate=False)
metricas.explain("formatted")
        """),
        code("""
# Window functions
w_hora = Window.partitionBy("pickup_hour").orderBy(F.desc("viajes"))

top_hora = (
    metricas
    .withColumn("rank_en_hora", F.rank().over(w_hora))
    .filter(F.col("rank_en_hora") <= 2)
    .orderBy("pickup_hour", "rank_en_hora")
)
top_hora.show(20, truncate=False)
        """),
        code("""
# Join con broadcast
zip_ref = (
    enriquecido.select("pickup_zip")
    .where(F.col("pickup_zip").isNotNull())
    .distinct()
    .limit(500)
    .withColumn(
        "zona",
        F.when(F.col("pickup_zip").between(10001, 10099), "Manhattan")
         .otherwise("Otra")
    )
)

joined = (
    enriquecido
    .join(F.broadcast(zip_ref), on="pickup_zip", how="left")
    .groupBy("zona")
    .agg(F.count("*").alias("viajes"), F.round(F.avg("fare_amount"), 2).alias("tarifa_prom"))
)
joined.show()
joined.explain("formatted")
        """),
        code("""
# Pivot
pivot_categoria = (
    enriquecido
    .groupBy("pickup_hour")
    .pivot("categoria_viaje", ["micro", "corto", "medio", "largo"])
    .agg(F.count(F.lit(1)))
    .orderBy("pickup_hour")
)
pivot_categoria.show()
        """),
        code("""
# Calidad de datos
sdf.select([
    F.round(F.sum(F.col(c).isNull().cast("int")) / F.count("*") * 100, 2).alias(c)
    for c in ["fare_amount", "trip_distance", "pickup_zip", "dropoff_zip"]
]).show(truncate=False)

limpio = (
    sdf.na.drop(subset=["fare_amount", "trip_distance"])
       .filter(F.col("fare_amount") > 0)
       .filter(F.col("trip_distance") > 0)
       .dropDuplicates(["tpep_pickup_datetime", "tpep_dropoff_datetime", "fare_amount"])
)
print(f"Filas limpias: {limpio.count():,}")
        """),
        code("""
# UDF vs pandas_udf vs funcion nativa: patron pedagogico
print("Orden recomendado:")
print("1. Funcion nativa de pyspark.sql.functions")
print("2. pandas_udf si la logica vectorizada en Python es inevitable")
print("3. udf clasica solo cuando no haya alternativa")

clasificacion_nativa = (
    enriquecido
    .withColumn(
        "tipo_duracion",
        F.when(F.col("duracion_min") < 5, "rapido")
         .when(F.col("duracion_min") < 20, "normal")
         .otherwise("largo")
    )
    .groupBy("tipo_duracion")
    .count()
)
clasificacion_nativa.show()
        """),
        interp("API PySpark", [
            "La API DataFrame permite escribir transformaciones legibles y optimizables.",
            "Los shuffles aparecen en agregaciones, joins y pivots.",
            "Despues de cada salida, interpreta patron descriptivo y limitaciones."
        ]),
    ]


def _seccion_11():
    return [
        section_header("11", "Por que Spark sobre Pandas, y cuando no"),
        md("""
## Idea clave

Pandas no es "malo" y Spark no es "siempre mejor". Pandas gana cuando el dataset
cabe comodamente en memoria y se necesita iterar rapido. Spark gana cuando el
volumen crece, se requieren pipelines reproducibles, SQL distribuido, observabilidad
y tablas gobernadas.
        """),
        code("""
# Comparacion representativa: Spark vs Pandas
import time
import pandas as pd

MUESTRA = leer_taxi().limit(500000)

t0 = time.perf_counter()
spark_res = (
    MUESTRA
    .filter(F.col("fare_amount") > 0)
    .withColumn("hora", F.hour("tpep_pickup_datetime"))
    .groupBy("hora")
    .agg(F.count("*").alias("viajes"), F.round(F.avg("fare_amount"), 2).alias("tarifa_prom"))
    .orderBy("hora")
)
spark_res.show(5)
t_spark = time.perf_counter() - t0

t0 = time.perf_counter()
pdf = MUESTRA.select("fare_amount", "tpep_pickup_datetime").toPandas()
pdf = pdf[pdf["fare_amount"] > 0].copy()
pdf["hora"] = pd.to_datetime(pdf["tpep_pickup_datetime"]).dt.hour
pdf_res = pdf.groupby("hora")["fare_amount"].agg(["count", "mean"]).sort_index()
print(pdf_res.head())
t_pandas = time.perf_counter() - t0

print(f"Spark : {t_spark:.2f}s")
print(f"Pandas: {t_pandas:.2f}s")
print("Nota: el tiempo Pandas incluye toPandas(), que mueve datos al driver.")
        """),
        md("""
## Tabla de decision

| Criterio | Elige Pandas | Elige Spark |
|---|---|---|
| Tamano | Cabe en RAM | Puede superar la RAM |
| Iteracion | Muy rapida | Pipeline estable |
| SQL distribuido | No necesario | Necesario |
| Observabilidad | Baja prioridad | Query Profile / Jobs |
| Tablas Delta | No nativo | Integrado |
        """),
    ]


def _seccion_12():
    return [
        section_header("12", "Por que Spark sobre Dask, y cuando no"),
        md("""
## Diferencia arquitectural

Dask escala Python y se integra muy bien con numpy, scipy y scikit-learn. Spark
trabaja con un optimizador SQL/DataFrame maduro: Catalyst. Por eso Spark suele
ser mas fuerte en data engineering, joins grandes, SQL distribuido y lakehouse.

## Por que no ejecutamos Dask en este notebook

En Databricks Free/Community serverless, las versiones de librerias externas
pueden no coincidir con las que espera un ejemplo de Dask. Para evitar que la
clase dependa de instalaciones o conflictos de version, esta seccion queda como
comparacion conceptual.

La decision tecnica sigue siendo importante:

- Si el flujo nace en Pandas/numpy/scipy y quieres paralelizar Python, Dask puede ser natural.
- Si el flujo vive en tablas, SQL, Delta Lake, jobs y gobierno de datos, Spark suele ser mejor.
- Para esta clase, Spark es el motor que ya viene integrado y soportado por Databricks.
        """),
        code("""
# Ejemplo equivalente SOLO en Spark: groupBy y join sobre la fuente de taxis
sdf_bench = (
    leer_taxi()
    .select("fare_amount", "tpep_pickup_datetime", "pickup_zip")
    .where("fare_amount > 0")
)

spark_bench = (
    sdf_bench
    .withColumn("hora", F.hour("tpep_pickup_datetime"))
    .groupBy("hora")
    .agg(
        F.count(F.lit(1)).alias("viajes"),
        F.round(F.avg("fare_amount"), 2).alias("tarifa_prom")
    )
    .orderBy("hora")
)
spark_bench.show(5)

zip_ref = (
    sdf_bench
    .select("pickup_zip")
    .where(F.col("pickup_zip").isNotNull())
    .distinct()
    .withColumn("zona_referencia", F.lit("zona_demo"))
)

join_spark = sdf_bench.join(F.broadcast(zip_ref), on="pickup_zip", how="inner")
print(f"Filas join Spark: {join_spark.count():,}")
join_spark.explain("formatted")
        """),
        md("""
## Tabla de decision

| Criterio | Elige Dask | Elige Spark |
|---|---|---|
| Ecosistema numpy/scipy | Prioritario | Secundario |
| Migracion desde Pandas | Gradual | Requiere nueva mentalidad |
| SQL distribuido | Limitado | Nativo |
| Optimizacion de joins | Menor | Catalyst |
| Lakehouse/Delta | No nativo | Integrado |
        """),
    ]


def _seccion_13():
    return [
        section_header("13", "Delta Lake avanzado"),
        md("""
## Definicion formal

**Delta Lake** guarda datos en archivos Parquet y agrega un transaction log
`_delta_log`. Ese log permite ACID, historial, MERGE, time travel, schema
enforcement y schema evolution.

## Parquet vs Delta

Parquet es formato de archivo. Delta es una capa transaccional sobre Parquet.
        """),
        code("""
# Crear tabla Delta base
DELTA_MAIN = nombre_tabla("taxi_sesion9_main")

try:
    spark.sql(f'''
    CREATE OR REPLACE TABLE {DELTA_MAIN}
    CLUSTER BY (tpep_pickup_datetime, pickup_zip)
    AS
    SELECT
      CAST(row_number() OVER (ORDER BY tpep_pickup_datetime) AS BIGINT) AS trip_id,
      tpep_pickup_datetime,
      tpep_dropoff_datetime,
      pickup_zip,
      dropoff_zip,
      fare_amount,
      trip_distance,
      CAST(1 AS INT) AS es_valido
    FROM taxi_source_v
    WHERE fare_amount > 0 AND trip_distance > 0
    ''')
except Exception as exc:
    print("CLUSTER BY no disponible; creando tabla Delta normal.")
    print(f"Detalle: {type(exc).__name__}: {exc}")
    spark.sql(f'''
    CREATE OR REPLACE TABLE {DELTA_MAIN}
    USING DELTA
    AS
    SELECT
      CAST(row_number() OVER (ORDER BY tpep_pickup_datetime) AS BIGINT) AS trip_id,
      tpep_pickup_datetime,
      tpep_dropoff_datetime,
      pickup_zip,
      dropoff_zip,
      fare_amount,
      trip_distance,
      CAST(1 AS INT) AS es_valido
    FROM taxi_source_v
    WHERE fare_amount > 0 AND trip_distance > 0
    ''')

spark.sql(f"DESCRIBE DETAIL {DELTA_MAIN}").select("format", "numFiles", "sizeInBytes").show()
        """),
        code("""
# MERGE: upsert
from delta.tables import DeltaTable

updates = spark.createDataFrame([
    (1, 0),
    (2, 0),
    (999999999, 1),
], ["trip_id", "es_valido"])

target = DeltaTable.forName(spark, DELTA_MAIN)

(
    target.alias("t")
    .merge(updates.alias("s"), "t.trip_id = s.trip_id")
    .whenMatchedUpdate(set={"es_valido": "s.es_valido"})
    .whenNotMatchedInsert(values={
        "trip_id": "s.trip_id",
        "tpep_pickup_datetime": "CAST(NULL AS TIMESTAMP)",
        "tpep_dropoff_datetime": "CAST(NULL AS TIMESTAMP)",
        "pickup_zip": "CAST(NULL AS INT)",
        "dropoff_zip": "CAST(NULL AS INT)",
        "fare_amount": "CAST(0 AS DOUBLE)",
        "trip_distance": "CAST(0 AS DOUBLE)",
        "es_valido": "s.es_valido",
    })
    .execute()
)

spark.sql(f"DESCRIBE HISTORY {DELTA_MAIN}").select(
    "version", "timestamp", "operation", "operationMetrics"
).show(5, truncate=False)
        """),
        code("""
# Time Travel y RESTORE
version_0 = spark.read.format("delta").option("versionAsOf", 0).table(DELTA_MAIN).count()
actual = spark.read.table(DELTA_MAIN).count()

print(f"Version 0: {version_0:,}")
print(f"Actual   : {actual:,}")

spark.sql(f"RESTORE TABLE {DELTA_MAIN} TO VERSION AS OF 0")
spark.sql(f"DESCRIBE HISTORY {DELTA_MAIN}").select("version", "timestamp", "operation").show(5, truncate=False)
        """),
        md("""
## Schema evolution, CONVERT y CLONE

- **Schema enforcement** evita escribir columnas inesperadas.
- **Schema evolution** permite agregar columnas de forma controlada.
- **CONVERT TO DELTA** convierte Parquet existente a Delta.
- **SHALLOW CLONE** copia metadatos y apunta a los mismos archivos.
- **DEEP CLONE** copia tambien archivos fisicos.
        """),
        code("""
# Schema evolution con ALTER TABLE y mergeSchema
spark.sql(f"ALTER TABLE {DELTA_MAIN} ADD COLUMNS (comentario_calidad STRING)")

df_nueva_col = spark.read.table(DELTA_MAIN).limit(10).withColumn("fuente_lote", F.lit("demo"))
(
    df_nueva_col.write
    .format("delta")
    .mode("append")
    .option("mergeSchema", "true")
    .saveAsTable(DELTA_MAIN)
)

spark.read.table(DELTA_MAIN).printSchema()
        """),
        code("""
# CLONE: crear tabla de prueba
CLONE_TABLE = nombre_tabla("taxi_sesion9_clone")

try:
    spark.sql(f"DROP TABLE IF EXISTS {CLONE_TABLE}")
    spark.sql(f"CREATE TABLE {CLONE_TABLE} SHALLOW CLONE {DELTA_MAIN}")
    spark.sql(f"DESCRIBE HISTORY {CLONE_TABLE}").select("version", "timestamp", "operation").show(5, truncate=False)
except Exception as exc:
    print("CLONE puede no estar disponible en este workspace.")
    print(f"Detalle: {type(exc).__name__}: {exc}")
        """),
        code("""
# VACUUM: eliminar archivos obsoletos
print("VACUUM elimina archivos obsoletos que ya no son necesarios para la tabla Delta.")
print("En Databricks serverless no cambiamos la configuracion de retencion.")
print("Usamos la retencion segura por defecto de Delta Lake.")

spark.sql(f"VACUUM {DELTA_MAIN}")
spark.sql(f"DESCRIBE DETAIL {DELTA_MAIN}").select("numFiles", "sizeInBytes").show()

print("\\nAdvertencia:")
print("En algunos laboratorios antiguos se fuerza una retencion de cero horas.")
print("No hacemos eso aqui: reduce o elimina la capacidad de hacer time travel a versiones antiguas.")
        """),
    ]


def _seccion_14():
    return [
        section_header("14", "Lakeflow / Delta Live Tables"),
        md("""
## Definicion formal

**Lakeflow Spark Declarative Pipelines** es la evolucion del producto conocido
como **Delta Live Tables (DLT)**. La API Python todavia usa el modulo `dlt`.

No se ejecuta como celda interactiva comun: se configura como pipeline. Esta
seccion imprime el patron para que el estudiante entienda la arquitectura.
        """),
        code("""
# Codigo pedagogico de pipeline Lakeflow/DLT
PIPELINE_CODE = '''
import dlt
from pyspark.sql import functions as F

@dlt.view(name="taxi_raw_view")
def taxi_raw_view():
    return spark.read.table("default.taxi_source_delta")

@dlt.table(name="taxi_bronze", comment="Ingesta raw")
def taxi_bronze():
    return dlt.read("taxi_raw_view")

@dlt.table(name="taxi_silver", comment="Datos limpios")
@dlt.expect_all({
    "fare_positivo": "fare_amount > 0",
    "distancia_positiva": "trip_distance > 0"
})
@dlt.expect_or_drop("duracion_valida", "tpep_dropoff_datetime >= tpep_pickup_datetime")
def taxi_silver():
    return (
        dlt.read("taxi_bronze")
        .withColumn("pickup_hour", F.hour("tpep_pickup_datetime"))
        .withColumn("tarifa_por_milla", F.col("fare_amount") / F.col("trip_distance"))
    )

@dlt.table(name="taxi_gold_hourly", comment="Metricas por hora")
def taxi_gold_hourly():
    return (
        dlt.read("taxi_silver")
        .groupBy("pickup_hour")
        .agg(
            F.count("*").alias("viajes"),
            F.round(F.avg("fare_amount"), 2).alias("tarifa_prom")
        )
    )
'''

print(PIPELINE_CODE)
print("Para ejecutar: Workflows -> Lakeflow Declarative Pipelines -> Create pipeline")
        """),
        md("""
## Batch vs streaming

- Usa **batch** cuando reprocesas lotes completos o tablas estables.
- Usa **streaming** cuando llegan archivos o eventos nuevos continuamente.
- En Databricks Free/Community serverless esta seccion es introductoria; verifica los triggers soportados por tu workspace.

## Parametros

Un pipeline puede leer parametros con `spark.conf.get("pipeline.parametro")`.
Esto permite cambiar fuentes, fechas o modos sin editar codigo.
        """),
        code("""
# Patron streaming pedagogico: imprimir, no ejecutar aqui
STREAMING_PATTERN = '''
import dlt

@dlt.table(name="eventos_bronze_stream")
def eventos_bronze_stream():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load("/Volumes/<catalog>/<schema>/<volume>/raw_events/")
    )
'''

print(STREAMING_PATTERN)
        """),
    ]


def _seccion_15():
    return [
        section_header("15", "Databricks Workflows y Jobs"),
        md("""
## Definicion formal

Un **Job** ejecuta una tarea de forma reproducible. Un **Workflow** puede contener
varias tareas conectadas como DAG: notebooks, Python scripts, SQL, pipelines
Lakeflow, dbt u otros tipos.

## Explicacion paso a paso

El notebook interactivo sirve para aprender y explorar. El Job sirve para operar:
programar, parametrizar, monitorear, reintentar y notificar.
        """),
        md("""
## Conceptos clave

| Concepto | Explicacion |
|---|---|
| Task | Unidad ejecutable dentro de un Job |
| Job cluster | Compute creado para el Job |
| Existing compute | Compute reutilizado |
| Schedule | Programacion cron o trigger |
| Parameters | Valores que cambian sin editar codigo |
| Notifications | Alertas por exito, falla o duracion |
        """),
        md("""
## Jobs vs Lakeflow

Usa **Jobs** para orquestacion general: notebooks, SQL, scripts, modelos, reportes.
Usa **Lakeflow** cuando el problema central es declarar tablas de datos con
dependencias, calidad y procesamiento incremental.
        """),
        code("""
# Patron para que un notebook sea invocable como task
dbutils.widgets.text("fecha_proceso", "2026-01-01", "Fecha de proceso")
dbutils.widgets.dropdown("modo", "demo", ["demo", "produccion"], "Modo")

fecha_proceso = dbutils.widgets.get("fecha_proceso")
modo = dbutils.widgets.get("modo")

print(f"Ejecutando notebook con fecha_proceso={fecha_proceso}, modo={modo}")

# En un Job real, al final se puede devolver un resultado textual:
# dbutils.notebook.exit("ok")
        """),
    ]


def _seccion_16():
    return [
        section_header("16", "Taller end-to-end"),
        md("""
## Objetivo del taller

Aplicar los conceptos de la sesion en ejercicios guiados. Cada ejercicio tiene
instrucciones y deja un `NotImplementedError` para que el estudiante complete.
        """),
        code("""
# Ejercicio 1 -- Window functions
# Construye el top 3 de categorias de viaje por hora con mayor tarifa_por_milla promedio.
# Requisitos:
# - Leer la fuente de taxis preparada en `leer_taxi()`.
# - Crear pickup_hour, tarifa_por_milla y categoria_viaje.
# - Agrupar por pickup_hour y categoria_viaje.
# - Filtrar grupos con menos de 100 viajes.
# - Usar Window.partitionBy("pickup_hour").orderBy(F.desc("tarifa_por_milla_prom")).

raise NotImplementedError("Completa el ejercicio 1 siguiendo las instrucciones.")
        """),
        code("""
# Ejercicio 2 -- MERGE en Delta
# Crea una tabla Delta con viajes del pickup_zip mas frecuente.
# Luego usa MERGE para marcar es_valido=0 donde fare_amount > 100 e insertar 3 filas nuevas.

raise NotImplementedError("Completa el ejercicio 2 siguiendo las instrucciones.")
        """),
        code("""
# Ejercicio 3 -- Reporte de calidad
# Construye un DataFrame [metrica, valor] con:
# - pct_nulos por columna
# - pct_negativos para columnas numericas
# - top 5 pickup_zip
# - total_filas

raise NotImplementedError("Completa el ejercicio 3 siguiendo las instrucciones.")
        """),
        code("""
# Ejercicio 4 -- Schema + I/O
# Define un StructType de 5 columnas, crea DataFrame sintetico, escribe con saveAsTable,
# lee de vuelta, verifica schema y agrega una columna con ALTER TABLE.

raise NotImplementedError("Completa el ejercicio 4 siguiendo las instrucciones.")
        """),
        code("""
# Ejercicio 5 -- Pipeline completo Databricks
# Lee la fuente de taxis preparada, filtra, enriquece con 5 columnas derivadas,
# crea tabla Silver con Liquid Clustering, ejecuta MERGE con 5 actualizaciones
# y muestra DESCRIBE HISTORY.

raise NotImplementedError("Completa el ejercicio 5 siguiendo las instrucciones.")
        """),
        md("""
## Checklist final

```
[ ] Uso `catalog.schema.table` cuando Unity Catalog esta disponible
[ ] Entiendo por que C:\\Users no funciona dentro de Databricks
[ ] Uso Volumes o tablas administradas en lugar de depender de DBFS legacy
[ ] Prefiero DataFrames/Spark SQL sobre RDDs para el trabajo principal
[ ] Uso %pip, no %sh pip
[ ] Puedo leer CSV, JSON, Parquet y Delta
[ ] Puedo explicar Parquet vs Delta
[ ] Puedo leer un plan con explain()
[ ] Reconozco Exchange como posible shuffle
[ ] Priorizo funciones nativas sobre UDFs
[ ] Entiendo el patron bronze/silver/gold
[ ] Se cuando usar Jobs y cuando Lakeflow
```

## Cierre

La idea mas importante: Databricks no es solo un notebook. Es una plataforma
para convertir datos en tablas confiables, transformaciones reproducibles y
ejecuciones gobernadas.
        """),
        md("""
## Referencias

- Databricks Free Edition: https://docs.databricks.com/aws/en/getting-started/free-edition
- Databricks Free Edition limitations: https://docs.databricks.com/aws/en/getting-started/free-edition-limitations
- Serverless compute limitations: https://docs.databricks.com/aws/en/compute/serverless/limitations
- Databricks notebooks: https://docs.databricks.com/en/notebooks/
- DBFS: https://docs.databricks.com/en/dbfs/
- Databricks widgets: https://docs.databricks.com/en/notebooks/widgets.html
- Unity Catalog Volumes: https://docs.databricks.com/aws/en/volumes/
- Apache Spark documentation: https://spark.apache.org/docs/latest/
- PySpark functions: https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/functions.html
- Apache Parquet: https://parquet.apache.org/docs/
- Delta Lake: https://docs.delta.io/latest/index.html
- Lakeflow Declarative Pipelines: https://docs.databricks.com/en/delta-live-tables/index.html
        """),
    ]


def build_cells():
    cells = [
        *uce_header(
            title="Databricks: tutorial completo de introduccion",
            session=9,
            github_path="main/Cuadernos/9_Databricks_Serverless_Completo.ipynb",
            nota_plataforma=(
                "Databricks Free/Community 2026 con compute serverless. "
                "El notebook evita DBFS legacy y prioriza tablas, Volumes y Spark SQL."
            ),
        ),
        _proposito(),
        _correspondencia(),
        _toc(),
        *_seccion_0(),
        *_seccion_1(),
        *_seccion_2(),
        pregunta(1, "Spark", "En esta clase el punto de entrada sera el objeto `spark`.", "Que herramienta conviene priorizar para trabajar con tablas en Databricks?", ["DataFrames y Spark SQL", "Bucles locales sobre listas", "Archivos del computador sin subirlos", "Variables sueltas sin tabla"], "A", "DataFrames y Spark SQL son el patron principal para leer, transformar y guardar datos."),
        *_seccion_3(),
        pregunta(2, "Tablas", "Databricks serverless no ve directamente el disco local del estudiante.", "Cual ruta NO debe usarse dentro de Databricks para leer datos del computador local?", ["catalog.schema.table", "/Volumes/catalog/schema/volume/datos.csv", "archivo subido al workspace", "C:/datos/trips.csv"], "D", "Databricks no ve directamente el disco local; se debe subir el archivo o usar Volumes/tablas."),
        *_seccion_4(),
        pregunta(3, "Spark SQL", "Una TempView vive durante la sesion.", "Que conviene usar para persistir resultados?", ["TempView", "Tabla administrada", "Variable Python", "print"], "B", "Una tabla administrada permanece disponible despues de la celda."),
        *_seccion_5(),
        pregunta(4, "Schemas", "El schema es el contrato del dato.", "Por que declarar schema ayuda?", ["Evita toda ejecucion", "Reduce errores de inferencia y cambios silenciosos", "Convierte todo a texto", "Elimina permisos"], "B", "Un contrato explicito mejora confiabilidad."),
        *_seccion_6(),
        pregunta(5, "Parquet", "Parquet es columnar y Delta agrega log transaccional.", "Que afirmacion es correcta?", ["Parquet y Delta son identicos", "Delta usa Parquet mas transaction log", "CSV siempre es mas eficiente", "Delta solo sirve para imagenes"], "B", "Delta agrega ACID, historial y MERGE sobre datos Parquet."),
        *_seccion_7(),
        pregunta(6, "Lazy evaluation", "Spark no ejecuta transformaciones hasta una accion.", "Cual es una accion?", ["filter", "select", "withColumn", "count"], "D", "`count` dispara ejecucion."),
        *_seccion_8(),
        pregunta(7, "Photon", "Photon acelera consultas compatibles sin cambiar codigo.", "Donde se verifica el rendimiento?", ["Query Profile", "Nombre del archivo", "Ruta C:/Users", "Markdown"], "A", "Query Profile muestra detalles de ejecucion."),
        *_seccion_9(),
        pregunta(8, "Funciones", "Las funciones nativas son optimizables.", "Que conviene preferir?", ["UDF Python siempre", "Funciones nativas de PySpark", "collect y for", "Pandas para todo"], "B", "Las funciones nativas permanecen dentro del motor Spark."),
        *_seccion_10(),
        *_seccion_11(),
        pregunta(9, "Spark vs Pandas", "Pandas es excelente si todo cabe en RAM.", "Cuando suele ganar Spark?", ["Datos grandes y pipelines reproducibles", "Cinco filas locales", "Editar a mano", "Sin SQL ni crecimiento"], "A", "Spark gana por escala, SQL distribuido y operacion."),
        *_seccion_12(),
        pregunta(10, "Spark vs Dask", "Dask escala Python; Spark optimiza planes SQL/DataFrame.", "Que ventaja es clara de Spark?", ["Catalyst y SQL distribuido", "Editar Excel", "No usar tablas", "Solo numpy local"], "A", "Catalyst optimiza consultas antes de ejecutarlas."),
        *_seccion_13(),
        pregunta(11, "Delta Lake", "Delta tiene transaction log.", "Que habilita?", ["MERGE, time travel y ACID", "Leer disco local C:", "Eliminar schemas", "Evitar todos los jobs"], "A", "El log permite control transaccional e historial."),
        *_seccion_14(),
        *_seccion_15(),
        pregunta(12, "Workflows", "Un Job operacionaliza un notebook.", "Que pregunta resume la sesion?", ["Como traigo todo al driver?", "Donde vive el dato, que plan ejecuta Spark y como lo opero?", "Como evito tablas?", "Como reemplazo Spark con for loops?"], "B", "La mentalidad correcta conecta datos, motor, tablas y operacion."),
        *_seccion_16(),
    ]
    return cells


if __name__ == "__main__":
    cells = build_cells()
    validate(cells)
    save(cells, "Cuadernos/9_Databricks_Serverless_Completo.ipynb")
