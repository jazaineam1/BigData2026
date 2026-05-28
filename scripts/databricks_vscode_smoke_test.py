"""
Smoke test para VS Code + Databricks Connect.

Este archivo se ejecuta desde VS Code. Python corre localmente, pero las
operaciones Spark deben ejecutarse en el compute remoto de Databricks.

Antes de ejecutarlo:
1. Instala/configura la extension oficial de Databricks para VS Code.
2. Autentica el workspace con OAuth o con un perfil de Databricks CLI.
3. Selecciona Serverless como compute en la extension.
4. Activa Databricks Connect desde la extension.
"""

from databricks.connect import DatabricksSession
from pyspark.sql import functions as F


CATALOG = "workspace"
SCHEMA = "default"
VOLUME = "tallerspark"

RAW_CSV_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}/secop/raw_csv/"
PARQUET_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}/secop/parquet/"
TABLA_ANALITICA = f"{CATALOG}.{SCHEMA}.secop_base_analitica"


spark = DatabricksSession.builder.getOrCreate()

print("Spark remoto:", spark.version)
print("Catalogo actual:", spark.sql("SELECT current_catalog()").first()[0])
print("Schema actual:", spark.sql("SELECT current_schema()").first()[0])

print("\nTablas SECOP visibles en workspace.default:")
spark.sql(f"SHOW TABLES IN {CATALOG}.{SCHEMA} LIKE 'secop*'").show(truncate=False)

print("\nPrueba de tabla analitica:")
df = spark.table(TABLA_ANALITICA)
df.select("departamento_norm", "valor_contrato", "anio").show(5, truncate=False)

print("\nTop departamentos por valor:")
(
    df
    .filter(F.col("valor_contrato").isNotNull() & (F.col("valor_contrato") > 0))
    .groupBy("departamento_norm")
    .agg(F.sum("valor_contrato").alias("valor_total"))
    .orderBy(F.desc("valor_total"))
    .limit(10)
    .show(truncate=False)
)

print("\nPlan fisico de una consulta pequena:")
(
    df
    .select("departamento_norm", "valor_contrato")
    .filter(F.col("valor_contrato") > 0)
    .groupBy("departamento_norm")
    .agg(F.sum("valor_contrato").alias("valor_total"))
    .orderBy(F.desc("valor_total"))
    .limit(10)
    .explain()
)
