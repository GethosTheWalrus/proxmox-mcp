#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load .env from project root if present
ENV_FILE="$SCRIPT_DIR/../.env"
if [[ -f "$ENV_FILE" ]]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

# ── Detect compute ───────────────────────────────────────
# Default to CPU — GPU training crashes the display on single-GPU systems
# (the RX 9070 is both display and compute, and ROCm takes exclusive access).
# Pass --gpu to explicitly enable GPU. 270M params trains fine on CPU.
USE_GPU=false
for arg in "$@"; do
    if [[ "$arg" == "--gpu" ]]; then
        USE_GPU=true
        break
    fi
done

if $USE_GPU && [[ -e /dev/kfd ]] && [[ -d /dev/dri ]]; then
    echo "AMD GPU requested — WARNING: may disrupt display on single-GPU systems!"
    export HSA_OVERRIDE_GFX_VERSION="${HSA_OVERRIDE_GFX_VERSION:-11.0.0}"
    PIP_EXTRA_INDEX="https://download.pytorch.org/whl/rocm6.2"
elif $USE_GPU && command -v nvidia-smi &>/dev/null && nvidia-smi &>/dev/null; then
    echo "NVIDIA GPU detected"
    PIP_EXTRA_INDEX="https://download.pytorch.org/whl/cu124"
else
    if $USE_GPU; then
        echo "No GPU detected — falling back to CPU"
    else
        echo "Using CPU (pass --gpu to enable GPU acceleration)"
    fi
    PIP_EXTRA_INDEX="https://download.pytorch.org/whl/cpu"
fi

# Strip --gpu from args before passing to pipeline
PIPELINE_ARGS=()
for arg in "$@"; do
    [[ "$arg" != "--gpu" ]] && PIPELINE_ARGS+=("$arg")
done

# ── Find Python 3.12 ─────────────────────────────────────
PYTHON_BIN=""
for candidate in python3.12 python312; do
    if command -v "$candidate" &>/dev/null; then
        PYTHON_BIN="$(command -v "$candidate")"
        break
    fi
done

if [[ -z "$PYTHON_BIN" ]]; then
    echo "ERROR: Python 3.12 is required but not found."
    echo "Install it with:  sudo dnf install python3.12   (Fedora)"
    echo "                  sudo apt install python3.12    (Debian/Ubuntu)"
    exit 1
fi

echo "Using $PYTHON_BIN ($("$PYTHON_BIN" --version 2>&1))"

# ── Virtual environment ──────────────────────────────────
VENV_DIR="$SCRIPT_DIR/.venv"
PLATFORM_MARKER="$VENV_DIR/.compute_platform"
# Recreate venv if the compute platform changed (e.g. switching between cpu/rocm)
if [[ -d "$VENV_DIR" ]] && [[ -f "$PLATFORM_MARKER" ]]; then
    PREV_PLATFORM="$(cat "$PLATFORM_MARKER")"
    if [[ "$PREV_PLATFORM" != "$PIP_EXTRA_INDEX" ]]; then
        echo "Compute platform changed ($PREV_PLATFORM → $PIP_EXTRA_INDEX), recreating venv..."
        rm -rf "$VENV_DIR"
    fi
fi
if [[ ! -d "$VENV_DIR" ]]; then
    echo "Creating virtual environment..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
echo "$PIP_EXTRA_INDEX" > "$PLATFORM_MARKER"

echo "Installing dependencies..."
pip install --upgrade pip
pip install torch --index-url "$PIP_EXTRA_INDEX"
pip install -r requirements.txt

# ── Run pipeline ─────────────────────────────────────────
echo ""
python pipeline.py "${PIPELINE_ARGS[@]+"${PIPELINE_ARGS[@]}"}"
