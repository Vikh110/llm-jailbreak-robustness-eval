# Pipeline

Python 3.12, PyTorch and Hugging Face Transformers. Every script imports `config.py`, the single source of truth for models, revisions, templates, settings and selection rules. Run the scripts from this folder.

| Step | Script | What it does | Needs GPU |
|---|---|---|---|
| 0 | `00_download_models.py` | Downloads the dataset and the three models at the pinned commit hashes into `models_cache/` | no |
| 1 | `01_select_prompts.py` | Applies the ten written exclusion rules to JBB-Behaviors, then draws a seeded, stratified sample of 20 pairs plus 4 pilot pairs | no |
| 2 | `02_generate.py` | Sends one user message per cell through the model's default chat template; greedy decoding, 256 new tokens, full metadata per record; resume-safe | yes* |
| 3 | `03_judge.py` | Scores each response with Qwen3Guard-Gen-0.6B (shown the original goal, not the jailbreak wrapper) and maps the output to an outcome label | yes* |
| 4 | `04_audit_sample.py` | Draws the blind audit sample: 5 responses from each of the 12 cells, shuffled, with model, condition and judge label hidden | no |
| 4b | `04b_audit_log.py` | Records the SHA-256 and save time of the audit labels, and the start of the judge run | no |
| 5 | `05_analysis.py` | Rates with Wilson 95% intervals, exact McNemar tests, judge-vs-audit agreement and Cohen's kappa, figures, `summary.json` | no |
| 6 | `06_freeze.py` | Writes the freeze manifest (file hashes, weight hashes, settings), and with `--check` detects any drift | no |
| 7 | `07_verify.py` | Recomputes every reported number through a separate code path (standard library only) and runs 26 integrity checks | no |
| 8 | `08_build_notebook.py` | Builds `analysis_notebook.ipynb`, a readable walk-through of the analysis | no |
| 9 | `09_build_report.py` | Writes the report, the Safety Evaluation Card and the error analysis from `summary.json` (pandoc for .docx) | no |

\* Runs on CPU too, but slowly, and float32 on CPU can change individual tokens compared with the bfloat16 GPU run.

## Order of the original run

```bash
python 01_select_prompts.py
python 02_generate.py --prompts ../02_data/pilot/pilot_prompts.csv --out ../02_data/pilot/pilot_responses.jsonl
python 03_judge.py    --responses ../02_data/pilot/pilot_responses.jsonl --out ../02_data/pilot/pilot_judge_goal.csv
python 06_freeze.py                       # freeze: nothing below may change the protocol
python 02_generate.py --prompts ../02_data/selected_prompts.csv --out ../02_data/responses_raw.jsonl
python 02b_lock_dataset.py                # locked dataset + SHA-256, files made read-only
python 04_audit_sample.py                 # 60 blinded responses
python 04b_audit_log.py labels            # after the audit labels are saved
python 04b_audit_log.py judge
python 03_judge.py    --responses ../02_data/responses_locked.jsonl --out ../02_data/judge_scores.csv
python 05_analysis.py
python 07_verify.py
python 08_build_notebook.py               # then: jupyter nbconvert --execute analysis_notebook.ipynb
python 09_build_report.py
```

`06_freeze.py` and `02b_lock_dataset.py` refuse to overwrite an existing freeze or lock. To repeat the generation, write to a new file (for example `--out ../rerun.jsonl`) and compare it with the locked dataset.

## Frozen files

`config.py`, `02_generate.py`, `03_judge.py` and `04_audit_sample.py` are hashed in `01_protocol/freeze_manifest.json`. They are kept byte-for-byte as they were when the protocol was frozen, which is why their style is not reformatted.

## Environment

`requirements_frozen.txt` is the exact environment of the original run (Python 3.12.12, PyTorch 2.14.1+cu126, Transformers 5.22.2, one NVIDIA RTX 3050 Laptop GPU with 4 GB). The CUDA build of PyTorch comes from the PyTorch package index:

```bash
pip install -r requirements_frozen.txt --extra-index-url https://download.pytorch.org/whl/cu126
```
