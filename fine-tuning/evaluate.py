#!/usr/bin/env python3
"""Evaluate a fine-tuned FunctionGemma model on the validation set.

Measures routing accuracy: does the model pick the correct tool?

Usage:
    python evaluate.py                          # evaluate fine-tuned model
    python evaluate.py --model-dir ./model      # evaluate base model (for comparison)
"""

import json
import random
import re
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoProcessor

MAX_TOOLS_PER_EXAMPLE = 5


def extract_tool_name(output: str) -> str | None:
    """Extract the tool name from FunctionGemma output."""
    match = re.search(r"call:(\w+)\{", output)
    if match:
        return match.group(1)
    return None


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate FunctionGemma tool routing")
    parser.add_argument("--model-dir", default="./output",
                        help="Path to fine-tuned model (default: ./output)")
    parser.add_argument("--val-data", default="./data/val.json",
                        help="Path to validation data (default: ./data/val.json)")
    parser.add_argument("--max-samples", type=int, default=None,
                        help="Max samples to evaluate (default: all)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print each prediction")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    model_dir = (script_dir / args.model_dir).resolve()
    val_path = (script_dir / args.val_data).resolve()

    if not model_dir.exists():
        print(f"Model not found at {model_dir}")
        return
    if not val_path.exists():
        print(f"Validation data not found at {val_path}")
        return

    print(f"Loading model from {model_dir}...")
    processor = AutoProcessor.from_pretrained(str(model_dir))

    use_gpu = torch.cuda.is_available()
    if use_gpu:
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    else:
        dtype = torch.float32

    model = AutoModelForCausalLM.from_pretrained(
        str(model_dir),
        dtype=dtype,
        device_map="auto" if use_gpu else None,
    )
    model.eval()

    with open(val_path) as f:
        examples = json.load(f)

    if args.max_samples:
        examples = examples[: args.max_samples]

    print(f"Evaluating {len(examples)} examples...")
    print()

    correct = 0
    total = 0
    category_stats: dict[str, dict[str, int]] = {}

    for i, example in enumerate(examples):
        messages = example["messages"]
        tools = example["tools"]
        expected = example["expected_tool"]

        # Subsample tools (same as training): keep expected + random distractors
        correct_tool = None
        other_tools = []
        for t in tools:
            if t["function"]["name"] == expected:
                correct_tool = t
            else:
                other_tools.append(t)
        if correct_tool and len(tools) > MAX_TOOLS_PER_EXAMPLE:
            distractors = random.sample(other_tools, min(MAX_TOOLS_PER_EXAMPLE - 1, len(other_tools)))
            tools = [correct_tool] + distractors
            random.shuffle(tools)

        # Generate
        inputs = processor.apply_chat_template(
            messages,
            tools=tools,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt",
        )
        with torch.no_grad():
            out = model.generate(
                **inputs.to(model.device),
                pad_token_id=processor.eos_token_id,
                max_new_tokens=64,
            )
        output = processor.decode(
            out[0][len(inputs["input_ids"][0]) :], skip_special_tokens=True
        )

        predicted = extract_tool_name(output)
        is_correct = predicted == expected
        if is_correct:
            correct += 1
        total += 1

        if args.verbose:
            user_query = messages[1]["content"]
            status = "OK" if is_correct else "MISS"
            print(f"[{status}] Q: {user_query}")
            print(f"      Expected: {expected}, Got: {predicted}")
            if not is_correct:
                print(f"      Raw: {output[:100]}")
            print()

        # Progress
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(examples)} - accuracy so far: {correct / total:.1%}")

    print()
    print(f"{'='*50}")
    print(f"Results: {correct}/{total} correct ({correct / total:.1%} accuracy)")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
