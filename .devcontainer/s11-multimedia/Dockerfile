FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm

# La imagen base trae una entrada Yarn ajena al laboratorio cuyo key puede caducar.
# Quitamos SOLO la fuente Yarn; conservamos la verificación de firmas de Debian.
RUN find /etc/apt/sources.list.d -type f -exec sed -i '/dl.yarnpkg.com/d' {} + \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       tesseract-ocr tesseract-ocr-spa ffmpeg poppler-utils espeak-ng fonts-dejavu-core \
       curl ca-certificates libgomp1 \
    && rm -rf /var/lib/apt/lists/*
