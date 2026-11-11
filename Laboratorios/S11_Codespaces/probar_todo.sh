#!/usr/bin/env bash
# Comprobación reproducible de la recuperación S11.
# --ligero: OCR real, proyecto TXT, Parquet, integridad y tests (sin bajar modelos).
# --completo: añade ASR Whisper real, Ollama EmbeddingGemma2 y consulta de modelo.
set -euo pipefail
cd "$(dirname "$0")"
MODO="--ligero"
if [[ "$#" -ge 1 ]]; then MODO="$1"; fi
if [[ "$MODO" != "--ligero" && "$MODO" != "--completo" ]]; then
  echo "Uso: bash probar_todo.sh [--ligero|--completo]" >&2
  exit 2
fi
TMP="$(mktemp -d -t s11-transferencia-XXXXXXXX)"
trap 'rm -rf "$TMP"' EXIT
echo "[1] Comprobando configuración y pruebas unitarias"
python -m unittest -q test_lab test_proyecto
echo "[2] Ejecutando OCR de ejemplo verdadero"
python lab.py preparar
python lab.py ocr
python proyecto.py iniciar --destino "$TMP/proyecto"
printf 'Documento simulado de ejemplo: valor de 320 mil pesos.\n' > "$TMP/proyecto/entradas/textos/ejemplo.txt"
python proyecto.py plan --config "$TMP/proyecto/config.json"
python proyecto.py procesar --config "$TMP/proyecto/config.json"
python proyecto.py auditar --config "$TMP/proyecto/config.json"
if [[ "$MODO" == "--ligero" ]]; then
  echo "OK modo ligero: OCR real, catálogo, Parquet, auditoría y pruebas; Whisper/Ollama no probados."
  exit 0
fi
echo "[3] Ejecutando Whisper real, no sustituto de prueba"
python lab.py asr
python lab.py evaluar-asr
python lab.py extraer
echo "[4] Preparando Ollama y EmbeddingGemma 2 local"
bash iniciar_ollama.sh
python lab.py indexar
python lab.py buscar --consulta "¿Cuál es el valor mencionado?"
echo "[5] Indexando el proyecto transferible con embeddings reales"
python proyecto.py indexar --config "$TMP/proyecto/config.json"
python proyecto.py buscar --config "$TMP/proyecto/config.json" --consulta "¿Qué documento menciona un valor?"
python proyecto.py auditar --config "$TMP/proyecto/config.json"
echo "OK modo completo: OCR y ASR reales, Ollama local, índice, consulta, Parquet y auditoría."
