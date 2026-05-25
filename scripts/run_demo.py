from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import _run_demo


if __name__ == "__main__":
    result = _run_demo(Path("examples/demo_run"))
    print("DeepScholar demo generated:")
    print(f"- draft:  {result.draft_path}")
    print(f"- docx:   {result.docx_path}")
    print(f"- report: {result.report_path}")
    print(f"- trace:  {result.trace_path}")
