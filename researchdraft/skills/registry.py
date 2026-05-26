from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchSkill:
    name: str
    purpose: str
    artifact: str


_SKILLS = [
    ResearchSkill("planning", "Create research plan and section outline", "task_plan.md"),
    ResearchSkill("source_search", "Retrieve candidate sources", "candidate_literature.json"),
    ResearchSkill("evidence_extract", "Convert candidates into Evidence Cards", "workspace/evidence/*.md"),
    ResearchSkill("citation_check", "Check citation/reference consistency", "quality_report.md"),
    ResearchSkill("report_synthesis", "Synthesize controlled Markdown draft", "draft.md"),
    ResearchSkill("docx_delivery", "Deliver formatted DOCX artifact", "paper.docx"),
]


def list_research_skills() -> list[ResearchSkill]:
    return list(_SKILLS)
