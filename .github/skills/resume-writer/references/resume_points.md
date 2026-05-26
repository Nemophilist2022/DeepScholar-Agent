# 简历可用亮点

## 推荐 bullet 素材

- 基于 LangGraph 设计 Scope → Plan → Explore → Extract → Synthesize → Review → Deliver 状态化研究流程，并通过 handoff trace 展示 Lead Agent 对子任务的调度链路。证据：`researchdraft/core/langgraph_harness.py`。
- 设计 Protocol / Task / Evidence / Artifact 四层 Markdown Workspace，将 Evidence Cards、Claim Map、产物 manifest 和 diff summary 文件化，支持过程审计和依据回溯。证据：`researchdraft/workspace/manager.py`、`workspace/`。
- 实现 Claim-Evidence 校验与 Bad Case Replay，输出引用覆盖率、无依据结论率、补检建议和文档交付成功率。证据：`researchdraft/evaluation/deep_research_eval.py`、`researchdraft/replay/bad_case_replay.py`。
- 基于 python-docx / OOXML 完成论文草稿 DOCX 自动交付，支持标题、正文、引用和参考文献结构化写入。证据：`researchdraft/tools/word_tools.py`、`examples/demo_run/paper.docx`。
- 构建 FastAPI Demo 与端到端测试，支持 HR 快速查看 trace、report、workspace、docx 和 replay 结果。证据：`app/main.py`、`tests/`。

## 禁止夸大

- 不写“生产级 Deep Research 平台”。
- 不写“完整 MCP server 已接入所有工具”。
- 不写“PostgreSQL/pgvector/Redis 已生产落地”。
- 不写“直接复刻 Claude Code / DeepResearch”。
