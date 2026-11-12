# S13 · Comparación justa: mismo modelo local vs Dask en 1k, 10k, 20k y 50k SECOP

## Pregunta científica

¿Se gana tiempo procesando/trabajando con Dask cuando **todo lo demás es idéntico**? No tiene sentido comparar tiempo de LinearSVC contra XGBoost: son algoritmos distintos.

### Diseño de paridad

**Fuente:** tres CSV reales versionados de SECOP II (300.000 registros); selección reproducible por reservorio de **50.000 fichas únicas** con descripción y UNSPSC válido. La auditoría anterior demuestra por qué NO se usan ceros de precio u ofertas como etiquetas.

**Categorías objetivo:** segmentos UNSPSC 80, 85, 93, 81, 72 y otras. Se aplica el mismo limpiador al título+descripción. Para cada tamaño, misma selección de datos, misma partición temporal 80/20, mismo vocabulario TF-IDF, mismos n-gramas, semilla e hiperparámetros.

**Pareja 1 (LinearSVC):**

- Local: `TfidfVectorizer.fit(train)`, `transform(train/test)`, `LinearSVC.fit`.
- Dask: *el mismo vectorizador ya ajustado*, `transform(train/test)` usando workers, `LinearSVC.fit` local con la matriz distribuida reunida.
- Hay pruebas que exigen **idénticas matrices, mismos pesos/predicciones y misma F1**. Dask **NO** distribuye el entrenamiento de LinearSVC.

**Pareja 2 (XGBoost):**

- Mismo TF-IDF y mismo SVD a 32 componentes, aprendidos únicamente sobre train.
- `xgboost.train` local contra `xgboost.dask.train` con idénticas etiquetas, 6 clases, 30 rondas, profundidad 4, eta 0,15, semilla 42, `hist`, `subsample=1` y `colsample_bytree=1`.
- Misma capacidad de cálculo nominal (local `nthread=2` frente a 2 workers × 1 hilo), aunque no garantiza equivalencia física perfecta.
- **Advertencia:** XGBoost distribuido usa agregaciones paralelas y cuantiles aproximados; la propia documentación oficial explica por qué las predicciones pueden diferir ligeramente aunque el método e hiperparámetros sean iguales. Se mide acuerdo de predicciones y F1, no se exige igualdad bit a bit. Este diseño demuestra la diferencia de *implementación* para el mismo algoritmo.

**Métricas:** tiempo de lectura, creación de clúster, ajuste vocabulario, transformación TF-IDF, entrenamiento LinearSVC, SVD, entrenamiento XGBoost local y Dask. Se registra F1 macro y balanced accuracy. Todo está en los JSON generados: sin cifras ficticias.

## Resultados reales verificados · GitHub Actions

**Prueba:** https://github.com/jazaineam1/BigData2026/actions/runs/43164041074  
**Entorno:** GitHub Actions Ubuntu, 4 núcleos lógicos, Python 3.11.18, dos workers Dask en una sola máquina. Se analizaron **300.000 filas**, se encontraron **287.682 fichas elegibles** y se muestrearon **50.000 fichas únicas**. Lectura y selección **79,913 s**; inicio del clúster **1,556 s**.

### Mismo LinearSVC, mismos datos y TF-IDF idénticos

| Procesos | Train / Test | Pipeline local (s) | Pipeline con Dask (s) | F1 macro idéntica |
|---:|---:|---:|---:|---:|
| 1.000 | 800 / 200 | **0,14112** | 0,30601 | 0,50408 |
| 10.000 | 8.000 / 2.000 | 1,46924 | **1,31748** | 0,55683 |
| 20.000 | 16.000 / 4.000 | 2,99225 | **2,66186** | 0,58361 |
| 50.000 | 40.000 / 10.000 | 8,14228 | **7,05756** | 0,58605 |

El tiempo de pipeline se calcula como **vocabulario TF-IDF + transformación train/test + fit LinearSVC**. No incluye predicción ni descarga, lectura o deduplicación de la fuente, ni arranque del clúster. En 50.000, el ahorro **1,085 s** no compensa por sí solo el arranque **1,556 s**.

**Paridad confirmada:** matrices TF-IDF iguales, mismos pesos LinearSVC dentro de tolerancias numéricas y predicciones idénticas en los cuatro tamaños. En ambas rutas el `LinearSVC.fit()` corre **localmente**; Dask sólo transforma.

### Mismo XGBoost, mismos datos, misma configuración

| Procesos | Fit XGBoost local (s) | Fit XGBoost Dask (s) | F1 macro local | F1 macro Dask | Predicciones coincidentes |
|---:|---:|---:|---:|---:|---:|
| 1.000 | **0,24466** | 0,90697 | 0,36080 | 0,36080 | 100 % |
| 10.000 | **0,42151** | 0,87320 | 0,41720 | 0,41710 | 96,65 % |
| 20.000 | **0,48047** | 1,05095 | 0,44777 | 0,44901 | 97,75 % |
| 50.000 | **0,75781** | 1,40522 | 0,44039 | 0,43724 | 98 % |

**Misma matriz SVD de 32 características**, mismas etiquetas y 30 rondas `multi:softprob`, `hist`, profundidad 4, tasa 0,15, sin muestreo y semilla 42. Local usa dos hilos y Dask dos workers de un hilo. Los tiempos XGBoost son **sólo `train`**, no incluyen preparar matrices TF-IDF/SVD, construir DMatrix ni predicción.

**Interpretación correcta:** para estos datos y equipo el entrenamiento XGBoost local fue más rápido; que las predicciones no sean bit a bit idénticas no significa que se usó otro modelo. XGBoost documenta variabilidad por histogramas aproximados y orden de reducciones distribuidas. La comparación está controlada, aunque no es una repetición estadística: los tiempos son **una ejecución por tamaño**, no un intervalo de confianza.

### EmbeddingGemma 2: piloto realmente ejecutado con el mismo modelo

**Prueba:** https://github.com/jazaineam1/BigData2026/actions/runs/43164041012

Ollama `embeddinggemma-2:270m`, misma entrada SECOP, 16 textos × lotes de 4:
- Inferencia secuencial **1,636 s**.
- Inferencia repartida por dos workers Dask contra **el mismo Ollama** **1,716 s**.
- Crear el clúster **1,094 s** adicionales.
- Embeddings de 768 dimensiones **exactamente iguales**, diferencia máxima 0.

La proyección lineal al **mismo runner** es aproximadamente 1,42 horas para 50.000 secuencialmente y 1,49 horas con Dask, **NO medición de 50.000 inferencias**. Cambiar hardware, longitud de textos y lotes cambia radicalmente el tiempo. El modelo en Ollama se midió en el runner, no en el HP del docente.

**Próxima prueba de calidad:** el clasificador EmbeddingGemma → LinearSVC usa la misma muestra de 50.000 y el mismo corte de 1.000, 10.000, 20.000 o 50.000 del TF-IDF, con idénticos hiperparámetros de LinearSVC. No se debe publicar una F1 hasta ejecutarlo con el modelo real. Este script ya acepta `--n 50000` y cachea vectores para reiniciar; la corrida completa no se ha efectuado.


## Ejecutar los cuatro tamaños

Dentro del Codespace S13:

```bash
python -m pip install -r Laboratorios/S13_Codespaces/requirements.txt
python Laboratorios/S13_Codespaces/benchmark_paridad_50k.py --sizes 1000 10000 20000 50000 --workers 2 --rondas 30
```

Salida: `Laboratorios/S13_Codespaces/salidas/benchmark_unspsc/paridad_50k_resumen.json`.

**Qué no debes interpretar:** una mejora de 0,2 segundos de Dask en transformación TF-IDF no compensa, por sí sola, crear el clúster, serializar datos y ajustar los modelos. Una sola ejecución de CI no es una prueba de significancia: para un rendimiento robusto deben repetirse tandas, alternar orden local/Dask, fijar procesos externos y registrar variabilidad.

## EmbeddingGemma 2: misma versión 270m y los mismos textos

El experimento adicional usa **sólo** `embeddinggemma-2:270m`, mediante `/api/embed`. Compara la inferencia secuencial con Dask, usando los **mismos textos, mismo lote y mismo servicio Ollama**. Dos workers en la misma CPU no equivalen a dos servidores independientes.

```bash
ollama pull embeddinggemma-2:270m
python Laboratorios/S13_Codespaces/benchmark_embeddinggemma_paridad.py --n 16 --batch 4
```

Si la prueba local pasa, obtendrás un JSON con tiempos medidos en **16 fichas reales** y extrapolaciones **hipotéticas** a 1.000, 10.000, 20.000 y 50.000. No se presenta ese pronóstico como tiempo medido de 50.000 inferencias. Una corrida completa de 50.000 se puede lanzar modificando `--n`, pero para comparar calidad no basta este script de latencia: usa `clasificar_unspsc_embeddinggemma2.py`, que guarda y reusa vectores SQLite.

### Estimación de carga para embeddings

A `float32`, 50.000 × 768 × 4 bytes = **146,5 MiB** sólo de vectores. El tiempo de inferencia será, normalmente, muchísimo más significativo que el almacenamiento. Para CPU local, primero calibra **batch y longitud**; no extrapoles las métricas de GitHub Actions a tu HP sin una medición en ese equipo.

## Evidencias y distinciones

- **QA unitario**: formato UNSPSC, etiquetas, parámetros del SVM, métricas.
- **QA completo GitHub Actions**: exige 50.000 registros reales, procesa los cuatro tamaños, comprueba invariantes y conserva JSON como artefacto.
- **Piloto EmbeddingGemma**: una medición breve REAL en un runner con Ollama solo si se consigue instalar, descargar y ejecutar el encoder; si falla, reportar fallo, no inventar tiempos.
- **Documentación oficial XGBoost**: https://xgboost.readthedocs.io/en/stable/tutorials/dask.html
- **Modelo oficial Ollama**: https://ollama.com/library/embeddinggemma-2:270m

**No medir sólo el `fit()` y llamar a eso «tiempo total».** El manifiesto guarda cada fase para permitir reconstruir el costo de extremo a extremo.
