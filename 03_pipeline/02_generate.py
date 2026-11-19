"""Phase 4/5 - generate target-model responses (black-box, single turn).

For every model x prompt pair x prompt type (harmful/benign) x condition the
script sends ONE user message through the model's default chat template and
stores the response with full metadata. Greedy decoding, one sample per cell.

Usage
  python 02_generate.py --prompts ../02_data/pilot/pilot_prompts.csv --out ../02_data/pilot/pilot_responses.jsonl
  python 02_generate.py --prompts ../02_data/selected_prompts.csv   --out ../02_data/responses_raw.jsonl
The run is resume-safe: response_ids already present in --out are skipped.
"""
import argparse
import datetime
import gc
import hashlib
import json
import platform
import time
from pathlib import Path

import pandas as pd
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

import config as C


def load_model(repo, revision):
    tok = AutoTokenizer.from_pretrained(repo, revision=revision, cache_dir=C.HF_CACHE)
    use_cuda = torch.cuda.is_available()
    # GPU: weights in their stored precision (bfloat16). CPU fallback: float32.
    dtype = "auto" if use_cuda else torch.float32
    try:
        model = AutoModelForCausalLM.from_pretrained(repo, revision=revision, cache_dir=C.HF_CACHE, dtype=dtype)
    except TypeError:  # older transformers
        model = AutoModelForCausalLM.from_pretrained(repo, revision=revision, cache_dir=C.HF_CACHE, torch_dtype=dtype)
    model.to("cuda" if use_cuda else "cpu").eval()
    return tok, model


def build_user_prompt(condition, goal, target):
    return C.CONDITIONS[condition].format(goal=goal, target=target)


@torch.no_grad()
def generate(tok, model, user_prompt):
    messages = [{"role": "user", "content": user_prompt}]
    if C.GEN["system_prompt"] is not None:
        messages.insert(0, {"role": "system", "content": C.GEN["system_prompt"]})
    rendered = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tok([rendered], return_tensors="pt").to(model.device)
    t0 = time.time()
    out = model.generate(
        **inputs,
        do_sample=C.GEN["do_sample"],
        max_new_tokens=C.GEN["max_new_tokens"],
        repetition_penalty=C.GEN["repetition_penalty"],
        temperature=None, top_p=None, top_k=None,
    )
    new_ids = out[0][inputs.input_ids.shape[1]:]
    eos = model.generation_config.eos_token_id
    eos = set(eos if isinstance(eos, (list, tuple)) else [eos])
    finish = "eos" if len(new_ids) and new_ids[-1].item() in eos else "length"
    return {
        "rendered_prompt": rendered,
        "response": tok.decode(new_ids, skip_special_tokens=True).strip(),
        "n_prompt_tokens": int(inputs.input_ids.shape[1]),
        "n_new_tokens": int(len(new_ids)),
        "finish_reason": finish,
        "gen_seconds": round(time.time() - t0, 3),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--models", nargs="*", default=list(C.TARGET_MODELS))
    args = ap.parse_args()

    prompts = pd.read_csv(args.prompts)
    out_path = Path(args.out)
    done = set()
    if out_path.exists():
        done = {json.loads(l)["response_id"] for l in out_path.read_text(encoding="utf-8").splitlines() if l.strip()}
    print(f"prompts: {len(prompts)} pairs | already done: {len(done)} | cuda: {torch.cuda.is_available()}")

    torch.manual_seed(C.SEED)
    for mkey in args.models:
        spec = C.TARGET_MODELS[mkey]
        todo = [(r, pt, cond) for _, r in prompts.iterrows() for pt in C.PROMPT_TYPES for cond in C.CONDITION_ORDER
                if f"{mkey}|{r.pair_id}|{pt}|{cond}" not in done]
        if not todo:
            continue
        tok, model = load_model(spec["repo"], spec["revision"])
        env = {
            "device": str(model.device), "dtype": str(model.dtype),
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "torch": torch.__version__, "transformers": transformers.__version__,
            "python": platform.python_version(), "os": platform.platform(),
        }
        print(f"[{mkey}] {spec['repo']}@{spec['revision']} on {env['device']} ({env['dtype']}), {len(todo)} generations")
        with out_path.open("a", encoding="utf-8") as fh:
            for n, (r, pt, cond) in enumerate(todo, 1):
                goal, target = r[f"{pt}_goal"], r[f"{pt}_target"]
                user_prompt = build_user_prompt(cond, goal, target)
                g = generate(tok, model, user_prompt)
                rec = {
                    "response_id": f"{mkey}|{r.pair_id}|{pt}|{cond}",
                    "model_key": mkey, "model_repo": spec["repo"], "model_revision": spec["revision"],
                    "pair_id": r.pair_id, "jbb_index": int(r.jbb_index), "category": r.category, "behavior": r.behavior,
                    "prompt_type": pt, "condition": cond,
                    "goal": goal, "target": target, "user_prompt": user_prompt,
                    "rendered_prompt_sha256": hashlib.sha256(g["rendered_prompt"].encode("utf-8")).hexdigest(),
                    "rendered_prompt": g["rendered_prompt"],
                    "response": g["response"],
                    "n_prompt_tokens": g["n_prompt_tokens"], "n_new_tokens": g["n_new_tokens"],
                    "finish_reason": g["finish_reason"], "gen_seconds": g["gen_seconds"],
                    "gen_settings": C.GEN, "seed": C.SEED, "env": env,
                    "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                }
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fh.flush()
                if n % 20 == 0 or n == len(todo):
                    print(f"  {n}/{len(todo)}  last: {g['n_new_tokens']} tok in {g['gen_seconds']}s ({g['finish_reason']})", flush=True)
        del model, tok
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    n = sum(1 for l in out_path.read_text(encoding="utf-8").splitlines() if l.strip())
    print(f"done: {n} responses in {out_path}")


if __name__ == "__main__":
    main()
