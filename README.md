# DeepScholar Agent｜多智能体深度研究与可信论文交付 Harness

DeepScholar Agent 是一个面向 HR 展示和工程演示的 **Lightweight MVP**：它把研究材料采集、任务规划、候选文献检索、来源审查、引用检查、Word 交付和 Trace 评测串成一个可运行的多智能体研究闭环。

> 项目定位：不是把 LLM 直接接到 Word 上，而是通过 Agent Harness、受控工具调用、Evidence Review、Human-in-the-loop 和 Trace Evaluation，让论文草稿与交付物具备可追踪、可复核、可继续扩展的工程结构。

## Tech Stack

Python / FastAPI / LangGraph / Research Config / Search-Fetch Tool Contract / Markdown Workspace / Web Search Provider / File Parsing / python-docx / Word COM / OOXML / Git Diff-friendly Artifacts / Trace Evaluation

LangGraph 已用于 demo graph path；项目借鉴 Open Deep Research / OpenAI Deep Research 公开架构中的 config、search/fetch、evaluation 思路，但实现为本仓库自研轻量模块；MCP 在当前 MVP 中作为 extension-ready adapter 预留，不作为运行主链路的强依赖。

## What It Demonstrates

- **Agent Harness 与多智能体协作研究闭环**：`researchdraft/core/langgraph_harness.py` 使用 LangGraph StateGraph 定义 Scope → Plan → Explore → Extract → Synthesize → Review → Deliver；`LeadResearchAgent` 通过 handoff trace 展示 Explore、Review 与 Artifact Subagents 的调度链路。
- **文件化 Research Memory**：`researchdraft/workspace/manager.py` 在运行时维护 Protocol / Task / Evidence / Artifact 四层 Markdown Workspace，生成 Evidence Cards、Claim Map、Artifact Manifest 与 Diff Summary；可用 ripgrep 对工作区做 progressive context loading 和依据回溯。
- **Research Skills 与证据验证**：`researchdraft/skills/registry.py` 将 planning、source_search、evidence_extract、citation_check、report_synthesis、docx_delivery 抽象成可复用 Skills；新增 `ResearchConfig`、`SearchFetchProvider` 与 `deep_research_eval`，形成 search → fetch → evaluate 的可测试研究链路。
- **文档生成与变更安全**：通过 python-docx / OOXML 生成 Word 文档，保留标题层级、正文结构、参考文献分节和页码字段；`diff_summary.md` 记录 Markdown Workspace 与交付产物快照，降低多轮修订中的内容漂移风险。
- **Trace 与质量评测**：生成 `trace.jsonl`、`trace.json`、`graph_handoff_trace.json` 和 `quality_report.md`，记录 Subagent Handoff、Skill 调用、工具执行、证据引用、审查反馈和产物版本；内置 Bad Case Replay 展示无依据结论检测。

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
GET  /demo/workspace
GET  /demo/claim-map
GET  /demo/diff
GET  /demo/replay
GET  /demo/config
GET  /demo/search-fetch
GET  /demo/evaluation
```

## Demo Artifacts

After `python scripts/run_demo.py`, check:

```text
examples/demo_run/draft_context.json
examples/demo_run/draft.md
examples/demo_run/paper.docx
examples/demo_run/quality_report.md
examples/demo_run/trace.json
examples/demo_run/graph_handoff_trace.json
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

- Real: LangGraph graph path, Agent orchestration, Research Config, Search/Fetch split, Evaluation Report, Markdown Workspace runtime, Evidence Cards, Claim Map, Bad Case Replay, Web Search Provider abstraction, citation checks, Word generation, trace/report artifacts, FastAPI wrapper.
- Extension-ready: MCP tool server, vector retrieval and production persistence.
- Safety rule: generated claims must stay grounded in Draft Context or remain as `[待补充]` / `[待确认]` markers.
