# Instalación explicada herramienta por herramienta

**Entorno recomendado para estudiantes:** GitHub Codespaces, sin instalar Linux en su computador. Cada paso de esta página también sirve para reproducir el proceso en Ubuntu/Debian si se desea. **No hace falta ejecutar nuevamente `apt install` dentro de un Codespace correctamente construido**: primero verifica que la herramienta ya está.

## 1. Cómo preparar Linux en Codespaces

Abre el archivo `.devcontainer/Dockerfile` de este kit. Las órdenes `apt-get install` instalan programas de sistema:
- `tesseract-ocr` y `tesseract-ocr-spa` → programa OCR e idioma español.
- `ffmpeg` y `poppler-utils` → leer/convertir audio y PDF.
- `fonts-dejavu-core` → fuentes estándar del sistema.
- `curl` y `zstd` → descargar/descomprimir el paquete oficial de Ollama **durante la construcción del contenedor**, sin `systemd`.

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

## 3. Ollama dentro de Codespaces: ya instalado, sin systemd

**La ruta correcta para los estudiantes ha cambiado.** El archivo `.devcontainer/Dockerfile` descarga y extrae el paquete oficial `ollama-linux-amd64.tar.zst` (o ARM64). **No ejecutes otra vez `https://ollama.com/install.sh` dentro del Codespace**: este contenedor no necesita ni debe configurar servicios `systemd`. El servidor se inicia en segundo plano mediante `iniciar_ollama.sh` al arrancar el Codespace, sin abrir el puerto a Internet.

**Primero, en un Codespace NUEVO de la rama `s11-estudiantes`:**

~~~bash
command -v ollama
ollama --version
bash iniciar_ollama.sh
curl -fsS http://127.0.0.1:11434/api/tags
~~~

**Resultado esperado:** `command -v ollama` muestra `/usr/bin/ollama`, la API responde un JSON con la lista de modelos. Si la lista está vacía es normal: Ollama ya está instalado, pero todavía no descargaste el modelo.

**Segundo, prepara el modelo visual y verifica sus 768 dimensiones:**

~~~bash
bash preparar_embeddinggemma.sh
~~~

Este comando ejecuta cuatro operaciones legibles: comprueba Ollama, muestra el espacio libre, descarga `embeddinggemma-2:440m` y hace una petición real a `/api/embed`. **El modelo 440m admite texto e imágenes; el 270m solo texto.** Al terminar verás `OK: Ollama local + embeddinggemma-2:440m + 768 dimensiones.` No uses `ollama embed`: el laboratorio invoca la **API** de Ollama desde Python.

### Si tu Codespace existía antes de la corrección

El contenedor abierto antes de esta actualización **NO se transforma automáticamente** al recibir cambios del Dockerfile. Haz lo siguiente:

1. Comprueba que estás en la rama `s11-estudiantes`, no en `main`. Conserva primero cualquier cambio sin guardar.
2. En la terminal, sincroniza el repositorio:

   ~~~bash
   git branch --show-current
   git pull --ff-only origin s11-estudiantes
   ~~~

3. Pulsa **Ctrl+Shift+P → Codespaces: Rebuild Container → Rebuild**. Esto reconstruye el entorno con Ollama incluido. GitHub documenta que los archivos de `/workspaces` se conservan tras reconstruir el contenedor; los modelos se guardan en `/workspaces/BigData2026/.cache/ollama/models`, excluido de Git.
4. Después ejecuta:

   ~~~bash
   ollama --version
   bash iniciar_ollama.sh
   bash preparar_embeddinggemma.sh
   ~~~

### Alternativa para arreglar un contenedor antiguo SIN reconstruir

Si necesitas continuar con el contenedor viejo, estos comandos **instalan el paquete manual oficial** y evitan `systemd`. Requieren `sudo`, conexión y espacio libre en Codespaces:

~~~bash
sudo apt-get update
sudo apt-get install -y zstd
ARQ="$(dpkg --print-architecture)"
curl -fL --retry 3 "https://ollama.com/download/ollama-linux-${ARQ}.tar.zst" -o /tmp/ollama-linux.tar.zst
sudo tar --zstd -xf /tmp/ollama-linux.tar.zst -C /usr
command -v ollama
ollama --version
bash iniciar_ollama.sh
bash preparar_embeddinggemma.sh
~~~

Si la descarga está incompleta, `tar` informará del error: no se considera instalado hasta ver `ollama --version`, una respuesta de `/api/tags` y el vector comprobado. No uses `less` en una secuencia de comandos de instalación: **`less archivo` abre un visor interactivo que se cierra pulsando `q`** y bloquea los comandos siguientes hasta entonces.

### Instalación en Ubuntu fuera de Codespaces

En un Ubuntu local, la guía **oficial** permite `curl -fsSL https://ollama.com/install.sh | sh`; ese instalador sí puede configurar el servicio del sistema. También es válida la extracción manual oficial. Revisa primero [las instrucciones oficiales para Linux](https://github.com/ollama/ollama/blob/main/docs/linux.mdx). En Codespaces usamos el método manual dentro del contenedor para no depender de servicios `systemd`.

**Seguridad y persistencia:** el servidor usa `127.0.0.1:11434` (no lo publiques). Los pesos del modelo se almacenan en `.cache/ollama/models` dentro de `/workspaces` y `.gitignore` evita subirlos al repositorio. El modelo se descarga solo una vez por almacenamiento persistente, salvo que borres la caché.

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

La programación del ejercicio se desarrolla en **01_laboratorio.ipynb** (FASE 1: herramientas; FASE 2: ampliación a 122 fuentes): no se aprende OCR mirando el visor si no escribes y explicas la llamada a Tesseract, los bucles y las comprobaciones.

## 6. Problemas recurrentes

| Síntoma | Primer control |
|---|---|
| Falta `spa` | Instala/verifica `tesseract-ocr-spa` |
| `TesseractNotFoundError` | Existe el paquete Python, pero falta ejecutable |
| `ModuleNotFoundError` | Falta ejecutar pip en el kernel seleccionado |
| `Connection refused` | Ejecuta `bash iniciar_ollama.sh` y revisa `/tmp/s11-ollama.log` |
| `ollama: command not found` | Actualiza la rama y reconstruye el Codespace; o usa instalación manual con `zstd` |\n| `model not found` | Ejecuta `bash preparar_embeddinggemma.sh`; comprueba `ollama list` |
| Whisper demora | Modelo tiny necesita descarga; CPU sin GPU |
| WER extraño | Comprueba que comparaste audio con la referencia del mismo registro |
| OCR de foto vacío | Quizá no hay texto legible; usa búsqueda visual |

El puerto 11434 es **local** dentro del Codespace. No lo expongas públicamente. Detén el Codespace al acabar para evitar consumir cuota.

**Fuentes oficiales:** https://tesseract-ocr.github.io/ · https://github.com/SYSTRAN/faster-whisper · https://ollama.com/library/embeddinggemma-2:440m · https://github.com/ollama/ollama/blob/main/docs/api.md.
