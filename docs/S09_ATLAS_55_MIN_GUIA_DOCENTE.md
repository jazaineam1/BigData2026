# S09 · Taller exprés de MongoDB Atlas Vector Search (55 min)
**Continuación inmediata de la diapositiva 21 — no repetir S1–21.**

## Resultado observable
Al terminar, el profesor debe mostrar en pantalla una ejecución **remota** de `col.aggregate([{"$vectorSearch": ...}])` desde Google Colab, con un índice de MongoDB Atlas en estado `queryable = true`, al menos un documento real y el JSON descargado `s09_atlas_evidencia.json`.

No basta con un resultado de NumPy ni un JSON ilustrativo. Si Atlas falla, identificar la ruta NumPy como «local» y documentar el impedimento.

## Preparación del docente ANTES de la demostración
- Disponer de un cluster MongoDB Atlas compatible (M0/Flex puede servir para pruebas pequeñas, con límites).
- Tener usuario de base de datos con permisos de lectura y escritura, privilegios suficientes para crear índices, y configuración de **Network Access** que permita la conexión saliente de Colab.
- Elegir en el Colab **`MODO_DEMO = "rápido (120)"`** y **`USAR_ATLAS = True`**. La contraseña se introduce con `getpass`, no en el código visible.
- Preparar una colección `clase_s09_demo.secop_vectores` y un índice `s09_vector_index` si ya se conoce el dataset y se necesita evitar esperas. La creación del índice es asíncrona; verificar `queryable`.
- En un cluster gratuito M0 hay límite de índices (consultar la documentación oficial). **No** solicitar que los 30 estudiantes creen su propio índice en el mismo cluster o compartan credenciales administrativas.
- No publicar la URI, capturas con contraseñas ni datos sensibles. Este flujo utiliza documentos públicos o un conjunto sintético para respaldo.

## Libreto de ejecución: 55 minutos desde S22
| Minuto | Diapositiva | Colab / acción | Comprobación visible |
| --- | --- | --- | --- |
| 00–08 | 22–23 | Explicar arquitectura, cluster, URI y Network Access. | Qué hace E5 frente a Atlas; ninguna contraseña a la vista. |
| 08–12 | 24 | Ejecutar instalación y carga de SECOP en modo rápido. | Recuento de IDs válidos y origen; 120 o el número real disponible. |
| 12–18 | 25 | Calcular embeddings mediante E5. | Matriz `(N,384)`. |
| 18–23 | 26 | Habilitar Atlas, pegar URI mediante `getpass` y hacer `ping`. | «ATLAS REAL · conexión confirmada». |
| 23–30 | 27 | `bulk_write` de documentos con `embedding`, `entidad`, `lote`. | `count_documents({"lote": LOTE})` igual a N. |
| 30–36 | 28 | Crear/verificar `SearchIndexModel` con `vectorSearch` y filtros. | Nombre del índice y campos configurados. |
| 36–40 | 29 | Esperar hasta 75 s para `queryable`. | `queryable = true` o aviso claro de pendiente. |
| 40–45 | 30 | Ejecutar consulta `$vectorSearch`; inspeccionar Top-5. | Resultados procedentes de Atlas (no de NumPy). |
| 45–48 | 31 | Repetir con una entidad real como prefiltro. | Se limita el universo elegible. |
| 48–51 | 32 | Comparar IDs de Atlas ANN frente a NumPy exacto. | Coincidencia de vecinos@k; no es relevancia humana. |
| 51–53 | 33 | Descargar evidencia JSON. | Motor, fuente, modelo, índice, parámetros, resultados. |
| 53–55 | 34–35 | Explicar plan B, transferencia a otros CSV, 3 respuestas cerradas. | El estudiante distingue ejecución local de Atlas remoto. |

## Qué hacer si algo falla
- **Falla la carga SECOP:** cambia a `respaldo sintético` en la primera celda y decláralo.
- **E5 tarda:** el docente utiliza un entorno previamente preparado y muestra cómo se calcularon los vectores; no inventa tiempos.
- **No conecta PyMongo:** revisar usuario, base de datos, Network Access y disponibilidad del cluster. Ejecutar búsqueda NumPy como respaldo.
- **Índice aún no disponible:** reejecutar la celda de estado; si sigue pendiente, usar un índice preparado o cerrar con la ruta local claramente identificada.
- **No hay coincidencias con filtro por entidad:** eliminar el filtro o elegir el valor exacto de `entidad` presente en el lote.

## Preguntas cerradas para comprobar la comprensión
1. **¿Quién produce los 384 números de un documento?** E5 en Colab.
2. **¿Quién almacena documentos y embeddings persistentemente?** MongoDB Atlas.
3. **¿El retorno de `create_search_index` indica que el índice está listo?** No; esperar `queryable`.
4. **¿Se ejecuta `$vectorSearch` dentro de NumPy?** No: en Atlas.
5. **¿Coincidencia de vecinos@5 = relevancia humana?** No; son métricas diferentes.

## Materiales (máximo 2 recursos estudiantiles)
- [Presentación S09 desde diapositiva 22](https://jazaineam1.github.io/BigData2026/Presentaciones/s09-de-palabras-a-significado.html#s22)
- [Cuaderno S09 en Google Colab](https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb)

**Referencia de comportamiento del índice:** [Documentación oficial PyMongo](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/indexes/) y [Vector Search Indexes](https://www.mongodb.com/docs/vector-search/indexes/vector-search-type/).
