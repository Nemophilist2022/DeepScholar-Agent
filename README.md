# DeepScholar Agent｜多智能体深度研究与可信论文交付 Harness

DeepScholar Agent 是一个面向 HR 展示和工程演示的 **Lightweight MVP**：它把研究材料采集、任务规划、候选文献检索、来源审查、引用检查、Word 交付和 Trace 评测串成一个可运行的多智能体研究闭环。

> 项目定位：不是把 LLM 直接接到 Word 上，而是通过 Agent Harness、受控工具调用、Evidence Review、Human-in-the-loop 和 Trace Evaluation，让论文草稿与交付物具备可追踪、可复核、可继续扩展的工程结构。

## Tech Stack

Python / FastAPI / Markdown Workspace / Web Search Provider / File Parsing / python-docx / Word COM / OOXML / Git Diff-friendly Artifacts / Trace Evaluation

LangGraph 与 MCP 在当前 MVP 中作为 extension-ready adapters 预留，不作为运行主链路的强依赖。

## What It Demonstrates

- **Agent Harness 与多智能体协作研究闭环**：`ResearchManagerAgent` 调度 Interview、Planning、Writing、Literature Search、Source Review、Human Review、Citation、Word Format 与 Verifier 等 specialist agents，形成 Scope → Plan → Explore → Extract → Synthesize → Review → Deliver 的状态化流程。
- **文件化 Research Memory**：`workspace/` 使用 Protocol / Task / Evidence / Artifact 四层 Markdown Workspace，沉淀研究规则、任务计划、Evidence Cards、Claim Map 和产物记录，便于续跑、审计与依据回溯。
- **Research Skills 与证据验证**：将来源检索、证据提取、引用核验、报告综合与 DOCX 交付拆成可复用工具链；基于 candidate literature、source review report 与 citation report 检查引用缺失、来源风险和过度推断。
- **文档生成与变更安全**：通过 python-docx / OOXML 生成 Word 文档，保留标题层级、正文结构、参考文献分节和页码字段；公开产物保持 Git Diff-friendly 的 Markdown/JSON/Trace 形式。
- **Trace 与质量评测**：生成 `trace.jsonl`、`trace.json` 和 `quality_report.md`，记录 Agent 路由、工具调用、候选文献、审查反馈和交付结果。

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python scripts/run_demo.py
python researchdraft/smoke_check.py
uvicorn app.main:app --reload
```

FastAPI demo:

```text
GET  /health
POST /demo/run
GET  /demo/trace
GET  /demo/report
GET  /demo/docx
```

## Demo Artifacts

After `python scripts/run_demo.py`, check:

```text
examples/demo_run/draft_context.json
examples/demo_run/draft.md
examples/demo_run/paper.docx
examples/demo_run/quality_report.md
examples/demo_run/trace.json
examples/demo_run/candidate_literature.json
examples/demo_run/source_review_report.json
examples/demo_run/search_cache.json
```

## Repository Layout

```text
app/                 FastAPI demo wrapper
researchdraft/       Multi-agent research and paper delivery harness
thesis_agent/        Rule/tool/trace components extracted from controllable thesis formatting
thesis_formatter/    OOXML and Word formatting utilities
workspace/           Markdown research memory: protocol, task plan, evidence cards, claim map
docs/                Architecture, MVP boundary and demo guide
examples/            Demo input/output artifacts
```

## MVP Boundary

The MVP intentionally focuses on a runnable, reviewable demo:

- Real: Agent orchestration, Web Search Provider abstraction, fallback search, citation checks, Word generation, trace/report artifacts, FastAPI wrapper.
- Extension-ready: LangGraph graph runtime, MCP tool server, vector retrieval and production persistence.
- Safety rule: generated claims must stay grounded in Draft Context or remain as `[待补充]` / `[待确认]` markers.
