import tempfile
import unittest
from pathlib import Path


class ResearchWorkspaceTests(unittest.TestCase):
    def test_workspace_manager_writes_evidence_claim_map_manifest_and_diff(self):
        from researchdraft.workspace.manager import WorkspaceManager

        candidates = [
            {
                "candidate_id": "C001",
                "title": "Traceable Research Agent",
                "source_url": "https://example.org/paper",
                "snippet": "Trace and evidence review for research agents.",
                "confidence": 0.42,
                "status": "pending_review",
                "risk_flags": ["unconfirmed_source"],
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            ws = WorkspaceManager(Path(tmp) / "workspace")
            result = ws.materialize(
                context_title="Traceable Research Agent",
                candidates=candidates,
                missing_items=["[待补充：引用来源]"],
                confirmation_items=["[待确认：参考文献真实性]"],
                artifact_paths={"draft": "draft.md", "docx": "paper.docx", "report": "quality_report.md"},
            )
            for path in [result.protocol_path, result.task_plan_path, result.claim_map_path, result.manifest_path, result.diff_summary_path]:
                self.assertTrue(Path(path).exists(), path)
                self.assertGreater(Path(path).stat().st_size, 0, path)
            evidence = list((Path(tmp) / "workspace" / "evidence").glob("*.md"))
            self.assertEqual(len(evidence), 1)
            claim_map = Path(result.claim_map_path).read_text(encoding="utf-8")
            self.assertIn("Traceable Research Agent", claim_map)
            self.assertIn("requires_followup", claim_map)
            task_plan = Path(result.task_plan_path).read_text(encoding="utf-8")
            self.assertIn("补检任务", task_plan)


if __name__ == "__main__":
    unittest.main()
