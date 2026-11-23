# S13 · De una máquina a un clúster (un solo cuaderno)

**Recursos del estudiante:** [presentación interactiva](../../Presentaciones/s13-de-una-maquina-a-un-cluster.html#s1) y [único cuaderno ejecutable](../../Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb). No es necesario ejecutar aplicaciones Streamlit, copiar scripts ni crear notebooks nuevos.

## Acceso directo para estudiantes — rama exclusiva de S13

[**Crear Codespace S13**](https://codespaces.new/jazaineam1/BigData2026/tree/s13-laboratorio) · [**Cuaderno en la rama del estudiante**](https://github.com/jazaineam1/BigData2026/blob/s13-laboratorio/Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb)

1. Abre el enlace y comprueba la rama **`s13-laboratorio`**. Esta rama dispone de **un único perfil predeterminado: S13 · Un solo cuaderno de Dask**; no debes elegir Airflow.
2. Selecciona **2 núcleos** si están disponibles, crea el Codespace y espera a ver **`LISTO PARA S13`**.
3. Abre el cuaderno `Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb` con **Python 3.11** y ejecútalo en orden. El reto de decisión final se completa con los resultados propios.

Los nueve CSV SECOP, incluidos tres fragmentos grandes (unos 300.000 registros en total), siguen disponibles. **El cuaderno conserva 55 celdas y sus 22 celdas de código intactas**; únicamente se actualizaron los textos de inicio. En el Explorador las carpetas técnicas se ocultan visualmente.

La configuración manual de perfiles descrita abajo solo aplica a quienes trabajan directamente sobre la rama docente `main`. **Para estudiantes utiliza el enlace de arriba.**

## Configuración docente alternativa en main

1. En el repositorio selecciona **Code → Codespaces → New with options**.
2. Elige el perfil **S13 · Dask, MapReduce y modelos SECOP**.
3. Al crearse, el entorno instala automáticamente las dependencias y hace una comprobación ligera de un worker Dask y las importaciones de K-means. No entrena modelos grandes.
4. Abre `Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb`, selecciona Python y ejecuta sus celdas **en orden**.

## Qué aprenderás

**Clúster de cómputo:** scheduler + workers + recursos. `LocalCluster` mantiene los workers en la misma VM; sus procesos comparten CPU y RAM. En un clúster multinodo cada máquina aporta sus recursos y se comunican por red. Un «clúster» de K-means significa un grupo de datos, no máquinas.

**Dos prácticas:** SECOP real para particiones, MapReduce, Parquet y tareas Dask; puntos numéricos **simulados** para K-means clásico local y distribuido.

**Una sola comparación:** mismos datos y centroides iniciales para scikit-learn y Dask-ML. Se registran `fit` y predicción local, arranque de Dask, persistencia, `fit` y predicción Dask, trabajadores que ejecutaron tareas y acuerdo de grupos. No se promete que Dask gane.

## Memoria: tres números que no debes mezclar

- **Matriz numérica:** `filas × variables × bytes del dato`. Para 20.000 × 20 `float64` = **3,2 MB**.
- **Centroides:** `grupos × variables × bytes`. Para 4 × 20 `float64` = **640 bytes**; no incluye el resto del estimador.
- **RAM durante entrenamiento:** Python, datos, copias, resultados temporales y workers. Se toman muestras de **RSS por proceso** con psutil. El máximo observado puede subestimar un pico entre muestras, y sumar RSS de procesos puede contar memoria compartida varias veces.

Las limitaciones de memoria por worker que informa Dask son límites lógicos, no RAM nueva. Los valores de 60, 70, 80 y 95 % corresponden a decisiones de gestión de memoria, no al tamaño del modelo.

## Parámetros del mismo cuaderno

| Parámetro | Valor inicial | Ampliación deliberada |
|---|---:|---:|
| `REGISTROS` | 1.000 | 20.000 |
| `VARIABLES` | 2 | 20 |
| `GRUPOS` | 4 | Dejar 4 para comparar |
| `WORKERS_MODELO` | hasta 2, según CPU efectiva | No exceder los recursos disponibles |

Con dos variables se ven la asignación de puntos, una actualización de centroides y los grupos finales. En 20 dimensiones no se presentan gráficos 2D como si representaran fielmente el problema.

No ejecutar benchmarks de 50.000 registros ni entrenamientos grandes en GitHub Actions. El flujo automático de PR es estático/visual; la prueba de ejecución completa del cuaderno solo existe como ejecución manual explícita.

**Referencias:** [Dask Distributed](https://distributed.dask.org/) · [Worker Memory](https://distributed.dask.org/en/stable/worker-memory.html) · [Dask-ML KMeans](https://ml.dask.org/modules/generated/dask_ml.cluster.KMeans.html).
