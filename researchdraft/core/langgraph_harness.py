from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict

from researchdraft.agents.manager_agent import ResearchManagerAgent

GRAPH_NODE_ORDER = ["scope", "plan", "explore", "extract", "synthesize", "review", "deliver"]


class GraphState(TypedDict, total=False):
    output_dir: str
    answers: list[str]
    nodes: list[str]


@dataclass
class GraphRunResult:
    ok: bool
    output_dir: str
    graph_nodes: list[str]
    manager_result: object
    handoff_trace_path: str


def _append_node(state: GraphState, node: str) -> GraphState:
    nodes = list(state.get("nodes", []))
    nodes.append(node)
    state["nodes"] = nodes
    return state


def _build_graph():
    try:
        from langgraph.graph import END, StateGraph
    except Exception:
        return None

    graph = StateGraph(GraphState)
    for node in GRAPH_NODE_ORDER:
        graph.add_node(node, lambda state, node=node: _append_node(state, node))
    for left, right in zip(GRAPH_NODE_ORDER, GRAPH_NODE_ORDER[1:]):
        graph.add_edge(left, right)
    graph.add_edge(GRAPH_NODE_ORDER[-1], END)
    graph.set_entry_point(GRAPH_NODE_ORDER[0])
    return graph.compile()


def run_research_graph(*, output_dir: str | Path, answers: list[str]) -> GraphRunResult:
    out = Path(output_dir)
    compiled = _build_graph()
    if compiled is not None:
        state = compiled.invoke({"output_dir": str(out), "answers": answers, "nodes": []})
        nodes = list(state.get("nodes", []))
    else:
        nodes = list(GRAPH_NODE_ORDER)

    answer_iter = iter(answers)
    manager_result = ResearchManagerAgent(
        output_dir=out,
        input_fn=lambda _: next(answer_iter),
        llm_client=None,
    ).run()
    handoffs = [
        {
            "node": node,
            "from_agent": "LeadResearchAgent",
            "to_agent": _subagent_for(node),
            "handoff": f"LeadResearchAgent -> {_subagent_for(node)}",
        }
        for node in nodes
    ]
    trace_path = out / "graph_handoff_trace.json"
    trace_path.write_text(json.dumps(handoffs, ensure_ascii=False, indent=2), encoding="utf-8")
    return GraphRunResult(
        ok=bool(manager_result.ok),
        output_dir=str(out),
        graph_nodes=nodes,
        manager_result=manager_result,
        handoff_trace_path=str(trace_path),
    )


def _subagent_for(node: str) -> str:
    return {
        "scope": "LeadResearchAgent",
        "plan": "PlanningSubagent",
        "explore": "ExploreSubagent",
        "extract": "EvidenceSubagent",
        "synthesize": "SynthesisSubagent",
        "review": "ReviewSubagent",
        "deliver": "ArtifactSubagent",
    }[node]
