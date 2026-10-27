# Python notes

The builder only needs the standard library, so any Python 3.9+ runs it. The
one place Python choice matters is the GUI editor, which needs a working Tk.

Check a Python in ten seconds:

```text
python3 -c "import tkinter; print(tkinter.TkVersion)"
```

A printed version means it can run the editor. A crash or traceback means use a
different Python for windows: some system and distro Pythons ship broken or
missing Tk, which is common on macOS and costs nothing to work around.

## Running the editor

```bash
python3 spdrm/gui_editor.py
```

Everything else happens inside the editor. Its Build button shells out to the
builder, which works on any Python.

## If you want to run the tests (optional, contributor territory)

Use a venv so pytest stays out of your system Python:

```bash
python3 -m venv .venv
source .venv/bin/activate      # zsh/bash; the prompt gains (.venv)
python -m pip install pytest
python -m pytest tests/ -q
```

Two things worth knowing:

1. A venv is a private copy of the exact Python that created it. If that
   Python has broken Tk, the venv does too. Make it with one that passed the
   check above.
2. Activation is just PATH editing and it is optional. Calling the venv
   directly always works: `.venv/bin/python -m pytest tests/ -q`. If `source`
   says "not a command", check which shell you are in (`echo $0`) and whether
   you are in the folder that contains `.venv`.
