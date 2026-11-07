# TC2 · Revisión pedagógica V6 y plan de mejora implementado

**Universidad Central · Maestría en Analítica de Datos · 2026-2S**
**Documento de control de calidad público:** contiene criterios, no soluciones individuales.
**Fecha de entrega corregida el 7 de noviembre de 2026:** domingo 15 de noviembre de 2026, 23:59:59, hora de Bogotá. La rectificación sustituye el sábado 14 informado inicialmente; no altera la rúbrica ni los productos exigidos.
**Ponderación del PDA 2026-2 de referencia:** segundo taller ETL, 20 % (verificar adopción formal del PDA del grupo 2).

## Dictamen y comparación con el TC1

| Regla del Taller 1 | Taller 2 V6 |
|---|---|
| Historia y problema persistentes (Laura/Compras Claras) | Cuatro actos: encontrar → leer → escuchar → auditar |
| Una pregunta por etapa y producto observable | E1 BM25, E2 E5/Atlas, E3 pertinencia/RRF, E4 OCR, E5 ASR, E6 ETL |
| Explicación + ejemplo manual + práctica propia | Guía de 8 apartados desplegables y notebook con mini ejemplos |
| Un solo hueco `____` por ejercicio | Ocho funciones `return ____` con `assert` y retroalimentación |
| Cuatro rótulos fijos al interpretar una salida | Checkpoints E1–E6: cómo se lee, qué nos dice, qué no permite concluir, qué error común |
| Rúbrica visible de 100 puntos y niveles observables | 24 controles; máximo sin cambios, niveles sin evidencia/parcial/completo en controles pertinentes |
| Evidencia y defensa, nunca prosa abierta | Decisiones estructuradas, resultados del caso propio, hashes, ZIP y PR |
| Colab y checkpoints que permiten retomar | Preparación por etapa, respaldo de Drive opcional y guía de recuperación |
| No calificar plataformas que no funcionan | Atlas permite ruta local con créditos propios y contingencia acreditada por docente |
| Los tiempos no están en el notebook | Mapa sin relojes; cronograma docente externo al recurso |
| Dos recursos por sesión | Notebook Colab + guía interactiva (41 comprobaciones) |
| Seguridad y validación antes de publicación | CI offline, E2E, auditoría adversarial, navegador y GitHub Pages |

El TC2 no vuelve a calificar ingesta SECOP, modelamiento documental, Cassandra o Neo4j del TC1. La fuente SECOP se recibe preparada, con cinco consultas pedagógicas asignadas por pareja. OCR se ejecuta sobre tres versiones de un gráfico propio de ranking y Whisper tiny sobre diez grabaciones MINDS14 es-ES. Estas voces **no** están relacionadas con los expedientes; esta limitación se declara y se evalúa.

## Criterios verificables de puntuación parcial

Los 24 controles conservan el máximo original y totalizan 100. Se incorporaron niveles parciales explícitos para E1.1 (2/3), E2.2 (3/5), E3.1 (2/4), E3.2 (2/4), E4.4 (4/6), E5.4 (3/6), E5.5 (1/2), E6.2 (3/6) y E6.5 (3/5). E2.3 conserva 2/4 si se declara ruta local en lugar de Atlas real. La justificación de cada nivel consta en el notebook y en la retroalimentación del evaluador.

**Equidad Atlas:** cuando el proveedor presenta una indisponibilidad documentada, el docente (no el estudiante) puede aplicar `--atlas-contingencia-confirmada` al calificar el ZIP. La opción exige un error de Atlas registrado en `E2/semantica.json`; acredita el nivel institucional excepcional **sin afirmar que se ejecutó Atlas**. No se acepta el argumento si el equipo eligió no intentarlo y no documentó error.

## Auditoría de autenticidad, privacidad y límites

El SHA-256 prueba integridad de bytes, pero **no** demuestra por sí solo que se haya ejecutado Tesseract o Whisper ni que el código sea autoría individual. Se incorpora `utils/tc2_media_audit.py` para que el docente pueda volver a inferir, desde los medios del ZIP, OCR en dos perfiles legibles y ASR en diez WAV. La opción del corrector `--audit-media` compara contenido, admite diferencias menores entre entornos, identifica contradicciones y marca controles para revisión humana. No afirma prevenir toda copia de resultados de otros equipos.

Las ocho soluciones de una línea dejaron de estar reunidas en una tabla lista para pegar. El E2E utiliza exclusivamente un adaptador de pruebas que **no está definido en Colab**. Un repositorio público no es un sistema de secreto: las operaciones matemáticas son transparentes y el aprendizaje se valida principalmente por resultados del caso, interpretación de límites y revisión del docente, no por ocultar una fórmula.

El notebook y ZIP incluyen nombres y códigos; la entrega sigue en el **repositorio preexistente y privado** del equipo, en `talleres/TC2/`, con PR y correo institucional. No se exponen claves ni URIs privadas. Al auditar, los archivos se extraen mediante un lector de ZIP con límites y protección frente a traversal.

## Pruebas y aceptación

- [ ] Ejecución offline: 24 controles / 100, coincidencia del motor `utils/tc2_core.py` con el embebido en el notebook, 8 huecos únicos, 4 rótulos por checkpoint y 41 casillas en la guía.
- [ ] Prueba adversarial: las predicciones OCR y ASR falsas provocan discrepancias frente a una segunda inferencia; los niveles auditados se recalculan.
- [ ] E2E real: Tesseract en tres PNG, Whisper sobre diez WAV, WER por fuente, catálogo de 13 activos, ZIP, `--audit-media` y equivalencia de puntuaciones; ruta local Atlas mantiene 98/100.
- [ ] Entrega: ZIP dentro del límite de carga web GitHub, notebook ejecutado y manifest externo, con SHA coincidente.
- [ ] Interfaz: responsividad 390/768/1366, modo oscuro, 41 checks, teclado, ocho secciones de ejemplos desplegables, WCAG en guía y contrato LMS universal V5.
- [ ] Fusión y despliegue GitHub Pages; comprobar que en la portada S12 lleva al notebook y guía definitivos.

No se declara una puerta como aprobada antes de que termine su ejecución en Actions.

## Riesgos que no se pueden eliminar solo con código

1. **Colab gratuito:** los recursos, cuotas y disponibilidad de GPU/CPU no están garantizados. Se usa CPU y se habilita continuidad tras descarga; se recomienda realizar un piloto humano con cuentas sin caché.
2. **Atlas temporal:** proveedor externo y API experimental; no puede exigirse que cada cuenta consiga el mismo resultado de red.
3. **Pruebas públicas:** ninguna rúbrica automatizada pública certifica autoría individual. La defensa estructurada y la inspección docente son necesarias.
4. **Datos heterogéneos:** OCR trabaja sobre una imagen generada desde resultados, no sobre PDF escaneado; ASR procesa MINDS14, no una nota periodística real. La integración es de formatos/procedencias, no una supuesta relación semántica entre fuentes.
5. **Tiempo:** el notebook tiene 111 celdas, más trabajo que el TC1 (81). Se debe asignar tiempo autónomo y probarlo con al menos un estudiante individual; CI no mide el tiempo humano de lectura/depuración.

## Control de cambios y política de no perjuicio

Este ajuste V6 **no cambia** fecha, porcentaje PDA, máximo de rúbrica, fuente licenciada, cantidad de audios ni tres entregables. Añade niveles parciales que favorecen a quienes hicieron evidencia verificable incompleta, mejoras de interpretación y una auditoría adicional del docente. Los trabajos iniciados en V5 conservan sus condiciones académicas; cualquier incidente por cambio técnico de versión debe resolverse sin penalizar el aprendizaje demostrado.

**Nombres de recursos finales:** `Cuadernos/Taller_Control_2.ipynb` y `assets/tutoriales/tc2-paso-a-paso.html`.
