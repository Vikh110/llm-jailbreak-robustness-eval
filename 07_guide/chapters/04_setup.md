\part{Inputs and setup}

# Data, models, tools and files

This chapter lists everything that went into the project and what each item contributed. Nothing here is a result yet.

## The starting documents

The project folder began with three files.

| File | What it is | What it contributed |
|---|---|---|
| The Individual Learning Plan (Word document) | The project description | The topic, models, dataset, sizes, outputs and boundaries |
| Presentation Guidelines (Word document) | Rules for the talk | 10 minutes, focus on method, example, assumptions, limitations, sources, lessons and next steps |
| Frankfurt School template (PowerPoint file) | The school's slide template | The school's logo. A first version of the slides used the whole template; the final version has its own design |

The first step of the work was to read all three completely and turn them into two checklists: 36 project requirements and 20 presentation rules. The final outputs were checked against these lists item by item.

## The dataset

| | |
|---|---|
| Name | JBB-Behaviors, from the JailbreakBench project |
| Where | Hugging Face, `JailbreakBench/JBB-Behaviors` |
| Exact version | revision `886acc352a31533ffbcf4ef22c744658688086fc` |
| Licence | MIT (a permissive open licence) |
| Files used | `harmful-behaviors.csv` and `benign-behaviors.csv` |
| Size | 100 rows each, in ten categories of ten |

A **CSV file** is a plain-text table: one row per line, with commas between the columns. The two files have identical structure, and row *n* of the benign file is the twin of row *n* of the harmful file. Unchanged copies of both are kept in `02_data/source/`.

The ten categories are: Harassment/Discrimination, Malware/Hacking, Physical harm, Economic harm, Fraud/Deception, Disinformation, Sexual/Adult content, Privacy, Expert advice, and Government decision-making.

What the dataset contributed: every request used in the project, each with its benign twin and its Target sentence.

## The three models

| Role | Model | Revision (start) | File size |
|---|---|---|---|
| Test model 1 | Qwen2.5-0.5B-Instruct | `7ae557604adf` | 0.99 GB |
| Test model 2 | Qwen2.5-1.5B-Instruct | `989aa7980e4c` | 3.09 GB |
| Judge | Qwen3Guard-Gen-0.6B | `fada3b2f655b` | 1.50 GB |

All three are published under the name "Qwen" on Hugging Face with the Apache-2.0 licence, a permissive open licence. The full revision codes are in the freeze manifest.

The models that are being tested are called the **target models**. Qwen is a family of models published by Alibaba Cloud. The two target models belong to the same generation (2.5) and differ in size, which lets us ask whether size changes behaviour. The judge belongs to a newer generation (Qwen3) and was trained for a different job.

::: documented
All three models were named in the Individual Learning Plan. The project did not choose them, and the plan's rule that no model may be added after the experiment was fixed was followed.
:::

## The sources that were read

The plan listed the sources. For this project the four papers and reports were downloaded as PDF files, converted to text, and searched for the specific facts used. Quotes in the project documents were copied from the files.

| Source | What it contributed to the project |
|---|---|
| JailbreakBench (Chao et al., 2024) | The requests, the matched harmful/benign design, greedy decoding, showing the judge the original request, and the lesson that judges must be validated |
| XSTest (Röttger et al., 2024) | The idea of over-refusal and the three-level refusal scale used in the audit |
| StrongREJECT (Souly et al., 2024) | The distinction between not refusing and actually giving harmful content |
| NIST AI 600-1 (2024) | The governance frame: document assumptions, annotator instructions and measurement error |
| Inspect documentation (UK AI Security Institute) | A way of structuring an evaluation, described below |
| Model and dataset cards on Hugging Face | Exact versions, default settings, the judge's output format |

**Inspect** is a software framework for running AI evaluations. Its documentation describes every evaluation as four parts: a **dataset** of test items, a **solver** that produces an answer for each item, a **scorer** that evaluates the answer, and a **log** of everything that happened. We did not use the Inspect software. We followed the same four-part structure in plain code, because the learning plan specified that the pipeline be written with Python and Hugging Face Transformers.

The verified facts and quotes from all sources are collected in `01_protocol/04_source_notes.md`.

## The software

A **pipeline** is a series of programs that are run in order, each taking the output of the one before. The pipeline here is written in **Python**, a widely used programming language. Python programs use add-on packages called **libraries**.

| Tool | What it is | What it did here |
|---|---|---|
| Python 3.12 | Programming language | Everything is written in it |
| PyTorch 2.14.1 | Library for the arithmetic behind AI models | Ran the models on the GPU |
| Transformers 5.22.2 | Hugging Face's library for loading and running language models | Loaded the three models, applied chat templates, generated text |
| pandas | Library for working with tables | Selected prompts, joined labels to responses, built result tables |
| statsmodels and SciPy | Statistics libraries | Wilson intervals and the McNemar test |
| Matplotlib | Charting library | The four result charts and the diagrams in this guide |
| Jupyter | A document format that mixes code with its output (a **notebook**) | The clean analysis notebook |
| pandoc | A document converter | Turned the report text into Word files, and this guide into a PDF |
| python-pptx | Library for PowerPoint files | Drew the final presentation, and built the first version from the school's template. A second version was built with pptxgenjs, a similar library that runs on Node.js |
| Microsoft PowerPoint and Word | Office programs | Rendered every slide as an image for checking; produced PDF copies |

The exact version of every library is recorded in `03_pipeline/requirements_frozen.txt`, so the same software can be installed again.

A **virtual environment** is a private folder holding its own copy of Python libraries, kept apart from the rest of the computer. The project has one, in `.venv/`. This guarantees that the versions used here are not disturbed by other software on the laptop.

## The hardware

One laptop: Windows 11, with an NVIDIA GeForce RTX 3050 Laptop GPU that has 4 GB of memory. All three models ran on this GPU. Producing the 240 responses took 1,775 seconds, a little under 30 minutes (871 seconds for the smaller model and 904 for the larger).

::: documented
The learning plan anticipated a weaker machine: "If local GPU inference is unavailable, I will use quantised or CPU inference." The GPU turned out to be usable, so this fallback was not needed.
:::

## A map of the project folder

Each numbered folder corresponds to a stage of the work.

| Folder | Contents | Role |
|---|---|---|
| `01_protocol/` | Research questions and threat model; selection rules; labels, metrics and rubric; source notes; pilot log; freeze manifest | The written rules, fixed before the main run |
| `02_data/` | Source files; the 20 selected pairs; pilot data; the locked 240 responses; judge scores; audit files | Everything that was measured |
| `03_pipeline/` | The numbered Python programs, the configuration file, the notebook | The code that did the work |
| `04_results/` | Tables, charts, error analysis, verification report | What the data showed |
| `05_report/` | Report and Safety Evaluation Card | Write-ups |
| `06_presentation/` | The slides, a PDF copy, a question-and-answer sheet | The submitted deliverable |
| `07_guide/` | This guide and the files that build it | Explanation |
| `sources_cache/`, `models_cache/`, `.venv/` | Source PDFs, downloaded models, software | Supporting material |

One file deserves special mention: `03_pipeline/config.py`. It is the single place where every setting of the experiment is written: the model versions, the generation settings, the exact jailbreak wordings, the selection rules and the seed. Every program reads its settings from this one file, so there is no risk of two programs quietly using different values.

::: recap
- Three documents defined the task; two checklists were built from them.
- The data is **JBB-Behaviors**: 100 harmful and 100 matched benign requests.
- Two **target models** (Qwen2.5 at two sizes) and one **judge** (Qwen3Guard) were used, all named in the plan and all pinned to exact versions.
- The **pipeline** is plain Python with the Transformers library, structured as dataset, solver, scorer, log.
- Everything ran on one laptop GPU; generation took about 30 minutes.
- All settings live in one file, `config.py`.
:::
