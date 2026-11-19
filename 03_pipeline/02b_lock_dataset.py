"""Phase 5 - lock the dataset of 240 responses.

Validates the raw run, writes the canonical locked file, its SHA-256, a flat
CSV copy for reading, and marks the locked files read-only.

Outputs
  02_data/responses_locked.jsonl   canonical dataset (one JSON record per response)
  02_data/responses_locked.sha256  checksum of the canonical file
  02_data/responses_locked.csv     flat copy (same rows; nested fields flattened)
  02_data/DATA_DICTIONARY.md       field descriptions
"""
import hashlib
import json
import os
import stat

import pandas as pd

import config as C

FIELDS = {
    "response_id": "model_key|pair_id|prompt_type|condition (unique key)",
    "model_key / model_repo / model_revision": "target model, Hugging Face repo and pinned commit hash",
    "pair_id / jbb_index / category / behavior": "prompt pair id (P01-P20) and its JBB-Behaviors index, category and behaviour name",
    "prompt_type": "harmful or benign (matched pair)",
    "condition": "direct, role_framing or prefix_steering",
    "goal / target": "original JBB Goal and Target strings",
    "user_prompt": "the single user message actually sent (template applied to goal/target)",
    "rendered_prompt / rendered_prompt_sha256": "full text after the chat template (includes the default system prompt) and its hash",
    "response": "model output, special tokens removed",
    "n_prompt_tokens / n_new_tokens": "token counts",
    "finish_reason": "eos = model stopped by itself; length = hit the 256-token cap",
    "gen_seconds": "wall-clock generation time",
    "gen_settings / seed": "frozen generation settings and project seed",
    "env": "device, dtype, GPU, library versions, OS",
    "timestamp_utc": "generation time (UTC)",
}


def main():
    raw = C.DATA_DIR / "responses_raw.jsonl"
    locked = C.DATA_DIR / "responses_locked.jsonl"
    if locked.exists():
        raise SystemExit("responses_locked.jsonl already exists - the dataset is locked.")
    recs = [json.loads(l) for l in raw.read_text(encoding="utf-8").splitlines() if l.strip()]
    df = pd.DataFrame(recs)
    assert len(df) == 240 and df.response_id.is_unique
    assert (df.groupby(["model_key", "condition", "prompt_type"]).size() == C.N_PAIRS).all()
    assert df.response.str.strip().ne("").all()

    order = {m: i for i, m in enumerate(C.TARGET_MODELS)}
    cond = {c: i for i, c in enumerate(C.CONDITION_ORDER)}
    recs.sort(key=lambda r: (order[r["model_key"]], r["pair_id"], C.PROMPT_TYPES.index(r["prompt_type"]), cond[r["condition"]]))
    locked.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs), encoding="utf-8")
    digest = hashlib.sha256(locked.read_bytes()).hexdigest()
    (C.DATA_DIR / "responses_locked.sha256").write_text(f"{digest}  responses_locked.jsonl\n")

    flat = pd.json_normalize(recs)
    flat.to_csv(C.DATA_DIR / "responses_locked.csv", index=False, encoding="utf-8-sig")
    (C.DATA_DIR / "DATA_DICTIONARY.md").write_text(
        "# Data dictionary: responses_locked.jsonl\n\n240 records = 2 models x 20 prompt pairs x 2 prompt types x 3 conditions.\n\n"
        "Content warning: the file contains model outputs to harmful requests (six lower-risk JBB-Behaviors categories only). It is published so that every reported number can be verified. Use it for safety research only; it is not training data.\n\n"
        "| Field | Meaning |\n|---|---|\n" + "".join(f"| `{k}` | {v} |\n" for k, v in FIELDS.items()), encoding="utf-8")
    for p in [locked, C.DATA_DIR / "responses_locked.sha256", C.DATA_DIR / "responses_locked.csv"]:
        os.chmod(p, stat.S_IREAD)

    print("locked 240 responses | sha256", digest)
    print("finish reasons:", df.finish_reason.value_counts().to_dict(), "| mean new tokens: %.1f" % df.n_new_tokens.mean())
    print("devices:", df.env.map(lambda e: e["device"] + "/" + e["dtype"]).value_counts().to_dict())
    print("time span:", df.timestamp_utc.min(), "->", df.timestamp_utc.max(), "| total gen seconds: %.0f" % df.gen_seconds.sum())


if __name__ == "__main__":
    main()
