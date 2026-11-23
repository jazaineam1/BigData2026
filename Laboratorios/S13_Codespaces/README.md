# S13 · De una máquina a un clúster (un solo cuaderno)

**Recursos del estudiante:** [presentación interactiva](../../Presentaciones/s13-de-una-maquina-a-un-cluster.html#s1) y [único cuaderno ejecutable](../../Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb). No es necesario ejecutar aplicaciones Streamlit, copiar scripts ni crear notebooks nuevos.

## Abrir Codespaces: enlace, perfil exacto y verificación

**Entrada de GitHub:** [Crear Codespace desde `main`](https://codespaces.new/jazaineam1/BigData2026/tree/main). **Este enlace NO garantiza que quede seleccionado el perfil S13**: hay que elegirlo manualmente antes de crear.

1. Inicia sesión en [BigData2026](https://github.com/jazaineam1/BigData2026), rama **`main`**.
2. Entra a **Code → Codespaces → ⋯ → New with options**. Si abriste el enlace de creación, revisa allí **Dev container configuration** antes de confirmar.
3. Selecciona **`S13 · Dask, MapReduce y modelos SECOP`** (archivo [`.devcontainer/s13-distribuido/devcontainer.json`](../../.devcontainer/s13-distribuido/devcontainer.json)). **NO `Airflow Lab`** (es el perfil predeterminado).
4. **Machine type:** 2 núcleos si está disponible, suficiente para la práctica inicial; 4 opcionales con mayor uso de cuota. **Branch:** `main`.
5. Pulsa **Create codespace** y espera a que finalice `postCreateCommand`: instala `requirements.txt` y ejecuta `verificar_entorno.py`.
6. Abre **Terminal → New Terminal**, desde `/workspaces/BigData2026`, y ejecuta:

   ```bash
   pwd
   python --version
   nproc
   free -h
   python Laboratorios/S13_Codespaces/verificar_entorno.py
   ```

7. La última línea del verificador debe ser **`LISTO PARA S13`**. Si falla, primero comprueba perfil, rama y error de instalación. Solo ante una dependencia ausente, en la terminal del Codespace ejecuta `python -m pip install -r Laboratorios/S13_Codespaces/requirements.txt`.
8. Desde el **Explorador de VS Code web**, abre **`Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb`**, no desde terminal ni solo en el navegador github.com. En la esquina superior derecha usa **Select Kernel → Python Environments → Python 3.11** (o el Python 3.11 del Codespace). Ejecuta las celdas en orden.

**Si ya tenías un Codespace con el perfil Airflow:** comprueba su configuración antes de reutilizarlo. Instalar Dask con `pip` no cambia la configuración predeterminada de Airflow; crea un Codespace S13 cuando sea necesario. No necesitas Ollama, Streamlit ni otro cuaderno.

**Enlaces útiles:** [presentación S13](../../Presentaciones/s13-de-una-maquina-a-un-cluster.html#s1) · [único cuaderno](../../Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb) · [configuración exacta](../../.devcontainer/s13-distribuido/devcontainer.json) · [documentación oficial de creación y perfiles de Codespaces](https://docs.github.com/en/codespaces/developing-in-a-codespace/creating-a-codespace-for-a-repository).


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
