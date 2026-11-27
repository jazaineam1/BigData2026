"""Validación acotada S14A; no toca Databricks ni ejecuta escala grande."""
import ast,json,os,sys,shutil
from pathlib import Path
P=Path(__file__).resolve().parents[1]
nb=json.loads((P/"Cuadernos/14A_Databricks_E2E_Escala.ipynb").read_text())
cells=["".join(c["source"]) for c in nb["cells"] if c["cell_type"]=="code"]
assert len(cells)==9
for c in cells: ast.parse(c)
html=(P/"Presentaciones/s14a-databricks-escala.html").read_text()
assert all(f'id="a{i}"' in html for i in range(9))
assert "14A_Databricks_E2E_Escala.ipynb" in html and "14a" in (P/"index.html").read_text()
assert "25000000" in cells[0] and "CONFIRMAR_GRANDE" in cells[0]
assert sum(c.count(".toPandas()") for c in cells)==3
print("S14A: sintaxis 9 bloques y navegación OK",flush=True)
if "--spark" not in sys.argv: sys.exit(0)
from pyspark.sql import SparkSession
spark=SparkSession.builder.master("local[2]").appName("S14A-smoke").config("spark.ui.enabled","false").config("spark.sql.shuffle.partitions","4").config("spark.driver.memory","2g").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
env={"spark":spark,"LAB_TEST_LOCAL":True,"LAB_N":5000}
try:
    for i,c in enumerate(cells):
        print("BLOQUE",i,flush=True)
        exec(compile(c,f"<S14A A{i}>","exec"),env)
    assert env["n_bronze"]==5009 and env["n_silver"]==4995
    assert set(env["modelos"])=={"logistica","arbol"}
    assert env["resultado"]["filas"]==env["n_test"]
    assert env["formato"]=="parquet_local"
    assert all(0<=env["resultado"][k]<=1 for k in ("accuracy","f1_macro","auc"))
    print("SMOKE REAL Spark local:",json.dumps(env["expediente"],ensure_ascii=False),flush=True)
finally:
    spark.stop()
    if "carpeta_local" in env: shutil.rmtree(env["carpeta_local"],ignore_errors=True)
