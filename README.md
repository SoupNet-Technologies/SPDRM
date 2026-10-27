# SPDRM

Single Page Dynamic Response Model. One JSON file in, one self-contained HTML site out.
No dependencies, no bundler, no node_modules, no framework. The whole pipeline is one
Python script that only uses the standard library.

SPDRM started in 2022 as a WordPress replacement. The idea was a newspaper layout:
sticky header and footer, independently scrolling regions, and every piece of content
living in data instead of page files. It has been quietly serving real sites since.
This is that, cleaned up and set free.

## How it works

Three moving parts:

- **`spdrm/build.py`** reads `spdrm/site_data.json`, validates the entire site, minifies
  the source CSS/JS with a conservative regex pass, and writes one self-contained
  `index.html` plus a PWA `manifest.json` and a `sitemap.xml`. If your data is broken,
  the build dies loudly with a list of everything wrong instead of shipping quietly
  broken. The previous build gets backed up to `index.html.bak` first.
- **`spdrm/site_data.json`** is the whole site: routes, nav, meta, layout, PWA settings.
  Every field is documented in `spdrm/SITE_DATA_REFERENCE.md`. Read that instead of
  guessing at the schema.
- **The runtime** is a 61-line hash router plus DOM primitives (`createCard`, dialogs,
  the abyss), bundled into the generated page in a fixed order. The page responds to
  navigation dynamically. That is the entire "Dynamic Response Model" pitch.

There is also `spdrm/gui_editor.py`, a Tkinter editor for the JSON, cause editing
routes in a text editor is fine until it is not. It refuses to start on invalid JSON
(losing edits is worse than a stern error message) and rebuilds when you save.

## Quickstart

```text
python3 spdrm/build.py
python3 -m http.server 8000
```

Open `http://localhost:8000`. That is it. The demo site in `site_data.json` is the
documentation you can click around in.

To start your own site, copy the repo (or just `spdrm/` plus the error pages), point
the `url` and content in `site_data.json` at your own stuff, rebuild, and deploy the
artifacts anywhere static files are served. Hash routing means no server rewrites are
needed anywhere, on anything. See `docs/deploying.md` for Cloudflare Pages, GitHub
Pages, Apache, and nginx recipes.

## Zero dependencies, on purpose

- The builder: Python 3 stdlib only. No pip installs.
- The runtime: vanilla ES6. No packages, no polyfills, no analytics.
- The editor: Tkinter, which ships with most Python installs.

The output is one HTML file. View source and read the entire site.

## Honest limitations

- Routing is hash-based and uses `location.replace`, so the back button leaves the
  site instead of walking your route history. That is deliberate for now; a History
  API router is on the roadmap for v0.2.
- SEO meta is set client-side after render. Search engines mostly see the static
  title and description from the build.
- The minifier is a conservative regex pass, not a real parser. It will not mangle
  normal code, but validate the built page after large route additions. Or trust the
  CI: it syntax-checks the built artifact with node.
- The GUI editor needs a display. Headless environments get nothing, which is fine,
  the CLI still builds.

## Status

v0.1. Tested (`pytest`, 40+ tests pinning builder behavior), CI-checked (build, size
budget, node syntax, markdown and prose style lint), and deployed. The demo lives
at [spdrm.jessy.boo](https://spdrm.jessy.boo).

Roadmap: History API router, npm packaging (deferred, the files are copy-paste-able
today), optional modules (synth, sudoku).

## License

MIT. See [LICENSE](LICENSE).
