"""End-to-end checks on the published results.

1. ``07_verify.py --skip-weights`` passes every check (the full run with model
   weights is the separate *full reproduction* workflow).
2. Re-running ``05_analysis.py`` from the locked data reproduces every table in
   ``04_results/`` and ``summary.json``. The analysis runs in a temporary copy
   of the repository, so the committed files are never touched.
"""
import json
import math
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from conftest import ROOT

RESULT_TABLES = [
    "metrics.csv",
    "paired_tests.csv",
    "harmful_compliance_by_category.csv",
    "over_refusal_by_category.csv",
    "per_prompt_pair.csv",
    "judge_vs_audit_items.csv",
]


def same(a, b, path="$"):
    """Recursive equality with a relative tolerance for floats; returns a list of differences."""
    if isinstance(a, dict) and isinstance(b, dict):
        diffs = [f"{path}: keys {sorted(set(a) ^ set(b))}"] if set(a) != set(b) else []
        return diffs + [d for k in set(a) & set(b) for d in same(a[k], b[k], f"{path}.{k}")]
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: length {len(a)} != {len(b)}"]
        return [d for i, (x, y) in enumerate(zip(a, b)) for d in same(x, y, f"{path}[{i}]")]
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        if math.isnan(a) and math.isnan(b):
            return []
        return [] if math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12) else [f"{path}: {a} != {b}"]
    return [] if a == b else [f"{path}: {a!r} != {b!r}"]


class VerificationTest(unittest.TestCase):
    def test_independent_verification_passes(self):
        r = subprocess.run([sys.executable, str(ROOT / "03_pipeline" / "07_verify.py"), "--skip-weights"],
                           capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("26/26 checks passed", r.stdout)
        self.assertNotIn("FAIL", r.stdout)


class ReproductionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import pandas  # noqa: F401
            import matplotlib  # noqa: F401
        except ImportError:  # pragma: no cover
            raise unittest.SkipTest("analysis dependencies not installed (pip install -r requirements-analysis.txt)")
        cls.tmp = Path(tempfile.mkdtemp(prefix="repro-"))
        for d in ("01_protocol", "02_data", "03_pipeline"):
            shutil.copytree(ROOT / d, cls.tmp / d, ignore=shutil.ignore_patterns("__pycache__"))
        (cls.tmp / "04_results" / "figures").mkdir(parents=True)
        cls.analysis = subprocess.run([sys.executable, "05_analysis.py"], capture_output=True, text=True,
                                 cwd=cls.tmp / "03_pipeline")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(getattr(cls, "tmp", ""), ignore_errors=True)

    def test_analysis_runs(self):
        self.assertEqual(self.analysis.returncode, 0, self.analysis.stderr[-3000:])

    def test_summary_json_is_reproduced(self):
        committed = json.loads((ROOT / "04_results" / "summary.json").read_text(encoding="utf-8"))
        rerun = json.loads((self.tmp / "04_results" / "summary.json").read_text(encoding="utf-8"))
        diffs = same(committed, rerun)
        self.assertEqual(diffs, [], "\n".join(diffs[:20]))

    def test_result_tables_are_reproduced(self):
        import pandas as pd
        for name in RESULT_TABLES:
            with self.subTest(table=name):
                committed = pd.read_csv(ROOT / "04_results" / name)
                rerun = pd.read_csv(self.tmp / "04_results" / name)
                pd.testing.assert_frame_equal(committed, rerun, check_exact=False, rtol=1e-9)

    def test_all_four_figures_are_drawn(self):
        figs = sorted(p.name for p in (self.tmp / "04_results" / "figures").glob("*.png"))
        self.assertEqual(figs, ["fig1_harmful_compliance.png", "fig2_over_refusal.png",
                                "fig3_outcome_composition.png", "fig4_judge_vs_audit.png"])


if __name__ == "__main__":
    unittest.main()
