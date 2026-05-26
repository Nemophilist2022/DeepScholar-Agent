from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from researchdraft.tools.diff_tools import write_diff_summary


@dataclass
class WorkspaceMaterializationResult:
    root: str
    protocol_path: str
    task_plan_path: str
    claim_map_path: str
    manifest_path: str
    diff_summary_path: str
    evidence_paths: list[str]


class WorkspaceManager:
    def __init__(self, root: str | Path = "workspace") -> None:
        self.root = Path(root)
        self.evidence_dir = self.root / "evidence"
        self.artifacts_dir = self.root / "artifacts"
        self.trace_dir = self.root / "trace"

    def materialize(
        self,
        *,
        context_title: str,
        candidates: list[dict[str, Any]],
        missing_items: list[str],
        confirmation_items: list[str],
        artifact_paths: dict[str, str],
    ) -> WorkspaceMaterializationResult:
        self._ensure_dirs()
        protocol_path = self.root / "protocol.md"
        task_plan_path = self.root / "task_plan.md"
        claim_map_path = self.root / "claim_map.md"
        manifest_path = self.artifacts_dir / "manifest.md"
        diff_summary_path = self.artifacts_dir / "diff_summary.md"

        protocol_path.write_text(_render_protocol(), encoding="utf-8")
        evidence_paths = self._write_evidence_cards(candidates)
        claim_map_path.write_text(
            _render_claim_map(context_title, candidates, missing_items, confirmation_items),
            encoding="utf-8",
        )
        task_plan_path.write_text(
            _render_task_plan(context_title, missing_items, confirmation_items, candidates),
            encoding="utf-8",
        )
        manifest_path.write_text(_render_manifest(artifact_paths, evidence_paths), encoding="utf-8")
        write_diff_summary(
            diff_summary_path,
            tracked_paths=[protocol_path, task_plan_path, claim_map_path, manifest_path, *map(Path, evidence_paths)],
        )
        return WorkspaceMaterializationResult(
            root=str(self.root),
            protocol_path=str(protocol_path),
            task_plan_path=str(task_plan_path),
            claim_map_path=str(claim_map_path),
            manifest_path=str(manifest_path),
            diff_summary_path=str(diff_summary_path),
            evidence_paths=evidence_paths,
        )

    def _ensure_dirs(self) -> None:
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.trace_dir.mkdir(parents=True, exist_ok=True)

    def _write_evidence_cards(self, candidates: list[dict[str, Any]]) -> list[str]:
        for old in self.evidence_dir.glob("evidence_card_*.md"):
            old.unlink()
        paths: list[str] = []
        for index, item in enumerate(candidates, 1):
            cid = item.get("candidate_id") or f"C{index:03d}"
            path = self.evidence_dir / f"evidence_card_{index:03d}.md"
            confidence = float(item.get("confidence", 0.0) or 0.0)
            status = item.get("status", "pending_review")
            risk_flags = item.get("risk_flags") or []
            path.write_text(
                "\n".join(
                    [
                        "---",
                        f"id: {cid}",
                        f"source_url: {item.get('source_url') or item.get('url') or ''}",
                        f"confidence: {confidence:.2f}",
                        f"status: {status}",
                        "---",
                        "",
                        f"# Evidence Card {cid}: {item.get('title', 'Untitled Source')}",
                        "",
                        f"- Snippet: {item.get('snippet', '')}",
                        f"- Risk flags: {', '.join(map(str, risk_flags)) if risk_flags else 'none'}",
                        f"- Review state: {'requires_followup' if status != 'confirmed' or confidence < 0.7 else 'supported'}",
                    ]
                ),
                encoding="utf-8",
            )
            paths.append(str(path))
        return paths


def _render_protocol() -> str:
    return """# Research Protocol

- Do not fabricate authors, venues, DOI, datasets, metrics or experimental results.
- Preserve missing facts as `[待补充：...]` and uncertain facts as `[待确认：...]`.
- Candidate sources must pass human review before entering formal references.
- Use ripgrep/progressive context loading over Markdown workspace files for audit and continuation.
"""


def _render_task_plan(title: str, missing: list[str], confirmations: list[str], candidates: list[dict[str, Any]]) -> str:
    followups = list(missing) + list(confirmations)
    unconfirmed = [c.get("candidate_id", "unknown") for c in candidates if c.get("status") != "confirmed"]
    lines = [
        "# Task Plan",
        "",
        f"Research task: {title or '[untitled]'}",
        "",
        "1. Scope user research question.",
        "2. Plan paper sections and evidence requirements.",
        "3. Explore candidate sources.",
        "4. Extract Evidence Cards.",
        "5. Synthesize controlled draft.",
        "6. Review claim-evidence coverage.",
        "7. Deliver DOCX, report and trace.",
        "",
        "## 补检任务",
    ]
    if not followups and not unconfirmed:
        lines.append("- 无；当前 demo 未发现补检项。")
    for item in followups:
        lines.append(f"- Follow up: {item}")
    for cid in unconfirmed:
        lines.append(f"- Confirm or replace candidate source: {cid}")
    return "\n".join(lines) + "\n"


def _render_claim_map(title: str, candidates: list[dict[str, Any]], missing: list[str], confirmations: list[str]) -> str:
    rows = [
        "# Claim Map",
        "",
        "| Claim | Evidence | Status | Review Note |",
        "|---|---|---|---|",
    ]
    status = "requires_followup" if missing or confirmations else "supported"
    rows.append(f"| {title or 'Research draft'} has traceable delivery artifacts. | artifacts/manifest.md | supported | Trace/report/DOCX are produced. |")
    if candidates:
        first = candidates[0]
        rows.append(f"| Candidate literature supports related-work exploration. | evidence/evidence_card_001.md | requires_followup | {first.get('candidate_id', 'C001')} remains review-dependent. |")
    else:
        rows.append("| Related work requires external support. | none | requires_followup | No candidate evidence exists. |")
    for item in missing + confirmations:
        rows.append(f"| {item} | none | {status} | Needs supplementation or human confirmation. |")
    return "\n".join(rows) + "\n"


def _render_manifest(artifact_paths: dict[str, str], evidence_paths: list[str]) -> str:
    lines = ["# Artifact Manifest", ""]
    for key, value in sorted(artifact_paths.items()):
        digest = _digest(Path(value)) if value and Path(value).exists() else "not_generated"
        lines.append(f"- {key}: `{value}` sha256={digest}")
    lines.append(f"- evidence_cards: {len(evidence_paths)}")
    return "\n".join(lines) + "\n"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]
