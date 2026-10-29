# Auditoría técnica, visual y pedagógica — S09 y S10

**Curso:** Big Data, Maestría en Analítica de Datos, Universidad Central · 2026-2S  
**Fecha de auditoría y publicación:** 29 de octubre de 2026 (America/Bogota)  
**Estado:** ambos PR integrados en `main`, LMS actualizado y GitHub Pages desplegado con prueba de humo aprobada.

## 1. Alcance y criterio de publicación

Se revisaron las sesiones como dos laboratorios **aprender haciendo**. Cada estudiante debe guardar su copia en Colab, ejecutar celdas, predecir resultados, modificar **una variable a la vez**, observar la diferencia, reconocer límites y conservar un producto verificable.

Se mantienen **dos recursos por sesión**: presentación interactiva con tutorial integrado + cuaderno Python completo. Las casillas de avance son ayudas personales; **no** equivalen a evidencia de ejecución ni nota adicional.

## 2. S09 — búsqueda vectorial (PR #131)

- [PR #131, fusionado](https://github.com/jazaineam1/BigData2026/pull/131).
- [Presentación publicada, desde la diapositiva 21](https://jazaineam1.github.io/BigData2026/Presentaciones/s09-de-palabras-a-significado.html#s21).
- [Cuaderno individual en Colab](https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb).
- 35 diapositivas; tutorial de seis pasos incrustado y disponible directamente desde la diapositiva 21; 21 celdas; redirección del enlace histórico de tutorial.
- Secuencia: documentos SECOP → E5 (`N×384`) → conexión opcional Atlas autorizada → upsert por lote → índice vectorial reutilizable → consulta ANN/ENN o respaldo NumPy explícito → consulta modificada/filtro → expediente JSON individual.
- `EQUIPO` debe ser un alias único antes de conectarse a Atlas; el índice compartido y las reglas de acceso corresponden a usuarios con autorización. Contraseñas introducidas por campo oculto, nunca en argumentos, notebooks ni archivos.
- **Alcance de CI:** sintaxis y pruebas de contratos; modelo/colección *dobles* en QA offline, no conexión a Atlas real. No se debe atribuir al test un rendimiento, relevancia o disponibilidad que no midió.
- **CI final en verde:** [S09 laboratorio reproducible](https://github.com/jazaineam1/BigData2026/actions/runs/40956805307), [QA visual LMS](https://github.com/jazaineam1/BigData2026/actions/runs/40956805207), [Validar LMS](https://github.com/jazaineam1/BigData2026/actions/runs/40956805215), [Higiene de secretos](https://github.com/jazaineam1/BigData2026/actions/runs/40956805216).

## 3. S10 — ETL de imágenes reales (PR #134)

- [PR #134, fusionado](https://github.com/jazaineam1/BigData2026/pull/134).
- [Presentación publicada](https://jazaineam1.github.io/BigData2026/Presentaciones/s10-etl-multimedia.html#s1).
- [Cuaderno individual en Colab](https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/10_ETL_Multimedia.ipynb).
- 17 diapositivas, seis pasos guiados integrados, 29 celdas Python, pantalla móvil y portátil, pruebas de accesibilidad en pantallas representativas.
- Secuencia: snapshot editorial preservado → relación entidad/noticia por `article_id` → RAW inmutable con SHA-256 → dos perfiles Pillow 320/640 → procesamiento por lotes con checkpoint → JSONL y Parquet → consulta por noticia elegida → decisión personal → carpeta completa en Drive para S11.
- **No se infiere que la imagen pruebe vínculo con un contrato**: noticias/entidad son contexto editorial.
- **CI con imágenes reales**, entorno Python 3.12 y dependencias declaradas: 8 archivos → 16 filas (7,1 s); 32 archivos → 64 filas (24,3 s). Se probó repetición sin duplicados, detección y recuperación de un JPEG derivado corrupto, relectura de los catálogos, alternativa propia y copia/restauración verificada en una ruta local simulada. Son tiempos del runner Linux, **no** de Colab ni del aula.
- Se corrigió la dependencia `IPython`, que faltaba al ejecutar en un entorno limpio.
- Se restauró un PDF académico preexistente eliminado accidentalmente por la rama.
- Se extendió el empaquetado Pages para incluir el `webp` real de S10 y comprobar su HTTP 200 en el sitio desplegado.
- **CI final en verde:** [ETL real S10](https://github.com/jazaineam1/BigData2026/actions/runs/40956946187), [QA visual LMS](https://github.com/jazaineam1/BigData2026/actions/runs/40956946222), [Validar LMS](https://github.com/jazaineam1/BigData2026/actions/runs/40956946128), [Higiene de secretos](https://github.com/jazaineam1/BigData2026/actions/runs/40956946149).

## 4. Publicación y LMS

- Commits fusionados: S09 `dd0b08d674aa2777cc30423e51d90196ef680398` y S10 `61635739c2ddde185c61c64d1eff93edc483b060`.
- [GitHub Pages — ejecución de publicación](https://github.com/jazaineam1/BigData2026/actions/runs/40957580632): **success**, incluyendo construcción, vínculos estáticos, despliegue y **smoke test del sitio publicado** (presentaciones, cuaderno S10, recurso fotográfico, LMS y SDK Realtime fijado).
- LMS real actualizado mediante la semilla idempotente `infraestructura/lms/s10-multimedia-seed.sql` tras la publicación. Confirmación con SQL: S10 tiene exactamente **2** recursos visibles, presentación y cuaderno; el antiguo ZIP queda invisible/archivado. Los dos recursos requeridos están activos y el **registro previo de progreso de la presentación** se conservó.
- Fecha registrada para S10: **29 de octubre de 2026, 18:00 de Bogotá** (`starts_at = 2026-10-29 23:00:00+00`).
- No se eliminaron historiales de evaluación o evidencias para realizar esta actualización.

## 5. Evaluación estética y pedagógica

**Aprobado por automatización:** navegación del tutorial, 35 diapositivas S09, 17 pantallas S10, geometría y legibilidad en portátiles/móvil, accesibilidad en vistas seleccionadas, enlaces a cuaderno, trazabilidad del resultado y conservación de la secuencia didáctica.

**Propósito pedagógico:** cada concepto exige una acción; el estudiante altera la consulta, el filtro, el tamaño o la noticia sobre **datos de su propia ejecución**. La salida se lee con cuatro preguntas: qué observé, qué demuestra, qué todavía no demuestra y qué error debo evitar. La ruta corta con ocho imágenes permite recuperación sin sacrificar la cadena E/T/L.

**Límites que no se deben ocultar:**
1. Las pruebas del repositorio **no autentican en Atlas real** con credenciales de cada estudiante ni garantizan IP autorizada, clúster e índice en ese momento.
2. La copia local de S10 **no demuestra una autorización de Google Drive real**. En cada Colab se debe observar `CONSERVADO EN DRIVE` y `COPIA REABIERTA Y VERIFICADA: True` y, idealmente, recuperar la carpeta tras reiniciar el runtime.
3. Los tiempos de CI no son tiempos de la clase. El primer arranque de E5, la red y la autenticación pueden variar.
4. Las pruebas automáticas no demuestran aprendizaje humano ni calidad editorial de todas las imágenes; se recomienda comprobación docente en clase.

## 6. Plan de acción operativo

- **Antes de clase:** comprobar que el clúster Atlas tiene el índice adecuado y accesos individuales listos; evitar comunicar contraseñas. Probar la ruta pública de las dos presentaciones y abrir en Colab ambos cuadernos.
- **Con estudiantes:** cada uno elige alias/copia personal, ejecuta por orden, cambia una variable, contrasta su propio resultado, elige un límite y guarda su evidencia. Si Atlas falla, registra NumPy local como alternativa sin suplantar la consulta remota.
- **Cierre S10:** comprobar carpeta real `MyDrive/BigData2026/S10/<firma>` con `manifest_s10.json`, `outputs/assets.parquet`, RAW, derived y `checks/decision.json`; registrar ruta de S11.
- **Después:** revisar errores y tiempos de la cohorte para adaptar ritmo de enseñanza; no confundir marcas del tutorial con evidencias académicas.

**Veredicto:** materiales, QA automatizada, publicación Pages y configuración del LMS verificados. La ejecución guiada con autenticaciones individuales de Atlas y Google Drive y el cronometraje humano se declaran **pendientes de validación en aula**, no aprobados sin evidencia.
