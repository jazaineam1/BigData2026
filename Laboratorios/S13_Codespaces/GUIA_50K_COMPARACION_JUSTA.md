# S13: comparación controlada con 1.000, 10.000, 20.000 y 50.000 procesos SECOP

**Pregunta científica:** ¿para clasificar el segmento UNSPSC de una ficha SECOP (título + descripción), cuándo convienen los vectores TF-IDF locales, su transformación distribuida Dask, o embeddings neuronales EmbeddingGemma 2? ¿Qué cuesta realmente escalar el volumen de entrenamiento?

Este nuevo benchmark **reemplaza las comparaciones previas como evidencia de escalado**: antes cada tamaño tenía un conjunto de prueba diferente. No era válido afirmar que una subida de F1 se debía exclusivamente a más entrenamiento.

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

