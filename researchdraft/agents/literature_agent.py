from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from researchdraft.core.context import DraftContext, reference_year


CURRENT_YEAR = 2026


@dataclass
class LiteratureReport:
    reference_count: int
    recent_reference_count: int
    recent_reference_ratio: float
    lacks_related_work_support: bool
    literature_needs: list[str] = field(default_factory=list)
    suggested_directions: list[str] = field(default_factory=list)
    manual_confirmation_items: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LiteratureAgent:
    def run(self, ctx: DraftContext) -> LiteratureReport:
        years = [reference_year(ref) for ref in ctx.references]
        recent_count = sum(1 for year in years if year and CURRENT_YEAR - 2 <= year <= CURRENT_YEAR)
        reference_count = len(ctx.references)
        ratio = round(recent_count / reference_count, 2) if reference_count else 0.0
        lacks_related_work = reference_count < 3

        needs: list[str] = []
        if not ctx.references:
            needs.append("[待补充：参考文献]")
        if lacks_related_work:
            needs.append("相关工作支撑不足，需要补充同主题、同方法或同应用场景文献。")
        if ratio < 0.3 and reference_count:
            needs.append("近三年文献占比较低，需要人工确认时效性。")

        directions = _suggest_directions(ctx)
        manual_items = ["[待确认：参考文献真实性、完整性与引用位置]"]
        if ratio < 0.3:
            manual_items.append("[待确认：近三年文献覆盖是否足够]")

        return LiteratureReport(
            reference_count=reference_count,
            recent_reference_count=recent_count,
            recent_reference_ratio=ratio,
            lacks_related_work_support=lacks_related_work,
            literature_needs=needs,
            suggested_directions=directions,
            manual_confirmation_items=manual_items,
        )


def _suggest_directions(ctx: DraftContext) -> list[str]:
    candidates: list[str] = []
    for item in ctx.method[:3]:
        candidates.append(f"围绕“{item}”补充近三年方法对比或系统实现类文献")
    for item in ctx.innovation_points[:2]:
        candidates.append(f"围绕“{item}”补充可验证性、可追踪性或质量评估类文献")
    if ctx.research_problem:
        candidates.append("补充与研究问题直接相关的综述、基准或应用场景文献")
    if not candidates:
        candidates.append("补充与研究方向、方法和应用场景对应的近三年高质量文献")
    return candidates[:5]
