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
