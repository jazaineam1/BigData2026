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
import json
from urllib.request import Request, urlopen

req = Request(
    "http://127.0.0.1:11434/api/embed",
    data=json.dumps({"model": "embeddinggemma-2:440m",
                     "input": "Una fotografía de viviendas en una ladera."}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urlopen(req, timeout=240) as response:
    data = json.load(response)
vectors = data.get("embeddings", [])
if len(vectors) != 1 or len(vectors[0]) != 768:
    raise RuntimeError("La API respondió, pero no produjo un vector de 768 valores.")
print("OK: Ollama local + embeddinggemma-2:440m + 768 dimensiones.")
PY
ollama list
echo "Listo. Regresa a 01_laboratorio.ipynb y ejecuta la celda de imágenes."
