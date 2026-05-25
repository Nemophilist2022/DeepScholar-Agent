from __future__ import annotations

from researchdraft.agents.manager_agent import ResearchManagerAgent


def main() -> int:
    print("ResearchDraft Agent Harness MVP v5")
    print("请根据提示输入研究材料；候选文献来自可插拔 SearchProvider，必须人工确认后才会进入参考文献。")
    result = ResearchManagerAgent(llm_client=None).run()
    print("\n输出完成：")
    print(f"- Draft Context: {result.context_path}")
    print(f"- Markdown 草稿: {result.draft_path}")
    print(f"- Word 文档: {result.docx_path}")
    print(f"- 质量报告: {result.report_path}")
    print(f"- Trace: {result.trace_path}")
    print(f"- 候选文献: {result.output_dir}\\candidate_literature.json")
    print(f"- 来源审查: {result.output_dir}\\source_review_report.json")
    print(f"- 搜索缓存: {result.output_dir}\\search_cache.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
