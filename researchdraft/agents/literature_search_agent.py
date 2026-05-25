from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from researchdraft.core.context import DraftContext
from researchdraft.tools.candidate_tools import (
    dedupe_candidates,
    extract_keywords_from_context,
    normalize_search_result,
    rank_candidates,
)
from researchdraft.tools.search_providers import (
    FallbackMockSearchProvider,
    SearchProvider,
    coerce_search_result,
    provider_from_env,
    search_provider_metadata,
)


@dataclass
class CandidateLiteratureResult:
    queries: list[str] = field(default_factory=list)
    candidates: list[dict[str, Any]] = field(default_factory=list)
    provider: str = "unknown"
    raw_result_count: int = 0
    deduped_result_count: int = 0
    cache_hit: bool = False
    fallback_used: bool = False
    failure_reason: str = ""
    output_path: str = ""
    cache_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LiteratureSearchAgent:
    def __init__(
        self,
        *,
        output_dir: str | Path = "researchdraft/outputs",
        search_provider: SearchProvider | None = None,
        per_query_limit: int = 3,
        force_refresh: bool | None = None,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.search_provider = search_provider or provider_from_env(
            fallback_provider=FallbackMockSearchProvider()
        )
        self.per_query_limit = per_query_limit
        env_refresh = os.getenv("RESEARCHDRAFT_SEARCH_FORCE_REFRESH", "").lower()
        self.force_refresh = force_refresh if force_refresh is not None else env_refresh in {"1", "true", "yes"}

    def run(self, ctx: DraftContext, *, extra_keywords: str = "") -> CandidateLiteratureResult:
        queries = build_search_queries(ctx, extra_keywords=extra_keywords)
        keywords = extract_keywords_from_context(ctx, extra_keywords)
        cache_path = self.output_dir / "search_cache.json"
        cache = _read_cache(cache_path)
        raw_results: list[tuple[str, dict[str, Any]]] = []
        cache_hit = False

        for query in queries:
            cached = cache.get(query)
            if cached and not self.force_refresh:
                cache_hit = True
                for item in cached.get("results", []):
                    raw_results.append((query, item))
                continue

            results = self._provider_search(query)
            result_dicts = [result.to_dict() for result in results]
            cache[query] = {
                "provider": _provider_name(self.search_provider),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "results": result_dicts,
            }
            for item in result_dicts:
                raw_results.append((query, item))

        candidates: list[dict[str, Any]] = []
        for index, (query, raw) in enumerate(raw_results, 1):
            result = coerce_search_result(raw, provider=raw.get("provider", _provider_name(self.search_provider)))
            candidates.append(
                normalize_search_result(
                    result,
                    query=query,
                    candidate_id=f"C{index:03d}",
                    keywords=keywords,
                )
            )

        deduped = dedupe_candidates(candidates)
        ranked = rank_candidates(deduped, keywords=keywords)
        for index, candidate in enumerate(ranked, 1):
            candidate["candidate_id"] = f"C{index:03d}"
            candidate["status"] = "pending_review"

        metadata = search_provider_metadata(self.search_provider)
        fallback_used = bool(metadata["fallback_used"]) or any(
            candidate.get("provider") == "fallback_mock" for candidate in ranked
        )
        result = CandidateLiteratureResult(
            queries=queries,
            candidates=ranked,
            provider=metadata["provider"],
            raw_result_count=len(raw_results),
            deduped_result_count=len(ranked),
            cache_hit=cache_hit,
            fallback_used=fallback_used,
            failure_reason=metadata["failure_reason"],
            cache_path=str(cache_path),
        )

        self.output_dir.mkdir(parents=True, exist_ok=True)
        _write_cache(cache_path, cache)
        output_path = self.output_dir / "candidate_literature.json"
        result.output_path = str(output_path)
        output_path.write_text(
            json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return result

    def _provider_search(self, query: str):
        try:
            results = self.search_provider.search(query, max_results=self.per_query_limit)
        except TypeError:
            results = self.search_provider.search(query, limit=self.per_query_limit)
        return [
            coerce_search_result(item, provider=_provider_name(self.search_provider))
            for item in results
        ]


def build_search_queries(ctx: DraftContext, *, extra_keywords: str = "") -> list[str]:
    seeds: list[str] = []
    for value in [ctx.title, ctx.research_problem, ctx.dataset]:
        if value and value.strip():
            seeds.append(value.strip())
    seeds.extend(item.strip() for item in ctx.method if item.strip())
    seeds.extend(item.strip() for item in ctx.innovation_points if item.strip())
    if extra_keywords.strip():
        seeds.extend(_split_keywords(extra_keywords))

    queries: list[str] = []
    seen: set[str] = set()
    for seed in seeds:
        query = f"{seed} literature review paper"
        if query.lower() not in seen:
            seen.add(query.lower())
            queries.append(query)
        if len(queries) >= 5:
            break
    if not queries:
        queries.append("research paper literature review")
    return queries


def _read_cache(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_cache(path: Path, cache: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def _split_keywords(value: str) -> list[str]:
    return [item.strip() for item in re.split(r"[,，;；\n]+", value) if item.strip()]


def _provider_name(provider: Any) -> str:
    return str(getattr(provider, "provider_name", provider.__class__.__name__))
