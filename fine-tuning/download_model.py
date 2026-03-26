#!/usr/bin/env python3
"""Download the FunctionGemma 270M model from Hugging Face.

Requires a Hugging Face account with Gemma license accepted:
  1. Go to https://huggingface.co/google/functiongemma-270m-it
  2. Accept the license agreement
  3. Create an access token at https://huggingface.co/settings/tokens

Usage:
    # With HF_TOKEN env var:
    HF_TOKEN=hf_xxx python download_model.py

    # Or login first:
    huggingface-cli login
    python download_model.py
"""

import os
import sys
from pathlib import Path


def main():
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("huggingface_hub not installed. Run: pip install huggingface_hub")
        sys.exit(1)

    model_id = "google/functiongemma-270m-it"
    output_dir = Path(__file__).resolve().parent / "model"

    token = os.environ.get("HF_TOKEN")
    if not token:
        # Try to use cached login
        try:
            from huggingface_hub import HfFolder
            token = HfFolder.get_token()
        except Exception:
            pass

    if not token:
        print("No Hugging Face token found.")
        print("Either set HF_TOKEN env var or run: huggingface-cli login")
        print()
        print("You also need to accept the Gemma license at:")
        print(f"  https://huggingface.co/{model_id}")
        sys.exit(1)

    print(f"Downloading {model_id} to {output_dir}...")
    print("This is ~540MB and may take a few minutes.")
    print()

    snapshot_download(
        repo_id=model_id,
        local_dir=str(output_dir),
        token=token,
    )

    print(f"\nModel downloaded to {output_dir}")
    print("You can now run: python fine_tune.py")


if __name__ == "__main__":
    main()
