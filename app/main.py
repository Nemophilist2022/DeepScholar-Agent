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
from researchdraft.config.research_config import ResearchConfig
from researchdraft.core.langgraph_harness import run_research_graph
from researchdraft.evaluation.deep_research_eval import evaluate_claims
from researchdraft.replay.bad_case_replay import run_bad_case_replay
from researchdraft.search.deep_search import SearchFetchProvider

ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "examples" / "demo_run"
WORKSPACE_DIR = ROOT / "workspace"

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


def _run_graph_demo(output_dir: Path = DEMO_DIR):
    return run_research_graph(output_dir=output_dir, answers=list(DEMO_ANSWERS))


def _read_json(path: Path) -> Any:
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Not generated: {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "DeepScholar Agent MVP"}


@app.post("/demo/run")
def run_demo() -> dict[str, Any]:
    graph_result = _run_graph_demo()
    result = graph_result.manager_result
    return {
        "ok": result.ok,
        "graph_nodes": graph_result.graph_nodes,
        "handoff_trace_path": graph_result.handoff_trace_path,
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


@app.get("/demo/workspace")
def demo_workspace() -> dict[str, Any]:
    files = []
    for path in sorted(WORKSPACE_DIR.rglob("*")):
        if path.is_file():
            files.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "size": path.stat().st_size,
                }
            )
    return {"root": str(WORKSPACE_DIR.relative_to(ROOT)), "files": files}


@app.get("/demo/claim-map", response_class=PlainTextResponse)
def demo_claim_map() -> str:
    path = WORKSPACE_DIR / "claim_map.md"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Run POST /demo/run first")
    return path.read_text(encoding="utf-8")


@app.get("/demo/diff", response_class=PlainTextResponse)
def demo_diff() -> str:
    path = WORKSPACE_DIR / "artifacts" / "diff_summary.md"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Run POST /demo/run first")
    return path.read_text(encoding="utf-8")


@app.get("/demo/replay")
def demo_replay() -> dict[str, Any]:
    return run_bad_case_replay()


@app.get("/demo/config")
def demo_config() -> dict[str, Any]:
    return ResearchConfig.default().to_dict()


@app.get("/demo/search-fetch")
def demo_search_fetch(query: str = "traceable research agent") -> dict[str, Any]:
    provider = SearchFetchProvider()
    results = provider.search(query, max_results=3)
    fetched = [provider.fetch(result).to_dict() for result in results]
    return {
        "query": query,
        "results": [result.to_dict() for result in results],
        "fetched_documents": fetched,
    }


@app.get("/demo/evaluation")
def demo_evaluation() -> dict[str, Any]:
    result = evaluate_claims(
        claims=[
            {"id": "C1", "text": "Trace is recorded", "evidence_id": "E1"},
            {"id": "C2", "text": "Unsupported performance gain", "evidence_id": ""},
        ],
        evidence_cards=[{"id": "E1", "confidence": 0.9, "status": "confirmed"}],
    )
    return result.to_dict()
