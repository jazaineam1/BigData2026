# S13 · Código que el estudiante puede reutilizar

**Plataforma principal:** GitHub Codespaces con el perfil **S13 · Dask, MapReduce y modelos SECOP**.

No instalar software en el computador personal. Al elegir el Codespace con ese perfil se instalan las dependencias. El perfil raíz del repositorio pertenece a **Airflow**: en `Code → Codespaces → ... → New with options` se debe escoger **S13**, no el perfil predeterminado.

## Primeros pasos

1. Desde la [portada del curso](../../index.html) abre la presentación de S13 y sigue el tutorial embebido.
2. Crea el Codespace con la configuración `.devcontainer/s13-distribuido/devcontainer.json`.
3. Abre una terminal en VS Code web. Comprueba instalación con:

   ```bash
   python --version
   python -m pip show dask
   python -m pip show scikit-learn
   python Laboratorios/S13_Codespaces/verificar_entorno.py
   ```

4. Si falta un módulo, la instalación reproducible se realiza **dentro del Codespace**, no en el equipo:

   ```bash
   python -m pip install -r Laboratorios/S13_Codespaces/requirements.txt
   ```

5. Abre `Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb`, selecciona el kernel de Python del Codespace y ejecuta por secciones.

## Herramientas y demostración

- **Python / MapReduce conceptual:** funciones de sumar y contar; nada de Hadoop MapReduce instalado.
- **HDFS:** simulación de bloques y réplicas; no se afirma haber instalado HDFS.
- **pandas:** resultados de referencia de un archivo SECOP.
- **Dask DataFrame:** particionado y operaciones diferidas, comparación con pandas.
- **scikit-learn:** TF-IDF y regresión logística con división entrenamiento/prueba; la etiqueta es modalidad contractual, NO fraude.
- **Dask Distributed:** coordina tareas independientes y gestiona fallos; con bibliotecas compatibles (por ejemplo XGBoost-Dask) también puede distribuir un entrenamiento, aunque no siempre conviene por rendimiento.
- **Parquet:** resultado tabular que se reutilizará en S14/PySpark.

## Ejecutar sin abrir Jupyter

```bash
python Laboratorios/S13_Codespaces/analisis.py mapreduce
python Laboratorios/S13_Codespaces/analisis.py comparar
python Laboratorios/S13_Codespaces/analisis.py modelo
python Laboratorios/S13_Codespaces/analisis.py experimentos
python Laboratorios/S13_Codespaces/analisis.py fallo
python Laboratorios/S13_Codespaces/analisis.py exportar
```

Para ejecutar todo: `python Laboratorios/S13_Codespaces/analisis.py todo`.

**Ruta mínima recomendada:** `python Laboratorios/S13_Codespaces/dask_cuando_si.py --workers 2` (el programa está autocontenido en el perfil Codespaces S13).

## Pruebas

```bash
cd Laboratorios/S13_Codespaces
python -m unittest -v test_s13
```

El tablero Dask opcional usa el **puerto privado 8787** de Codespaces. Si no se abre, usa `client.scheduler_info()`: el resultado del laboratorio no depende de la interfaz gráfica. Los workers pueden ser procesos con uno o varios hilos; observa su configuración real mediante `client.scheduler_info()`. Permanecen dentro de una misma VM salvo que se conecten otros nodos.

## Transferencia a otros proyectos

El módulo `analisis.py` tiene funciones separadas para lectura, preparación, procesamiento, entrenamiento y exportación. Para adaptar el caso, cambia la ruta del CSV, `COL_TEXTO`, `COL_LABEL` y `CLASES` después de verificar nombres/valores reales. Usa siempre `train_test_split` ANTES de ajustar TF-IDF; nunca selecciones hiperparámetros usando el conjunto de prueba. Prueba cada cambio con una muestra pequeña.

Los archivos creados van a `Laboratorios/S13_Codespaces/salidas/`, excluida de Git. No subas datos personales ni credenciales al repositorio público. Cierra el Codespace al finalizar para ahorrar cuota.

## Fuente preparada y control de experimentos

Los CSV de SECOP que usa el curso están versionados y se suministran preparados para el laboratorio de procesamiento. La validación integral de fuente, etiquetas administrativas y modelos es responsabilidad técnica docente y **no se exige como actividad de clase S13**.

Las ampliaciones de XGBoost, los benchmarks de 50.000 y los 1.000 embeddings neuronales permanecen en los scripts de investigación, pero están **desactivadas en el recorrido central**. No deben iniciarse como pruebas automáticas ni son requisitos para comprender workers y Dask.

## Ruta principal de S13 · Dask en acción, sin pruebas pesadas

**Objetivo:** demostrar mediante tareas realmente ejecutadas por Dask que un mismo computador virtual puede tener uno, dos, cuatro o más trabajadores y que la concurrencia o el paralelismo depende de CPU lógicas, hilos, funciones y memoria. La clase no requiere auditar ceros administrativos, repetir un benchmark de 50.000 fichas, ejecutar OCR real ni descargar modelos.

**Solo dos recursos de estudio:** [presentación interactiva de 32 diapositivas](../../Presentaciones/s13-de-una-maquina-a-un-cluster.html#s1) y [cuaderno S13](../../Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb). Los programas ya están dentro de Codespaces.

### 1. Revisar recursos de la máquina virtual

Abre un Codespace con perfil `S13 · Dask, MapReduce y modelos SECOP` y ejecuta:

```bash
nproc
lscpu | head -25
free -h
cat /proc/self/status | grep Cpus_allowed_list
python -c "import os; print(len(os.sched_getaffinity(0)))"
```

- `nproc` y la afinidad indican **CPU lógicas habilitadas al proceso**. En contenedores, `lscpu` puede mostrar características del host y no las cuotas efectivas del contenedor.
- `free -h` muestra memoria, pero los límites del contenedor pueden ser menores.
- Una máquina con cuatro CPU lógicas puede ejecutar 1 worker × 4 hilos, 2 workers × 2 hilos, 4 workers × 1 hilo o más. Con 8 workers de un hilo habría sobresuscripción. El número de workers **no equivale a número de computadores físicos**.
- Para Python puro suelen funcionar bien workers separados de un hilo; para NumPy/algoritmos nativos pueden aprovecharse varios hilos.

### 2. Demostración breve que ejecuta Dask real

```bash
python Laboratorios/S13_Codespaces/dask_cuando_si.py --workers 2
# Opcional si hay al menos cuatro CPU lógicas y la cuota lo permite:
python Laboratorios/S13_Codespaces/dask_cuando_si.py --workers 4
```

El programa lee como máximo 1.000 títulos SECOP y los divide en ocho lotes. Ejecuta conteo y SHA-256, además de **0,6 segundos de espera externa simulada por lote** (equivalente conceptual a esperar llamadas de OCR/ASR). Dask sí crea procesos worker, reparte la función y comprueba igualdad de resultados. **La simulación NO realiza OCR, transcripción ni solicitudes externas.**

Al finalizar crea `Laboratorios/S13_Codespaces/salidas/dask_demostracion_s13.json` con:

| Campo | Significado |
|---|---|
| `workers_reales` | Direcciones, hilos y memoria de cada proceso worker |
| `cpus_logicas_disponibles` | CPU habilitadas al proceso |
| `segundos_secuencial` | Ocho lotes uno después del otro |
| `segundos_arranque_y_espera_workers` | Iniciar scheduler y workers |
| `segundos_dask_cluster_caliente` | Procesar lotes con trabajadores ya abiertos |
| `segundos_dask_total_incluido_arranque` | Desde iniciar Dask hasta obtener respuesta |
| `resultados_identicos` | Comprobación de igualdad secuencial/distribuido |
| `ganador_caliente` y `ganador_total` | Ganador en **dos mediciones diferentes** |

No hay tiempos predefinidos: el código mide los segundos de cada Codespace. Para comparar el papel de la CPU con funciones de cálculo sintético, de forma opcional:

```bash
python Laboratorios/S13_Codespaces/dask_cuando_si.py --workers 2 --modo cpu
```

Esa modalidad utiliza PBKDF2 con carga moderada; **no** es un modelo de IA ni un benchmark representativo de OCR. Una ganancia no está garantizada y no se obliga a ejecutarla.

### Visualizar el scheduler sin contaminar los tiempos

```bash
python Laboratorios/S13_Codespaces/dask_cuando_si.py --workers 2 --tablero --mantener-tablero-segundos 30
```

Abre **PORTS → 8787 → Private → Open in Browser** mientras el programa conserva el clúster. Los 30 segundos de observación no se suman a los cronómetros. Cuando termina, el panel se cierra deliberadamente.

### 3. Herramienta gráfica en Codespaces

```bash
streamlit run Laboratorios/S13_Codespaces/app_tfidf_unspsc.py --server.address 0.0.0.0 --server.port 8503
```

Abrir `PORTS → 8503 → Private → Open in Browser`. La pestaña **Dask** permite lanzar voluntariamente la demostración y consultar los tiempos reales. En la presentación, las simulaciones de reparto son explícitamente teóricas y complementan este script ejecutable.

### 4. TF-IDF como representación útil para Big Data

**Objetivo:** convertir palabras de fichas SECOP en números para búsqueda o clasificación. TF(A) = veces que aparece la palabra en documento A; DF = documentos del corpus donde aparece; IDF = importancia inversa por frecuencia; TF×IDF = peso de la palabra; L2(A) = peso normalizado del vector A para calcular coseno.

En el corpus A «mantenimiento computadores», B «infraestructura computadores», C «hospital mantenimiento»:
- DF de `hospital` = 1, IDF = 1,6931; en A, TF=0, peso=0.
- DF de `computadores` = 2, IDF = 1,2877; en A, TF=1 y L2=0,7071.
- La tabla interactiva de la presentación muestra estas columnas como tabla legible y cambia si editas los textos.

### 5. Interpretar, no volver a gastar

El análisis histórico interno de 50.000 train + 10.000 test utilizó un **test fijo de 10.000 registros** para comparar distintos tamaños de entrenamiento; los conjuntos no se mezclaban. Los valores corresponden solo a transformar vectores TF-IDF, o a entrenar XGBoost según el cronómetro declarado, y se obtuvieron en una VM GitHub Actions de referencia pública (4 vCPU, 16 GB RAM). Los segundos cambiarán en otra máquina.

**No repetir la prueba de 50.000 en clase ni en Actions.** Los scripts de investigación `benchmark_50k_test_fijo.py`, `medir_workers_50k.py`, `cv_dask_mismo_modelo.py` y Ollama se conservan solo como herramientas opcionales del proyecto docente. El estudiante aprende con ocho lotes, diagnósticos de workers, MapReduce y TF-IDF. No se publican las validaciones exhaustivas de fuente como tarea estudiantil.

### 6. Adaptar a un caso real

Para aplicar Dask a documentos de otro proyecto, sustituye dentro de `procesar_lote` la espera simulada por una función real de OCR, transcripción, ETL o extracción de características. Hazlo únicamente si se dispone de modelos, permisos y capacidad suficientes. Debes mantener la verificación de resultados y los cronómetros separados.

**Fuentes técnicas:** [Dask Best Practices](https://docs.dask.org/en/stable/best-practices.html) · [Dask Distributed Efficiency](https://distributed.dask.org/en/stable/efficiency.html) · [Especificaciones de runners GitHub Actions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job).
