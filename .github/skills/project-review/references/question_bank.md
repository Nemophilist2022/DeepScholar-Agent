# DeepScholar-Agent 复习题库

## 1. 项目定位

Q1：这个项目解决什么问题？
A：它不是单纯生成论文，而是把研究任务拆解、证据管理、引用核验、文档交付和评测串成可追踪 Harness。路径：`README.md`、`docs/architecture.md`。

Q2：为什么说它是 MVP，而不是生产平台？
A：FastAPI、LangGraph demo、Workspace、DOCX、Trace 已可运行；MCP、向量库、生产数据库是 extension-ready。路径：`docs/mvp_boundary.md`。

## 2. Agent 工作流

Q3：Scope → Deliver 每步分别做什么？
A：Scope 定义任务，Plan 制定计划，Explore 找来源，Extract 建 Evidence，Synthesize 写草稿，Review 核验 claim，Deliver 输出 DOCX 和 trace。路径：`researchdraft/core/langgraph_harness.py`。

Q4：Lead Agent 和 Subagents 怎么体现？
A：LangGraph 节点和 handoff trace 记录 Planning/Explore/Review/Artifact 等角色调度。路径：`examples/demo_run/graph_handoff_trace.json`。

## 3. Research Memory

Q5：Markdown Workspace 为什么有价值？
A：把协议、任务、证据、产物文件化，便于续跑、审计、rg 检索和面试展示。路径：`workspace/`、`researchdraft/workspace/manager.py`。

Q6：Evidence Cards 和 Claim Map 的关系？
A：Evidence Cards 保存来源元数据和摘要；Claim Map 把结论映射到 evidence id，并标记 low confidence / missing evidence。路径：`workspace/evidence/`、`workspace/claim_map.md`。

## 4. 验证与评测

Q7：怎么发现无依据结论？
A：Verifier / replay 检查 claim 是否有 evidence 支撑，输出 unsupported claim rate、follow-up 建议。路径：`researchdraft/replay/bad_case_replay.py`、`researchdraft/evaluation/deep_research_eval.py`。

Q8：质量报告有哪些指标？
A：citation coverage、unsupported claim rate、follow-up pass rate、document delivery success rate。路径：`examples/demo_run/quality_report.md`。

## 5. 文档交付

Q9：DOCX 怎么生成？
A：使用 python-docx/OOXML 写入标题层级、正文、参考文献和字段；Word COM 是 Windows 可选增强，不是强依赖。路径：`researchdraft/tools/word_tools.py`。

Q10：变更安全怎么讲？
A：`diff_summary.md` 记录 draft、claim_map、evidence、report 的变化摘要，减少多轮修改内容漂移。路径：`researchdraft/tools/diff_tools.py`。

## 6. 展示与面试

Q11：HR 看这个仓库最该展示什么？
A：README 定位、`scripts/run_demo.py`、FastAPI endpoints、`workspace/` 证据文件、`paper.docx`、`quality_report.md`。

Q12：如果被问“是不是直接用了 DeepResearch/Claude Code 源码”？
A：回答：没有复制闭源源码；借鉴公开 agent/workspace/evidence verification 思路，用本仓库轻量代码实现 demo。路径：`docs/architecture.md` 的边界说明。
