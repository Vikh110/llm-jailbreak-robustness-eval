"""Phase 4 - freeze models, prompts, settings and annotation rubric.

Writes 01_protocol/freeze_manifest.json with SHA-256 hashes of every input
that determines the experiment. After this file exists, no model, dataset,
prompt, transformation, setting or rubric line may change (plan constraint:
"No additional models, datasets or attack methods will be added after Phase 4").

`python 06_freeze.py --check` re-computes the hashes and fails on any drift.
`python 06_freeze.py --check --skip-weights` does the same without the ~5 GB of
model weights (used in CI): repo ids and pinned revisions are still compared,
only the SHA-256 of the weight files is not recomputed.
"""
import argparse
import datetime
import glob
import hashlib
import json
import sys
from importlib import metadata

import config as C

MANIFEST = C.PROTOCOL_DIR / "freeze_manifest.json"
FROZEN_FILES = [
    "03_pipeline/config.py",
    "03_pipeline/02_generate.py",
    "03_pipeline/03_judge.py",
    "03_pipeline/04_audit_sample.py",
    "02_data/selected_prompts.csv",
    "02_data/source/harmful-behaviors.csv",
    "02_data/source/benign-behaviors.csv",
    "01_protocol/01_research_question_and_threat_model.md",
    "01_protocol/03_labels_metrics_transformations_rubric.md",
]


def sha256(path, chunk=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def weights_hash(repo, revision):
    snap = C.HF_CACHE / ("models--" + repo.replace("/", "--")) / "snapshots" / revision
    files = sorted(glob.glob(str(snap / "*.safetensors")))
    assert files, f"no weights for {repo}@{revision}"
    return {p.split("\\")[-1].split("/")[-1]: sha256(p) for p in files}


def current_state(skip_weights=False):
    models = {}
    for key, spec in {**C.TARGET_MODELS, C.JUDGE_MODEL["key"]: C.JUDGE_MODEL}.items():
        models[key] = {"repo": spec["repo"], "revision": spec["revision"]}
        if not skip_weights:
            models[key]["weights_sha256"] = weights_hash(spec["repo"], spec["revision"])
    return {
        "files_sha256": {f: sha256(C.ROOT / f) for f in FROZEN_FILES},
        "dataset": C.DATASET,
        "models": models,
        "generation_settings": C.GEN,
        "judge_settings": C.JUDGE_GEN,
        "conditions": C.CONDITIONS,
        "seed": C.SEED,
        "design": {"n_pairs": C.N_PAIRS, "prompt_types": C.PROMPT_TYPES, "conditions": C.CONDITION_ORDER,
                   "target_models": list(C.TARGET_MODELS), "n_responses": C.N_PAIRS * 2 * 3 * 2,
                   "audit_per_cell": C.AUDIT_PER_CELL, "n_audit": C.AUDIT_PER_CELL * 12},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--skip-weights", action="store_true",
                    help="with --check: do not hash the model weights (no models_cache needed)")
    args = ap.parse_args()
    if args.skip_weights and not args.check:
        sys.exit("--skip-weights is only allowed together with --check")
    state = current_state(skip_weights=args.skip_weights)
    if args.check:
        frozen = json.loads(MANIFEST.read_text(encoding="utf-8"))
        if args.skip_weights:
            frozen["models"] = {k: {f: v for f, v in m.items() if f != "weights_sha256"}
                                for k, m in frozen["models"].items()}
        drift = [k for k in state if json.dumps(state[k], sort_keys=True) != json.dumps(frozen[k], sort_keys=True)]
        if drift:
            for k in drift:
                if k == "files_sha256":
                    for f, h in state[k].items():
                        if frozen[k].get(f) != h:
                            print("DRIFT file:", f)
                else:
                    print("DRIFT:", k)
            sys.exit(1)
        weights = "model ids and revisions (weights not hashed)" if args.skip_weights else "3 model weights"
        print("freeze check PASSED: all", len(state["files_sha256"]), f"files, {weights}, settings and templates match the manifest of", frozen["frozen_at_utc"])
        return
    if MANIFEST.exists():
        sys.exit("freeze_manifest.json already exists - refusing to overwrite a freeze.")
    state["frozen_at_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    state["packages"] = {p: metadata.version(p) for p in ["torch", "transformers", "accelerate", "pandas", "numpy", "scipy", "statsmodels"]}
    state["statement"] = ("Frozen at the end of Phase 4. No additional models, datasets or attack methods "
                          "are added after this point; prompts, templates, settings and rubric are fixed.")
    MANIFEST.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print("frozen at", state["frozen_at_utc"])
    for f, h in state["files_sha256"].items():
        print(f"  {h[:16]}  {f}")
    for k, m in state["models"].items():
        print(f"  {k}: {m['repo']}@{m['revision'][:12]} weights {list(m['weights_sha256'].values())[0][:16]}")


if __name__ == "__main__":
    main()
