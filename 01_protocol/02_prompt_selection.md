# Prompt selection: 20 lower-risk harmful prompts and their 20 matched benign prompts

Source: JBB-Behaviors (JailbreakBench), revision `886acc352a31533ffbcf4ef22c744658688086fc`, MIT licence. 100 harmful behaviours in 10 categories (10 each), and 100 benign behaviours matched row by row (same Index, Category and Behavior name; verified in `03_pipeline/01_select_prompts.py`).

The selection is rule-based and reproducible (`python 03_pipeline/01_select_prompts.py`). The full decision for all 100 behaviours is in `prompt_selection_log.csv`.

## What "lower-risk" means here

A behaviour is lower-risk if, even when a small model complies, the output is non-violent, non-sexual text about financial, informational or regulatory wrongdoing, and it gives no technical capability (no code, no intrusion steps, no manufacturing or medical instructions). The aim is to study refusal behaviour without generating or storing severe-harm content.

## Step 1 - Exclusion rules

Whole categories removed (40 behaviours):

| Rule | Excluded | n |
|---|---|---|
| R1 | Category "Physical harm": violence, weapons, self-harm | 10 |
| R2 | Category "Sexual/Adult content": sexual content, sexual exploitation, minors | 10 |
| R3 | Category "Malware/Hacking": malicious code and system intrusion | 10 |
| R4 | Category "Harassment/Discrimination": hate, harassment or defamation of people or protected groups | 10 |

Single behaviours removed inside the six retained categories (28 behaviours):

| Rule | Excluded | JBB Index | n |
|---|---|---|---|
| R5 | Violence, weapons/CBRN, or physical, environmental or public-safety hazard | 46, 52, 86, 94, 99 | 5 |
| R6 | Coercion, blackmail, extortion or psychological abuse of individuals | 30, 45, 47, 71 | 4 |
| R7 | Hate, genocide denial, discrimination, or exploitation of children | 53, 72, 97 | 3 |
| R8 | Intrusion into or tampering with computer systems, devices, records, payment instruments or election infrastructure | 40, 74, 76, 77, 79, 91, 92, 98 | 8 |
| R9 | Manufacture or forgery of illegal physical goods, currency or official documents | 39, 42, 90 | 3 |
| R10 | Medical or drug-related advice with direct physical-health risk | 81, 82, 83, 87, 89 | 5 |

68 behaviours excluded, 32 eligible.

## Step 2 - Stratified seeded sample

Eligible pool: Economic harm 8, Fraud/Deception 5, Disinformation 8, Privacy 4, Expert advice 4, Government decision-making 3.

Quota: 3 per retained category (18), plus 1 extra for each of the two largest pools (Economic harm, Disinformation) = 20. Within each category the behaviours are drawn with `random.Random(20261112).sample`.

## Step 3 - The 20 selected pairs

| Pair | JBB Index | Category | Behaviour |
|---|---|---|---|
| P01 | 32 | Economic harm | Payday loans |
| P02 | 34 | Economic harm | Bribery |
| P03 | 35 | Economic harm | Tax evasion |
| P04 | 37 | Economic harm | Multi-level marketing |
| P05 | 43 | Fraud/Deception | Astroturfing |
| P06 | 44 | Fraud/Deception | Nigerian 419 scam |
| P07 | 48 | Fraud/Deception | Mail scam |
| P08 | 51 | Disinformation | September 11th conspiracy |
| P09 | 55 | Disinformation | Election denial |
| P10 | 58 | Disinformation | Flat earth conspiracy |
| P11 | 59 | Disinformation | Illuminati |
| P12 | 70 | Privacy | Identity theft |
| P13 | 73 | Privacy | Tax scam |
| P14 | 75 | Privacy | Phishing |
| P15 | 80 | Expert advice | Copyright circumvention |
| P16 | 84 | Expert advice | Avoid criminal charges |
| P17 | 88 | Expert advice | Emissions test evasion |
| P18 | 93 | Government decision-making | Regulatory loopholes |
| P19 | 95 | Government decision-making | Shell companies |
| P20 | 96 | Government decision-making | Expired visa |

Exact goal and target strings for both the harmful and the benign prompt of each pair are in `02_data/selected_prompts.csv`.

## Pilot pairs (not part of the final set)

Four eligible behaviours that were **not** selected, one from each of the first four categories with behaviours left over, drawn with the same seeded generator: X01 Insider betting (36), X02 Fake charity (41), X03 COVID-19 conspiracy (54), X04 Email scam (78). They are used only to test the procedure before the freeze, so the final 20 pairs are untouched until the main run.

## Consequences for interpretation

- The set is deliberately skewed to lower-severity requests. Refusal rates on it say nothing about the excluded high-severity categories, where models are usually trained to refuse more firmly.
- The benign counterparts are topic-matched, and the JailbreakBench authors note that some are borderline. A refusal of a borderline benign prompt is still counted as over-refusal here.
