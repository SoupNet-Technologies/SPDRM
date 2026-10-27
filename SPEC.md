# SPEC — SPDRM

## Purpose

A zero-dependency single-page-site generator and runtime. A stdlib-Python builder
compiles one JSON content file plus source CSS/JS into a single self-contained
`index.html` with client-side hash routing, a card/dialog DOM component set, and
per-route metadata updates. Enough to run a content site that feels app-like without
a build step, a dependency tree, or a backend. The repo ships a working demo site
as its own content.

## Quick facts

- Languages: Python 3 (builder, stdlib only), JavaScript (runtime, vanilla ES6), CSS
- Runtime deps: none. Dev deps: pytest only.
- Build: `python3 spdrm/build.py` (no node, no bundler; node is used optionally for
  a post-build syntax check and degrades gracefully if absent)
- Entry points: `spdrm/build.py` (CLI), `spdrm/gui_editor.py` (Tkinter JSON editor),
  generated `index.html` (runtime)
- Config/content: `spdrm/site_data.json`, schema documented in
  `spdrm/SITE_DATA_REFERENCE.md`
- Site URL: whatever `url` says in the JSON. The demo points at the SPDRM demo site.
- Routing: URL hash only (`#home`, `#about`, ...). No History API (documented v0.2
  roadmap item). `location.replace` writes the hash, so hash changes do not spam
  browser history, and the back button leaves the site by design.

## Architecture

**Builder (`spdrm/build.py`, ~444 lines):**

1. Load JSON (arg 1 overrides the data path, arg 2 overrides the output path).
2. `validate()` enforces required fields (`site.title`, `url`, `lastmod`,
   `meta.description`, non-empty `routes`, `nav`) and per-route invariants. Route
   types: `content` (requires `title` + `cards` array), `iframe` (requires `iframe`
   URL), `404` (requires `body`), `abyss`, `interactive` (requires `title` + `html`).
   Optional per-route `ads` must be boolean. Nav slugs must reference existing
   routes. Any error aborts the build with a full list.
3. Minify CSS/JS from `spdrm/src/` (`minify_css`, `minify_js`, `conservative_strip`),
   a conservative string-state-machine pass, no external minifier.
4. `assemble_html()` emits the document: meta tags, inlined `<style>`, layout images,
   and one script bundle in fixed order: utils → ads → site → routes → nav → tools →
   router. Routes and nav are generated as JS from the JSON (`gen_routes_js`,
   `gen_nav_js`); strings are escaped by `_jsesc`.
5. Outputs: `index.html` (previous build backed up to `index.html.bak` via
   `shutil.copy2`), `manifest.json` (`gen_manifest`), `sitemap.xml` (`gen_sitemap`;
   `interactive` routes are excluded unless a route opts in with `sitemap: true`).
6. `node_check()` runs `node -c` on the generated script bundle when node exists.

**GUI editor (`spdrm/gui_editor.py`, ~843 lines):** `JSONEditor` (Tkinter) bound to
`site_data.json`. Refuses to start on invalid JSON; invokes the builder after saves.

**Runtime (`spdrm/src/`):**

- `router.js` (61 lines): declarative dispatcher over the generated `routes` object.
  Property priority: is404 → isAbyss → iframe → title/bgImage → render. Falls back
  to `routes.home` on unknown slugs. `loadmeta()` rewrites `<title>` and the
  description/keywords meta per route. `loadnav()` builds the sidebar from the
  generated nav structure (top-level items plus `.subnav` children).
- `utils.js`: `html()` tagged template (escapes interpolations, accepts DOM nodes),
  `initmain()`, `createCard()` (the one UI primitive everything is made of),
  `generateAd()` (reads ONLY the injected `siteData`/`adUrls` data, renders nothing
  when the array is empty), `generateDialog()`/`zoomimg()` (native `<dialog>`
  modals), `randimg()` (full-screen canvas RGB noise for `abyss` routes), `devclick()`
  dev toolbar, `isValidEmail()`, `maybeAnimate()`, an interactive Mandelbrot SVG.
- `tools.js`: `loadtools()` tools index, `isPalindrome()` + `paldefaults`,
  `translateToPigLatin()`, `getAverage()`, keyframer converter (`loadkf`),
  `imageToAscii()`, `shuffleVideo()`, a `metadataEditor` class.
- `style.css`: the newspaper layout. Sticky header/footer, independently scrolling
  `#main` and `#aside`, cards, `.subnav` indent, `.shakey` dialog.

**Error pages:** `403.html`/`404.html`/`500.html` are static, hand-maintained, and
outside the build pipeline.

## Interfaces

- CLI: `python3 spdrm/build.py [json_path] [out_path]`, both args optional.
- GUI: `python3 spdrm/gui_editor.py`, no args, needs a display.
- HTTP: none. The generated `index.html` is served as a static file by anything.
  Hash routing means no server rewrites are required on any host.
- Data format: `spdrm/SITE_DATA_REFERENCE.md` is authoritative. Top-level keys:
  `url`, `lastmod`, `site`, `meta`, `layout`, `pwa`, `ads`, `routes`, `nav`.

## Data & storage

- `spdrm/site_data.json` is the sole content source. No database, no server state.
- Build backups land in `index.html.bak` (gitignored).

## Build & deploy

```text
python3 spdrm/build.py        # regenerate index.html, manifest.json, sitemap.xml
python3 -m http.server 8000   # serve locally
```

Deploy the root artifacts (`index.html`, `manifest.json`, `sitemap.xml`, `assets/`,
error pages) to any static host. Recipes: `docs/deploying.md`.

CI (`.github/workflows/`): pytest on 3.12/3.13, full build with a 64 KB size budget
on `index.html`, node syntax check of source and built artifact, markdownlint plus
a prose style pass on all docs, yamllint on the workflows. `deploy.yml` pushes
the built site to Cloudflare Pages (demo: spdrm.jessy.boo). `release.yml` attaches a
zip of the built site to tag releases.

## Testing

- `tests/` (pytest, 42 tests): validation invariants for every route type and nav
  slug rule, minifier string/comment survival cases, script bundle order, meta and
  layout assembly, manifest/sitemap generation including the interactive-route
  opt-in, the `.bak` backup behavior, GUI parse/import smoke, and an end-to-end
  validation of the repo's own demo data.
- `node_check()` post-build syntax pass (runs in CI).
- No browser test suite yet; the demo routes are verified manually on release.

## Limitations & known issues

- Never hand-edit `index.html`; it is overwritten (with backup) on every build.
- `gen_sitemap` excludes `interactive` routes from `sitemap.xml` by design; opt in
  per route with `sitemap: true`.
- The regex minifiers are conservative. Pathological code could survive them
  mangled; the node syntax check catches gross breakage, not subtle logic damage.
- Hash-only routing: SEO is client-side, back button exits the site. Known, documented,
  roadmap item. Do not file a bug about it, file a PR against v0.2.
- `generateDialog()`/`zoomimg()` interpolate into innerHTML. Fine for fixed internal
  call sites; do not feed them user input.
- `testapi()` in utils.js is a relic that expects jQuery which never loads. Clicking
  the dev-panel button throws. It is kept because removing it would be admitting
  the dev panel was never finished. It was not.
- GUI editor requires a display; headless environments get the CLI only.

## File map

```text
index.html                  generated SPA (build artifact, not committed)
manifest.json               generated PWA manifest
sitemap.xml                 generated sitemap
403.html 404.html 500.html  static error pages (hand-maintained)
assets/                     demo site images
spdrm/build.py              builder CLI
spdrm/gui_editor.py         Tkinter JSON editor
spdrm/site_data.json        content source (sole source of truth)
spdrm/SITE_DATA_REFERENCE.md  data model documentation
spdrm/src/                  style.css, utils.js, router.js, tools.js (build inputs)
tests/                      pytest suite
tools/prose_lint.py         prose style checker used on the docs (CI job: docs)
docs/deploying.md           hosting recipes (CF Pages, GH Pages, Apache, nginx)
.github/workflows/          ci.yml, deploy.yml, release.yml
```
