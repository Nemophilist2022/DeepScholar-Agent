from __future__ import annotations

import re
from typing import Any

from researchdraft.tools.search_providers import SearchResult


ACADEMIC_TYPES = {"paper"}


def normalize_search_result(
    result: SearchResult,
    *,
    query: str,
    candidate_id: str,
    keywords: list[str],
) -> dict[str, Any]:
    searchable = " ".join([result.title, result.snippet, result.url])
    year = _coerce_year(result.year) or _extract_year(searchable) or "unknown"
    source_type = _classify_source(result)
    possible_venue = _extract_possible_venue(searchable, source_type)
    is_academic_like = source_type in ACADEMIC_TYPES
    risk_flags = _risk_flags(result, year, source_type)
    candidate = {
        "candidate_id": candidate_id,
        "title": result.title or "[待确认：候选文献标题]",
        "source_url": result.url,
        "snippet": result.snippet,
        "year": year,
        "source_type": source_type,
        "possible_venue": possible_venue,
        "is_academic_like": is_academic_like,
        "risk_flags": risk_flags,
        "provider": result.provider,
        "query": query,
        "confidence": 0.0,
        "status": "pending_review",
        "raw": result.raw,
    }
    candidate["confidence"] = score_candidate(candidate, keywords=keywords)
    return candidate


def rank_candidates(candidates: list[dict[str, Any]], *, keywords: list[str]) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for candidate in candidates:
        item = dict(candidate)
        item["confidence"] = score_candidate(item, keywords=keywords)
        ranked.append(item)
    ranked.sort(key=lambda item: float(item.get("confidence", 0.0)), reverse=True)
    return ranked


def score_candidate(candidate: dict[str, Any], *, keywords: list[str]) -> float:
    text = " ".join(
        str(candidate.get(key, ""))
        for key in ("title", "snippet", "source_url")
    ).lower()
    tokens = [token.lower() for token in keywords if token.strip()]
    if tokens:
        match_count = sum(1 for token in tokens if token in text)
        score = 0.2 + min(0.35, match_count / max(len(tokens), 1) * 0.35)
    else:
        score = 0.2
    if candidate.get("source_type") in ACADEMIC_TYPES or candidate.get("is_academic_like"):
        score += 0.25
    year = candidate.get("year")
    if isinstance(year, int) and year >= 2024:
        score += 0.15
    if candidate.get("source_url"):
        score += 0.05
    if candidate.get("risk_flags"):
        score -= min(0.2, 0.05 * len(candidate["risk_flags"]))
    return round(max(0.0, min(1.0, score)), 3)


def dedupe_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    deduped: list[dict[str, Any]] = []
    for candidate in candidates:
        key = (
            re.sub(r"\s+", " ", str(candidate.get("title", "")).strip().lower()),
            str(candidate.get("source_url", "")).strip().lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(candidate)
    return deduped


def extract_keywords_from_context(ctx, extra_keywords: str = "") -> list[str]:
    values: list[str] = []
    values.append(getattr(ctx, "title", ""))
    values.append(getattr(ctx, "research_problem", ""))
    values.append(getattr(ctx, "dataset", ""))
    values.extend(getattr(ctx, "method", []) or [])
    values.extend(getattr(ctx, "innovation_points", []) or [])
    values.extend(_split_keywords(extra_keywords))
    tokens: list[str] = []
    lowered_seen: set[str] = set()
    for value in values:
        for token in _keyword_tokens(str(value)):
            key = token.lower()
            if key not in lowered_seen:
                lowered_seen.add(key)
                tokens.append(token)
    return tokens[:12]


def _classify_source(result: SearchResult) -> str:
    declared = str(result.source_type or "").strip().lower()
    text = " ".join([declared, result.title, result.snippet, result.url]).lower()
    if any(token in text for token in ("arxiv.org", "doi.org", "ieee", "acm.org", "springer", "sciencedirect", "paper", "journal", "conference", "proceedings")):
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


def _risk_flags(result: SearchResult, year: int | str, source_type: str) -> list[str]:
    risks: list[str] = []
    if not result.url:
        risks.append("missing_url")
    if year == "unknown":
        risks.append("missing_year")
    if source_type == "unknown":
        risks.append("unknown_source_type")
    if source_type in {"blog", "github", "news", "unknown"}:
        risks.append("non_academic_source")
    return risks


def _extract_possible_venue(text: str, source_type: str) -> str:
    lowered = text.lower()
    if "arxiv.org" in lowered:
        return "arXiv"
    if "ieee" in lowered:
        return "IEEE"
    if "acm.org" in lowered:
        return "ACM"
    if "springer" in lowered:
        return "Springer"
    if source_type == "unknown":
        return "unknown"
    return source_type


def _extract_year(text: str) -> int | None:
    match = re.search(r"\b(19|20)\d{2}\b", text)
    return int(match.group(0)) if match else None


def _coerce_year(value: Any) -> int | None:
    try:
        year = int(value)
    except (TypeError, ValueError):
        return None
    return year if 1900 <= year <= 2100 else None


def _split_keywords(value: str) -> list[str]:
    return [item.strip() for item in re.split(r"[,，;；\n]+", value) if item.strip()]


def _keyword_tokens(value: str) -> list[str]:
    return [token for token in re.split(r"[^A-Za-z0-9\u4e00-\u9fff]+", value) if len(token) >= 2]
