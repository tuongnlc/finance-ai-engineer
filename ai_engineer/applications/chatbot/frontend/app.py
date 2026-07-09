import sys
from pathlib import Path


def _ensure_repo_root_on_syspath() -> None:
    file_path = Path(__file__).resolve()
    for parent in file_path.parents:
        if (parent / "pyproject.toml").exists():
            sys.path.insert(0, str(parent))
            return


_ensure_repo_root_on_syspath()

from ai_engineer.applications.chatbot.frontend.ui.layout import build_demo

demo = build_demo()


demo.queue().launch()
