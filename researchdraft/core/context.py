from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


LIST_FIELDS = {"method", "metrics", "innovation_points", "output_format", "references"}
REQUIRED_FIELDS = {
    "title",
    "background",
    "research_problem",
    "method",
    "dataset",
    "metrics",
    "innovation_points",
    "references",
}


@dataclass
class DraftContext:
    title: str = ""
    background: str = ""
    research_problem: str = ""
    method: list[str] = field(default_factory=list)
    dataset: str = ""
    metrics: list[str] = field(default_factory=list)
    innovation_points: list[str] = field(default_factory=list)
    paper_type: str = "short_paper"
    output_format: list[str] = field(default_factory=lambda: ["docx"])
    references: list[dict[str, Any]] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)

    @classmethod
    def from_answers(cls, answers: dict[str, Any]) -> "DraftContext":
        data: dict[str, Any] = {}
        for key in (
            "title",
            "background",
            "research_problem",
            "dataset",
            "paper_type",
        ):
            data[key] = _clean_scalar(answers.get(key, ""))
        for key in LIST_FIELDS:
            if key == "references":
                data[key] = _parse_references(answers.get(key, ""))
            else:
                data[key] = _split_list(answers.get(key, ""))

        if not data["paper_type"]:
            data["paper_type"] = "short_paper"
        if not data["output_format"]:
            data["output_format"] = ["docx"]

        ctx = cls(**data)
        ctx.missing_fields = ctx.compute_missing_fields()
        return ctx

    def compute_missing_fields(self) -> list[str]:
        missing: list[str] = []
        for key in REQUIRED_FIELDS:
            value = getattr(self, key)
            is_missing = len(value) == 0 if isinstance(value, list) else not str(value).strip()
            if is_missing:
                missing.append(key)
        return sorted(missing)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def save_json(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def reference_raw_text(reference: str | dict[str, Any]) -> str:
    if isinstance(reference, dict):
        return str(reference.get("raw_text", "")).strip()
    return str(reference or "").strip()


def reference_year(reference: str | dict[str, Any]) -> int | None:
    if isinstance(reference, dict):
        year = reference.get("year")
        return int(year) if isinstance(year, int) else None
    return _extract_year(str(reference))


def _clean_scalar(value: Any) -> str:
    return str(value or "").strip()


def _split_list(value: Any) -> list[str]:
    if isinstance(value, list):
        raw_items = [str(v) for v in value]
    else:
        raw_items = re.split(r"[,，;；\n]+", str(value or ""))
    return [item.strip() for item in raw_items if item.strip()]


def _parse_references(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        raw_items = value
    else:
        raw_items = re.split(r"[;；\n]+", str(value or ""))

    references: list[dict[str, Any]] = []
    for item in raw_items:
        if isinstance(item, dict):
            raw_text = _clean_scalar(item.get("raw_text") or item.get("text") or "")
            if not raw_text:
                continue
            references.append(
                {
                    "raw_text": raw_text,
                    "year": _coerce_year(item.get("year")) or _extract_year(raw_text),
                    "source_type": item.get("source_type") or _infer_source_type(raw_text),
                    "source_url": item.get("source_url", ""),
                    "candidate_id": item.get("candidate_id", ""),
                    "is_confirmed": bool(item.get("is_confirmed", False)),
                    "confirmed_by_user": bool(item.get("confirmed_by_user", False)),
                }
            )
        else:
            raw_text = _clean_scalar(item)
            if not raw_text:
                continue
            references.append(
                {
                    "raw_text": raw_text,
                    "year": _extract_year(raw_text),
                    "source_type": _infer_source_type(raw_text),
                    "source_url": "",
                    "candidate_id": "",
                    "is_confirmed": False,
                    "confirmed_by_user": False,
                }
            )
    return references


def _extract_year(text: str) -> int | None:
    match = re.search(r"\b(19|20)\d{2}\b", text)
    return int(match.group(0)) if match else None


def _coerce_year(value: Any) -> int | None:
    try:
        year = int(value)
    except (TypeError, ValueError):
        return None
    return year if 1900 <= year <= 2100 else None


def _infer_source_type(text: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ("journal", "transactions", "学报", "期刊")):
        return "journal"
    if any(word in lowered for word in ("conference", "proceedings", "会议")):
        return "conference"
    if any(word in lowered for word in ("book", "press", "出版社", "专著")):
        return "book"
    if any(word in lowered for word in ("arxiv", "preprint", "预印本")):
        return "preprint"
    return "unknown"
