#!/usr/bin/env bash
# Inicia el visor al abrir Codespaces, sin abrir el puerto al público.
set -euo pipefail
cd "$(dirname "$0")"
if curl -fsS --max-time 2 http://127.0.0.1:8501/_stcore/health >/dev/null 2>&1; then
  echo "Visor S11 ya disponible en el puerto privado 8501"
  exit 0
fi
nohup streamlit run visor_fuentes.py \
  --server.headless true \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  > /tmp/s11-visor.log 2>&1 </dev/null &
echo "Iniciando visor S11 en el puerto privado 8501 (abre Puertos → 8501 → Vista previa)"
