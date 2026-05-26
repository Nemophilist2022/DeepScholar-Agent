import unittest


class BadCaseReplayTests(unittest.TestCase):
    def test_bad_case_replay_reports_grounding_metrics(self):
        from researchdraft.replay.bad_case_replay import run_bad_case_replay

        result = run_bad_case_replay()
        self.assertFalse(result["passed"])
        self.assertGreater(result["metrics"]["unsupported_claim_rate"], 0)
        self.assertIn("unsupported_claim", result["issues"][0])
        self.assertIn("补检", result["recommendation"])


if __name__ == "__main__":
    unittest.main()
