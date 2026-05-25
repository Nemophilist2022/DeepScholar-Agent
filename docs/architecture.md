# Architecture

DeepScholar Agent uses a lightweight Manager-Specialist Harness.

```text
Scope -> Plan -> Explore -> Extract -> Synthesize -> Review -> Deliver
  |       |        |          |           |          |          |
Interview Planning Search   Source      Writing    Verifier   Word/Report
Agent     Agent    Agent    Review      Agent      Agent      Agent
```

## Core Runtime

- `ResearchManagerAgent` owns `ResearchDraftState` and stage transitions.
- Specialist agents are deterministic Python components with optional LLM hooks.
- Tool outputs are persisted as Markdown, JSON and DOCX artifacts.
- `TraceRecorder` records task id, agent name, stage, input/output keys, tool call, status and failure reason.

## Extension Adapters

- LangGraph can replace the manager loop once graph persistence is required.
- MCP can expose search, file parsing, citation check and DOCX generation as remote tools.
- Vector retrieval can be introduced behind `SearchProvider` without changing the delivery layer.
