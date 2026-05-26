from __future__ import annotations

import os
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ResearchConfig:
    max_research_loops: int = 2
    max_sources: int = 5
    report_style: str = "paper"
    search_provider: str = "fallback_mock"
    fetch_max_chars: int = 1600
    workflow: str = "scope-plan-search-fetch-evaluate-deliver"

    @classmethod
    def default(cls) -> "ResearchConfig":
        return cls(
            max_research_loops=int(os.getenv("DEEPSCHOLAR_MAX_RESEARCH_LOOPS", "2")),
            max_sources=int(os.getenv("DEEPSCHOLAR_MAX_SOURCES", "5")),
            report_style=os.getenv("DEEPSCHOLAR_REPORT_STYLE", "paper"),
            search_provider=os.getenv("RESEARCHDRAFT_SEARCH_PROVIDER", "fallback_mock") or "fallback_mock",
            fetch_max_chars=int(os.getenv("DEEPSCHOLAR_FETCH_MAX_CHARS", "1600")),
        )

    def to_dict(self) -> dict:
        return asdict(self)
