# DeepScholar-Agent 项目地图

## 一句话定位

DeepScholar-Agent 是一个 HR 展示型真实 MVP：用 Agent Harness 把研究任务拆解、证据沉淀、引用核验、文档交付和质量评测串成可运行闭环。

## 运行链路

`Scope → Plan → Explore → Extract → Synthesize → Review → Deliver`

- Scope/Plan：确定研究主题、章节和任务计划。
- Explore：候选文献/网页来源搜索，输出 `candidate_literature.json`。
- Extract：候选来源转 Evidence Cards。
- Synthesize：基于上下文生成 `draft.md`。
- Review：生成 `claim_map.md` 和 `quality_report.md`，识别 unsupported claims。
- Deliver：生成 `paper.docx`，写入 trace 和 manifest。

## 关键源码

- `app/main.py`：FastAPI 展示层。
- `scripts/run_demo.py`：一键 demo。
- `researchdraft/agents/manager_agent.py`：确定性执行主链路。
- `researchdraft/core/langgraph_harness.py`：LangGraph 状态图 demo。
- `researchdraft/workspace/manager.py`：Markdown Workspace 生成。
- `researchdraft/search/deep_search.py`：Search/Fetch provider。
- `researchdraft/evaluation/deep_research_eval.py`：质量评测指标。
- `researchdraft/replay/bad_case_replay.py`：Bad Case Replay。
- `researchdraft/tools/word_tools.py`：DOCX 输出。
- `thesis_agent/`、`thesis_formatter/`：论文格式控制与工具化排版能力。

## Demo 产物

- `examples/demo_run/draft.md`
- `examples/demo_run/paper.docx`
- `examples/demo_run/quality_report.md`
- `examples/demo_run/graph_handoff_trace.json`
- `workspace/evidence/*.md`
- `workspace/claim_map.md`
- `workspace/artifacts/diff_summary.md`

## 稳妥边界

- 可以说：LangGraph demo path 真实存在；Markdown Workspace、Evidence/Claim 校验、DOCX 交付、Trace/Evaluation 有代码和样例。
- 不要说：已经是生产级 Deep Research、已经完整 MCP server、已经接 PostgreSQL/pgvector 生产库、直接复制 Claude Code 或 DeepResearch 源码。
