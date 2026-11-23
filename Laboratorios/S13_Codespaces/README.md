# Sesión 13 · Dask con un solo cuaderno

**Material para los estudiantes:**
- [Presentación S13](../../Presentaciones/s13-de-una-maquina-a-un-cluster.html#s1): conceptos y decisiones.
- [Cuaderno S13](../../Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb): **todas las ejecuciones del laboratorio**, incluido K-means local y distribuido.

La sesión usa dos ejemplos claramente diferenciados: **registros SECOP reales** para demostrar MapReduce, pandas/Dask y tareas con workers; y **puntos numéricos simulados** para explicar K-means, un modelo clásico de agrupamiento. No hay que crear ni ejecutar un archivo Python adicional para el modelo.

## Abrir el entorno

1. En GitHub: **Code → Codespaces → ... → New with options**.
2. Elige **S13 · Dask, MapReduce y modelos SECOP**; no el perfil predeterminado.
3. Abre `Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb` y selecciona el kernel Python.
4. Ejecuta las celdas en orden. La instalación del Codespace incluye Dask, Dask-ML y scikit-learn.

Puedes verificar el entorno desde la terminal con `nproc`, `free -h` y `python Laboratorios/S13_Codespaces/verificar_entorno.py`. Esto **no constituye un recurso adicional de estudio**.

## Modelos y tamaños

**K-means** agrupa puntos por cercanía a centroides; `sklearn.cluster.KMeans` lo entrena localmente y `dask_ml.cluster.KMeans` distribuye el ajuste de **un único modelo**. El cuaderno permite modificar:

| Variable | Prueba inicial | Ampliación voluntaria |
|---|---:|---:|
| `REGISTROS` | 1.000 | 20.000 |
| `VARIABLES` | 2 | 20 |
| `WORKERS_MODELO` | 2 | Según CPU y memoria disponibles |

Una matriz `float64` de 20.000 × 20 contiene 400.000 números y ocupa ~3,2 MB **solo en valores**. No significa automáticamente que distribuir sea necesario. En el cuaderno se contrastan tiempos de entrenamiento, arranque del clúster, persistencia y resultados.

Las demás herramientas se **explican, pero no se ejecutan como ejercicios adicionales**: regresiones distribuidas y XGBoost tienen bibliotecas compatibles; ejecutar validaciones independientes no equivale a distribuir un único ajuste; DBSCAN estándar no se convierte en distribuido usando Dask.

## Alcance y recursos

- Se mantienen las demostraciones ligeras de los ocho lotes SECOP y su comparación con ejecución secuencial. La espera externa del ejemplo es **simulada**; el reparto de Dask es real.
- Los puntos de K-means son **simulados con semilla fija**, no etiquetas o predicciones sobre contratación pública.
- No repetir 50.000 registros, OCR, modelos neuronales ni entrenamientos costosos en GitHub Actions. Las pruebas automáticas se limitan a sintaxis, estructura y visualización.
- Dos workers dentro del Codespace no son dos computadores; más workers no crean capacidad física adicional.
- No se promete una aceleración. Si Dask tarda más, se explican los costos de coordinación.
- El resultado de SECOP se exporta a Parquet y puede reutilizarse en S14/PySpark. Los datos simulados de K-means no se hacen pasar por SECOP.

**Fuentes:** [Dask](https://docs.dask.org/), [Dask-ML K-means](https://ml.dask.org/modules/generated/dask_ml.cluster.KMeans.html), [scikit-learn](https://scikit-learn.org/stable/modules/clustering.html).
