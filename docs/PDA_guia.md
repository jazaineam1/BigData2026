# PDA 2026-2 · guía de verificación curricular (Big Data)

**Documento de referencia:** [PDA_2026-02_BIGDATA.pdf](../PDA_2026-02_BIGDATA.pdf), 5 páginas, Universidad Central, asignatura Big Data, código 64491093, 3 créditos, período 2026-2.

**Advertencia institucional:** el PDF identifica al docente Wilman Javier Rincón Bautista y el **grupo 1**. Este repositorio desarrolla el **grupo 2**; antes de modificar definitivamente ponderaciones o fechas de evaluación, confirmar que la coordinación usa ese mismo PDA para el grupo. La guía anterior interpretaba un PDF de 2023-I: era histórico y **no** describe correctamente el documento 2026. El archivo histórico está en [docs/PDA_2024-01_BIGDATA (1).pdf](PDA_2024-01_BIGDATA%20%281%29.pdf).

## Finalidad

Preparar datos de varios formatos y procedencias, gestionarlos mediante tecnologías adecuadas y obtener información de valor para decisiones organizacionales, por lotes o en tiempo real. Big Data no se reduce al tamaño de un archivo; se requiere justificar el diseño y, cuando aplique, evidenciar procesamiento distribuido.

## Evaluación establecida en el PDF 2026-2

| Componente | Peso |
|---|---:|
| Primer taller práctico (NoSQL) | 20 % |
| Segundo taller práctico (ETL) | 20 % |
| Quices | 20 % |
| Laboratorio en casa | 10 % |
| Proyecto final de integración | 30 % |
| **Total** | **100 %** |

El documento expresa aprobación con al menos el 70 % acumulado. **No usar** los porcentajes 25/25/10/40 del PDA anterior para describir el de 2026.

## Ruta literal del PDA 2026-2

| Sesión | Fecha en el documento | Temas y producto esperado |
|---|---|---|
| 1 | 06-ago | Fundamentos, datos estructurados/no estructurados y características Big Data |
| 2 | 13-ago | BI, ciclo analítico, SQL/NoSQL |
| 3 | 20-ago | MongoDB documental y quiz |
| 4 | 27-ago | MongoDB práctica, inicio Cassandra |
| 5 | 03-sep | Cassandra práctica, inicio grafos |
| 6 | 10-sep | Neo4j práctica e introducción Elasticsearch |
| 7 | 17-sep | Elasticsearch y BM25; quiz NoSQL |
| 8 | 24-sep | Primer taller evaluativo MongoDB/Cassandra/Neo4j |
| 9 | 01-oct | Bases vectoriales, búsqueda semántica y Colab |
| 10 | 15-oct | ETL con imágenes; práctica en VS Code y laboratorio semántico |
| 11 | 22-oct | ETL con audio y video; práctica en VS Code |
| 12 | 29-oct | Segundo taller evaluativo sobre ETL |
| 13 | 05-nov | Archivos distribuidos, clústeres, MapReduce, Dask |
| 14 | 12-nov | PySpark en Colab |
| 15 | 19-nov | Spark/Databricks |
| 16 | 26-nov | Sustentación final |

*Nota documental:* el PDA contiene formulaciones inconsistentes de horas de clase/autónomas (3 créditos × 48 horas y 16 sesiones × 3 horas), por lo cual las horas deben conciliarse con coordinación, no inferirse de la guía.

## Correspondencia con la implementación del grupo 2

- **S01–S09:** hay materiales de ingestión, arquitectura, NoSQL, búsqueda lexical y vectorial, y un primer taller sobre SECOP. Las fechas del LMS no son las fechas del PDF del grupo 1.
- **S10:** presentación y cuaderno multimedia ya publicados; ETL reactivo con originales, derivados, JSONL/Parquet y verificación. El PDF pide específicamente imágenes y ejercicio en VS Code; la experiencia actual prioriza navegador/Colab.
- **S11 (decisión expresa del docente):** **ETL integral de imágenes y audio, SIN video**. Recursos de estudiante: `Presentaciones/s11-etl-audio-imagenes.html` y `Cuadernos/11_ETL_Audio_Imagenes.ipynb`. Contiene 32 imágenes del snapshot del curso, 10 voces humanas reales MINDS-14 (licenciadas), 42 transformaciones, catálogo, manifiesto, recuperación y ZIP. Se puede ejecutar en Colab o VS Code. **Adaptación parcial, no cumplimiento literal del componente de video del PDA de grupo 1.**
- **S12:** el segundo taller evaluativo de ETL, ponderado al 20 % en el PDA de referencia, requiere actividad y rúbrica propias; la sesión 11 es formativa y no debe contarse automáticamente como Taller 2.
- **S13–S15:** Dask/MapReduce, PySpark y Databricks deben tener sus propias evidencias operativas. Scripts históricos en el repositorio no equivalen a sesiones publicadas.
- **S16:** sustentación del proyecto integrador.

## Criterio de cumplimiento

Para cada tema: **(a)** el PDA lo solicita, **(b)** hay recurso estudiantil y escenario ejecutable, **(c)** se produce un artefacto con procedencia, **(d)** se ha comprobado una ejecución limpia, **(e)** la evaluación —si existe— se enlaza a la rúbrica y al peso correspondiente.

No confundir: archivo presente en Git = clase impartida = aprendizaje demostrado = calificación registrada. Son evidencias distintas.

## Bibliografía central

Khattak, Buhler y Erl (2016), *Big Data Fundamentals: Concepts, Drivers & Techniques*. El PDF institucional incluye además Rajaraman/Leskovec/Ullman, Ryza y White, entre otras referencias.

