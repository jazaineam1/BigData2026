# Implementación de mejoras · avance verificable (26 de noviembre de 2026)

## Estado
No se declara finalizado el curso ni aprobada ninguna sesión bajo el estándar de 40.000 palabras originales, 25 diapositivas sustantivas, laboratorio real, ensayo de 150 minutos y rúbrica ≥4,5/5. La implementación añade trabajo real y conserva materiales canónicos y rúbricas. No se fusionó ni publicó en main; las ramas especializadas de estudiantes se conservaron intactas.

### Cambios efectivamente guardados
- Revisión y actualización semántica de los 102 destinos de laboratorio; 21 brechas iniciales señaladas explícitamente y las nuevas ampliaciones ligadas a sus secciones. No se afirma que todos los destinos constituyan una actividad ejecutada.
- Agendas diferenciadas de 150 minutos para 17 sesiones; S02 corrige el cronograma previo de 180 minutos. No es tiempo observado.
- 17 nuevos laboratorios de navegador con cálculo real, modificación de entradas, predicción, tabla de resultados intermedios, interpretación y reto autónomo. Se preservan 17 controles previos y 68 comparaciones precalculadas, que no cuentan como experimentos ejecutados. Datos didácticos sintéticos declarados.
- 12 cuadernos canónicos ampliados con 2 celdas nuevas cada uno (explicación y código visible), más 2 bloques Python integrados en la presentación para S11/S13, reutilizables en sus Codespaces. S08/S12/S16 conservan cuadernos evaluativos sin cambios y reciben solo repaso no evaluativo y corrección de orden.
- Los nuevos ejercicios incluyen operaciones auténticas locales de Python, SQLite, hashing, lectura/relectura y concurrencia. Las rutas opt-in MongoDB/Atlas/CQL/Elasticsearch/Spark/Databricks, Whisper y Dask no fueron ejecutadas aquí; no se sustituyen por simulaciones para acreditarlas. Los benchmarks grandes permanecen manuales.

| Sesión | Laboratorio nuevo de navegador | Ampliación de cuaderno o protección de evaluación |
|---|---|---|
| S01 | Paginación: cobertura por identidad | Laboratorio ampliado · Paginación, cobertura y RAW releíble (celda 85) |
| S02 | Dimensionar requisitos de arquitectura | Laboratorio ampliado · Contrato de datos y restricciones ejecutables (celda 41) |
| S03 | Predicados sobre arrays | Laboratorio ampliado · Índices y explain controlado (celda 130) |
| S04 | Faltantes y bandeja | Laboratorio ampliado · Persistencia, reconexión y bandeja (celda 39) |
| S05 | Query-first: diseñar buckets | Laboratorio ampliado · Dos patrones de consulta CQL (celda 82) |
| S06 | Caminos y nodos únicos | Laboratorio ampliado · Integridad y exportación de un subgrafo (celda 119) |
| S07 | BM25: frecuencia, rareza y longitud | Laboratorio ampliado · BM25, análisis y explicación del resultado (celda 31) |
| S08 | Repaso de cobertura y concurrencia en biblioteca | Repaso no evaluativo integrado |
| S09 | Fusión RRF y relevancia | Laboratorio ampliado · RRF y relevancia sobre el mismo universo (celda 21) |
| S10 | Onda, RMS y frecuencia observada | Laboratorio ampliado · Threads, mismo corpus y verificación de bytes (celda 48) |
| S11 | Segmentación temporal sin pérdida | Ampliación de código · audio largo con cobertura y offsets |
| S12 | Repaso: reconciliación de inventario de museo | Repaso no evaluativo integrado |
| S13 | MapReduce: estados parciales y carga | Ampliación de código · una regresión logística con gradientes por lote |
| S14 | Join y cardinalidad | Laboratorio ampliado · Cardinalidad de join y equivalencia de estrategias (celda 71) |
| S14A | Matriz de confusión y umbral | Laboratorio ampliado · Preflight de entrenamiento y evidencia de capacidad (celda 28) |
| S15 | Recuperación: checkpoint y escritura | Laboratorio ampliado · Fallo inyectado, replay y equivalencia de estados (celda 19) |
| S16 | Repaso: grano de integración | Repaso no evaluativo integrado |

### Pruebas y límites
17 resultados de referencia y 51 configuraciones iniciales/extremas de los nuevos cálculos JS comprobados antes de guardar. 12 controles de Python reproducidos localmente a partir de los fragmentos de los cuadernos (rutas default, no ejecución íntegra del ipynb ni de ramas remotas); se corrigió cierre explícito de SQLite S04/S15. En S11, la referencia local segmentó una señal PCM sintética de 73 s en cuatro ventanas con cobertura completa. En S13, la referencia secuencial entrenó un modelo logístico único con gradientes de 8 lotes de 1.000 filas sintéticas, 20 épocas; pérdida inicial 0,693147, pérdida en última época 0,352416, accuracy en test sintético independiente 0,907. No se ejecutó Dask, no se acredita ML a escala ni generalización a SECOP. No se clonó el repo en el entorno local porque no hay resolución DNS a GitHub; el acceso y la escritura fueron mediante la integración GitHub. Las referencias locales no sustituyen el ensayo del cuaderno completo desde entorno limpio. Las pruebas de interfaz se limitan a sintaxis y DOM simulado; falta navegador real, proyección y evaluación con estudiantes.

### Pendiente no negociable
Acreditar 40.000 palabras elegibles por sesión mediante auditoría individual deduplicada de presentación y cuaderno; no hay certificación de extensión y no se infló el conteo. Desarrollar más mecanismos y ejemplos, realizar las pruebas de motores reales, ensayar las agendas y aplicar la rúbrica de aceptación. Los 17 laboratorios nuevos cubren un mecanismo prioritario por sesión; no constituyen todos los experimentos ni un laboratorio E2E certificado. Las ampliaciones de S11/S13 están en presentación, no en notebooks de ramas de estudiantes, para evitar alterar entornos publicados sin revisión. Los talleres conservan criterios y productos originales. No publicar como curso final.

## Verificación posterior de archivos guardados
Se reconstruyó el HTML desde fuentes releídas y coincidió byte a byte. En DOM simulado se recorrieron 425 pantallas, 17 índices, 148 opciones de comparaciones anteriores, 51 ejecuciones de laboratorios nuevos (inicial, mínimo y máximo) y 25 accesos a ampliaciones; se comprobó existencia de tablas calculadas y retorno a diapositivas. La presentación conserva 19 avisos explícitos de brechas técnicas o de evidencia. Estos avisos no son una lista exhaustiva de los pendientes del plan. Se corrige la regla CSS que mostraba lectura ampliada pese a estar cerrada en móvil; pendiente inspección en navegador real. Sin certificación de 40.000 palabras, ni de ejecución integral, ni de tiempo en aula.
