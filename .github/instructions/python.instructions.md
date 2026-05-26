---
applyTo: "**/*.py"
---

# Python Coding Instructions for DeepScholar-Agent

- 默认保持标准库优先和轻量实现，避免为 HR demo 引入沉重基础设施依赖。
- Agent 流程代码要显式记录 trace / handoff / artifact path，便于面试讲解。
- Evidence、Claim、Workspace、Evaluation 相关代码必须能用测试或 `scripts/run_demo.py` 生成可查看文件。
- FastAPI endpoint 返回值要偏展示友好：包含 status、path、summary 或 metrics。
- DOCX 生成优先使用 `python-docx` / OOXML；Word COM 只能作为 Windows 可选后处理，不做强依赖。
- 新增功能后优先补 `tests/` 下的契约测试，保持 demo stable。
