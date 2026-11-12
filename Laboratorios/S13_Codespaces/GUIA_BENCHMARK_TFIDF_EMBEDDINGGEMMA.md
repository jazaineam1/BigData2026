# S13 · ¿TF-IDF o EmbeddingGemma 2? Benchmark real sobre SECOP

**Objetivo profesional:** Laura quiere clasificar fichas SECOP con etiqueta UNSPSC declarada. No usamos `precio_base` ni contadores de ofertas: la auditoría de los ceros cuestiona su interpretación.

## Qué estamos comparando exactamente

| Variante | Qué se ejecuta | ¿Dask distribuido? | ¿Se entrena un único modelo distribuido? |
|---|---|---|---|
| A · TF-IDF + LinearSVC local | Tokenizar, vectorizar y entrenar clasificador | No | No; entrenamiento local |
| B · TF-IDF repartido + LinearSVC | Dask transforma particiones con vocabulario común; LinearSVC entrena localmente | Sí, sólo transformación | No |
| C · TF-IDF + SVD + XGBoost Dask | TF-IDF/SVD local + un XGBoost entrenado sobre particiones Dask | Sí | **Sí**, con `xgboost.dask.train` |
| D · EmbeddingGemma 2 270m | Ollama produce embeddings neuronales; clasificador encima | No necesario para una CPU | No al generar embeddings; sólo infiere |

**Misma información de entrada para todos:** título y descripción pública; mismo objetivo UNSPSC (5 segmentos 80, 85, 93, 81, 72 y "OTRAS"), sin usar código UNSPSC como entrada.

**Garantías para cada tamaño:** se leen archivos SECOP verdaderos, se descartan IDs duplicados o códigos inválidos, se muestrean reproduciblemente hasta 20.000, se ordenan por fecha y se separan 80 % antiguo / 20 % reciente. Se comprueba la igualdad exacta del TF-IDF transformado por Dask y por scikit-learn, más identidad de sus predicciones. Se calculan F1 macro (6 clases, incluso si alguna falta en la prueba) y balanced accuracy.

**Limitaciones:** segmentación de 5 códigos + resto y evaluación temporal son una tarea pedagógica. El segmento 80 aparece con frecuencia muy superior al resto, por eso `accuracy` sola engaña. Algunas descripciones contienen códigos explícitos, que intentamos enmascarar; falta inspección humana de fuga, clase y calidad de títulos. Son 20.000 **fichas**, no 20.000 PDF.

## 1 · Medición reproducible TF-IDF

En GitHub Codespaces con perfil **S13**, terminal del repositorio:

```bash
python -m pip install -r Laboratorios/S13_Codespaces/requirements.txt
python Laboratorios/S13_Codespaces/benchmark_unspsc_tfidf_dask.py --sizes 1000 10000 20000 --workers 2 --rondas 20 --svd-dim 32
```

**Interpretación:**
- `segundos_vocabulario_local`: tiempo de aprender el diccionario TF-IDF, **siempre local**.
- `segundos_tfidf_local`: tiempo de transformar los datos (train+test) localmente.
- `segundos_tfidf_dask`: tiempo de transformar exactamente los mismos textos en dos trabajadores (train+test), con comunicación.
- `segundos_svc_local_fit_predict`: entrenamiento del clasificador LinealSVC con TF-IDF local.
- `segundos_svd_local`: reducción SVD que hace posible entrenar árboles compactos. NO es embedding neuronal.
- `segundos_xgb_train_distribuido`: tiempo de **entrenar un único modelo** XGBoost entre workers. No es comparable aislado con toda la tubería TF-IDF local.
- `metricas`: calidad en la prueba temporal de 20 %.
- `segundos_crear_cluster`: coste de crear el clúster, separado, para no ocultar este overhead.

El job CI adjunta los JSON medidos. **Son tiempos en GitHub Actions, NO en tu HP**. En tu HP el rendimiento depende de CPU, swap, RAM, textos, versión, carga, caché y configuración de modelos.

## 2 · ¿Qué variante de EmbeddingGemma elegir?

**`embeddinggemma-2:270m`**, texto solamente. No el modelo completo `embeddinggemma-2` de ~1,3 GB, salvo que después quieras imágenes/audio. El encoder de 270M representa texto en un espacio de 768 dimensiones, tiene variantes compactas, y funciona en Ollama.

En el HP con Ubuntu y Ollama:

```bash
ollama pull embeddinggemma-2:270m
ollama list
python3 -m pip install pandas
python3 Laboratorios/S13_Codespaces/medir_embeddinggemma2.py --model embeddinggemma-2:270m --n 48 --lote 4 --rondas 2
```

**NOTA:** el benchmark usa `/api/embed` por HTTP. El comando `ollama embed` no existe en todas las versiones de Ollama; no es necesario.

La muestra toma descripciones **reales** del primer CSV de 1.000 filas de prueba y las limita a 1.200 caracteres para fijar una carga reproducible. Se calienta el modelo, mide 96 textos repartidos en lotes de 4 y calcula texto/s. A partir de esa tasa extrapola 1.000, 10.000 y 20.000. Es una **estimación basada en tu CPU**, no la ejecución efectiva sobre los 20.000 documentos.

### Estimación inicial por escenarios, pendiente de la medición HP

Si cada documento ocupa en promedio **0,5 / 2 / 8 segundos** una vez calentado Ollama:

| Documentos | 0,5 s/texto (optimista) | 2 s/texto (intermedio) | 8 s/texto (conservador) |
|---:|---:|---:|---:|
| 1.000 | 8 min 20 s | 33 min 20 s | 2 h 13 min |
| 10.000 | 1 h 23 min | 5 h 33 min | 22 h 13 min |
| 20.000 | 2 h 47 min | 11 h 7 min | 44 h 27 min |

**No son tiempos medidos** en tu HP ni un intervalo estadístico: son escenarios condicionados a tasas hipotéticas. Podrían resultar mucho menores con lotes optimizados o mayores con textos extensos, limitación térmica, swap o contención. El programa de calibración sustituye estas hipótesis por una tasa observada.

La memoria de 20.000 × 768 embeddings float32 es aproximadamente **58,6 MiB** sólo de vectores. El peso del modelo, atención y procesos usan RAM adicional. Puedes truncar vectores a 256 dimensiones, si lo permite el modelo/herramienta, y medir el impacto en F1. No confundir tamaño de vectores con tamaño total de inferencia.

### Dask y EmbeddingGemma

Dask puede repartir una lista de textos entre **servidores de inferencia independientes** con suficiente CPU/GPU y modelos cargados. **Dos workers en el mismo HP llamando al único Ollama del HP NO garantizan acelerar**: la CPU sigue siendo la misma. En Codespaces el modelo debe estar instalado **en el Codespace o en un servicio accesible**: instalarlo en el HP no hace que aparezca en los workers remotos.

## 2B · Evaluar realmente EmbeddingGemma como clasificador (opcional en HP o Codespace con Ollama)

La medición de velocidad anterior no evalúa **calidad**. Para compararla con TF-IDF usa el mismo conjunto SECOP, el mismo corte temporal y un clasificador LinearSVC con embeddings congelados:

```bash
# Requiere que Ollama se ejecute en ESTA máquina:
ollama pull embeddinggemma-2:270m
python Laboratorios/S13_Codespaces/clasificar_unspsc_embeddinggemma2.py --n 1000 --batch 4
```

También acepta `--n 10000` o `--n 20000`. Guarda cada vector en SQLite bajo `salidas/benchmark_unspsc/`, identificado por hash de modelo+texto; si se interrumpe, reanuda sin repetir los lotes terminados. Los resultados se guardan como `embgemma_1000.json`.

**Esto es inferencia de embeddings y entrenamiento de LinearSVC, NO ajuste de pesos de EmbeddingGemma**. Si Ollama está en el HP, la GPU de GitHub Actions no se usa. No confundas el costo de generar vectores la primera vez con el costo de reentrenar sobre vectores en caché.

## 3 · ¿Tiene sentido realmente?

**1.000:** TF-IDF/LinearSVC suele ser la primera opción; Dask añade overhead. EmbeddingGemma sólo si necesita semántica o prueba de transferencia que demuestre mejora.

**10.000:** TF-IDF es aún viable localmente; Dask puede ser útil para aprendizaje y coordinación, pero la medición decide.

**20.000:** TF-IDF local sigue siendo viable en equipos modernos, aunque textos y dimensionalidad importan. Dask para procesamiento/entrenamiento distribuido es útil para enseñar arquitectura, no necesariamente por velocidad. EmbeddingGemma añade semántica multilingüe pero su generación puede ser el cuello de botella.

**Regla de éxito:** calidad (F1 macro y clases minoritarias) y costo total (tiempo de vectorización + entrenamiento). No proclamamos «más precisión de embedding» sin ejecutar exactamente el mismo train/test y comparar.

## 4 · Fuentes oficiales

- Ollama: https://ollama.com/library/embeddinggemma-2
- Google, ficha del modelo: https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2
- Google Developers, guía de EmbeddingGemma 2: https://developers.googleblog.com/embeddinggemma-2-the-developer-guide/
- Dask Distributed: https://distributed.dask.org/
- XGBoost-Dask: https://xgboost.readthedocs.io/en/stable/tutorials/dask.html
