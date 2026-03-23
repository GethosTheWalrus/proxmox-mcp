FROM python:3.14-slim

WORKDIR /app

# Install build deps
COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Non-root user for security
RUN useradd --create-home --shell /bin/bash mcp
USER mcp

ENTRYPOINT ["proxmox-mcp-server"]
