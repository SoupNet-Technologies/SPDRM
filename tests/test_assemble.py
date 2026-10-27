def assemble(build, data):
    return build.assemble_html(
        data,
        "/*UTILS*/", "/*ROUTER*/", "/*TOOLS*/",
        build.minify_js(build.gen_site_js(data["site"])),
        build.minify_js(build.gen_routes_js(data["routes"])),
        build.minify_js(build.gen_nav_js(data["nav"])),
        build.minify_js(build.gen_ads_js(data.get("ads", []))),
        "body{color:#333}",
    )


def test_script_bundle_order_utils_before_router(build, base_data):
    html = assemble(build, base_data())
    assert html.index("/*UTILS*/") < html.index("/*ROUTER*/")
    # and the router is the LAST script piece
    assert html.index("/*ROUTER*/") > html.index("/*TOOLS*/")


def test_css_inlined_in_style_tag(build, base_data):
    html = assemble(build, base_data())
    assert "<style>" in html and "body{color:#333}" in html


def test_meta_tags_present(build, base_data):
    html = assemble(build, base_data())
    assert '<meta name="description" content="an example site">' in html
    assert '<meta name="theme-color" content="#ffffff">' in html
    assert '<link rel="manifest" href="manifest.json">' in html


def test_title_from_site(build, base_data):
    assert "<title>Example</title>" in assemble(build, base_data())


def test_layout_images_from_data(build, base_data):
    d = base_data()
    d["layout"]["header_img"] = "assets/h.webp"
    d["layout"]["nav_img"] = "assets/n.webp"
    html = assemble(build, d)
    assert '<img src="assets/h.webp">' in html
    assert '<img src="assets/n.webp">' in html


def test_content_route_becomes_render_function(build, base_data):
    html = assemble(build, base_data())
    assert 'home:{' in html
    assert 'createCard("hello",' in html


def test_noAd_flag_for_ads_false(build, base_data):
    d = base_data()
    d["routes"]["home"]["ads"] = False
    assert "noAd:true" in assemble(build, d)


def test_iframe_route_shape(build, base_data):
    d = base_data()
    d["routes"]["x"] = {"type": "iframe", "iframe": "https://example.com/embed", "meta": ["", "", ""]}
    html = assemble(build, d)
    assert 'iframe:"https://example.com/embed"' in html


def test_404_route_redirects_home(build, base_data):
    d = base_data()
    d["routes"]["gone"] = {"type": "404", "body": "not here", "meta": ["", "", ""]}
    html = assemble(build, d)
    assert "is404:true" in html
    assert 'setTimeout(()=>move("home"),2000);' in html


def test_jsesc_escapes_dangerous_chars(build):
    assert build._jsesc('a"b\\c`d\ne') == 'a\\"b\\\\c\\`d\\ne'


def test_write_output_backs_up_previous_build(build, tmp_path):
    out = tmp_path / "index.html"
    assert build.write_output("<html>v1</html>", out) == len("<html>v1</html>")
    build.write_output("<html>v2</html>", out)
    assert out.with_suffix(".html.bak").read_text() == "<html>v1</html>"
    assert out.read_text() == "<html>v2</html>"


def test_gallery_route_generates_grid_with_zoom(build, base_data):
    d = base_data()
    d["routes"]["art"] = {
        "type": "gallery", "title": "Art", "ads": False, "meta": ["", "", ""],
        "rows": [[{"src": "a.png", "title": 'One "A"'}, {"src": "b.png", "title": "Two"}]],
    }
    html = assemble(build, d)
    assert "zoomimg(col);" in html
    assert '{src:"a.png",title:"One \\"A\\""}' in html
    assert "main.offsetWidth/row.length" in html


def test_minify_js_mangles_regex_literals_documented_limitation(build):
    """Why modules ship verbatim: the minifier reads // inside /regex/ as a
    comment start (a regex ending in an escaped slash puts its terminator
    adjacent to it). The recovered highlight module hit exactly this and
    node_check caught it. If this ever stops being true, modules could be
    minified again."""
    src = r"const c = /\/\/.*|\/\*[^]*?\*\//g;"  # trimmed from highlight.js
    out = build.minify_js(src)
    assert "//g" not in out  # the regex terminator got eaten as a "comment"


def test_module_js_lands_between_tools_and_router(build, base_data):
    d = base_data()
    html = build.assemble_html(
        d,
        "/*UTILS*/", "/*ROUTER*/", "/*TOOLS*/",
        build.minify_js(build.gen_site_js(d["site"])),
        build.minify_js(build.gen_routes_js(d["routes"])),
        build.minify_js(build.gen_nav_js(d["nav"])),
        build.minify_js(build.gen_ads_js([])),
        "body{}",
        "/*MODULE*/",
    )
    assert html.index("/*TOOLS*/") < html.index("/*MODULE*/") < html.index("/*ROUTER*/")
