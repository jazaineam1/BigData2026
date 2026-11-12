# Guía del estudiante · Sesión 11: de archivos a evidencia consultable

**Universidad Central · Big Data 2026-2S**  
**Tiempo de lectura:** ~15 min. La ejecución y primera descarga de modelos puede requerir más tiempo.

**Objetivo:** procesar imágenes y audios, recuperar candidatos y buscarlos sin perder sus fuentes. Este laboratorio es complementario al ETL original, no sustituye el Taller de Control 2.

| Herramienta | Qué hace | Qué NO demuestra |
|---|---|---|
| Tesseract (OCR) | Imagen → texto probable | No certifica la cifra ni describe toda la foto |
| Faster-Whisper (ASR) | Audio → palabras y segundos | No garantiza nombres ni cantidades exactas |
| Reglas/regex | Texto → cifras/fechas candidatas | No comprueba que un hecho ocurrió |
| Python ETL | Archivos → catálogo JSONL/Parquet | No significa computación distribuida |
| EmbeddingGemma 2 | Texto → vectores para búsqueda | No transcribe audio ni redacta respuestas |
| SHA-256 | Compara igualdad de bytes | No certifica verdad ni autoría |

## Paso 1 · Abrir un Codespace

En [GitHub BigData2026](https://github.com/jazaineam1/BigData2026) elige **Code → Codespaces → New with options → S11 · OCR, voz y EmbeddingGemma 2**. No selecciones Airflow. Abre Terminal:

~~~bash
cd Laboratorios/S11_Codespaces
python --version
tesseract --list-langs
bash probar_todo.sh --ligero
~~~

**Comprueba:** idioma `spa` y salida `OK`. El modo ligero NO prueba inferencia real de Whisper/Ollama. Usa datos autorizados, conserva el puerto 8501 privado y detén Codespaces al terminar para ahorrar cuota.

## Paso 2 · Generar y observar dos archivos sintéticos

~~~bash
python lab.py preparar
sha256sum salidas/afiche_simulado.png salidas/voz_simulada.wav
cat salidas/origen.json
~~~

Abre `salidas/afiche_simulado.png` y reproduce `salidas/voz_simulada.wav`. Ambos se crearon para enseñar; **no son noticias ni audios periodísticos reales**. `origen.json` registra los hashes de los originales.

## Paso 3 · OCR: de píxeles a letras

~~~bash
python lab.py ocr
cat salidas/ocr.json
tesseract salidas/afiche_simulado.png stdout -l spa --psm 6
~~~

La línea clave es:

~~~python
texto = pytesseract.image_to_string(imagen, lang="spa", config="--psm 6")
~~~

**Qué significa:** `spa` es español; `psm 6` supone un bloque de texto. La CLI comprueba que Tesseract produce la misma salida por otra vía, pero **ambas vías usan el mismo motor**. Compara las cifras manualmente con el PNG para comprobar si acertó.

## Paso 4 · ASR: de sonido a palabras

~~~bash
python lab.py asr
cat salidas/asr.json
python lab.py evaluar-asr
cat salidas/evaluacion_asr.json
~~~

La línea clave es `modelo.transcribe(ruta_audio, language="es")`. Abre el WAV, escucha la frase y revisa un segmento de `inicio_s` a `fin_s`. Whisper tiny corre en CPU; la primera vez descarga pesos.

**WER:** errores de palabra / número de palabras de referencia. Aquí podemos calcularlo porque conocemos la frase de la voz sintética. Para otra grabación sin referencia humana, NO inventes WER.

## Paso 5 · Extracción y fuentes

~~~bash
python lab.py extraer
cat salidas/extraccion.json
~~~

Encuentra una cifra o fecha y vuelve a la imagen o al intervalo del audio para verificarla. Una coincidencia con regex identifica **candidatos**, no hechos certificados.

## Paso 6 · Embeddings y recuperación

~~~bash
bash iniciar_ollama.sh
python lab.py indexar
python lab.py buscar --consulta "¿Cuántos contratos se mencionaron?"
python lab.py buscar --consulta "¿Qué valor se indicó?"
~~~

Usamos `embeddinggemma-2:270m`: codificador de **texto** que devuelve vectores de **768 dimensiones**. Consulta su API directamente (sin `lab.py`):

~~~bash
curl -fsS http://127.0.0.1:11434/api/embed \
 -H 'Content-Type: application/json' \
 -d '{"model":"embeddinggemma-2:270m","input":"Un contrato de ejemplo"}' \
 | python -c 'import json,sys; print(len(json.load(sys.stdin)["embeddings"][0]))'
~~~

**Esperado:** `768`. Revisa `salidas/indice.json`: contiene fragmentos, ruta, hash y vector. Coseno alto significa **similitud** y NO porcentaje de verdad.

## Paso 7 · Comprobación independiente de la lógica del laboratorio

~~~bash
python verificar_independiente.py --caso lab --modelo
~~~

Este script separado compara hashes, vuelve a ejecutar la CLI Tesseract, comprueba segmentos, recalcula WER si la referencia corresponde y consulta directamente Ollama. Sigue siendo indispensable inspeccionar imagen y audio para evaluar contenido.

## Paso 8 · Reutilizar el mismo motor con un nuevo proyecto

Copia **dos fuentes sintéticas autorizadas** a otra carpeta. Son dos modalidades y no se fusionan como un único hecho:

~~~bash
python proyecto.py iniciar --destino proyectos/mi_reto
cp salidas/afiche_simulado.png proyectos/mi_reto/entradas/imagenes/
cp salidas/voz_simulada.wav proyectos/mi_reto/entradas/audios/
python proyecto.py plan --config proyectos/mi_reto/config.json
python proyecto.py procesar --config proyectos/mi_reto/config.json
python proyecto.py indexar --config proyectos/mi_reto/config.json
python proyecto.py buscar --config proyectos/mi_reto/config.json --consulta "¿Cuántos contratos?"
python proyecto.py auditar --config proyectos/mi_reto/config.json
python verificar_independiente.py --proyecto proyectos/mi_reto
~~~

Explora las salidas:

- `catalogo.jsonl`: una fila por archivo, texto probable, SHA-256 y origen.
- `candidatos.jsonl`: cifras/fechas/referencias con texto de respaldo y ruta.
- `catalogo.parquet`: datos tabulares por columnas.
- `manifest.json`: inventario para comprobar integridad.
- `indice.json`: vectores y fragmentos consultables.

**Modifica un parámetro:** en `proyectos/mi_reto/config.json` cambia `ocr.psm` de 6 a 11. Guarda una copia del texto anterior, vuelve a ejecutar `procesar`, `indexar` y `auditar`, y compara el OCR sobre el mismo PNG.

Después **reemplaza los archivos del ejemplo por tus propios archivos autorizados**, vuelve a procesar y explica qué cambió. No necesitas reescribir `proyecto.py`.

## Mini-reto y evidencia mínima

- [ ] Abrí la imagen y contrasté una cifra contra su OCR.
- [ ] Escuché el audio y comprobé una palabra o cantidad del ASR.
- [ ] Encontré una cifra candidata y rastreé su archivo original.
- [ ] Consulté el índice y confirmé fuente + hash.
- [ ] Cambié un parámetro y documenté el antes/después.
- [ ] Reutilicé el motor con archivos distintos sin cambiar su lógica.

**Entrega formativa:** tabla `fuente | herramienta | resultado | error/límite | comprobación` y dos capturas (catálogo y comparación). Esta práctica **no modifica** la rúbrica del Taller de Control 2.

## Si algo falla

| Mensaje o problema | Primera acción |
|---|---|
| No aparece `spa` | Abre el contenedor Codespaces S11, no Airflow |
| OCR vacío | Mira el PNG: ¿tiene letras? |
| Whisper tarda | Comprueba descarga/red; prueba WAV corto |
| Ollama no responde | Ejecuta `bash iniciar_ollama.sh` |
| Búsqueda obsoleta | Repite `procesar` y después `indexar` |
| Auditoría falla | Revisa ruta, fuente y SHA; no sobreescribas originales |

**Profundización:** [Manual de reutilización](./GUIA_REUTILIZACION.md) · [Presentación de la videoclase](../../Presentaciones/s11-videoclase-ocr-asr-embeddings.html) · [Tesseract](https://tesseract-ocr.github.io/) · [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) · [EmbeddingGemma 2](https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2?hl=es-419).
