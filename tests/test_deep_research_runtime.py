import unittest


class DeepResearchRuntimeTests(unittest.TestCase):
    def test_research_config_exposes_deep_research_controls(self):
        from researchdraft.config.research_config import ResearchConfig

        config = ResearchConfig.default()

        self.assertEqual(config.max_research_loops, 2)
        self.assertGreaterEqual(config.max_sources, 5)
        self.assertEqual(config.report_style, "paper")
        self.assertEqual(config.to_dict()["workflow"], "scope-plan-search-fetch-evaluate-deliver")

    def test_search_fetch_provider_returns_search_results_and_fetched_documents(self):
        from researchdraft.search.deep_search import SearchFetchProvider

        provider = SearchFetchProvider()

        results = provider.search("traceable research agent", max_results=2)
        fetched = provider.fetch(results[0])

        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].result_id.startswith("R"))
        self.assertIn("traceable research agent", results[0].title)
        self.assertEqual(fetched.result_id, results[0].result_id)
        self.assertIn(results[0].title, fetched.content)

    def test_evaluator_scores_claims_against_evidence_cards(self):
        from researchdraft.evaluation.deep_research_eval import evaluate_claims

        result = evaluate_claims(
            claims=[
                {"id": "C1", "text": "Trace is recorded", "evidence_id": "E1"},
                {"id": "C2", "text": "Accuracy improves 95%", "evidence_id": ""},
            ],
            evidence_cards=[{"id": "E1", "confidence": 0.9, "status": "confirmed"}],
        )

        self.assertEqual(result.metrics["claim_count"], 2)
        self.assertEqual(result.metrics["supported_claim_count"], 1)
        self.assertGreater(result.metrics["unsupported_claim_rate"], 0)
        self.assertIn("C2", result.report_markdown)

    def test_fastapi_exposes_deep_research_runtime_endpoints(self):
        import importlib

        app_mod = importlib.import_module("app.main")
        routes = {route.path for route in app_mod.app.routes}

        self.assertIn("/demo/config", routes)
        self.assertIn("/demo/search-fetch", routes)
        self.assertIn("/demo/evaluation", routes)


if __name__ == "__main__":
    unittest.main()
