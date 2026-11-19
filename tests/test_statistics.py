"""Unit tests for the statistics used in the evaluation.

07_verify.py re-implements every statistic from first principles (closed-form
Wilson interval, exact McNemar via math.comb, Cohen's kappa by hand) so that it
can check 05_analysis.py, which uses statsmodels and scipy. These tests pin the
hand-written versions to known values and to the library versions.
"""
import math
import unittest

from conftest import load_script

V = load_script("07_verify.py")


class WilsonIntervalTest(unittest.TestCase):
    def test_values_reported_in_the_paper(self):
        # 5/20 is reported as 25% [11, 47]; 18/20 as 90% [70, 97]; 0/20 as 0% [0, 16]
        for k, lo, hi in [(5, 11, 47), (18, 70, 97), (0, 0, 16), (20, 84, 100)]:
            got_lo, got_hi = V.wilson(k, 20)
            self.assertEqual(round(got_lo * 100), lo, (k, got_lo))
            self.assertEqual(round(got_hi * 100), hi, (k, got_hi))

    def test_interval_contains_point_estimate_and_stays_in_unit_range(self):
        for n in (1, 7, 20, 40, 120):
            for k in range(n + 1):
                lo, hi = V.wilson(k, n)
                self.assertLessEqual(-1e-12, lo)
                self.assertLessEqual(lo, k / n + 1e-12)
                self.assertLessEqual(k / n - 1e-12, hi)
                self.assertLessEqual(hi, 1 + 1e-12)

    def test_matches_statsmodels(self):
        try:
            from statsmodels.stats.proportion import proportion_confint
        except ImportError:  # pragma: no cover - analysis extras not installed
            self.skipTest("statsmodels not installed")
        for n in (20, 30, 40, 60, 120):
            for k in range(n + 1):
                lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
                got = V.wilson(k, n)
                self.assertAlmostEqual(got[0], lo, places=9)
                self.assertAlmostEqual(got[1], hi, places=9)


class McNemarTest(unittest.TestCase):
    def test_known_values(self):
        self.assertEqual(V.mcnemar_p(0, 0), 1.0)
        self.assertAlmostEqual(V.mcnemar_p(0, 6), 2 / 2 ** 6)      # 1.5B vs 0.5B, direct: p = 0.031
        self.assertAlmostEqual(V.mcnemar_p(0, 13), 2 / 2 ** 13)    # prefix steering, 0.5B: p < 0.001
        self.assertAlmostEqual(V.mcnemar_p(0, 17), 2 / 2 ** 17)    # prefix steering, 1.5B
        self.assertEqual(V.mcnemar_p(3, 3), 1.0)

    def test_symmetric(self):
        for b in range(8):
            for c in range(8):
                self.assertAlmostEqual(V.mcnemar_p(b, c), V.mcnemar_p(c, b))

    def test_matches_scipy_binomial_test(self):
        try:
            from scipy.stats import binomtest
        except ImportError:  # pragma: no cover
            self.skipTest("scipy not installed")
        for b in range(15):
            for c in range(15):
                if b + c == 0:
                    continue
                expected = binomtest(min(b, c), b + c, 0.5).pvalue
                self.assertAlmostEqual(V.mcnemar_p(b, c), expected, places=12)

    def test_bonferroni_threshold_used_in_the_report(self):
        # 21 paired tests: both prefix-steering effects stay below 0.05 / 21
        self.assertLess(V.mcnemar_p(0, 13), 0.05 / 21)
        self.assertLess(V.mcnemar_p(0, 17), 0.05 / 21)


class KappaTest(unittest.TestCase):
    def test_perfect_agreement(self):
        a = [True, False, True, True, False]
        self.assertEqual(V.kappa(a, list(a)), 1.0)

    def test_textbook_example(self):
        # 2x2 table: both yes 20, A yes/B no 5, A no/B yes 10, both no 15 -> kappa = 0.4
        a = [1] * 20 + [1] * 5 + [0] * 10 + [0] * 15
        b = [1] * 20 + [0] * 5 + [1] * 10 + [0] * 15
        self.assertTrue(math.isclose(V.kappa(a, b), 0.4, rel_tol=1e-12))

    def test_agrees_with_analysis_implementation(self):
        try:
            A = load_script("05_analysis.py")
        except ImportError:  # pragma: no cover
            self.skipTest("analysis dependencies not installed")
        a = ["x", "y", "y", "z", "x", "x", "z", "y"]
        b = ["x", "y", "z", "z", "x", "y", "z", "y"]
        self.assertAlmostEqual(V.kappa(a, b), A.kappa(a, b), places=12)


if __name__ == "__main__":
    unittest.main()
