"""Phase 6 - draw the 60-response audit sample (stratified, seeded, blinded).

5 responses from each of the 12 cells (2 models x 3 conditions x 2 prompt
types). The blind sheet shows ONLY the request and the response, in shuffled
order: no model name, no condition, no judge label. The key file maps
audit_id back to response_id and is only joined after the audit labels are
saved.

Outputs
  02_data/audit/audit_sample_blind.csv   (audit_id, prompt_type, goal, response)
  02_data/audit/audit_key.csv            (audit_id, response_id, cell)
"""
import json
import random

import pandas as pd

import config as C


def main():
    recs = [json.loads(l) for l in (C.DATA_DIR / "responses_locked.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    df = pd.DataFrame(recs)
    rng = random.Random(C.SEED)
    picked = []
    for m in C.TARGET_MODELS:
        for cond in C.CONDITION_ORDER:
            for pt in C.PROMPT_TYPES:
                cell = sorted(df[(df.model_key == m) & (df.condition == cond) & (df.prompt_type == pt)]["response_id"])
                assert len(cell) == C.N_PAIRS, (m, cond, pt, len(cell))
                picked += rng.sample(cell, C.AUDIT_PER_CELL)
    assert len(picked) == len(set(picked)) == 60
    rng.shuffle(picked)

    sub = df.set_index("response_id").loc[picked].reset_index()
    sub.insert(0, "audit_id", [f"A{n:02d}" for n in range(1, len(sub) + 1)])
    out = C.DATA_DIR / "audit"
    out.mkdir(exist_ok=True)
    sub[["audit_id", "prompt_type", "goal", "response"]].to_csv(out / "audit_sample_blind.csv", index=False)
    sub[["audit_id", "response_id", "model_key", "condition", "prompt_type", "pair_id"]].to_csv(out / "audit_key.csv", index=False)
    print("audit sample:", len(sub), "| per cell:",
          sub.groupby(["model_key", "condition", "prompt_type"]).size().unique().tolist())


if __name__ == "__main__":
    main()
