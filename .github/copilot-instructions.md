# DeepScholar-Agent Repository Instructions

默认用中文回答。这个仓库是 **DeepScholar Agent｜多智能体深度研究与可信论文交付 Harness** 的 HR 展示型真实 MVP，不是生产级 Deep Research 平台。

## 项目定位

- 核心卖点：把研究任务拆成 Scope → Plan → Explore → Extract → Synthesize → Review → Deliver，并留下 Evidence Cards、Claim Map、Trace、Quality Report、DOCX 产物。
- 真实已落地：FastAPI demo、LangGraph demo path、Markdown Workspace、Search/Fetch provider、Evidence/Claim 校验、Bad Case Replay、python-docx/OOXML 文档生成、Trace Evaluation、测试用例。
- 扩展预留：MCP server、向量库、数据库持久化、生产级多源检索。不要把这些说成已完整生产落地。
- 不要声称复制 DeepResearch 或 Claude Code 源码；正确表述是：借鉴公开 Deep Research / agent harness / skills workspace 思路，本仓库实现为原创轻量 MVP。

## 代码地图

- `app/main.py`：FastAPI demo 入口，提供 `/demo/run`、trace/report/docx/workspace/claim-map/diff/replay/config/search-fetch/evaluation 等端点。
- `researchdraft/agents/manager_agent.py`：确定性 Manager-Specialist 主流程，保证 demo 稳定。
- `researchdraft/core/langgraph_harness.py`：LangGraph `StateGraph` 演示路径，输出 handoff trace。
- `researchdraft/workspace/manager.py`：生成 Protocol / Task / Evidence / Artifact 四层 Markdown Workspace。
- `researchdraft/search/deep_search.py`：search/fetch 分离的轻量检索契约。
- `researchdraft/evaluation/deep_research_eval.py`：claim-evidence 覆盖率与评测报告。
- `researchdraft/replay/bad_case_replay.py`：无依据结论 / 引用缺失 bad case replay。
- `researchdraft/tools/word_tools.py`、`thesis_agent/`、`thesis_formatter/`：DOCX/OOXML/格式校验相关能力。
- `workspace/` 与 `examples/demo_run/`：最适合 HR 或面试展示的产物目录。

## 修改原则

1. 先读相关模块和测试，再改代码；不要只改 README 包装。
2. 所有新增宣传点必须能落到具体文件、接口、测试或 demo artifact。
3. 保持 demo 可快速运行；不要引入必须联网或必须配置私钥才能跑通的强依赖。
4. 文档和简历表达要使用 “Lightweight MVP / extension-ready / demo path” 等边界词，避免生产级夸大。
5. Windows 环境优先，PowerShell 命令优先；文件路径注意中文目录和反斜杠。

## 常用验证命令

```powershell
python -m unittest tests.test_mvp_contract tests.test_research_workspace tests.test_langgraph_harness tests.test_replay tests.test_deep_research_runtime -v
python scripts/run_demo.py
python researchdraft/smoke_check.py
uvicorn app.main:app --host 127.0.0.1 --port 8123
```

如果本机 Python 依赖不完整，优先尝试项目邻近虚拟环境：

```powershell
..\Controllable-Document-Typesettin\.venv\Scripts\python.exe -m unittest tests.test_mvp_contract tests.test_research_workspace tests.test_langgraph_harness tests.test_replay tests.test_deep_research_runtime -v
```
