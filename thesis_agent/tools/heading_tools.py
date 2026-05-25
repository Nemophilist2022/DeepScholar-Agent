"""Heading-related tools.

- ``tool_assign_heading_styles``       — auto-promote chapter/section
  paragraphs to Heading{1..4}
- ``tool_renumber_headings``           — fix gaps in heading numbering
- ``tool_normalize_heading_spacing``   — apply space_before / space_after
  per the profile
- ``tool_setup_multilevel_list``       — wire Heading{1..4} into a Word
  multilevel list so editing a heading auto-renumbers downstream
"""

from __future__ import annotations

import json
import re
from typing import Any

from thesis_formatter._common import (
    _ALIGN_MAP,
    apply_paragraph_spacing,
    parse_length,
    set_style_font,
)
from thesis_formatter.headings import (
    auto_assign_heading_styles,
    normalize_heading_spacing,
    renumber_headings,
)
from thesis_formatter.numbering import setup_multilevel_list

from ._legacy import run_legacy
from .base import ToolContext, ToolResult

_INPUT_SCHEMA_EMPTY: dict[str, Any] = {
    "type": "object",
    "properties": {},
    "additionalProperties": False,
}

_INPUT_SCHEMA_PRESERVE_LOOK: dict[str, Any] = {
    "type": "object",
    "properties": {
        "preserve_look": {"type": "boolean", "default": False},
    },
    "additionalProperties": False,
}

_INPUT_SCHEMA_AI_HEADINGS: dict[str, Any] = {
    "type": "object",
    "properties": {
        "confidence_threshold": {"type": "number", "default": 0.7},
        "max_candidates": {"type": "integer", "default": 18},
        "max_text_chars": {"type": "integer", "default": 32},
        "renumber": {"type": "boolean", "default": True},
    },
    "additionalProperties": False,
}

_AI_HEADING_SYSTEM_PROMPT = (
    "You are a conservative thesis heading classifier. Return only JSON "
    "with key items. Each item must contain paragraph_index, level "
    "(1, 2, 3, 4, or null), and confidence (0..1). Do not rewrite or "
    "quote manuscript content."
)


# ---------------------------------------------------------------------------
# tool_ai_classify_headings
# ---------------------------------------------------------------------------

class AIClassifyHeadings:
    name = "tool_ai_classify_headings"
    description = (
        "Use the configured LLM to classify short heading candidates into "
        "Heading1..Heading4, then optionally normalize numeric heading order."
    )
    input_schema = _INPUT_SCHEMA_AI_HEADINGS
    requires: list[str] = []
    idempotent = True

    def run(self, doc, params: dict[str, Any], ctx: ToolContext) -> ToolResult:
        llm = (ctx.runtime or {}).get("llm_client")
        if llm is None:
            return ToolResult(ok=True, message="LLM unavailable; skipped AI heading classification")

        threshold = float(params.get("confidence_threshold", 0.7))
        max_candidates = max(1, min(int(params.get("max_candidates", 18)), 40))
        max_text_chars = max(12, min(int(params.get("max_text_chars", 32)), 60))
        candidates = _heading_candidates(doc, max_candidates, max_text_chars)
        if not candidates:
            return ToolResult(ok=True, message="no heading candidates found")

        prompt = _build_ai_heading_prompt(candidates)
        response = llm.complete(prompt, schema={"system_prompt": _AI_HEADING_SYSTEM_PROMPT})
        items = response.get("items") if isinstance(response, dict) else None
        if not isinstance(items, list):
            return ToolResult(ok=True, message="AI heading classification returned no usable items")

        token = ctx.snapshot_mgr.take(doc, tool_name=self.name) if ctx.snapshot_mgr else None
        try:
            changed = _apply_ai_heading_items(
                doc,
                items,
                confidence_threshold=threshold,
                renumber=bool(params.get("renumber", True)),
            )
        except Exception as exc:
            return ToolResult(ok=False, message=str(exc), rollback_token=token)

        return ToolResult(
            ok=True,
            message=f"AI classified {len(changed)} heading paragraph(s)",
            changed_paragraphs=[{"paragraph_index": i} for i in changed],
            changed_styles=[f"Heading {i}" for i in range(1, 5)] if changed else [],
            warnings=[],
            rollback_token=token,
        )


# ---------------------------------------------------------------------------
# tool_assign_heading_styles (existing)
# ---------------------------------------------------------------------------

class AssignHeadingStyles:
    name = "tool_assign_heading_styles"
    description = (
        "Detect chapter/section paragraphs and apply Heading1..Heading4 "
        "styles. Backs rule heading.h1.style_present."
    )
    input_schema = _INPUT_SCHEMA_PRESERVE_LOOK
    requires: list[str] = []
    idempotent = True

    # KNOWN LIMITATION (C2):
    # The legacy ``auto_assign_heading_styles`` matches chapter headings
    # via a permissive regex (``^第\s*\d+\s*章``) that also matches TOC
    # entries like ``第一章 绪论 ............ 1`` and promotes them to
    # Heading 1. This affects real theses that contain a styled TOC
    # before tool runs. Two safe workarounds for callers:
    #   1. Make sure TOC paragraphs use the ``TOC 1`` style before this
    #      tool runs (legacy auto_assign skips paragraphs that already
    #      have a non-default style).
    #   2. If you control the input text, avoid the ``第N章`` literal
    #      in TOC entries until v0.3 ships a fix.
    # The fix lives in ``thesis_formatter.headings.auto_assign_heading_styles``;
    # touching it would alter behaviour for every existing thesis-format
    # CLI user, so it stays out of the MVP Tool layer.

    def run(self, doc, params: dict[str, Any], ctx: ToolContext) -> ToolResult:
        token = ctx.snapshot_mgr.take(doc, tool_name=self.name) if ctx.snapshot_mgr else None
        try:
            return self._run_inner(doc, params, ctx, token)
        except Exception as exc:
            return ToolResult(ok=False, message=str(exc), rollback_token=token)

    def _run_inner(self, doc, params, ctx, token) -> ToolResult:
        cfg = ctx.config or {}
        preserve_look = bool(params.get("preserve_look", False))
        with doc.write() as writer:
            raw_doc = writer.raw
            changes = auto_assign_heading_styles(
                raw_doc, cfg, preserve_look=preserve_look
            )
            for i, para in enumerate(raw_doc.paragraphs):
                if para.style and para.style.name.lower().startswith("heading"):
                    writer._model._record_paragraph(i)  # type: ignore[attr-defined]
            for level in (1, 2, 3, 4):
                writer.mark_style_dirty(f"Heading {level}")

        cs = doc.last_changes
        return ToolResult(
            ok=True,
            message=f"auto-assigned {len(changes)} heading style(s)",
            changed_paragraphs=[{"paragraph_index": i} for i in cs.paragraphs],
            changed_styles=list(cs.styles),
            warnings=[],
            rollback_token=token,
        )


# ---------------------------------------------------------------------------
# tool_renumber_headings
# ---------------------------------------------------------------------------

class RenumberHeadings:
    name = "tool_renumber_headings"
    description = (
        "Fix gaps in heading numbering (e.g. 1, 1.1, 1.3 → 1, 1.1, 1.2). "
        "No-op for paragraphs whose ids appear in skip_para_ids."
    )
    input_schema = _INPUT_SCHEMA_EMPTY
    requires: list[str] = ["tool_assign_heading_styles"]
    idempotent = True

    def run(self, doc, params: dict[str, Any], ctx: ToolContext) -> ToolResult:
        return run_legacy(
            name=self.name,
            doc=doc,
            ctx=ctx,
            legacy_fn=renumber_headings,
            dirty_styles=("Heading 1", "Heading 2", "Heading 3", "Heading 4"),
        )


# ---------------------------------------------------------------------------
# tool_normalize_heading_spacing
# ---------------------------------------------------------------------------

class NormalizeHeadingSpacing:
    name = "tool_normalize_heading_spacing"
    description = (
        "Apply heading space_before / space_after from the profile to "
        "all Heading{1..4} paragraphs."
    )
    input_schema = _INPUT_SCHEMA_EMPTY
    requires: list[str] = ["tool_assign_heading_styles"]
    idempotent = True

    def run(self, doc, params: dict[str, Any], ctx: ToolContext) -> ToolResult:
        result = run_legacy(
            name=self.name,
            doc=doc,
            ctx=ctx,
            legacy_fn=normalize_heading_spacing,
            dirty_styles=("Heading 1", "Heading 2", "Heading 3", "Heading 4"),
        )
        if not result.ok:
            return result

        try:
            changed = _apply_heading_style_config(doc, ctx.config or {})
        except Exception as exc:
            return ToolResult(
                ok=False,
                message=str(exc),
                rollback_token=result.rollback_token,
                warnings=list(result.warnings),
            )

        styles = set(result.changed_styles)
        styles.update(changed)
        return ToolResult(
            ok=True,
            message="heading styles normalized",
            changed_paragraphs=list(result.changed_paragraphs),
            changed_styles=sorted(styles),
            changed_sections=list(result.changed_sections),
            warnings=list(result.warnings),
            rollback_token=result.rollback_token,
        )


# ---------------------------------------------------------------------------
# tool_setup_multilevel_list
# ---------------------------------------------------------------------------

class SetupMultilevelList:
    name = "tool_setup_multilevel_list"
    description = (
        "Bind Heading{1..4} styles to a Word multilevel list so inserts "
        "auto-renumber. Idempotent: re-running adds a fresh list def."
    )
    input_schema = _INPUT_SCHEMA_EMPTY
    requires: list[str] = ["tool_assign_heading_styles"]
    idempotent = True

    def run(self, doc, params: dict[str, Any], ctx: ToolContext) -> ToolResult:
        return run_legacy(
            name=self.name,
            doc=doc,
            ctx=ctx,
            legacy_fn=setup_multilevel_list,
            dirty_styles=("Heading 1", "Heading 2", "Heading 3", "Heading 4"),
        )


TOOLS = [
    AIClassifyHeadings(),
    AssignHeadingStyles(),
    RenumberHeadings(),
    NormalizeHeadingSpacing(),
    SetupMultilevelList(),
]


def _heading_candidates(doc, max_candidates: int, max_text_chars: int) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for p in doc.paragraphs():
        text = _squash_space(p.text)
        if not _is_heading_candidate_text(text):
            continue
        candidates.append(
            {
                "paragraph_index": p.index,
                "text": text[:max_text_chars],
                "style": p.style_name,
                "number_prefix": _number_prefix(text),
            }
        )
        if len(candidates) >= max_candidates:
            break
    return candidates


def _build_ai_heading_prompt(candidates: list[dict[str, Any]]) -> str:
    payload = {
        "task": (
            "Classify each candidate paragraph as thesis heading level "
            "1, 2, 3, 4, or null. Return JSON only: "
            "{\"items\":[{\"paragraph_index\":0,\"level\":1,"
            "\"confidence\":0.9}]}. Use null for body text."
        ),
        "candidates": candidates,
    }
    prompt = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    while len(prompt.encode("utf-8")) > 3800 and payload["candidates"]:
        payload["candidates"] = payload["candidates"][:-1]
        prompt = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return prompt


def _is_heading_candidate_text(text: str) -> bool:
    if not text:
        return False
    if len(text) > 90:
        return False
    lowered = text.lower()
    if lowered.startswith(("图", "表", "figure", "table")):
        return False
    if re.match(r"^\d+(?:\.\d+){0,3}(?:[\.、\s]|(?=[\u4e00-\u9fffA-Za-z]))", text):
        return True
    if re.match(r"^第.{1,8}[章节]\s*", text):
        return True
    if re.match(r"^[一二三四五六七八九十]+[、.．]\s*", text):
        return True
    if len(text) <= 36 and not re.search(r"[。！？!?；;]$", text):
        return True
    return False


def _number_prefix(text: str) -> str:
    match = re.match(r"^\s*(\d+(?:\.\d+){0,3})", text)
    return match.group(1) if match else ""


def _apply_ai_heading_items(
    doc,
    items: list[Any],
    *,
    confidence_threshold: float,
    renumber: bool,
) -> list[int]:
    normalized: list[tuple[int, int]] = []
    para_count = len(doc.paragraphs())
    for item in items:
        if not isinstance(item, dict):
            continue
        try:
            idx = int(item.get("paragraph_index"))
        except (TypeError, ValueError):
            continue
        level = item.get("level")
        if level is None:
            continue
        try:
            level_i = int(level)
            confidence = float(item.get("confidence", 0.0))
        except (TypeError, ValueError):
            continue
        if not (0 <= idx < para_count and 1 <= level_i <= 4):
            continue
        if confidence < confidence_threshold:
            continue
        normalized.append((idx, level_i))

    if not normalized:
        return []

    changed: list[int] = []
    counters = [0, 0, 0, 0]
    with doc.write() as writer:
        raw_doc = writer.raw
        for idx, level in sorted(normalized):
            para = raw_doc.paragraphs[idx]
            para.style = raw_doc.styles[f"Heading {level}"]
            if renumber:
                _advance_counters(counters, level)
                title = _strip_number_prefix(para.text)
                writer.set_paragraph_text(idx, f"{'.'.join(str(n) for n in counters[:level])} {title}")
            else:
                writer._model._record_paragraph(idx)  # type: ignore[attr-defined]
            writer.mark_style_dirty(f"Heading {level}")
            changed.append(idx)
    return changed


def _advance_counters(counters: list[int], level: int) -> None:
    if level > 1:
        for i in range(level - 1):
            if counters[i] == 0:
                counters[i] = 1
    counters[level - 1] += 1
    for i in range(level, len(counters)):
        counters[i] = 0


def _strip_number_prefix(text: str) -> str:
    stripped = _squash_space(text)
    stripped = re.sub(r"^\d+(?:\.\d+){0,3}(?:[\.、．]|\s+)?\s*", "", stripped, count=1)
    return stripped or _squash_space(text)


def _squash_space(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _apply_heading_style_config(doc, cfg: dict[str, Any]) -> list[str]:
    """Apply H1-H4 style font/size/bold/alignment from profile config.

    The legacy helper named ``normalize_heading_spacing`` only normalizes
    paragraph text spacing. The RuleSet also binds heading font/size/bold
    checks to this tool, so the wrapper owns the profile style sync.
    """
    changed: list[str] = []
    fonts = cfg.get("fonts", {}) or {}
    sizes = cfg.get("sizes", {}) or {}
    headings = cfg.get("headings", {}) or {}
    latin = fonts.get("latin", "Times New Roman")

    with doc.write() as writer:
        raw_doc = writer.raw
        for level in (1, 2, 3, 4):
            style_name = f"Heading {level}"
            h_key = f"h{level}"
            try:
                style = raw_doc.styles[style_name]
            except KeyError:
                continue

            h_cfg = headings.get(h_key, {}) or {}
            east_asia = fonts.get(h_key)
            size = sizes.get(h_key)
            bold = h_cfg.get("bold")
            if bold == "keep":
                bold = None

            if east_asia is not None and size is not None:
                set_style_font(
                    style,
                    east_asia=east_asia,
                    size_pt=parse_length(size),
                    bold=bold,
                    latin=latin,
                )

            pf = style.paragraph_format
            align = h_cfg.get("align")
            if align in _ALIGN_MAP:
                pf.alignment = _ALIGN_MAP[align]
            if "space_before" in h_cfg:
                apply_paragraph_spacing(pf, "before", h_cfg.get("space_before"))
            if "space_after" in h_cfg:
                apply_paragraph_spacing(pf, "after", h_cfg.get("space_after"))

            writer.mark_style_dirty(style_name)
            changed.append(style_name)

    return changed
