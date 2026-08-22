import unittest

from benchmark.score_benchmark import build_clean_consensus, finding_shape, gold_shape, score_trial


def finding(file: str, line: int, category: str, title: str = "", evidence: str = "") -> dict:
    return finding_shape(
        {"file": file, "line": line, "category": category, "title": title, "evidence": evidence}
    )


def gold(identifier: str, file: str, line: int, category: str, in_scope: bool = True) -> dict:
    return gold_shape(
        {
            "id": identifier,
            "file": file,
            "final_line": line,
            "primary_category": category,
            "accepted_categories": [category],
            "in_scope": in_scope,
        }
    )


class CleanConsensusTests(unittest.TestCase):
    def test_requires_majority_and_ignores_one_off_clean_noise(self):
        stable = finding("core/a.js", 10, "secret")
        one_off = finding("core/noise.js", 20, "auth")
        consensus = build_clean_consensus([[stable, one_off], [stable], []])
        self.assertEqual(1, len(consensus))
        self.assertEqual("core/a.js", consensus[0]["file"])
        self.assertEqual(2, consensus[0]["clean_trial_frequency"])


class TrialScoringTests(unittest.TestCase):
    def test_tp_duplicate_fp_baseline_and_unmatched_fp(self):
        gold_items = [
            gold("S1", "core/a.js", 10, "secret"),
            gold("S2", "core/b.js", 30, "auth"),
        ]
        baseline = [finding("core/original.js", 50, "config")]
        findings = [
            finding("core/a.js", 14, "secret", "first TP"),       # within +5
            finding("core/a.js", 11, "secret", "duplicate"),      # duplicate => FP
            finding("core/original.js", 52, "config", "baseline"),
            finding("core/random.js", 70, "crypto", "unmatched"),
        ]
        result = score_trial(findings, gold_items, baseline)

        self.assertEqual(1, result["counts"]["tp_all"])
        self.assertEqual(2, result["counts"]["fp"])
        self.assertEqual(1, result["counts"]["baseline_excluded"])
        self.assertAlmostEqual(0.5, result["metrics"]["in_scope_recall"])
        self.assertAlmostEqual(1 / 3, result["metrics"]["in_scope_precision"])
        self.assertAlmostEqual(2 / 3, result["metrics"]["in_scope_fdr"])
        self.assertAlmostEqual(0.4, result["metrics"]["f1_in_scope"])
        self.assertEqual({"tp": 1, "fn": 0, "fp": 1, "recall": 1.0, "precision": 0.5}, result["per_category"]["secret"])
        self.assertEqual(0.0, result["per_category"]["auth"]["recall"])

    def test_wrong_category_is_fp_and_gold_remains_missed(self):
        result = score_trial(
            [finding("core/a.js", 10, "auth")],
            [gold("S1", "core/a.js", 10, "secret")],
            [],
        )
        self.assertEqual(0, result["counts"]["tp_all"])
        self.assertEqual(1, result["counts"]["fp"])
        self.assertEqual(["S1"], result["missed_gold_ids"])

    def test_out_of_scope_gold_affects_coverage_not_in_scope_recall_denominator(self):
        gold_items = [
            gold("IN", "core/in.js", 10, "auth", True),
            gold("OUT", "core/out.js", 20, "input", False),
        ]
        result = score_trial([finding("core/out.js", 20, "input")], gold_items, [])
        self.assertEqual(0.0, result["metrics"]["in_scope_recall"])
        self.assertEqual(0.5, result["metrics"]["end_to_end_coverage"])
        self.assertEqual(1, result["counts"]["tp_out_of_checklist"])
        self.assertEqual(0.0, result["metrics"]["in_scope_precision"])
        self.assertEqual(1.0, result["metrics"]["all_seeded_precision"])


class BaselineBeforeGoldTests(unittest.TestCase):
    """Amendment 22/08/2026 - the two halves of the differential ordering fix."""

    def test_stable_clean_finding_is_excluded_even_when_it_matches_gold(self):
        """scoring_rules.md:62 - TP is "spiked ONLY". Gold match never rescues it."""
        gold_items = [gold("S1", "core/a.js", 10, "secret")]
        baseline = [finding("core/a.js", 10, "secret", evidence="const KEY = 'x'")]
        result = score_trial(
            [finding("core/a.js", 10, "secret", evidence="const KEY = 'x'")],
            gold_items,
            baseline,
        )
        self.assertEqual(0, result["counts"]["tp_all"])
        self.assertEqual(1, result["counts"]["baseline_excluded"])
        self.assertEqual(["S1"], result["missed_gold_ids"])

    def test_insertion_shift_collision_still_scores_tp(self):
        """Real SEED-DEP-01 case: the seeded line INHERITS the clean line number.

        Clean flags multer at package.json:23; the seeded lodash lands on 23 and
        pushes multer to 24. Same file, same `dependency` category, line delta 0
        - location alone would suppress a genuine detection. Evidence separates.
        """
        gold_items = [gold("SEED-DEP-01", "package.json", 23, "dependency")]
        baseline = [finding("package.json", 23, "dependency", evidence='"multer": "^2.1.1"')]
        result = score_trial(
            [finding("package.json", 23, "dependency", evidence='"lodash": "4.17.15"')],
            gold_items,
            baseline,
        )
        self.assertEqual(1, result["counts"]["tp_all"])
        self.assertEqual(0, result["counts"]["baseline_excluded"])
        self.assertEqual(["SEED-DEP-01"], result["matched_gold_ids"])

    def test_missing_evidence_falls_back_to_suppression_not_credit(self):
        gold_items = [gold("S1", "core/a.js", 10, "secret")]
        baseline = [finding("core/a.js", 10, "secret", evidence="const KEY = 'x'")]
        result = score_trial([finding("core/a.js", 10, "secret")], gold_items, baseline)
        self.assertEqual(0, result["counts"]["tp_all"])
        self.assertEqual(1, result["counts"]["baseline_excluded"])


class ConsensusClusterTests(unittest.TestCase):
    """Consensus and exclusion must use ONE identity relation, or a cluster of
    distinct nearby findings elects a single representative and then rejects its
    own members. Real case: package.json dependency findings on lines 16/18/23
    collapsed onto the axios entry, after which the line-16 entries scored FP."""

    def _clean_trial(self):
        return [
            finding("package.json", 16, "dependency", evidence='"dependencies"'),
            finding("package.json", 18, "dependency", evidence='"axios": "^1.6.0"'),
        ]

    def test_distinct_nearby_findings_both_reach_consensus(self):
        consensus = build_clean_consensus([self._clean_trial() for _ in range(3)])
        self.assertEqual(2, len(consensus))
        self.assertEqual({16, 18}, {item["line"] for item in consensus})

    def test_every_cluster_member_is_excluded_not_just_the_representative(self):
        consensus = build_clean_consensus([self._clean_trial() for _ in range(3)])
        result = score_trial(self._clean_trial(), [], consensus)
        self.assertEqual(2, result["counts"]["baseline_excluded"])
        self.assertEqual(0, result["counts"]["fp"])


if __name__ == "__main__":
    unittest.main()
