# PDA: fuente de guía del curso

Resumen operativo del **Plan de Desarrollo de la Asignatura (PDA)** de Big Data, para alinear el material con lo que la institución declara del curso. El documento original está en [`PDA_2024-01_BIGDATA (1).pdf`](PDA_2024-01_BIGDATA%20%281%29.pdf).

> **Versión.** El PDF que hay en el repo es el **PDA 2023-I** (así lo dice su primera página y sus metadatos de febrero de 2023), aunque el archivo se llame `2024-01`. Un archivo `PDA_2026-02_BIGDATA.pdf` entregado después resultó **idéntico byte a byte** (mismo SHA-256), es decir, tampoco es un PDA de 2026. Mientras no se suba el PDA vigente, esta guía describe el 2023-I y las diferencias con el curso 2026-2S se listan abajo. Cuando exista el vigente, se reemplaza este archivo y se conserva el anterior como historia.

## Cómo se usa

- **Toda evaluación se traza al PDA:** puedes señalar qué porcentaje y qué producción del PDA respalda cada entrega. Si una entrega no cabe en ninguna, es una decisión que se documenta, no una omisión.
- **La finalidad manda sobre la herramienta:** el PDA pide decisiones en entornos distribuidos, no dominar un producto (ver `AGENTS.md` §1).
- **Lo que este archivo no sabe:** el calendario y las fechas 2026-2S viven en `lms/data/course.json`, no aquí.

## Datos del espacio formativo

| Campo | Valor en el PDA |
|---|---|
| Programa | Maestría en Analítica de Datos · Facultad de Ingeniería y Ciencias Básicas · Universidad Central |
| Espacio formativo | Big Data · código 64491093 · 3 créditos |
| Naturaleza | Teórico-práctica |
| Prerrequisito | Métodos Estadísticos para Analítica de Datos (sin co-requisitos) |
| Dispositivos pedagógicos | Clase expositiva o dialógica · estudio de caso · laboratorio en centro de cómputo |

## Finalidad y problema general

Con datos que vienen de sensores, redes sociales, simulación y nuevas técnicas de adquisición, hacen falta algoritmos y tecnologías de administración de datos que permitan **extraer e interpretar** información. El curso trata técnicas de análisis y gestión de datos para **tomar decisiones en entornos distribuidos**, la inteligencia empresarial y el descubrimiento científico, con **aprendizaje basado en problemas** que integra Analítica I y II y Bases de Datos.

Abordar Big Data **más allá del volumen**: explotar los datos para diseñar productos y servicios a partir de información sobre el entorno, los usuarios, la competencia y el contexto. Recogida la información, hay que tener la infraestructura para procesarla y obtener indicadores útiles en ejecución **por lotes o en tiempo real**.

## Ruta de sesiones del PDA 2023-I

| Sesión | Tema | Producción del estudiante |
|---|---|---|
| 1 | Presentación; datos y analítica; qué es Big Data; datos estructurados, semi y no estructurados | Lectura (Erl, cap. 1) |
| 2 | Arquitectura empresarial; procesos de negocio; ciclo de vida de la analítica | Lectura (caps. 2–3) |
| 3 | Casos de uso; inteligencia de negocios tradicional y con Big Data | Presentación de casos del entorno laboral |
| 4 | OLTP y OLAP; Data Marts, Warehouses y Lakes; ETL | Lectura (cap. 4) |
| 5 | Implementación de ETL con herramientas de flujos de trabajo | **Quiz** (sistemas de análisis y ETL) |
| 6 | **Primer taller de evaluación** | Taller 1: herramientas para procesos ETL |
| 7 | Sistemas de archivos distribuidos, clusters, replicación y fragmentación | Lectura (cap. 5) |
| 8 | Procesamiento paralelo y distribuido; Hadoop; batch con Map-Reduce | **Quiz** (almacenamiento) · lectura (cap. 6) |
| 9 | Implementación de Map-Reduce | Práctica |
| 10 | **Segundo taller de evaluación** | Taller 2: procesamiento batch con Map-Reduce |
| 11–12 | NoSQL: grafos, columnares y documentales (partes 1 y 2) | Lectura (cap. 7) · práctica · proyecto |
| 13 | Elasticsearch | Proyecto |
| 14 | PySpark | Proyecto |
| 15 | Dask | Proyecto |
| 16 | **Evaluación del proyecto final** | Proyecto de integración |

## Evaluación (lo que el PDA fija)

| Componente | Peso |
|---|---|
| Primer taller (teórico y práctico) | 25 % |
| Segundo taller (teórico y práctico) | 25 % |
| Presentaciones y quizzes | 10 % |
| Proyecto de integración de conceptos | 40 % |

Notas de 0,0 a 5,0 en múltiplos de 0,1. La asignatura se pierde con **20 % de fallas o más**.

## Bibliografía

- **Texto guía:** Khattak, Buhler y Erl (2016), *Big Data Fundamentals: Concepts, Drivers & Techniques*, Pearson.
- **Complementaria (selección):** Rajaraman, Leskovec y Ullman, *Mining of Massive Datasets* (2011); Ryza et al., *Advanced Analytics with Spark* (2015); Pentreath, *Machine Learning with Spark* (2015); White, *Hadoop: The Definitive Guide* (2012); Dollimore, Kindberg y Coulouris, *Distributed Systems: Concepts and Design*; Erl, Mahmood y Puttini, *Cloud Computing: Concepts, Technology & Architecture* (2013). La lista completa está en el PDF.

## Diferencias a reconciliar con el curso 2026-2S

Son diferencias observables entre el PDA 2023-I y `lms/data/course.json`; **no se resuelven aquí**, se llevan al docente.

| Tema | PDA 2023-I | Curso 2026-2S (`course.json`) |
|---|---|---|
| Talleres de evaluación | Sesión 6 (ETL) y sesión 10 (Map-Reduce) | Un taller de control en la sesión 8 (pipeline SECOP, API, concurrencia y NoSQL) |
| Hadoop / Map-Reduce | Sesiones 8–10 | No aparece entre las sesiones 1–9 visibles |
| Búsqueda | Elasticsearch en la sesión 13 | Búsqueda (BM25, semántica y vectorial) en las sesiones 7 y 9 |
| Peso de evaluación | 25 / 25 / 10 / 40 | Por confirmar en el libreto docente (`.local-docente/`) |
| Sesiones 10–16 | Definidas | En borrador (`draft`) |

**Decisión pendiente para el docente:** confirmar si el PDA vigente de 2026 mantiene los porcentajes 25/25/10/40 y la lista de temas, y subirlo para reemplazar este resumen.
