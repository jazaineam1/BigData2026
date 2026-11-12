# Instalación explicada herramienta por herramienta

**Entorno recomendado para estudiantes:** GitHub Codespaces, sin instalar Linux en su computador. Cada paso de esta página también sirve para reproducir el proceso en Ubuntu/Debian si se desea. **No hace falta ejecutar nuevamente `apt install` dentro de un Codespace correctamente construido**: primero verifica que la herramienta ya está.

## 1. Cómo preparar Linux en Codespaces

Abre el archivo `.devcontainer/Dockerfile` de este kit. Las órdenes `apt-get install` instalan programas de sistema:
- `tesseract-ocr` y `tesseract-ocr-spa` → programa OCR e idioma español.
- `ffmpeg` y `poppler-utils` → leer/convertir audio y PDF.
- `fonts-dejavu-core` → fuentes estándar del sistema.
- `curl` → descargar instalador oficial de Ollama.

**Compruébalo en la terminal:**

~~~bash
python --version
tesseract --version
tesseract --list-langs
ffprobe -version | head -1
pdftoppm -v
~~~

En una instalación Ubuntu propia, los mismos paquetes se instalan con:

~~~bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
sudo apt install -y tesseract-ocr tesseract-ocr-spa ffmpeg poppler-utils
~~~

**Explicación docente:** el ejecutable Tesseract no es lo mismo que el paquete Python `pytesseract`: el segundo solo hace la llamada al primero.

## 2. Bibliotecas Python: para qué sirve cada una

El contenedor ejecuta `python -m pip install -r requirements.txt`. Para hacerlo manualmente en Ubuntu, desde una copia del kit:

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
~~~

| Paquete | Qué muestra el video |
|---|---|
| Pillow | Abrir PNG, JPG y WEBP; inspeccionar tamaño |
| pytesseract | Una llamada de Python al motor Tesseract |
| pandas + PyArrow | Tablas, JSONL y Parquet |
| requests | Enviar JSON a la API local de Ollama |
| faster-whisper | Ejecutar Whisper tiny para ASR |
| ipykernel + Jupyter | Escribir, ejecutar y modificar celdas |

**Verifica:** `python -c "import pytesseract,pandas,pyarrow,requests,faster_whisper; print('OK')"`.

## 3. Ollama y EmbeddingGemma 2:440m (visión)

A diferencia de Tesseract, Ollama **no está preinstalado** en el contenedor S11. Explica cada acción y su seguridad:

1. Abre el sitio oficial: https://ollama.com/download/linux.
2. Descarga el instalador a un archivo temporal para poder examinarlo.
3. Ejecuta la instalación oficial dentro del Codespace.
4. Inicia el servicio local; descarga el modelo correcto y consulta la API.

~~~bash
curl -fsSL https://ollama.com/install.sh -o /tmp/ollama-install.sh
less /tmp/ollama-install.sh
sh /tmp/ollama-install.sh
ollama --version
nohup ollama serve >/tmp/s11-ollama.log 2>&1 &
ollama pull embeddinggemma-2:440m
ollama list
curl -fsS http://127.0.0.1:11434/api/tags
~~~

Si el servicio se inicia automáticamente, la línea `nohup` puede ser innecesaria. El modelo 440m admite **texto e imágenes**; el 270m **solo texto**. La primera instalación y descarga puede requerir más de los 60 minutos de la videoclase: muestra los comandos reales, pero descarga previamente para la grabación.

**Comprobación mínima:** la API `/api/tags` responde, el modelo está en la lista y una llamada `/api/embed` devuelve un vector de 768 valores.

## 4. Whisper: transcripción de audio REAL

Instalaste `faster-whisper` con pip. La primera vez que escribas:

~~~python
from faster_whisper import WhisperModel
modelo = WhisperModel("tiny", device="cpu", compute_type="int8")
~~~

se descargarán pesos de Whisper tiny. Esto no es una transcripción: es **cargar el modelo**. Luego debes escribir `modelo.transcribe(ruta_audio, language="es")` y recorrer sus segmentos.

**Verificación:** escucha el WAV real del corpus MINDS-14, compara con su texto humano y calcula WER. **No inventes WER** si no hay referencia humana.

## 5. Interfaz para abrir y visualizar documentos

Además del cuaderno, puedes instalar Streamlit con soporte para PDF y la biblioteca de audio SoundFile:

~~~bash
python -m pip install "streamlit[pdf]>=1.56,<2" "soundfile>=0.12,<1"
streamlit run visor_fuentes.py --server.address 0.0.0.0 --server.port 8501
~~~

**Streamlit** crea una interfaz local: permite escoger un documento y mostrar un PDF con st.pdf, fotografías con st.image y audio con st.audio. Requiere el complemento streamlit-pdf para st.pdf. El puerto **8501 debe ser privado** dentro de Codespaces; nunca lo expongas a Internet para archivos con datos personales.

La programación del ejercicio sigue en el cuaderno: no se aprende OCR mirando una interfaz si no escribes y explicas la llamada a Tesseract.

## 6. Problemas recurrentes

| Síntoma | Primer control |
|---|---|
| Falta `spa` | Instala/verifica `tesseract-ocr-spa` |
| `TesseractNotFoundError` | Existe el paquete Python, pero falta ejecutable |
| `ModuleNotFoundError` | Falta ejecutar pip en el kernel seleccionado |
| `Connection refused` | Ollama no está iniciado; inspecciona `/tmp/s11-ollama.log` |
| `model not found` | Descarga `embeddinggemma-2:440m` |
| Whisper demora | Modelo tiny necesita descarga; CPU sin GPU |
| WER extraño | Comprueba que comparaste audio con la referencia del mismo registro |
| OCR de foto vacío | Quizá no hay texto legible; usa búsqueda visual |

El puerto 11434 es **local** dentro del Codespace. No lo expongas públicamente. Detén el Codespace al acabar para evitar consumir cuota.

**Fuentes oficiales:** https://tesseract-ocr.github.io/ · https://github.com/SYSTRAN/faster-whisper · https://ollama.com/library/embeddinggemma-2:440m · https://github.com/ollama/ollama/blob/main/docs/api.md.
