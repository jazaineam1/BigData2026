# Taller de Control 2 · Revisión contra PDA 2026-2 y repositorio estudiantil existente

**Estado:** corrección curricular del PR #145, **no publicar el cuaderno previo de BM25/E5 como Taller 2** hasta sustituir su centro evaluativo. Documento basado en el PDA institucional `PDA_2026-02_BIGDATA.pdf` (5 páginas) y `docs/PDA_guia.md`, junto al TC1 V9.

## 1. Resolución de los dos errores

1. **Peso real:** el PDA 2026-2 establece **Taller 1 = 20 %, Taller 2 = 20 %, quices = 20 %, laboratorio en casa = 10 %, proyecto final = 30 %**. El dato antiguo de 25 % procede de otra versión del PDA y se descarta para diseñar TC2. El PDF está firmado para **grupo 1**, no para el grupo 2; comprobar aplicabilidad administrativa del mismo PDA, pero no inventar otra distribución.
2. **Tema real:** sesión 10 = ETL con imágenes; sesión 11 = ETL con audio y video; sesión 12 = **segundo taller: implementación de procesos de ETL**. El taller propuesto anteriormente distribuye 60/100 puntos entre BM25, E5 y RRF, por lo que **no cumple la centralidad ETL**. Su código puede sobrevivir como herramienta de recuperación opcional, pero no como núcleo evaluativo.
3. **Restricción docente vigente:** hasta **lo trabajado en la sesión 10 del grupo 2**. Ese material incluyó imágenes y audio. **No evaluar video, Dask, Spark ni Airflow como requisitos del TC2**. Video pertenece a S11 del PDA del grupo 1; explicitar que se trata de una adaptación y no de cumplimiento literal de toda la secuencia.
4. **Entrega:** los estudiantes **ya poseen repositorios GitHub de trabajo**. Nunca obligar a crear un segundo repositorio. Usar el **mismo repositorio GitHub de la pareja/proyecto**, una rama `taller/tc2-etl`, carpeta `talleres/TC2/` y un Pull Request hacia su propia rama principal. Si una pareja ya usa otra ruta/convención, conservarla siempre que identifique claramente la entrega, el commit y los tres artefactos. Compartir el enlace del PR/commit y la huella por correo institucional, como TC1. Se ha localizado `jazaineam1/BigData2026-Verificacion-S3` como repositorio **docente privado de práctica**: no asumir que es el repositorio privado de todas las parejas ni forzar subir entregas allí.
5. **Plazo definido por el profesor:** sábado **14 de noviembre de 2026 a las 23:59:59 hora de Bogotá (UTC−5)**, final del día 14. Es una fecha de entrega administrativa, distinta de las fechas programadas en el PDA grupo 1.

## 2. Competencia evaluable

**Laura recibe un conjunto heterogéneo de imágenes y audios auténticos**, y debe construir una línea ETL trazable desde la fuente hasta un catálogo consultable que permita interpretar los datos sin atribuciones falsas.

La práctica usa **fuentes y datos ya preparados**: imágenes del material S10 con permiso de uso o imágenes generadas/autorizadas, diez voces auténticas MINDS14 es-ES CC BY 4.0 y sus metadatos. No exigir descargar SECOP ni crear bases de datos convencionales, porque eso ya se evaluó en TC1. La relación imagen→registro debe existir en el manifiesto, no suponerse. Las voces MINDS14 no pertenecen a SECOP ni a noticias de El Tiempo.

**Mapa del producto:** extraer bytes y metadatos → inspeccionar formato real → transformar imágenes y audio → registrar medidas → cargar un catálogo multimedia (JSONL/Parquet, eventualmente servicio gratuito si el curso lo ha enseñado) → reabrir y consultar por identificador → probar una corrupción y recuperación → paquete y defensa de decisiones con resultados propios.

## 3. Rúbrica corregida: 100 puntos (aporte del TC2 a la asignatura = 20 %)

| Etapa | Qué demuestra | Controles de puntuación | Puntos |
|---|---|---|---:|
| E1 · Extraer | Identificación de 2 fuentes distintas, archivo real vs extensión y procedencia explícita; sin volver a calificar ingesta SECOP | Fuente y licencias 5, inspección de bytes y decodificación 5, selección de activos verificables 5 | **15** |
| E2 · Transformar imágenes | RGB y luminancia, dos transformaciones con efecto comprobable, histograma interpretado, recuperación visual de información necesaria | Lectura de señal 8, transformación reproducible 10, contraste de legibilidad y límites 7 | **25** |
| E3 · Transformar audio | Decodificación real, forma de onda, duración y RMS, FFT/espectrograma, una variación de ventana y contraste con transcripción de referencia | Decodificación/códec 7, rasgos calculados en 10 WAV 10, experimento e interpretación 8 | **25** |
| E4 · Cargar y consultar | Un **catálogo único** con tipos de activo y procedencia; volver a cargarlo y responder una pregunta con sus registros (no solo serializar un JSON) | Estructura y carga 7, relectura e integridad referencial 5, consulta reproducible 3 | **15** |
| E5 · Calidad y recuperación | Reejecución idempotente de multimedia, detección de transformaciones erróneas y recuperación ante una falla controlada (no volver a calificar descargas SECOP) | Idempotencia 6, prueba negativa 5, restauración verificada 4 | **15** |
| E6 · Decisión final | Selección de un perfil y un límite concreto con números/IDs del equipo; evidencia versionada | Defensa estructurada y trazabilidad del resultado 5 | **5** |
| **Total** | **Sólo ETL multimodal aprendido hasta S10** | | **100** |

**No calificar BM25, E5, Atlas remoto ni RRF** en el TC2: ya son logros de S07/S09 y pueden ser recursos de consulta final sin puntuación específica. Tampoco puntuar la simple creación del repositorio, la firma SHA o el ZIP como competencias nuevas: son requisitos de trazabilidad de entrega.

## 4. Diseño de experiencia de aprendizaje a la profundidad del TC1

Objetivo editorial: **seis etapas encadenadas** con portada, problema de Laura, mapa, definiciones contextualizadas, mini ejemplo manual, ejemplo aplicado, una celda `COMPLETA` por habilidad central, predicción antes de ejecutar, dos perfiles/alternativas, resultado visible, cuatro rótulos («Cómo se lee», «Qué nos dice», «Qué NO permite concluir todavía», «Qué error común»), checkpoint por etapa, recuperación de errores y entrega. No forzar 91 celdas; igualar profundidad y trabajo real, no longitud artificial.

**Prácticas de cada etapa:**
- E1: detectar un archivo cuyo sufijo no coincida con bytes reales; no penalizar al estudiante por detectar una anomalía.
- E2: trabajar con una imagen autorizada, elegir perfil de tamaño y brillo, medir tamaño y legibilidad; indicar qué dato haría falta para afirmar que una fotografía contiene cierta información.
- E3: usar diez WAV licenciados, cambiar una ventana FFT de 512 a 1024 en el mismo audio y contrastar RMS/espectrograma con referencia de texto. No afirmar transcripción ASR sin ejecutarlo.
- E4: registrar `asset_id`, `source_kind`, `source_record_id`, `media_type`, `license`, `original`, `derived`, medidas y estado; reabrir JSONL/Parquet y resolver consultas de forma reproducible.
- E5: reejecutar sin duplicar catálogos ni modificar originales, provocar un error seguro sobre derivado y reconstruirlo.
- E6: seleccionar una decisión fundada por números propios y una alternativa descartada, y un límite verificable; crear expediente final.

## 5. Repositorio existente de los estudiantes: instrucciones correctas

**No pedir «New repository».** El estudiante entra a su repositorio que ya creó durante el curso. Si el repositorio es un fork público del material docente, **no publicar ahí** sus nombres, códigos ni archivos privados: usar una ruta privada aprobada del mismo proyecto o garantizar que los artefactos publicados sean anonimizados. No crear repositorios adicionales por defecto.

1. Abrir **el repositorio existente de su pareja** y comprobar el nombre, propietario y permisos.
2. Crear rama `taller/tc2-etl` desde su trabajo previo, sin borrar los hitos del proyecto.
3. Agregar `talleres/TC2/TC2_<PAREJA>.ipynb`, `talleres/TC2/TC2_<PAREJA>.zip` y `talleres/TC2/manifest_tc2.json`. Evitar secretos/PII en repos públicos.
4. Registrar los cambios con **commit** verificable y abrir **PR en su propio repositorio** desde la rama TC2 a `main`; no modificar la rama `main` del docente.
5. Enviar desde correo institucional el enlace al repositorio ya creado y al PR/commit, integrantes y SHA-256 del manifest. Si el repositorio es privado, comprobar que el docente tiene acceso (cuenta GitHub institucional por confirmar, no inventar cuál).
6. Considerar entregado antes de las **23:59:59 de Bogotá del 14-11-2026** cuando están presentes los archivos, el commit y el correo; los archivos y el enlace se revisan en el estado del commit de cierre.

**Alerta de operación:** el archivo ZIP de 10 WAV puede superar límites de carga desde la web si se incluyen fuentes grandes. Mantener sólo el material autorizado y necesario; ofrecer Git/LFS si procede, pero no exigir compras ni cuentas adicionales.

## 6. Acciones técnicas para completar antes de publicar

- [ ] Sustituir `Cuadernos/Taller_Control_2.ipynb` que evalúa BM25/E5 por un cuaderno cuyo flujo **sea ETL** y cuyos puntos sigan la tabla anterior; dejar el documento previo como borrador/no aprobado.
- [ ] Reutilizar las funciones de imagen/audio y los contratos del cuaderno `11_ETL_Audio_Imagenes.ipynb` **sólo** para capacidades efectivamente enseñadas hasta S10.
- [ ] Adaptar `utils/tc2_core.py` y `utils/validate_taller_control_2.py`: puntos 15/25/25/15/15/5, verificaciones de archivos reales y consulta de catálogo; simular fallos de transformación, no de SECOP.
- [ ] Modificar `assets/tutoriales/tc2-paso-a-paso.html`: usar repositorio existente, fecha/hora, PR propio, sin crear otro.
- [ ] Validar end-to-end con datos licenciados, notebook de estudiante limpio y calificador de ZIP externo; probar GitHub en modo público anonimizante y privado restringido.
- [ ] Conciliar el PDA del **grupo 1** con el plan aprobado para **grupo 2** antes de publicar la calificación institucional del 20 %.
- [ ] Fusionar PR y abrir la actividad en LMS sólo cuando los criterios anteriores estén satisfechos.

## 7. Fuentes

- PDA auténtico: `PDA_2026-02_BIGDATA.pdf` p. 1–5: método evaluativo y S10–S12.
- Guía actualizada: `docs/PDA_guia.md` (corrige el error histórico de 2023).
- Primer taller: `Cuadernos/Taller_Control_1.ipynb` (V9).
- Ruta docente de GitHub: `infraestructura/git-ejemplo/README.md`.
- Laboratorio multimedia ya existente: `Cuadernos/11_ETL_Audio_Imagenes.ipynb`.
- Repositorio docente de práctica: `jazaineam1/BigData2026-Verificacion-S3` (privado; no confundir con las copias/repositorios de estudiantes).
