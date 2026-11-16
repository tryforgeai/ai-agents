"""Compare base model vs base+LoRA adapter on the held-out eval set.

Metric is behavioural, not loss: does the model output valid JSON with the right category?
Usage:
    python evaluate.py                                  # base model only
    python evaluate.py --adapter out/lora-merchant      # base + adapter
"""

import argparse
import json

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def load(model_id, adapter):
    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float32 if device == "cpu" else torch.float16)
    if adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter)
    return tok, model.to(device).eval(), device


def predict(tok, model, device, messages):
    enc = tok.apply_chat_template(messages, add_generation_prompt=True, return_dict=True, return_tensors="pt").to(device)
    ids = enc["input_ids"]
    with torch.no_grad():
        out = model.generate(**enc, max_new_tokens=40, do_sample=False)  # greedy: deterministic eval
    return tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True).strip()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct")
    p.add_argument("--adapter", default=None)
    p.add_argument("--data", default="data/eval.jsonl")
    a = p.parse_args()

    tok, model, device = load(a.model, a.adapter)
    rows = [json.loads(l) for l in open(a.data)]
    valid = correct = 0
    for r in rows:
        gold = json.loads(r["completion"][0]["content"])["category"]
        raw = predict(tok, model, device, r["prompt"])
        try:
            pred = json.loads(raw).get("category")
            valid += 1
        except (json.JSONDecodeError, AttributeError):
            pred = None
        correct += pred == gold
        if pred != gold:
            print(f"MISS  gold={gold:<13} got={raw[:60]!r}  note={r['prompt'][1]['content']!r}")

    n = len(rows)
    se = (correct / n * (1 - correct / n) / n) ** 0.5  # W8: standard error, differences < 2 SE are noise
    print(f"\n{'adapter' if a.adapter else 'base'}: valid JSON {valid}/{n} | accuracy {correct}/{n} "
          f"= {correct / n:.2%} (± {se:.2%} SE)")


if __name__ == "__main__":
    main()
