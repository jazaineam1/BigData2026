#!/usr/bin/env bash
# Inicio idempotente de Ollama sin systemd; solo escucha dentro de Codespaces.
set -euo pipefail
export OLLAMA_HOST=127.0.0.1:11434
# La carpeta de modelos se guarda en el espacio de trabajo, excluida de Git.
export OLLAMA_MODELS="${OLLAMA_MODELS:-/workspaces/BigData2026/.cache/ollama/models}"
mkdir -p "$OLLAMA_MODELS"

if ! command -v ollama >/dev/null 2>&1; then
  echo "ERROR: Ollama no está instalado en ESTE contenedor." >&2
  echo "Comprueba la configuración .devcontainer/Dockerfile del Codespace." >&2
  echo "Consulta la guía INSTALACION_UBUNTU.md." >&2
  exit 1
fi

if curl -fsS --max-time 2 "http://127.0.0.1:11434/api/tags" >/dev/null 2>&1; then
  echo "Ollama ya está funcionando en ${OLLAMA_HOST}"
  exit 0
fi

if pgrep -f '[o]llama serve' >/dev/null 2>&1; then
  echo "Ya existe un proceso ollama serve; comprobando API..."
else
  echo "Iniciando Ollama sin systemd..."
  nohup env OLLAMA_HOST=127.0.0.1:11434 OLLAMA_MODELS="$OLLAMA_MODELS" ollama serve \
    > /tmp/s11-ollama.log 2>&1 </dev/null &
fi

for intento in $(seq 1 40); do
  if curl -fsS --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "Ollama listo en http://127.0.0.1:11434 (solo acceso local)"
    exit 0
  fi
  sleep 1
done

echo "ERROR: Ollama no respondió; revisa el registro:" >&2
tail -n 50 /tmp/s11-ollama.log 2>/dev/null >&2 || true
exit 1
