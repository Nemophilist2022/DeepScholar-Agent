from __future__ import annotations

from pathlib import Path
from typing import Any

from researchdraft.core.context import DraftContext
from researchdraft.tools.draft_tools import missing_marker


REQUIRED_SECTIONS = [
    "摘要",
    "关键词",
    "引言",
    "相关工作",
    "方法",
    "实验与结果分析",
    "结论",
    "参考文献",
]


class PlanningAgent:
    def __init__(
        self,
        template_path: str | Path = "researchdraft/templates/paper_outline.yaml",
    ) -> None:
        self.template_path = Path(template_path)

    def run(self, ctx: DraftContext) -> dict[str, Any]:
        sections = self._load_sections()
        return {
            "title": ctx.title or missing_marker("title"),
            "paper_type": ctx.paper_type,
            "sections": [
                {
                    "title": name,
                    "goals": self._goals_for(name, ctx),
                }
                for name in sections
            ],
        }

    def _load_sections(self) -> list[str]:
        if not self.template_path.exists():
            return REQUIRED_SECTIONS
        text = self.template_path.read_text("utf-8")
        parsed = _parse_sections_from_simple_yaml(text)
        return parsed or REQUIRED_SECTIONS

    @staticmethod
    def _goals_for(name: str, ctx: DraftContext) -> list[str]:
        if name == "摘要":
            return ["概述背景、问题、方法和贡献；缺失信息显式标记。"]
        if name == "关键词":
            return ["从方法模块和创新点抽取关键词；不足时标记待补充。"]
        if name == "方法":
            return ctx.method or [missing_marker("method")]
        if name == "实验与结果分析":
            return ["只描述用户提供的数据集、材料和指标；不编造结果、规模或数值。"]
        if name == "参考文献":
            return [
                ref.get("raw_text", str(ref)) if isinstance(ref, dict) else str(ref)
                for ref in ctx.references
            ] or [missing_marker("references")]
        problem = ctx.research_problem or missing_marker("research_problem")
        return [f"围绕“{problem}”展开，未确认事实保留标记。"]


def _parse_sections_from_simple_yaml(text: str) -> list[str]:
    sections: list[str] = []
    in_sections = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "sections:":
            in_sections = True
            continue
        if in_sections and line.startswith("- "):
            value = line[2:].strip().strip("\"'")
            if value:
                sections.append(value)
            continue
        if in_sections and not raw.startswith((" ", "\t", "-")):
            break
    return sections
