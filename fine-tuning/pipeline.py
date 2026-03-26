#!/usr/bin/env python3
"""Run the full FunctionGemma fine-tuning pipeline.

Steps:
  1. Download model (if not already present)
  2. Generate training data (if not already present)
  3. Fine-tune
  4. Evaluate
"""

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def run(cmd: list[str], description: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}\n")
    result = subprocess.run(cmd, cwd=str(SCRIPT_DIR))
    if result.returncode != 0:
        print(f"\nFailed: {description} (exit code {result.returncode})")
        sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(description="Run the full fine-tuning pipeline")
    parser.add_argument("--use-lora", action="store_true",
                        help="Use LoRA for fine-tuning (less VRAM)")
    parser.add_argument("--epochs", type=int, default=3,
                        help="Training epochs (default: 3)")
    parser.add_argument("--batch-size", type=int, default=4,
                        help="Training batch size (default: 4)")
    parser.add_argument("--lr", type=float, default=2e-5,
                        help="Learning rate (default: 2e-5)")
    parser.add_argument("--examples-per-tool", type=int, default=4,
                        help="Training examples per tool (default: 4)")
    parser.add_argument("--skip-download", action="store_true",
                        help="Skip model download (already present)")
    parser.add_argument("--skip-generate", action="store_true",
                        help="Skip data generation (already present)")
    parser.add_argument("--skip-eval", action="store_true",
                        help="Skip evaluation after training")
    args = parser.parse_args()

    model_dir = SCRIPT_DIR / "model"
    data_dir = SCRIPT_DIR / "data" / "train.json"

    # Step 1: Download model
    if not args.skip_download and not (model_dir / "config.json").exists():
        run(
            [sys.executable, "download_model.py"],
            "Step 1/4: Downloading FunctionGemma 270M",
        )
    else:
        print("\n  Step 1/4: Model already present, skipping download")

    # Step 2: Generate training data
    if not args.skip_generate and not data_dir.exists():
        run(
            [sys.executable, "generate_training_data.py",
             "--examples-per-tool", str(args.examples_per_tool)],
            "Step 2/4: Generating training data",
        )
    else:
        print("\n  Step 2/4: Training data already present, skipping generation")

    # Step 3: Fine-tune
    ft_cmd = [
        sys.executable, "fine_tune.py",
        "--epochs", str(args.epochs),
        "--batch-size", str(args.batch_size),
        "--lr", str(args.lr),
    ]
    if args.use_lora:
        ft_cmd.append("--use-lora")
    run(ft_cmd, "Step 3/4: Fine-tuning model")

    # Step 4: Evaluate
    if not args.skip_eval:
        run(
            [sys.executable, "evaluate.py", "--verbose"],
            "Step 4/4: Evaluating fine-tuned model",
        )
    else:
        print("\n  Step 4/4: Skipping evaluation")

    print(f"\n{'='*60}")
    print("  Pipeline complete!")
    print(f"  Fine-tuned model saved to: {SCRIPT_DIR / 'output'}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
