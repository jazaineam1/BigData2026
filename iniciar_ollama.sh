#!/usr/bin/env bash
# Inicio idempotente de Ollama sin systemd; solo escucha dentro de Codespaces.
set -euo pipefail
export OLLAMA_HOST=127.0.0.1:11434

if ! command -v ollama >/dev/null 2>&1; then
  echo "ERROR: Ollama no está instalado en ESTE contenedor." >&2
  echo "Actualiza s11-estudiantes y ejecuta Codespaces: Rebuild Container." >&2
  echo "Consulta INSTALACION_UBUNTU.md para el arreglo sin reconstruir." >&2
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
  nohup env OLLAMA_HOST=127.0.0.1:11434 ollama serve \
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
