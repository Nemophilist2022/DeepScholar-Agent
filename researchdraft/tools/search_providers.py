from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol
from urllib.error import URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


@dataclass
class SearchResult:
    title: str
    url: str = ""
    snippet: str = ""
    year: int | str = "unknown"
    source_type: str = "unknown"
    provider: str = "unknown"
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SearchProvider(Protocol):
    provider_name: str

    def search(self, query: str, *, max_results: int = 5) -> list[SearchResult]:
        ...


class FallbackMockSearchProvider:
    provider_name = "fallback_mock"

    def search(self, query: str, *, max_results: int = 5) -> list[SearchResult]:
        return [
            SearchResult(
                title=f"Candidate source for {query}",
                url=f"https://example.org/search?q={_slug(query)}",
                snippet="Fallback candidate only. User confirmation is required before citation use.",
                year="unknown",
                source_type="unknown",
                provider=self.provider_name,
                raw={"fallback": True},
            )
        ][:max_results]


class WebSearchProvider:
    provider_name = "web_search"

    def __init__(
        self,
        *,
        endpoint: str | None = None,
        api_key: str | None = None,
        provider_name: str | None = None,
        fallback_provider: SearchProvider | None = None,
        timeout: float = 8.0,
    ) -> None:
        self.endpoint = endpoint if endpoint is not None else os.getenv("RESEARCHDRAFT_SEARCH_ENDPOINT", "")
        self.api_key = api_key if api_key is not None else os.getenv("RESEARCHDRAFT_SEARCH_API_KEY", "")
        self.provider_name = provider_name or os.getenv("RESEARCHDRAFT_SEARCH_PROVIDER", "web_search")
        self.fallback_provider = fallback_provider or FallbackMockSearchProvider()
        self.timeout = timeout
        self.fallback_used = False
        self.failure_reason = ""

    def search(self, query: str, *, max_results: int = 5) -> list[SearchResult]:
        self.fallback_used = False
        self.failure_reason = ""
        if not self.endpoint or not self.api_key:
            self.fallback_used = True
            self.failure_reason = "missing_endpoint_or_api_key"
            return self._fallback_search(query, max_results=max_results)
        try:
            return self._request_search(query, max_results=max_results)
        except Exception as exc:
            self.fallback_used = True
            self.failure_reason = f"{type(exc).__name__}: {exc}"
            return self._fallback_search(query, max_results=max_results)

    def _request_search(self, query: str, *, max_results: int) -> list[SearchResult]:
        separator = "&" if "?" in self.endpoint else "?"
        url = self.endpoint + separator + urlencode({"q": query, "count": max_results})
        request = Request(url, headers={"Authorization": f"Bearer {self.api_key}"})
        with urlopen(request, timeout=self.timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        items = _extract_items(payload)
        results: list[SearchResult] = []
        for item in items[:max_results]:
            results.append(
                SearchResult(
                    title=str(item.get("title") or item.get("name") or "").strip(),
                    url=str(item.get("url") or item.get("link") or item.get("source_url") or "").strip(),
                    snippet=str(item.get("snippet") or item.get("description") or "").strip(),
                    year=item.get("year", "unknown"),
                    source_type=str(item.get("source_type") or "unknown"),
                    provider=self.provider_name,
                    raw=item,
                )
            )
        return results

    def _fallback_search(self, query: str, *, max_results: int) -> list[SearchResult]:
        try:
            raw_results = self.fallback_provider.search(query, max_results=max_results)
        except TypeError:
            raw_results = self.fallback_provider.search(query, limit=max_results)
        provider_name = getattr(self.fallback_provider, "provider_name", "fallback")
        return [coerce_search_result(item, provider=provider_name) for item in raw_results]


def provider_from_env(*, fallback_provider: SearchProvider | None = None) -> SearchProvider:
    provider = os.getenv("RESEARCHDRAFT_SEARCH_PROVIDER", "").strip().lower()
    endpoint = os.getenv("RESEARCHDRAFT_SEARCH_ENDPOINT", "").strip()
    api_key = os.getenv("RESEARCHDRAFT_SEARCH_API_KEY", "").strip()
    if provider in {"", "mock", "fallback", "fallback_mock"}:
        if endpoint and api_key:
            return WebSearchProvider(fallback_provider=fallback_provider)
        return FallbackMockSearchProvider()
    return WebSearchProvider(fallback_provider=fallback_provider)


def coerce_search_result(item: SearchResult | dict[str, Any], *, provider: str = "unknown") -> SearchResult:
    if isinstance(item, SearchResult):
        return item
    return SearchResult(
        title=str(item.get("title") or item.get("name") or "").strip(),
        url=str(item.get("url") or item.get("source_url") or item.get("link") or "").strip(),
        snippet=str(item.get("snippet") or item.get("description") or "").strip(),
        year=item.get("year", "unknown"),
        source_type=str(item.get("source_type") or "unknown"),
        provider=str(item.get("provider") or provider),
        raw=item.get("raw") if isinstance(item.get("raw"), dict) else dict(item),
    )


def search_provider_metadata(provider: Any) -> dict[str, Any]:
    return {
        "provider": getattr(provider, "provider_name", provider.__class__.__name__),
        "fallback_used": bool(getattr(provider, "fallback_used", False)),
        "failure_reason": str(getattr(provider, "failure_reason", "")),
    }


def _extract_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("results", "items", "webPages"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict) and isinstance(value.get("value"), list):
            return [item for item in value["value"] if isinstance(item, dict)]
    return []


def _slug(value: str) -> str:
    encoded = quote(re.sub(r"\s+", " ", value.strip()))
    return encoded.replace("%20", "+")
