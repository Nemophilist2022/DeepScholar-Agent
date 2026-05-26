from __future__ import annotations

from pathlib import Path


def write_diff_summary(output_path: str | Path, *, tracked_paths: list[Path]) -> str:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Diff Summary", "", "Git Diff-friendly artifact snapshot.", ""]
    for path in tracked_paths:
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        lines.append(f"- {path.as_posix()}: {'present' if exists else 'missing'}, {size} bytes")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(output)
