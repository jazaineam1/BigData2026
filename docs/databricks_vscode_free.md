# Conexion VS Code con Databricks Free Edition

Este repositorio incluye una copia del cuaderno SECOP pensada para revisarse desde VS Code:

`Cuadernos/11_Spark_SECOP_Solucion_Taller_VSCode_Connect.ipynb`

La ejecucion completa del cuaderno sigue siendo mas estable dentro de Databricks, porque usa Volumes, `dbutils`, `displayHTML`, Query Profile y Jobs. Desde VS Code conviene probar piezas Spark pequenas con Databricks Connect.

## Flujo recomendado

1. Instala la extension oficial **Databricks** en VS Code.
2. Abre este repositorio como carpeta de trabajo.
3. Copia `databricks.yml.example` como `databricks.yml` y cambia el host por la URL real del workspace.
4. En la extension de Databricks, convierte o configura el proyecto.
5. Autentica el workspace con OAuth o con un perfil de Databricks CLI.
6. Selecciona **Serverless** como compute. En Free Edition solo esta disponible serverless.
7. Activa Databricks Connect desde la extension.
8. Copia `databricks.env.example` como `databricks.env` si necesitas variables locales.
9. Ejecuta `scripts/databricks_vscode_smoke_test.py` desde la configuracion de depuracion:
   `Databricks Connect: smoke test SECOP`.

## Autenticacion

Opcion recomendada: OAuth desde la extension de Databricks para VS Code.

Si usas Databricks CLI, el flujo general es:

```powershell
databricks auth login --host https://<tu-workspace>.cloud.databricks.com
```

Luego seleccionas ese perfil desde la extension.

## Que se puede probar desde VS Code

- Consultas sobre tablas ya creadas en Databricks.
- Transformaciones con Spark DataFrames.
- Agregaciones, ventanas y `explain()`.
- Pruebas pequenas sobre `workspace.default.secop_base_analitica`.

## Que conviene ejecutar dentro de Databricks

- Descarga de archivos hacia Volumes.
- Celdas con `dbutils`.
- Celdas con `displayHTML`.
- Creacion y revision visual de Query Profile.
- Ejecucion completa del notebook como Job.

## Smoke test

El archivo `scripts/databricks_vscode_smoke_test.py` valida:

- Version de Spark remoto.
- Catalogo y schema visibles.
- Existencia de tablas SECOP.
- Lectura de `workspace.default.secop_base_analitica`.
- Agregacion por departamento.
- Lectura del plan con `explain()`.

Si falla porque no existe la tabla, primero ejecuta el cuaderno principal dentro de Databricks hasta crear:

`workspace.default.secop_base_analitica`

## Nota sobre MCP

MCP no es el camino principal para ejecutar Spark en este caso. La ruta mas directa es:

VS Code -> Extension oficial Databricks -> Databricks Connect -> Serverless remoto

MCP puede servir para asistentes o herramientas de observabilidad, pero no reemplaza Databricks Connect para probar DataFrames Spark.
