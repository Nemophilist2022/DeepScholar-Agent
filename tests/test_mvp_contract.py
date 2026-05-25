import importlib
import json
import tempfile
import unittest
from pathlib import Path


class DeepScholarMVPContractTests(unittest.TestCase):
    def test_researchdraft_manager_generates_required_artifacts(self):
        from researchdraft.agents.manager_agent import ResearchManagerAgent

        answers = iter([
            "DeepScholar Agent Harness",
            "HR needs a traceable research-and-docx demo.",
            "How to deliver grounded research drafts with review traces?",
            "planning; evidence review; docx delivery",
            "demo materials",
            "citation coverage; delivery success",
            "trace evaluation; human review gate",
            "short_paper",
            "docx",
            "",
            "traceable research agent",
            "skip",
        ])
        with tempfile.TemporaryDirectory() as tmp:
            result = ResearchManagerAgent(output_dir=tmp, input_fn=lambda _: next(answers), llm_client=None).run()
            out = Path(tmp)
            for name in ["draft_context.json", "draft.md", "paper.docx", "quality_report.md", "trace.json", "candidate_literature.json", "source_review_report.json", "search_cache.json"]:
                self.assertTrue((out / name).exists(), name)
            trace = json.loads((out / "trace.json").read_text(encoding="utf-8"))
            self.assertTrue(any(item["agent"] == "VerifierAgent" for item in trace))
            self.assertTrue(result.ok)

    def test_fastapi_app_exposes_demo_endpoints(self):
        app_mod = importlib.import_module("app.main")
        self.assertTrue(hasattr(app_mod, "app"))
        routes = {route.path for route in app_mod.app.routes}
        self.assertIn("/health", routes)
        self.assertIn("/demo/run", routes)
        self.assertIn("/demo/trace", routes)
        self.assertIn("/demo/report", routes)

    def test_workspace_contract_files_exist(self):
        root = Path(__file__).resolve().parents[1]
        for rel in ["workspace/protocol.md", "workspace/task_plan.md", "workspace/claim_map.md", "workspace/evidence/evidence_card_001.md", "docs/architecture.md", "docs/demo_guide.md", "README.md"]:
            self.assertTrue((root / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
