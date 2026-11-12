# Guía docente S13 · SECOP, TF-IDF, Dask Distributed y EmbeddingGemma 2

**Clase:** Universidad Central, Maestría en Analítica de Datos, modalidad virtual, 180 minutos. **ÚNICOS recursos que el estudiante necesita abrir:** (1) `Presentaciones/s13-de-una-maquina-a-un-cluster.html` (60 diapositivas, calculadora interactiva) y (2) `Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb` (82 celdas). **Instrumentos dentro del mismo Codespace:** panel Streamlit en 8503, Dask Dashboard 8787 y scripts editables. Esta guía es **para el docente**, no una tercera lectura obligatoria.

## Caso que une toda la sesión

> «Laura recibe centenares de miles de fichas de procesos SECOP. Su equipo cree que necesita un clúster para usar inteligencia artificial. Antes de comprar infraestructura, necesitamos saber qué significa cada dato, convertir descripciones a variables, evaluar un modelo real y medir si repartir tareas supera al cálculo local. No podemos justificar el gasto porque una presentación muestre flechas.»

**Producto de la sesión:** una representación TF-IDF explicada, un clasificador de categorías UNSPSC auditado, un experimento local vs Dask con el mismo algoritmo y test, y una decisión justificable sobre cuándo convienen embeddings neuronales. No producir una «lista de contratos sospechosos».

**Salud de los datos:** la auditoría de 300.000 fichas detectó 298.726 ceros en contador de ofertas y 11.392 precios base cero. No son etiquetas de fraude ni ausencia de competencia. Los 6.419 IDs repetidos obligan a deduplicar. UNSPSC con `V1.80111600` corresponde al segmento **80** (no 18). Hay seis clases docentes: 72, 80, 81, 85, 93 y OTRAS. Las clases son administrativas, no verdades jurídicas.

## Distribución de la sesión · 180 minutos

| Bloque | Minutos | Diapositivas | Trabajo tangible |
|---|---:|---|---|
| Caso y auditoría de datos | 0–20 | 1–5, 36, 40, 48 | Formular etiqueta válida sin ceros ambiguos |
| Herramientas de datos y HDFS/MapReduce | 20–40 | 6–12 | Explicar partición, réplica, promedio correcto |
| Codespaces y fuente SECOP | 40–55 | 13–20 | Abrir perfil S13, verificar módulos y CSV |
| TF-IDF *a mano* y búsqueda | 55–90 | 41–47, 44–46 | Calcular DF/IDF; editar 3 textos; buscar |
| Descanso corto | 90–100 | — | Sin tareas nuevas |
| Entrenar LinearSVC + control | 100–120 | 28–35, 48–49 | F1 macro, balance de clases, fuga de datos |
| Comparación Dask vs local vs joblib | 120–155 | 50–54 | Leer pruebas de 50k y CV con folds idénticos |
| EmbeddingGemma + reto transferible | 155–180 | 55–60 | Comparar 1k real, justificar costo, entregar evidencia |

La primera mitad promueve preguntas y experimentos manuales; desde la segunda mitad el alumno manipula datos, código y resultados. No conviertas las 60 diapositivas en 60 monólogos: algunas sirven como referencia de consulta.

## Libreto palabra por palabra: apertura

**Docente:** «Nos contaron que Big Data significa datos grandes y muchos servidores. Hoy pondremos esa idea a prueba. Laura tiene registros de contratación pública, pero no todas sus columnas significan lo que parecen. Antes de escoger un modelo o distribuirlo, hagan una hipótesis: si un contador de ofertas vale cero, ¿eso demuestra que no hubo competencia?»

**Espera una respuesta.** «No. Podría ser un campo incompleto, una fase, un código o una regla del sistema. Auditamos 300.000 registros y encontramos casi 299.000 ceros en ese contador; hay expedientes seleccionados con el mismo cero. Por eso **descartamos esa etiqueta**. La nueva pregunta sí es verificable: ¿podemos inferir el segmento UNSPSC que está registrado utilizando el título y la descripción?»

**En pantalla:** apertura del curso, luego S13 #36–#40. Pide a un estudiante que identifique la diferencia entre una ficha de proceso y un PDF adjunto. No digas que hay 50.000 PDFs: **son fichas tabulares**.

## Libreto TF-IDF: el ejemplo de tres documentos

**Docente:** «Un modelo estadístico no entiende una oración como la entendemos nosotros. Recibe números. TF-IDF es una forma de transformar palabras en pesos. TF significa *frecuencia de término*: cuántas veces aparece. DF significa *frecuencia documental*: en cuántos documentos aparece. IDF significa *frecuencia documental inversa*: una palabra que aparece en todas partes aporta poco para distinguir un documento de otro».

**Muestra diapositiva 42 y escribe:**

```text
A = mantenimiento computadores
B = hospital computadores
C = hospital mantenimiento
```

**Docente:** «Primero cuenten: 'computadores' aparece en A y B, por tanto DF=2. 'Hospital' aparece en B y C: DF=2. 'Mantenimiento' aparece en A y C: DF=2. Ahora sustituyan en la fórmula: ln((1+3)/(1+2))+1 = 1,28768. ¿Por qué sumamos uno? Por suavizado y estabilidad. Esta misma IDF corresponde a cada término, independientemente del documento donde se encuentre».

**Espera hipótesis.** «Si escribo dos veces 'computadores' en A, cambia su TF, pero no su DF: continúa apareciendo en dos documentos. El peso inicial de A sube, luego se normaliza L2. Por tanto, **peso TF-IDF no es probabilidad de que el contrato sea de tecnología**».

**Abre diapositiva 44 y pulsa «Calcular pesos manuales»**. Cambia la palabra «hospital» de B a «infraestructura». Pregunta: «¿Cuánto es ahora la IDF de 'hospital'?». Si aparece en un solo documento: ln(4/2)+1 = 1,6931. La calculadora interactiva muestra TF(A)×IDF pero no normaliza L2; para esa comprobación pasa al cuaderno, celda que imprime `mini_tabla` y valida norma 1.

**Docente:** «En el cuaderno no ejecuten el siguiente bloque sin comprenderlo: `fit_transform` construye un vocabulario e IDF; `transform` aplica **el mismo** a un texto nuevo. Repetir `fit_transform` con el test haría trampa».

**Actividad:** los estudiantes cambian el corpus, predicen cambios, ejecutan y registran cuatro rótulos:
- **Cómo se lee:** fila documento, columna palabra, valor ponderación.
- **Qué nos dice:** las palabras que distinguen se ponderan.
- **Qué NO permite concluir:** semántica, legalidad, causalidad.
- **Error común:** confundir IDF y un resultado de clasificación.

## Libreto de las variables del modelo

**Docente:** «El paso siguiente es separar entradas y objetivo. Las entradas son título y descripción. La etiqueta es el segmento del código UNSPSC declarado por la entidad. El código no se introduce en el texto de entrenamiento porque sería una fuga directa. Si falta el código, no inventamos la respuesta».

**Muestra en cuaderno** `pd.read_csv(usecols=[...])`, `drop_duplicates("id_del_proceso")`, `re.fullmatch` y las frecuencias de categoría. «Si el segmento 80 es el mayoritario, podríamos presumir que un clasificador que prediga siempre '80' es bueno. Por eso nuestra referencia es `DummyClassifier`, y nuestra métrica es **F1 macro**, el promedio de F1 de cada categoría».

**Docente:** «El clasificador se llama LinearSVC. Aprende una frontera lineal entre los pesos TF-IDF; no genera texto ni se convierte en un LLM. Fijamos la semilla y los parámetros. Reservamos el periodo más reciente como prueba, y ajustamos el vocabulario sin ver el test».

**Actividad:** entrenar, mirar F1 por clase, cambiar unigramas/bigramas con test intacto y explicar límites. Evitar reiterar el ajuste de hiperparámetros usando la misma prueba final.

## Libreto de Dask: demostrar, no prometer velocidad

**Docente:** «Ahora imaginemos 50.000 fichas. ¿Es obligatorio un clúster? No. Lo medimos. Dask es un planificador que reparte trabajo; no es un nuevo algoritmo de clasificación. Distinguiremos tres comparaciones: transformar TF-IDF local y repartido; entrenar XGBoost local y XGBoost distribuido con el mismo modelo; y repetir validación cruzada con **el mismo TF-IDF + LinearSVC** de forma secuencial, multiproceso local y Dask».

**En pantalla, diapositivas 49–54:** tablas medidas con test fijo de 10.000, tamaños 1k/10k/20k/50k, tres repeticiones de transformación. A 50k la transformación tarda 3,0996 s local y 1,7655 s Dask, pero esto omite abrir el clúster y aprender el vocabulario.

**Docente:** «Ese ahorro es real para la operación concreta, no para el pipeline completo. ¿Y el entrenamiento XGBoost? En 50k el local tardó 0,4488 s y Dask 0,9337 s. Dask perdió. El problema es demasiado pequeño, y esa es una conclusión profesional válida».

**Abre `cv_dask_mismo_modelo.py`:** «Cada fold vuelve a ajustar TF-IDF sólo con su propio entrenamiento. La misma función se ejecuta secuencial, con joblib y con Dask. Las tres F1 deben ser idénticas. Si hay diferencias, no estamos midiendo sólo arquitectura». La prueba real reportó que en 50k el secuencial tardó 9,66 s, joblib 7,30 s y Dask 42,77 s; en esta máquina Dask no ofreció ventaja. Debe investigarse la comunicación y serialización del corpus.

**Pregunta de decisión:** «¿Qué necesitaríamos para que Dask compense? Muchas tareas costosas, datos persistidos en workers, varias CPU desocupadas o un clúster físico que verdaderamente resuelva una limitación de memoria/capacidad. No basta agregar workers a un solo portátil».

**Codespaces con más CPU:** GitHub permite cambiar la máquina a 4 cores si está disponible. Ruta comprobable: `github.com/codespaces` → menú de tres puntos → **Change machine type**; también la paleta de comandos de VS Code → **Codespaces: Change Machine Type**. Una máquina superior puede costar más: revisar cuota/facturación y detenerla al salir. 2 vs 4 núcleos no deben confundirse con múltiples computadores.

## Libreto EmbeddingGemma 2: la prueba de 1.000

**Docente:** «Ya entendemos un vector disperso con palabras. Ahora probemos un vector neuronal: EmbeddingGemma 2 270m. No vamos a volver a entrenar los 270 millones de parámetros. Usamos `/api/embed` de Ollama para producir una representación de 768 números por descripción y aplicamos el **mismo clasificador LinearSVC**».

**Muestra la ejecución de GitHub Actions verificada** y el resultado de la comparación con los mismos 800 train y 200 test:
- TF-IDF F1 macro **0,45134**, vectorización **0,111 segundos**.
- EmbeddingGemma 2 F1 macro **0,47586**, vectorización **119,898 segundos**.
- Modelos y etiquetas idénticas, representación distinta. **Mejora 2,452 puntos porcentuales** de F1, a costo de mucha más inferencia.
- Esto se midió en CPU de GitHub Actions; no afirmar tiempos de HP.

**Docente:** «¿Pagarían aproximadamente dos minutos para representar mil documentos si la mejora de F1 es pequeña? Depende del impacto profesional, la necesidad de semántica y si se reutilizan los embeddings. No conocemos aún la respuesta para 50.000 embeddings reales. El script tiene caché SQLite para conservar progreso y no recalcular».

**Práctica:** abre `app_tfidf_unspsc.py` en Codespaces con `streamlit run ... --server.port 8503`; abre PORTS → 8503 → Private. El estudiante debe observar la matriz TF-IDF, escribir su consulta y contrastar los casos donde el texto no comparte palabras. Si Ollama se ejecuta en otro equipo, ese servidor no aparece mágicamente dentro del Codespace.

## Lista de comprobación antes de dictar

1. La presentación tiene 60 diapositivas y calculadora dinámica en #44; la app carga con cinco pestañas y código visible.
2. El cuaderno tiene todos los ejemplos hechos a mano y código editable, ejecuta **Run All sin activar inferencias costosas**. No depende de que S12 se haya dictado.
3. Los procesos SECOP se leen del repositorio y su objetivo es el código UNSPSC declarado; no se imputan ceros.
4. Los benchmarks tienen huellas del test y muestras anidadas, comparan el **mismo modelo** cuando se mide velocidad.
5. Las cifras se citan como GitHub Actions, no como HP; los resultados de 50k no se atribuyen a EmbeddingGemma.
6. Dashboard Dask 8787 privado; panel docente 8503 privado; puerto 8502 es legado de regresión exploratoria de precios y no se necesita para la nueva historia.
7. Todos los recursos quedan en el mismo repositorio. No exigir una instalación Ubuntu, pago de APIs ni cuentas adicionales.

## Evidencia de los resultados

- Ensayo 1k real Ollama / EmbeddingGemma 2: https://github.com/jazaineam1/BigData2026/actions/runs/43167105003
- Ensayo justo hasta 50k: https://github.com/jazaineam1/BigData2026/actions/runs/43167104999
- Validación cruzada, mismos 3 folds y algoritmo: https://github.com/jazaineam1/BigData2026/actions/runs/43167597500
- Guía técnica reproducible: `Laboratorios/S13_Codespaces/GUIA_50K_COMPARACION_JUSTA.md`

**Cierre:** «Una gran habilidad en Big Data no es usar el mayor número de máquinas: es escoger la menor arquitectura que resuelve de forma confiable el problema, poder explicar cada variable y reproducir el resultado».
