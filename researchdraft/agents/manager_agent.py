from __future__ import annotations

from pathlib import Path
from typing import Callable

from researchdraft.agents.citation_agent import CitationAgent
from researchdraft.agents.human_review_gate import HumanReviewGate
from researchdraft.agents.interview_agent import InterviewAgent
from researchdraft.agents.literature_agent import LiteratureAgent
from researchdraft.agents.literature_search_agent import LiteratureSearchAgent
from researchdraft.agents.planning_agent import PlanningAgent
from researchdraft.agents.source_review_agent import SourceReviewAgent
from researchdraft.agents.verifier_agent import VerifierAgent
from researchdraft.agents.word_format_agent import WordFormatAgent
from researchdraft.agents.writing_agent import WritingAgent
from researchdraft.core.state import ResearchDraftState, RunResult, Stage
from researchdraft.core.trace import TraceRecorder
from researchdraft.workspace.manager import WorkspaceManager


class ResearchManagerAgent:
    def __init__(
        self,
        *,
        output_dir: str | Path = "researchdraft/outputs",
        input_fn: Callable[[str], str] = input,
        llm_client=None,
        search_provider=None,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.input_fn = input_fn
        self.llm_client = llm_client
        self.search_provider = search_provider
        self.state = ResearchDraftState()
        self.trace = TraceRecorder(self.output_dir / "trace.jsonl")
        self.state.trace_path = str(self.trace.path)

    def run(self) -> RunResult:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._run_interview()
        self._run_planning()
        self._run_drafting()
        self._run_web_searching()
        self._run_source_reviewing()
        self._run_human_reviewing()
        self._run_drafting(task_id="drafting-after-human-review")
        self._run_literature_reviewing()
        self._run_citation_checking()
        self._run_formatting()
        self._run_verifying()
        if self.state.verification and self.state.verification.has_format_problem:
            self._run_formatting(task_id="formatting-retry")
            self._run_verifying(task_id="verifying-retry")
        self._run_workspace_materialization()
        self.state.stage = Stage.DONE
        json_trace_path = self.trace.write_json(self.output_dir / "trace.json")
        self.state.trace_path = json_trace_path
        return RunResult(
            ok=True,
            output_dir=str(self.output_dir),
            context_path=str(self.output_dir / "draft_context.json"),
            draft_path=self.state.draft_path,
            docx_path=self.state.docx_path,
            report_path=self.state.report_path,
            trace_path=self.state.trace_path,
        )

    def _run_interview(self) -> None:
        self.state.stage = Stage.INTERVIEWING
        ctx = InterviewAgent(output_dir=self.output_dir, input_fn=self.input_fn).run()
        self.state.context = ctx
        self.trace.record(
            task_id="interview",
            agent="InterviewAgent",
            stage=self.state.stage.value,
            input_keys=[],
            output_keys=["context", "draft_context.json"],
            tool_call="fixed_questionnaire",
        )

    def _run_planning(self) -> None:
        self.state.stage = Stage.PLANNING
        assert self.state.context is not None
        self.state.outline = PlanningAgent().run(self.state.context)
        self.trace.record(
            task_id="planning",
            agent="PlanningAgent",
            stage=self.state.stage.value,
            input_keys=["context"],
            output_keys=["outline"],
            tool_call="paper_outline.yaml",
        )

    def _run_drafting(self, task_id: str = "drafting") -> None:
        self.state.stage = Stage.DRAFTING
        assert self.state.context is not None
        draft = WritingAgent(llm_client=self.llm_client).run(
            self.state.context, self.state.outline
        )
        draft_path = self.output_dir / "draft.md"
        draft_path.write_text(draft, encoding="utf-8")
        self.state.draft_markdown = draft
        self.state.draft_path = str(draft_path)
        self.state.context.save_json(self.output_dir / "draft_context.json")
        self.trace.record(
            task_id=task_id,
            agent="WritingAgent",
            stage=self.state.stage.value,
            input_keys=["context", "outline"],
            output_keys=["draft_markdown", "draft.md", "draft_context.json"],
            tool_call="llm_optional_or_template",
        )

    def _run_web_searching(self) -> None:
        self.state.stage = Stage.WEB_SEARCHING
        assert self.state.context is not None
        extra_keywords = self._optional_input("请输入额外文献搜索关键词（可直接回车跳过）：")
        result = LiteratureSearchAgent(
            output_dir=self.output_dir,
            search_provider=self.search_provider,
        ).run(self.state.context, extra_keywords=extra_keywords)
        self.state.candidate_literature = result
        self.trace.record(
            task_id="web-searching",
            agent="LiteratureSearchAgent",
            stage=self.state.stage.value,
            input_keys=["context", "extra_keywords"],
            output_keys=[
                "candidate_literature",
                "candidate_literature.json",
                "search_cache.json",
            ],
            tool_call=(
                "web_search_provider_or_fallback "
                f"provider={result.provider} "
                f"queries={len(result.queries)} "
                f"raw_result_count={result.raw_result_count} "
                f"deduped_result_count={result.deduped_result_count} "
                f"cache_hit={result.cache_hit} "
                f"fallback_used={result.fallback_used}"
            ),
            status="ok" if result.candidates else "partial",
            failure_reason=result.failure_reason or ("" if result.candidates else "未获得候选文献"),
        )

    def _run_source_reviewing(self) -> None:
        self.state.stage = Stage.SOURCE_REVIEWING
        candidates = self.state.candidate_literature.candidates if self.state.candidate_literature else []
        result = SourceReviewAgent(output_dir=self.output_dir).run(candidates)
        self.state.source_review_report = result
        self.trace.record(
            task_id="source-reviewing",
            agent="SourceReviewAgent",
            stage=self.state.stage.value,
            input_keys=["candidate_literature"],
            output_keys=["source_review_report", "source_review_report.json"],
            tool_call="review_candidate_sources",
        )

    def _run_human_reviewing(self) -> None:
        self.state.stage = Stage.HUMAN_REVIEWING
        assert self.state.context is not None
        candidates = self.state.candidate_literature.candidates if self.state.candidate_literature else []
        result = HumanReviewGate(
            input_fn=lambda prompt: self._optional_input(prompt, default="skip")
        ).run(self.state.context, candidates)
        self.state.human_review_result = result
        self.state.context.save_json(self.output_dir / "draft_context.json")
        self.trace.record(
            task_id="human-reviewing",
            agent="HumanReviewGate",
            stage=self.state.stage.value,
            input_keys=["candidate_literature", "user_selection"],
            output_keys=["human_review_result", "draft_context.json"],
            tool_call="cli_candidate_confirmation",
            status="skipped" if result.skipped else "ok",
        )

    def _run_literature_reviewing(self) -> None:
        self.state.stage = Stage.LITERATURE_REVIEWING
        assert self.state.context is not None
        result = LiteratureAgent().run(self.state.context)
        self.state.literature_report = result
        self.trace.record(
            task_id="literature-reviewing",
            agent="LiteratureAgent",
            stage=self.state.stage.value,
            input_keys=["context.references", "context.method", "context.innovation_points"],
            output_keys=["literature_report"],
            tool_call="analyze_literature_needs",
        )

    def _run_citation_checking(self) -> None:
        self.state.stage = Stage.CITATION_CHECKING
        assert self.state.context is not None
        result = CitationAgent().run(
            draft_markdown=self.state.draft_markdown,
            draft_context=self.state.context,
        )
        self.state.citation_report = result
        if result.needs_source_marker and "[待补充：引用来源]" not in self.state.draft_markdown:
            self.state.draft_markdown = (
                self.state.draft_markdown.rstrip()
                + "\n\n## 引用一致性标记\n[待补充：引用来源]\n"
            )
            Path(self.state.draft_path).write_text(self.state.draft_markdown, encoding="utf-8")
        self.trace.record(
            task_id="citation-checking",
            agent="CitationAgent",
            stage=self.state.stage.value,
            input_keys=["draft_markdown", "context.references"],
            output_keys=["citation_report", "draft.md"],
            tool_call="check_citation_consistency",
            status="issues_found" if result.needs_source_marker else "ok",
            failure_reason="引用来源缺失" if result.needs_source_marker else "",
        )

    def _run_formatting(self, task_id: str = "formatting") -> None:
        self.state.stage = Stage.FORMATTING
        docx_path, tool_results = WordFormatAgent(output_dir=self.output_dir).run(
            self.state.draft_markdown
        )
        self.state.docx_path = docx_path
        tool_call = ", ".join(result["tool"] for result in tool_results)
        status = "ok" if all(result["ok"] for result in tool_results) else "partial"
        failure_reason = "; ".join(
            result["message"] for result in tool_results if not result["ok"]
        )
        self.trace.record(
            task_id=task_id,
            agent="WordFormatAgent",
            stage=self.state.stage.value,
            input_keys=["draft_markdown"],
            output_keys=["docx_path"],
            tool_call=tool_call,
            status=status,
            failure_reason=failure_reason,
        )

    def _run_verifying(self, task_id: str = "verifying") -> None:
        self.state.stage = Stage.VERIFYING
        self.trace.write_json(self.output_dir / "trace.json")
        entry = self.trace.record(
            task_id=task_id,
            agent="VerifierAgent",
            stage=self.state.stage.value,
            input_keys=[
                "draft_markdown",
                "docx_path",
                "trace_entries",
                "citation_report",
                "literature_report",
                "candidate_literature",
                "source_review_report",
                "human_review_result",
            ],
            output_keys=["quality_report.md", "verification"],
            tool_call="verify_content_web_literature_citation_and_format",
            status="ok",
        )
        result = VerifierAgent(output_dir=self.output_dir).run(
            draft_markdown=self.state.draft_markdown,
            docx_path=self.state.docx_path,
            trace_entries=list(self.trace.entries),
            draft_context=self.state.context,
            draft_path=self.state.draft_path,
            citation_report=self.state.citation_report,
            literature_report=self.state.literature_report,
            candidate_literature=self.state.candidate_literature,
            source_review_report=self.state.source_review_report,
            human_review_result=self.state.human_review_result,
        )
        self.state.verification = result
        self.state.report_path = result.report_path
        entry.status = "ok" if not result.has_problem else "issues_found"
        entry.failure_reason = _verification_failure_reason(result)
        self.trace.rewrite_jsonl()
        self.trace.write_json(self.output_dir / "trace.json")

    def _run_workspace_materialization(self) -> None:
        candidates = (
            self.state.candidate_literature.candidates
            if self.state.candidate_literature
            else []
        )
        missing = (
            self.state.verification.missing_items
            if self.state.verification
            else []
        )
        confirmations = (
            self.state.verification.confirmation_items
            if self.state.verification
            else []
        )
        title = self.state.context.title if self.state.context else ""
        result = WorkspaceManager("workspace").materialize(
            context_title=title,
            candidates=candidates,
            missing_items=missing,
            confirmation_items=confirmations,
            artifact_paths={
                "draft": self.state.draft_path,
                "docx": self.state.docx_path,
                "report": self.state.report_path,
                "trace": self.state.trace_path,
            },
        )
        self.trace.record(
            task_id="workspace-materialization",
            agent="ArtifactSubagent",
            stage=Stage.DONE.value,
            input_keys=["candidate_literature", "verification", "artifact_paths"],
            output_keys=[
                "workspace/protocol.md",
                "workspace/task_plan.md",
                "workspace/claim_map.md",
                "workspace/artifacts/manifest.md",
                "workspace/artifacts/diff_summary.md",
            ],
            tool_call=f"markdown_workspace_materialize evidence_cards={len(result.evidence_paths)} handoff=LeadResearchAgent->ArtifactSubagent",
        )
        self.trace.rewrite_jsonl()
        self.trace.write_json(self.output_dir / "trace.json")

    def _optional_input(self, prompt: str, *, default: str = "") -> str:
        try:
            return self.input_fn(prompt)
        except (EOFError, StopIteration):
            return default


def _verification_failure_reason(result) -> str:
    failed = [
        check.name
        for check in (
            result.file_checks
            + result.structure_checks
            + result.trace_checks
            + result.format_checks
        )
        if not check.passed
    ]
    return "；".join(failed)
