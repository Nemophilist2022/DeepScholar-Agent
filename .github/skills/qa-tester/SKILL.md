---
name: qa-tester
description: 验证 DeepScholar-Agent demo、测试、workspace、trace、docx 是否可展示。Use when user asks 测试一下、验证项目、跑 demo、检查能不能展示、qa、smoke test, or before publishing.
---

# DeepScholar-Agent QA Tester

## 验证顺序

1. `git status --short --branch`：确认只包含本次目标改动。
2. 单元测试：
   ```powershell
   python -m unittest tests.test_mvp_contract tests.test_research_workspace tests.test_langgraph_harness tests.test_replay tests.test_deep_research_runtime -v
   ```
3. Demo：
   ```powershell
   python scripts/run_demo.py
   python researchdraft/smoke_check.py
   ```
4. 检查产物存在：`workspace/evidence/*.md`、`workspace/claim_map.md`、`workspace/artifacts/diff_summary.md`、`examples/demo_run/paper.docx`。
5. 如需 API：启动 `uvicorn app.main:app --host 127.0.0.1 --port 8123`，检查 `/health` 和 `/demo/*`。

## 判定

- 只要 demo 可离线稳定跑通，就可作为 HR 展示。
- 外部搜索/API key 不应成为必须条件。
