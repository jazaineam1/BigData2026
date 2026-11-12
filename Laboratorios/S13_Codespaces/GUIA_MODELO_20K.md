# Extensión S13 · Inteligencia de presupuestos SECOP con entrenamiento realmente distribuido

> **AVISO DE REVISIÓN CIENTÍFICA (noviembre de 2026).** Este experimento demuestra entrenamiento distribuido, pero **NO valida un precio justo o una alerta contractual**. La auditoría de 300.000 filas encontró 11.392 precios base cero, 298.726 ceros en el contador de ofertas y 6.419 IDs repetidos. Además, se corrigió la extracción de códigos UNSPSC, pues `V1.80111600` se interpretaba incorrectamente como segmento 18 (correcto: 80). **Las métricas anteriores a esta corrección no son comparables.** Revisa [la auditoría completa](../../docs/S13_AUDITORIA_DATOS_SECOP_300K.md). Para el siguiente laboratorio recomiendo clasificar códigos UNSPSC desde el texto, no tasar contratos.

**Caso:** Laura en Compras Claras recibe más de 20.000 fichas de procesos SECOP. Quiere anticipar un **rango de presupuesto de referencia** y encontrar **discrepancias estadísticas** que merecen verificación humana. La discrepancia **no prueba corrupción, fraude, precios irregulares ni sobrecostos**.

La fuente contiene *registros tabulares de procesos publicados*, no 26.000 PDFs OCR. Ya está en el repositorio: `Cuadernos/datos/secop_chunks/secop_chunk_*.csv`. **No se descarga masivamente SECOP durante la videoclase**.

## ¿Por qué este modelo y no embeddings directamente?

- **Objetivo medible:** `precio_base` publicado, convertido a `log1p(precio_base)`. No se inventan etiquetas de fraude.
- **Modelo A (control):** mediana de precios de entrenamiento; no aprende relaciones.
- **Modelo B (variables):** XGBoost con modalidad, departamento, categoría, contrato, duración, mes y longitud de descripción.
- **Modelo C (variables + texto):** el mismo XGBoost más **16 componentes TF-IDF + SVD**, calculados sobre descripciones. Son **ejes latentes** (LSA), **no embeddings neuronales**.
- **Trabajo realmente distribuido:** `xgboost.dask.DaskDMatrix` y `xgboost.dask.train()` entrenan cada modelo entre **dos workers** y con los datos particionados. Es distinto de usar Dask `client.map()` para entrenar tres modelos locales independientes.
- **Por qué no un embedding neuronal de entrada:** producir embeddings para 26.000 descripciones por CPU exigiría descargar pesos y consumir tiempo de inferencia adicional; con variables medibles y texto TF-IDF/SVD conseguimos una comparación reproducible. Se puede añadir EmbeddingGemma posteriormente **sólo si aporta rendimiento medido**.

## 1. Codespace (no instalar en Ubuntu)

Desde el repositorio escoge **Code → Codespaces → … → New with options → S13 · Dask, MapReduce y modelos SECOP**. No elijas `Airflow Lab` ni `S11 Multimedia`. El entorno instalará dependencias automáticamente. En su terminal:

```bash
python Laboratorios/S13_Codespaces/verificar_entorno.py
python -m pip show xgboost
```

Si falta XGBoost, dentro del propio Codespace:

```bash
python -m pip install -r Laboratorios/S13_Codespaces/requirements.txt
```

**Ejecución exploratoria (26.000 fichas únicas elegidas mediante muestreo de reservorio reproducible sobre el universo elegible; 20.800 de entrenamiento):**

```bash
python Laboratorios/S13_Codespaces/modelo_distribuido_20k.py
```

La versión de prueba en Codespaces/GitHub Actions, con menos árboles para ahorrar tiempo:

```bash
python Laboratorios/S13_Codespaces/modelo_distribuido_20k.py --rondas 30
```

El script imprime número de procesos, cantidad de trabajadores, variables, tiempos y métricas. No imputa ceros; registra su cantidad y elimina el tratamiento como alerta de contrato. Tiene fines formativos, no operativos. **Panel posterior al entrenamiento (visibilidad Codespaces: PRIVATE):**

```bash
streamlit run Laboratorios/S13_Codespaces/app_modelo_20k.py --server.address 0.0.0.0 --server.port 8502
```

En la pestaña **PORTS** abre el puerto **8502** y filtra errores del modelo en la prueba temporal por modalidad y factor de diferencia. La aplicación presenta las predicciones **sobre el conjunto de prueba**, permite abrir el proceso SECOP original y recalca que las discrepancias no son juicios de legalidad.

El puerto **8787** muestra el Dask Dashboard; mantenerlo **PRIVATE** en Codespaces. **Dos trabajadores en un Codespace son un único equipo físico**, aunque el entrenamiento XGBoost use comunicación distribuida entre workers.

## 2. ¿Qué aprende el alumno herramienta por herramienta?

| Paso | Programa visible | Qué hace | Qué debes observar |
|---|---|---|---|
| A | `cargar_procesos()` | Lee por bloques CSV reales y exige IDs únicos | 26.000 fichas, sin inventar duplicados |
| B | `corte_temporal()` | 80 % antiguo para entrenar; 20 % reciente para prueba | **20.800 entrenamiento** como mínimo |
| C | `variables_estructuradas()` | Codifica datos medibles, ajusta sólo sobre train | Número de características y exclusión de columnas de fuga |
| D | `ejes_textuales()` | Convierte textos con TF-IDF + SVD | 16 componentes numéricos, sin modelo neuronal |
| E | `DummyRegressor()` | Predicción de la mediana sin aprender relaciones | Métrica base contra la que competir |
| F | `DaskDMatrix()` | Reparte filas/chunks para XGBoost | Particiones y 2 workers |
| G | `xgboost.dask.train()` | **Entrena UN modelo de forma distribuida** | Modelo B, luego modelo C |
| H | `evaluar()` | Errores sobre periodo reciente | MAE(log), factor de error mediano, % dentro de factor ×2 |
| I | `guardar_revision()` | Ordena discrepancias ×3 o mayores | Casos de **revisión estadística**, no acusaciones |
| J | `manifest.json` | Registra archivos fuente y SHA-256 | Reproducibilidad de datos y configuración |

## 3. Guía para interpretar las salidas

**MAE logarítmico**: error medio entre el logaritmo del presupuesto observado y el pronosticado. Cuanto menor, mejor. Puede relacionarse aproximadamente con una diferencia multiplicativa, pero no es un error porcentual simple.

**Factor de error mediano**: para cada caso calcula el mayor de `real / previsto` y `previsto / real`, después la mediana. Una mediana de 1,6 quiere decir que la discrepancia multiplicativa típica es 1,6 veces (no 60 % para todos los casos).

**Porcentaje dentro de ×2**: fracción de casos cuya predicción no excede el doble ni cae por debajo de la mitad del precio observado.

**Discrepancias ×3**: revisiones prioritarias si el valor real supera en factor 3 el modelo o viceversa; **el modelo no conoce el detalle jurídico, la calidad del contrato, las condiciones de ejecución ni las cantidades**.

**Corte temporal**: evalúa periodos más recientes que los usados para entrenar. Es más honesto que una división aleatoria para una herramienta que debería ayudar a analizar procesos nuevos. Vigilar derivación del dataset: sólo se toman filas del conjunto disponible, sin extrapolar al universo SECOP.

## 4. Salidas privadas

Todo se genera dentro de `Laboratorios/S13_Codespaces/salidas/modelo_20k/`, que está en `.gitignore`:

- `muestra_26k.parquet`: 26.000 registros realmente seleccionados.
- `xgboost_variables.json` y `xgboost_variables_y_texto.json`: dos modelos entrenados.
- `transformadores_confiables.joblib`: mapeo de variables, vectorizador TF-IDF y SVD. Sólo cargar si el archivo es propio y confiable: joblib serializa objetos Python.
- `procesos_revision.csv`: fichas de test ordenables con URL pública SECOP, presupuesto observado/estimado y factor.
- `manifiesto.json`: fuentes y SHA-256, tamaño de train/test, versiones y métricas.

## 5. Ejercicio de razonamiento: un modelo realmente distribuido

1. Abre el tablero Dask (puerto privado 8787). Observa workers, tareas y uso de memoria mientras se construyen matrices y entrenan árboles.
2. Registra la métrica de la mediana y de los modelos B/C. ¿El texto mejora MAE(log) o factor ×2?
3. Si mejora, pregunta si esa diferencia puede deberse a frases que incluyen valores presupuestales. Si empeora, pregunta si SVD pierde información útil.
4. Abre `procesos_revision.csv`, filtra factor ≥3 y **visita la URL pública de un expediente**. Compara descripción, condiciones y presupuesto. No publiques nombres de contratistas con etiquetas de «sospechosos».
5. Compara `--workers 2` con `--workers 3` **sólo si tu Codespace tiene recursos suficientes**; Dask no garantiza que el segundo sea más rápido.
6. Documenta qué partes podrías reutilizar para un proyecto de educación, noticias o facturas; cambia la fuente, las columnas y la variable objetivo.

## 6. Límites que deben quedar claros

- **Los 26.000 son fichas SECOP, no documentos PDF.** Si necesitamos 20.000 PDF con OCR, habría que crear una tubería documental distinta y verificar licencias/acceso.
- El precio base es una cifra registrada; no representa necesariamente un valor de adjudicación, ni un costo justo o estimado por ingenieros.
- No se incluyen datos posteriores como `valor_total_adjudicacion`, `adjudicado` o `respuestas_al_procedimiento` para entrenar, porque no deberían conocerse al fijar el presupuesto.
- Los textos pueden contener cantidades o precios explícitos. Una métrica alta podría derivarse de esa fuga semántica. Hay que revisar esas pistas antes de presentar utilidad operacional.
- **20.800 ejemplos y 2 workers no son por sí mismos una necesidad de Big Data**. El mismo XGBoost podría entrenar más rápido en una máquina. El valor de la clase es demostrar el mecanismo distribuido y contrastar honestamente su costo.

## 7. Referencias oficiales

- SECOP II Procesos: https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-II-Procesos-de-Contrataci-n/p6dx-8zbt
- Dask Machine Learning: https://docs.dask.org/en/stable/ml.html
- Entrenamiento real XGBoost + Dask: https://xgboost.readthedocs.io/en/stable/python/dask-examples/cpu_training.html

**Estado de validación:** documentar resultados de CI y una apertura manual de Codespaces. No afirmar «entrenado sobre 26.000» hasta ejecutar la prueba con los CSV verdaderos.
