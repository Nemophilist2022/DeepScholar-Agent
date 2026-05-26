---
name: project-learner
description: 通过源码走读帮助理解 DeepScholar-Agent。Use when the user says 学习项目、了解项目、代码走读、源码讲解、learn codebase、walk through code, or wants to understand how modules connect.
---

# DeepScholar-Agent Project Learner

默认中文。按“入口 → 状态 → 工具 → 产物 → 测试”带用户理解项目。

## 走读顺序

1. `README.md` / `docs/architecture.md`：先建立业务和架构图。
2. `scripts/run_demo.py`：看一键 demo 如何启动。
3. `app/main.py`：看 FastAPI 如何包装 demo。
4. `researchdraft/agents/manager_agent.py`：看稳定执行链路。
5. `researchdraft/core/langgraph_harness.py`：看 LangGraph 演示链路。
6. `researchdraft/workspace/manager.py`：看 Evidence/Claim/Artifact 文件化。
7. `researchdraft/evaluation/deep_research_eval.py`：看评测指标。
8. `tests/`：看哪些能力有测试契约。

## 输出要求

每个模块讲：职责、输入、输出、为什么这么设计、面试怎么说、下一步扩展。
