from __future__ import annotations

import re
from typing import Any

from researchdraft.core.context import DraftContext, reference_raw_text
from researchdraft.tools.draft_tools import (
    build_keywords,
    confirmation_marker,
    llm_prompt,
    missing_marker,
)


REQUIRED_HEADINGS = [
    "摘要",
    "关键词",
    "引言",
    "相关工作",
    "方法",
    "实验与结果分析",
    "结论",
    "参考文献",
]

SYSTEM_PROMPT = (
    "You are ResearchDraft WritingAgent. Return JSON only with key markdown. "
    "Use only the supplied DraftContext. Do not fabricate experimental results, "
    "dataset scale, metric values, references, DOI, or authors. Mark missing "
    "facts as [待补充：...] or [待确认：...]."
)


class WritingAgent:
    def __init__(self, llm_client=None) -> None:
        self.llm_client = llm_client

    def run(self, ctx: DraftContext, outline: dict[str, Any]) -> str:
        draft = self._try_llm(ctx, outline)
        if not draft:
            draft = self._template_draft(ctx)
        draft = self._ensure_required_sections(ctx, draft)
        return self._enforce_required_markers(ctx, draft)

    def _try_llm(self, ctx: DraftContext, outline: dict[str, Any]) -> str:
        client = self.llm_client
        if client is None or not hasattr(client, "complete"):
            return ""
        try:
            payload = client.complete(
                llm_prompt(ctx, outline), schema={"system_prompt": SYSTEM_PROMPT}
            )
        except Exception:
            return ""
        markdown = payload.get("markdown") if isinstance(payload, dict) else None
        if not isinstance(markdown, str) or not markdown.strip():
            return ""
        if _looks_fabricated(ctx, markdown):
            return ""
        return markdown.strip() + "\n"

    def _template_draft(self, ctx: DraftContext) -> str:
        title = ctx.title or missing_marker("title")
        background = _sentence(ctx.background) if ctx.background else missing_marker("background")
        problem = _sentence(ctx.research_problem) if ctx.research_problem else missing_marker("research_problem")
        keywords = "；".join(build_keywords(ctx))
        method_text = "；".join(ctx.method) if ctx.method else missing_marker("method")
        metrics_text = "；".join(ctx.metrics) if ctx.metrics else missing_marker("metrics")
        dataset_text = ctx.dataset or (
            f"{missing_marker('dataset')}；{confirmation_marker('数据集规模')}"
        )
        innovation_text = (
            "；".join(ctx.innovation_points)
            if ctx.innovation_points
            else missing_marker("innovation_points")
        )
        citation = "[1]" if ctx.references else missing_marker("related_work_citation")
        refs_text = _references_markdown(ctx)

        sections = [
            f"# {title}",
            "",
            "## 摘要",
            (
                f"本文围绕“{problem}”展开。"
                f"研究背景为：{background}"
                f"方法上，本文计划采用 {method_text}。"
                "本文只整理用户提供的材料，未提供的信息均保留为人工补充或确认标记。"
            ),
            "",
            "## 关键词",
            keywords,
            "",
            "## 引言",
            (
                f"{background}"
                f"本文关注的问题是：{problem}"
                "草稿仅基于 Draft Context 生成，不扩展未经确认的事实。"
            ),
            "",
            "## 相关工作",
            (
                "本节用于梳理与研究问题相关的已有工作。"
                f"当前草稿依据用户提供的参考文献设置引用占位 {citation}；"
                "后续需要人工确认引用位置和论述对应关系。"
            ),
            "",
            "## 方法",
            f"本文拟采用的方法模块包括：{method_text}。",
            f"创新点包括：{innovation_text}。",
            "",
            "## 实验与结果分析",
            f"数据集或材料：{dataset_text}。",
            f"实验指标：{metrics_text}。",
            "实验结果、指标数值和对比结论需要由用户提供后再写入；本文不自动生成。",
            "",
            "## 结论",
            (
                "本文形成了基于用户材料的科研论文草稿生成流程。"
                "后续需要根据质量报告补充缺失材料，并人工确认数据、指标和引用。"
            ),
            "",
            "## 参考文献",
            refs_text,
            "",
        ]
        return "\n".join(sections)

    @staticmethod
    def _ensure_required_sections(ctx: DraftContext, draft: str) -> str:
        result = draft.rstrip()
        if not result.startswith("# "):
            result = f"# {ctx.title or missing_marker('title')}\n\n{result}"
        for heading in REQUIRED_HEADINGS:
            if f"## {heading}" not in result:
                result += f"\n\n## {heading}\n{missing_marker(heading)}"
        return result.strip() + "\n"

    @staticmethod
    def _enforce_required_markers(ctx: DraftContext, draft: str) -> str:
        additions: list[str] = []
        required = [
            ("metrics", missing_marker("metrics")),
            ("references", missing_marker("references")),
        ]
        for field, marker in required:
            value = getattr(ctx, field)
            if not value and marker not in draft:
                additions.append(marker)
        if not ctx.dataset and confirmation_marker("数据集规模") not in draft:
            additions.append(confirmation_marker("数据集规模"))
        if not ctx.references and missing_marker("related_work_citation") not in draft:
            additions.append(missing_marker("related_work_citation"))
        if not additions:
            return draft
        return draft.rstrip() + "\n\n## 自动质检标记\n" + "\n".join(additions) + "\n"


def _references_markdown(ctx: DraftContext) -> str:
    references = [
        reference
        for reference in ctx.references
        if not isinstance(reference, dict)
        or not reference.get("candidate_id")
        or reference.get("confirmed_by_user") is True
    ]
    if not references:
        return missing_marker("references")
    return "\n".join(
        f"[{index}] {reference_raw_text(reference)}"
        for index, reference in enumerate(references, 1)
    )


def _looks_fabricated(ctx: DraftContext, markdown: str) -> bool:
    if not ctx.references and re.search(r"^\s*\[\d+\]\s+.+\d{4}", markdown, re.M):
        return True
    if not ctx.metrics and re.search(r"\b\d+(?:\.\d+)?\s*%", markdown):
        return True
    doi_pattern = r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b"
    if not ctx.references and re.search(doi_pattern, markdown):
        return True
    return False


def _sentence(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return ""
    if stripped[-1] in "。！？!?":
        return stripped
    return stripped + "。"
