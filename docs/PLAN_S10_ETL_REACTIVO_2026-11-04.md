# S10 · ETL reactivo de imágenes y audios — plan docente y guía reproducible

**Universidad Central · Maestría en Analítica de Datos · Big Data 2026-2S**

## Alcance

Es una ampliación **de la sesión 10 existente**. No agrega otra sesión, recursos LMS adicionales, orquestación, Spark, OCR ni transcripción obligatoria. Los dos recursos oficiales continúan siendo la presentación S10 y el cuaderno Colab S10; la aplicación se abre mediante un enlace integrado en la presentación (navegación y diapositiva 23).

### Caso y producto

**Pregunta:** ¿Cómo convertir archivos de imagen y audio en un catálogo consultable sin perder los originales, y cómo demostrar que los resultados se pueden guardar y verificar?

**Producto autónomo:** ZIP con originales en raw/, derivados en derived/, catalogo.jsonl y manifest.json. La importación de este ZIP vuelve a comprobar CRC y SHA-256, restaura los originales y los parámetros de proceso.

### Archivos

- Aplicación: assets/s10/etl-reactivo.html
- Presentación: Presentaciones/s10-imagenes-audio.html
- Cuaderno oficial (no se reemplaza): Cuadernos/10_Imagenes_Audio.ipynb
- Pruebas: tests/s10-etl-reactivo.spec.js

Tras fusionar y desplegar GitHub Pages, la URL prevista es:
https://jazaineam1.github.io/BigData2026/assets/s10/etl-reactivo.html

Antes del merge, esta ruta pública aún no es la nueva aplicación.

## Matriz E → T → L

| Etapa | Imágenes | Audios | Evidencia |
|---|---|---|---|
| E | Carga PNG/JPG/WEBP local; conserva RAW | Carga WAV/MP3, o ejemplo creado localmente | Nombre, tipo, tamaño, SHA-256 original |
| T | Escalar a 160/320/640/1024, brillo, contraste, gris, umbral, histograma 8 bandas | Decodificar a PCM16 WAV mono 16 kHz, RMS, pico, duración, cruces por cero | Derivado, parámetros, métricas, SHA-256 derivado |
| L | Guardar derivado PNG + catálogo | Guardar derivado WAV + catálogo | JSONL, manifiesto y ZIP estándar |
| Verificar | CRC + SHA-256 al reabrir el ZIP | CRC + SHA-256 al reabrir el ZIP | PAQUETE VERIFICADO / PAQUETE RECHAZADO |

La descripción automática es estrictamente **técnica**: dimensiones, brillo, histograma, duración o amplitud. **No** identifica objetos, personas, contenido hablado, hechos contractuales, ni evalúa precisión de OCR o ASR.

## Tutorial autónomo del estudiante (dentro de la aplicación)

1. **Crear ejemplo**: un clic produce una imagen y una señal acústica de prueba sin voz humana. Como alternativa, subir una imagen/audio autorizados desde el equipo. Evidencia en demo: E: 2 archivos recibidos; T: 2 derivados correctos; L: 2 filas en memoria. Si no tiene archivos, la demo desbloquea todo el tutorial.
2. **Extraer**: leer nombre, procedencia, peso y SHA-256 original. El hash demuestra igualdad de bytes, no autenticidad de una fuente editorial.
3. **Transformar**: cambiar solo el lado máximo (320 → 160) y observar nueva imagen y medidas, conservando el mismo original. Probar brillo, contraste, escala gris, umbral. En audio, escuchar la salida, observar onda, duración, RMS y WAV 16 kHz. RMS NO equivale a una transcripción.
4. **Cargar**: consultar tabla. Una fila corresponde a un activo, su modalidad, la fuente, los parámetros y el derivado. Identificar tamaño y hash original frente a derivado.
5. **Guardar**: pulsar Guardar ZIP verificable. Con Reabrir ZIP seleccionar ese mismo archivo y comprobar la confirmación PAQUETE VERIFICADO. El archivo está en la carpeta de descargas del estudiante, NO se envía a LMS ni Drive automáticamente.
6. **Comparar**: seleccionar tipo de contenido y límite desde opciones cerradas. Cambiar un parámetro, guardar otro ZIP, explicar a partir de las mediciones qué cambió y qué permaneció inmutable.

**Error recuperable:** un audio cuyo códec no decodifique el navegador informa un fallo explícito; usar el WAV de demostración. Se admiten máximo 6 archivos de 8 MiB cada uno, 20 MP por imagen y 60 s por audio.

## Libreto del docente · 180 minutos

| Minutos | Actividad |
|---:|---|
| 0–15 | Problema: por qué conservar el original y su procedencia |
| 15–40 | Conceptos E/T/L, activo, RAW, derivado, catálogo, SHA |
| 40–65 | Demo desde cero, sin instalación; abrir archivo y hacer E |
| 65–95 | Variar un parámetro en imagen y analizar un WAV |
| 95–105 | Descanso |
| 105–135 | Transferencia: imagen/audio propio con permiso y segundo perfil |
| 135–158 | L: catálogo, manifiesto, ZIP, reimportar y verificar |
| 158–175 | Errores controlados: imagen incompatible o archivo demasiado grande |
| 175–180 | Cierre: distinguir una métrica de contenido semántico |

## Integración y replicabilidad

La herramienta es una sola página HTML/CSS/JavaScript, sin llamadas a un backend ni dependencia CDN. Usa Canvas, Web Audio y Web Crypto en navegador moderno. No expone archivos al servidor ni guarda automáticamente información privada en un almacenamiento compartido. El ZIP es local, portable y verificable. El estudiante puede extraerlo con cualquier descompresor común, leer catalogo.jsonl y repetir la ejecución con los RAW.

El catálogo del navegador es JSONL, no Parquet. El cuaderno oficial Colab continúa trabajando JSONL/Parquet y el corpus MINDS-14 de diez voces. No presentar esta página como sustituto del cuaderno académico ni como evidencia registrada en Supabase.

## Pruebas y liberación

1. Ejecutar pruebas Playwright de ejemplo, carga de imagen propia, cambios reactivos, rechazo de archivo demasiado grande, ZIP y reimportación, portátil y móvil.
2. Hacer una prueba manual con un JPEG real y un WAV propio, desde Chrome y con teclado.
3. Comprobar que no cambió la cantidad de 23 diapositivas ni los enlaces Colab existentes.
4. Fusionar PR solo tras superar QA; GitHub Pages ya copia assets/ en su build.
5. Verificar HTTP 200 de la aplicación y enlaces desde la presentación.
6. No registrar un tercer recurso LMS ni alterar notas, historial o entregas.

## Extensiones, no incluidas en este alcance

- Parquet mediante Colab o implementación local opcional.
- ASR/OCR con modelos reales, conjuntos de referencia y métricas de error, sin inventar contenido.
- Persistencia académica autenticada mediante backend oficial, solo después de diseñar permisos y contratos de evaluación.
