# S09 · Guía docente final: Big Data y bases vectoriales

**Maestría en Analítica de Datos · Universidad Central · 55 minutos desde la diapositiva 21**

## Por qué se rediseñó

El grupo ya conoció búsqueda lexical/Elasticsearch, BM25, E5, embeddings, coseno y Top-k. **No volver a dictar esos conceptos**. El nuevo objetivo es explicar cómo pasar de una matriz local de vectores a un **sistema de base de datos vectorial persistente**, con modelo documental, índice, filtros y evidencias operativas.

| Antes | Problema | Corrección |
| --- | --- | --- |
| 48 celdas | Se repetía un segundo laboratorio completo después de Atlas | 21 celdas, 17 de ruta y 4 de ampliación |
| 120 documentos tratados como Big Data | El tamaño no prueba capacidad de escalar | Muestras honestas de 120 / hasta 6.000 y cálculo de memoria |
| Comparación NumPy vs Atlas ANN | No equivale a comparar ambos motores dentro de Atlas | Consultas reales ANN y ENN de Atlas, con el mismo índice y filtro cuando la versión lo admite |
| IDs solo por proceso | Se podía sobrescribir una ronda/pareja diferente | ID con lote SHA-256 + identificador de proceso + equipo |
| Crear índice confundido con usarlo | Creación asíncrona | Exigir estado queryable antes de consultar |
| Latencia única como benchmark | Imposible inferir escalabilidad o p95 | Latencia etiquetada y extensión opcional de varias pruebas |
| Glosarios y ejemplos de código inconexos | Poca conexión con Big Data | Una arquitectura visual, operaciones y evidencia por paso |

**Competencia evaluable:** diseñar, persistir, indexar y consultar documentos con embeddings en MongoDB Atlas Vector Search, distinguiendo ANN, ENN, filtros, identidad de los lotes y límites del resultado.

## Preparar ANTES de la clase

1. Tener un cluster MongoDB Atlas activo y compatible, con colección disponible.
2. Crear usuario de base de datos con lectura/escritura. Para administrar índices de búsqueda el rol del proyecto debe ser Project Data Access Admin o superior.
3. Configurar Network Access para permitir la IP de salida de Colab. No proyectar la URI ni compartir contraseñas administrativas. Se introduce mediante getpass.
4. MongoDB Atlas Free permite **máximo 3 índices de búsqueda** y Flex hasta 10 según la documentación. Para 30 participantes, usar una demostración docente, no 30 índices sobre un cluster Free.
5. Abrir el cuaderno y escoger **SECOP curso · 120**. Verificar N observado, IDs únicos, lote y que la matriz E5 tenga (N, 384) dimensiones; precargar modelo y embeddings antes de clase.
6. Si la creación del índice tarda, dejar preparado el índice s09_vector_index con campo embedding de 384 dimensiones, cosine, y prefiltros lote/entidad.
7. Si falla Atlas, usar **Respaldo sintético · 6** y NumPy local. No presentar esa ejecución como MongoDB Atlas.

## Libreto de 55 minutos

| Tiempo | Diapositiva | Guion hablado | Acción y evidencia |
| --- | --- | --- | --- |
| 00–04 | 21–22 | «Ya aprendimos a convertir texto en números. ¿Dónde se guardan y consultan los vectores si la solución tiene que operar?» | Señalar los cinco componentes del esquema. |
| 04–08 | 23 | «¿Colab es Atlas? No: Colab ejecuta Python; Atlas mantiene la colección y el índice.» | Preparar usuario, conexión, permisos y red. |
| 08–12 | 24 | «Sin identidad ni procedencia, los vecinos no son auditables.» | Cargar SECOP, mostrar recibidos/válidos/N/LOTE. |
| 12–18 | 25 | «¿Quién produce 384 dimensiones?» E5, no la base de datos. | Generar o recuperar embeddings y tamaño MiB. |
| 18–23 | 26 | «¿Qué demuestra ping?» Conectividad, no índice listo. | Activar USAR_ATLAS y conectar sin publicar contraseña. |
| 23–30 | 27 | «¿Qué pasa si cargamos dos veces?» Debe conservar N sin duplicar. | Upsert, conteo del lote, documento de 384 dimensiones. |
| 30–36 | 28 | «¿Lote y entidad son dimensiones del embedding?» No, son metadatos. | Crear/verificar índice vectorial y filtros. |
| 36–40 | 29 | «¿Una solicitud de índice equivale a índice disponible?» No. | Ver Pending/Ready en Atlas UI; reejecutar celda 5 si el índice se creó desde interfaz; verificar queryable=True. |
| 40–45 | 30 | «¿Quién devuelve este Top-5?» Atlas mediante $vectorSearch. | Ejecutar ANN con filtro lote por PyMongo; generar pipeline JSON para pegar en Data Explorer → Aggregations → Text → Run. |
| 45–48 | 31 | «¿El filtro cambia el embedding?» No, restringe elegibilidad. | Repetir activando SOLO_ENTIDAD_FRECUENTE. |
| 48–51 | 32 | «¿Quién busca exacto y quién aproximado?» ENN y ANN dentro de Atlas si es compatible. | Activar COMPARAR_ENN_ATLAS y comparar IDs, no probabilidades. |
| 51–53 | 33 | «¿Se puede reproducir la operación sin ver mi contraseña?» Sí: consulta, lote, índice, modelo y resultados. | Exportar s09_atlas_evidencia.json. |
| 53–55 | 34–35 | «¿Ciento veinte filas prueban Big Data?» No. «¿Qué mediríamos con un millón?» | Memoria, latencia distribuida, actualización, costo y calidad. |

## Demostración obligatoria de MongoDB Atlas UI

**El mismo índice y consulta se trabajan en dos interfaces.** La clase no termina solo con un `col.aggregate()` mostrado en Python.

**Crear/verificar índice en Atlas UI:**
1. Antes de la celda 5 en Colab, decide crear el índice desde la interfaz. En la celda 5 selecciona `CREAR_INDICE_EN_COLAB=False`; así PyMongo no se adelanta a crearlo.
2. En [Atlas](https://cloud.mongodb.com/) abre tu proyecto → **Search & Vector Search** → **Create Search Index**. Escoge **Vector Search**, base `clase_s09_demo`, colección `secop_vectores`, nombre `s09_vector_index` y **JSON Editor**.
3. Copia la definición completa mostrada por la **celda 5**, también disponible en `s09_indice_atlas_ui.json`. Debe declarar vector `embedding` (384, `cosine`) y filtros `lote` / `entidad`. Confirma la creación. **No crees otro índice si ya existe uno con ese nombre.**
4. En Atlas, observa **Pending → Ready** en Search & Vector Search. Regresa a Colab, vuelve a ejecutar la celda 5 y luego la 6: `queryable=True` confirma disponibilidad.

**Ejecutar Vector Search en la propia consola Atlas:**
1. Ejecuta la **celda 7** de Colab para calcular `q` a partir de la consulta. **No se pega una frase en el campo `queryVector`: se necesitan 384 números del modelo E5 usado para documentos.**
2. La **celda 7** genera inmediatamente **`s09_pipeline_atlas_ui.json`** y un bloque desplegable con el pipeline completo, incluidos `$vectorSearch`, `$project`, el vector de 384 números y el filtro de lote. La celda 8 exporta la evidencia.
3. En Atlas abre **Data Explorer → clase_s09_demo → secop_vectores → Aggregations → &lt;&gt; Text**. Pega el pipeline completo y pulsa **Run**. La consola debe mostrar los documentos recuperados; comprueba `id_proceso`, `entidad` y `score`.
4. Repite desde Colab/PyMongo y verifica que ambas ejecuciones consultan el mismo índice. El **JSON de evidencia de Colab solo certifica las acciones que Colab haya ejecutado**; los resultados de una ejecución exclusivamente en Atlas UI deben comprobarse en Atlas.

Si se elige el camino PyMongo desde el principio, deja `CREAR_INDICE_EN_COLAB=True`; Atlas UI sirve para **inspeccionar estado y ejecutar de nuevo el pipeline**, pero no es necesario crear un segundo índice.

Documentación oficial: [crear índices Vector Search](https://www.mongodb.com/docs/vector-search/indexes/vector-search-type/) · [crear pipelines en Data Explorer](https://www.mongodb.com/docs/atlas/atlas-ui/create-agg-pipeline/) · [consultas ANN/ENN](https://www.mongodb.com/docs/vector-search/query/aggregation-stages/vector-search-stage/).

## Lo que realmente mide cada herramienta

- **NumPy local:** calcula una referencia exacta en memoria, sobre la muestra del Colab. No constituye una búsqueda en Atlas.
- **Atlas ANN:** ejecuta $vectorSearch con numCandidates (por ejemplo 100 para Top-5); el índice navega entre candidatos aproximados.
- **Atlas ENN:** ejecuta $vectorSearch con exact=true y **sin numCandidates**. Si la versión no es compatible, el cuaderno registra NO EJECUTADO.
- **Solapamiento@k de vecinos:** proporción de IDs devueltos por ANN que coinciden con los de ENN. No equivale a precisión humana.
- **Precision@k humana:** proporción de resultados juzgados relevantes por una persona. La sesión no la estima sin etiquetas.
- **Latencia:** tiempo de ida y vuelta de una consulta. Una medición aislada NO valida p50, p95 ni capacidad a escala.

El cuaderno exporta **motor_ann_ejecutado** y **motor_enn_ejecutado** por separado, los conteos, lote, parámetros, resultados, latencias y fuente de datos. Nunca exporta URI ni contraseña.

## Pensamiento Big Data

Para vectores de 384 dimensiones float32, sin contar índice ni metadatos, la matriz consume aproximadamente:

| Registros | Memoria de vectores |
| ---: | ---: |
| 120 | 0,18 MiB |
| 6.000 | 8,79 MiB |
| 100.000 | 146,48 MiB |
| 1.000.000 | 1,43 GiB |

La matriz NO representa el tamaño final de BSON, índice HNSW, caché del servidor, almacenamiento o coste del modelo. La escalabilidad exige ingestión por lotes, actualizaciones, colas/reintentos, indexación, partición, latencia p50/p95, carga concurrente y observabilidad. S11–S15 desarrollan esos temas.

## Contingencias sin falsificar resultados

- **SECOP no entrega 6.000 registros:** mostrar N verdadero; cambiar al CSV del curso si es necesario.
- **E5 tarda en descargar:** usar un Colab docente preparado, sin inventar mediciones.
- **Atlas rechaza ping:** revisar acceso, usuario, permisos y red; continuar local etiquetado LOCAL.
- **Queryable tarda:** esperar o mostrar índice previamente configurado; no atribuir resultados no observados.
- **Atlas sin soporte ENN:** dejar motor_enn_ejecutado como NO EJECUTADO y usar NumPy exacto solo como referencia local.
- **Filtro reduce a cero resultados:** escoger la entidad que sí aparece en el lote; no alterar las etiquetas.
- **Un alumno pierde la ejecución:** el expediente JSON debe indicar qué salió, qué no salió, con ID y parámetros.

## Preguntas cerradas de salida

1. ¿Qué biblioteca ejecuta E5? **SentenceTransformers, en Colab.**
2. ¿Qué sistema almacena y consulta los vectores persistentemente? **MongoDB Atlas.**
3. ¿Cuándo está disponible el índice? **Cuando queryable es True.**
4. ¿Qué diferencia a ANN y ENN? **Aproximación frente a exactitud de vecinos.**
5. ¿Un solapamiento de 1 demuestra relevancia humana? **No.**
6. ¿6.000 embeddings implican automáticamente Big Data? **No.**

## Recursos estudiantiles — máximo dos

1. [Presentación desde S21](https://jazaineam1.github.io/BigData2026/Presentaciones/s09-de-palabras-a-significado.html#s21)
2. [Cuaderno Colab de 21 celdas](https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb)

Esta guía es **material del docente**, no un tercer recurso LMS.

Referencias oficiales: [MongoDB Vector Search: índices](https://www.mongodb.com/docs/vector-search/indexes/vector-search-type/) y [consultas ANN y ENN](https://www.mongodb.com/docs/vector-search/query/aggregation-stages/vector-search-stage/).
