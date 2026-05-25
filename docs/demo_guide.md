# Demo Guide

## One-command demo

```powershell
python scripts/run_demo.py
```

## What to show HR

1. Open `README.md` for positioning and architecture.
2. Open `workspace/` to show file-based research memory.
3. Open `examples/demo_run/quality_report.md` to show verification output.
4. Open `examples/demo_run/trace.json` to show agent execution trace.
5. Open `examples/demo_run/paper.docx` to show Word delivery.

## FastAPI demo

```powershell
uvicorn app.main:app --reload
```

Then visit `/docs` or call `/demo/run`, `/demo/trace`, `/demo/report`, `/demo/docx`.
