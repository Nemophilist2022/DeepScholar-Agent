from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

from researchdraft.core.context import DraftContext, reference_raw_text


@dataclass
class CitationReport:
    reference_count: int
    in_text_citations: list[int] = field(default_factory=list)
    missing_reference_numbers: list[int] = field(default_factory=list)
    unused_reference_numbers: list[int] = field(default_factory=list)
    duplicate_references: list[str] = field(default_factory=list)
    format_risks: list[str] = field(default_factory=list)
    needs_source_marker: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CitationAgent:
    def run(self, *, draft_markdown: str, draft_context: DraftContext) -> CitationReport:
        references = [reference_raw_text(ref) for ref in draft_context.references]
        citations = sorted({int(value) for value in re.findall(r"\[(\d+)\]", draft_markdown)})
        reference_numbers = set(range(1, len(references) + 1))
        citation_numbers = set(citations)

        duplicates = _duplicate_references(references)
        risks = _format_risks(references)
        missing = sorted(citation_numbers - reference_numbers)
        unused = sorted(reference_numbers - citation_numbers)

        return CitationReport(
            reference_count=len(references),
            in_text_citations=citations,
            missing_reference_numbers=missing,
            unused_reference_numbers=unused,
            duplicate_references=duplicates,
            format_risks=risks,
            needs_source_marker=bool(missing) or (not references),
        )


def _duplicate_references(references: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for raw in references:
        key = re.sub(r"\s+", " ", raw.strip().lower())
        if not key:
            continue
        if key in seen and raw not in duplicates:
            duplicates.append(raw)
        seen.add(key)
    return duplicates


def _format_risks(references: list[str]) -> list[str]:
    risks: list[str] = []
    for index, raw in enumerate(references, 1):
        stripped = raw.strip()
        if len(stripped) < 25:
            risks.append(f"[{index}] 参考文献过于简略")
            continue
        if not re.search(r"\b(19|20)\d{2}\b", stripped):
            risks.append(f"[{index}] 缺少年份")
        if "." not in stripped and "。" not in stripped:
            risks.append(f"[{index}] 缺少题名/来源分隔信息")
    return risks
