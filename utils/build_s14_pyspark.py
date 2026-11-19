# -*- coding: utf-8 -*-
"""Generador de S14. Verificación plataforma Free Edition: 2026-11-19.
Uso: python utils/build_s14_pyspark.py [--check]
No ejecuta Spark ni descarga datos pesados.
"""
import json
import sys
from pathlib import Path
from make_notebook import md, code, build, save, validate

BLOQUES = [
  [
    "markdown",
    "# S14 · ¿Cómo pasa Laura de Dask a Spark y Databricks?\n**Universidad Central · Maestría en Analítica de Datos · Big Data 2026-2S**\n\n[Presentación interactiva y tutorial](../Presentaciones/s14-de-dask-a-spark.html#s1) | [Abrir en Google Colab](https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/14_PySpark_Compras_Claras.ipynb)\n\n**Caso transversal:** Compras Claras debe consolidar resultados de 30 ventanas de extracción SECOP. Usaremos **datos agregados reales**, no contratos individuales, y construiremos una misma consulta en PySpark y Spark SQL.\n\n**Producto:** expediente JSON con fuente, parámetros, resultado contrastado y límite de interpretación. **Ruta principal:** Colab con Spark local; **ruta alternativa:** Databricks Free Edition con serverless. Sin claves ni tarjeta de crédito exigidas por esta práctica."
  ],
  [
    "markdown",
    "## Ruta de aprendizaje y resultado esperado\n1. Entender cuándo usar pandas, Dask, Spark y Databricks, sin suponer que Spark siempre gana.\n2. Crear un DataFrame con esquema explícito y detectar la **acción** que ejecuta el plan.\n3. Ver particiones, agregación, shuffle y planes con `explain()`.\n4. Calcular cobertura ponderada mediante API PySpark y SQL; validar contra Python puro.\n5. Abrir el mismo notebook en Databricks si hay acceso y ubicar cómputo, catálogo y perfil de consulta.\n6. Guardar evidencia con fuente y límites.\n\n**El reloj y el libreto son del docente, no de este cuaderno.** El tutorial paso a paso está integrado en la presentación: sigue ese orden y ejecuta estas celdas."
  ],
  [
    "markdown",
    "## 1 · Del problema a la herramienta\n**pandas:** opera principalmente en la memoria de un proceso; es suficiente si el dato cabe. **Dask:** programa tareas paralelas y flujos similares a pandas. **Apache Spark:** motor con DataFrame API, Spark SQL y planificación distribuida. **Databricks:** plataforma gestionada que ejecuta Spark y añade herramientas de datos, gobernanza y automatización.\n\nEn un despliegue distribuido Spark separa **driver** (coordina), **executors** (procesan) y **particiones** (porciones lógicas del dato). Un **job** nace de una acción; un **stage** agrupa tareas; una **task** procesa una partición. **Shuffle** es el intercambio de filas entre particiones, típico al agrupar o unir por claves.\n\n**No confundir:** usar `local[2]` en Colab NO significa dos servidores. Una partición no equivale a un worker. En Databricks serverless parte de la infraestructura está administrada y no siempre se expone la Spark UI clásica."
  ],
  [
    "markdown",
    "## 2 · Preparar el motor sin instalar clústeres\n**HAZ ESTO AHORA.** Colab: abre el cuaderno, ejecuta la celda, espera la instalación inicial si PySpark no existe. Databricks: importa el notebook y selecciona Serverless; no ejecutes comandos de instalación de un clúster clásico. La siguiente celda detecta el entorno y reutiliza el objeto `spark` si ya existe.\n\n**Límite de la plataforma:** Databricks Free Edition es serverless, tiene cuotas y restringe conexiones a internet. Guía oficial comprobada el 19-nov-2026: https://docs.databricks.com/aws/en/getting-started/free-edition-limitations"
  ],
  [
    "code",
    "# 1 · Verificar el entorno y crear una SparkSession de forma repetible\nimport importlib.util, subprocess, sys, platform\nif importlib.util.find_spec(\"pyspark\") is None:\n    subprocess.check_call([sys.executable, \"-m\", \"pip\", \"install\", \"-q\", \"pyspark==4.0.1\"])\nfrom pyspark.sql import SparkSession, functions as F, types as T\nif \"spark\" not in globals():\n    spark = SparkSession.builder.master(\"local[2]\").appName(\"UC_S14_SECOP\").getOrCreate()\n    spark.sparkContext.setLogLevel(\"ERROR\")\n    ENTORNO = \"Colab / Spark local\"\nelse:\n    ENTORNO = \"Spark preexistente / Databricks\"\nprint(\"Entorno:\", ENTORNO, \"| Spark:\", spark.version, \"| Python:\", platform.python_version())"
  ],
  [
    "markdown",
    "**Cómo se lee:** `ENTORNO` y `spark.version` indican el motor disponible. **Qué nos dice:** la API PySpark puede ejecutarse. **Qué NO permite concluir todavía:** que existan varios computadores ni cuál es la velocidad de un clúster. **Qué error común:** llamar distribuido a un modo local por tener dos hilos. Si aparece un error de Java en Colab, reinicia el runtime y ejecuta desde el inicio; si falla la cuota de Databricks, sigue por Colab."
  ],
  [
    "markdown",
    "## 3 · Datos públicos, transformaciones trazables\nFuente: `Datos/tc1_ventanas_resumen.json` (generado por `utils/tc1_data_gates.py` el 2026-10-02T06:22:55+00:00), a partir de SECOP II Procesos (`p6dx-8zbt`) y Contratos (`jbjy-vk9h`) de datos.gov.co. La selección original usa hasta 3.000 procesos y 4.000 contratos por ventana mensual con criterios explícitos: **no es un censo nacional**.\n\nUsamos 30 ventanas con cinco campos: `mes`, `procesos_unicos`, `emparejados`, `cobertura`, `departamento_particion`. Los 30 registros quedan incorporados en el notebook para **evitar 30 descargas simultáneas a Socrata**.\n\n**Lectura manual:** la ventana 2024-01 tiene 3.000 procesos únicos y 201 emparejamientos: `201/3000=0.067` (6,7 %). Esta razón se refiere únicamente al recorte registrado; no demuestra irregularidades de contratación."
  ],
  [
    "code",
    "# 2 · Snapshot offline derivado del manifiesto real; no hay consultas a la API\nFILAS = [[\"2024-01\",3000,201,0.067,\"Cauca\"],[\"2024-02\",2945,120,0.0407,\"Distrito Capital de Bogotá\"],[\"2024-03\",2872,188,0.0655,\"Tolima\"],[\"2024-04\",2874,130,0.0452,\"Distrito Capital de Bogotá\"],[\"2024-05\",2858,275,0.0962,\"Bolívar\"],[\"2024-06\",2920,86,0.0295,\"Distrito Capital de Bogotá\"],[\"2024-07\",2910,69,0.0237,\"Antioquia\"],[\"2024-08\",2900,231,0.0797,\"Boyacá\"],[\"2024-09\",2932,88,0.03,\"Distrito Capital de Bogotá\"],[\"2024-10\",2924,148,0.0506,\"Distrito Capital de Bogotá\"],[\"2024-11\",2967,310,0.1045,\"Distrito Capital de Bogotá\"],[\"2024-12\",2946,169,0.0574,\"Distrito Capital de Bogotá\"],[\"2025-01\",2990,204,0.0682,\"Cauca\"],[\"2025-02\",2984,84,0.0282,\"Antioquia\"],[\"2025-03\",2971,132,0.0444,\"Chocó\"],[\"2025-04\",2934,147,0.0501,\"Antioquia\"],[\"2025-05\",2952,101,0.0342,\"Distrito Capital de Bogotá\"],[\"2025-06\",2915,120,0.0412,\"Antioquia\"],[\"2025-07\",2946,113,0.0384,\"Antioquia\"],[\"2025-08\",2872,118,0.0411,\"Antioquia\"],[\"2025-09\",2902,171,0.0589,\"Distrito Capital de Bogotá\"],[\"2025-10\",2805,131,0.0467,\"Distrito Capital de Bogotá\"],[\"2025-11\",2981,138,0.0463,\"Distrito Capital de Bogotá\"],[\"2025-12\",2879,90,0.0313,\"Distrito Capital de Bogotá\"],[\"2026-01\",2999,282,0.094,\"Boyacá\"],[\"2026-02\",2992,70,0.0234,\"Distrito Capital de Bogotá\"],[\"2026-03\",2902,243,0.0837,\"Norte de Santander\"],[\"2026-04\",2802,100,0.0357,\"Distrito Capital de Bogotá\"],[\"2026-05\",2922,85,0.0291,\"Distrito Capital de Bogotá\"],[\"2026-06\",2766,201,0.0727,\"Norte de Santander\"]]\nPROCEDENCIA = {\"fuente\":\"SECOP II p6dx-8zbt y jbjy-vk9h\", \"archivo\":\"Datos/tc1_ventanas_resumen.json\", \"generado_utc\":\"2026-10-02T06:22:55+00:00\", \"script\":\"utils/tc1_data_gates.py\", \"grano\":\"ventana de extracción, no contrato\"}\nassert len(FILAS) == 30\nassert FILAS[0][:3] == [\"2024-01\", 3000, 201]\nprint(\"Ventanas:\", len(FILAS), \"| Primer registro:\", FILAS[0])"
  ],
  [
    "markdown",
    "## 4 · Tipos: no dejemos que Spark adivine el significado\nUna columna llamada `mes` contiene claves `YYYY-MM`, no fechas de contratos; `cobertura` es un número entre 0 y 1, no un valor monetario. Crear el **schema** evita inferencias accidentales.\n\n**Mini ficha `spark.createDataFrame(data, schema=...)`:** entrada: filas y tipos; salida: DataFrame. `printSchema()` muestra los tipos; `show(n)` materializa una vista de n filas. Error típico: dar por hecho que `show(5)` ha explorado toda la fuente."
  ],
  [
    "code",
    "# 3 · Esquema estricto y primera acción\nschema = T.StructType([\n    T.StructField(\"mes\", T.StringType(), False),\n    T.StructField(\"procesos_unicos\", T.LongType(), False),\n    T.StructField(\"emparejados\", T.LongType(), False),\n    T.StructField(\"cobertura\", T.DoubleType(), False),\n    T.StructField(\"departamento_particion\", T.StringType(), True)\n])\ndf = spark.createDataFrame([tuple(f) for f in FILAS], schema=schema)\ndf.printSchema()\ndf.orderBy(\"mes\").show(5, truncate=False)\nassert df.count() == 30"
  ],
  [
    "markdown",
    "**Cómo se lee:** se ven tipos y cinco primeras ventanas ordenadas. **Qué nos dice:** hay 30 ventanas con campos definidos. **Qué NO permite concluir todavía:** que la extracción original cubrió la totalidad de SECOP o que la cobertura corresponde al valor del gasto. **Qué error común:** interpretar la columna de departamento como la ubicación de todos los contratos de la ventana; es una partición de control del manifiesto."
  ],
  [
    "markdown",
    "## 5 · Transformaciones frente a acciones\n`filter`, `select` y `withColumn` normalmente construyen un **plan diferido** (*lazy*). `count`, `show` y escribir resultados activan un trabajo. El optimizador **Catalyst** utiliza el plan para elegir operaciones. Que el código tenga menos líneas no significa que vaya a ejecutarse más rápido.\n\n**Mini fichas:** `filter(condición)` conserva filas; `withColumn(nombre, expresión)` deriva un campo; `count()` devuelve un entero tras ejecutar. Error común: medir solo el tiempo de construir el DataFrame y compararlo con una acción de otro motor."
  ],
  [
    "code",
    "# 4 · Define un plan y ejecuta dos acciones explícitas\nplan = df.filter(F.col(\"procesos_unicos\") >= 2800).withColumn(\"anio\", F.substring(\"mes\", 1, 4))\nprint(\"PLAN construido; columnas:\", plan.columns)\nprint(\"ACCIÓN count:\", plan.count())\nplan.select(\"anio\", \"mes\", \"cobertura\").orderBy(\"mes\").show(6, truncate=False)"
  ],
  [
    "markdown",
    "**Cómo se lee:** `count` representa ventanas que cumplieron el criterio. **Qué nos dice:** cambia el universo a partir del filtro. **Qué NO permite concluir todavía:** qué porcentaje del país quedó representado. **Qué error común:** confundir el umbral de procesos únicos (2.800) con el umbral de cobertura."
  ],
  [
    "markdown",
    "## 6 · No promediar porcentajes sin revisar el denominador\nSi una ventana tiene `10/100=10 %` y otra `9/10=90 %`, el promedio simple de porcentajes es 50 %, pero la cobertura combinada es `(10+9)/(100+10)=17,27 %`. Para comparar años de la misma selección, calculamos **SUM(emparejados) / SUM(procesos_unicos)** y conservamos el número de ventanas.\n\n**Mini ficha `groupBy().agg()`:** agrupa claves; recibe agregaciones (sum/count); devuelve un nuevo plan que puede requerir shuffle. **Error común:** calcular `avg(cobertura)` y presentarlo como cobertura global."
  ],
  [
    "code",
    "# 5 · Agregado anual ponderado: la medida tiene un denominador explícito\nresumen = (df.withColumn(\"anio\", F.substring(\"mes\", 1, 4))\n    .groupBy(\"anio\")\n    .agg(F.count(\"*\").alias(\"ventanas\"),\n         F.sum(\"procesos_unicos\").alias(\"procesos_unicos\"),\n         F.sum(\"emparejados\").alias(\"emparejados\"))\n    .withColumn(\"cobertura_ponderada\", F.col(\"emparejados\") / F.col(\"procesos_unicos\"))\n    .orderBy(\"anio\"))\nresumen.show(truncate=False)\nassert resumen.agg(F.sum(\"ventanas\")).first()[0] == 30"
  ],
  [
    "markdown",
    "**Cómo se lee:** cada fila es un año; `ventanas` revela que la cobertura temporal de los años puede ser desigual. **Qué nos dice:** razón de emparejamiento de los registros seleccionados. **Qué NO permite concluir todavía:** que 2026 sea comparable con un año completo, o que existan hechos causales. **Qué error común:** comparar años con cantidades distintas de ventanas sin observar el denominador."
  ],
  [
    "markdown",
    "## 7 · Spark SQL: dos sintaxis, mismo motor\nUna **vista temporal** es un nombre consultable hasta que termine la sesión, no una tabla persistida. `spark.sql(query)` construye un DataFrame y puede ejecutar las mismas operaciones que PySpark. Validaremos el resultado con un **assert**; no basta mirar tablas parecidas.\n\n**Mini fichas:** `createOrReplaceTempView(nombre)` registra una vista temporal; `spark.sql(SQL)` devuelve un DataFrame. Error: creer que SQL no requiere shuffle."
  ],
  [
    "code",
    "# 6 · Equivalencia explícita PySpark ↔ Spark SQL\ndf.createOrReplaceTempView(\"s14_ventanas\")\nsql = spark.sql('''\nSELECT SUBSTRING(mes,1,4) anio, COUNT(*) ventanas,\nSUM(procesos_unicos) procesos_unicos, SUM(emparejados) emparejados,\nSUM(emparejados)/SUM(procesos_unicos) cobertura_ponderada\nFROM s14_ventanas GROUP BY SUBSTRING(mes,1,4) ORDER BY anio\n''')\na = [(r.anio,int(r.ventanas),round(float(r.cobertura_ponderada),9)) for r in resumen.collect()]\nb = [(r.anio,int(r.ventanas),round(float(r.cobertura_ponderada),9)) for r in sql.collect()]\nassert a == b, (a,b)\nprint(\"Paridad PySpark/SQL: OK\", a)"
  ],
  [
    "markdown",
    "**Cómo se lee:** el mensaje OK comprueba año, número de ventanas y razón con nueve decimales. **Qué nos dice:** API y SQL representan el mismo cálculo sobre este snapshot. **Qué NO permite concluir todavía:** latencia idéntica, ni calidad del dato nacional. **Qué error común:** usar `collect()` sobre millones de filas; aquí se limita a tres filas anuales."
  ],
  [
    "markdown",
    "## 8 · Shuffle, particiones y plan de ejecución\nUn **shuffle** mueve registros para que las mismas claves se combinen. El plan de `groupBy` puede incluir `Exchange`, mientras un filtro sencillo normalmente no requiere el mismo intercambio. `explain(mode=\"formatted\")` expone el **plan físico**, que no sustituye un Query Profile real.\n\n**Mini ficha `repartition(n, columna)`:** redistribuye registros, normalmente con un intercambio. No crea nuevos servidores. **Error común:** creer que `repartition(1)` siempre optimiza."
  ],
  [
    "code",
    "# 7 · Ver planes con señales de redistribución\nprint(\"FILTRO:\")\ndf.filter(F.col(\"emparejados\") > 100).explain(mode=\"formatted\")\nprint(\"\\nAGRUPACIÓN:\")\nresumen.explain(mode=\"formatted\")\nprint(\"Busca Exchange y Aggregate; su forma exacta depende de la versión.\")"
  ],
  [
    "code",
    "# 8 · Ver particiones sin usar API RDD (compatible con serverless)\nbase = spark.range(0, 40, 1, 4)\nprint(\"ANTES:\")\nbase.withColumn(\"p\", F.spark_partition_id()).groupBy(\"p\").count().orderBy(\"p\").show()\nredistribuido = base.repartition(2, (F.col(\"id\") % 3))\nprint(\"DESPUÉS:\")\nredistribuido.withColumn(\"p\", F.spark_partition_id()).groupBy(\"p\").count().orderBy(\"p\").show()\nassert redistribuido.count() == 40"
  ],
  [
    "markdown",
    "**Cómo se lee:** el reparto muestra filas por ID de partición y mantiene 40 registros. **Qué nos dice:** las particiones pueden cambiar con una redistribución. **Qué NO permite concluir todavía:** que se usaron dos servidores, que se redujo el tiempo o que el reparto sea uniformemente balanceado. **Qué error común:** llamar *workers* a las particiones."
  ],
  [
    "markdown",
    "## 9 · Control independiente: Spark no valida su propia respuesta\nUna prueba útil compara contra un cálculo simple en Python puro, sobre las mismas 30 filas. No instalamos Dask ni ejecutamos benchmarks costosos: **corrección primero, velocidad después**. El experimento es demasiado pequeño para demostrar que Spark es más rápido."
  ],
  [
    "code",
    "# 9 · Oráculo externo a Spark: Python puro\nfrom collections import defaultdict\ncontrol = defaultdict(lambda: [0,0,0])\nfor mes,unicos,emparejados,cobertura,departamento in FILAS:\n    item = control[mes[:4]]\n    item[0] += 1\n    item[1] += unicos\n    item[2] += emparejados\nreferencia = [(anio, v[0], round(v[2]/v[1],9)) for anio,v in sorted(control.items())]\nassert a == referencia, (a,referencia)\nprint(\"Paridad Spark/SQL/Python: OK\")"
  ],
  [
    "markdown",
    "**Cómo se lee:** el último OK significa que coinciden resultados anuales bajo la misma fórmula. **Qué nos dice:** es correcta esta implementación sobre el snapshot. **Qué NO permite concluir todavía:** que los datos originales sean exhaustivos o que Spark tenga ventaja de rendimiento. **Qué error común:** presentar tiempos de construir planes frente a tiempos de ejecutar acciones como comparación justa."
  ],
  [
    "markdown",
    "## 10 · Reto de transferencia: cambia una decisión\nElige un umbral entre 4 %, 7 % y 10 %: modifica **solo** `INDICE_UMBRAL` y ejecuta. Las filas representan ventanas cuya cobertura de emparejamiento dentro de la extracción supera el valor elegido. **No** se trata de una clasificación de fraude. La pregunta depende de tu propia ejecución, no de redactar una respuesta genérica."
  ],
  [
    "code",
    "# 10 · CAMBIA ESTE ÚNICO NÚMERO: 0, 1 o 2\nINDICE_UMBRAL = 1\nUMBRALES = (0.04, 0.07, 0.10)\nassert INDICE_UMBRAL in (0,1,2)\numbral = UMBRALES[INDICE_UMBRAL]\nelegidos = df.filter(F.col(\"cobertura\") >= umbral)\nprint(\"Umbral:\", umbral, \"| Ventanas:\", elegidos.count())\nelegidos.select(\"mes\",\"cobertura\").orderBy(\"mes\").show(8, truncate=False)"
  ],
  [
    "markdown",
    "**Cómo se lee:** el conteo cambia si cambias el umbral; `show(8)` presenta solo una vista. **Qué nos dice:** qué ventanas cumplen tu regla dentro del snapshot. **Qué NO permite concluir todavía:** que las ventanas sean más riesgosas; falta etiqueta o verificación independiente. **Qué error común:** usar un umbral sin documentarlo y comparar resultados de reglas distintas."
  ],
  [
    "markdown",
    "## 11 · Primer contacto con Databricks, sin repetir el laboratorio\n**Databricks** es una plataforma; **Spark** sigue siendo el motor. En Free Edition, el cómputo de notebooks es **serverless** y está sujeto a cuota. Sigue la guía embebida en la presentación para crear/entrar al workspace, importar este notebook, seleccionar Serverless y ejecutar las mismas celdas. **No pidas un clúster clásico, token de API ni tarjeta.**\n\nUbica **Workspace** (cuadernos), **Compute/Serverless** (ejecución), **Catalog** (gobierno de tablas y archivos) y **Query Profile** o detalles de ejecución (observabilidad). Un **Volume** almacena archivos; una **tabla Delta** añade un registro de transacciones; **Jobs** permiten programar tareas.\n\n**Puente S15:** a partir de este resultado construiremos Bronze → Silver → Gold, escribiremos una tabla Delta, controlaremos su historial y ejecutaremos un Job. No necesitas persistir datos compartidos en S14."
  ],
  [
    "markdown",
    "## 12 · Evidencia automática, decisiones cerradas\nEl siguiente expediente guarda la fórmula, los recuentos, el entorno y la procedencia. Elige un motor con un índice de `(pandas, Dask, Spark)` para un **escenario de producción hipotético que sí requiera procesamiento distribuido**. Esta decisión no altera los hechos: 30 filas no requieren Spark."
  ],
  [
    "code",
    "# 11 · Expediente verificable, sin credenciales ni archivos pesados\nimport json\nMOTORES = (\"pandas\",\"Dask\",\"Spark\")\nINDICE_MOTOR = 2  # 0/1/2: decisión cerrada para un escenario de crecimiento\nassert INDICE_MOTOR in (0,1,2)\nexpediente = {\n \"sesion\":14,\"fuente\":PROCEDENCIA,\"entorno\":ENTORNO,\"spark_version\":spark.version,\n \"filas\":len(FILAS),\"resultado\":[{\"anio\":x,\"ventanas\":n,\"cobertura\":c} for x,n,c in a],\n \"paridad\":{\"spark_sql\":a==b,\"python\":a==referencia},\n \"seleccion\":{\"umbral\":umbral,\"ventanas\":elegidos.count()},\n \"motor_escenario_futuro\":MOTORES[INDICE_MOTOR],\n \"limite\":\"30 ventanas de extracción, NO censo de contratos ni evidencia de fraude\"\n}\nassert all(expediente[\"paridad\"].values())\nprint(json.dumps(expediente,ensure_ascii=False,indent=2))"
  ],
  [
    "markdown",
    "**Cómo se lee:** verifica `fuente`, `filas`, `resultado`, `paridad`, `umbral` y `limite`. **Qué nos dice:** qué calculaste y bajo qué condiciones. **Qué NO permite concluir todavía:** escalabilidad, latencia o cobertura nacional. **Qué error común:** compartir solo el gráfico sin el denominador ni versión.\n\n**Autoevaluación formativa (no calificable):** (1) una partición es un servidor: **falso**; (2) `count()` es una acción: **verdadero**; (3) Spark SQL usa siempre otro motor: **falso**; (4) una tabla con 30 filas demuestra velocidad distribuida: **falso**; (5) Databricks Free Edition obliga a crear un cluster clásico: **falso**.\n\n**Referencias:** [PySpark DataFrames](https://spark.apache.org/docs/latest/api/python/user_guide/dataframes.html) · [Databricks Free Edition](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations)."
  ]
]
DESTINO = Path(__file__).resolve().parents[1] / "Cuadernos/14_PySpark_Compras_Claras.ipynb"

def main():
    cells = [md(t) if kind == "markdown" else code(t) for kind,t in BLOQUES]
    validate(cells)
    if "--check" in sys.argv:
        assert json.loads(DESTINO.read_text(encoding="utf-8")) == build(cells), "Cuaderno desincronizado con generador"
        print("S14: cuaderno sincronizado", len(cells), "celdas")
    else:
        save(cells, str(DESTINO))

if __name__ == "__main__":
    main()
