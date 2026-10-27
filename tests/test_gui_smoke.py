"""Headless-capable smoke tests for the Tkinter GUI editor.

Runs on machines with a working display (macOS dev machines), skips elsewhere.
The display probe runs in a subprocess because a broken tkinter build can abort
the interpreter outright ( Tcl/Tk version mismatch), which pytest cannot catch.

Failures marked xfail document known GUI bugs — flip them to plain asserts when
the fix lands.
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
    # gui bug: '-zoomed' was removed in Tk 9.0 — tolerate it so the rest of the
    # app is reachable (tracked in the launch-crash issue)
    orig = tk.Tk.attributes

    def safe_attrs(self, *args):
        try:
            return orig(self, *args)
        except tk.TclError:
            pass

    tk.Tk.attributes = safe_attrs
    root.withdraw()
    ed = mod.JSONEditor(root)
    yield ed
    root.destroy()
    tk.Tk.attributes = orig


def test_all_route_types_open(editor):
    for slug in editor.data["routes"]:
        editor.load_route_editor(slug)


@pytest.mark.xfail(reason="GUI bug: gallery (and its rows editor) missing from the type dropdown")
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


@pytest.mark.xfail(reason="GUI bug: type switching reads widgets destroyed by the rebuild (TclError)")
def test_switch_route_type_does_not_crash(editor):
    editor.load_route_editor("about")  # content
    editor.route_type_var.set("iframe")
    editor.load_route_editor("about")  # what the combobox binding runs


@pytest.mark.xfail(reason="GUI bug: interactive routes default + save sitemap:true; builder excludes them unless sitemap:true")
def test_sitemap_checkbox_matches_builder_semantics(editor):
    editor.load_route_editor("piglatin")  # interactive, no sitemap key
    assert editor.route_fields["sitemap"].get() is False


@pytest.mark.xfail(reason="GUI bug: gather_all writes keys the data never had (bg_image:'', explicit sitemap/ads)")
def test_gather_all_is_lossless_on_untouched_route(editor):
    before = json.dumps(editor.data, sort_keys=True)
    editor.load_route_editor("home")
    editor.gather_all()
    after = json.dumps(editor.data, sort_keys=True)
    assert before == after, "gather_all wrote keys the data never had"
