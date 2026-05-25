from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import FileResponse, PlainTextResponse
except ModuleNotFoundError:  # Keeps contract tests importable before deps are installed.
    class _Route:
        def __init__(self, path: str) -> None:
            self.path = path

    class FastAPI:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs) -> None:
            self.routes: list[_Route] = []
        def get(self, path: str, *args, **kwargs):
            self.routes.append(_Route(path))
            return lambda fn: fn
        def post(self, path: str, *args, **kwargs):
            self.routes.append(_Route(path))
            return lambda fn: fn

    class HTTPException(Exception):  # type: ignore[no-redef]
        def __init__(self, status_code: int, detail: str) -> None:
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)

    class FileResponse:  # type: ignore[no-redef]
        def __init__(self, path: str | Path, *args, **kwargs) -> None:
            self.path = str(path)

    class PlainTextResponse(str):  # type: ignore[no-redef]
        pass

from researchdraft.agents.manager_agent import ResearchManagerAgent

ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "examples" / "demo_run"

app = FastAPI(
    title="DeepScholar Agent MVP",
    description="Multi-agent research and trusted paper delivery harness demo.",
    version="0.1.0",
)

DEMO_ANSWERS = [
    "DeepScholar Agent：多智能体深度研究与可信论文交付 Harness",
    "HR 需要快速理解一个可运行的研究 Agent MVP，系统需要留下证据、Trace 和 Word 交付物。",
    "如何在论文草稿生成过程中降低无依据结论，并保留可审计交付链路？",
    "任务规划; 候选文献检索; 来源审查; 引用检查; Word 交付",
    "公开网页与用户上传材料的结构化摘要",
    "引用覆盖率; 无依据结论率; 文档交付成功率",
    "Evidence Cards; Trace Evaluation; Human Review Gate",
    "short_paper",
    "docx",
    "",
    "research agent evidence verification",
    "skip",
]


def _run_demo(output_dir: Path = DEMO_DIR):
    answers = iter(DEMO_ANSWERS)
    return ResearchManagerAgent(
        output_dir=output_dir,
        input_fn=lambda _: next(answers),
        llm_client=None,
    ).run()


def _read_json(path: Path) -> Any:
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Not generated: {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "DeepScholar Agent MVP"}


@app.post("/demo/run")
def run_demo() -> dict[str, Any]:
    result = _run_demo()
    return {
        "ok": result.ok,
        "output_dir": result.output_dir,
        "context_path": result.context_path,
        "draft_path": result.draft_path,
        "docx_path": result.docx_path,
        "report_path": result.report_path,
        "trace_path": result.trace_path,
    }


@app.get("/demo/trace")
def demo_trace() -> Any:
    return _read_json(DEMO_DIR / "trace.json")


@app.get("/demo/report", response_class=PlainTextResponse)
def demo_report() -> str:
    path = DEMO_DIR / "quality_report.md"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Run POST /demo/run first")
    return path.read_text(encoding="utf-8")


@app.get("/demo/docx")
def demo_docx() -> FileResponse:
    path = DEMO_DIR / "paper.docx"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Run POST /demo/run first")
    return FileResponse(path, filename="deepscholar-demo-paper.docx")
