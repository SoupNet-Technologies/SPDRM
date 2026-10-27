import ast
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GUI = REPO_ROOT / "spdrm" / "gui_editor.py"


def test_gui_editor_parses():
    """Syntax-level smoke test — runs everywhere, no Tk needed."""
    tree = ast.parse(GUI.read_text())
    assert any(isinstance(n, ast.FunctionDef) for n in ast.walk(tree))


def test_gui_editor_importable():
    """Import smoke test; skipped where tkinter isn't built (headless CI)."""
    try:
        import tkinter  # noqa: F401
    except ImportError:
        import pytest

        pytest.skip("tkinter not available in this Python build")
    spec = importlib.util.spec_from_file_location("spdrm_gui", GUI)
    mod = importlib.util.module_from_spec(spec)
    if "spdrm_gui" in sys.modules:
        return  # already imported by another test in this session
    spec.loader.exec_module(mod)
    # entry point is a __main__ guard around a JSONEditor + root.mainloop(), not a main() function
    assert hasattr(mod, "JSONEditor")
