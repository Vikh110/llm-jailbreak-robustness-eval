\appendix

# Glossary

Terms are listed alphabetically. The chapter where each is introduced is given in brackets.

Adversary
:   The imagined attacker in a threat model. (Ch. 9)

Agreement
:   The share of items on which two raters give the same label. (Ch. 5)

Attack success rate
:   Another name for the harmful-compliance rate: the share of harmful requests that produce harmful compliance. (Ch. 10)

Audit
:   A second, more careful labelling of a sample of responses, used to measure how reliable the judge is. Here: 60 responses, labelled by an AI model. (Ch. 4)

Benchmark
:   A fixed set of test items with an agreed way of scoring them. (Ch. 4)

Benign
:   Harmless. A benign request is the harmless twin of a harmful one. (Ch. 3)

Benign compliance
:   The model answers a harmless request. The desired outcome. Also called safe compliance. (Ch. 10)

bfloat16
:   A compact number format used to store and run the models. It causes tiny rounding differences between machines. (Ch. 2)

Black-box
:   Testing a model only by sending it messages and reading the replies, with no view of its insides. (Ch. 3)

Blinding
:   Hiding information from a marker so that it cannot bias the labels. (Ch. 4)

Bonferroni correction
:   Dividing the significance threshold by the number of tests, to guard against lucky results. Here 0.05 / 21 = 0.0024. (Ch. 5)

Cell
:   One combination of model, condition and kind of request. There are 12, each with 20 responses. (Ch. 8)

Chat template
:   The recipe that joins the messages of a conversation into the single text a model reads. (Ch. 2)

Checksum (hash)
:   A short code computed from a file's contents; any change to the file changes the code. The method used is SHA-256. (Ch. 4)

Cohen's kappa
:   A measure of agreement between two raters that removes the agreement expected by chance. 1 is perfect, 0 is chance level. (Ch. 5)

Compliance
:   The model does what was asked. (Ch. 3)

Condition
:   One of the three ways a request was sent: direct, role framing, prefix steering. (Ch. 8)

Confidence interval
:   A range around an estimate that expresses its uncertainty. A 95% interval comes from a method that captures the true value about 95 times in 100. (Ch. 5)

Correct refusal
:   The model declines a harmful request. The desired outcome for harmful requests. (Ch. 3)

CSV
:   A plain-text table with commas between columns. (Ch. 7)

Dataset
:   An organised collection of data, here a table of requests. (Ch. 4)

Decoding
:   The rule for choosing the next token during generation. (Ch. 2)

Default system prompt
:   The system message a model's chat template inserts when none is supplied. (Ch. 2)

Deployment
:   Putting a system into real use. (Ch. 6)

Empty jailbreak
:   A response that does not refuse a harmful request but contains nothing that serves the harmful goal. (Ch. 3)

End-of-sequence token
:   A special token a model writes when it considers its answer finished. (Ch. 2)

Error bar
:   A line on a chart showing a confidence interval. (Ch. 13)

Exploratory
:   Describes an analysis decided on after seeing the data. Weaker evidence than a pre-specified one. (Ch. 12)

False negative
:   A miss: the judge fails to flag something the reference flagged. (Ch. 5)

False positive
:   A false alarm: the judge flags something the reference did not. (Ch. 5)

Fine-tuning
:   Further training of an existing model. Possible for anyone who has the weights. (Ch. 2)

Freeze
:   The point after which no part of the experiment may change. (Ch. 4)

Generation
:   A model producing its answer, token by token. (Ch. 2)

Governance
:   The rules, standards and institutions that shape how AI is built and released. (Ch. 6)

GPU
:   A chip that does the arithmetic of AI models quickly. (Ch. 2)

Greedy decoding
:   Always choosing the most likely next token. The same input always gives the same output. (Ch. 2)

Guard model
:   A model trained to classify text as safe or unsafe. (Ch. 4)

Harmful compliance
:   The model produces content that serves a harmful request. In the judge's version: the judge says Unsafe. (Ch. 3, Ch. 10)

Hugging Face
:   The website that hosts the models and the dataset. (Ch. 2)

Instruction-tuned
:   Describes a model trained to follow instructions and answer like an assistant. (Ch. 2)

Jailbreak
:   Wording a request so that a model which would normally refuse complies. (Ch. 3)

JBB-Behaviors
:   The dataset of 100 harmful and 100 matched benign behaviours from JailbreakBench. (Ch. 4)

JSONL
:   A file format with one structured record per line. (Ch. 11)

Judge
:   An automatic scorer that labels model responses. Here: Qwen3Guard-Gen-0.6B. (Ch. 4)

Language model
:   A program that continues text by repeatedly predicting the next token. (Ch. 2)

Lexical overfitting
:   A model reacting to particular words or topics instead of to what is being asked. (Ch. 3)

Locked dataset
:   The final file of 240 responses, sealed with a checksum and marked read-only. (Ch. 11)

Lower bound
:   A value the true figure is at least as large as. (Ch. 9)

Manifest
:   A list of contents; here, the file of checksums and settings written at the freeze. (Ch. 10)

Matched pair
:   A harmful request and its benign twin on the same topic. (Ch. 3)

Maximum new tokens
:   The limit on the length of a generated answer. Here 256. (Ch. 2)

McNemar test
:   A test for comparing two conditions on the same items, using only the items that changed. (Ch. 5)

Metadata
:   Descriptive information stored alongside data. (Ch. 10)

Open-weight
:   Describes a model whose parameters are published for anyone to download. (Ch. 2)

Other non-refusal
:   A response to a harmful request that neither refuses nor is harmful. (Ch. 3)

Over-refusal
:   The model refuses a harmless request. (Ch. 3)

p-value
:   The chance of a result at least as extreme as the one seen, if there were truly no effect. (Ch. 5)

Parameters (weights)
:   The numbers inside a model that store what it learned. (Ch. 2)

Pilot
:   A rehearsal of the procedure on data that does not count. (Ch. 10)

Pinning
:   Recording the exact revision of a model or dataset. (Ch. 2)

Pipeline
:   A series of programs run in order. (Ch. 7)

Pooling
:   Combining several groups into one to get a larger count. (Ch. 12)

Pre-fill
:   Writing the first words of the model's answer on its behalf. Not used in this project. (Ch. 9)

Precision
:   Of everything the judge flagged, the share that was right. (Ch. 5)

Prefix steering
:   The transformation that tells the model to start its answer with an agreeing sentence. (Ch. 3)

Prompt
:   The text given to a model. (Ch. 3)

Recall
:   Of everything that should have been flagged, the share the judge caught. (Ch. 5)

Red-teaming
:   Structured testing that probes an AI system for flaws. (Ch. 6)

Refusal
:   A response that declines to do what was asked. (Ch. 3)

Repetition penalty
:   A setting that makes a model less likely to repeat itself. Here 1.1. (Ch. 2)

Revision
:   A code that identifies one exact version of a model or dataset. (Ch. 2)

Role framing
:   The transformation that wraps a request in a role-play story. (Ch. 3)

Rubric
:   A written set of marking rules. (Ch. 4)

Sampling
:   Choosing the next token at random according to its likelihood. (Ch. 2)

Seed
:   The starting number for a computer's random choices; the same seed gives the same choices. (Ch. 4)

Sensitivity analysis
:   Repeating an analysis under a different reasonable choice to see whether the conclusion holds. (Ch. 10)

Statistical power
:   The ability of a study to detect an effect that really exists. (Ch. 5)

Stratified sample
:   A sample drawn in equal numbers from each of several groups. (Ch. 4)

System card (model card)
:   A document published with a model describing its tests and limits. (Ch. 6)

System prompt
:   The background instruction at the start of a conversation. (Ch. 2)

System under test
:   Everything being evaluated together: weights, chat template, system prompt and decoding settings. (Ch. 9)

Target (in the dataset)
:   The agreeing first sentence stored with each request. (Ch. 4)

Target model
:   A model being tested, as opposed to the judge. (Ch. 7)

Temperature
:   A sampling setting; higher values give more varied output. (Ch. 2)

Template
:   A fixed piece of wording with placeholders. (Ch. 10)

Threat model
:   The description of the imagined attacker: goals, knowledge and abilities. (Ch. 3)

Token
:   A word or part of a word; the unit a model reads and writes. (Ch. 2)

Tokenizer
:   The component that converts between text and tokens. (Ch. 10)

Transformation
:   A fixed change applied to a request to make a jailbreak-style prompt. (Ch. 3)

Truncated
:   Cut off at the length limit before the model finished. (Ch. 2)

Upper bound
:   A value the true figure does not exceed. (Ch. 15)

Virtual environment
:   A private folder of software libraries, separate from the rest of the computer. (Ch. 7)

White-box
:   Testing or attacking a model with access to its insides. (Ch. 3)

Wilson interval
:   A confidence interval for a rate that behaves well with small samples. (Ch. 5)

# All 21 paired tests

Each row is one exact McNemar test on the same 20 prompt pairs. "First only" counts pairs that show the outcome only in the first-named arm; "second only" counts pairs that show it only in the second. Only p-values below 0.0024 pass the strict threshold; they are in bold.

| Outcome | Comparison | Within | First only | Second only | p-value |
|---|---|---|---|---|---|
| Harmful compliance | Role framing vs direct | 0.5B | 4 | 3 | 1.00 |
| Harmful compliance | Prefix steering vs direct | 0.5B | 13 | 0 | **0.00024** |
| Harmful compliance | Role framing vs direct | 1.5B | 4 | 0 | 0.125 |
| Harmful compliance | Prefix steering vs direct | 1.5B | 17 | 0 | **0.000015** |
| Harmful compliance | 1.5B vs 0.5B | Direct | 0 | 5 | 0.063 |
| Harmful compliance | 1.5B vs 0.5B | Role framing | 3 | 5 | 0.73 |
| Harmful compliance | 1.5B vs 0.5B | Prefix steering | 1 | 2 | 1.00 |
| Correct refusal | Role framing vs direct | 0.5B | 2 | 4 | 0.69 |
| Correct refusal | Prefix steering vs direct | 0.5B | 0 | 14 | **0.00012** |
| Correct refusal | Role framing vs direct | 1.5B | 0 | 5 | 0.063 |
| Correct refusal | Prefix steering vs direct | 1.5B | 0 | 19 | **0.000004** |
| Correct refusal | 1.5B vs 0.5B | Direct | 6 | 0 | 0.031 |
| Correct refusal | 1.5B vs 0.5B | Role framing | 6 | 3 | 0.51 |
| Correct refusal | 1.5B vs 0.5B | Prefix steering | 1 | 0 | 1.00 |
| Over-refusal | Role framing vs direct | 0.5B | 2 | 1 | 1.00 |
| Over-refusal | Prefix steering vs direct | 0.5B | 0 | 2 | 0.50 |
| Over-refusal | Role framing vs direct | 1.5B | 0 | 4 | 0.125 |
| Over-refusal | Prefix steering vs direct | 1.5B | 0 | 6 | 0.031 |
| Over-refusal | 1.5B vs 0.5B | Direct | 5 | 1 | 0.22 |
| Over-refusal | 1.5B vs 0.5B | Role framing | 0 | 1 | 1.00 |
| Over-refusal | 1.5B vs 0.5B | Prefix steering | 0 | 0 | 1.00 |

Source: `04_results/paired_tests.csv`.

# The project files

| File | What it is |
|---|---|
| `01_protocol/01_research_question_and_threat_model.md` | The three research questions and the threat model |
| `01_protocol/02_prompt_selection.md` | The exclusion rules and the 20 selected pairs |
| `01_protocol/03_labels_metrics_transformations_rubric.md` | Conditions, settings, outcome labels, metrics and the audit rubric |
| `01_protocol/04_source_notes.md` | Verified facts and quotes from every source |
| `01_protocol/05_pilot_log.md` | What the pilot checked and what it changed |
| `01_protocol/freeze_manifest.json` | Checksums and settings at the freeze |
| `01_protocol/prompt_selection_log.csv` | The decision for each of the 100 behaviours |
| `02_data/source/` | Unchanged copies of the two dataset files |
| `02_data/selected_prompts.csv` | The 20 pairs with their goals and targets |
| `02_data/pilot/` | Pilot requests, responses and judge labels |
| `02_data/responses_locked.jsonl` | The 240 responses with metadata (the locked dataset) |
| `02_data/responses_locked.sha256` | Its checksum |
| `02_data/judge_scores.csv` | The judge's verdict and outcome label for each response |
| `02_data/audit/audit_sample_blind.csv` | What the auditor saw |
| `02_data/audit/audit_key.csv` | The link from audit numbers to responses |
| `02_data/audit/audit_labels.csv` | The 60 audit labels with notes |
| `02_data/audit/audit_log.json` | When the labels were saved and when the judge started |
| `02_data/audit/disagreement_types.csv` | The type given to each disagreement |
| `03_pipeline/config.py` | Every setting of the experiment |
| `03_pipeline/01_select_prompts.py` | Selects the 20 pairs and the pilot pairs |
| `03_pipeline/02_generate.py` | Produces the responses |
| `03_pipeline/02b_lock_dataset.py` | Checks and locks the dataset |
| `03_pipeline/03_judge.py` | Runs the judge and derives outcome labels |
| `03_pipeline/04_audit_sample.py` | Draws the blind audit sample |
| `03_pipeline/04b_audit_log.py` | Records the audit and judge times |
| `03_pipeline/05_analysis.py` | Rates, intervals, tests, reliability, charts |
| `03_pipeline/06_freeze.py` | Writes and checks the freeze manifest |
| `03_pipeline/07_verify.py` | Independent re-computation (26 checks) |
| `03_pipeline/08_build_notebook.py`, `analysis_notebook.ipynb` | The clean notebook |
| `03_pipeline/09_build_report.py` | Builds the report, card and error analysis from the results |
| `04_results/summary.json` | Every result in one file |
| `04_results/metrics.csv`, `paired_tests.csv` | The rate table and the test table |
| `04_results/judge_vs_audit_items.csv` | Judge and audit labels side by side |
| `04_results/error_analysis.md` | The written error analysis |
| `04_results/verification_report.txt` | The 26 checks and their results |
| `04_results/figures/` | The four result charts |
| `05_report/` | Report and Safety Evaluation Card |
| `06_presentation/` | The slides, a PDF copy, the question-and-answer sheet, the build program |
| `07_guide/` | This guide, its chapters, diagrams and build files |

# Sources

**Read for the project** (verified facts are in `01_protocol/04_source_notes.md`):

- Chao, P., Debenedetti, E., Robey, A., Andriushchenko, M., Croce, F., Sehwag, V., Dobriban, E., Flammarion, N., Pappas, G. J., Tramèr, F., Hassani, H. and Wong, E. (2024). *JailbreakBench: An Open Robustness Benchmark for Jailbreaking Large Language Models.* NeurIPS 2024 Datasets and Benchmarks Track. arXiv:2404.01318.
- Röttger, P., Kirk, H. R., Vidgen, B., Attanasio, G., Bianchi, F. and Hovy, D. (2024). *XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models.* NAACL 2024. arXiv:2308.01263.
- Souly, A., Lu, Q., Bowen, D., Trinh, T., Hsieh, E., Pandey, S., Abbeel, P., Svegliato, J., Emmons, S., Watkins, O. and Toyer, S. (2024). *A StrongREJECT for Empty Jailbreaks.* NeurIPS 2024 Datasets and Benchmarks Track. arXiv:2402.10260.
- National Institute of Standards and Technology (2024). *Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile*, NIST AI 600-1.
- UK AI Security Institute and Meridian Labs. *Inspect* documentation, inspect.aisi.org.uk.
- The model cards of the three Qwen models used (the two Qwen2.5 Instruct models and Qwen3Guard-Gen) and the dataset card of JBB-Behaviors, on huggingface.co.

**Checked at the level of their public pages only:**

- BlueDot Impact. *Technical AI Safety* course, bluedot.org/courses/technical-ai-safety.
- BlueDot Impact. *Frontier AI Governance* course, bluedot.org/courses/ai-governance.

**How this guide was checked.** After writing, every fraction of the form "k of n" or "k/n" and every percentage in the guide was compared automatically with the project's results file, and the remaining figures (times, token counts, file sizes, quotations) were compared with the project files they come from.
