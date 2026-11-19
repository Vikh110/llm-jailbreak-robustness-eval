# Data

> **Content warning.** Several files here contain requests for harmful content and the models' responses to them. The requests come from six lower-risk JBB-Behaviors categories (economic harm, fraud, disinformation, privacy, expert advice, government decision-making). Violence, weapons, malware, sexual content and hate speech were excluded before any model was run. The data is published so that every number in the report can be checked. Use it for safety research only.

| File | Rows | What it is |
|---|---|---|
| `source/harmful-behaviors.csv`, `source/benign-behaviors.csv` | 100 + 100 | JBB-Behaviors at commit `886acc352a31`, unchanged ([MIT licence](source/LICENSE-JBB-Behaviors)) |
| `selected_prompts.csv` | 20 | The 20 harmful/benign pairs chosen by `01_select_prompts.py` (seeded, stratified) |
| `pilot/` | 4 pairs, 48 responses | Pilot run on four held-out pairs, used to test the pipeline before the freeze. Not part of the results |
| `responses_raw.jsonl` | 240 | Generation output in run order |
| `responses_locked.jsonl` | 240 | **The locked dataset**: the same records in canonical order, read-only, SHA-256 in `responses_locked.sha256`. All analysis reads this file. Fields: [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) |
| `responses_locked.csv` | 240 | Flat CSV copy of the locked dataset, for spreadsheets |
| `judge_scores.csv` | 240 | Qwen3Guard-Gen-0.6B output per response: safety level, categories, refusal flag, the mapped outcome label and the raw judge text |
| `audit/audit_sample_blind.csv` | 60 | What the auditor saw: request and response only. No model, condition or judge label |
| `audit/audit_key.csv` | 60 | Links each audit id back to its response (kept apart from the blind sheet) |
| `audit/audit_labels.csv` | 60 | Audit labels: refusal level (full / partial / none) and harmful content (yes / no) |
| `audit/audit_log.json` | n/a | SHA-256 and save time of the labels, and the start time of the judge run. Shows the labels were saved before the judge ran |
| `audit/disagreement_types.csv` | 11 | Type of every judge/audit disagreement (used in `04_results/error_analysis.md`) |
| `generation_run.log` | n/a | Console log of the main generation run |

## Design

2 models × 20 pairs × 2 prompt types (harmful, benign) × 3 conditions (direct, role framing, prefix steering) = **240 responses**, one greedy sample each.
