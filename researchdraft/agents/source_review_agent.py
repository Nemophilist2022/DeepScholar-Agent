from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SourceReviewResult:
    review_items: list[dict[str, Any]] = field(default_factory=list)
    source_type_distribution: dict[str, int] = field(default_factory=dict)
    high_risk_candidate_ids: list[str] = field(default_factory=list)
    output_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SourceReviewAgent:
    def __init__(self, *, output_dir: str | Path = "researchdraft/outputs") -> None:
        self.output_dir = Path(output_dir)

    def run(self, candidates: list[dict[str, Any]]) -> SourceReviewResult:
        review_items: list[dict[str, Any]] = []
        distribution: dict[str, int] = {}
        high_risk: list[str] = []
        seen_titles: set[str] = set()

        for candidate in candidates:
            source_type = classify_source(candidate)
            risks = _risks(candidate, source_type, seen_titles)
            candidate_id = str(candidate.get("candidate_id", ""))
            review_items.append(
                {
                    "candidate_id": candidate_id,
                    "source_type": source_type,
                    "risks": risks,
                    "title": candidate.get("title", ""),
                    "source_url": candidate.get("source_url", ""),
                }
            )
            distribution[source_type] = distribution.get(source_type, 0) + 1
            if len(risks) >= 2 or "low_confidence" in risks:
                high_risk.append(candidate_id)
            title_key = _title_key(str(candidate.get("title", "")))
            if title_key:
                seen_titles.add(title_key)

        result = SourceReviewResult(
            review_items=review_items,
            source_type_distribution=distribution,
            high_risk_candidate_ids=high_risk,
        )
        output_path = self.output_dir / "source_review_report.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result.output_path = str(output_path)
        output_path.write_text(
            json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return result


def classify_source(candidate: dict[str, Any]) -> str:
    text = " ".join(
        str(candidate.get(key, ""))
        for key in ("source_url", "title", "snippet", "source_type")
    ).lower()
    if any(token in text for token in ("arxiv.org", "doi.org", "ieee", "acm.org", "springer", "sciencedirect", "paper")):
        return "paper"
    if any(token in text for token in (".gov", ".edu", "official", "documentation", "docs.")):
        return "official"
    if "github.com" in text:
        return "github"
    if any(token in text for token in ("blog", "medium.com", "substack")):
        return "blog"
    if any(token in text for token in ("news", "reuters", "apnews", "nytimes")):
        return "news"
    return "unknown"


def _risks(candidate: dict[str, Any], source_type: str, seen_titles: set[str]) -> list[str]:
    risks: list[str] = []
    try:
        confidence = float(candidate.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    if confidence < 0.5:
        risks.append("low_confidence")
    if candidate.get("year") in (None, "", "unknown"):
        risks.append("missing_year")
    if not candidate.get("source_url"):
        risks.append("missing_url")
    if source_type == "unknown":
        risks.append("unknown_source_type")
    searchable = " ".join(str(candidate.get(key, "")) for key in ("title", "snippet"))
    if not _has_author_signal(searchable):
        risks.append("missing_author")
    if source_type in {"blog", "github", "news", "unknown"}:
        risks.append("non_academic_source")
    title_key = _title_key(str(candidate.get("title", "")))
    if title_key and title_key in seen_titles:
        risks.append("possible_duplicate")
    return risks


def _has_author_signal(text: str) -> bool:
    return bool(re.search(r"\b[A-Z][a-z]+(?:\s+[A-Z]\.)?\s+[A-Z][a-z]+\b", text))


def _title_key(title: str) -> str:
    return re.sub(r"\s+", " ", title.strip().lower())
