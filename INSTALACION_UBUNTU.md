# Instalación por tu cuenta en Ubuntu o Debian

En Codespaces estas herramientas ya están preparadas; esta guía explica cómo instalarlas independientemente.

## Python y entorno virtual

~~~bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python --version
~~~

## Tesseract (ejecutable del sistema) y español

~~~bash
sudo apt install -y tesseract-ocr tesseract-ocr-spa
tesseract --version
tesseract --list-langs
~~~

Debe aparecer `spa`. `pytesseract` es el adaptador Python; no instala el ejecutable por sí solo.

## PDF, audio y datos de prueba

~~~bash
sudo apt install -y ffmpeg poppler-utils espeak-ng fonts-dejavu-core
ffprobe -version | head -1
espeak-ng --version
pdftoppm -v
~~~

FFmpeg examina audio; Poppler rasteriza PDF; espeak-ng permite fabricar una voz sintética para practicar sin grabaciones privadas.

## Bibliotecas Python

Dentro de la carpeta de esta rama, con el entorno virtual activado:

~~~bash
python -m pip install -r requirements.txt
python -c 'from PIL import Image; import pytesseract, faster_whisper, requests, pyarrow, streamlit; print("Instalación Python: OK")'
~~~

Pillow abre/crea píxeles; pytesseract llama Tesseract; faster-whisper reconoce voz con CPU; requests consulta Ollama; PyArrow guarda Parquet; Streamlit construye una interfaz opcional.

## Ollama y modelo de embeddings

Revisa la documentación en https://ollama.com/download/linux y el instalador antes de ejecutarlo:

~~~bash
curl -fsSL https://ollama.com/install.sh -o /tmp/ollama-install-s11.sh
sh /tmp/ollama-install-s11.sh
ollama --version
ollama pull embeddinggemma-2:270m
ollama list
curl -fsS http://127.0.0.1:11434/api/tags
~~~

Si Ollama no responde, ejecuta `ollama serve` en otra terminal. El modelo 270m en esta ruta recibe TEXTO; no transcribe directamente audio.

## Verificaciones independientes

~~~bash
python lab.py preparar
tesseract salidas/afiche_simulado.png stdout -l spa --psm 6
python lab.py ocr
python lab.py asr
python lab.py evaluar-asr
python lab.py extraer
python lab.py indexar
python lab.py buscar --consulta "¿Cuántos contratos?"
python verificar_independiente.py --caso lab --modelo
~~~

Si no hay Internet la primera descarga de pesos de Whisper/Ollama puede fallar. Nunca utilices un hash o similitud de vectores como certificado de verdad.

Referencias: https://tesseract-ocr.github.io/tessdoc/Installation.html · https://github.com/SYSTRAN/faster-whisper · https://ollama.com/download/linux
