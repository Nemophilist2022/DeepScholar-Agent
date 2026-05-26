# Architecture

DeepScholar Agent now exposes both a lightweight LangGraph path and the original deterministic Manager-Specialist Harness.

```text
Scope -> Plan -> Explore -> Extract -> Synthesize -> Review -> Deliver
  |       |        |          |           |          |          |
Lead     Planning Explore    Evidence    Synthesis  Review     Artifact
Agent    Subagent Subagent   Subagent    Subagent   Subagent   Subagent
```

## Runtime

- `researchdraft/core/langgraph_harness.py` defines the LangGraph `StateGraph` and writes `graph_handoff_trace.json`.
- `ResearchManagerAgent` still performs the actual deterministic execution so the demo remains stable and testable.
- `researchdraft/workspace/manager.py` materializes Markdown Research Memory: protocol, task plan, Evidence Cards, Claim Map, artifact manifest and diff summary.

## Evidence and Review

- Candidate literature is converted to Evidence Cards.
- `claim_map.md` links claims to evidence and marks `requires_followup` when evidence is missing, low-confidence or unconfirmed.
- `quality_report.md` includes citation coverage, unsupported claim rate, follow-up pass rate and document delivery success rate.

## Extension Boundary

- LangGraph is real in the demo path.
- MCP, vector retrieval and production database are extension adapters, not required for the HR demo.
