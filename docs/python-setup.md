# Python setup on macOS

Short version: macOS hands you several Pythons and at least one of them is
broken in ways that are not your fault. This file tells you which to use and
how to stop thinking about it.

## The situation

- `/usr/bin/python3` is the Xcode Command Line Tools Python. It is old, and its
  Tk is frequently built against a newer macOS SDK than the one you have
  installed, which makes `import tkinter` crash the interpreter outright. If a
  GUI app dies on launch with a message like "macOS 15 (1507) or later
  required", that is this. You can not fix it without touching Xcode, so do not
  try.
- Homebrew / python.org / installer Pythons vary. Check yours:

```
python3 -c "import tkinter; print(tkinter.TkVersion)"
```

If that prints a version, Tk works. If it aborts or traceback-spams, that
Python is fine for the builder but useless for the GUI editor.

## What SPDRM actually needs

The builder and the generated site need nothing but the standard library:

```
python3 spdrm/build.py
python3 -m http.server 8000
```

Any Python 3.9+ works for that, including the broken-Tk ones. Tkinter only
matters for `spdrm/gui_editor.py` (the Tkinter editor) and for running the GUI
tests.

## venv, the short honest version

A venv is a private copy of one specific Python. It inherits everything from
the Python that created it, including broken Tk. So: create it with a Python
you have verified.

```bash
# pick a python whose tkinter check printed a version (see above)
python3 -m venv .venv

# activate (zsh/bash). Must be run from the folder that contains .venv
source .venv/bin/activate

# your prompt now shows (.venv). Install dev deps and run the tests:
python -m pip install pytest
python -m pytest tests/ -q

# leave when you feel like it
deactivate
```

The part nobody tells you: activation is just PATH editing, and it is optional.
Calling the venv's interpreter directly always works and cannot be forgotten:

```
.venv/bin/python -m pytest tests/ -q
```

If `source` says "not a command", you are not in zsh/bash (fish uses
`source .venv/bin/activate.fish`, csh uses something worse). Or you are not in
the folder you think you are. `ls .venv/bin/activate` will tell you.

## The GUI editor

```
python3 spdrm/gui_editor.py
```

Run it with a Python whose tkinter check passed. On a Mac where the system
Python is broken, that is usually a newer python.org or Homebrew build.
