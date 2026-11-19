"""Tests that the published data still follows the frozen protocol.

These checks are independent of 07_verify.py: they test the prompt-selection
rules and the experimental design straight from the CSV/JSONL files.
"""
import csv
import json
import unittest
from collections import Counter

from conftest import ROOT

import config as C

DATA = ROOT / "02_data"


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


class PromptSelectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pairs = read_csv(DATA / "selected_prompts.csv")
        cls.pilot = read_csv(DATA / "pilot" / "pilot_prompts.csv")

    def test_twenty_pairs_with_unique_ids(self):
        self.assertEqual(len(self.pairs), C.N_PAIRS)
        self.assertEqual(len({p["pair_id"] for p in self.pairs}), C.N_PAIRS)
        self.assertEqual(len({p["jbb_index"] for p in self.pairs}), C.N_PAIRS)

    def test_no_excluded_category_or_behaviour(self):
        for p in self.pairs + self.pilot:
            self.assertNotIn(p["category"], C.EXCLUDED_CATEGORIES, p["pair_id"])
            self.assertNotIn(int(p["jbb_index"]), C.EXCLUDED_BEHAVIOURS, p["pair_id"])

    def test_stratified_quota(self):
        counts = Counter(p["category"] for p in self.pairs)
        self.assertEqual(set(counts), set(C.RETAINED_CATEGORY_ORDER))
        self.assertEqual(sorted(counts.values()), [3, 3, 3, 3, 4, 4])

    def test_pilot_pairs_are_disjoint_from_the_final_set(self):
        self.assertEqual(len(self.pilot), C.N_PILOT_PAIRS)
        final = {p["jbb_index"] for p in self.pairs}
        self.assertFalse(final & {p["jbb_index"] for p in self.pilot})

    def test_pairs_come_from_the_source_files(self):
        harmful = {r["Index"]: r for r in read_csv(DATA / "source" / "harmful-behaviors.csv")}
        benign = {r["Index"]: r for r in read_csv(DATA / "source" / "benign-behaviors.csv")}
        for p in self.pairs:
            self.assertEqual(harmful[p["jbb_index"]]["Goal"], p["harmful_goal"])
            self.assertEqual(benign[p["jbb_index"]]["Goal"], p["benign_goal"])
            self.assertEqual(harmful[p["jbb_index"]]["Category"], p["category"])


class DesignTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        text = (DATA / "responses_locked.jsonl").read_text(encoding="utf-8")
        cls.recs = [json.loads(line) for line in text.splitlines() if line.strip()]

    def test_full_factorial_design(self):
        cells = Counter((r["model_key"], r["condition"], r["prompt_type"]) for r in self.recs)
        self.assertEqual(len(self.recs), 240)
        self.assertEqual(len(cells), 2 * 3 * 2)
        self.assertEqual(set(cells.values()), {C.N_PAIRS})

    def test_prompts_are_the_frozen_templates(self):
        for r in self.recs:
            expected = C.CONDITIONS[r["condition"]].format(goal=r["goal"], target=r["target"])
            self.assertEqual(r["user_prompt"], expected, r["response_id"])

    def test_single_turn_with_default_system_prompt(self):
        for r in self.recs:
            rendered = r["rendered_prompt"]
            self.assertEqual(rendered.count("<|im_start|>user"), 1, r["response_id"])
            self.assertIn("<|im_start|>system", rendered)
            self.assertTrue(rendered.endswith("<|im_start|>assistant\n"), r["response_id"])

    def test_greedy_decoding_at_pinned_revisions(self):
        for r in self.recs:
            self.assertEqual(r["gen_settings"], C.GEN)
            self.assertFalse(r["gen_settings"]["do_sample"])
            self.assertEqual(r["model_revision"], C.TARGET_MODELS[r["model_key"]]["revision"])


class BlindAuditTest(unittest.TestCase):
    def test_blind_sheet_reveals_no_condition_model_or_judge_label(self):
        with open(DATA / "audit" / "audit_sample_blind.csv", encoding="utf-8-sig", newline="") as fh:
            header = next(csv.reader(fh))
        hidden = {"model_key", "condition", "response_id", "judge_safety", "judge_refusal", "judge_outcome", "user_prompt"}
        self.assertFalse(hidden & set(header), header)

    def test_labels_saved_before_judge_run(self):
        log = json.loads((DATA / "audit" / "audit_log.json").read_text(encoding="utf-8"))
        self.assertLess(log["audit_labels_saved_utc"], log["judge_run_started_utc"])


if __name__ == "__main__":
    unittest.main()
