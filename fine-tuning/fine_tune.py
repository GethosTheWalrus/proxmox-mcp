#!/usr/bin/env python3
"""Fine-tune FunctionGemma 270M on Proxmox MCP tool routing.

Based on Google's FunctionGemma fine-tuning recipe:
https://github.com/google-gemini/gemma-cookbook/blob/main/FunctionGemma/

Usage:
    # Generate training data first (if not already done):
    python generate_training_data.py

    # Fine-tune:
    python fine_tune.py

    # With custom options:
    python fine_tune.py --epochs 5 --batch-size 4 --lr 2e-5 --output-dir ./output
"""

import json
import os
import random
from pathlib import Path

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoModelForCausalLM,
    AutoProcessor,
    DataCollatorForSeq2Seq,
    TrainingArguments,
    Trainer,
)


class FunctionGemmaDataset(Dataset):
    """Dataset for FunctionGemma fine-tuning on tool routing.

    Each training example includes the correct tool plus a random subset of
    distractors, keeping total sequence length manageable. The full tool list
    in the JSON can be hundreds of entries; we subsample per __getitem__ call
    so the model sees different distractor sets each epoch.
    """

    MAX_TOOLS_PER_EXAMPLE = 5  # 1 correct + up to 4 distractors

    def __init__(self, data_path: str, processor, max_length: int = 2048):
        with open(data_path) as f:
            self.examples = json.load(f)
        self.processor = processor
        self.max_length = max_length

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        example = self.examples[idx]
        messages = example["messages"]
        tools = example["tools"]
        expected_tool = example["expected_tool"]

        # Subsample tools: always include the correct one + random distractors
        correct_tool = None
        other_tools = []
        for t in tools:
            if t.get("function", {}).get("name") == expected_tool:
                correct_tool = t
            else:
                other_tools.append(t)

        if correct_tool is None:
            # Fallback: if the correct tool isn't in the list, use all tools
            subset = tools[:self.MAX_TOOLS_PER_EXAMPLE]
        else:
            n_distractors = min(self.MAX_TOOLS_PER_EXAMPLE - 1, len(other_tools))
            distractors = random.sample(other_tools, n_distractors)
            subset = [correct_tool] + distractors
            random.shuffle(subset)

        # Build the expected output in FunctionGemma format
        target_output = f"<start_function_call>call:{expected_tool}{{}}<end_function_call>"

        # Apply chat template with the subsampled tools
        input_text = self.processor.apply_chat_template(
            messages,
            tools=subset,
            add_generation_prompt=True,
            tokenize=False,
        )

        # Full text = input + expected output
        full_text = input_text + target_output

        # Tokenize (no padding — batch_size=1 so padding is wasteful;
        # the 262K vocab makes padded logits extremely memory-hungry)
        encodings = self.processor(
            full_text,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )

        input_ids = encodings["input_ids"].squeeze()
        attention_mask = encodings["attention_mask"].squeeze()

        # Create labels: mask the input portion (set to -100), only train on the output
        input_only = self.processor(
            input_text,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )
        input_length = input_only["input_ids"].shape[1]

        labels = input_ids.clone()
        labels[:input_length] = -100  # Mask input tokens

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fine-tune FunctionGemma 270M")
    parser.add_argument("--model-dir", default="./model",
                        help="Path to the base model (default: ./model)")
    parser.add_argument("--train-data", default="./data/train.json",
                        help="Path to training data (default: ./data/train.json)")
    parser.add_argument("--val-data", default="./data/val.json",
                        help="Path to validation data (default: ./data/val.json)")
    parser.add_argument("--output-dir", default="./output",
                        help="Output directory for fine-tuned model (default: ./output)")
    parser.add_argument("--epochs", type=int, default=3,
                        help="Number of training epochs (default: 3)")
    parser.add_argument("--batch-size", type=int, default=1,
                        help="Training batch size (default: 1)")
    parser.add_argument("--lr", type=float, default=2e-5,
                        help="Learning rate (default: 2e-5)")
    parser.add_argument("--max-length", type=int, default=1024,
                        help="Max sequence length (default: 1024)")
    parser.add_argument("--gradient-accumulation-steps", type=int, default=8,
                        help="Gradient accumulation steps (default: 8)")
    parser.add_argument("--use-lora", action="store_true",
                        help="Use LoRA for parameter-efficient fine-tuning")
    parser.add_argument("--lora-r", type=int, default=16,
                        help="LoRA rank (default: 16)")
    parser.add_argument("--lora-alpha", type=int, default=32,
                        help="LoRA alpha (default: 32)")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    model_dir = (script_dir / args.model_dir).resolve()
    train_path = (script_dir / args.train_data).resolve()
    val_path = (script_dir / args.val_data).resolve()
    output_dir = (script_dir / args.output_dir).resolve()

    # Validate paths
    if not train_path.exists():
        print(f"Training data not found at {train_path}")
        print("Run 'python generate_training_data.py' first.")
        return
    if not model_dir.exists():
        print(f"Model not found at {model_dir}")
        print("Run 'python download_model.py' first.")
        return

    print(f"Loading model from {model_dir}...")
    processor = AutoProcessor.from_pretrained(str(model_dir))

    use_gpu = torch.cuda.is_available()
    if use_gpu:
        compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    else:
        compute_dtype = torch.float32

    model = AutoModelForCausalLM.from_pretrained(
        str(model_dir),
        dtype=compute_dtype,
        device_map="auto" if use_gpu else None,
    )

    # Optionally apply LoRA
    if args.use_lora:
        try:
            from peft import LoraConfig, get_peft_model, TaskType
        except ImportError:
            print("LoRA requested but 'peft' is not installed.")
            print("Install with: pip install peft")
            return

        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=args.lora_r,
            lora_alpha=args.lora_alpha,
            lora_dropout=0.05,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        )
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()

    # Load datasets
    print(f"Loading training data from {train_path}...")
    train_dataset = FunctionGemmaDataset(str(train_path), processor, args.max_length)
    print(f"  {len(train_dataset)} training examples")

    val_dataset = None
    if val_path.exists():
        print(f"Loading validation data from {val_path}...")
        val_dataset = FunctionGemmaDataset(str(val_path), processor, args.max_length)
        print(f"  {len(val_dataset)} validation examples")

    # Training arguments
    total_steps = (len(train_dataset) // args.batch_size // args.gradient_accumulation_steps) * args.epochs
    warmup_steps = max(1, int(total_steps * 0.1))

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.lr,
        warmup_steps=warmup_steps,
        weight_decay=0.01,
        logging_steps=10,
        eval_strategy="epoch" if val_dataset else "no",
        save_strategy="epoch",
        save_total_limit=2,
        bf16=use_gpu and torch.cuda.is_bf16_supported(),
        fp16=use_gpu and not torch.cuda.is_bf16_supported(),
        report_to="none",
        gradient_checkpointing=True,
        dataloader_pin_memory=use_gpu,
        remove_unused_columns=False,
        load_best_model_at_end=True if val_dataset else False,
        metric_for_best_model="eval_loss" if val_dataset else None,
    )

    # Enable gradient checkpointing to reduce activation memory
    model.gradient_checkpointing_enable()

    # Collator pads variable-length sequences to the longest in each batch
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=processor,
        model=model,
        padding=True,
        label_pad_token_id=-100,
    )

    # Train
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
    )

    print("Starting training...")
    trainer.train()

    # Save the fine-tuned model
    print(f"Saving fine-tuned model to {output_dir}...")
    trainer.save_model(str(output_dir))
    processor.save_pretrained(str(output_dir))

    print("Done! Fine-tuned model saved.")
    print(f"\nTo use in your MCP server, point to: {output_dir}")


if __name__ == "__main__":
    main()
