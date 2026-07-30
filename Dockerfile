FROM python:3.13-slim AS builder

WORKDIR /app

COPY pyproject.toml .
COPY README.md .
COPY src/ src/

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install '.[router]' && \
    rm -rf /usr/local/lib/python3.13/site-packages/pip* /usr/local/lib/python3.13/site-packages/setuptools* /usr/local/lib/python3.13/site-packages/msgpack* && \
    apt-get purge -y --auto-remove build-essential && \
    rm -rf /var/lib/apt/lists/*

FROM debian:trixie-slim

WORKDIR /app

ENV PATH=/usr/local/bin:$PATH

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates libatomic1 libgomp1 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local /usr/local
COPY --from=builder /install /usr/local

# Non-root user for security
RUN useradd --create-home --shell /bin/bash mcp
USER mcp

ENTRYPOINT ["proxmox-mcp-server"]
