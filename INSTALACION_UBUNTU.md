# Instalación de las herramientas de S11

Esta guía explica qué aporta cada herramienta y cómo verificarla. El entorno de **GitHub Codespaces** incluye las herramientas indicadas por Dockerfile y requirements.txt. También puedes repetir la instalación en tu propio Ubuntu.

## 1. Herramientas del Codespace

| Herramienta | Función | Comprobación |
|---|---|---|
| Python 3.11 | Ejecutar el cuaderno | `python --version` |
| Tesseract + español | Reconocer caracteres en imágenes | `tesseract --list-langs` |
| Pillow y pytesseract | Abrir imágenes y llamar Tesseract desde Python | `python -c "import PIL,pytesseract"` |
| Poppler | Inspeccionar PDF, renderizar páginas y leer texto seleccionable | `pdfinfo -v` |
| FFmpeg y Faster-Whisper | Preparar y transcribir voz | `ffmpeg -version` |
| Ollama | Ejecutar localmente modelos de embeddings | `ollama --version` |
| pandas / PyArrow | JSONL, Parquet y tablas | `python -c "import pandas,pyarrow"` |
| Streamlit | Visor web privado de documentos | Puerto 8501 |

El archivo **.devcontainer/Dockerfile** instala programas del sistema, **requirements.txt** define las bibliotecas Python y **.devcontainer/devcontainer.json** configura el entorno.

En Codespaces:

~~~bash
pwd
python --version
tesseract --list-langs
command -v pdfinfo
command -v pdftoppm
ollama --version
python -c "import PIL,pytesseract,pandas,streamlit; print('Listo')"
~~~

La lista de idiomas debe incluir `spa`. No necesitas instalar Ubuntu en tu computador para usar Codespaces.

## 2. Preparar EmbeddingGemma 2 en Codespaces

Ollama se ejecuta como servicio local dentro del Codespace. El modelo multimodal que usaremos es **embeddinggemma-2:440m**, compatible con imágenes y texto.

~~~bash
bash preparar_embeddinggemma.sh
~~~

El script comprueba Ollama, descarga el modelo y hace **dos pruebas reales**: una consulta de texto y una fotografía WebP. En ambas usa `input` como lista (`[entrada]`) y verifica un vector de 768 dimensiones. Comprueba también:

~~~bash
ollama list
curl -fsS http://127.0.0.1:11434/api/tags
~~~

**Diferencia clave:** Ollama ejecuta el servicio; EmbeddingGemma transforma texto e imágenes en vectores. El modelo 270m solo funciona con texto. Los modelos se guardan en la carpeta local de caché del espacio de trabajo, excluida del repositorio Git.

## 3. Instalación independiente en Ubuntu

Para Ubuntu local, abre una terminal:

~~~bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip \
  tesseract-ocr tesseract-ocr-spa ffmpeg poppler-utils
~~~

Desde una copia del kit:

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
~~~

Para instalar Ollama en Ubuntu sigue su documentación oficial en https://ollama.com/download/linux:

~~~bash
curl -fsSL https://ollama.com/install.sh -o /tmp/ollama-install.sh
sh /tmp/ollama-install.sh
ollama --version
ollama pull embeddinggemma-2:440m
~~~

Estos comandos son para **Ubuntu local**. En **Codespaces**, el programa está definido en Dockerfile; prepara el modelo con `bash preparar_embeddinggemma.sh`.

## 4. Comprender OCR y PSM

**OCR** significa reconocimiento óptico de caracteres: transforma píxeles en letras y números probables. **Tesseract** es el motor OCR; **pytesseract** es la interfaz de Python.

**PSM** significa *Page Segmentation Mode* (modo de segmentación de página). Es una instrucción sobre cómo organizar los bloques de texto, **no** una medida de confianza:

- **PSM 3:** diseño automático, útil al empezar con un documento completo con varios bloques.
- **PSM 6:** supone un bloque uniforme de texto, útil en una zona recortada.
- **PSM 7:** considera el recorte una **única línea**, útil para aislar la palabra VALLE del logotipo.
- **PSM 11:** intenta encontrar texto disperso, útil en letreros; puede mezclar columnas de tablas.

Ejemplo con la primera página del PDF elegido para S11:

~~~python
from PIL import Image
import pytesseract

pagina = Image.open("datos/raw/actas/secop_acta_728704921_pagina1.png")
texto = pytesseract.image_to_string(pagina, lang="spa", config="--psm 3")
print(texto)
~~~

### Ejemplo fotográfico: logotipo de la Lotería del Valle

En `datos/raw/fotos/eltiempo_023.webp` puedes leer el mensaje «Lotería del VALLE». Para reconocer las letras artísticas primero **recorta la palabra VALLE**, después compara `--psm 6`, `--psm 7` y `--psm 11`. El visor contiene controles para seleccionar región, tamaño y contraste. En el cuaderno puedes modificar `ZONA_VALLE`, `FACTOR` y `USAR_CONTRASTE` para reproducir el procedimiento en Python.

La escala y el contraste pueden mejorar o empeorar la lectura; una confianza alta de Tesseract no sustituye la comprobación con la imagen.

### Diagnosticar la llamada a EmbeddingGemma

Para generar vectores de imágenes, la API recibe `input` **como lista**. Para la práctica se utilizan los **bytes originales** WebP en Base64 y `"input": [{"image": imagen64}]`. La conversión a JPEG RGB en memoria es una transformación opcional que puede compararse con los bytes originales. Prueba siempre una imagen antes del lote. Si Ollama rechaza una petición HTTP, debes mostrar `respuesta.status_code` y `respuesta.text` para conocer el mensaje concreto del servidor. **No cambies a un modelo solo textual para evitar el problema**.

~~~python
from pathlib import Path
import base64, requests

ruta = Path("datos/raw/fotos/eltiempo_023.webp")
imagen64 = base64.b64encode(ruta.read_bytes()).decode("ascii")
r = requests.post(
    "http://127.0.0.1:11434/api/embed",
    json={"model": "embeddinggemma-2:440m", "input": [{"image": imagen64}]},
    timeout=240,
)
if not r.ok:
    raise RuntimeError(f"HTTP {r.status_code}: {r.text[:1500]}")
print("Dimensiones:", len(r.json()["embeddings"][0]))
~~~

**Interpretación:** `input` contiene **una lista de entradas**, por eso `embeddings` devuelve una lista de vectores y tomamos `embeddings[0]`. Si obtienes 768 dimensiones puedes continuar; si aparece HTTP 400, la línea del error ahora incluye el motivo comunicado por Ollama. El archivo fuente no se altera durante la conversión.

El archivo PDF original está en `datos/raw/actas_pdf/secop_acta_728704921.pdf`. En la primera página aparecen **ACTA DE INICIO, CONTRATO 006-2026, VALOR DEL CONTRATO, DURACIÓN y FORMA DE PAGO**. Debes comprobar cada respuesta del OCR contra los píxeles, especialmente cuando se mezclan columnas.

Poppler aporta tres utilidades distintas: `pdfinfo` cuenta páginas, `pdftoppm` genera una imagen de la página elegida y `pdftotext` busca texto seleccionable dentro del PDF. Ninguna de ellas es un modelo de reconocimiento visual.

## 5. Transcripción con Faster-Whisper

Faster-Whisper permite reconocimiento automático del habla (ASR) en CPU. El modelo `tiny` es útil para experimentar con varias voces:

~~~python
from faster_whisper import WhisperModel

modelo = WhisperModel("tiny", device="cpu", compute_type="int8")
segmentos, info = modelo.transcribe(
    "datos/derived/audios/voz_01.wav", language="es"
)
for s in segmentos:
    print(s.start, s.end, s.text)
~~~

Primero prepara las voces humanas autorizadas de MINDS-14 con el botón del visor. Compara la predicción de Whisper con la transcripción humana del **mismo** audio antes de calcular WER, la tasa de error de palabras.

## 6. Visor documental Streamlit

En Codespaces:

~~~bash
bash abrir_visor.sh
~~~

Abre **Puertos → 8501 → Abrir vista previa** y conserva la visibilidad **Private**. El visor permite elegir un PDF completo, seleccionar su página, comparar el texto OCR con la página y abrir fotografías o audios.

## 7. Comprobaciones habituales

| Situación | Verificación |
|---|---|
| No aparece idioma español | `tesseract --list-langs` debe incluir `spa` |
| Falta un paquete Python | `python -m pip install -r requirements.txt` |
| Visor no responde | `bash abrir_visor.sh` y puerto privado 8501 |
| Ollama no responde | `bash iniciar_ollama.sh` y puerto local 11434 |
| Modelo 440m no está en la lista | `bash preparar_embeddinggemma.sh` y `ollama list` |
| El OCR no detecta un valor | Revisa la página y compara PSM 3, 6 y 11 |
| Whisper tarda | Procesa primero pocas voces en CPU |
| JSONL y Parquet difieren | Reabre los archivos y compara datos y hashes |

**Fuentes oficiales:** [Tesseract](https://tesseract-ocr.github.io/) · [Poppler](https://poppler.freedesktop.org/) · [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) · [Ollama](https://ollama.com/download/linux).
