# Proyecto final Big Data 2026-2S · Compras Claras
**Propuesta docente auditable · 22 de noviembre de 2026 · grupo 2 · alcance máximo S14**

> **Estado:** diseño implementado parcialmente en una rama de revisión. No equivale a publicación académica, evaluación habilitada ni prueba E2E en Databricks Free. **No fijar fecha de entrega** hasta decisión docente. El PDA 2026-2 en `docs/PDA_guia.md` procede del grupo 1; su ponderación del proyecto final (30 %) queda pendiente de confirmar para el grupo 2.

## 1. Un problema, un flujo, un resultado

**Problema único para todos:** Laura necesita clasificar la **modalidad administrativa** de procesos SECOP II, buscar descripciones relacionadas y presentar evidencia trazable. Se usan exclusivamente las etiquetas `Contratación directa` y `Contratación régimen especial` porque ya están preparadas en S13. **No se modela fraude ni se atribuyen irregularidades.** El alumno no elige tema, fuente, etiqueta, algoritmo, modalidad de entrega ni conjunto de prueba.

**Producto único:** un expediente analítico consultable del mismo caso que une: demostración de descarga paralela real y controlada; ETL sobre la muestra SECOP versionada; tareas reales Dask; tres entrenamientos independientes coordinados por Dask; tablas/consultas Spark–Databricks; regresión logística distribuida en Spark MLlib **guiada**; explorador de resultados y manifiesto técnico. El proyecto es integración de lo enseñado, no inventario de servicios.

### Rúbrica corregida (100 puntos, para revisión docente)

El observatorio **funcional sin Codespaces** vale 20 puntos. El estudiante deberá producir sus salidas y justificar una predicción correcta y una errada si existe; ejecutar celdas no basta.

| Bloque | Puntos | Evidencia observable |
|---|---:|---|
| A. Descarga controlada | 8 | dos páginas, hash, tiempos reales o fallo de red demostrado |
| B. Contrato ETL | 12 | registros fuente, limpieza, IDs únicos, split común, hashes |
| C. Dask datos y workers | 12 | particiones, dos workers observados, igualdad con pandas |
| D. Dask entrenamiento | 13 | tres ajustes independientes, CV en train, test reservado |
| E. Databricks, Spark SQL y Delta | 15 | subida CSV, capas Bronze/Silver/Gold, consulta contrastada |
| F. Spark MLlib guiado | 15 | pipeline resuelto, predicciones y F1 solo en test |
| G. Observatorio del estudiante | 20 | HTML offline consultable, filtros, predicciones y CSV descargable |
| H. Manifiesto, trazas y defensa | 5 | PR del equipo, SHA y explicación de un registro propio |
| **Total** | **100** | |

**Equidad:** no se pierden puntos por no pagar un servicio o agotar cuotas preexistentes. La actividad bloqueada se documenta con error real y se valida mediante un plan de respaldo docente previamente probado. No inventar ejecuciones remotas.

## 2. Lo que sí se impartió y lo nuevo que NO puede exigirse sin guía

| Tema | Soporte real | Condición del taller |
|---|---|---|
| Arquitectura y ETL | S01–S02, S10–S12 | aplicar, no redictar |
| Descarga HTTP concurrente | TC1 E1 (`utils/tc1_secop.py`, `ThreadPoolExecutor`) | ejemplo de 2 páginas con tope y reintentos |
| MongoDB/Cassandra/Neo4j | S03–S06/TC1 | consulta conceptual en Explorer; **no** crear tres cuentas nuevas |
| BM25, embeddings, ranking | S07/S09/TC2 | explorar y vincular; no repetir modelo pesado |
| OCR/ASR | S10/S11/TC2 | evidencia consultable de forma opcional; **no** volver a transcribir 10 audios |
| Dask/TF-IDF/regresión logística | S13 (`Laboratorios/S13_Codespaces/analisis.py`) | reutilizar `entrenar_y_evaluar`, `experimentos_distribuidos` |
| Spark DataFrame/SQL, Delta, Databricks | S14 (`Cuadernos/14_PySpark_Compras_Claras.ipynb`) | ejecutar en mismo caso |
| Spark MLlib sobre texto | **NO** figura en la ruta principal S14 | ofrecer celdas resueltas, explicación de `Pipeline`, `Tokenizer`, `HashingTF`, `IDF`, `LogisticRegression`. Primer piloto docente antes de calificar |

## 3. Datos y contrato único

- **Única base de entrenamiento calificada:** `Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv` (1.000 filas, 59 columnas; verificar SHA y conteos en ejecución limpia).
- Columnas de trabajo: `id_del_proceso`, `descripci_n_del_procedimiento`, `modalidad_de_contratacion`. El filtro de clases, deduplicación y exclusión de descripción vacía viene del módulo real S13.
- **División fija** entrenar/test estratificada, `random_state=42`, exactamente según `separar_muestra` de S13; se exporta con columna `split` para Databricks. No recalcular una nueva división en Spark.
- `10.000` **NO** se usa como supuesto dato ya existente. Una ampliación a registros adicionales requerirá snapshot real único con fecha, fuente, licencia, SHA y validación previa del profesor. Los estudiantes no multiplican las 1.000 filas.
- La descarga en vivo de la API oficial SECOP (identificador público `p6dx-8zbt`) es **un experimento de concurrencia independiente del dataset de entrenamiento**. Limitar a dos páginas de 20 filas, con `$order` estable; repetir únicamente 4 solicitudes por pareja (2 seriales + 2 concurrentes). La fuente cambia con el tiempo: una discrepancia no se oculta. Registrar resultado de red y usar snapshot para continuar si el servicio falla.
- La fuente no debe ser atacada desde todos los alumnos simultáneamente. Hacer turnos, usar caché y respetar HTTP 429/`Retry-After`.

## 4. Recorrido del estudiante — pasos guiados, sin tema a escoger

### Paso 0 · abrir material y comprobar entorno
1. Abrir el tutorial interactivo `Presentaciones/proyecto-final-explorer.html` desde la rama de revisión o sitio tras publicación.
2. Abrir `Cuadernos/Proyecto_Final_Compras_Claras.ipynb` en **Codespaces S13**. No usar el perfil raíz Airflow.
3. Ejecutar `python Laboratorios/S13_Codespaces/verificar_entorno.py`. Observar `nproc`, `free -h`, versiones y ubicación de datos; si no hay entorno, usar dependencias del perfil S13. No confundir CPU físicas con workers.
4. Establecer la identidad de la pareja en el manifiesto, sin escribir datos personales en un repositorio público. **Evidencia:** comprobación de los archivos reales.

### Paso 1 · adquisición controlada
1. Leer esquema de las 1.000 filas congeladas y anotar SHA-256.
2. Ejecutar **dos páginas secuenciales** de 20 registros contra SODA `p6dx-8zbt`; respetar límite de concurrencia.
3. Ejecutar **las mismas dos páginas** con `ThreadPoolExecutor(max_workers=2)`.
4. Comparar IDs, valores y hashes ordenados; observar tiempos medidos sin afirmar que paralelo siempre gana.
5. En error de red, registrar HTTP, página y contingencia: el aprendizaje posterior sigue con snapshot. **No inventar una descarga exitosa.**
6. **Evidencia:** `A_descarga.json`, con `modo`, `filas`, `mismas_paginas`, `segundos` y error si ocurre.

### Paso 2 · ETL y datos del entrenamiento
1. Filtrar exactamente las dos modalidades existentes y deduplicar por `id_del_proceso`.
2. Limpiar texto de `descripci_n_del_procedimiento` sin alterar etiquetas.
3. Construir `train`/`test` con semilla 42 y guardar `secop_final.csv` (ID, texto, modalidad y `split`), más manifest con SHA.
4. Verificar dos etiquetas, ausencia de IDs repetidos, split disjunto y presencia de ambas clases. **Evidencia:** `B_fuente.json`, CSV y conteos por clase.

### Paso 3 · procesamiento con Dask DataFrame
1. Visualizar CPU lógicas permitidas y configurar 2 workers; comprobar direcciones reales con `Client.scheduler_info()`.
2. Ejecutar conteo por modalidad con pandas y con Dask repartiendo particiones.
3. Comprobar igualdad numérica y registrar tiempos del mismo cálculo. No se exige acelerar una muestra pequeña.
4. **Evidencia:** `C_dask.json` con workers, particiones, conteos y verificación.

### Paso 4 · entrenamiento paralelo real (Dask)
1. Revisar el modelo ya conocido: `TfidfVectorizer` + `LogisticRegression`.
2. Ajustar la división fija y ejecutar tres valores de C = `0.1, 1.0, 10.0` mediante tareas independientes del cliente Dask.
3. Seleccionar C por F1 de validación cruzada **dentro del entrenamiento**, y evaluar **una sola vez** con test.
4. Comparar con el `DummyClassifier` de S13. **Evidencia:** `D_modelo_dask.json`.
5. Interpretación obligatoria: este bloque distribuye **experimentos separados**, no el entrenamiento interno de un único modelo.

### Paso 5 · Databricks Free Edition, Bronze / Silver / Gold
1. Guardar CSV ya preparado desde Codespaces.
2. Abrir Databricks Free Edition y usar **Catalog → Add/Upload data / Create table from upload**. El nombre del menú puede variar: localizar la herramienta para crear una tabla a partir de CSV. No usar descarga HTTP dentro de Databricks Free.
3. Crear una tabla Delta en el catálogo y esquema disponibles; **registrar el nombre real** (por ejemplo `workspace.default.secop_final` sólo si existe).
4. En un notebook de Databricks, ejecutar Spark DataFrame y SQL con ese nombre; normalizar a Bronze/Silver/Gold y conservar `split`.
5. Reabrir tablas y comprobar conteos y claves. **Evidencia:** `E_databricks.json`, consulta SQL y captura auténtica de workspace.

### Paso 6 · entrenamiento Spark MLlib, extensión guiada de S14
1. Explicar que Spark distribuye transformaciones y cálculos del modelo sobre particiones; no equivale a correr 3 fits independientes.
2. Ejecutar código resuelto: `Tokenizer → HashingTF → IDF → LogisticRegression` con un único pipeline.
3. Ajustar **sólo** el conjunto `train` importado; evaluar `test`, sin volver a dividirlo.
4. Calcular F1, matriz de confusión, número de registros y errores de predicción. **Evidencia:** `F_spark_modelo.json`.
5. **Riesgo:** `pyspark.ml` existe en serverless de Databricks, pero no se ha validado este cuaderno en una cuenta estudiantil Free. Si falla por cuota/plataforma: el docente registra contingencia; ejecutar variante PySpark local probada (si está preparada). No atribuir la falla al estudiante.

### Paso 7 · Producto final offline y entrega
1. Usar el mejor C elegido en E4, ajustar el modelo en `train` y guardar predicciones reales exclusivamente sobre `test`.
2. Generar `predicciones.csv`, `observatorio.html` con `Laboratorios/Proyecto_Final_2026/generar_observatorio.py`, y el manifiesto.
3. Abrir el observatorio **sin servidor**. Verificar filtros, búsqueda de descripciones, modalidad real/predicha, F1 y exportación CSV.
4. Identificar un ID correctamente predicho y otro incorrectamente predicho si existe, ambos provenientes del propio test.
5. Registrar trazas y evidencia Databricks real si se ejecutó; documentar fallos de cuota. No simular éxito.
6. Entregar aplicación estática funcional y evidencias mediante PR en el repositorio privado existente.
7. No publicar en la portada ni el LMS hasta autorización.

**Evidencia:** aplicación funcional, CSV test, SHA, manifiesto y defensa basada en resultados propios.

## 5. Fichas de interpretación repetibles

Para cada salida relevante, repetir exactamente:
- **Cómo se lee:** qué campo, denominador, universo y unidad se observan.
- **Qué nos dice:** conclusión válida del caso.
- **Qué NO permite concluir:** cuál evidencia concreta falta.
- **Qué error común:** ejemplo de error que falsearía esa conclusión.

La teoría prepara acciones. Un paso tiene siempre **HAZ ESTO**, **DEBE VERSE**, **SI FALLA** y **EVIDENCIA**. No exigir instalar MongoDB/Cassandra/Neo4j/Ollama, OCR o Whisper de nuevo; su función de repaso permanece en la herramienta consultable.

## 6. Restricciones reales comprobadas (fuentes primarias, nov-2026)

- Databricks Free: serverless-only, cuotas y egress restringido: https://docs.databricks.com/aws/en/getting-started/free-edition-limitations
- Databricks serverless: sin RDD API ni Spark UI convencional, modelos Spark ML limitados por tamaño, usar Unity Catalog: https://docs.databricks.com/aws/en/compute/serverless/limitations
- Subir CSV por interfaz en Free Edition: https://docs.databricks.com/aws/en/ingestion/create-or-modify-table
- PySpark MLlib soportado en serverless: https://docs.databricks.com/gcp/en/machine-learning/train-model/mllib
- Dask recomienda controlar particiones, carga por tarea, y no confundir más workers con más velocidad: https://docs.dask.org/en/stable/best-practices.html
- API Socrata limita/segmenta páginas y puede aplicar throttling: https://dev.socrata.com/consumers/getting-started.html ; https://support.socrata.com/hc/en-us/articles/202949268-How-to-query-more-than-1000-rows-of-a-dataset

## 7. Viabilidad, riesgos y decisiones

| Riesgo | Impacto | Medida |
|---|---|---|
| Internet/API SECOP caída o límites por IP | no se completan 4 solicitudes | snapshot versionado; evidencia del fallo, no simulación de éxito |
| Dask pequeño más lento que pandas | interpretación errónea | calificar igualdad y trazas, no speedup |
| Datos demasiado pequeños para mostrar ventaja | falsa historia «Big Data porque es grande» | usar particiones/trabajo real y explicar por qué es laboratorio de arquitectura, **no prueba de escala masiva** |
| Databricks sin salida a GitHub/SECOP | importar archivos falla | carga CSV por interfaz oficial, no `requests` desde Databricks |
| MLlib no visto en S14 | sobrecarga | entregar código resuelto, explicación de funciones, no examen de API no enseñada |
| Distinta tokenización entre sklearn/Spark | F1 distinto | mismo split/etiquetas; no exigir métricas idénticas |
| Cuenta Free con cuotas agotadas | inequidad | piloto docente de disponibilidad y crédito condicionado al servicio; no exigir compra |
| Proyecto muy largo | abandono de pasos | recursos limitados a Explorer/guía + cuaderno; bloques cortos y checklist recuperable |
| Correcciones costosas en Actions | gastos | sin E2E automático de modelos; pruebas de estructura ligeras, ejecución real manual y justificada |
| Respuestas clonadas entre equipos (mismos datos) | autenticidad baja | PR privado con trazas y defensa individual sobre resultados efectivamente calculados |

## 8. Control docente antes de publicar

1. **Verificar** que el snapshot del S13 contiene realmente 1.000 filas, dos clases suficientes y claves únicas.
2. Ejecutar secuencial y concurrente desde una red real (máx. 4 solicitudes); no realizarlo en cada push.
3. Ejecutar S13 Dask en Codespaces de estudiante, con 2 workers reales y 3 modelos.
4. Probar upload manual + Delta + Spark MLlib en **una cuenta Databricks Free** sin acceso premium/caché previo.
5. Confirmar que todos los recursos abren con móviles, sin scroll lateral, contraste correcto y fuente de cada dato.
6. Confirmar rúbrica, peso y **fecha del grupo 2**. No publicar ni crear calificación oficial hasta este paso.
7. Publicar como máximo dos recursos del taller: el Explorer/guía y un cuaderno principal. Los archivos auxiliares son infraestructura, no «material 3».
8. Probar un alumno piloto en entorno limpio; leer errores, no estimar el tiempo de trabajo sin evidencia.
9. Revisar secretos/PII y preservar el repo de cada equipo como privado.
10. No activar benchmarks grandes ni modelos de lenguaje en GitHub Actions.

## 9. Criterios para considerar terminado el taller

- **Funcional:** Codespaces produce CSV, JSON y validaciones Dask; Databricks produce tablas y métricas verificables.
- **Pedagógico:** un estudiante sin la clase anterior sigue todos los pasos sin tener que descubrir rutas, APIs o credenciales.
- **Consulta permanente:** el Explorer indexa S01–S14, diferencia muestras demostrativas/resultados propios y enlaza los materiales existentes.
- **Entrega:** un manifiesto auditable con huellas/filas y PR del repositorio **ya existente**.
- **Calidad:** ejecución limpia del recorrido central y pruebas de navegador / validadores ligeros, con marca explícita de cualquier paso pendiente de test real.

**Limitación al redactar:** no se ha ejecutado aquí el notebook real en Codespaces, la API en vivo, ni Databricks Free con una cuenta estudiantil. Esos resultados deben marcarse pendientes. No afirmar resultados de pilotos todavía no realizados.


## Auditoría de viabilidad

Antes de asignar, revisar [análisis de viabilidad y presupuesto estudiantil](PROYECTO_FINAL_S14_VIABILIDAD.md). **No publicar este taller en la portada ni el LMS durante revisión**.
