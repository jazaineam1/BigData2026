# Plan de implementación y liberación — S10 imagen y audio
Fecha: 2026-10-29 · Curso: Big Data 2026-2S · Universidad Central

## Decisión didáctica
S10 estudia **imágenes y audios**, no solo thumbnails. La exposición parte de una misma necesidad profesional: convertir binarios en propiedades consultables sin perder procedencia y sin confundir características con evidencia semántica.

Se respetan los dos recursos visibles del LMS:
1. Presentación-aplicación con explicación, experimentos visuales del navegador y preguntas con retroalimentación.
2. Un cuaderno único en Google Colab, donde **se ejecuta todo el código Python**. No se ejecuta Python dentro de la presentación, ni se exige VS Code.

## Alcance implementado
- Imagen: RGB, dimensión, reducción, luminancia, histograma, transformaciones, dos tamaños verificables.
- Audio: WAV PCM, muestras, duración, escucha, RMS, FFT, espectrograma, silencios, diferencia entre señal y transcripción.
- Evidencia: comparación propia, catálogo JSONL/Parquet, hashes SHA-256, reapertura y manifiesto; carpeta completa opcional en Drive.
- Referencias editoriales: el ejemplo de \`article_id=3530042\` solo demuestra el esquema de unión por metadatos; NO realiza peticiones a El Tiempo.
- Actividades sin respuesta libre, sin nota automática y con opciones estructuradas.

## Restricciones de contenido
Los términos publicados de El Tiempo restringen expresamente análisis, minería, uso automatizado y uso para IA sin autorización escrita. Una URL pública no licencia el audio ni las fotografías. Para una práctica que se pueda publicar y repetir sin depender de terceros, se generan localmente una ilustración y un audio PCM sin voz. Los estudiantes pueden usar sus propios archivos con permiso en las opciones educativas. No hay descarga automática de contenidos editoriales.

## Matriz de QA requerida
1. Validación estructural de presentación y cuaderno (14 pantallas, 32 celdas, dos modalidades).
2. Ejecución íntegra del cuaderno Python en entorno limpio de CI con bibliotecas instaladas.
3. Verificar original PNG, audio WAV, matriz de dos tamaños, región silenciosa, espectrograma, catálogo y hash.
4. Cambiar un derivado intencionalmente en QA: el manifiesto debe detectar error.
5. Playwright: versión escritorio y móvil, controles de imágenes, cambio de ventana de audio, descarga JSON, retroalimentación y enlace.
6. Prueba real en Colab con cuenta y Google Drive aún pendiente de validación presencial (el CI no puede completar autenticación del estudiante).
7. Comprobar desplegado GitHub Pages: URL de presentación, Notebook GitHub y acceso desde la portada.
8. Aplicar semilla SQL del LMS en Supabase tras el merge, comprobar 2 recursos visibles y preservar historiales.

## Liberación y continuidad
- PR a \`main\`; conservar el antiguo notebook de imágenes como archivo histórico, no como tercer recurso exigido.
- CI verde antes de fusionar. No afirmar cobertura de Colab real sin prueba de cuenta.
- Publicar mediante GitHub Pages; ejecutar humo HTTP.
- Luego S11 puede ampliar el mismo catálogo con archivos autorizados reales, lotes, transcripciones y evaluación contra referencia humana.

## Ampliación de audio real (29 de octubre de 2026)

- Se incorpora **PolyAI/MINDS14 es-ES**, conjunto de grabaciones humanas de voz en español con licencia **CC BY 4.0**, accesible en Parquet desde Hugging Face. Se descarga una sola vez en Colab (~39 MB) y se extraen de forma determinista **10 WAV correspondientes a diez intenciones distintas**, guardando huella, duración, identificación de origen, licencia y transcripción de referencia. Se detiene el ejercicio si falta cualquiera de los diez WAV; no se sustituye por señal sintética silenciosamente.
- Audio: escuchar, comparar voces, onda, RMS, tasa de cruces por cero y centroide espectral; ASR opcional con Whisper tiny y evaluación posterior mediante WER sobre una referencia adecuada.
- **Integración con S10 de imágenes anterior:** se lee exclusivamente el manifiesto de las 32 imágenes reales asociadas a 24 noticias, conservando el contrato `article_id`. El inventario del corpus de voz utiliza `source_record_id`; no se inventan coincidencias entre artículos y grabaciones de servicios financieros.
- El catálogo Parquet/JSONL de la actividad contiene **13 filas**: 2 imágenes derivadas del ejemplo original, 1 WAV sintético de explicación y **10 WAV humanos**. Incluye manifiesto de integridad para todos los WAV, procedencia, licencia, catálogo reabierto y copia opcional en Drive.
- Los datos editoriales de El Tiempo NO se descargan automáticamente para ASR ni minería: sus condiciones de uso restringen la extracción y reutilización sin autorización. Los feeds `/servicios/feeds/articulo/{id}` se explican como estructura de metadatos, nunca como licencia de uso.
- QA: pruebas de ejecución end-to-end, exactamente diez WAV únicos con licencia y transcripciones, catálogo de 13 filas, revisión de hashes y detección de alteración de un derivado. **No afirmar éxito de la descarga real hasta que una prueba de red lo verifique.**

Fuente: https://huggingface.co/datasets/PolyAI/minds14/tree/main/es-ES · licencia CC BY 4.0: https://creativecommons.org/licenses/by/4.0/

## Auditoría de autonomía estudiantil y guía de pruebas (29 oct. 2026)

- La presentación anterior (14 pantallas) **no era autoexplicativa**: no guiaba desde la cuenta de Colab a la ejecución, no detallaba cómo comprobar los diez WAV, ofrecía VS Code pese al requisito «solo Colab» y mostraba una unión `article_id` que podía confundir los dos corpus.
- La presentación revisada tiene **23 pantallas**, de las que 12–21 actúan como instructivo desde cero: conectar Colab y guardar copia, instalar bibliotecas, imagen, audio sintético, corpus de 10 voces, análisis, ASR opcional, integración del snapshot de 32 imágenes, catálogo de 13 filas, nueve controles automáticos y ZIP/Drive. Cada tarea incluye resultado observable y recuperación ante fallo. Todo el código Python ejecutable sigue dentro del único cuaderno Colab.
- El ASR opcional se desplazó a **después** de descargar y medir las diez voces: una persona que recorre el cuaderno en orden puede activar el modelo sobre un WAV existente.
- El cuaderno produce `AUTOCOMPROBACIÓN: LISTO (9/9)` solamente si las nueve condiciones técnicas se cumplen, incluida una decisión individual con tres opciones no nulas. La ruta por defecto muestra `INCOMPLETO` hasta que el estudiante actúa, sin falsear éxito.
- Se añadió ZIP descargable con **20 WAV** de voz (10 originales + 10 decodificados), JSONL/Parquet, manifiesto y metadatos, o conservación opcional en Drive. El ZIP excluye el Parquet caché transitorio, mantiene los 10 WAV y valida su contenido. La lista de cotejo de la presentación es solo declaración personal y **no puede leer la sesión privada Colab**.
- QA prueba escritorio/móvil, navegación, contenidos y marcadores pedagógicos; ejecuta **todo el notebook** desde runtime limpio, confirma descarga y procesamiento auténticos, toma tres decisiones simuladas del estudiante, verifica los 9 controles y produce/reabre el ZIP con 20 WAV. Se mantiene como pendiente una prueba individual de autorización de Google Drive y un test de ASR con modelo externo si no hay constancia de ejecución de ese subpaso.
