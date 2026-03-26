FROM python:3.14-slim

WORKDIR /app

# Install build deps
COPY pyproject.toml .
COPY src/ src/

# Set INSTALL_ROUTER=true to include torch/transformers for tool routing
ARG INSTALL_ROUTER=false
RUN pip install --no-cache-dir --upgrade pip && \
    if [ "$INSTALL_ROUTER" = "true" ]; then \
        pip install --no-cache-dir ".[router]"; \
    else \
        pip install --no-cache-dir .; \
    fi

# Non-root user for security
RUN useradd --create-home --shell /bin/bash mcp
USER mcp

ENTRYPOINT ["proxmox-mcp-server"]
