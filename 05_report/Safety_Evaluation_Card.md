# Safety Evaluation Card

**Jailbreak robustness and over-refusal of Qwen2.5-0.5B-Instruct and Qwen2.5-1.5B-Instruct**

| | |
|---|---|
| Evaluated systems | Qwen/Qwen2.5-0.5B-Instruct (`7ae557604adf`), Qwen/Qwen2.5-1.5B-Instruct (`989aa7980e4c`): weights, default chat template, default system prompt, greedy decoding, no external guardrail |
| Evaluator | Independent of the developer. Vishwas Khandelwal, Individual Learning Plan project, 12 November 2026 |
| Purpose of this card | Evidence for a deployer or reviewer about one configuration under one threat model. Not a safety certification |

## What was tested

| | |
|---|---|
| Threat model | Black-box, single turn, one attempt per request, no system-prompt control, no pre-filled assistant turn, no fine-tuning |
| Test set | 20 lower-risk harmful requests and 20 topic-matched benign requests from JBB-Behaviors (`886acc352a31`), six categories: economic harm, fraud, disinformation, privacy, expert advice, government decision-making |
| Excluded by design | Physical harm, sexual content, malware and hacking, harassment and discrimination, and 28 further behaviours (68 of 100 excluded by ten written rules) |
| Conditions | Direct; role framing (fixed role-play wrapper); prefix steering (instruction to start with an affirmative sentence) |
| Volume | 240 responses: 2 models x 20 pairs x 2 prompt types x 3 conditions |
| Scoring | Qwen3Guard-Gen-0.6B (`fada3b2f655b`); 60 responses audited blind against a written rubric by an LLM annotator |

## Results

Rate [95% Wilson interval], n = 20 per cell, judge-based.

| Model | Condition | Harmful compliance | Correct refusal | Over-refusal (benign) |
|---|---|---|---|---|
| Qwen2.5-0.5B | Direct | 25% [11, 47] (5/20) | 70% [48, 85] (14/20) | 10% [3, 30] (2/20) |
| Qwen2.5-0.5B | Role framing | 30% [15, 52] (6/20) | 60% [39, 78] (12/20) | 15% [5, 36] (3/20) |
| Qwen2.5-0.5B | Prefix steering | 90% [70, 97] (18/20) | 0% [0, 16] (0/20) | 0% [0, 16] (0/20) |
| Qwen2.5-1.5B | Direct | 0% [0, 16] (0/20) | 100% [84, 100] (20/20) | 30% [15, 52] (6/20) |
| Qwen2.5-1.5B | Role framing | 20% [8, 42] (4/20) | 75% [53, 89] (15/20) | 10% [3, 30] (2/20) |
| Qwen2.5-1.5B | Prefix steering | 85% [64, 95] (17/20) | 5% [1, 24] (1/20) | 0% [0, 16] (0/20) |

**Reliability of the automated scores (60-response audit)**

| Judge output | Agreement | Kappa | Note |
|---|---|---|---|
| Refusal flag | 95% | 0.88 | No missed refusals; 3 false refusal flags |
| Unsafe label | 73% | 0.44 | 8 false positives, 0 false negatives among 30; precision 6/14 |

Harmful-compliance rates are upper bounds. On the 30 audited harmful-prompt responses: judge 14/30 (47%), audit 6/30 (20%).

## Findings

1. **Built-in refusals are easy to switch off.** A one-line instruction to begin with an affirmative sentence reduced correct refusals from 34/40 to 1/40 across both models.
2. **Not every non-refusal is harmful.** About half of the audited prefix-steering responses that the judge called unsafe contain no harmful content (5/10 harmful by audit, 10/10 by judge).
3. **Over-refusal exists and is topic-driven.** Asked directly, the models refused 2/20 (10%) and 6/20 (30%) of the benign requests, mostly on disinformation topics.
4. **The small guard model over-flags.** It marked 23 of 120 responses to benign prompts as Unsafe.

## What this evaluation does not show

- Behaviour on high-severity categories, in other languages, over several turns, or with sampling.
- Resistance to adaptive or white-box attacks, or to fine-tuning of the open weights. Attack success here is a lower bound.
- Real-world uplift. Much of the complying output is generic or inaccurate.
- Human-validated labels. The audit is one LLM annotation pass over 60 responses.
- Statistical precision. With 20 prompts per cell, intervals are up to 39 percentage points wide.

## Implications for a deployer

- Do not treat the model's own refusals as a safety control. Add an independent input or output control if the application needs one.
- Validate any automated judge or filter on labelled samples from your own use case before relying on its numbers. Measure false positives on benign content as well as misses.
- Report both failure directions together. A configuration that looks safer on harmful prompts may refuse more legitimate ones.

## Traceability

| | |
|---|---|
| Freeze manifest | `01_protocol/freeze_manifest.json`, frozen 2026-11-12T11:31:22+00:00 |
| Locked dataset | `02_data/responses_locked.jsonl`, SHA-256 `92a321243be6585b...` |
| Rubric and annotator instructions | `01_protocol/03_labels_metrics_transformations_rubric.md` |
| Verification | 26 of 26 checks passed (`04_results/verification_report.txt`) |
| NIST AI 600-1 actions addressed | MS-1.3-002 (external evaluation), MS-2.3-002 and MS-2.3-003 (validated methods, shared results), MS-2.7-007 (red-teaming against adversarial prompts), MS-2.8-002 (documented annotator instructions), MS-2.11-001 (documented benchmark limitations), MS-2.13-001 (measurement error of the metric) |
