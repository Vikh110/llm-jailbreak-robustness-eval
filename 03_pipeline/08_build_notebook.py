"""Phase 8 - build the clean analysis notebook (then executed with nbconvert).

The notebook re-uses the functions of 05_analysis.py on the locked data, so it
cannot drift from the reported numbers. It prints labels and statistics only,
never the raw text of responses to harmful prompts.
"""
import nbformat as nbf

import config as C

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [
    md("# Jailbreak robustness and over-refusal in small instruction-tuned models\n\n"
       "Clean analysis notebook for the Individual Learning Plan project. It reads only locked inputs:\n\n"
       "- `02_data/responses_locked.jsonl` - 240 responses (2 models x 20 prompt pairs x 2 prompt types x 3 conditions)\n"
       "- `02_data/judge_scores.csv` - Qwen3Guard-Gen-0.6B labels for all 240 responses\n"
       "- `02_data/audit/audit_labels.csv` - blind rubric audit of 60 responses\n\n"
       "Raw responses to harmful prompts are never printed here; only labels and statistics."),
    code("import sys, json, importlib\nfrom pathlib import Path\nimport pandas as pd\nfrom IPython.display import Image, display\n"
         "sys.path.insert(0, str(Path.cwd()))\nimport config as C\nA = importlib.import_module('05_analysis')\n"
         "pd.set_option('display.width', 200)\ndf = A.load()\nprint(df.shape)"),
    md("## 1. Design check\n\nEvery cell of the design must contain exactly 20 responses."),
    code("df.groupby(['model_key', 'prompt_type', 'condition']).size().unstack('condition')[C.CONDITION_ORDER]"),
    code("print('finish reasons:', df.finish_reason.value_counts().to_dict())\nprint('mean new tokens: %.1f' % df.n_new_tokens.mean())\n"
         "pd.crosstab([df.prompt_type, df.judge_safety], df.judge_refusal)"),
    md("## 2. Headline metrics with 95% Wilson confidence intervals\n\n"
       "Rates per model and condition (n = 20 prompts per cell). `k` is the number of responses with that outcome."),
    code("tab = A.metrics_tables(df)\n"
         "tab['pct [95% CI]'] = tab.apply(lambda r: f\"{r.rate*100:.0f}% [{r.ci_low*100:.0f}, {r.ci_high*100:.0f}]  ({r.k}/{r.n})\", axis=1)\n"
         "cell = tab[(tab.model != 'both') & (tab.condition != 'all')]\n"
         "cell.pivot(index=['model', 'condition'], columns='metric', values='pct [95% CI]')"
         ".loc[[(m, c) for m in C.TARGET_MODELS for c in C.CONDITION_ORDER], ['harmful_compliance', 'correct_refusal', 'other_non_refusal', 'benign_compliance', 'over_refusal']]"),
    code("pooled = tab[(tab.model == 'both') | (tab.condition == 'all')]\n"
         "pooled.pivot(index=['model', 'condition'], columns='metric', values='pct [95% CI]')[['harmful_compliance', 'correct_refusal', 'benign_compliance', 'over_refusal', 'harmful_compliance_lenient']]"),
    code("for f in ['fig1_harmful_compliance.png', 'fig2_over_refusal.png', 'fig3_outcome_composition.png']:\n    display(Image(filename=str(C.FIG_DIR / f), width=720))"),
    md("## 3. Paired comparisons (exact McNemar, same 20 prompts)\n\n"
       "`first_only` / `second_only` count prompts where only the first / only the second arm shows the outcome. "
       "With 20 prompts per arm these tests have low power."),
    code("A.paired_tests(df)"),
    md("## 4. Harmful compliance by JBB category (pooled over models and conditions)"),
    code("pd.read_csv(C.RESULTS_DIR / 'harmful_compliance_by_category.csv').assign(pct=lambda d: (d.rate*100).round(1))[['category', 'k', 'n', 'pct', 'ci_low', 'ci_high']]"),
    md("## 5. Reliability of the automated judge against the 60-response audit\n\n"
       "The audit is a blind second annotation by an LLM annotator (Claude) applying the frozen rubric. "
       "It was saved before the judge scored the main run."),
    code("a, rel = A.judge_reliability(df)\n"
         "for k in ['refusal', 'refusal_partial_as_refusal', 'harmful_compliance_strict', 'harmful_compliance_lenient']:\n"
         "    r = rel[k]\n    print(f\"{k:30} n={r['n']}  agreement={r['agreement']:.3f} [{r['agreement_ci'][0]:.3f}, {r['agreement_ci'][1]:.3f}]  kappa={r['kappa']:.3f}  TP={r['tp']} FP={r['fp']} FN={r['fn']} TN={r['tn']}\")\n"
         "r = rel['outcome_label']\nprint(f\"{'outcome_label':30} n={r['n']}  agreement={r['agreement']:.3f} [{r['agreement_ci'][0]:.3f}, {r['agreement_ci'][1]:.3f}]  kappa={r['kappa']:.3f}\")"),
    code("pd.crosstab(a.audit_outcome, a.judge_outcome, margins=True)"),
    code("display(Image(filename=str(C.FIG_DIR / 'fig4_judge_vs_audit.png'), width=720))"),
    md("### Disagreements (labels and audit notes only)"),
    code("dis = a[~a.agree_outcome | ~a.agree_refusal]\n"
         "dis[['audit_id', 'response_id', 'category', 'judge_safety', 'judge_refusal', 'judge_outcome', 'refusal', 'harmful_content', 'audit_outcome', 'notes']]"),
    md("### Rates on the audited sample: judge vs audit"),
    code("pd.DataFrame([{'metric': m, 'audit k/n': f\"{v['audit']['k']}/{v['audit']['n']}\", 'audit rate': round(v['audit']['rate'], 3), "
         "'judge k/n': f\"{v['judge']['k']}/{v['judge']['n']}\", 'judge rate': round(v['judge']['rate'], 3)} for m, v in rel['rates_on_audit_sample'].items()])"),
]
nb = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}})
nbf.write(nb, C.PIPELINE_DIR / "analysis_notebook.ipynb")
print("notebook written:", C.PIPELINE_DIR / "analysis_notebook.ipynb")
