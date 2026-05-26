# Demo Guide

## One-command demo

```powershell
python scripts/run_demo.py
```

## What to show HR

1. `README.md`: project positioning and five technical highlights.
2. `examples/demo_run/graph_handoff_trace.json`: LangGraph node handoff chain.
3. `workspace/evidence/`: Evidence Cards generated from candidate literature.
4. `workspace/claim_map.md`: claim-evidence mapping and follow-up status.
5. `workspace/artifacts/diff_summary.md`: Git Diff-friendly artifact snapshot.
6. `examples/demo_run/quality_report.md`: verification metrics and delivery report.
7. `examples/demo_run/paper.docx`: DOCX delivery artifact.

## FastAPI demo

```powershell
uvicorn app.main:app --reload
```

Useful endpoints:

```text
GET  /health
POST /demo/run
GET  /demo/trace
GET  /demo/report
GET  /demo/docx
GET  /demo/workspace
GET  /demo/claim-map
GET  /demo/diff
GET  /demo/replay
```
