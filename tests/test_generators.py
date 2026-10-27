import json


def test_gen_manifest_fields(build, base_data):
    d = base_data()
    d["pwa"] = {"short_name": "Ex", "theme_color": "#ff0000", "icon": "assets/icon.png"}
    m = json.loads(build.gen_manifest(d))
    assert m["name"] == "Example"
    assert m["short_name"] == "Ex"
    assert m["theme_color"] == "#ff0000"
    assert m["icons"][0]["src"] == "assets/icon.png"
    assert m["display"] == "standalone"


def test_gen_manifest_defaults(build, base_data):
    m = json.loads(build.gen_manifest(base_data()))
    assert m["short_name"] == "Example"
    assert m["icons"][0]["src"] == "assets/icon.png"


def test_sitemap_lists_content_routes(build, base_data):
    xml = build.gen_sitemap(base_data())
    assert "https://example.com/</loc>" in xml
    assert "https://example.com/#home</loc>" in xml
    assert "<lastmod>2026-10-27</lastmod>" in xml


def test_sitemap_excludes_interactive_by_default(build, base_data):
    d = base_data()
    d["routes"]["tool"] = {"type": "interactive", "title": "T", "html": "<b></b>", "meta": ["", "", ""]}
    xml = build.gen_sitemap(d)
    assert "#tool</loc>" not in xml


def test_sitemap_includes_interactive_with_optin(build, base_data):
    d = base_data()
    d["routes"]["tool"] = {
        "type": "interactive", "title": "T", "html": "<b></b>",
        "meta": ["", "", ""], "sitemap": True, "priority": 0.5,
    }
    xml = build.gen_sitemap(d)
    assert "#tool</loc>" in xml
    assert "<priority>0.5</priority>" in xml


def test_gen_site_js_escapes(build):
    js = build.gen_site_js({"title": 'a"b', "seo_title": "", "tagline": ""})
    assert js.startswith("const siteData=")
    assert 'title:"a\\"b"' in js


def test_gen_routes_js_quotes_hyphenated_slugs(build, base_data):
    d = base_data()
    d["routes"]["my-tool"] = {"type": "abyss", "meta": ["", "", ""]}
    js = build.gen_routes_js(d["routes"])
    assert '"my-tool":{' in js


def test_gen_nav_js_wires_clicks(build, base_data):
    js = build.gen_nav_js(base_data()["nav"])
    assert 'click:()=>move("home")' in js
    assert "function loadnav(){" in js


def test_gen_ads_js_shape(build):
    js = build.gen_ads_js([{"src": "a.png", "url": "https://example.com"}])
    assert '{src:"a.png",url:"https://example.com"}' in js
    assert js.startswith("const adUrls=[")


def test_end_to_end_build_of_repo_demo(build):
    """The real site_data.json in the repo must validate and build."""
    data = json.loads((build.JSON_PATH).read_text())
    assert build.validate(data) == []
    routes_js = build.gen_routes_js(data["routes"])
    for slug in data["routes"]:
        assert f'"{slug}":{{' in routes_js or f"{slug}:{{" in routes_js
