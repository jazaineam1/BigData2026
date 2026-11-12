#!/usr/bin/env bash
set -euo pipefail
if ! command -v ollama >/dev/null 2>&1; then
  echo 'Instalando Ollama desde su instalador oficial: https://ollama.com/download/linux'
  curl -fsSL https://ollama.com/install.sh -o /tmp/ollama-install-s11.sh
  sh /tmp/ollama-install-s11.sh
fi
if ! curl -fsS --max-time 3 http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  nohup ollama serve >/tmp/s11-ollama.log 2>&1 </dev/null &
  for i in $(seq 1 40); do
    if curl -fsS --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then break; fi
    sleep 1
  done
fi
curl -fsS --max-time 4 http://127.0.0.1:11434/api/tags >/dev/null || { echo 'No arrancó Ollama: revisar /tmp/s11-ollama.log'; exit 1; }
ollama pull embeddinggemma-2:270m
printf '\nModelo listo. Para modalidad imagen (opcional): ollama pull embeddinggemma-2:440m\n'
