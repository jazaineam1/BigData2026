# Mejoramiento pedagógico integral · rama de revisión

## Qué incorpora esta versión
- Explorador común de las 17 rutas (S01–S16 y S14A), con 68 estaciones, cálculos interactivos por tema, 17 preguntas con retroalimentación, 17 fragmentos de código formativos y retos de modificación.
- Cada ruta enlaza el cuaderno original y material conceptual existente. El progreso es local, no oficial. S11 y S13 conservan ramas estudiantiles para no duplicar datos.
- S15: cuaderno nuevo de pipeline incremental, transacción, rollback, checkpoint e idempotencia con SQLite y datos sintéticos; ampliación voluntaria con Spark Structured Streaming local y checkpoint de archivos. Sin nota y sin activar el borrador en course.json. La ampliación Spark no está probada en este entorno.
- Portada: corrige 24 controles TC2 y descripción S13; añade acceso a rutas. LMS: acceso a ruta y S14A desde S14, sin cambiar el backend ni el registro oficial.
- Proyecto final: solo corrección editorial de estado; rúbrica intacta.

## Uso en revisión
Con el repositorio en esta rama, desde su raíz: `python -m http.server 8000`. Abrir `http://localhost:8000/Presentaciones/ruta-aprendizaje.html?s=01`. El selector recorre todas las sesiones. GitHub Pages sigue publicando main; no activar despliegue de esta rama.

## Criterios de aceptación y deuda
Esta intervención añade una capa de navegación, experimentos y práctica. Integra un bloque formativo plegable en 11 cuadernos de aprendizaje (12 archivos por copia histórica de S02), preservando orden, celdas de código y evaluaciones. Los generadores identificados invocan un helper idempotente. No reestructura todos los contenidos históricos, no reemplaza sus presentaciones, ni verifica cuentas externas. Los fragmentos son complementarios; no deben confundirse con resultados reales de bases, clústeres ni fuentes. Para la siguiente iteración, profundizar en el orden interno de cada sesión, verificar en Colab/Codespaces/Databricks, confirmar regeneración de todos los cuadernos y realizar QA visual. No cambiar evaluaciones históricas ni exigir servicios pagos.

## Verificación
`node utils/validate_pedagogia.js` (sin dependencias, sin descargas ni benchmarks).
`python utils/validate_s15_pipeline.py` (solo biblioteca estándar y datos pequeños, no servicios externos).
`python utils/validate_pedagogia_notebooks.py` (sintaxis, bloques idempotentes y experimentos pequeños; no necesita nube).
Los experimentos de S14A grandes se ejecutan manualmente solo con cuota disponible; registrar escala, versiones, duración y resultado real, no inferir ejecución por estimaciones.
