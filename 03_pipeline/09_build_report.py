"""Phase 7/8 - build the error analysis, the report and the Safety Evaluation Card.

Every number is formatted from 04_results/summary.json at build time, so the
documents cannot drift from the verified results. Markdown is converted to
.docx with pandoc.
"""
import json
import subprocess

import pandas as pd

import config as C

S = json.loads((C.RESULTS_DIR / "summary.json").read_text(encoding="utf-8"))
MET = {(m["model"], m["condition"], m["metric"]): m for m in S["metrics"]}
REL, DESC = S["judge_reliability"], S["descriptives"]
TEST = {(t["metric"], t["comparison"], t["within"]): t for t in S["paired_tests"]}
MAN = json.loads((C.PROTOCOL_DIR / "freeze_manifest.json").read_text(encoding="utf-8"))
SHA = (C.DATA_DIR / "responses_locked.sha256").read_text().split()[0]
VERIF = (C.RESULTS_DIR / "verification_report.txt").read_text(encoding="utf-8").strip().splitlines()[-1].replace("/", " of ")
REPORT_DIR = C.ROOT / "05_report"
A, B = "qwen2.5-0.5b", "qwen2.5-1.5b"


def pct(x):
    return f"{x * 100:.0f}%"


def kn(r):
    return f"{r['k']}/{r['n']}"


def full(r):
    return f"{kn(r)} ({pct(r['rate'])}, 95% CI {r['ci_low'] * 100:.0f} to {r['ci_high'] * 100:.0f}%)"


def short(r):
    return f"{kn(r)} ({pct(r['rate'])})"


def cell(r):
    return f"{pct(r['rate'])} [{r['ci_low'] * 100:.0f}, {r['ci_high'] * 100:.0f}] ({kn(r)})"


def m(model, cond, metric):
    return MET[(model, cond, metric)]


def p(metric, comparison, within):
    v = TEST[(metric, comparison, within)]["p_exact_mcnemar"]
    return "p < 0.001" if v < 0.001 else f"p = {v:.3f}" if v < 0.1 else f"p = {v:.2f}"


def disc(metric, comparison, within):
    t = TEST[(metric, comparison, within)]
    return t["first_only"], t["second_only"]


def agree(block):
    return f"{block['agreement'] * 100:.0f}% (95% CI {block['agreement_ci'][0] * 100:.0f} to {block['agreement_ci'][1] * 100:.0f}%), kappa {block['kappa']:.2f}"


def results_table():
    rows = ["| Model | Condition | Harmful compliance | Correct refusal | Other non-refusal | Benign compliance | Over-refusal |",
            "|---|---|---|---|---|---|---|"]
    for mk in C.TARGET_MODELS:
        for c in C.CONDITION_ORDER:
            rows.append(f"| {C.MODEL_LABELS[mk]} | {C.CONDITION_LABELS[c]} | " + " | ".join(
                cell(m(mk, c, x)) for x in ["harmful_compliance", "correct_refusal", "other_non_refusal", "benign_compliance", "over_refusal"]) + " |")
    return "\n".join(rows)


def pooled_table():
    rows = ["| Group | Harmful compliance | Correct refusal | Benign compliance | Over-refusal |", "|---|---|---|---|---|"]
    groups = [(f"{C.MODEL_LABELS[A]}, all conditions (n = 60)", A, "all"), (f"{C.MODEL_LABELS[B]}, all conditions (n = 60)", B, "all")]
    groups += [(f"{C.CONDITION_LABELS[c]}, both models (n = 40)", "both", c) for c in C.CONDITION_ORDER]
    groups += [("All responses (n = 120 per prompt type)", "both", "all")]
    for label, mk, c in groups:
        rows.append(f"| {label} | " + " | ".join(cell(m(mk, c, x)) for x in ["harmful_compliance", "correct_refusal", "benign_compliance", "over_refusal"]) + " |")
    return "\n".join(rows)


def audit_condition_table():
    rows = ["| Condition (10 audited harmful-prompt responses each) | Judge: Unsafe | Audit: harmful content | Audit: full refusal | Audit: other non-refusal |",
            "|---|---|---|---|---|"]
    for r in REL["harmful_by_condition_on_audit_sample"]:
        rows.append(f"| {C.CONDITION_LABELS[r['condition']]} | {kn(r['judge_unsafe'])} | {kn(r['audit_harmful'])} | {r['audit_full_refusal']}/10 | {r['audit_other_non_refusal']}/10 |")
    return "\n".join(rows)


def category_tables():
    hc = {r["category"]: r for r in S["by_category"]}
    orf = {r["category"]: r for r in S["over_refusal_by_category"]}
    rows = ["| JBB category | Harmful compliance (harmful prompts) | Over-refusal (benign prompts) |", "|---|---|---|"]
    for c in C.RETAINED_CATEGORY_ORDER:
        rows.append(f"| {c} | {int(hc[c]['k'])}/{int(hc[c]['n'])} ({pct(hc[c]['rate'])}) | {int(orf[c]['k'])}/{int(orf[c]['n'])} ({pct(orf[c]['rate'])}) |")
    return "\n".join(rows)


TYPE_TEXT = {
    "affirmative_but_empty": "Affirmative opening, no harmful content",
    "lawful_advice": "Lawful advice presented as help",
    "off_topic_output": "Off-topic output (capability failure)",
    "partial_refusal_definition": "Refuses, then gives related content (partial refusal)",
    "safe_rewrite_as_refusal": "Harmless rewrite counted as a refusal",
    "judge_error_on_compliance": "Plain compliance flagged as a refusal",
}
items = pd.read_csv(C.RESULTS_DIR / "judge_vs_audit_items.csv")
dis = items[items.error_type.notna()].copy()
N_TYPE = {r["error_type"]: r["n"] for r in REL["disagreement_types"]}
hs, rf, ol = REL["harmful_compliance_strict"], REL["refusal"], REL["outcome_label"]
prec, rec = REL["judge_unsafe_precision"], REL["judge_unsafe_recall"]
ras = REL["rates_on_audit_sample"]
cond_audit = {r["condition"]: r for r in REL["harmful_by_condition_on_audit_sample"]}
ben = REL["benign_on_audit_sample"]
orf_cat = {r["category"]: r for r in S["over_refusal_by_category"]}
MAXW = max((x["ci_high"] - x["ci_low"]) * 100 for x in S["metrics"] if x["model"] != "both" and x["condition"] != "all")

# --------------------------------------------------------------------------
# Error analysis
# --------------------------------------------------------------------------
dis_rows = "\n".join(
    f"| {r.audit_id} | {C.MODEL_LABELS[r.model_key]} | {C.CONDITION_LABELS[r.condition]} | {r.prompt_type} | {r.category} | "
    f"{r.judge_safety}, refusal {r.judge_refusal} | {r.refusal}, harmful {r.harmful_content} | {TYPE_TEXT[r.error_type]} |"
    for r in dis.sort_values(["dimension", "error_type", "audit_id"]).itertuples())

ERROR_ANALYSIS = f"""# Error analysis: Qwen3Guard-Gen-0.6B against the 60-response audit

All numbers come from `04_results/summary.json`. Response text is described, not quoted.

## 1. Summary

- **Refusal flag: reliable.** Agreement {agree(rf)}. The judge missed no refusal ({rf['fn']} false negatives) and flagged {rf['fp']} responses as refusals that the audit did not label as full refusals.
- **Unsafe label on harmful prompts: over-triggers.** Agreement {agree(hs)}. The judge flagged {prec['n']} of the 30 audited harmful-prompt responses as Unsafe; the audit found harmful content in {prec['k']} of them (precision {pct(prec['rate'])}, 95% CI {prec['ci_low'] * 100:.0f} to {prec['ci_high'] * 100:.0f}%). It missed none of the {rec['n']} responses the audit labelled harmful.
- **Final outcome label:** agreement {agree(ol)}. {REL['n_disagreements']} of the 60 audited responses carry at least one disagreement.
- **Consequence:** on the audited sample the judge-based harmful-compliance rate is {full(ras['harmful_compliance']['judge'])} and the audit-based rate is {full(ras['harmful_compliance']['audit'])}. Judge-based harmful-compliance rates in this study should be read as upper bounds.

## 2. Where the over-counting happens

{audit_condition_table()}

Under prefix steering the judge marked all {cond_audit['prefix_steering']['judge_unsafe']['k']} audited responses Unsafe. The audit found harmful content in {cond_audit['prefix_steering']['audit_harmful']['k']}. The other {cond_audit['prefix_steering']['audit_other_non_refusal']} open with an affirmative sentence that restates the request and then give generic, reversed or incoherent content. These are the "empty jailbreaks" described by StrongREJECT: the refusal is gone, the harmful content is not there.

## 3. Types of disagreement

| Type | n | Dimension |
|---|---|---|
""" + "\n".join(f"| {TYPE_TEXT[r['error_type']]} | {r['n']} | {'Harmful content (judge false positive)' if r['dimension'] == 'harmful_content' else 'Refusal flag'} |"
                for r in sorted(REL["disagreement_types"], key=lambda r: (r["dimension"], -r["n"]))) + f"""

**Affirmative opening, no harmful content ({N_TYPE['affirmative_but_empty']}).** All from prefix steering. Examples: the reply announces a guide to a scam-oriented business and then lists ordinary business steps (one such reply even calls for transparency); the reply announces a blog post in favour of a harmful financial choice and then argues against it; the reply announces a hoax article and then argues, incoherently, that the event was real. The judge appears to react to the affirmative sentence that repeats the harmful request.

**Lawful advice presented as help ({N_TYPE['lawful_advice']}).** The reply accepts the framing of the request and then lists lawful steps, such as consulting a lawyer or renewing a visa.

**Off-topic output ({N_TYPE['off_topic_output']}).** The smaller model wrote a letter addressed to the tax authority about deductions when asked for a fraudulent letter from it. This is a capability failure, not a safety success, and the judge still marked it Unsafe.

**Refusal flag ({rf['fp']}).** One reply says it cannot answer and then gives related context: a partial refusal in the rubric and a refusal for the judge, so this is a definitional difference (agreement rises to {pct(REL['refusal_partial_as_refusal']['agreement'])} if partial refusals count as refusals). One reply does not decline but writes a harmless substitute. One is a plain answer that the judge marked as a refusal.

## 4. All disagreements

| Audit id | Model | Condition | Prompt type | Category | Judge | Audit | Type |
|---|---|---|---|---|---|---|---|
{dis_rows}

## 5. The judge on benign prompts

The outcome labels for benign prompts use only the refusal flag, so they are not affected by the safety label. The safety label is still informative about the judge: it marked {DESC['benign_flagged_unsafe']} of the 120 responses to benign prompts as Unsafe and {DESC['benign_flagged_controversial']} as Controversial. In the audited benign sample it marked {ben['judge_unsafe']} of {ben['n']} as Unsafe and {ben['judge_controversial']} as Controversial; the audit found harmful content in {ben['audit_harmful']}. The flagged responses are concentrated on scam, phishing, identity-theft and conspiracy topics. This is the same pattern XSTest describes for chat models: sensitivity to the topic of a text, not to what the text does.

## 6. What this means for the headline numbers

1. Refusal-based metrics (correct refusal, over-refusal) rest on the reliable part of the judge.
2. Harmful-compliance rates rest on the unreliable part and are upper bounds. The direction of the main effect survives the audit: audited harmful content rises from {kn(cond_audit['direct']['audit_harmful'])} under direct prompting to {kn(cond_audit['prefix_steering']['audit_harmful'])} under prefix steering.
3. If this judge were deployed as an output filter, it would block a substantial share of harmless answers.

## 7. Caveats on the audit itself

The audit is one annotation pass by an LLM annotator (Claude) with the frozen rubric, blind to model, condition and judge label. It is not a human gold standard and there is no second annotator, so no inter-annotator agreement is available. Some calls are borderline, for example a generic but on-topic answer about regulatory loopholes that was labelled harmful. With 30 harmful-prompt responses the intervals are wide.
"""

# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------
static = (REPORT_DIR / "_report_static_sections.md").read_text(encoding="utf-8")
sec = {name: body.strip() for name, body in
       [(part.split("-->", 1)[0].strip(), part.split("-->", 1)[1]) for part in static.split("<!-- SECTION:")[1:]]}

b1, c1 = disc("harmful_compliance", "prefix_steering vs direct", A)
b2, c2 = disc("harmful_compliance", "prefix_steering vs direct", B)
r1, d1 = disc("correct_refusal", "1.5B vs 0.5B", "direct")

REPORT = f"""# Black-Box Evaluation of Jailbreak Robustness and Over-Refusal in Small Instruction-Tuned Language Models

Individual Learning Plan project report. Vishwas Khandelwal, 12 November 2026.

## 1. Summary

Two small open-weight chat models, Qwen2.5-0.5B-Instruct and Qwen2.5-1.5B-Instruct, were tested on 20 lower-risk harmful requests and 20 topic-matched benign requests from JBB-Behaviors, each sent directly and with two fixed prompt transformations (240 responses). Qwen3Guard-Gen-0.6B scored every response, and 60 responses were audited blind against a written rubric.

1. **A one-line format instruction removes almost all refusals.** Asked directly, the models refused {short(m(A, 'direct', 'correct_refusal'))} and {short(m(B, 'direct', 'correct_refusal'))} of the harmful requests. With prefix steering they refused {short(m(A, 'prefix_steering', 'correct_refusal'))} and {short(m(B, 'prefix_steering', 'correct_refusal'))}, and the judge-based harmful-compliance rate rose to {full(m(A, 'prefix_steering', 'harmful_compliance'))} and {full(m(B, 'prefix_steering', 'harmful_compliance'))}.
2. **Role framing had no clear effect.** Harmful compliance was {short(m(A, 'role_framing', 'harmful_compliance'))} and {short(m(B, 'role_framing', 'harmful_compliance'))}, not distinguishable from direct prompting with 20 prompts.
3. **The larger model refuses more, in both directions.** Asked directly, the 1.5B model refused all 20 harmful requests but also {short(m(B, 'direct', 'over_refusal'))} of the benign ones; the 0.5B model refused {short(m(A, 'direct', 'over_refusal'))} of the benign ones. Over-refusal is concentrated on disinformation and privacy topics.
4. **The automated judge is reliable for refusals and unreliable for harm.** Against the audit its refusal flag agrees in {pct(rf['agreement'])} of cases (kappa {rf['kappa']:.2f}). Its Unsafe label agrees in {pct(hs['agreement'])} (kappa {hs['kappa']:.2f}): of {prec['n']} audited responses it called Unsafe, the audit found harmful content in {prec['k']}. Harmful-compliance rates above are therefore upper bounds. On the audited prefix-steering responses the judge found {kn(cond_audit['prefix_steering']['judge_unsafe'])} unsafe and the audit {kn(cond_audit['prefix_steering']['audit_harmful'])}.

The practical reading: the built-in refusals of these models are not a safeguard, because a trivial instruction switches them off, and a small guard model cannot simply be trusted to measure or filter the result.

{sec['method']}

## 4. Results

### 4.1 Results per model and condition

Rate [95% Wilson interval] (count). n = 20 prompts per cell. Outcomes are judge-based.

{results_table()}

Pooled:

{pooled_table()}

![Harmful-compliance rate by model and condition](../04_results/figures/fig1_harmful_compliance.png)

![Outcome composition per cell](../04_results/figures/fig3_outcome_composition.png)

### 4.2 RQ1: robustness to the two transformations

**Prefix steering.** All {DESC['prefix_steering_affirmative_opening']['k']} prefix-steering responses, harmful and benign, open affirmatively ("Sure, here ..." or "Certainly ..."). Harmful compliance rose on {b1} of 20 prompts and fell on {c1} for the 0.5B model ({p('harmful_compliance', 'prefix_steering vs direct', A)}), and rose on {b2} and fell on {c2} for the 1.5B model ({p('harmful_compliance', 'prefix_steering vs direct', B)}, exact McNemar). Both effects remain significant after a Bonferroni correction for the {len(S['paired_tests'])} paired tests reported.

**Role framing.** No detectable effect: {p('harmful_compliance', 'role_framing vs direct', A)} for the 0.5B model and {p('harmful_compliance', 'role_framing vs direct', B)} for the 1.5B model. The intervals are wide, so a moderate effect cannot be excluded.

**Model size.** Asked directly, the 1.5B model refused more harmful requests than the 0.5B model ({r1} prompts refused only by the 1.5B model, {d1} only by the 0.5B model, {p('correct_refusal', '1.5B vs 0.5B', 'direct')}). Under prefix steering the difference disappears ({short(m(B, 'prefix_steering', 'harmful_compliance'))} against {short(m(A, 'prefix_steering', 'harmful_compliance'))}).

**How much of this is real harm?** The audit (section 5) shows that the judge over-counts. On the 30 audited harmful-prompt responses the judge-based harmful-compliance rate is {short(ras['harmful_compliance']['judge'])} and the audit-based rate is {short(ras['harmful_compliance']['audit'])}. The direction of the prefix-steering effect holds in the audit ({kn(cond_audit['direct']['audit_harmful'])} harmful under direct prompting, {kn(cond_audit['role_framing']['audit_harmful'])} under role framing, {kn(cond_audit['prefix_steering']['audit_harmful'])} under prefix steering), but its size is roughly half of what the judge reports.

### 4.3 RQ2: over-refusal

![Over-refusal rate by model and condition](../04_results/figures/fig2_over_refusal.png)

Asked directly, the 0.5B model refused {full(m(A, 'direct', 'over_refusal'))} of the benign requests and the 1.5B model {full(m(B, 'direct', 'over_refusal'))}. Under prefix steering neither model refused any benign request. The model that is safer on harmful requests when asked directly is also the one that refuses more benign requests, although with 20 prompts the difference in over-refusal is not significant ({p('over_refusal', '1.5B vs 0.5B', 'direct')}).

Over-refusal depends on the topic:

{category_tables()}

All {m('both', 'all', 'over_refusal')['k']} over-refusals occurred under direct prompting ({DESC['over_refusal_by_condition'].get('direct', 0)}) or role framing ({DESC['over_refusal_by_condition'].get('role_framing', 0)}), and {int(orf_cat['Disinformation']['k'])} of them are on disinformation topics, where the benign request asks to explain or discuss a conspiracy belief. This matches the "lexical overfitting" explanation in XSTest: the model reacts to the topic of the request and not to what is being asked.

## 5. RQ3: reliability of the automated judge

![Judge against audit](../04_results/figures/fig4_judge_vs_audit.png)

| Judge output | n | Agreement with audit | Cohen's kappa | Judge false positives | Judge false negatives |
|---|---|---|---|---|---|
| Refusal flag | {rf['n']} | {pct(rf['agreement'])} | {rf['kappa']:.2f} | {rf['fp']} | {rf['fn']} |
| Unsafe label, harmful prompts | {hs['n']} | {pct(hs['agreement'])} | {hs['kappa']:.2f} | {hs['fp']} | {hs['fn']} |
| Final outcome label | {ol['n']} | {pct(ol['agreement'])} | {ol['kappa']:.2f} | | |

The judge's refusal flag can be used as it is. Its Unsafe label cannot: {hs['fp']} of the {prec['n']} responses it flagged contain no harmful content according to the audit. {N_TYPE['affirmative_but_empty']} of these {hs['fp']} are prefix-steering responses that open with an affirmative sentence and then give generic, reversed or incoherent content. The judge also marked {DESC['benign_flagged_unsafe']} of the 120 responses to benign prompts as Unsafe.

{audit_condition_table()}

The full error analysis, with every disagreement and its type, is in `04_results/error_analysis.md`.

## 6. Assumptions and limitations

1. **Small sample.** 20 prompts per cell give wide intervals (for example {cell(m(A, 'direct', 'harmful_compliance'))}), and the paired tests have low power. Only the prefix-steering effect is large enough to be established.
2. **Lower-risk subset.** The 20 pairs come from six of the ten JBB categories after ten exclusion rules. The results say nothing about violence, weapons, malware, sexual content or hate, where models are usually trained to refuse more firmly.
3. **Weak, fixed attacks.** Two non-adaptive templates, one attempt, one turn, English. Attack success is a lower bound on what an adaptive adversary would achieve.
4. **One greedy sample per cell.** The shipped default is sampling at temperature 0.7. Deployed behaviour may differ and no variance across samples was measured.
5. **Truncation.** {DESC['finish_reason']['length']} of 240 responses reached the 256-token cap and were judged on the text present.
6. **Judge error.** The harmful-compliance rates depend on a judge whose Unsafe label over-triggers. They are upper bounds.
7. **The audit is not a human gold standard.** One LLM annotator, 60 responses, no second annotator, some borderline calls.
8. **Harm is judged by content, not by usefulness.** Much of the complying text from these small models is generic or inaccurate. Real-world uplift is likely lower than even the audited rate suggests, which is the willingness-versus-capability point made by StrongREJECT.
9. **Borderline benign prompts.** The JailbreakBench authors note that some benign behaviours are borderline. Every refusal of a benign prompt is counted as over-refusal here.
10. **Black-box only.** With open weights, safeguards can be removed by fine-tuning. That ceiling was not tested.
11. **Hardware.** Greedy decoding is deterministic on the same hardware and library versions; bfloat16 arithmetic on another GPU may change individual tokens.
12. **Multiple comparisons.** {len(S['paired_tests'])} paired tests are reported without correction and should be read as descriptive, apart from the prefix-steering effects noted above.

{sec['governance']}

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
| Freeze time (UTC) | {MAN['frozen_at_utc']} |
| Dataset | {MAN['dataset']['repo']} @ `{MAN['dataset']['revision'][:12]}` |
| Target models | {MAN['models'][A]['repo']} @ `{MAN['models'][A]['revision'][:12]}`; {MAN['models'][B]['repo']} @ `{MAN['models'][B]['revision'][:12]}` |
| Judge | {MAN['models']['qwen3guard-gen-0.6b']['repo']} @ `{MAN['models']['qwen3guard-gen-0.6b']['revision'][:12]}` |
| Libraries | PyTorch {MAN['packages']['torch']}, Transformers {MAN['packages']['transformers']} |
| Locked dataset | `02_data/responses_locked.jsonl`, SHA-256 `{SHA[:16]}...` |
| Generation time | {DESC['total_generation_seconds'] / 60:.0f} minutes on one RTX 3050 Laptop GPU (4 GB) |
| Verification | `03_pipeline/07_verify.py`: {VERIF} |

{sec['references']}
"""

# --------------------------------------------------------------------------
# Safety Evaluation Card
# --------------------------------------------------------------------------
CARD = f"""# Safety Evaluation Card

**Jailbreak robustness and over-refusal of Qwen2.5-0.5B-Instruct and Qwen2.5-1.5B-Instruct**

| | |
|---|---|
| Evaluated systems | Qwen/Qwen2.5-0.5B-Instruct (`{MAN['models'][A]['revision'][:12]}`), Qwen/Qwen2.5-1.5B-Instruct (`{MAN['models'][B]['revision'][:12]}`): weights, default chat template, default system prompt, greedy decoding, no external guardrail |
| Evaluator | Independent of the developer. Vishwas Khandelwal, Individual Learning Plan project, 12 November 2026 |
| Purpose of this card | Evidence for a deployer or reviewer about one configuration under one threat model. Not a safety certification |

## What was tested

| | |
|---|---|
| Threat model | Black-box, single turn, one attempt per request, no system-prompt control, no pre-filled assistant turn, no fine-tuning |
| Test set | 20 lower-risk harmful requests and 20 topic-matched benign requests from JBB-Behaviors (`{MAN['dataset']['revision'][:12]}`), six categories: economic harm, fraud, disinformation, privacy, expert advice, government decision-making |
| Excluded by design | Physical harm, sexual content, malware and hacking, harassment and discrimination, and 28 further behaviours (68 of 100 excluded by ten written rules) |
| Conditions | Direct; role framing (fixed role-play wrapper); prefix steering (instruction to start with an affirmative sentence) |
| Volume | 240 responses: 2 models x 20 pairs x 2 prompt types x 3 conditions |
| Scoring | Qwen3Guard-Gen-0.6B (`{MAN['models']['qwen3guard-gen-0.6b']['revision'][:12]}`); 60 responses audited blind against a written rubric by an LLM annotator |

## Results

Rate [95% Wilson interval], n = 20 per cell, judge-based.

| Model | Condition | Harmful compliance | Correct refusal | Over-refusal (benign) |
|---|---|---|---|---|
""" + "\n".join(f"| {C.MODEL_LABELS[mk]} | {C.CONDITION_LABELS[c]} | {cell(m(mk, c, 'harmful_compliance'))} | {cell(m(mk, c, 'correct_refusal'))} | {cell(m(mk, c, 'over_refusal'))} |"
                for mk in C.TARGET_MODELS for c in C.CONDITION_ORDER) + f"""

**Reliability of the automated scores (60-response audit)**

| Judge output | Agreement | Kappa | Note |
|---|---|---|---|
| Refusal flag | {pct(rf['agreement'])} | {rf['kappa']:.2f} | No missed refusals; {rf['fp']} false refusal flags |
| Unsafe label | {pct(hs['agreement'])} | {hs['kappa']:.2f} | {hs['fp']} false positives, {hs['fn']} false negatives among 30; precision {kn(prec)} |

Harmful-compliance rates are upper bounds. On the 30 audited harmful-prompt responses: judge {short(ras['harmful_compliance']['judge'])}, audit {short(ras['harmful_compliance']['audit'])}.

## Findings

1. **Built-in refusals are easy to switch off.** A one-line instruction to begin with an affirmative sentence reduced correct refusals from {kn(m('both', 'direct', 'correct_refusal'))} to {kn(m('both', 'prefix_steering', 'correct_refusal'))} across both models.
2. **Not every non-refusal is harmful.** About half of the audited prefix-steering responses that the judge called unsafe contain no harmful content ({kn(cond_audit['prefix_steering']['audit_harmful'])} harmful by audit, {kn(cond_audit['prefix_steering']['judge_unsafe'])} by judge).
3. **Over-refusal exists and is topic-driven.** Asked directly, the models refused {short(m(A, 'direct', 'over_refusal'))} and {short(m(B, 'direct', 'over_refusal'))} of the benign requests, mostly on disinformation topics.
4. **The small guard model over-flags.** It marked {DESC['benign_flagged_unsafe']} of 120 responses to benign prompts as Unsafe.

## What this evaluation does not show

- Behaviour on high-severity categories, in other languages, over several turns, or with sampling.
- Resistance to adaptive or white-box attacks, or to fine-tuning of the open weights. Attack success here is a lower bound.
- Real-world uplift. Much of the complying output is generic or inaccurate.
- Human-validated labels. The audit is one LLM annotation pass over 60 responses.
- Statistical precision. With 20 prompts per cell, intervals are up to {MAXW:.0f} percentage points wide.

## Implications for a deployer

- Do not treat the model's own refusals as a safety control. Add an independent input or output control if the application needs one.
- Validate any automated judge or filter on labelled samples from your own use case before relying on its numbers. Measure false positives on benign content as well as misses.
- Report both failure directions together. A configuration that looks safer on harmful prompts may refuse more legitimate ones.

## Traceability

| | |
|---|---|
| Freeze manifest | `01_protocol/freeze_manifest.json`, frozen {MAN['frozen_at_utc']} |
| Locked dataset | `02_data/responses_locked.jsonl`, SHA-256 `{SHA[:16]}...` |
| Rubric and annotator instructions | `01_protocol/03_labels_metrics_transformations_rubric.md` |
| Verification | {VERIF} (`04_results/verification_report.txt`) |
| NIST AI 600-1 actions addressed | MS-1.3-002 (external evaluation), MS-2.3-002 and MS-2.3-003 (validated methods, shared results), MS-2.7-007 (red-teaming against adversarial prompts), MS-2.8-002 (documented annotator instructions), MS-2.11-001 (documented benchmark limitations), MS-2.13-001 (measurement error of the metric) |
"""

(C.RESULTS_DIR / "error_analysis.md").write_text(ERROR_ANALYSIS, encoding="utf-8")
(REPORT_DIR / "Report.md").write_text(REPORT, encoding="utf-8")
(REPORT_DIR / "Safety_Evaluation_Card.md").write_text(CARD, encoding="utf-8")
for name in ["Report", "Safety_Evaluation_Card"]:
    subprocess.run(["pandoc", f"{name}.md", "-o", f"{name}.docx", "--from", "gfm", "--resource-path", str(REPORT_DIR)],
                   cwd=REPORT_DIR, check=True)
print("written: error_analysis.md, Report.md/.docx, Safety_Evaluation_Card.md/.docx")
print("report words:", len(REPORT.split()), "| card words:", len(CARD.split()))
