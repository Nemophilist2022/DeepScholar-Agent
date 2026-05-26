from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class EvaluationResult:
    metrics: dict[str, float]
    issues: list[str]
    report_markdown: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_claims(*, claims: list[dict[str, Any]], evidence_cards: list[dict[str, Any]]) -> EvaluationResult:
    evidence_by_id = {str(card.get("id")): card for card in evidence_cards}
    issues: list[str] = []
    supported = 0
    low_confidence = 0
    unconfirmed = 0

    for claim in claims:
        cid = str(claim.get("id") or "unknown")
        evidence_id = str(claim.get("evidence_id") or "")
        card = evidence_by_id.get(evidence_id)
        if not evidence_id or card is None:
            issues.append(f"unsupported_claim:{cid}")
            continue
        confidence = float(card.get("confidence", 0.0) or 0.0)
        status = str(card.get("status", "pending_review"))
        if confidence < 0.7:
            low_confidence += 1
            issues.append(f"low_confidence_evidence:{cid}->{evidence_id}")
        if status not in {"confirmed", "supported"}:
            unconfirmed += 1
            issues.append(f"unconfirmed_evidence:{cid}->{evidence_id}")
        if confidence >= 0.7 and status in {"confirmed", "supported"}:
            supported += 1

    claim_count = len(claims)
    unsupported = len([issue for issue in issues if issue.startswith("unsupported_claim")])
    metrics = {
        "claim_count": float(claim_count),
        "supported_claim_count": float(supported),
        "citation_coverage_rate": round((claim_count - unsupported) / claim_count, 2) if claim_count else 1.0,
        "unsupported_claim_rate": round(unsupported / claim_count, 2) if claim_count else 0.0,
        "low_confidence_evidence_count": float(low_confidence),
        "unconfirmed_evidence_count": float(unconfirmed),
    }
    report = _render_report(metrics, issues)
    return EvaluationResult(metrics=metrics, issues=issues, report_markdown=report)


def _render_report(metrics: dict[str, float], issues: list[str]) -> str:
    lines = ["# Deep Research Evaluation", ""]
    for key, value in metrics.items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Issues")
    if issues:
        lines.extend(f"- {issue}" for issue in issues)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"
