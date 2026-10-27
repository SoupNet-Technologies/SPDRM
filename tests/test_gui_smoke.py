"""Headless-capable smoke tests for the Tkinter GUI editor.

Runs on machines with a working display (macOS dev machines), skips elsewhere.
The display probe runs in a subprocess because a broken tkinter build can abort
the interpreter outright (Tcl/Tk version mismatch), which pytest cannot catch.
"""
import json
import subprocess
import sys

import pytest


def _display_ok() -> bool:
    probe = "import tkinter; r = tkinter.Tk(); r.withdraw(); r.destroy()"
    try:
        return subprocess.run(
            [sys.executable, "-c", probe], capture_output=True, timeout=30
        ).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


pytestmark = pytest.mark.skipif(not _display_ok(), reason="tkinter/display not usable in this python")


@pytest.fixture()
def editor():
    import importlib.util
    import tkinter as tk
    from pathlib import Path

    repo = Path(__file__).resolve().parent.parent
    spec = importlib.util.spec_from_file_location("gui_editor_smoke", repo / "spdrm" / "gui_editor.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    root = tk.Tk()
    root.withdraw()
    ed = mod.JSONEditor(root)
    yield ed
    root.destroy()


def test_launch_works_on_tk9(editor):
    """Issue #10: '-zoomed' is gone in Tk 9.0 — the editor must launch anyway.
    No monkeypatch in this fixture: if init raises, this test fails."""
    assert editor.data


def test_all_route_types_open(editor):
    for slug in editor.data["routes"]:
        editor.load_route_editor(slug)


def test_every_known_type_in_dropdown(editor):
    import tkinter as tk
    from tkinter import ttk

    editor.load_route_editor("home")
    combos = [
        c
        for w in editor.right_route_frame.winfo_children()
        for c in w.winfo_children()
        if isinstance(c, ttk.Combobox)
    ]
    values = combos[0]["values"] if combos else ()
    for known in ("content", "iframe", "404", "abyss", "interactive", "gallery"):
        assert known in values, f"{known} missing from the route-type dropdown"


def test_new_keys_load_without_loss(editor):
    assert editor.data["routes"]["gallery"]["rows"], "gallery rows present"
    assert "modules" in editor.data
    assert len(editor.data["ads"]) == 3


def test_switch_route_type_does_not_crash(editor):
    """Issue #11: switching types must not read destroyed widgets."""
    editor.load_route_editor("about")  # content
    editor.route_type_var.set("iframe")
    editor.load_route_editor("about")
    editor.load_route_editor("sudoku")  # iframe -> content direction
    editor.route_type_var.set("content")
    editor.load_route_editor("sudoku")


def test_type_switch_prunes_old_keys_and_seeds_new(editor):
    editor.load_route_editor("about")  # content with cards
    assert editor.data["routes"]["about"]["cards"]
    editor.route_type_var.set("iframe")
    editor.on_type_change(None)
    route = editor.data["routes"]["about"]
    assert route["type"] == "iframe"
    assert "cards" not in route, "old type's cards should be pruned on switch"
    assert route["iframe"] == ""
    # and back
    editor.route_type_var.set("content")
    editor.on_type_change(None)
    route = editor.data["routes"]["about"]
    assert route["type"] == "content"
    assert route["cards"] == []
    assert "iframe" not in route


def test_sitemap_checkbox_matches_builder_semantics(editor):
    """Issue #12: interactive routes are excluded from the sitemap unless they
    opt in — the checkbox must default to False for them."""
    editor.load_route_editor("piglatin")  # interactive, no sitemap key
    assert editor.route_fields["sitemap"].get() is False
    assert "sitemap" not in editor.data["routes"]["piglatin"]


def test_gather_all_is_lossless_on_untouched_route(editor):
    before = json.dumps(editor.data, sort_keys=True)
    editor.load_route_editor("home")
    editor.gather_all()
    after = json.dumps(editor.data, sort_keys=True)
    assert before == after, "gather_all wrote keys the data never had"


def test_gallery_rows_editor_round_trip(editor):
    """Issue #13: gallery routes get a rows editor that round-trips the data."""
    editor.load_route_editor("gallery")
    assert hasattr(editor, "row_list") and hasattr(editor, "cell_list")
    before = json.dumps(editor.data["routes"]["gallery"]["rows"], sort_keys=True)
    editor.save_current_cell()
    editor.gather_all()
    after = json.dumps(editor.data["routes"]["gallery"]["rows"], sort_keys=True)
    assert before == after


def test_modules_ui_round_trip(editor):
    """Issue #14: modules checkboxes read and write the modules key."""
    assert set(editor.module_vars) >= {"synth", "cards", "carousel", "highlight", "label"}
    before = sorted(editor.data["modules"])
    editor.module_vars["synth"].set(False)
    editor.gather_all()
    assert "synth" not in editor.data["modules"]
    assert "cards" in editor.data["modules"]
    editor.module_vars["synth"].set(True)
    editor.gather_all()
    assert sorted(editor.data["modules"]) == before
