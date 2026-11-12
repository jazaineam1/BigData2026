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

## La nueva historia principal de S13: TF-IDF, 50.000 procesos y EmbeddingGemma 2

**Atención: esta es la práctica central recomendada.** El antiguo módulo de regresión exploratoria de precios se mantiene sólo para mostrar capacidades de XGBoost, NO para estimar sobrecostos. Los ceros de SECOP no constituyen etiquetas válidas. Consulta la [auditoría de 300.000 registros](../../docs/S13_AUDITORIA_DATOS_SECOP_300K.md).

**Recursos estudiantiles (máximo dos):** la [presentación S13 de 32 diapositivas](../../Presentaciones/s13-de-una-maquina-a-un-cluster.html#s1), con calculadora interactiva de TF-IDF en #44, y el [cuaderno S13 de 91 celdas](../../Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb). No necesitas volver a S12.

### Estación A: herramienta visual de cinco módulos (puerto 8503 privado)

```bash
python -m pip install -r Laboratorios/S13_Codespaces/requirements.txt
streamlit run Laboratorios/S13_Codespaces/app_tfidf_unspsc.py --server.address 0.0.0.0 --server.port 8503
```

Abre `PORTS → 8503 → Open in Browser`. Módulos: explorar SECOP; TF-IDF a mano; búsqueda por coseno; clasificar y visualizar F1 por clase con n-gramas editables; Dask y mediciones; simulación de costos de arranque; exportación de decisiones estructuradas. El código es visible y editable, no una API misteriosa.

### Estación B: benchmark justo, mismo test para 1k, 10k, 20k y 50k

```bash
python Laboratorios/S13_Codespaces/benchmark_50k_test_fijo.py --sizes 1000 10000 20000 50000 --workers 2 --repeticiones 3 --rondas 20
```

Se preservan **10.000 procesos de evaluación fijos** para los cuatro tamaños, una semilla y los parámetros de TF-IDF/LinearSVC. La calidad y tiempo se separan. En una máquina de GitHub Actions con cuatro CPU lógicas, para 50k la transformación de TF-IDF tardó 3,0996 s local vs 1,7655 s Dask, pero su ganancia fue sólo sobre la transformación, no sobre el total.

### Estación C: cuándo NO usar Dask; evaluación cruzada con mismo modelo

```bash
python Laboratorios/S13_Codespaces/cv_dask_mismo_modelo.py --sizes 1000 10000 20000 50000 --cv 3 --workers 2
```

Los mismos tres folds son ejecutados secuencialmente, con `joblib` local en dos procesos y con Dask en dos workers. Sus puntuaciones deben ser **idénticas**. La prueba de 50k dio 9,66 s secuencial, 7,30 s joblib y 42,77 s Dask: aquí Dask **no gana**. Explica serialización de datos, costo de scheduler y el principio de no adoptar infraestructura por moda.

### Estación D: EmbeddingGemma 2 realmente medido en 1.000 procesos

```bash
# Sólo donde corre Ollama (puede ser HP o un Codespace):
ollama pull embeddinggemma-2:270m
python Laboratorios/S13_Codespaces/comparar_1000_embeddings_reales.py --batch 8
```

GitHub Actions ya hizo las **1.000 inferencias reales**: 800 train, 200 test; TF-IDF F1 macro 0,45134 en 0,111 s de vectorización; EmbeddingGemma 2 F1 macro 0,47586 en 119,898 s. **No significa que esos sean los tiempos de tu HP**. Los pesos de Gemma no se reentrenan; sólo se usa su vector como entrada para el mismo LinearSVC. La caché SQLite impide desperdiciar inferencias ya realizadas.

### ¿Cómo elegir más CPU en Codespaces?

GitHub permite máquinas de distintos tamaños según cuenta/cuota. En `https://github.com/codespaces`, abre `...` en tu Codespace → **Change machine type** → selecciona 4-core si está disponible. También `Ctrl+Shift+P → Codespaces: Change Machine Type` en VS Code. No fuerces 4 workers Dask en 2 CPU y no prometas reducción lineal de tiempos. **Cuatro workers dentro de un Codespace siguen siendo una única VM**. Revisa cuota/costo y apaga el entorno al finalizar.

**Referencia técnica:** [mismo test hasta 50k](GUIA_50K_COMPARACION_JUSTA.md).


### Resultado medido de una máquina de 4 CPU lógicas

Se verificó local vs Dask 2 vs Dask 4 workers con el **mismo vocabulario, los mismos 50.000+10.000 textos, las mismas matrices y tres repeticiones**: 1,8497 s local; 1,1595 s Dask 2; 1,0259 s Dask 4. Arrancar Dask costó 1,346–1,459 s y no está incluido en esos tiempos de transformación. [Ejecución y artefacto comprobables](https://github.com/jazaineam1/BigData2026/actions/runs/43172013462). Cuatro workers son cuatro procesos en una VM, no cuatro equipos.

```bash
python Laboratorios/S13_Codespaces/medir_workers_50k.py --reps 3
```
