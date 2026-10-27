# Contributing

Short version: issues are read, PRs are reviewed, both are appreciated.

## Before you open an issue

- Read the SPEC. Most "bugs" about hash routing, the back button, and client-side
  SEO are documented design decisions with reasons attached. Disagree with the
  reason? Say so, design discussions are welcome, relitigating the FAQ is not.
- The builder dies loudly on invalid data by design. If your build failed, the
  error list is the feature; include it.

## Pull requests

- Zero dependencies is the whole identity of this project. If your change adds
  a package, a bundler, or a polyfill, it will not be merged no matter how good
  the idea is. Write the stdlib/vanilla version.
- The builder is Python stdlib only. The runtime is vanilla ES6. The editor is
  Tkinter. Same rule each.
- The router is bug-for-bug parity with the deployed sites by contract; behavior
  changes to it belong in an issue first.
- Tests: builder changes need tests pinning the new behavior (pytest, see
  tests/ for the house style). GUI changes run tests/test_gui_smoke.py locally
  on a machine with a display; CI cannot.
- The built artifacts (index.html, manifest.json, sitemap.xml) are generated.
  Never commit them; CI builds from source and enforces a size budget.
- Docs get linted (markdownlint plus a prose style pass, both in CI). If CI
  rejects your prose, rewrite rather than delete; the linter is opinionated but
  it is usually right.

## AI-generated contributions

Disclose it in the PR description. Nothing against tools, but the project's
voice is part of what makes it readable, and undisclosed machine prose gets
rewritten anyway, which wastes everyone's time.
