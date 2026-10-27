#!/usr/bin/env python3
"""SPDRM Site Builder — Reads site_data.json + src/*, generates index.html"""
import sys, json, os, shutil, subprocess, re
from pathlib import Path

LT = chr(60)
GT = chr(62)

BASE = Path(__file__).resolve().parent
PROJECT_ROOT = BASE.parent
JSON_PATH = BASE / "site_data.json"
SRC_CSS = BASE / "src" / "style.css"
SRC_UTILS = BASE / "src" / "utils.js"
SRC_ROUTER = BASE / "src" / "router.js"
SRC_TOOLS = BASE / "src" / "tools.js"
OUT_PATH = PROJECT_ROOT / "index.html"

# optional modules: included in the bundle only when site_data.json lists them
MODULE_FILES = {
    "synth": "synth.js",
    "cards": "cards.js",
    "carousel": "carousel.js",
    "highlight": "highlight.js",
    "label": "label.js",
}

def die(msg):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)

def warn(msg):
    print(f"Warning: {msg}", file=sys.stderr)

def validate(data):
    errors = []
    site = data.get("site", {})
    if not site.get("title"):
        errors.append("site.title is required")
    if not data.get("url"):
        errors.append("url is required (FQDN like https://example.com)")
    if not data.get("lastmod"):
        errors.append("lastmod is required (date like 2025-07-02)")
    meta = data.get("meta", {})
    if not meta.get("description"):
        errors.append("meta.description is required")
    layout = data.get("layout", {})
    layout.setdefault("header_img", "assets/header.webp")
    layout.setdefault("nav_img", "assets/nav.webp")
    layout.setdefault("footer_html", 'Powered by ' + LT + 'a href="https://github.com/SoupNet-Technologies/SPDRM"' + GT + 'SPDRM' + LT + '/a' + GT)
    routes = data.get("routes", {})
    if not routes or not isinstance(routes, dict):
        errors.append("routes must be a non-empty object")
        return errors
    for slug, route in routes.items():
        if not slug or not isinstance(slug, str):
            errors.append(f"route has invalid slug: {slug}")
            continue
        rtype = route.get("type")
        if rtype not in ("content", "iframe", "404", "abyss", "interactive", "gallery"):
            errors.append(f"route '{slug}': invalid type '{rtype}'")
            continue
        if rtype == "content":
            if not route.get("title"):
                errors.append(f"route '{slug}': content type requires 'title'")
            if "cards" not in route or not isinstance(route.get("cards"), list):
                errors.append(f"route '{slug}': content type requires 'cards' array")
        elif rtype == "gallery":
            if not route.get("title"):
                errors.append(f"route '{slug}': gallery type requires 'title'")
            rows = route.get("rows")
            if not isinstance(rows, list) or not rows or not all(isinstance(r, list) for r in rows):
                errors.append(f"route '{slug}': gallery type requires 'rows' (array of arrays)")
            else:
                for i, row in enumerate(rows):
                    for j, cell in enumerate(row):
                        if not isinstance(cell, dict) or not cell.get("src"):
                            errors.append(f"route '{slug}': gallery row {i} cell {j} requires 'src'")
        elif rtype == "iframe":
            if not route.get("iframe"):
                errors.append(f"route '{slug}': iframe type requires 'iframe' URL")
        elif rtype == "404":
            if not route.get("body"):
                errors.append(f"route '{slug}': 404 type requires 'body' string")
        elif rtype == "interactive":
            if not route.get("title"):
                errors.append(f"route '{slug}': interactive type requires 'title'")
            if not route.get("html"):
                errors.append(f"route '{slug}': interactive type requires 'html' string")
        if "ads" in route and not isinstance(route["ads"], bool):
            errors.append(f"route '{slug}': ads must be true/false")
    nav = data.get("nav", [])
    if not isinstance(nav, list):
        errors.append("nav must be an array")
    else:
        for item in nav:
            slug = item.get("slug", "")
            if slug and slug not in routes:
                errors.append(f"nav '{item.get('label')}': slug '{slug}' not found in routes")
            for child in item.get("children", []):
                cslug = child.get("slug", "")
                if cslug and cslug not in routes:
                    errors.append(f"nav '{item.get('label')}' > '{child.get('label')}': slug '{cslug}' not found")
    if not SRC_CSS.exists():
        errors.append(f"src/style.css not found at {SRC_CSS}")
    if not SRC_UTILS.exists():
        errors.append(f"src/utils.js not found at {SRC_UTILS}")
    if not SRC_ROUTER.exists():
        errors.append(f"src/router.js not found at {SRC_ROUTER}")
    if not SRC_TOOLS.exists():
        errors.append(f"src/tools.js not found at {SRC_TOOLS}")
    for m in data.get("modules", []):
        if m not in MODULE_FILES:
            errors.append(f"unknown module '{m}' (available: {', '.join(sorted(MODULE_FILES))})")
        elif not (BASE / "src" / MODULE_FILES[m]).exists():
            errors.append(f"module '{m}': src/{MODULE_FILES[m]} not found")
    return errors
def gen_site_js(site):
    t = site.get("title", "")
    st = site.get("seo_title", "")
    tg = site.get("tagline", "")
    return f'const siteData={{title:"{_jsesc(t)}",seotitle:"{_jsesc(st)}",tagline:"{_jsesc(tg)}"}};'


def gen_routes_js(routes):
    parts = ["const routes={"]
    for slug, r in routes.items():
        qslug = f'"{slug}"' if "-" in slug else slug
        parts.append(f"  {qslug}:{{")
        rtype = r.get("type", "content")
        if rtype == "content":
            parts.append(f'    title:"{_jsesc(r.get("title",""))}",')
            bg = r.get("bg_image", "")
            if bg:
                parts.append(f'    bgImage:"{_jsesc(bg)}",')
            if r.get("ads") is False:
                parts.append("    noAd:true,")
            parts.append("    render(){")
            for card in r.get("cards", []):
                ct = _jsesc(card.get("title", ""))
                cb = _jsesc(card.get("body", ""))
                parts.append(f'      createCard("{ct}",')
                parts.append(f'        "{cb}"')
                parts.append("      );")
            parts.append("    },")
        elif rtype == "iframe":
            parts.append(f'    iframe:"{_jsesc(r.get("iframe",""))}",')
            if r.get("ads") is False:
                parts.append("    noAd:true,")
        elif rtype == "gallery":
            parts.append(f'    title:"{_jsesc(r.get("title",""))}",')
            if r.get("ads") is False:
                parts.append("    noAd:true,")
            parts.append("    render(){")
            rows = r.get("rows", [])
            row_parts = []
            for row in rows:
                cells = ",".join(
                    '{src:"%s",title:"%s"}' % (_jsesc(c.get("src", "")), _jsesc(c.get("title", "")))
                    for c in row
                )
                row_parts.append("[%s]" % cells)
            parts.append("      var grid=[%s];" % ",".join(row_parts))
            parts.append("      grid.forEach(function(row){")
            parts.append("        row.forEach(function(col){")
            parts.append('          var artimg=document.createElement("img");')
            parts.append("          artimg.src=col.src;")
            parts.append('          artimg.style="width:"+(main.offsetWidth/row.length)+"px;cursor:pointer";')
            parts.append("          artimg.onclick=function(){zoomimg(col);};")
            parts.append("          main.appendChild(artimg);")
            parts.append("        });")
            parts.append("      });")
            parts.append("    },")
        elif rtype == "404":
            parts.append("    is404:true,")
            body = _jsesc(r.get("body", ""))
            parts.append("    render(){")
            parts.append(f'      main.innerHTML="{body}";')
            parts.append('      setTimeout(()=>move("home"),2000);')
            parts.append("    },")
        elif rtype == "abyss":
            parts.append("    isAbyss:true,")
        elif rtype == "interactive":
            parts.append(f'    title:"{_jsesc(r.get("title",""))}",')
            if r.get("ads") is False:
                parts.append("    noAd:true,")
            parts.append("    render(){")
            parts.append(f'      initmain("{_jsesc(r.get("title",""))}");')
            parts.append(f'      main.insertAdjacentHTML("beforeend",`{_jsesc(r.get("html",""))}`);')
            onload = r.get("onload", "")
            if onload:
                parts.append(f'      {onload};')
            parts.append("    },")
        meta = r.get("meta", ["", "", ""])
        m0, m1, m2 = (meta + ["", "", ""])[:3]
        parts.append(f'    meta:["{_jsesc(m0)}","{_jsesc(m1)}","{_jsesc(m2)}"]')
        parts.append("  },")
    parts.append("};")
    return "\n".join(parts)


def gen_nav_js(nav):
    parts = ["function loadnav(){"]
    parts.append("    let navitems=[")
    for item in nav:
        parts.append("        {")
        parts.append(f'            title:"{_jsesc(item.get("label",""))}",')
        parts.append(f'            click:()=>move("{item.get("slug","")}"),')
        children = item.get("children", [])
        if children:
            parts.append("            children:[")
            for c in children:
                parts.append("                {")
                parts.append(f'                    title:"{_jsesc(c.get("label",""))}",')
                parts.append(f'                    click:()=>move("{c.get("slug","")}"),')
                parts.append("                },")
            parts.append("            ]")
        parts.append("        },")
    parts.append("    ];")
    parts.append("    let navul=document.createElement(\"ul\");")
    parts.append("    navitems.forEach((item)=>{")
    parts.append("        let navli=document.createElement(\"li\");")
    parts.append("        navli.innerHTML=item.title;")
    parts.append("        navli.onclick=item.click;")
    parts.append("        navul.appendChild(navli);")
    parts.append('        if(item.children&&item.children[0].hasOwnProperty("title")){')
    parts.append("            item.children.forEach((itemchild)=>{")
    parts.append("                let navlichild=document.createElement(\"li\");")
    parts.append("                navlichild.innerHTML=itemchild.title;")
    parts.append('                navlichild.className="subnav";')
    parts.append("                navlichild.onclick=itemchild.click;")
    parts.append("                navul.appendChild(navlichild);")
    parts.append("            });")
    parts.append("        }")
    parts.append("    });")
    parts.append("    nav.appendChild(navul);")
    parts.append("}")
    return "\n".join(parts)


def _jsesc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("`", "\\`").replace("\n", "\\n").replace("\r", "\\r")


def gen_ads_js(ads):
    parts = ["const adUrls=["]
    for ad in ads:
        src = _jsesc(ad.get("src", ""))
        url = _jsesc(ad.get("url", ""))
        parts.append(f'  {{src:"{src}",url:"{url}"}},')
    parts.append("];")
    return "\n".join(parts)


def assemble_html(data, utils_js, router_js, tools_js, site_js, routes_js, nav_js, ads_js, css="", module_js=""):
    meta = data.get("meta", {})
    layout = data.get("layout", {})
    meta_tags = ""
    desc = meta.get("description", "")
    kw = meta.get("keywords", "")
    author = meta.get("author", "")
    tc = meta.get("theme_color", "#ffffff")
    for k, v in [("description", desc), ("keywords", kw), ("author", author)]:
        if v:
            meta_tags += f'{LT}meta name="{k}" content="{_htmlesc(v)}"{GT}\n'
    meta_tags += f'{LT}meta charset="UTF-8"{GT}\n'
    meta_tags += f'{LT}meta name="viewport" content="initial-scale=1.0, user-scalable=no"{GT}\n'
    meta_tags += f'{LT}meta name="theme-color" content="{_htmlesc(tc)}"{GT}\n'
    meta_tags += f'{LT}link rel="manifest" href="manifest.json"{GT}\n'


    hi = _htmlesc(layout.get("header_img", "assets/header.webp"))
    ni = _htmlesc(layout.get("nav_img", "assets/nav.webp"))
    fh = layout.get("footer_html", "")

    script_js = f"{utils_js}\n{ads_js}\n{site_js}\n{routes_js}\n{nav_js}\n{tools_js}\n{module_js}{router_js}"

    return (
        f'{LT}!DOCTYPE html{GT}\n'
        f'{LT}head{GT}\n'
        f'    {LT}title{GT}{_htmlesc(data.get("site",{}).get("title",""))}{LT}/title{GT}\n'
        f'{meta_tags}'
        f'    {LT}style{GT}\n{css}\n    {LT}/style{GT}\n'
        f'{LT}/head{GT}\n'
        f'{LT}body{GT}\n'
        f'    {LT}header id="header"{GT}{LT}img src="{hi}"{GT}{LT}/header{GT}\n'
        f'    {LT}main id="main"{GT}{LT}/main{GT}\n'
        f'    {LT}aside id="aside"{GT}{LT}img src="{ni}"{GT}{LT}nav id="nav"{GT}{LT}/nav{GT}{LT}/aside{GT}\n'
        f'    {LT}dialog id="dialog" class="shakey"{GT}{LT}/dialog{GT}\n'
        f'    {LT}button id="btndev" onclick="devclick()" style="float:right;opacity:0"{GT}just tests{LT}/button{GT}\n'
        f'    {LT}footer id="footer"{GT}{LT}sup{GT}{fh}{LT}/sup{GT}{LT}/footer{GT}\n'
        f'    {LT}script{GT}\n{script_js}\n    {LT}/script{GT}\n'
        f'{LT}/body{GT}'
    )


def _htmlesc(s):
    return s.replace("&", "&amp;").replace(LT, "&lt;").replace(GT, "&gt;").replace('"', "&quot;")


def gen_manifest(data):
    site = data.get("site", {})
    pwa = data.get("pwa", {})
    return json.dumps({
        "name": site.get("title", ""),
        "short_name": pwa.get("short_name", site.get("title", "")),
        "start_url": "/",
        "scope": "/",
        "lang": "en-US",
        "display": "standalone",
        "background_color": pwa.get("background_color", "#1e1f26"),
        "theme_color": pwa.get("theme_color", "#5e5aba"),
        "dir": "auto",
        "orientation": "portrait",
        "categories": ["utilities"],
        "icons": [{
            "purpose": "any",
            "sizes": pwa.get("icon_sizes", "512x512"),
            "src": pwa.get("icon", "assets/icon.png"),
            "type": "image/png"
        }]
    }, indent=2)


def gen_sitemap(data):
    base = data.get("url", "")
    lm = data.get("lastmod", "")
    routes = data.get("routes", {})
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
             f'  <url><loc>{base}/</loc><lastmod>{lm}</lastmod>'
             f'<changefreq>monthly</changefreq><priority>1.0</priority></url>']
    for slug, r in routes.items():
        if r.get("sitemap", r.get("type") != "interactive"):
            pri = r.get("priority", 0.8)
            lines.append(f'  <url><loc>{base}/#{slug}</loc><lastmod>{lm}</lastmod>'
                         f'<changefreq>monthly</changefreq><priority>{pri}</priority></url>')
    lines.append('</urlset>')
    return "\n".join(lines)


def minify_js(code):
    result = []
    i = 0
    in_dq = in_sq = in_bt = in_lc = in_bc = False
    while i < len(code):
        ch = code[i]
        nc = code[i+1] if i + 1 < len(code) else ""
        if (in_dq or in_sq or in_bt) and ch == "\\" and nc:
            result.extend([ch, nc]); i += 2; continue
        if not in_lc and not in_bc:
            if ch == chr(34) and not in_sq and not in_bt: in_dq ^= True
            elif ch == "'" and not in_dq and not in_bt: in_sq ^= True
            elif ch == "`" and not in_dq and not in_sq: in_bt ^= True
        if in_dq or in_sq or in_bt:
            result.append(ch); i += 1; continue
        if ch == "/" and nc == "/":
            in_lc = True; i += 2; continue
        if in_lc:
            if ch == "\n": in_lc = False; result.append(" ")
            i += 1; continue
        if ch == "/" and nc == "*":
            in_bc = True; i += 2; continue
        if in_bc:
            if ch == "*" and nc == "/": in_bc = False; i += 2; continue
            i += 1; continue
        if ch in "\n\r\t ":
            if result and result[-1] != " ": result.append(" ")
            i += 1; continue
        result.append(ch); i += 1
    return "".join(result).strip()


def minify_css(code):
    result = []
    i = 0
    in_bc = in_dq = in_sq = False
    while i < len(code):
        ch = code[i]
        nc = code[i+1] if i + 1 < len(code) else ""
        if not in_bc:
            if ch == chr(34) and not in_sq: in_dq ^= True
            elif ch == "'" and not in_dq: in_sq ^= True
        if not in_dq and not in_sq:
            if ch == "/" and nc == "*": in_bc = True; i += 2; continue
            if in_bc and ch == "*" and nc == "/": in_bc = False; i += 2; continue
        if in_bc: i += 1; continue
        result.append(ch); i += 1
    code = "".join(result)
    code = re.sub(r"\s+", " ", code)
    for a, b in [(" {", "{"), ("{ ", "{"), (" }", "}"), ("} ", "}"),
                 (" :", ":"), (": ", ":"), (" ;", ";"), ("; ", ";"),
                 (" ,", ","), (", ", ","), ("( ", "("), (" )", ")")]:
        code = code.replace(a, b)
    return code.strip()


def conservative_strip(text):
    lines = text.split("\n")
    stripped = [l.strip() for l in lines]
    result = []
    blank_count = 0
    for l in stripped:
        if l == "":
            blank_count += 1
            if blank_count <= 1:
                result.append("")
        else:
            blank_count = 0
            result.append(l)
    return "\n".join(result)


def write_output(html, out_path):
    bak = out_path.with_suffix(".html.bak")
    if out_path.exists():
        shutil.copy2(out_path, bak)
    out_path.write_text(html, encoding="utf-8")
    return len(html)


def write_file(path, content):
    path.write_text(content, encoding="utf-8")


def node_check(html):
    try:
        js_code = html.split("<script>")[1].split("</script>")[0]
        r = subprocess.run(
            ["node", "-c", "-"],
            input=js_code,
            capture_output=True, text=True, timeout=5
        )
        if r.returncode != 0:
            warn(f"Node.js syntax check failed:\n{r.stderr.strip()}")
            return False
        else:
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return False

def main():
    json_path = BASE / "site_data.json"
    if len(sys.argv) > 1:
        json_path = Path(sys.argv[1])
    if len(sys.argv) > 2:
        global OUT_PATH
        OUT_PATH = Path(sys.argv[2])

    if not json_path.exists():
        die(f"JSON file not found: {json_path}")

    data = json.loads(json_path.read_text(encoding="utf-8"))
    data.setdefault("layout", {})

    errors = validate(data)
    if errors:
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        die(f"Validation failed with {len(errors)} error(s)")

    css = minify_css(SRC_CSS.read_text(encoding="utf-8"))
    utils_js = minify_js(SRC_UTILS.read_text(encoding="utf-8"))
    router_js = minify_js(SRC_ROUTER.read_text(encoding="utf-8"))
    tools_js = minify_js(SRC_TOOLS.read_text(encoding="utf-8"))

    site_js = minify_js(gen_site_js(data.get("site", {})))
    routes_js = minify_js(gen_routes_js(data.get("routes", {})))
    nav_js = minify_js(gen_nav_js(data.get("nav", [])))
    ads_js = minify_js(gen_ads_js(data.get("ads", [])))
    module_js = "\n".join(
        (BASE / "src" / MODULE_FILES[m]).read_text(encoding="utf-8")
        for m in data.get("modules", [])
        if m in MODULE_FILES
    )

    html = assemble_html(data, utils_js, router_js, tools_js, site_js, routes_js, nav_js, ads_js, css, module_js)
    html = conservative_strip(html)

    size = write_output(html, OUT_PATH)

    manifest = gen_manifest(data)
    write_file(PROJECT_ROOT / "manifest.json", manifest)

    sitemap = gen_sitemap(data)
    write_file(PROJECT_ROOT / "sitemap.xml", sitemap)

    route_count = len(data.get("routes", {}))
    nav_count = len(data.get("nav", []))
    card_count = sum(len(r.get("cards", [])) for r in data.get("routes", {}).values())

    print(f"Generated: {OUT_PATH.name} ({size:,}B), manifest.json, sitemap.xml — {route_count} routes, {nav_count} nav items, {card_count} cards")

    node_check(html)


if __name__ == "__main__":
    main()
