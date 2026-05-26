# MVP Boundary

## Implemented in this repository

- LangGraph StateGraph for the HR demo path.
- Multi-stage research draft harness.
- SearchProvider abstraction plus Deep Research-style Search/Fetch split with fallback mock search.
- Runtime Markdown Workspace with Evidence Cards, Claim Map, Artifact Manifest and Diff Summary.
- Research Skill registry for planning/search/evidence/citation/report/docx delivery.
- Citation consistency checks and recent literature ratio check.
- Markdown to DOCX delivery with python-docx / OOXML operations.
- Trace, handoff trace, deep research evaluation metrics and Bad Case Replay.
- FastAPI demo wrapper.

## Extension-ready but not required for the demo

- MCP server deployment.
- pgvector / hybrid retrieval.
- Production database and distributed queue.

## Not used

- No Claude Code source code is copied.
- No closed-source Deep Research implementation is copied.
- Public/open-source ideas are reimplemented as lightweight project-local modules.
