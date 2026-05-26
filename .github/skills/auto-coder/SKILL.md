---
name: auto-coder
description: 在 DeepScholar-Agent 中安全实现新功能。Use when user asks to add/fix/optimize code, implement endpoints, improve agents, extend workspace, add tests, or update demo behavior.
---

# DeepScholar-Agent Auto Coder

## 开发原则

- 新功能必须对应 README/面试可讲的真实能力，不做空包装。
- 先找现有入口：`app/main.py`、`researchdraft/agents/manager_agent.py`、`researchdraft/core/langgraph_harness.py`、`researchdraft/workspace/manager.py`、`tests/`。
- 保持 demo 离线可运行；外部 search provider 必须有 fallback。
- 新增展示能力时同步补：artifact、trace 或测试至少一个证据点。
- 代码改动后运行相关 unittest 或 smoke check。

## 常见改动位置

- API 端点：`app/main.py`
- Agent 编排：`researchdraft/core/langgraph_harness.py`、`researchdraft/agents/manager_agent.py`
- Evidence/Claim：`researchdraft/workspace/manager.py`
- 检索：`researchdraft/search/deep_search.py`
- 评测：`researchdraft/evaluation/deep_research_eval.py`
- DOCX：`researchdraft/tools/word_tools.py`、`thesis_formatter/`
