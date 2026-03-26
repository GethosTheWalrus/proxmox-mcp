# FunctionGemma 270M Fine-Tuning for Proxmox MCP Tool Routing

Fine-tune [FunctionGemma 270M](https://huggingface.co/google/functiongemma-270m-it) to accurately route natural language queries to the correct Proxmox MCP tool (285 tools across 11 categories).

## Overview

FunctionGemma 270M is a lightweight function-calling model (~540MB fp16) that can run alongside the MCP server in the same Docker container. Out of the box it achieves ~62% accuracy on general function calling benchmarks — fine-tuning on domain-specific data pushes this to ~85%+.

## Prerequisites

1. **Python 3.12** — PyTorch does not yet publish wheels for Python 3.13+. Install with:
   - Fedora: `sudo dnf install python3.12`
   - Ubuntu/Debian: `sudo apt install python3.12 python3.12-venv`
2. **HuggingFace account** with [Gemma license accepted](https://huggingface.co/google/functiongemma-270m-it)
3. **HuggingFace token** — create one at https://huggingface.co/settings/tokens

### GPU Support (optional but recommended)

Fine-tuning works on CPU but is slow. For GPU acceleration, install the drivers for your platform:

**AMD (ROCm) — Fedora:**
```bash
sudo tee /etc/yum.repos.d/rocm.repo <<'EOF'
[ROCm-6.2]
name=ROCm 6.2
baseurl=https://repo.radeon.com/rocm/rhel9/6.2/main
enabled=1
gpgcheck=1
gpgkey=https://repo.radeon.com/rocm/rocm.gpg.key
EOF

sudo dnf install rocm-hip-runtime

# Add ROCm libraries to the linker path
echo '/opt/rocm-6.2.0/lib' | sudo tee /etc/ld.so.conf.d/rocm.conf
sudo ldconfig

sudo usermod -aG render,video $USER
# Log out and back in for group changes
```

**AMD (ROCm) — Ubuntu/Debian:**
```bash
sudo mkdir --parents --mode=0755 /etc/apt/keyrings
wget https://repo.radeon.com/rocm/rocm.gpg.key -O - | gpg --dearmor | sudo tee /etc/apt/keyrings/rocm.gpg > /dev/null
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/rocm.gpg] https://repo.radeon.com/rocm/apt/6.2 jammy main" | sudo tee /etc/apt/sources.list.d/rocm.list
sudo apt update && sudo apt install rocm-hip-runtime

# Add ROCm libraries to the linker path
echo '/opt/rocm-6.2.0/lib' | sudo tee /etc/ld.so.conf.d/rocm.conf
sudo ldconfig

sudo usermod -aG render,video $USER
```

**NVIDIA:**
```bash
# Install the NVIDIA driver and CUDA toolkit for your distro
# See: https://developer.nvidia.com/cuda-downloads
```

> **RDNA4 GPUs (RX 9000 series):** Add `HSA_OVERRIDE_GFX_VERSION=11.0.0` to your `.env` — PyTorch ROCm doesn't have native RDNA4 kernels yet but runs fine under the RDNA3 compatibility layer.

## Quick Start (Docker)

Run the entire pipeline with a single command:

```bash
HF_TOKEN=hf_your_token docker compose --profile fine-tune up --build
```

This will download the model, generate training data, fine-tune, and evaluate — all inside a container. Results are persisted to `model/`, `data/`, and `output/` via volume mounts.

Set `COMPUTE_PLATFORM` in your `.env` to control the PyTorch build:
| Value | Platform |
|-------|----------|
| `cpu` (default) | CPU only |
| `cu124` | NVIDIA CUDA 12.4 |
| `rocm6.2` | AMD ROCm 6.2 |

With options:
```bash
# Use LoRA (less VRAM)
docker compose --profile fine-tune run --rm fine-tune --use-lora

# Custom hyperparameters
docker compose --profile fine-tune run --rm fine-tune --epochs 5 --batch-size 2 --use-lora
```

## Quick Start (Native with GPU)

The `run.sh` script auto-detects your GPU (AMD/NVIDIA/CPU), creates a virtual environment, installs the correct PyTorch, and runs the full pipeline:

```bash
cd fine-tuning
./run.sh                    # auto-detect GPU, run full pipeline
./run.sh --use-lora         # with LoRA
./run.sh --epochs 5         # custom epochs
```

It sources your `.env` automatically for `HF_TOKEN` and `HSA_OVERRIDE_GFX_VERSION`.

## Manual Setup

```bash
cd fine-tuning
pip install -r requirements.txt
```

Run the full pipeline manually:
```bash
export HF_TOKEN=hf_your_token
python pipeline.py              # full pipeline
python pipeline.py --use-lora   # with LoRA
python pipeline.py --help       # all options
```

Or run each step individually:

## Workflow

### 1. Download the Model

```bash
export HF_TOKEN="hf_your_token_here"
python download_model.py
```

This downloads the model to `./model/`. You must accept the Gemma license on HuggingFace first.

### 2. Generate Training Data

```bash
python generate_training_data.py
```

Generates synthetic training examples in `./data/`:
- `training_data.json` — all examples
- `train.json` — 90% training split
- `val.json` — 10% validation split

Each example pairs a natural language query with the correct tool, presented alongside a context window of related tools (same category + random others) to teach the model to discriminate.

Options:
```bash
python generate_training_data.py --examples-per-tool 6 --seed 42
```

### 3. Fine-Tune

```bash
python fine_tune.py
```

Key options:
```bash
# With LoRA (less memory, faster, recommended for single GPU)
python fine_tune.py --use-lora

# Custom hyperparameters
python fine_tune.py --epochs 5 --lr 1e-5 --batch-size 2

# Full options
python fine_tune.py --help
```

The fine-tuned model is saved to `./output/`.

| Parameter | Default | Notes |
|-----------|---------|-------|
| `--epochs` | 3 | 3-5 is usually sufficient |
| `--lr` | 2e-5 | Lower (1e-5) for full fine-tune, higher (5e-5) for LoRA |
| `--batch-size` | 4 | Reduce if OOM |
| `--grad-accum` | 4 | Effective batch = batch-size × grad-accum |
| `--use-lora` | off | Recommended for <24GB VRAM |

### 4. Evaluate

```bash
# Evaluate fine-tuned model
python evaluate.py --verbose

# Compare with base model
python evaluate.py --model-dir ./model --verbose
```

## Directory Structure

```
fine-tuning/
├── README.md
├── Dockerfile             # GPU-enabled Docker image
├── requirements.txt
├── pipeline.py            # Single-command full pipeline
├── download_model.py      # Download FunctionGemma 270M
├── generate_training_data.py  # Synthetic training data generator
├── fine_tune.py           # Fine-tuning script (full + LoRA)
├── evaluate.py            # Accuracy evaluation
├── model/                 # Downloaded base model (gitignored)
├── data/                  # Generated training data
│   ├── training_data.json
│   ├── train.json
│   └── val.json
└── output/                # Fine-tuned model (gitignored)
```

## Training Data Format

Each example follows FunctionGemma's chat template:

```json
{
  "messages": [
    {
      "role": "developer",
      "content": "You are a Proxmox VE assistant. Given a user query, call the most appropriate tool."
    },
    {
      "role": "user",
      "content": "Show me all VMs on node proxmox1"
    }
  ],
  "tools": [
    {
      "name": "list_vms",
      "description": "List all VMs, optionally filtered by node",
      "parameters": { ... }
    }
  ],
  "expected_tool": "list_vms"
}
```

The model learns to output: `<start_function_call>call:list_vms{"node": "proxmox1"}<end_function_call>`

## Integration

After fine-tuning, the model can be integrated into the MCP server as a routing layer:

```python
from transformers import AutoModelForCausalLM, AutoProcessor

processor = AutoProcessor.from_pretrained("./fine-tuning/output")
model = AutoModelForCausalLM.from_pretrained("./fine-tuning/output")

# Route a user query to the right tool category
messages = [
    {"role": "developer", "content": "You are a Proxmox VE assistant..."},
    {"role": "user", "content": user_query},
]
inputs = processor.apply_chat_template(messages, tools=tool_schemas, ...)
output = model.generate(**inputs)
# Parse the tool name from output
```
