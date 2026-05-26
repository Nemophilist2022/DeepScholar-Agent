from __future__ import annotations


def run_bad_case_replay() -> dict:
    claims = [
        {"id": "BC001", "text": "The system improves citation coverage by 95%.", "evidence": ""},
        {"id": "BC002", "text": "The delivery chain writes trace artifacts.", "evidence": "trace.json"},
    ]
    unsupported = [claim for claim in claims if not claim["evidence"]]
    unsupported_rate = round(len(unsupported) / len(claims), 2)
    issues = [f"unsupported_claim:{claim['id']}" for claim in unsupported]
    return {
        "passed": not issues,
        "case_id": "bad_case_unsupported_claim",
        "issues": issues,
        "metrics": {
            "citation_coverage_rate": 0.5,
            "unsupported_claim_rate": unsupported_rate,
            "followup_pass_rate": 0.0,
            "document_delivery_success_rate": 1.0,
        },
        "recommendation": "补检缺失证据，删除或重写 unsupported claim 后再次 replay。",
    }
