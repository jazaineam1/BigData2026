# S09 · Libreto docente ÚNICO (55 minutos, desde la diapositiva 21)

**Universidad Central · Maestría en Analítica de Datos · Grupo 2 · Big Data 2026-2S**

## Qué cambió y qué se exige

**Ruta principal autónoma:** cada estudiante abre su Colab y usa **Atlas temporal automático**. El notebook llama a la API oficial de **MongoDB Atlas Ephemeral Free/M0** para crear un clúster individual. La API devuelve una URI privada y un enlace de reclamación; el cuaderno no solicita host, usuario, contraseña ni IP al profesor. No reutiliza el clúster compartido del curso. En su servicio temporal MongoDB permite 0.0.0.0/0 con autenticación individual. No se cambia el acceso de ningún proyecto existente.

**Lo que debe aprender realmente:** E5 produce embeddings; MongoDB conserva documentos y metadatos; un índice vectorial de 384D/cosine habilita ANN; el filtro restringe el universo; $vectorSearch devuelve candidatos, no una verdad. Se distinguen simulador 2D, NumPy local y Atlas auténtico.

**Dos recursos estudiantiles:** presentación HTML con laboratorio visual y el cuaderno de 21 celdas. El tutorial está integrado; no se añade tercer recurso LMS.

## Libreto unificado de 55 minutos

| Tiempo | Diapositivas / recurso | Libreto y acción observable |
| --- | --- | --- |
| 00–04 | S21–S23 | «Ya representamos textos. ¿Cómo guardar y consultar los vectores sin perder identidad, filtros y trazabilidad?». Señalar E5 → documento → índice → consulta. |
| 04–07 | Laboratorio visual: Documentos | Abrir «Explorar base vectorial». Insertar y repetir upsert: 8 → 9 → 9; explicar _id y persistencia conceptual. |
| 07–10 | Laboratorio visual: Índice | Probar campo vectorial 2D válido, luego incompatibilidad 384D; distinguir solicitar índice de comprobar disponible. |
| 10–14 | Laboratorio visual: Consulta | Ejecutar exacta, cambiar filtro, recorrer grafo aproximado. Explicar que el dibujo NO es HNSW ni E5 real. |
| 14–17 | Laboratorio visual: Evaluación | Juzgar los k candidatos y calcular Precision@k. Exportar JSON marcado SIMULACIÓN LOCAL. |
| 17–23 | S24–S25 / Colab celdas 0–2 | Abrir copia individual Colab; cargar SECOP curso 120; mostrar cantidad real N y E5 (N,384) normalizado. |
| 23–31 | S26 / Colab celda 3 | Mantener «Atlas temporal automático». Ejecutar: API crea clúster M0, URI se guarda en memoria y ping verifica conexión real. No se introduce contraseña ni IP manualmente. Mostrar enlace para reclamar y ver la consola UI. |
| 31–36 | S27 / Colab celda 4 | Cargar documentos de lote en Atlas; repetir bulk_write y mostrar conteo idéntico. |
| 36–41 | S28–S29 / Colab celdas 5–6 | Mostrar JSON índice; crear índice real; comprobar queryable=True. No confundir crear con disponibilidad. |
| 41–49 | S30–S32 / Colab celda 7 | Consulta $vectorSearch con filtro de lote. Cambiar frase, luego seleccionar entidad de ranking propio; comparar IDs. ENN opcional si instancia admite. |
| 49–53 | S33 / Colab celda 8 | Exportar expediente JSON; demostrar motor real, lote, IDs, filtro e índice. Si Atlas falla, evidencia dice NO EJECUTADO y conserva NumPy local. |
| 53–55 | S34–S35 | «¿Qué no probamos?». 120 registros no son Big Data; el coseno no es probabilidad; una consulta no estima precisión general ni rendimiento sostenido. |

**Al proyectar la consola Atlas real:** la opción de reclamar clúster es voluntaria y exige una cuenta personal MongoDB/Google para abrir Atlas UI. El resto (crear clúster, crear colección, construir índice, buscar) sí puede realizarse íntegramente por Python sin cuenta. Si quieres mostrar Atlas UI durante los 55 minutos, reclama previamente **tu propio clúster docente temporal** y proyecta Database → Data Explorer → clase_s09_demo → secop_vectores; luego Search & Vector Search → s09_vector_index y Aggregations → Text. No compartas el enlace privado de reclamación ni la URI.

## Qué debe observarse y cómo interpretar cada prueba

| Prueba | Evidencia legítima | Qué NO demuestra |
| --- | --- | --- |
| Creación Ephemeral | Respuesta válida de API y URI privada en memoria | Que el índice está disponible |
| ping | «ATLAS REAL · conexión confirmada» | Que se escribieron datos |
| bulk_write + count_documents | «documentos del lote: N de N» | Que la recuperación funciona |
| create_search_index | «creación del índice solicitada» | Que queryable ya es True |
| list_search_indexes | «disponible: True» | Que los resultados son relevantes |
| col.aggregate($vectorSearch) | Tabla Atlas REAL con ID, entidad, score | Precisión humana o escalabilidad |
| NumPy local | Vecinos exactos en la muestra local | Persistencia ni búsqueda Atlas |
| JSON de simulación | Relaciones conceptuales en vectores 2D | E5, HNSW o MongoDB |

## ¿Qué hace el alumno, sin requerir al docente?

1. Abre el Colab publicado y usa **Entorno de ejecución → Ejecutar todo**. No se le solicita contraseña, IP ni host para la ruta predeterminada.
2. Observa los cuatro hitos reales: ping, N documentos, índice queryable y Top-k remoto.
3. Cambia una consulta y después una entidad desde resultados observados, una variable por vez.
4. Descarga su expediente; la copia a Drive es opcional, no bloquea la ruta principal.
5. Para **aprender la interfaz MongoDB Atlas** de forma individual, reclama desde el enlace privado mostrado y abre el Data Explorer, el índice y el constructor de agregaciones. Esto sí puede exigir cuenta y confirmación de correo personales; nunca del profesor.

## Contingencias y límites

- **API Atlas devuelve 429/5xx:** no se crea clúster. El cuaderno lo declara y continúa con NumPy; la ejecución real queda pendiente. No afirmar que conectó.
- **Atlas demora en provisionar:** la celda de conexión reintenta ping; una conexión fallida no se disfraza de Atlas.
- **Índice tarda:** reejecutar verificación; nunca usar «creado» como sustituto de queryable=True.
- **El clúster se pausa o desaparece:** sin reclamar, MongoDB pausa a los 2 días y elimina a los 7. La evidencia JSON debe conservarse fuera del clúster.
- **Red de cualquier origen:** solo aplica a cada Ephemeral aislado; no es una invitación a abrir 0.0.0.0/0 en el clúster compartido. Tras reclamar, MongoDB permite restringir IPs.
- **No almacenamiento de credenciales:** la URI se mantiene en memoria del runtime; el notebook no escribe la contraseña ni el enlace privado de reclamación en JSON o código. El enlace de reclamación puede verse en la salida y no debe redistribuirse.
- **Costo:** Free/M0 es gratuito sujeto a límites de capacidad y a la política vigente de MongoDB. Si el estudiante reclama el clúster, no debe seleccionar ofertas de pago.
- **El laboratorio del navegador** sigue siendo conceptual. Su estado no se evalúa por el LMS como evidencia real de Atlas.

## Material y verificaciones

- Presentación: https://jazaineam1.github.io/BigData2026/Presentaciones/s09-de-palabras-a-significado.html#s21
- Colab: https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb
- Documentación MongoDB Ephemeral: https://www.mongodb.com/docs/atlas/tutorial/create-ephemeral-cluster/
- Índices desde PyMongo: https://www.mongodb.com/docs/search/indexes/manage-indexes/
- Búsquedas: https://www.mongodb.com/docs/vector-search/query/aggregation-stages/vector-search-stage/

La CI offline comprueba estructura, rutas de recuperación y contratos mediante mocks; **no** certifica acceso remoto real, tasa de éxito de la API, experiencia del alumno ni ausencia de límites por instancia. Una verificación genuina debe observar el clúster, índice y consulta desde un runtime con red.
