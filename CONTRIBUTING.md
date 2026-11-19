# Contributing

Thanks for taking a look. This repository is the record of a finished evaluation, so the most useful contributions are **checks of the results** and **extensions that keep the original run intact**.

## Found a problem with a number or a label?

Open an issue with the **Problem with a result** template. Name the file and the row or field, and say what you expected. Every number is produced from `04_results/summary.json`, and `03_pipeline/07_verify.py` recomputes it independently, so a reproducible discrepancy is a real finding.

## Rules that keep the evaluation valid

- **Do not edit frozen or locked files.** `03_pipeline/config.py`, `02_generate.py`, `03_judge.py`, `04_audit_sample.py`, the protocol files and the source data are hashed in `01_protocol/freeze_manifest.json`. `02_data/responses_locked.*` and `02_data/audit/audit_labels.csv` are hashed too. Changing them makes the verification fail, which is the point.
- **New experiments go in new files.** For example, write a re-run to `--out ../rerun.jsonl` and compare it with the locked dataset. Don't overwrite the original.
- **Keep the scope.** No high-severity categories (violence, weapons, malware, sexual content, hate). Report over-refusal next to attack success, and validate any automated judge before relying on it.
- **Don't paste harmful model output into issues or pull requests.** Refer to it by `response_id`.

## Development setup

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python 03_pipeline/07_verify.py --skip-weights       # must print 26/26 checks passed
python -m pytest                                     # must pass
python -m ruff check .
```

CI runs the same three commands on every pull request.
