from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from researchdraft.config.research_config import ResearchConfig
from researchdraft.tools.search_providers import FallbackMockSearchProvider, SearchProvider, coerce_search_result, provider_from_env


@dataclass(frozen=True)
class DeepSearchResult:
    result_id: str
    title: str
    url: str
    snippet: str
    provider: str
    raw: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FetchedDocument:
    result_id: str
    title: str
    url: str
    content: str
    source_type: str = "web"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SearchFetchProvider:
    """Search/fetch split inspired by public Deep Research tool contracts.

    The implementation is intentionally lightweight: search delegates to the
    existing SearchProvider abstraction; fetch turns a selected result into a
    bounded document payload that downstream evidence extraction can cite.
    """

    def __init__(self, *, provider: SearchProvider | None = None, config: ResearchConfig | None = None) -> None:
        self.config = config or ResearchConfig.default()
        self.provider = provider or provider_from_env(fallback_provider=FallbackMockSearchProvider())

    def search(self, query: str, *, max_results: int | None = None) -> list[DeepSearchResult]:
        limit = max_results or self.config.max_sources
        raw_results = list(self.provider.search(query, max_results=limit))
        while len(raw_results) < limit:
            raw_results.append(
                {
                    "title": f"Candidate source for {query} #{len(raw_results) + 1}",
                    "url": f"https://example.org/deep-search/{len(raw_results) + 1}",
                    "snippet": f"Fallback fetched candidate for {query}.",
                    "provider": "fallback_mock",
                }
            )
        results: list[DeepSearchResult] = []
        for index, item in enumerate(raw_results[:limit], 1):
            result = coerce_search_result(item, provider=getattr(self.provider, "provider_name", "unknown"))
            results.append(
                DeepSearchResult(
                    result_id=f"R{index:03d}",
                    title=result.title,
                    url=result.url,
                    snippet=result.snippet,
                    provider=result.provider,
                    raw=result.to_dict(),
                )
            )
        return results

    def fetch(self, result: DeepSearchResult | dict[str, Any]) -> FetchedDocument:
        if isinstance(result, dict):
            result = DeepSearchResult(**result)
        content = (
            f"Title: {result.title}\n"
            f"URL: {result.url}\n"
            f"Snippet: {result.snippet}\n\n"
            "Fetched content is represented as a bounded source packet for the MVP. "
            "A production adapter can replace this method with real web/file fetch."
        )
        return FetchedDocument(
            result_id=result.result_id,
            title=result.title,
            url=result.url,
            content=content[: self.config.fetch_max_chars],
        )

    def search_and_fetch(self, query: str, *, max_results: int | None = None) -> list[FetchedDocument]:
        return [self.fetch(result) for result in self.search(query, max_results=max_results)]
