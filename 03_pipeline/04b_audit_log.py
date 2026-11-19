"""Phase 6 - timestamp the blind audit relative to the judge run.

  python 04b_audit_log.py labels   -> validates audit_labels.csv, stores its SHA-256 and save time
  python 04b_audit_log.py judge    -> records the moment the judge run on the main dataset starts

07_verify.py checks that the labels were saved first and have not changed since.
"""
import datetime
import hashlib
import json
import sys

import pandas as pd

import config as C

LOG = C.DATA_DIR / "audit" / "audit_log.json"
now = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def main():
    stage = sys.argv[1]
    log = json.loads(LOG.read_text(encoding="utf-8")) if LOG.exists() else {}
    if stage == "labels":
        assert not (C.DATA_DIR / "judge_scores.csv").exists(), "judge scores already exist - audit would not be blind"
        path = C.DATA_DIR / "audit" / "audit_labels.csv"
        lab = pd.read_csv(path)
        key = pd.read_csv(C.DATA_DIR / "audit" / "audit_key.csv")
        assert len(lab) == 60 and set(lab.audit_id) == set(key.audit_id)
        assert lab.refusal.isin(["full_refusal", "partial_refusal", "compliance"]).all()
        assert lab.harmful_content.isin(["yes", "no"]).all()
        log.update({"auditor": "Claude (LLM annotator) applying 01_protocol/03_labels_metrics_transformations_rubric.md",
                    "blinding": "auditor saw only audit_id, prompt_type, goal and response; no model, condition or judge label",
                    "audit_labels_saved_utc": now(),
                    "audit_labels_sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        print("audit labels validated and logged:", lab.refusal.value_counts().to_dict(), lab.harmful_content.value_counts().to_dict())
    elif stage == "judge":
        assert "audit_labels_saved_utc" in log, "save the audit labels first"
        log["judge_run_started_utc"] = now()
        print("judge start logged")
    LOG.write_text(json.dumps(log, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
