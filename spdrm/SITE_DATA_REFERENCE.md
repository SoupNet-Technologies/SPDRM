# SPDRM Site Builder — `site_data.json` Reference

This document describes every field in `site_data.json`. This file is the **sole source of content** for the generated SPDRM website. Edit this file, then run `python3 secret666python/build.py` to regenerate `index.html`, `manifest.json`, and `sitemap.xml`.

---

## Top-Level Structure

```json
{
  "url": "https://example.com",
  "lastmod": "2025-07-02",
  "site": { ... },
  "meta": { ... },
  "layout": { ... },
  "pwa": { ... },
  "ads": [ ... ],
  "routes": { ... },
  "nav": [ ... ]
}
```

| Field | Required | Type | Description |
|---|---|---|---|
| `url` | **Yes** | string | Full FQDN of the site. Used in sitemap generation. |
| `lastmod` | **Yes** | string | ISO date for sitemap `<lastmod>`. Format: `YYYY-MM-DD` |
| `site` | **Yes** | object | Site identity metadata |
| `meta` | **Yes** | object | HTML meta tags and branding |
| `layout` | No | object | Visual layout paths (has defaults) |
| `pwa` | No | object | PWA manifest settings (has defaults) |
| `ads` | No | array | Ad image URLs and click destinations |
| `routes` | **Yes** | object | All pages/routes on the site |
| `nav` | **Yes** | array | Navigation menu structure |

---

## `site` — Site Identity

```json
{
  "site": {
    "title": "Example Site",
    "seo_title": " • Example Site",
    "tagline": "An example site"
  }
}
```

| Field | Required | Description |
|---|---|---|
| `title` | **Yes** | The site name. Used as `<title>` and in metadata. |
| `seo_title` | No | Suffix appended to every page title. Default: `""` |
| `tagline` | No | Short descriptor. Currently unused in generated HTML but reserved. |

---

## `meta`, HTML Meta Tags

```json
{
  "meta": {
    "description": "Exploring the intersection of creativity and technology: music, art, games, literature, coding, and more!",
    "keywords": "example, demo",
    "author": "SoupNet Technologies",
    "theme_color": "#ffffff"
  }
}
```

| Field | Required | Description |
|---|---|---|
| `description` | **Yes** | `<meta name="description">` content |
| `keywords` | No | `<meta name="keywords">` content |
| `author` | No | `<meta name="author">` content |
| `theme_color` | No | `<meta name="theme-color">` content. Default: `#ffffff` |

The following meta tags are hardcoded in `build.py` and do **not** come from JSON:
- `<meta charset="UTF-8">`
- `<meta name="viewport" content="initial-scale=1.0, user-scalable=no">`

---

## `layout`, Visual Assets

```json
{
  "layout": {
    "header_img": "assets/header.webp",
    "nav_img": "assets/nav.webp",
    "footer_html": "Powered by <a href=\"https://github.com/SoupNet-Technologies/SPDRM\">SPDRM</a>"
  }
}
```

All fields are optional. If omitted, these defaults apply:

| Field | Default | Description |
|---|---|---|
| `header_img` | `assets/header.webp` | Image path for the `<header>` banner |
| `nav_img` | `assets/nav.webp` | Image path displayed above the sidebar `<nav>` |
| `footer_html` | `Powered by ...` | Raw HTML injected into `<footer>` |

---

## `pwa`, Progressive Web App / manifest.json

```json
{
  "pwa": {
    "short_name": "Example Site",
    "background_color": "#1e1f26",
    "theme_color": "#5e5aba",
    "icon": "assets/icon.png",
    "icon_sizes": "512x512"
  }
}
```

All fields optional. These override the `meta.theme_color` for the manifest specifically.

| Field | Default | Description |
|---|---|---|
| `short_name` | `site.title` | Used in `manifest.json` `short_name` |
| `background_color` | `#1e1f26` | PWA splash screen background |
| `theme_color` | `#5e5aba` | PWA theme color (can differ from meta) |
| `icon` | `assets/icon.png` | Path to PWA icon image |
| `icon_sizes` | `512x512` | Icon dimensions |

---

## `ads`, Advertisements

```json
{
  "ads": [
    {"src": "assets/ads/10721.webp", "url": "https://example.com"},
    {"src": "assets/ads/10722.webp", "url": ""},
    {"src": "assets/ads/10723.webp", "url": ""}
  ]
}
```

Array of ad objects. Each build generates `const adUrls = [...]` from this array.

| Field | Required | Description |
|---|---|---|
| `src` | **Yes** | Image path for the ad banner |
| `url` | No | Click destination. If empty string `""` or omitted, ad is **not clickable** (no `<a>` wrapper). If non-empty, wraps the `<img>` in `<a href="url" target="_blank">` |

**Per-route ad visibility** is controlled by the `ads` field inside each route object (see route reference below). The `ads` array here just provides the pool of images; you can have 0-ad pages even with 50 images defined.

---

## `routes`, Page Definitions

The core of the site. Each key is the route slug (used in URLs as `#slug`). There are **four route types**:

### Route Type: `content` (Standard Page)

```json
"projects": {
  "type": "content",
  "title": "My Projects",
  "bg_image": "assets/background.webp",
  "ads": true,
  "sitemap": true,
  "priority": 0.8,
  "meta": ["My Projects", "A description", "keyword1, keyword2"],
  "cards": [
    {"title": "Project One", "body": "Description with <b>HTML</b> tags.<hr><a href='https://...'><button>Link</button></a>"},
    {"title": "Project Two", "body": "Another description."}
  ]
}
```

| Field | Required | Description |
|---|---|---|
| `type` | **Yes** | Must be `"content"` |
| `title` | **Yes** | Page heading displayed at the top |
| `bg_image` | No | URL/path for full-page CSS background image |
| `ads` | No | Boolean. `true` shows ads, `false` hides them. Default: `true` |
| `sitemap` | No | Boolean. Include in sitemap. Default: `true` |
| `priority` | No | Sitemap priority (0.0 – 1.0). Default: `0.8` |
| `meta` | No | Array of 3 strings: `[page_title_suffix, description, keywords]`. Used by `loadmeta()`. |
| `cards` | **Yes** | Array of card objects. Each card has a `title` and `body`. The body is raw HTML. |

**Slug rules:**
- If the slug contains a hyphen (`-`), it gets quoted in the generated JS: `"my-page"`
- Slug characters: `[a-zA-Z0-9-]`

**Card body style:**
- Plain text and HTML are both fine
- Use `<hr>` for separators
- Use `<a href='...'><button>Text</button></a>` for links styled as buttons
- JS template literal syntax (`${}`) will break, avoid it in card bodies

---

### Route Type: `iframe` (Embedded Page)

```json
"external-tool": {
  "type": "iframe",
  "iframe": "https://example.com/widget",
  "ads": false,
  "sitemap": true,
  "priority": 0.8,
  "meta": ["External Tool", "", ""]
}
```

| Field | Required | Description |
|---|---|---|
| `type` | **Yes** | Must be `"iframe"` |
| `iframe` | **Yes** | The URL to embed in an `<iframe>` filling the main area |
| `ads` | No | Same as content type |
| `sitemap` | No | Same as content type |
| `priority` | No | Same as content type |
| `meta` | No | Same as content type |

Note: `iframe` routes have **no** `title` or `cards`. They are full-screen embeds.
The iframe URL is interpolated directly into a JS template literal: `` `<iframe src='${route.iframe}'...` ``. Do not include `$` or backticks in the iframe URL.

---

### Route Type: `404` (Not Found Page)

```json
"notfound": {
  "type": "404",
  "ads": false,
  "sitemap": false,
  "meta": ["Not Found", "", ""],
  "body": "<h2>Nothing Here</h2><p class=\"shakey\">The page you're looking for doesn't exist.</p>"
}
```

| Field | Required | Description |
|---|---|---|
| `type` | **Yes** | Must be `"404"` |
| `body` | **Yes** | Raw HTML injected into `main.innerHTML`. No `createCard()` wrapper. |
| `ads` | No | Usually `false` for error pages |
| `sitemap` | No | Usually `false`, you don't want 404 pages indexed |
| `priority` | No | Ignored if `sitemap` is false |
| `meta` | No | Same as content type |

The generated JS auto-redirects to the home route after 2 seconds:
```js
setTimeout(() => move("home"), 2000);
```
This behavior is hardcoded in `build.py`.

---

### Route Type: `abyss` (Random Noise Page)

```json
"abyss": {
  "type": "abyss",
  "ads": false,
  "sitemap": false,
  "meta": ["Abyss", "", ""]
}
```

| Field | Required | Description |
|---|---|---|
| `type` | **Yes** | Must be `"abyss"` |
| `ads` | No | Usually `false` |
| `sitemap` | No | Usually `false` |
| `priority` | No | Ignored |
| `meta` | No | Same as content type |

No extra fields. This route generates random RGB noise on a `<canvas>` element via the `randimg()` function from `utils.js`.

---

### Route Type: `interactive` (Tool/Utility Page)

```json
"piglatin": {
  "type": "interactive",
  "title": "Pig Latin Translator",
  "ads": false,
  "sitemap": false,
  "meta": ["Pig Latin", "", ""],
  "html": "<input id='pigInput' placeholder='Enter sentence'><button onclick='document.getElementById(\"pigOut\").innerText=translateToPigLatin(document.getElementById(\"pigInput\").value)'>Translate</button><div id='pigOut' style='margin-top:1em;font-size:1.2em'></div>",
  "onload": ""
}
```

| Field | Required | Description |
|---|---|---|
| `type` | **Yes** | Must be `"interactive"` |
| `title` | **Yes** | Page heading displayed at the top |
| `html` | **Yes** | Raw HTML markup injected into the page. The JS functions that power the UI come from `src/tools.js`. |
| `onload` | No | Optional JS expression called after the HTML is injected. Used for tools that need initialization (e.g., `"loadkf()"` for the Keyframe Animator). |
| `ads` | No | Same as content type |
| `sitemap` | No | Defaults to **`false`** for interactive routes. Set to `true` if you want the page indexed. |
| `priority` | No | Same as content type |
| `meta` | No | Same as content type |

**HTML injection notes:**
- The `html` field is injected via `main.insertAdjacentHTML("beforeend", \`...\`)`, a JS template literal
- **Avoid `${}`** in your HTML markup, it will be interpreted as template interpolation and break the page
- Use single quotes for HTML attribute values where possible (`onclick='...'` instead of `onclick="..."`) to avoid backtick/template conflicts
- Double quotes in attribute values should be escaped with backslash: `onclick='document.getElementById(\"myId\")'`
- Wire up interactivity using `onclick`, `onchange`, `oninput` attributes that call functions from `src/tools.js`

**Available functions from `src/tools.js`:**
- `translateToPigLatin(sentence)`, returns Pig Latin translation
- `isPalindrome(str)`, returns boolean
- `loadkf()`, renders the Keyframe Animator UI into `#kfContainer`
- `imageToAscii(fileInput, scale, textarea)`, converts image to ASCII art
- `shuffleVideo(fileInput)`, creates a video shuffler interface
- `toplessPicGenerator(fileInput)`, image effect tool
- `getValuesFromCSVFile(file)`, CSV line reader
- `getAverage(numbers)`, average calculator

---

## `nav`, Navigation Menu

```json
{
  "nav": [
    {
      "label": "Home",
      "slug": "home",
      "children": [
        {"label": "Assist", "slug": "assist"},
        {"label": "Abyss", "slug": "abyss"}
      ]
    },
    {
      "label": "Cyber",
      "slug": "cyber",
      "children": [
        {"label": "Ophanim", "slug": "ophanim"},
        {"label": "Super-Wordlister", "slug": "super-wordlister"},
        {"label": "SNT Secure VaultX", "slug": "snt-secure-vaultx"},
        {"label": "Skills", "slug": "skills"}
      ]
    },
    {
      "label": "Contact",
      "slug": "contact"
    }
  ]
}
```

| Field | Required | Description |
|---|---|---|
| `label` | **Yes** | Display text in the sidebar nav |
| `slug` | **Yes** | Must match a key in `routes` exactly |
| `children` | No | Array of child nav items (same structure, without `children`) |

**Requirements:**
- Every `slug` must reference an existing route key. Validation will reject unknown slugs.
- A nav item with no `children` key renders as a plain nav entry.
- A nav item with `children` is shown as a parent with indented sub-items (CSS class `subnav`).
- The `label` text is inserted via `innerHTML`, so basic HTML entities work (e.g., `&amp;`).

---

## Per-Route Field Reference (All Types)

| Field | content | iframe | 404 | abyss | interactive |
|---|---|---|---|---|---|---|
| `type` | **Required** | **Required** | **Required** | **Required** | **Required** |
| `title` | **Required** |, |, |, | **Required** |
| `cards` | **Required** |, |, |, |, |
| `bg_image` | Optional |, |, |, |, |
| `iframe` |, | **Required** |, |, |, |
| `body` |, |, | **Required** |, |, |
| `html` |, |, |, |, | **Required** |
| `onload` |, |, |, |, | Optional |
| `ads` | Optional | Optional | Optional | Optional | Optional |
| `sitemap` | Optional | Optional | Optional | Optional | Optional |
| `priority` | Optional | Optional | Optional | Optional | Optional |
| `meta` | Optional | Optional | Optional | Optional | Optional |

Default values when omitted:
- `ads`: `true`
- `sitemap`: `true` (except `interactive` routes which default to `false`)
- `priority`: `0.8` (home defaults to `0.9`)
- `meta`: `["", "", ""]`

---

## src/ Directory Files

These are **not** part of `site_data.json` but are read by `build.py` and inlined:

| `src/` File | Purpose | Edit When |
|---|---|---|
| `src/style.css` | All CSS inlined into `<style>` | Changing site visuals |
| `src/utils.js` | JS functions: `createCard()`, `initmain()`, `generateAd()`, `randimg()`, `generateDialog()`, `zoomimg()`, `devclick()`, `html` tagged template, `isValidEmail()` | Changing how pages render or adding new functionality. **Edit `adUrls` here** |
| `src/router.js` | JS functions: `move(s)`, `moveurl(s)`, `loadmeta()`, `window.onload` | Changing routing behavior, URL handling, or bootstrap logic |
| `src/tools.js` | JS functions for interactive routes: `translateToPigLatin()`, `isPalindrome()`, `loadkf()`, `imageToAscii()`, `shuffleVideo()`, `toplessPicGenerator()` | Adding or modifying interactive tools used in `"interactive"` type routes |

---

## Validation Rules (What `build.py` Checks)

On each run, `build.py` validates the entire JSON. Here's exactly what it checks:

### Top-Level
- `site.title` must exist and be non-empty
- `url` must exist and be non-empty (FQDN like `https://example.com`)
- `lastmod` must exist and be non-empty (date like `2025-07-02`)
- `meta.description` must exist and be non-empty
- `routes` must be a non-empty object
- `nav` must be an array

### Per Route
- `type` must be one of: `content`, `iframe`, `404`, `abyss`, `interactive`
- `content` type requires `title` and `cards` array
- `iframe` type requires `iframe` URL string
- `404` type requires `body` string
- `interactive` type requires `title` and `html` string
- `ads` must be boolean if present

### Per Nav Item
- Every `slug` must match a key in `routes`
- Every child's `slug` must match a key in `routes`

### File Checks
- `src/style.css` must exist
- `src/utils.js` must exist
- `src/router.js` must exist
- `src/tools.js` must exist

If any validation fails, the script exits with a non-zero code and prints all errors.

---

## Common Mistakes

| Mistake | What happens |
|---|---|
| Forgetting to escape quotes in a string | JSON parsing fails. Use `\"` inside strings, or wrap the string in single quotes where possible. |
| Using `$` or `` ` `` in a card body or iframe URL | The generated JS will break because these trigger template literal interpretation. Escape them as `\${` or avoid them. |
| Referencing a nav slug that doesn't exist | Validation error: `nav 'X': slug 'Y' not found in routes` |
| Setting `type` to something other than the 4 valid types | Validation error: `route 'X': invalid type 'Y'` |
| Omitting `title` on a content route | Validation error: content type requires `title` |
| Leaving `cards` off a content route | Validation error: content type requires `cards` array |
| The `body` field in 404 routes has unescaped double quotes | The generated JS will break. Use `\"` or wrap in single quotes in the body (e.g., `class='shakey'` instead of `class="shakey"`). |

---

## Workflow

```
1. Edit site_data.json  ← you are here
2. Edit src/style.css   (optional, visual changes)
3. Edit src/utils.js    (optional, framework changes)
4. Edit src/router.js   (optional, routing changes)
5. Run: python3 secret666python/build.py
6. Output: index.html, manifest.json, sitemap.xml
7. Open index.html in browser to verify
8. If something broke, restore from index.html.bak and fix the JSON
```
