"""Phase 2 - select 20 lower-risk harmful prompts + their 20 matched benign prompts.

Rule-based and reproducible: documented exclusion rules, then a seeded
stratified sample. Also draws 4 pilot pairs from the eligible behaviours that
were NOT selected, so the final 20 are never touched before the freeze.

Outputs
  02_data/source/harmful-behaviors.csv, benign-behaviors.csv  (verbatim copies)
  02_data/selected_prompts.csv
  02_data/pilot/pilot_prompts.csv
  01_protocol/prompt_selection_log.csv  (all 100 behaviours with status + rule)
"""
import glob
import random
import shutil

import pandas as pd

import config as C


def main():
    snap = glob.glob(str(C.HF_CACHE / "datasets--JailbreakBench--JBB-Behaviors" / "snapshots" / C.DATASET["revision"]))[0]
    src_dir = C.DATA_DIR / "source"
    src_dir.mkdir(parents=True, exist_ok=True)
    for name in ["harmful-behaviors.csv", "benign-behaviors.csv"]:
        shutil.copyfile(f"{snap}/data/{name}", src_dir / name)
    harm = pd.read_csv(src_dir / "harmful-behaviors.csv")
    ben = pd.read_csv(src_dir / "benign-behaviors.csv")

    # --- integrity of the harmful/benign matching --------------------------
    assert len(harm) == len(ben) == 100
    assert (harm["Index"].values == ben["Index"].values).all()
    assert (harm["Category"].values == ben["Category"].values).all()
    # behaviour names match row by row (whitespace-normalised: row 67 has a double space upstream)
    norm = lambda s: s.str.split().str.join(" ")
    assert (norm(harm["Behavior"]).values == norm(ben["Behavior"]).values).all()

    # --- apply exclusion rules -------------------------------------------
    log = []
    for _, r in harm.iterrows():
        idx, cat = int(r["Index"]), r["Category"]
        if cat in C.EXCLUDED_CATEGORIES:
            rule = C.EXCLUDED_CATEGORIES[cat]
        else:
            rule = C.EXCLUDED_BEHAVIOURS.get(idx, "")
        log.append({"jbb_index": idx, "category": cat, "behavior": r["Behavior"],
                    "status": "excluded" if rule else "eligible", "rule": rule})
    log = pd.DataFrame(log)
    eligible = log[log["status"] == "eligible"]

    # --- quota: 3 per retained category, +1 for the two largest pools ------
    pool = {c: sorted(eligible[eligible["category"] == c]["jbb_index"]) for c in C.RETAINED_CATEGORY_ORDER}
    quota = {c: C.BASE_QUOTA_PER_CATEGORY for c in C.RETAINED_CATEGORY_ORDER}
    extra = C.N_PAIRS - sum(quota.values())
    for c in sorted(C.RETAINED_CATEGORY_ORDER, key=lambda c: (-len(pool[c]), C.RETAINED_CATEGORY_ORDER.index(c)))[:extra]:
        quota[c] += 1
    assert sum(quota.values()) == C.N_PAIRS
    assert all(len(pool[c]) >= quota[c] for c in pool)

    rng = random.Random(C.SEED)
    selected = []
    for c in C.RETAINED_CATEGORY_ORDER:
        selected += sorted(rng.sample(pool[c], quota[c]))

    # --- pilot pairs: eligible but NOT selected, 4 distinct categories -----
    remaining = {c: [i for i in pool[c] if i not in selected] for c in C.RETAINED_CATEGORY_ORDER}
    pilot_cats = [c for c in C.RETAINED_CATEGORY_ORDER if remaining[c]][: C.N_PILOT_PAIRS]
    pilot = [rng.choice(remaining[c]) for c in pilot_cats]
    assert len(pilot) == C.N_PILOT_PAIRS and not set(pilot) & set(selected)

    def build(indices, prefix):
        rows = []
        for n, idx in enumerate(indices, 1):
            h, b = harm.iloc[idx], ben.iloc[idx]
            assert int(h["Index"]) == idx == int(b["Index"])
            rows.append({
                "pair_id": f"{prefix}{n:02d}", "jbb_index": idx,
                "category": h["Category"], "behavior": h["Behavior"],
                "jbb_source_harmful": h["Source"],
                "harmful_goal": h["Goal"], "harmful_target": h["Target"],
                "benign_goal": b["Goal"], "benign_target": b["Target"],
            })
        return pd.DataFrame(rows)

    sel_df, pilot_df = build(selected, "P"), build(pilot, "X")
    sel_df.to_csv(C.DATA_DIR / "selected_prompts.csv", index=False)
    (C.DATA_DIR / "pilot").mkdir(exist_ok=True)
    pilot_df.to_csv(C.DATA_DIR / "pilot" / "pilot_prompts.csv", index=False)

    log["status"] = log.apply(
        lambda r: "selected" if r["jbb_index"] in selected else ("pilot" if r["jbb_index"] in pilot else r["status"]), axis=1)
    log["rule_text"] = log["rule"].map(C.EXCLUSION_RULES).fillna("")
    log.to_csv(C.PROTOCOL_DIR / "prompt_selection_log.csv", index=False)

    print("eligible pool per category:", {c: len(v) for c, v in pool.items()}, "total", sum(len(v) for v in pool.values()))
    print("quota:", quota)
    print("status counts:", log["status"].value_counts().to_dict())
    print("exclusions per rule:", log[log["rule"] != ""]["rule"].value_counts().sort_index().to_dict())
    print("\nSELECTED (20 pairs):")
    for _, r in sel_df.iterrows():
        print(f"  {r.pair_id} [{r.jbb_index:>2}] {r.category:27} {r.behavior}")
    print("\nPILOT (4 pairs, outside the final set):")
    for _, r in pilot_df.iterrows():
        print(f"  {r.pair_id} [{r.jbb_index:>2}] {r.category:27} {r.behavior}")


if __name__ == "__main__":
    main()
