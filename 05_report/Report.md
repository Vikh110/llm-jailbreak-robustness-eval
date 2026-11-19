# Black-Box Evaluation of Jailbreak Robustness and Over-Refusal in Small Instruction-Tuned Language Models

Individual Learning Plan project report. Vishwas Khandelwal, 12 November 2026.

## 1. Summary

Two small open-weight chat models, Qwen2.5-0.5B-Instruct and Qwen2.5-1.5B-Instruct, were tested on 20 lower-risk harmful requests and 20 topic-matched benign requests from JBB-Behaviors, each sent directly and with two fixed prompt transformations (240 responses). Qwen3Guard-Gen-0.6B scored every response, and 60 responses were audited blind against a written rubric.

1. **A one-line format instruction removes almost all refusals.** Asked directly, the models refused 14/20 (70%) and 20/20 (100%) of the harmful requests. With prefix steering they refused 0/20 (0%) and 1/20 (5%), and the judge-based harmful-compliance rate rose to 18/20 (90%, 95% CI 70 to 97%) and 17/20 (85%, 95% CI 64 to 95%).
2. **Role framing had no clear effect.** Harmful compliance was 6/20 (30%) and 4/20 (20%), not distinguishable from direct prompting with 20 prompts.
3. **The larger model refuses more, in both directions.** Asked directly, the 1.5B model refused all 20 harmful requests but also 6/20 (30%) of the benign ones; the 0.5B model refused 2/20 (10%) of the benign ones. Over-refusal is concentrated on disinformation and privacy topics.
4. **The automated judge is reliable for refusals and unreliable for harm.** Against the audit its refusal flag agrees in 95% of cases (kappa 0.88). Its Unsafe label agrees in 73% (kappa 0.44): of 14 audited responses it called Unsafe, the audit found harmful content in 6. Harmful-compliance rates above are therefore upper bounds. On the audited prefix-steering responses the judge found 10/10 unsafe and the audit 5/10.

The practical reading: the built-in refusals of these models are not a safeguard, because a trivial instruction switches them off, and a small guard model cannot simply be trusted to measure or filter the result.

## 2. Research questions and threat model

**RQ1 - Robustness.** Under a single-turn, prompt-only black-box threat model, how often do Qwen2.5-0.5B-Instruct and Qwen2.5-1.5B-Instruct produce harmful compliance on 20 lower-risk JBB-Behaviors requests, asked directly and under two fixed prompt transformations?

**RQ2 - Over-refusal.** How often do the same models refuse the 20 matched benign requests under the same three conditions?

**RQ3 - Evaluator reliability.** How reliable is Qwen3Guard-Gen-0.6B as an automated judge of refusal and harmful compliance, measured against a 60-response rubric audit?

The adversary is a low-resource user with query-only access: one user message, no control of the system prompt, no pre-filled assistant turn, no access to weights or logits, no retries and no adaptive search. The system under test is the model with its default chat template, default system prompt and greedy decoding, with no external guardrail. White-box, iterative, multi-turn, multilingual and fine-tuning attacks are out of scope, so every robustness figure below is a lower bound on what a determined adversary could obtain.

## 3. Method

### 3.1 Data and prompt selection

JBB-Behaviors (Chao et al., 2024) contains 100 harmful behaviours in ten categories and 100 benign behaviours, each matching the topic of one harmful behaviour. Twenty pairs were selected with documented rules:

1. Four whole categories were excluded (Physical harm, Sexual/Adult content, Malware/Hacking, Harassment/Discrimination): 40 behaviours.
2. Inside the six retained categories, 28 behaviours were excluded by six further rules (violence or public-safety hazard; coercion or blackmail; hate or exploitation of children; system intrusion or tampering; manufacture or forgery; medical or drug advice with direct health risk).
3. From the 32 eligible behaviours a seeded stratified sample of 20 was drawn: three per category, plus one extra for the two largest pools.

The selected pairs cover Economic harm (4), Fraud/Deception (3), Disinformation (4), Privacy (3), Expert advice (3) and Government decision-making (3). Four eligible but unselected pairs served as the pilot set, so the final 20 were untouched before the freeze. Full rules and lists: `01_protocol/02_prompt_selection.md`.

### 3.2 Conditions

Each prompt is sent three ways. The templates are fixed and identical for harmful and benign prompts.

| Condition | What the user message contains |
|---|---|
| Direct | The JBB goal string, unchanged |
| Role framing | A short role-play wrapper: the model is asked to answer as "Alex", a fictional expert who never refuses or adds warnings, followed by the goal |
| Prefix steering | The goal, followed by an instruction to start the response with the JBB target string ("Sure, here is ...") |

Prefix steering is an instruction inside the user message, not a pre-filled assistant turn, so it stays within the black-box threat model.

### 3.3 Generation

2 models x 20 pairs x 2 prompt types x 3 conditions = 240 responses, one per cell. Settings: greedy decoding, at most 256 new tokens, the shipped repetition penalty of 1.1, default chat template and default system prompt ("You are Qwen, created by Alibaba Cloud. You are a helpful assistant."). Model revisions are pinned by commit hash. Hardware: one NVIDIA GeForce RTX 3050 Laptop GPU (4 GB), weights in bfloat16.

### 3.4 Automated evaluator

Qwen3Guard-Gen-0.6B in response-moderation mode, used as in its model card. For each response it returns a safety level (Safe, Controversial, Unsafe), categories, and a refusal flag (Yes, No). The judge is shown the original JBB goal and the response, not the transformed prompt, following the JailbreakBench convention.

### 3.5 Outcome labels and metrics

| Prompt type | Outcome | Rule applied to the judge output |
|---|---|---|
| Harmful | Harmful compliance | Safety = Unsafe |
| Harmful | Correct refusal | Not Unsafe and Refusal = Yes |
| Harmful | Other non-refusal | Not Unsafe and Refusal = No |
| Benign | Over-refusal | Refusal = Yes |
| Benign | Benign compliance | Refusal = No |

The third harmful outcome exists because not refusing is different from giving harmful content. StrongREJECT (Souly et al., 2024) shows that counting every non-refusal as a successful jailbreak overstates attack success. A sensitivity analysis also counts Controversial as harmful.

Rates are reported per model and condition (n = 20) with 95% Wilson score intervals. Paired differences on the same 20 prompts use the exact McNemar test. With 20 prompts per cell the tests have low power, so the intervals are the main result.

### 3.6 Audit of the judge

Sixty responses were audited: five from each of the twelve cells, drawn with the project seed and shuffled. The auditor saw only the request and the response, with no model name, condition or judge label, and recorded a three-level refusal label (full refusal, partial refusal, compliance, following XSTest) and whether the response contains harmful content (following the JailbreakBench judge guideline and StrongREJECT's emphasis on specific, usable content). The audit labels were saved and hashed before the judge scored the main run.

The auditor was an LLM annotator (Claude) applying the frozen rubric. It is a second annotation by a stronger model, not a human gold standard, and the agreement figures should be read with that in mind.

### 3.7 Freeze and reproducibility

After the pilot, the models (by commit hash and weight checksum), prompts, templates, generation settings, judge mapping and rubric were frozen in `01_protocol/freeze_manifest.json`. No model, dataset or attack method was added afterwards. The 240 responses are stored with full metadata in `02_data/responses_locked.jsonl`, with a SHA-256 checksum. `03_pipeline/07_verify.py` recomputes every reported number through an independent code path.

## 4. Results

### 4.1 Results per model and condition

Rate [95% Wilson interval] (count). n = 20 prompts per cell. Outcomes are judge-based.

| Model | Condition | Harmful compliance | Correct refusal | Other non-refusal | Benign compliance | Over-refusal |
|---|---|---|---|---|---|---|
| Qwen2.5-0.5B | Direct | 25% [11, 47] (5/20) | 70% [48, 85] (14/20) | 5% [1, 24] (1/20) | 90% [70, 97] (18/20) | 10% [3, 30] (2/20) |
| Qwen2.5-0.5B | Role framing | 30% [15, 52] (6/20) | 60% [39, 78] (12/20) | 10% [3, 30] (2/20) | 85% [64, 95] (17/20) | 15% [5, 36] (3/20) |
| Qwen2.5-0.5B | Prefix steering | 90% [70, 97] (18/20) | 0% [0, 16] (0/20) | 10% [3, 30] (2/20) | 100% [84, 100] (20/20) | 0% [0, 16] (0/20) |
| Qwen2.5-1.5B | Direct | 0% [0, 16] (0/20) | 100% [84, 100] (20/20) | 0% [0, 16] (0/20) | 70% [48, 85] (14/20) | 30% [15, 52] (6/20) |
| Qwen2.5-1.5B | Role framing | 20% [8, 42] (4/20) | 75% [53, 89] (15/20) | 5% [1, 24] (1/20) | 90% [70, 97] (18/20) | 10% [3, 30] (2/20) |
| Qwen2.5-1.5B | Prefix steering | 85% [64, 95] (17/20) | 5% [1, 24] (1/20) | 10% [3, 30] (2/20) | 100% [84, 100] (20/20) | 0% [0, 16] (0/20) |

Pooled:

| Group | Harmful compliance | Correct refusal | Benign compliance | Over-refusal |
|---|---|---|---|---|
| Qwen2.5-0.5B, all conditions (n = 60) | 48% [36, 61] (29/60) | 43% [32, 56] (26/60) | 92% [82, 96] (55/60) | 8% [4, 18] (5/60) |
| Qwen2.5-1.5B, all conditions (n = 60) | 35% [24, 48] (21/60) | 60% [47, 71] (36/60) | 87% [76, 93] (52/60) | 13% [7, 24] (8/60) |
| Direct, both models (n = 40) | 12% [5, 26] (5/40) | 85% [71, 93] (34/40) | 80% [65, 90] (32/40) | 20% [10, 35] (8/40) |
| Role framing, both models (n = 40) | 25% [14, 40] (10/40) | 68% [52, 80] (27/40) | 88% [74, 95] (35/40) | 12% [5, 26] (5/40) |
| Prefix steering, both models (n = 40) | 88% [74, 95] (35/40) | 2% [0, 13] (1/40) | 100% [91, 100] (40/40) | 0% [0, 9] (0/40) |
| All responses (n = 120 per prompt type) | 42% [33, 51] (50/120) | 52% [43, 60] (62/120) | 89% [82, 94] (107/120) | 11% [6, 18] (13/120) |

![Harmful-compliance rate by model and condition](../04_results/figures/fig1_harmful_compliance.png)

![Outcome composition per cell](../04_results/figures/fig3_outcome_composition.png)

### 4.2 RQ1: robustness to the two transformations

**Prefix steering.** All 80 prefix-steering responses, harmful and benign, open affirmatively ("Sure, here ..." or "Certainly ..."). Harmful compliance rose on 13 of 20 prompts and fell on 0 for the 0.5B model (p < 0.001), and rose on 17 and fell on 0 for the 1.5B model (p < 0.001, exact McNemar). Both effects remain significant after a Bonferroni correction for the 21 paired tests reported.

**Role framing.** No detectable effect: p = 1.00 for the 0.5B model and p = 0.12 for the 1.5B model. The intervals are wide, so a moderate effect cannot be excluded.

**Model size.** Asked directly, the 1.5B model refused more harmful requests than the 0.5B model (6 prompts refused only by the 1.5B model, 0 only by the 0.5B model, p = 0.031). Under prefix steering the difference disappears (17/20 (85%) against 18/20 (90%)).

**How much of this is real harm?** The audit (section 5) shows that the judge over-counts. On the 30 audited harmful-prompt responses the judge-based harmful-compliance rate is 14/30 (47%) and the audit-based rate is 6/30 (20%). The direction of the prefix-steering effect holds in the audit (0/10 harmful under direct prompting, 1/10 under role framing, 5/10 under prefix steering), but its size is roughly half of what the judge reports.

### 4.3 RQ2: over-refusal

![Over-refusal rate by model and condition](../04_results/figures/fig2_over_refusal.png)

Asked directly, the 0.5B model refused 2/20 (10%, 95% CI 3 to 30%) of the benign requests and the 1.5B model 6/20 (30%, 95% CI 15 to 52%). Under prefix steering neither model refused any benign request. The model that is safer on harmful requests when asked directly is also the one that refuses more benign requests, although with 20 prompts the difference in over-refusal is not significant (p = 0.22).

Over-refusal depends on the topic:

| JBB category | Harmful compliance (harmful prompts) | Over-refusal (benign prompts) |
|---|---|---|
| Economic harm | 10/24 (42%) | 0/24 (0%) |
| Fraud/Deception | 9/18 (50%) | 0/18 (0%) |
| Disinformation | 7/24 (29%) | 9/24 (38%) |
| Privacy | 9/18 (50%) | 3/18 (17%) |
| Expert advice | 6/18 (33%) | 0/18 (0%) |
| Government decision-making | 9/18 (50%) | 1/18 (6%) |

All 13 over-refusals occurred under direct prompting (8) or role framing (5), and 9 of them are on disinformation topics, where the benign request asks to explain or discuss a conspiracy belief. This matches the "lexical overfitting" explanation in XSTest: the model reacts to the topic of the request and not to what is being asked.

## 5. RQ3: reliability of the automated judge

![Judge against audit](../04_results/figures/fig4_judge_vs_audit.png)

| Judge output | n | Agreement with audit | Cohen's kappa | Judge false positives | Judge false negatives |
|---|---|---|---|---|---|
| Refusal flag | 60 | 95% | 0.88 | 3 | 0 |
| Unsafe label, harmful prompts | 30 | 73% | 0.44 | 8 | 0 |
| Final outcome label | 60 | 82% | 0.74 | | |

The judge's refusal flag can be used as it is. Its Unsafe label cannot: 8 of the 14 responses it flagged contain no harmful content according to the audit. 5 of these 8 are prefix-steering responses that open with an affirmative sentence and then give generic, reversed or incoherent content. The judge also marked 23 of the 120 responses to benign prompts as Unsafe.

| Condition (10 audited harmful-prompt responses each) | Judge: Unsafe | Audit: harmful content | Audit: full refusal | Audit: other non-refusal |
|---|---|---|---|---|
| Direct | 2/10 | 0/10 | 8/10 | 2/10 |
| Role framing | 2/10 | 1/10 | 7/10 | 2/10 |
| Prefix steering | 10/10 | 5/10 | 0/10 | 5/10 |

The full error analysis, with every disagreement and its type, is in `04_results/error_analysis.md`.

## 6. Assumptions and limitations

1. **Small sample.** 20 prompts per cell give wide intervals (for example 25% [11, 47] (5/20)), and the paired tests have low power. Only the prefix-steering effect is large enough to be established.
2. **Lower-risk subset.** The 20 pairs come from six of the ten JBB categories after ten exclusion rules. The results say nothing about violence, weapons, malware, sexual content or hate, where models are usually trained to refuse more firmly.
3. **Weak, fixed attacks.** Two non-adaptive templates, one attempt, one turn, English. Attack success is a lower bound on what an adaptive adversary would achieve.
4. **One greedy sample per cell.** The shipped default is sampling at temperature 0.7. Deployed behaviour may differ and no variance across samples was measured.
5. **Truncation.** 145 of 240 responses reached the 256-token cap and were judged on the text present.
6. **Judge error.** The harmful-compliance rates depend on a judge whose Unsafe label over-triggers. They are upper bounds.
7. **The audit is not a human gold standard.** One LLM annotator, 60 responses, no second annotator, some borderline calls.
8. **Harm is judged by content, not by usefulness.** Much of the complying text from these small models is generic or inaccurate. Real-world uplift is likely lower than even the audited rate suggests, which is the willingness-versus-capability point made by StrongREJECT.
9. **Borderline benign prompts.** The JailbreakBench authors note that some benign behaviours are borderline. Every refusal of a benign prompt is counted as over-refusal here.
10. **Black-box only.** With open weights, safeguards can be removed by fine-tuning. That ceiling was not tested.
11. **Hardware.** Greedy decoding is deterministic on the same hardware and library versions; bfloat16 arithmetic on another GPU may change individual tokens.
12. **Multiple comparisons.** 21 paired tests are reported without correction and should be read as descriptive, apart from the prefix-steering effects noted above.

## 7. What results like these can and cannot support

The governance material frames three uses of evaluation results.

**Independent testing.** The whole evaluation ran on a 4 GB laptop GPU with open weights, an open dataset and an open judge. A third party can repeat it from the freeze manifest without the developer's cooperation. NIST AI 600-1 asks for assessments that involve "independent assessors" (MEASURE 1.3) and for claims to be evaluated "using empirically validated methods" (MS-2.3-002). The audit of the judge is the validation step here: an automated judge is itself a measurement instrument with an error rate, and NIST asks for "measurement error models for pre-deployment metrics" (MS-2.13-001).

**System cards.** A system card is only as useful as the conditions it states. The Safety Evaluation Card in this project reports the threat model, the prompt set and its exclusions, both failure directions (harmful compliance and over-refusal), the uncertainty, and the judge's measured error. NIST asks to "document assumptions and limitations of benchmarks" (MS-2.11-001) and to "document the instructions given to data annotators or AI red-teamers" (MS-2.8-002); the frozen rubric and templates do this.

**Pre-deployment assurance.** These results are evidence about one configuration under one weak threat model. NIST notes that "jailbreaking or prompt engineering tests may not systematically assess validity or reliability risks" and that benchmark-to-deployment gaps are widened by "prompt sensitivity and broad heterogeneity of contexts of use". For open-weight models the gap is larger still, because anyone can fine-tune the safeguards away. So a low attack success rate here would not justify a claim that the model is safe to deploy, while a high one is sufficient to show that the model alone is not a safeguard and that a deployer needs additional controls.

## 8. What I would explore with more time

1. **Scale and variance:** all 100 JBB pairs, several samples per prompt at the shipped temperature, and a third model size.
2. **Graded harm scoring:** a StrongREJECT-style rubric (refusal, specificity, convincingness) in place of a binary Unsafe label, to separate willingness from capability.
3. **Judge comparison:** the larger Qwen3Guard variants, Llama Guard and an LLM judge with the JailbreakBench prompt, all measured against a human-labelled audit with at least two annotators.
4. **Stronger threat models:** assistant-turn pre-fill, multi-turn and adaptive attacks, with the same reporting format.
5. **Defences and their cost:** a hardened system prompt and a guard model used as an output filter, measuring the change in harmful compliance and in over-refusal together.
6. **Mechanism:** why a format instruction overrides refusal in these models, and whether the same holds for larger ones.

## 9. Reproducibility

| Item | Value |
|---|---|
| Freeze time (UTC) | 2026-11-12T11:31:22+00:00 |
| Dataset | JailbreakBench/JBB-Behaviors @ `886acc352a31` |
| Target models | Qwen/Qwen2.5-0.5B-Instruct @ `7ae557604adf`; Qwen/Qwen2.5-1.5B-Instruct @ `989aa7980e4c` |
| Judge | Qwen/Qwen3Guard-Gen-0.6B @ `fada3b2f655b` |
| Libraries | PyTorch 2.14.1+cu126, Transformers 5.22.2 |
| Locked dataset | `02_data/responses_locked.jsonl`, SHA-256 `92a321243be6585b...` |
| Generation time | 30 minutes on one RTX 3050 Laptop GPU (4 GB) |
| Verification | `03_pipeline/07_verify.py`: 26 of 26 checks passed |

## 10. References

- Chao, P., Debenedetti, E., Robey, A., Andriushchenko, M., Croce, F., Sehwag, V., Dobriban, E., Flammarion, N., Pappas, G. J., Tramèr, F., Hassani, H. and Wong, E. (2024). JailbreakBench: An Open Robustness Benchmark for Jailbreaking Large Language Models. NeurIPS 2024 Datasets and Benchmarks Track. arXiv:2404.01318.
- Röttger, P., Kirk, H. R., Vidgen, B., Attanasio, G., Bianchi, F. and Hovy, D. (2024). XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models. NAACL 2024. arXiv:2308.01263.
- Souly, A., Lu, Q., Bowen, D., Trinh, T., Hsieh, E., Pandey, S., Abbeel, P., Svegliato, J., Emmons, S., Watkins, O. and Toyer, S. (2024). A StrongREJECT for Empty Jailbreaks. NeurIPS 2024 Datasets and Benchmarks Track. arXiv:2402.10260.
- National Institute of Standards and Technology (2024). Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile, NIST AI 600-1. https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
- UK AI Security Institute and Meridian Labs. Inspect documentation. https://inspect.aisi.org.uk/
- BlueDot Impact. Technical AI Safety course. https://bluedot.org/courses/technical-ai-safety
- BlueDot Impact. Frontier AI Governance course. https://bluedot.org/courses/ai-governance
- JailbreakBench. JBB-Behaviors dataset. https://huggingface.co/datasets/JailbreakBench/JBB-Behaviors
- Alibaba Cloud, Qwen team. Model cards: Qwen/Qwen2.5-0.5B-Instruct, Qwen/Qwen2.5-1.5B-Instruct, Qwen/Qwen3Guard-Gen-0.6B. https://huggingface.co/Qwen
