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
- **Dask Distributed:** distribuye entrenamientos independientes y recupera un fallo controlado de tarea; **no entrena un solo modelo distribuido**.
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

## Pruebas

```bash
cd Laboratorios/S13_Codespaces
python -m unittest -v test_s13
```

El panel Dask usa el **puerto privado 8787** de Codespaces. Si no se abre, usa `client.scheduler_info()`: el resultado del laboratorio no depende de la interfaz gráfica. Los dos workers son hilos en la misma máquina remota, no dos equipos físicos.

## Transferencia a otros proyectos

El módulo `analisis.py` tiene funciones separadas para lectura, preparación, procesamiento, entrenamiento y exportación. Para adaptar el caso, cambia la ruta del CSV, `COL_TEXTO`, `COL_LABEL` y `CLASES` después de verificar nombres/valores reales. Usa siempre `train_test_split` ANTES de ajustar TF-IDF; nunca selecciones hiperparámetros usando el conjunto de prueba. Prueba cada cambio con una muestra pequeña.

Los archivos creados van a `Laboratorios/S13_Codespaces/salidas/`, excluida de Git. No subas datos personales ni credenciales al repositorio público. Cierra el Codespace al finalizar para ahorrar cuota.

## Datos y límites

- 200 expedientes de `Datos/tc2_corpus_2026.json`: **sin etiqueta de modalidad** y no usados para aprendizaje supervisado.
- 1.000 procesos de `Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv`: 59 columnas, sí incluye descripción y modalidad.
- La muestra de entrenamiento y las dos clases frecuentes no representan el universo SECOP; clasificar modalidad **no prueba irregularidades**.
- Dask puede ser más lento que pandas en datos pequeños; no presentar tiempos medidos en un Codespace como ventaja universal.

## Advertencia de calidad de datos

**No interpretamos los ceros de SECOP como ausencia de competencia.** Consulta la [auditoría sobre 300.000 filas](../../docs/S13_AUDITORIA_DATOS_SECOP_300K.md). Este modelo de precio es una demostración de entrenamiento distribuido, NO sirve para declarar sobrecostos. Los códigos UNSPSC `V1.80111600` deben leerse como segmento 80 (no 18). Los archivos de modelos entrenados antes de esa corrección no deben usarse.

## Profundización · 20.800 procesos de entrenamiento XGBoost distribuidos

El cuaderno S13 contiene una **ampliación opcional** sobre 26.000 fichas SECOP, con 20.800 procesos para entrenamiento y 5.200 para evaluación temporal. El programa real es [modelo_distribuido_20k.py](./modelo_distribuido_20k.py); la guía [GUIA_MODELO_20K.md](./GUIA_MODELO_20K.md) explica fuente, instalación, XGBoost distribuido verdadero y métricas. No son 26.000 PDF.

```bash
python Laboratorios/S13_Codespaces/modelo_distribuido_20k.py --rondas 30
streamlit run Laboratorios/S13_Codespaces/app_modelo_20k.py --server.port 8502
```

Codespaces → PORTS 8502 **PRIVATE**. Ninguna discrepancia predicha constituye prueba de fraude. El cuaderno y la presentación originales siguen siendo los dos recursos estudiantiles de la sesión.

## Benchmark científico · 50.000 procesos, mismo modelo local y distribuido

**[Guía y resultados medidos](./GUIA_PARIDAD_50K.md)** · [Código reproducible](./benchmark_paridad_50k.py).

Ya se compararon 1.000, 10.000, 20.000 y 50.000 procesos SECOP reales usando **un solo algoritmo LinearSVC** contra sí mismo (TF-IDF local/Dask con matrices y predicciones idénticas) y XGBoost frente a XGBoost distribuido (iguales datos, 32 componentes SVD, clases y rondas). No compares velocidad de LinearSVC y XGBoost: son modelos diferentes.

```bash
python Laboratorios/S13_Codespaces/benchmark_paridad_50k.py --sizes 1000 10000 20000 50000 --workers 2 --rondas 30
ollama pull embeddinggemma-2:270m
python Laboratorios/S13_Codespaces/benchmark_embeddinggemma_paridad.py --n 16 --batch 4
python Laboratorios/S13_Codespaces/clasificar_unspsc_embeddinggemma2.py --n 50000 --batch 8
```

La última instrucción es una **corrida potencialmente larga**, no completada en CI. Los tiempos EmbeddingGemma para 50.000 son extrapolaciones de un piloto de 16, no medidas directas. El código almacena vectores SQLite para recuperarse de interrupciones.
