# S13: comparación controlada con 1.000, 10.000, 20.000 y 50.000 procesos SECOP

**Pregunta científica:** ¿para clasificar el segmento UNSPSC de una ficha SECOP (título + descripción), cuándo convienen los vectores TF-IDF locales, su transformación distribuida Dask, o embeddings neuronales EmbeddingGemma 2? ¿Qué cuesta realmente escalar el volumen de entrenamiento?

Este nuevo benchmark **reemplaza las comparaciones previas como evidencia de escalado**: antes cada tamaño tenía un conjunto de prueba diferente. No era válido afirmar que una subida de F1 se debía exclusivamente a más entrenamiento.

## Resultados que YA se midieron (GitHub Actions, 12 de noviembre 2026)

**Método:** test temporal de 10.000 IDs idénticos, entrenamientos anidados, mismo TfidfVectorizer, mismo LinearSVC e hiperparámetros. TF-IDF local y Dask se ejecutaron tres veces por tamaño, reportando mediana. Dos workers Dask dentro de un runner con cuatro CPU lógicas.

| Train | TF-IDF local (s) | TF-IDF Dask (s) | F1 macro LinealSVC mismo test |
|---:|---:|---:|---:|
| 1.000 | 0,5773 | 0,4028 | 0,48914 |
| 10.000 | 1,0469 | 0,6435 | 0,55635 |
| 20.000 | 1,5667 | 0,9170 | 0,56585 |
| 50.000 | 3,0996 | 1,7655 | 0,57385 |

A 50.000, XGBoost sobre los mismos 32 ejes TF-IDF/SVD y los mismos parámetros tardó **0,4488 s local**, **0,9337 s Dask** en su entrenamiento. No mezclar estos tiempos con el tiempo de TF-IDF o LinearSVC. <https://github.com/jazaineam1/BigData2026/actions/runs/43167104999>

**EmbeddingGemma 2:** se generaron los **1.000 embeddings reales**, no un piloto extrapolado. Mismo test 200, mismo train 800, mismo LinearSVC. TF-IDF obtuvo F1 macro **0,45134** y vectorizó en **0,111 s**; EmbeddingGemma 2 obtuvo F1 macro **0,47586** y generó vectores en **119,898 s**. Esta prueba es diferente de la comparación con test fijo de 10.000; no se deben cruzar sus F1. <https://github.com/jazaineam1/BigData2026/actions/runs/43167105003>

**Validación cruzada idéntica:** tres folds y el mismo TF-IDF + LinearSVC:
| Entrenamiento | Secuencial | joblib 2 procesos | Dask 2 workers |
|---:|---:|---:|---:|
| 1.000 | 0,2757 s | 0,8906 s | 0,4585 s |
| 10.000 | 1,7595 s | 1,0624 s | 6,1408 s |
| 20.000 | 3,2329 s | 2,2706 s | 13,7370 s |
| 50.000 | 9,6596 s | 7,2979 s | 42,7739 s |

Los folds produjeron las mismas puntuaciones con los tres motores. **Dask perdió en ese entorno**, lo cual descarta la idea de prometer mejoras automáticas. Un clúster físico, datos persistidos y cálculos más costosos podrían cambiar el resultado, pero eso requiere una prueba nueva, no una afirmación. <https://github.com/jazaineam1/BigData2026/actions/runs/43167597500>

## Protocolo reproducible

- **Origen idéntico:** tres archivos `secop_chunk_*.csv` versionados en el repositorio, 300.000 registros crudos. Selección reproducible de 60.000 IDs únicos con UNSPSC válido, fecha, título/descripción suficientes; códigos numéricos se eliminan del texto. No descargar ni generar contratos artificiales.
- **Conjunto de prueba común:** las **10.000 fichas más recientes del muestreo**, idénticas en las cuatro condiciones. La huella SHA-256 de sus IDs se registra para demostrarlo.
- **Entrenamiento:** 50.000 fichas anteriores al test, orden aleatorio fijo con semilla 42. Subconjuntos **anidados** de 1.000, 10.000, 20.000 y 50.000. El cambio planificado único es el número de documentos para entrenar. Se registra la frecuencia de cada categoría por tamaño.
- **Seis clases iguales:** 80, 85, 93, 81, 72 y OTRAS. F1 macro, balanced accuracy, matriz de confusión y F1 por clase sobre el MISMO test.
- **Representación local y Dask exactamente equivalente:** TfidfVectorizer igual (hasta 6.000 términos, unigramas/bigramas, `min_df=2`, `max_df=.98`, normalización y tipo float32). En cada tamaño el vocabulario se **ajusta exclusivamente a los datos de entrenamiento de ese tamaño**. Dask recibe ese vocabulario ya ajustado, distribuye solamente la transformación; el script verifica igualdad de matrices y predicciones.
- **Clasificador exactamente igual:** LinearSVC con `class_weight="balanced"`, `random_state=42`; entrenado sobre el mismo TF-IDF en cada tamaño, no se atribuye un ajuste distribuido que no ocurrió.
- **XGBoost local y Dask:** ambos usan **exactamente los mismos 32 ejes TF-IDF/SVD**, parámetros (`multi:softprob`, 6 clases, `hist`, profundidad 4, tasa .15, semilla 42, 20 rondas). XGBoost local usa 2 hilos y Dask utiliza dos workers de un hilo: suma equivalente de 2 hilos, aunque la carga del scheduler no es idéntica. Las métricas pueden variar por paralelismo.
- **Medición separada:** tiempo para leer y muestrear los 300.000 registros, crear el clúster, ajustar vocabulario, transformar local/Dask (3 repeticiones, mediana), entrenar LinearSVC, ajustar SVD, entrenar XGBoost local/distribuido. La comparación temporal de un único `transform` NO equivale al tiempo extremo a extremo.

## Ejecución de la parte TF-IDF / Dask (50k completos)

Desde GitHub Codespaces S13, sin instalar nada en Ubuntu local:

```bash
python -m pip install -r Laboratorios/S13_Codespaces/requirements.txt

python Laboratorios/S13_Codespaces/benchmark_50k_test_fijo.py \
  --sizes 1000 10000 20000 50000 --workers 2 --repeticiones 3 --rondas 20
```

Métricas en `Laboratorios/S13_Codespaces/salidas/benchmark_unspsc/benchmark_50k_test_fijo.json`. GitHub Actions entrega exactamente los JSON como artefacto temporal.

## EmbeddingGemma 2: mismo encoder en los cuatro tamaños

Modelo congelado **`embeddinggemma-2:270m`**, texto, 768 dimensiones; mismos textos, clases y test de 10.000 procesos; clasificador **LinearSVC con los mismos parámetros** que TF-IDF. El modelo no se afina, sólo se generan embeddings. La cache SQLite guarda vectores con huella SHA-256 de modelo + texto, para no inferir dos veces.

### Piloto real de velocidad (también se intenta en GitHub Actions con CPU)

```bash
ollama pull embeddinggemma-2:270m
python Laboratorios/S13_Codespaces/benchmark_embeddinggemma2_50k.py \
  --modo piloto --n-piloto 32 --batch 4
```

Para el piloto se usan **32 textos del mismo conjunto de prueba fijo**, se mide calentamiento y 8 lotes, y se informa la tasa efectiva. La estimación de procesamiento para cada tamaño incluye los **10.000 ejemplos de test** que una evaluación justa también tiene que codificar.

### Experimento completo con embeddings (50k entrenamiento + 10k test)

```bash
python Laboratorios/S13_Codespaces/benchmark_embeddinggemma2_50k.py \
  --modo full --sizes 1000 10000 20000 50000 --batch 4
```

La primera ejecución debe generar hasta **60.000 embeddings** y podría ser costosa en CPU. Si se corta, los lotes confirmados permanecen en `salidas/benchmark_unspsc/cache_embeddinggemma2.sqlite3`, y una nueva ejecución reutiliza esos vectores. No afirmamos que corrió ni una sola F1 neuronal hasta completar esa extracción. El piloto sólo mide latencia.

### Lo que NO se puede comparar sin matices

- Si 1.000 usa el mismo test de 10.000 que 50.000, el costo de evaluar también cuenta. No confundir «tamaño total procesado» con «tamaño de entrenamiento».
- Cambiar de TF-IDF a EmbeddingGemma 2 significa cambiar de **representación**, aunque conservemos LinearSVC y test. Podemos comparar su F1 y costo extremo a extremo, pero no atribuir toda la diferencia sólo a Dask.
- TF-IDF con Dask y TF-IDF local comparten idéntico vocabulario y modelo; esta sí es una comparación directa de transformación.
- XGBoost local y distribuido comparten matriz y parámetros; permite medir el costo de entrenar un algoritmo distribuido, con cuidado de la no determinación de paralelismo y recursos.
- No inventar tasas de Ollama en el HP basadas en resultados de GitHub Actions: hardware y enfriamiento son diferentes.
- Los códigos UNSPSC declarados son etiquetas administrativas, **no verdad jurídica**; errores de registro, categorías sobrerrepresentadas y frases con códigos explícitos siguen siendo riesgos a revisar.

## Criterios de aceptación

1. Cuatro resultados de 1k, 10k, 20k y 50k **con el mismo hash de IDs del test fijo**.
2. 50.000 ejemplos de train y 10.000 test de SECOP auténtico, sin duplicación.
3. Tres repeticiones de vectorización local y Dask por tamaño, igualdad exacta de matrices.
4. F1 macro/por-clase, matriz de confusión, balanced accuracy y baseline de mayoría.
5. XGBoost local **y** Dask con datos y parámetros equivalentes.
6. Para EmbeddingGemma 2, informe separado de **inferencia real de piloto** y **proyecciones**; sin ninguna F1 inventada.

### Fuentes

- [SECOP II Procesos de Contratación](https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-II-Procesos-de-Contrataci-n/p6dx-8zbt)
- [EmbeddingGemma 2 en Ollama: etiqueta 270m](https://ollama.com/library/embeddinggemma-2/tags)
- [XGBoost con Dask](https://xgboost.readthedocs.io/en/stable/tutorials/dask.html)


## Prueba completada de 4 CPU lógicas: exactamente el mismo trabajo

En GitHub Actions, [ejecución 43172013462](https://github.com/jazaineam1/BigData2026/actions/runs/43172013462), comprobamos la igualdad exacta de las matrices TF-IDF en **50.000 train + 10.000 test**. Un solo vocabulario aprendido previamente, mismos textos, misma máquina con 4 CPU lógicas, tres repeticiones por método:

| Motor / trabajadores | Mediana sólo de transformación | Arranque de clúster |
|---|---:|---:|
| scikit-learn local | **1,8497 s** | No aplica |
| Dask 2 procesos | **1,1595 s** | 1,3460 s |
| Dask 4 procesos | **1,0259 s** | 1,4587 s |

**Cómo se lee:** Dask 4 ganó sólo la transformación, ahorrando 0,1336 segundos frente a Dask 2.  
**Qué nos dice:** algunos textos se transforman más rápido en paralelo cuando hay CPU disponible.  
**Qué NO permite concluir:** que Dask gane el tiempo de extremo a extremo; aquí no se incluyó leer/limpiar 300.000 registros, aprender vocabulario ni iniciar el clúster.  
**Error común:** creer que cuatro procesos Dask equivalen a cuatro máquinas o que la mejora pequeña compensa pagar una máquina más grande.

```bash
# Sólo para una máquina que reporte cuatro CPU lógicas:
python Laboratorios/S13_Codespaces/medir_workers_50k.py --reps 3
```
