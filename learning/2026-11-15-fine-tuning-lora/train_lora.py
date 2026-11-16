"""LoRA / QLoRA supervised fine-tuning (SFT) with Hugging Face TRL.

- NVIDIA GPU (e.g. Colab T4):  QLoRA  = base weights in 4-bit + small LoRA adapters
- Mac (Apple Silicon) / CPU:   LoRA   = base weights in fp32/fp16 + small LoRA adapters
  (bitsandbytes 4-bit does not run on Apple Silicon, so QLoRA is CUDA-only)

Usage:
    python make_data.py
    python train_lora.py                      # default: Qwen/Qwen2.5-0.5B-Instruct
    python train_lora.py --model <hf-id> --epochs 3

Written against trl 1.14 / peft 0.21. APIs move fast; if a kwarg errors, check the TRL docs.
"""

import argparse

import torch
from datasets import load_dataset
from peft import LoraConfig
from transformers import BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct")
    p.add_argument("--out", default="out/lora-merchant")
    p.add_argument("--epochs", type=float, default=3)
    p.add_argument("--lr", type=float, default=2e-4)   # LoRA tolerates a much higher LR than full fine-tuning
    p.add_argument("--rank", type=int, default=16)
    return p.parse_args()


def main():
    args = parse_args()
    cuda = torch.cuda.is_available()

    # ---- 1. Data: held-out eval set is never trained on (W8: sealed test) ----
    ds = load_dataset("json", data_files={"train": "data/train.jsonl", "eval": "data/eval.jsonl"})

    # ---- 2. Base model loading: 4-bit on CUDA (QLoRA), plain on Mac/CPU (LoRA) ----
    quant = None
    if cuda:
        quant = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",            # 4-bit NormalFloat, the QLoRA paper's format
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
    dtype = "bfloat16" if cuda else "float32"

    # ---- 3. LoRA: freeze W, learn a low-rank update  W' = W + (alpha/r) * B @ A ----
    peft_config = LoraConfig(
        r=args.rank,               # rank of A/B; 8-64 is typical
        lora_alpha=2 * args.rank,  # scale of the update
        lora_dropout=0.05,
        target_modules="all-linear",  # attach adapters to every linear layer (q,k,v,o,gate,up,down)
        task_type="CAUSAL_LM",
    )

    # ---- 4. Training config ----
    cfg = SFTConfig(
        output_dir=args.out,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=8,
        gradient_accumulation_steps=2,      # effective batch = 16
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_steps=10,
        max_length=512,
        logging_steps=5,
        eval_strategy="epoch",              # watch eval loss: if it rises while train loss falls -> overfitting
        save_strategy="epoch",
        bf16=cuda,
        gradient_checkpointing=cuda,        # trade compute for memory
        report_to="none",
        model_init_kwargs={"dtype": dtype},
        # prompt-completion data => loss only on the assistant's answer (default behaviour)
    )

    trainer = SFTTrainer(
        model=args.model,                   # TRL loads it, applies quantization + LoRA
        args=cfg,
        train_dataset=ds["train"],
        eval_dataset=ds["eval"],
        quantization_config=quant,
        peft_config=peft_config,
    )
    trainer.model.print_trainable_parameters()  # expect well under 5% trainable
    trainer.train()

    # ---- 5. Save ONLY the adapter (a few MB), not the whole model ----
    trainer.save_model(args.out)
    print(f"adapter saved to {args.out}")


if __name__ == "__main__":
    main()
