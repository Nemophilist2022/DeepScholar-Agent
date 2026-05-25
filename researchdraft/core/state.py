from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .context import DraftContext


class Stage(str, Enum):
    INIT = "INIT"
    INTERVIEWING = "INTERVIEWING"
    PLANNING = "PLANNING"
    DRAFTING = "DRAFTING"
    WEB_SEARCHING = "WEB_SEARCHING"
    SOURCE_REVIEWING = "SOURCE_REVIEWING"
    HUMAN_REVIEWING = "HUMAN_REVIEWING"
    LITERATURE_REVIEWING = "LITERATURE_REVIEWING"
    CITATION_CHECKING = "CITATION_CHECKING"
    FORMATTING = "FORMATTING"
    VERIFYING = "VERIFYING"
    DONE = "DONE"


@dataclass
class ResearchDraftState:
    stage: Stage = Stage.INIT
    context: DraftContext | None = None
    outline: dict[str, Any] = field(default_factory=dict)
    draft_markdown: str = ""
    draft_path: str = ""
    docx_path: str = ""
    report_path: str = ""
    trace_path: str = ""
    candidate_literature: Any = None
    source_review_report: Any = None
    human_review_result: Any = None
    literature_report: Any = None
    citation_report: Any = None
    verification: Any = None


@dataclass
class RunResult:
    ok: bool
    output_dir: str
    context_path: str
    draft_path: str
    docx_path: str
    report_path: str
    trace_path: str
