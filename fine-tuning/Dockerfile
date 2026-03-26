FROM python:3.11-slim

# Compute platform: cpu, cu124 (NVIDIA CUDA 12.4), rocm6.2 (AMD)
ARG COMPUTE_PLATFORM=cpu

WORKDIR /app

# Install PyTorch for the target platform, then the rest of the deps
COPY fine-tuning/requirements.txt .
RUN pip install --no-cache-dir \
        torch --index-url https://download.pytorch.org/whl/${COMPUTE_PLATFORM} && \
    pip install --no-cache-dir -r requirements.txt

# Copy the MCP tool source (needed by generate_training_data.py to extract tool schemas)
COPY src/proxmox_mcp/tools/ ./src/proxmox_mcp/tools/

# Copy fine-tuning scripts
COPY fine-tuning/*.py ./fine-tuning/

# Create output directories
RUN mkdir -p fine-tuning/model fine-tuning/data fine-tuning/output

WORKDIR /app/fine-tuning

ENTRYPOINT ["python3", "pipeline.py"]
