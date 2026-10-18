import unittest

from tools.evidence_intelligence import EvidenceIntelligence


class TestEvidenceSummary(unittest.TestCase):
    def test_empty_evidence(self):
        summary = EvidenceIntelligence.build_summary([])

        self.assertEqual(summary["total_claims"], 0)
        self.assertEqual(summary["supported_claims"], 0)
        self.assertEqual(summary["evidence_coverage_rate"], 0.0)

    def test_evidence_coverage_calculation(self):
        evidence_map = [
            {"evidence_strength": "Strong"},
            {"evidence_strength": "Moderate"},
            {"evidence_strength": "Weak"},
            {"evidence_strength": "Insufficient"},
            {"evidence_strength": "No Evidence"},
        ]

        summary = EvidenceIntelligence.build_summary(evidence_map)

        self.assertEqual(summary["total_claims"], 5)
        self.assertEqual(summary["supported_claims"], 2)
        self.assertEqual(summary["strong"], 1)
        self.assertEqual(summary["moderate"], 1)
        self.assertEqual(summary["weak"], 1)
        self.assertEqual(summary["unsupported_claims"], 2)
        self.assertEqual(summary["evidence_coverage_rate"], 40.0)
        self.assertEqual(summary["support_rate"], 40.0)

    def test_coverage_does_not_claim_independent_verification(self):
        summary = EvidenceIntelligence.build_summary(
            [{"evidence_strength": "Strong"}]
        )

        self.assertIn(
            "does not establish",
            summary["metric_note"],
        )

    def test_all_weak_evidence_has_zero_coverage(self):
        summary = EvidenceIntelligence.build_summary(
            [
                {"evidence_strength": "Weak"},
                {"evidence_strength": "Weak"},
            ]
        )

        self.assertEqual(summary["evidence_coverage_rate"], 0.0)
        self.assertEqual(summary["weak_claims"], 2)


if __name__ == "__main__":
    unittest.main()
