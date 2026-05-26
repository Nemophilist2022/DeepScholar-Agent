from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from researchdraft.core.context import DraftContext, reference_raw_text
from researchdraft.core.trace import TraceEntry
from researchdraft.tools.verify_tools import (
    VerificationResult,
    check_docx_format,
    check_output_files,
    check_required_sections,
    check_trace_entries,
    scan_content_markers,
)


class VerifierAgent:
    def __init__(self, *, output_dir: str | Path = "researchdraft/outputs") -> None:
        self.output_dir = Path(output_dir)

    def run(
        self,
        *,
        draft_markdown: str,
        docx_path: str,
        trace_entries: list[TraceEntry],
        draft_context: DraftContext | None = None,
        draft_path: str = "",
        citation_report=None,
        literature_report=None,
        candidate_literature=None,
        source_review_report=None,
        human_review_result=None,
    ) -> VerificationResult:
        missing, confirmations = scan_content_markers(draft_markdown)
        report_path = self.output_dir / "quality_report.md"
        result = VerificationResult(
            completed=[
                "Draft Context 已生成",
                "Markdown 草稿已生成",
                "Word 文档已生成",
                "候选文献、来源审查与搜索缓存已生成",
                "Trace 已记录 Manager-Specialist 执行步骤",
                "VerifierAgent 已执行文件、章节、缺失标记、Word、搜索与 Trace 检查",
            ],
            missing_items=missing,
            confirmation_items=confirmations,
            structure_checks=check_required_sections(draft_markdown),
            file_checks=check_output_files(
                {
                    "draft_context.json": str(self.output_dir / "draft_context.json"),
                    "draft.md": draft_path,
                    "paper.docx": docx_path,
                    "candidate_literature.json": str(self.output_dir / "candidate_literature.json"),
                    "source_review_report.json": str(self.output_dir / "source_review_report.json"),
                    "search_cache.json": str(self.output_dir / "search_cache.json"),
                    "trace.json": str(self.output_dir / "trace.json"),
                }
            ),
            trace_checks=check_trace_entries(trace_entries),
            format_checks=check_docx_format(docx_path),
            citation_report=citation_report,
            literature_report=literature_report,
            candidate_literature=candidate_literature,
            source_review_report=source_review_report,
            human_review_result=human_review_result,
            quality_metrics=_quality_metrics(
                missing,
                confirmations,
                citation_report,
                candidate_literature,
                docx_path,
            ),
            report_path=str(report_path),
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            _render_report(
                result,
                trace_entries,
                draft_context=draft_context,
                draft_path=draft_path,
                docx_path=docx_path,
            ),
            encoding="utf-8",
        )
        return result


def _render_report(
    result: VerificationResult,
    trace_entries: list[TraceEntry],
    *,
    draft_context: DraftContext | None = None,
    draft_path: str = "",
    docx_path: str = "",
) -> str:
    ctx = draft_context
    title = ctx.title if ctx and ctx.title else "[待补充：论文标题]"
    lines = ["# ResearchDraft Agent Harness 质量报告", ""]

    lines.append("## 项目摘要")
    lines.append("- 项目名称：ResearchDraft Agent Harness")
    lines.append("- 版本：MVP v5 Web Search Provider 与候选文献元数据增强")
    lines.append("- 架构意图：Manager 负责任务调度，Specialist Agent 分别负责访谈、规划、写作、搜索、来源审查、人工确认、引用检查、Word 排版和验证。")
    lines.append("- 约束：不做 RAG，不做向量库，不新增 LaTeX、GUI 或数据库。")
    lines.append("- 文献原则：搜索结果仅作为 candidate_literature，未经人工确认不得进入正式参考文献。")
    lines.append("- 内容原则：禁止编造论文、作者、DOI、期刊、实验结果、指标或数据集规模。")
    lines.append(f"- 论文标题：{title}")
    if draft_path:
        lines.append(f"- Markdown 草稿：{draft_path}")
    if docx_path:
        lines.append(f"- Word 文档：{docx_path}")
    lines.append("")

    lines.append("## Draft Context 摘要")
    if ctx is None:
        lines.append("- [待补充：Draft Context]")
    else:
        lines.append(f"- 研究背景：{ctx.background or '[待补充：研究背景]'}")
        lines.append(f"- 研究问题：{ctx.research_problem or '[待补充：研究问题]'}")
        lines.append(f"- 方法模块：{_join_or_missing(ctx.method, '方法模块')}")
        lines.append(f"- 数据集或材料：{ctx.dataset or '[待补充：数据集或材料]'}")
        lines.append(f"- 实验指标：{_join_or_missing(ctx.metrics, '实验指标')}")
        lines.append(f"- 创新点：{_join_or_missing(ctx.innovation_points, '创新点')}")
        lines.append(f"- 参考文献：{_references_summary(ctx)}")
        if ctx.missing_fields:
            lines.append(f"- Draft Context 缺失字段：{'；'.join(ctx.missing_fields)}")
    lines.append("")

    lines.append("## 结构检查")
    for check in result.structure_checks:
        lines.append(_check_line(check))
    lines.append("")

    lines.append("## 内容缺失")
    lines.append(f"- 待补充标记数量：{len(result.missing_items)}")
    lines.append(f"- 待确认标记数量：{len(result.confirmation_items)}")
    lines.append("- 原则：缺失内容必须保留 [待补充：...] 或 [待确认：...]，不得替换为猜测内容。")
    lines.append("")

    lines.append("## 待补充项")
    lines.extend(_items_or_none(result.missing_items))
    lines.append("")

    lines.append("## 待确认项")
    manual_items = list(result.confirmation_items)
    if ctx and not ctx.references:
        manual_items.append("[待确认：参考文献真实性与引用位置]")
    if ctx and not ctx.metrics:
        manual_items.append("[待确认：实验指标与结果数值]")
    literature = result.literature_report
    if literature:
        manual_items.extend(literature.manual_confirmation_items)
    lines.extend(_items_or_none(sorted(set(manual_items))))
    lines.append("")

    lines.append("## 引用与文献质量检查")
    _append_citation_literature_report(lines, result.citation_report, result.literature_report)
    lines.append("")

    lines.append("## 联网文献搜索与人工确认")
    _append_web_search_report(
        lines,
        result.candidate_literature,
        result.source_review_report,
        result.human_review_result,
    )
    lines.append("")

    lines.append("## Word 输出检查")
    for check in result.file_checks:
        lines.append(_check_line(check))
    for check in result.format_checks:
        lines.append(_check_line(check))
    if result.missing_items or result.confirmation_items:
        lines.append("- 提示：Word 输出保留待补充/待确认标记，便于人工继续编辑。")
    lines.append("")

    lines.append("## Agent 执行摘要")
    by_agent: dict[str, int] = {}
    for entry in trace_entries:
        by_agent[entry.agent] = by_agent.get(entry.agent, 0) + 1
    for agent, count in by_agent.items():
        lines.append(f"- {agent}: {count} 步")
    for check in result.trace_checks:
        lines.append(_check_line(check))
    lines.append("")

    lines.append("## Trace 与质量评测")
    metrics = result.quality_metrics
    lines.append(f"- 引用覆盖率：{metrics.get('citation_coverage_rate', 0.0):.0%}")
    lines.append(f"- 无依据结论率：{metrics.get('unsupported_claim_rate', 0.0):.0%}")
    lines.append(f"- 补检通过率：{metrics.get('followup_pass_rate', 0.0):.0%}")
    lines.append(f"- 文档交付成功率：{metrics.get('document_delivery_success_rate', 0.0):.0%}")
    lines.append("- Bad Case Replay：可通过 `/demo/replay` 或 `researchdraft.replay.bad_case_replay` 复现无依据结论场景。")
    lines.append("")

    lines.append("## Agent 执行明细")
    for entry in trace_entries:
        data = asdict(entry)
        lines.append(
            "- "
            f"{data['task_id']} | {data['stage']} | {data['agent']} | "
            f"tool={data['tool_call'] or 'none'} | status={data['status']} | "
            f"time={data['timestamp']}"
        )
        if data["failure_reason"]:
            lines.append(f"  - failure_reason: {data['failure_reason']}")
    lines.append("")

    lines.append("## 版本限制")
    lines.append("- 搜索结果只是候选文献线索，不自动写入正式参考文献。")
    lines.append("- 没有搜索 API key 或真实搜索失败时自动 fallback 到 mock provider。")
    lines.append("- 不自动生成 DOI、作者、期刊、实验结果、数据集规模、指标数值或对比结论。")
    lines.append("- 不做 RAG、向量库、LaTeX、GUI 或数据库。")
    lines.append("")
    return "\n".join(lines)


def _append_citation_literature_report(lines: list[str], citation, literature) -> None:
    if citation is None:
        lines.append("- 引用检查：未运行")
    else:
        lines.append(f"- 参考文献总数：{citation.reference_count}")
        lines.append(f"- 正文引用数量：{len(citation.in_text_citations)}")
        lines.append(f"- 未在正文引用的参考文献：{_numbers_or_none(citation.unused_reference_numbers)}")
        lines.append(f"- 正文引用但参考文献缺失的问题：{_numbers_or_none(citation.missing_reference_numbers)}")
        lines.append(f"- 重复参考文献：{_items_text(citation.duplicate_references)}")
        lines.append(f"- 文献格式风险：{_items_text(citation.format_risks)}")
        if citation.needs_source_marker:
            lines.append("- 人工确认项：[待补充：引用来源]")

    if literature is None:
        lines.append("- 文献质量分析：未运行")
    else:
        ratio = f"{literature.recent_reference_ratio:.0%}"
        lines.append(f"- 近三年文献数量：{literature.recent_reference_count}")
        lines.append(f"- 近三年文献占比：{ratio}")
        lines.append(f"- 是否缺少相关工作支撑：{'是' if literature.lacks_related_work_support else '否'}")
        lines.append(f"- 文献需求分析：{_items_text(literature.literature_needs)}")
        lines.append(f"- 建议补充的文献方向：{_items_text(literature.suggested_directions)}")
        lines.append(f"- 人工确认项：{_items_text(literature.manual_confirmation_items)}")


def _quality_metrics(missing, confirmations, citation, candidates, docx_path: str) -> dict[str, float]:
    reference_count = getattr(citation, "reference_count", 0) if citation else 0
    citation_count = len(getattr(citation, "in_text_citations", [])) if citation else 0
    citation_coverage = 1.0 if reference_count == 0 and citation_count == 0 else min(citation_count / max(reference_count, 1), 1.0)
    unsupported_total = len(missing) + len(confirmations)
    unsupported_rate = min(unsupported_total / max(unsupported_total + 3, 1), 1.0)
    candidate_items = getattr(candidates, "candidates", []) if candidates else []
    confirmed = [item for item in candidate_items if item.get("status") == "confirmed"]
    followup_pass = len(confirmed) / len(candidate_items) if candidate_items else 0.0
    delivery_success = 1.0 if Path(docx_path).exists() and Path(docx_path).stat().st_size > 0 else 0.0
    return {
        "citation_coverage_rate": round(citation_coverage, 2),
        "unsupported_claim_rate": round(unsupported_rate, 2),
        "followup_pass_rate": round(followup_pass, 2),
        "document_delivery_success_rate": round(delivery_success, 2),
    }


def _append_web_search_report(lines: list[str], candidates, source_review, human_review) -> None:
    candidate_items = candidates.candidates if candidates else []
    queries = candidates.queries if candidates else []
    distribution = source_review.source_type_distribution if source_review else {}
    high_risk = source_review.high_risk_candidate_ids if source_review else []
    confirmed_ids = human_review.confirmed_candidate_ids if human_review else []
    unconfirmed_count = max(len(candidate_items) - len(confirmed_ids), 0)
    high_confidence = sum(1 for item in candidate_items if float(item.get("confidence", 0.0)) >= 0.7)
    low_confidence = sum(1 for item in candidate_items if float(item.get("confidence", 0.0)) < 0.5)

    lines.append(f"- 搜索 provider：{getattr(candidates, 'provider', 'unknown') if candidates else 'unknown'}")
    lines.append(f"- 搜索 query 列表：{_items_text(queries)}")
    lines.append(f"- 是否使用缓存：{getattr(candidates, 'cache_hit', False) if candidates else False}")
    lines.append(f"- 候选去重前数量：{getattr(candidates, 'raw_result_count', 0) if candidates else 0}")
    lines.append(f"- 候选去重后数量：{getattr(candidates, 'deduped_result_count', len(candidate_items)) if candidates else 0}")
    lines.append(f"- 候选文献数量：{len(candidate_items)}")
    lines.append(f"- 高置信候选数量：{high_confidence}")
    lines.append(f"- 低置信候选数量：{low_confidence}")
    lines.append(f"- 已确认文献数量：{len(confirmed_ids)}")
    lines.append(f"- 未确认候选数量：{unconfirmed_count}")
    lines.append(f"- 来源类型分布：{_distribution_text(distribution)}")
    lines.append(f"- 高风险候选：{_items_text(high_risk)}")
    lines.append(f"- 人工确认结果：{_items_text(confirmed_ids) if confirmed_ids else 'skip/无确认'}")
    lines.append(f"- 搜索失败与 fallback 情况：fallback_used={getattr(candidates, 'fallback_used', False) if candidates else False}；failure_reason={getattr(candidates, 'failure_reason', '') if candidates else ''}")
    if candidate_items:
        lines.append("- 未进入正式参考文献的候选说明：pending_review 候选仅保留在 candidate_literature.json，不写入 draft.md 参考文献章节。")


def _join_or_missing(items: list[str], label: str) -> str:
    return "；".join(items) if items else f"[待补充：{label}]"


def _references_summary(ctx: DraftContext) -> str:
    if not ctx.references:
        return "[待补充：参考文献]"
    return "；".join(reference_raw_text(ref) for ref in ctx.references)


def _items_or_none(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] if items else ["- 无"]


def _items_text(items) -> str:
    return "；".join(str(item) for item in items) if items else "无"


def _numbers_or_none(numbers: list[int]) -> str:
    return "；".join(f"[{number}]" for number in numbers) if numbers else "无"


def _distribution_text(distribution: dict[str, int]) -> str:
    if not distribution:
        return "无"
    return "；".join(f"{key}:{value}" for key, value in sorted(distribution.items()))


def _check_line(check) -> str:
    status = "通过" if check.passed else "需处理"
    return f"- {check.name}: {status}；{check.evidence}"
