# S10 · Audios humanos reales autorizados para la clase

## Fuente y licencia

**Corpus:** PolyAI / MINDS-14, subconjunto `es-ES`, voz humana en español para clasificación de intenciones de servicios financieros.

- Página: https://huggingface.co/datasets/PolyAI/minds14/tree/main/es-ES
- Archivo: https://huggingface.co/datasets/PolyAI/minds14/resolve/main/es-ES/train-00000-of-00001.parquet
- Licencia declarada: **Creative Commons Attribution 4.0 (CC BY 4.0)**.
- SHA-256 del Parquet (observado en Hugging Face): `989bf2f90676a5eb5852fe785a03b1d9b97763e0febbd0fd0a3f489afd83badf`.
- Atribución en productos: **PolyAI, MINDS-14, subset es-ES; CC BY 4.0; fuente Hugging Face**. No implica que PolyAI o los hablantes respalden la actividad.

## Cómo se ejecuta

El único recurso ejecutable para estudiantes es [Google Colab, S10](../../Cuadernos/10_Imagenes_Audio.ipynb). La celda **7A** recupera automáticamente ~39 MB del Parquet de la fuente y comprueba su hash. Selecciona de forma determinista diez filas de **diez intenciones diferentes**, ordenadas por ruta de origen. No se descargan artículos ni audios de El Tiempo.

Cada registro crea:
- `raw/voz_real/voz_XX_fuente.wav`: **fuente sin modificar** (en algunos registros WAV con compresión G.711 μ-law).
- `raw/voz_real/voz_XX.wav`: WAV derivado PCM16 mono, apto para `wave`, NumPy, FFT y escucha.
- `raw/voz_real/dataset_manifest.json`: `source_record_id`, `source_original_sha256`, `sha256` del PCM16, `source_codec`, texto de referencia, duración, código de intención y licencia.

La celda **7B** calcula duración, frecuencia de muestreo, RMS, tasa de cruces por cero y centroide espectral y deja elegir una de las diez voces para escuchar. ASR `faster-whisper` está disponible **solo como profundización opcional** para comparar un audio concreto contra su referencia humana.

## Relación con el corpus de imágenes de noticias

El snapshot histórico conserva **32 imágenes/24 artículos** en `Datos/s10_imagenes_reales/inputs.json`. La celda **7C** comprueba solo esos metadatos, genera `outputs/source_registry.json` y preserva sus identificadores editoriales `article_id`. Los diez audios MINDS-14 usan `source_record_id`, no `article_id`, porque no pertenecen a esas noticias. **Se integran dos inventarios en un contrato de catálogo común, sin afirmar correspondencias que no existen**.

El catálogo final contiene **13 filas**: dos derivaciones de imagen de demostración, una señal acústica original de demostración y diez audios grabados por personas. Se guarda en JSONL y Parquet; el manifiesto verifica todos los originales y derivados descargados o creados.

## Licencias de medios editoriales

El feed `https://www.eltiempo.com/servicios/feeds/articulo/{id}` puede contener la referencia `audio_url`, pero **una referencia no es una licencia de uso**. Los términos de El Tiempo restringen la extracción automatizada y la minería de datos sin permiso escrito, por lo que el laboratorio no descarga ni transcribe audios del medio. No inferir relaciones noticia-audio de la muestra bancaria.

## Calidad y límite

El validador `utils/validate_s10_multimodal.py` ejecuta el cuaderno desde un entorno limpio en CI, comprueba exactamente diez WAV reales únicos con procedencia y licencia, verifica la fuente de metadatos de imágenes, comprueba el catálogo de 13 filas, y corrompe una copia de QA para confirmar que la verificación detecta el cambio. Una prueba de Colab con autenticación individual a Google Drive debe hacerse por separado; una ejecución de CI no la sustituye.
