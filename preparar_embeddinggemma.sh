#!/usr/bin/env bash
# Descarga SOLO el modelo que admite texto e imágenes; la instalación del
# programa Ollama ya viene del Dockerfile.
set -euo pipefail
cd "$(dirname "$0")"

echo "[1/4] Comprobando Ollama..."
bash iniciar_ollama.sh

echo "[2/4] Comprobando recursos disponibles..."
df -h "$HOME" | tail -n 1

echo "[3/4] Descargando embeddinggemma-2:440m (solo primera vez)..."
ollama pull embeddinggemma-2:440m

echo "[4/4] Comprobando API y vector de 768 dimensiones..."
python - <<'PY'
import base64
import json
from pathlib import Path
from urllib.request import Request, urlopen

URL = "http://127.0.0.1:11434/api/embed"
MODELO = "embeddinggemma-2:440m"

def incrustar(entrada, nombre):
    # Una imagen o pregunta es UN elemento de la lista input.
    payload = {"model": MODELO, "input": [entrada]}
    req = Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=240) as response:
            result = json.load(response)
    except Exception as error:
        detalle = error.read().decode("utf-8", errors="replace") if hasattr(error, "read") else str(error)
        raise RuntimeError(f"La API no aceptó {nombre}: {detalle[:1500]}") from error
    vectors = result.get("embeddings", [])
    if len(vectors) != 1 or len(vectors[0]) != 768:
        raise RuntimeError(f"{nombre}: se esperaba un vector de 768 valores")
    print(f"OK {nombre}: {len(vectors[0])} dimensiones")

incrustar("Una fotografía de viviendas en una ladera.", "texto")
foto = Path("datos/raw/fotos/eltiempo_023.webp")
if not foto.is_file():
    raise FileNotFoundError(f"No existe la foto de prueba: {foto}")
b64 = base64.b64encode(foto.read_bytes()).decode("ascii")
incrustar({"image": b64}, foto.name)
print("OK: Ollama local + embeddinggemma-2:440m + texto e imagen, 768 dimensiones.")
PY
ollama list
echo "Listo. Regresa a 01_laboratorio.ipynb y ejecuta la celda de imágenes."
