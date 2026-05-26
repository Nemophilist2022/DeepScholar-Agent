import json
import tempfile
import unittest
from pathlib import Path


class LangGraphHarnessTests(unittest.TestCase):
    def test_graph_harness_runs_expected_nodes_and_writes_handoff_trace(self):
        from researchdraft.core.langgraph_harness import GRAPH_NODE_ORDER, run_research_graph

        answers = [
            "Graph Harness Demo",
            "Need a graph-backed research delivery demo.",
            "How can graph handoffs stay auditable?",
            "scope; plan; review; deliver",
            "demo corpus",
            "citation coverage",
            "graph trace",
            "short_paper",
            "docx",
            "",
            "graph research agent",
            "skip",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_graph(output_dir=tmp, answers=answers)
            out = Path(tmp)
            self.assertTrue(result.ok)
            self.assertEqual(result.graph_nodes, GRAPH_NODE_ORDER)
            trace_path = out / "graph_handoff_trace.json"
            self.assertTrue(trace_path.exists())
            handoffs = json.loads(trace_path.read_text(encoding="utf-8"))
            self.assertEqual([item["node"] for item in handoffs], GRAPH_NODE_ORDER)
            self.assertIn("LeadResearchAgent", {item["from_agent"] for item in handoffs})


if __name__ == "__main__":
    unittest.main()
