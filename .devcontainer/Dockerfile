FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm
# Herramientas del laboratorio: OCR, PDF, audio y extracción .tar.zst.
RUN set -eux; \
    find /etc/apt/sources.list.d -type f -exec sed -i '/dl.yarnpkg.com/d' {} +; \
    apt-get update; \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      tesseract-ocr tesseract-ocr-spa ffmpeg poppler-utils fonts-dejavu-core \
      curl ca-certificates libgomp1 zstd; \
    rm -rf /var/lib/apt/lists/*

# Instalación MANUAL OFICIAL de Ollama durante la construcción del contenedor.
# Evita install.sh, creación de usuarios de sistema y systemctl dentro de Codespaces.
# https://github.com/ollama/ollama/blob/main/docs/linux.mdx
RUN set -eux; \
    arch="$(dpkg --print-architecture)"; \
    case "$arch" in amd64|arm64) ;; *) echo "Arquitectura Ollama no soportada: $arch" >&2; exit 1;; esac; \
    curl --fail --location --show-error --silent --retry 3 \
      "https://ollama.com/download/ollama-linux-${arch}.tar.zst" \
      --output /tmp/ollama-linux.tar.zst; \
    test -s /tmp/ollama-linux.tar.zst; \
    tar --zstd -xf /tmp/ollama-linux.tar.zst -C /usr; \
    rm -f /tmp/ollama-linux.tar.zst; \
    test -x /usr/bin/ollama

# El servidor NO se arranca durante docker build.
# postStartCommand lo iniciará en el puerto local 127.0.0.1:11434.
ENV OLLAMA_HOST=127.0.0.1:11434
