from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Callable, Any

from researchdraft.core.context import DraftContext


@dataclass
class HumanReviewResult:
    confirmed_candidate_ids: list[str] = field(default_factory=list)
    skipped: bool = False
    rejected_candidate_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class HumanReviewGate:
    def __init__(self, *, input_fn: Callable[[str], str] = input) -> None:
        self.input_fn = input_fn

    def run(
        self,
        ctx: DraftContext,
        candidates: list[dict[str, Any]],
    ) -> HumanReviewResult:
        if not candidates:
            return HumanReviewResult(skipped=True)

        print("\n候选文献（仅供人工确认，不会自动进入参考文献）：")
        for candidate in candidates:
            print(
                f"- {candidate.get('candidate_id')}: {candidate.get('title')} "
                f"({candidate.get('year', 'unknown')}) {candidate.get('source_url', '')}"
            )
        raw = self.input_fn("请输入确认的 candidate_id（逗号分隔），或输入 skip 跳过：").strip()
        if not raw or raw.lower() == "skip":
            return HumanReviewResult(
                skipped=True,
                rejected_candidate_ids=[str(item.get("candidate_id", "")) for item in candidates],
            )

        requested = [item.strip() for item in raw.replace("，", ",").split(",") if item.strip()]
        by_id = {str(candidate.get("candidate_id")): candidate for candidate in candidates}
        confirmed: list[str] = []
        for candidate_id in requested:
            candidate = by_id.get(candidate_id)
            if candidate is None:
                continue
            confirmed.append(candidate_id)
            ctx.references.append(_candidate_to_reference(candidate))

        rejected = [
            str(candidate.get("candidate_id", ""))
            for candidate in candidates
            if str(candidate.get("candidate_id", "")) not in confirmed
        ]
        ctx.missing_fields = ctx.compute_missing_fields()
        return HumanReviewResult(
            confirmed_candidate_ids=confirmed,
            skipped=not confirmed,
            rejected_candidate_ids=rejected,
        )


def _candidate_to_reference(candidate: dict[str, Any]) -> dict[str, Any]:
    title = str(candidate.get("title") or "[待确认：候选文献标题]").strip()
    year = candidate.get("year")
    year_text = "" if year in (None, "", "unknown") else f" {year}"
    return {
        "raw_text": f"{title}{year_text}".strip(),
        "year": year if isinstance(year, int) else None,
        "source_type": candidate.get("source_type") or "unknown",
        "source_url": candidate.get("source_url", ""),
        "candidate_id": candidate.get("candidate_id", ""),
        "is_confirmed": True,
        "confirmed_by_user": True,
    }
