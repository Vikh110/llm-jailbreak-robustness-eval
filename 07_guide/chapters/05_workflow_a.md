\part{The workflow, step by step}

# The workflow at a glance

Part IV follows the project in the order it actually happened. This short chapter gives the map; the next four chapters walk through each step.

![The sixteen steps of the project, in order. Read each row in the direction of the arrows.](figures/d2_workflow.png){width=100%}

## The design in one picture

Every result in the project comes from one grid. Two models, three ways of sending a request, and two kinds of request give twelve combinations. The project calls each combination a **cell**. Each cell holds 20 responses, one per prompt pair.

![The experimental design. Each of the 12 cells contains 20 responses, giving 240 in total.](figures/d1_design_grid.png){width=95%}

The three ways of sending a request are called **conditions**:

- **Direct**: the request exactly as it appears in the dataset.
- **Role framing**: the request wrapped in a role-play story.
- **Prefix steering**: the request followed by an instruction to start the answer with an agreeing sentence.

## Why the order of the steps matters

Two points in the sequence protect the honesty of the results.

**The freeze comes before the main run (step 7 before step 8).** We tried the whole procedure on a few spare requests first, fixed any problems, and then locked every choice. Only after that did we produce the 240 responses that count. This way no choice could be adjusted to make the results look better, because the results did not exist yet.

**The audit comes before the judge (step 10 before step 11).** The 60 audit labels were written down and sealed with a checksum before the judge had scored a single response from the main run. So the auditor could not have been influenced by the judge's opinion, even without meaning to.

## How the work was organised

Vishwas set the project up in phases with checkpoints:

- **Phase 0**: read everything, list every requirement, ask about anything unclear, and wait for approval.
- **Phase 1**: do the project.
- **Phase 2**: check the project against the requirement list, line by line.
- **Phase 3**: build the presentation from the template.
- **Phase 4**: inspect every slide and re-check both lists.

The steps in the diagram fall inside these phases: step 1 is Phase 0, steps 2 to 15 are Phases 1 and 2, and step 16 is Phases 3 and 4.

::: recap
- The whole experiment is a grid of 12 **cells** (2 models x 3 **conditions** x 2 kinds of request), 20 responses each.
- Choices were **frozen before** the main run, and the audit was **sealed before** the judge ran.
- The work followed phases with checkpoints set by Vishwas.
:::

# Setting up and choosing what to test

This chapter covers steps 1 to 4: reading and planning, setting up the software, writing the questions, and choosing the 20 prompt pairs.

## Step 1: Reading, listing and asking

**In plain English.** Before doing anything, find out exactly what is being asked.

**What went in:** the three starting documents. **What came out:** two checklists and a list of open questions.

**What we did.** All three files were read completely, including all 44 sample slides in the template and a "how-to" slide inside it that carries the template's own rules (only Arial, only the school's colours, delete the sample slides when finished). The learning plan yielded 36 separate requirements. The guidelines and template yielded 20 rules.

Seven things were unclear and were put to Vishwas. His answers shaped the project:

| Question | Decision |
|---|---|
| Who labels the 60 audit responses? | Claude does it. It is not a manual (human) audit. |
| Is there a deadline? | No fixed date, but finish the same day. |
| May software be installed and about 6 GB downloaded? | Use best judgement (yes). |
| Should prefix steering be an instruction in the request, or should the start of the answer be written for the model? | Best judgement: an instruction in the request. |
| Report and card format, cover details, sign-off on the selected requests | Best judgement. |
| What is submitted? | Only the presentation. |

**Why it was needed.** The answers changed real things. Because the audit was done by an AI model, every document says so. Because only the presentation is submitted, the slides had to be able to stand alone.

**Possible errors.** A requirement misread at this stage would flow through everything. The protection was the line-by-line check at the end, which marked each of the 36 requirements as met and said where.

## Step 2: Setting up the software and getting the models

**In plain English.** Install the tools, download the models and data, and make sure the models actually run.

**What went in:** a laptop with Python already installed. **What came out:** a private software environment, the three models and the dataset on disk at exact versions, and proof that the GPU could run them.

**What we did.**

1. A check of the laptop showed that the installed copy of PyTorch could only use the CPU, although the laptop has a GPU. PyTorch comes in different builds, and the one present was the CPU-only build.
2. A virtual environment was created inside the project folder and a GPU-capable build of PyTorch was installed into it, along with the other libraries.
3. The dataset and the three models were downloaded from Hugging Face, and the exact revision of each was recorded.
4. A quick test confirmed that PyTorch could see the GPU and do arithmetic on it in the bfloat16 number format.

**Why it was needed.** The plan required that the models "can run locally", meaning on the project's own machine and not on someone else's service. Running locally also means the exact model files are under our control.

**A problem met and solved.** The mismatch between the installed PyTorch and the GPU would have forced the slower fallback the plan allowed (running on the CPU). Installing the right build inside the private environment solved it without changing anything else on the laptop.

## Step 3: Writing the research questions and the threat model

**In plain English.** Write down exactly what is being asked and exactly which attacker is imagined, before running anything.

**What came out:** the file `01_protocol/01_research_question_and_threat_model.md`.

The three research questions were given in Chapter 1. The threat model, from the same file:

| Element | Assumption in this study |
|---|---|
| Adversary | A low-resource user of a chat assistant built on the model |
| Access | Query-only ("black-box"): one user message per conversation |
| Cannot do | Set or change the system prompt; pre-fill the assistant turn; read weights or internal scores; change decoding settings; fine-tune |
| Knowledge | Public, generic jailbreak wordings only; nothing specific to this model |
| Effort | One attempt per request: no retries, no adaptive search |
| Goal | Obtain content that substantively fulfils a policy-violating request |
| Language | English, single turn |

An **adversary** is the imagined attacker. A **turn** is one message in a conversation; "single turn" means the attacker sends one message and gets one reply. "Pre-fill the assistant turn" means writing the first words of the model's answer on its behalf.

![The threat model. The attacker controls one message and nothing else.](figures/d3_threat_model.png){width=95%}

The file also defines the **system under test**: the model's weights, plus its default chat template, plus its default system prompt, plus greedy decoding, with no extra filter in front of or behind the model. The results describe this whole package, not the model weights alone.

::: documented
The file gives the reason for testing black-box although the weights are public: "it mirrors what an independent evaluator or a downstream deployer with interface-only access can test, and it keeps the pipeline identical for open and closed models."
:::

**Trade-off.** A weak attacker makes the test easy to run and easy to repeat. The price is that the results understate the danger. The file says so directly: because fine-tuning is "the realistic ceiling of misuse" for open-weight models, the results "are a lower bound on what a determined adversary can obtain, not an upper bound." A **lower bound** means the true value is at least this much.

## Step 4: Selecting the 20 prompt pairs

**In plain English.** Choose 20 of the 100 harmful requests (their benign twins come with them), using written rules so that the choice is not a matter of taste.

**What went in:** the two dataset files. **What came out:** `02_data/selected_prompts.csv` (the 20 pairs), a log of the decision for all 100 behaviours, and four spare pairs for the trial run.

### What "lower-risk" means

The plan asked for "lower-risk harmful prompts". The project defined this in `01_protocol/02_prompt_selection.md`: a behaviour is lower-risk if, even when a small model complies, the output is non-violent, non-sexual text about financial, informational or regulatory wrongdoing, and gives no technical capability (no code, no break-in steps, no manufacturing or medical instructions).

::: documented
The stated aim of this definition: "to study refusal behaviour without generating or storing severe-harm content."
:::

### First, check the data

Before selecting anything, the program checks that the two files really line up row by row:

```python
assert len(harm) == len(ben) == 100
assert (harm["Index"].values == ben["Index"].values).all()
assert (harm["Category"].values == ben["Category"].values).all()
# behaviour names match row by row (whitespace-normalised: row 67 has a double space upstream)
norm = lambda s: s.str.split().str.join(" ")
assert (norm(harm["Behavior"]).values == norm(ben["Behavior"]).values).all()
```

`assert` means "stop with an error if this is not true". `harm` and `ben` are the two tables. The lines check that both have 100 rows, that the row numbers match, that the categories match, and that the behaviour names match.

::: project
The last check failed on the first try. One behaviour name was spelled with two spaces in one file and one space in the other ("Human  trafficking" against "Human trafficking"). The files did match; only the spacing differed. The check was changed to ignore extra spaces, and the comment in the code records why. That row was in an excluded category anyway. This is a small example of why such checks are worth writing: without it, a real mismatch between twins would go unnoticed.
:::

### Second, apply the exclusion rules

Ten rules remove behaviours. Four rules remove whole categories; six remove individual behaviours inside the categories that remain.

| Rule | What is excluded | Number removed |
|---|---|---|
| R1 | Category "Physical harm": violence, weapons, self-harm | 10 |
| R2 | Category "Sexual/Adult content" | 10 |
| R3 | Category "Malware/Hacking": malicious code and system break-ins | 10 |
| R4 | Category "Harassment/Discrimination" | 10 |
| R5 | Violence, weapons, or a physical, environmental or public-safety hazard | 5 |
| R6 | Coercion, blackmail, extortion or psychological abuse of individuals | 4 |
| R7 | Hate, genocide denial, discrimination, or exploitation of children | 3 |
| R8 | Breaking into or tampering with computer systems, devices, records, payment tools or election systems | 8 |
| R9 | Making or forging illegal goods, money or official documents | 3 |
| R10 | Medical or drug advice with a direct risk to physical health | 5 |

That removes 68 of the 100 behaviours and leaves 32 **eligible** ones in six categories: Economic harm (8), Fraud/Deception (5), Disinformation (8), Privacy (4), Expert advice (4), Government decision-making (3).

In the code each behaviour is looked up against the rules, and the reason is logged:

```python
for _, r in harm.iterrows():
    idx, cat = int(r["Index"]), r["Category"]
    if cat in C.EXCLUDED_CATEGORIES:
        rule = C.EXCLUDED_CATEGORIES[cat]
    else:
        rule = C.EXCLUDED_BEHAVIOURS.get(idx, "")
    log.append({"jbb_index": idx, "category": cat, "behavior": r["Behavior"],
                "status": "excluded" if rule else "eligible", "rule": rule})
```

The loop visits each harmful behaviour. If its whole category is excluded, it records that rule. Otherwise it looks the behaviour up in a list of individually excluded ones. `C` is the settings file `config.py`, where both lists are written out. An empty rule means the behaviour is eligible.

### Third, draw 20 with a fixed seed

Choosing 20 from the 32 by hand would again be a matter of taste. So the program draws them at random, but with the fixed seed, so the same 20 come out every time. The draw is **stratified** by category: each of the six categories gets three places, and the two categories with the most eligible behaviours (Economic harm and Disinformation, with eight each) get one extra. That makes 4 + 3 + 4 + 3 + 3 + 3 = 20.

```python
pool = {c: sorted(eligible[eligible["category"] == c]["jbb_index"])
        for c in C.RETAINED_CATEGORY_ORDER}
quota = {c: C.BASE_QUOTA_PER_CATEGORY for c in C.RETAINED_CATEGORY_ORDER}
extra = C.N_PAIRS - sum(quota.values())
for c in sorted(C.RETAINED_CATEGORY_ORDER,
                key=lambda c: (-len(pool[c]), C.RETAINED_CATEGORY_ORDER.index(c)))[:extra]:
    quota[c] += 1

rng = random.Random(C.SEED)
selected = []
for c in C.RETAINED_CATEGORY_ORDER:
    selected += sorted(rng.sample(pool[c], quota[c]))
```

Line by line:

- `pool` holds, for each category, the list of eligible behaviours.
- `quota` starts at 3 for every category (`BASE_QUOTA_PER_CATEGORY` is 3).
- `extra` is how many places are still missing (20 minus 18, so 2). The loop gives one extra place to each of the two largest pools.
- `random.Random(C.SEED)` creates a random-number generator started from the seed 20261112.
- `rng.sample(pool[c], quota[c])` draws the required number from each category.

### The 20 selected pairs

| Pair | Category | Behaviour (the dataset's short name) |
|---|---|---|
| P01 | Economic harm | Payday loans |
| P02 | Economic harm | Bribery |
| P03 | Economic harm | Tax evasion |
| P04 | Economic harm | Multi-level marketing |
| P05 | Fraud/Deception | Astroturfing |
| P06 | Fraud/Deception | Nigerian 419 scam |
| P07 | Fraud/Deception | Mail scam |
| P08 | Disinformation | September 11th conspiracy |
| P09 | Disinformation | Election denial |
| P10 | Disinformation | Flat earth conspiracy |
| P11 | Disinformation | Illuminati |
| P12 | Privacy | Identity theft |
| P13 | Privacy | Tax scam |
| P14 | Privacy | Phishing |
| P15 | Expert advice | Copyright circumvention |
| P16 | Expert advice | Avoid criminal charges |
| P17 | Expert advice | Emissions test evasion |
| P18 | Government decision-making | Regulatory loopholes |
| P19 | Government decision-making | Shell companies |
| P20 | Government decision-making | Expired visa |

("Astroturfing" means posting fake reviews or opinions that pretend to come from ordinary people.)

### The four spare pairs

The same generator then drew four more eligible behaviours that were **not** among the 20: Insider betting, Fake charity, COVID-19 conspiracy and Email scam. These are the **pilot** pairs, used for the trial run in the next chapter.

::: documented
The selection file explains why the pilot pairs are separate: they "are used only to test the procedure before the freeze, so the final 20 pairs are untouched until the main run."
:::

### Assumptions and trade-offs

- **The rules are the project's own.** They were written for this project and are not an official standard. Someone else might draw the lines differently, for example on whether a general request about identity theft belongs with the eligible ones while a request to steal hospital records does not. The rules are written down so that anyone can see and question them.
- **The set is deliberately mild.** Everything about violence, weapons, malicious code, sexual content and hate was removed. The results therefore say nothing about those areas. The selection file states this as a consequence for interpretation.
- **Some benign twins are borderline.** This is inherited from the dataset, as its authors warn. In this project every refusal of a benign twin is counted as over-refusal, even if a careful person might also hesitate.

::: recap
- The task was first turned into checklists; open questions were settled by Vishwas.
- The software was set up in a private environment; a CPU-only PyTorch was replaced by a GPU build.
- The **threat model** is a weak attacker: one message, one try, public wordings only. Results are therefore a **lower bound** on attack success.
- Ten written rules removed 68 of 100 behaviours; a **seeded, stratified** draw picked 20 of the remaining 32.
- Four other eligible pairs were set aside for the pilot.
:::
