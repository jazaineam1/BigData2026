# EMPIEZA AQUÍ · S11 en Codespaces, paso a paso

**Propósito:** que cualquier estudiante pueda **repetir toda la investigación**, desde un Codespace nuevo hasta un catálogo de **122 fuentes**, y explicar el código esencial. La parte larga se hace después de la videoclase de 60 minutos.

## Cómo se relacionan las herramientas

| Recurso | ¿Cuándo lo abres? | ¿Qué hace? | ¿Qué debes producir? |
|---|---|---|---|
| [Presentación S11](https://jazaineam1.github.io/BigData2026/Presentaciones/s11-videoclase-ocr-asr-embeddings.html#s1) | Al comenzar cada tema | Plantea pregunta, concepto, error y demostración | Explicación, no solo ejecución |
| **00_EMPIEZA_AQUI.md** (este documento) | Al abrir Codespaces | Instrucciones de replicación y recuperación | Entorno comprobado |
| **visor_fuentes.py** | Antes y después de cada inferencia | Muestra el PDF completo, PNG, foto o audio original; OCR/ASR opcionales | Comparación humana con la fuente |
| **01_laboratorio.ipynb** | Durante el video | Construye Python desde cero sobre 4 fotos, 1 acta y 1 voz | Celdas entendidas y modificadas |
| **02_lotes_122_fuentes.ipynb** | Tras aprender cada función | Escala con bucles a 62 fotos, 30 actas y 30 voces | Métricas, ranking y catálogo |
| **INSTALACION_UBUNTU.md** | Al explicar herramientas | Muestra instalación en contenedor/Ubuntu y verificaciones | Saber instalar Tesseract, Python, Whisper y Ollama |
| **FUENTES.md** | Antes de compartir resultados | Distingue origen, crédito, licencias y limitaciones | Resultados atribuibles y seguros |

## Paso 0 · Abrir el entorno CORRECTO

1. Entra a **https://github.com/jazaineam1/BigData2026/tree/s11-estudiantes**.
2. En el selector de rama verifica **s11-estudiantes**, NO main.
3. Elige **Code → Codespaces → Create codespace on s11-estudiantes**. Si aparece una configuración, selecciona **S11 · OCR, visión y voz (aprende Python)**. **No selecciones Airflow**.
4. Cuando abra VS Code en el navegador, usa **Terminal → New Terminal** y confirma que el directorio de trabajo es \`/workspaces/BigData2026\`.
5. En el explorador deben aparecer los dos cuadernos \`.ipynb\`, \`datos/\`, \`visor_fuentes.py\`, \`requirements.txt\` y estas guías. Si ves \`Airflow\`, \`evaluaciones\` u otras carpetas del curso, **estás en otro Codespace o en main**.

**Explicación para el docente:** Codespaces es un entorno Linux remoto con VS Code. El repositorio almacena el código y una configuración de contenedor; el computador personal no necesita ejecutar Whisper ni alojar Ollama.

## Paso 1 · ¿Qué se instaló y cómo comprobarlo?

Abre \`.devcontainer/Dockerfile\`: allí están los **programas Linux** (Tesseract, idioma español, FFmpeg, Poppler). Abre \`requirements.txt\`: allí están las **bibliotecas Python** (Pillow, pytesseract, pandas, PyArrow, Faster-Whisper, Streamlit, Jupyter). En \`.devcontainer/devcontainer.json\` verás el comando que instala esas bibliotecas.

En la terminal:

~~~bash
pwd
python --version
tesseract --version
tesseract --list-langs
python -c "from PIL import Image; import pytesseract, pandas, pyarrow, requests, faster_whisper, streamlit; print('Python OK')"
~~~

**Esperado:** \`pwd\` termina en \`/workspaces/BigData2026\`; Python funciona; \`tesseract --list-langs\` incluye \`spa\`; y se imprime **Python OK**. Si falta una biblioteca, revisa \`postCreateCommand\` y ejecuta \`python -m pip install -r requirements.txt\`. La instalación en Ubuntu propio está explicada paso a paso en \`INSTALACION_UBUNTU.md\`.

**No confundas:** \`pytesseract\` es un puente Python; \`tesseract\` es el programa OCR del sistema. \`Faster-Whisper\` es una biblioteca que carga pesos del modelo al ejecutar inferencia. Ollama es **otro servicio** y no viene preparado automáticamente.

## Paso 2 · Abre un documento REAL en el visor privado

Al iniciar el Codespace se ejecuta \`abrir_visor.sh\` y debería aparecer un aviso para abrir el puerto **8501**. Si no aparece:

~~~bash
bash abrir_visor.sh
curl -fsS http://127.0.0.1:8501/_stcore/health
~~~

Si sigue sin funcionar, ejecuta en la terminal (y déjala abierta):

~~~bash
streamlit run visor_fuentes.py --server.address 0.0.0.0 --server.port 8501
~~~

Abre la pestaña **Ports / Puertos**, selecciona el 8501 y **Open Preview / Abrir vista previa**. **Confirma que la visibilidad sea Private.** La interfaz web del curso (GitHub Pages) es pública y **NO** puede leer directamente archivos privados del Codespace; el visor real corre **dentro del Codespace**, en el puerto privado.

En el visor:

1. Selecciona **Actas SECOP (30)**; busca \`728490281\`; abre el PDF completo a la izquierda y la primera página PNG a la derecha. Identifica la tabla de importes sin proyectar datos personales innecesarios.
2. Selecciona **El Tiempo (30)**; abre \`eltiempo_006.webp\` y \`eltiempo_009.webp\`. ¿Cuál contiene un letrero legible? ¿Cuál requiere una búsqueda visual?
3. Selecciona **Fotografías con ficha (32)** y abre otra imagen. Comprueba si tiene créditos/URL registrados.
4. Selecciona **Voces MINDS-14 (30)**. La primera vez pulsa **Preparar / comprobar las 30 voces**. Se descarga y comprueba un Parquet (~39 MB); se crean 30 WAV humanos. Puede requerir conexión y algo de tiempo. Escucha uno y abre su referencia humana.

El visor es **para observar y verificar fuentes**, no para sustituir que escribas Python.

## Paso 3 · Aprende con el cuaderno 01 (video)

Haz doble clic en \`01_laboratorio.ipynb\`. Arriba a la derecha, selecciona **Select Kernel → Python 3** del Codespace. Si se pide instalar el kernel, usa el entorno Python que viene del contenedor.

Ejecuta una celda por vez con **Shift + Enter**, en este orden:

| Sección del cuaderno | Qué escribes y explicas | Qué debes comprobar |
|---|---|---|
| Abrir imagen | \`Path\`, \`Image.open\`, \`display\` | Formato y píxeles; cambia foto 006→009 |
| OCR de acta | \`pytesseract.image_to_string(..., lang="spa")\` | Letras/cifras con la imagen original, sin divulgar datos personales |
| Comparar PSM | \`--psm 6\`, \`--psm 11\`, opcional \`--psm 3\` | Una diferencia o error real, no solo cantidad de caracteres |
| OCR en fotografías | \`for\` sobre cuatro fotos | Letrero vs escena sin texto |
| Embeddings | \`requests.post(... /api/embed ...)\` | Vector de imagen de 768 dimensiones y ranking con una pregunta |
| Audio/Whisper | \`WhisperModel(...)\`, \`transcribe\` | Escuchar antes, comparar ASR y referencia del MISMO WAV |
| Catálogo ETL | \`dict\`, \`json.dumps\`, \`to_parquet\` | Reabrir y comprobar hashes |

**Instrucción para aprender:** en cada bloque responde por escrito **«¿qué hace esta línea?, ¿qué parámetro cambié?, ¿qué observé?, ¿cómo lo verifiqué?»**. Si algo falla, conserva el error y explica su causa antes de seguir.

## Paso 4 · Preparar Ollama y EmbeddingGemma 2:440m

Cuando llegues a vectores, abre \`INSTALACION_UBUNTU.md\`. El modelo **440m** admite imagen y texto; la variante **270m** solo texto.

En la terminal, si Ollama no está instalado, sigue los pasos oficiales de la guía y después:

~~~bash
ollama --version
ollama pull embeddinggemma-2:440m
ollama list
curl -fsS http://127.0.0.1:11434/api/tags
~~~

**Esperado:** \`ollama list\` incluye \`embeddinggemma-2:440m\`; la API local responde. Si el puerto 11434 no responde, inicia \`ollama serve\` en otra terminal y revisa errores. **No hagas público ese puerto.** La descarga inicial no se puede garantizar dentro de los 60 minutos de grabación: realiza la preparación antes de empezar el video, pero **explica cada paso en pantalla**.

## Paso 5 · Amplía con el cuaderno 02 (práctica de corpus)

Abre \`02_lotes_122_fuentes.ipynb\`; ejecuta las celdas **en orden**. Primero deja:

- \`N_ACTAS = 5\`: OCR real de cinco primeras páginas.
- \`N_FOTOS = 8\`: OCR de ocho fotografías, revisando falsos positivos.
- \`N_VISION = 8\`: crea ocho vectores visuales (puede tardar CPU).
- \`N_ASR = 3\`: transcribe tres voces y mide WER.

Después prueba la escala completa: **30 actas, 62 fotos, 62 embeddings de imagen y 30 audios**. Para los vectores se reutiliza la caché \`outputs/vectores_440m.json\` si los bytes de las imágenes siguen teniendo el mismo SHA-256; no borres esa caché por costumbre.

**Resultado esperado del ETL final:** \`outputs/catalogo_122.jsonl\` y \`outputs/catalogo_122.parquet\`, ambos con **122 registros**: 62 fotografías + 30 actas + 30 voces. Las 30 primeras páginas PNG son **vistas de los PDF**, no otros documentos. Verifica **integridad** comparando SHA-256 y reabriendo ambos formatos. Los 30 audios descargados conservan referencia/atribución; no son audios de las fotos periodísticas.

**Importante:** la inferencia de 62 imágenes y 30 voces no tiene una duración fija en CPU. El video enseña 4–8 ejemplos y la práctica completa se ejecuta fuera de los 60 minutos.

## Paso 6 · Comprobar aprendizaje y producir evidencia

Cada estudiante entrega una tabla breve:

| Pregunta | Archivo/fuente | Herramienta | Cambio al código | Resultado | Comprobación independiente | Límite/error |
|---|---|---|---|---|---|---|

Se requieren como mínimo: un valor SECOP contrastado visualmente, un OCR de letrero, una búsqueda visual con una consulta cambiada, una voz con comparación frente a referencia, y una fila del catálogo con SHA-256 verificado. **No basta enviar capturas de comandos que terminaron sin errores.**

**No publiques** las salidas completas de OCR de actas que puedan contener identificaciones ni redistribuyas fotografías sin condiciones de uso verificadas.

## Recuperación de fallos

| Síntoma | Qué revisar antes de avanzar |
|---|---|
| Abre carpetas de otros cursos | Estás en rama/main/Codespace equivocado; selecciona \`s11-estudiantes\` |
| \`spa\` no aparece | \`tesseract-ocr-spa\` del Dockerfile; reconstruir contenedor |
| Kernel Python no está | Python/Jupyter de \`requirements.txt\`; seleccionar kernel del contenedor |
| Visor no abre | \`bash abrir_visor.sh\`, health 8501 y pestaña Ports; puerto privado |
| PDF no se ve | Versión \`streamlit[pdf]\` y soporte integrado; descarga el PDF desde el visor si la previsualización falla |
| Audios no aparecen | Preparar 30 voces; conexión a HF, hash de fuente, revisar mensaje en barra lateral |
| Ollama rechaza el modelo | Ejecutar \`ollama pull embeddinggemma-2:440m\`, verificar servicio 11434 |
| El modelo visual falla tras varios archivos | Guardar caché, reducir \`N_VISION\`, comprobar recursos del Codespace |
| Whisper tarda | Descarga inicial/CPU; \`tiny\`, lotes pequeños durante clase |
| \`NameError\` en cuaderno 02 | Ejecutar celdas anteriores; usa **Restart Kernel → Run All** solo cuando ya entiendas la secuencia |
| Parquet y JSONL no coinciden | Reejecutar celda ETL y luego auditoría, sin borrar originales |
| El programa ejecuta pero OCR está mal | Revisar fuente, PSM y fragmento; no marcarlo como «correcto» |

## Lectura adicional y referencias

- [Tesseract OCR](https://tesseract-ocr.github.io/) · [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) · [Ollama (Linux)](https://ollama.com/download/linux).
- [EmbeddingGemma 2:440m](https://ollama.com/library/embeddinggemma-2:440m) · [PolyAI MINDS-14](https://huggingface.co/datasets/PolyAI/minds14).
- [FUENTES.md](./FUENTES.md) explica procedencia, atribución pendiente y precauciones con SECOP.

**El guion narrativo del profesor NO forma parte de esta rama estudiantil.**
