import copy


def err(build, data):
    return build.validate(copy.deepcopy(data))


def test_valid_base_passes(build, base_data):
    assert err(build, base_data()) == []


def test_missing_required_top_keys(build, base_data):
    for key in ("url", "lastmod"):
        d = base_data()
        d.pop(key)
        msgs = " ".join(err(build, d))
        assert key in msgs
    d = base_data()
    d["site"] = {}
    assert "site.title is required" in " ".join(err(build, d))
    d = base_data()
    d["meta"] = {}
    assert "meta.description is required" in " ".join(err(build, d))


def test_routes_must_be_nonempty_dict(build, base_data):
    msgs = " ".join(err(build, base_data(routes={})))
    assert "non-empty object" in msgs


def test_invalid_route_type(build, base_data):
    msgs = " ".join(err(build, base_data(routes={"x": {"type": "magic"}})))
    assert "invalid type 'magic'" in msgs


def test_content_route_needs_title_and_cards(build, base_data):
    msgs = " ".join(err(build, base_data(routes={"x": {"type": "content"}})))
    assert "requires 'title'" in msgs
    assert "requires 'cards' array" in msgs


def test_iframe_route_needs_url(build, base_data):
    msgs = " ".join(err(build, base_data(routes={"x": {"type": "iframe"}})))
    assert "requires 'iframe' URL" in msgs


def test_404_route_needs_body(build, base_data):
    msgs = " ".join(err(build, base_data(routes={"x": {"type": "404"}})))
    assert "requires 'body' string" in msgs


def test_interactive_route_needs_title_and_html(build, base_data):
    msgs = " ".join(err(build, base_data(routes={"x": {"type": "interactive"}})))
    assert "requires 'title'" in msgs
    assert "requires 'html' string" in msgs


def test_route_ads_must_be_bool(build, base_data):
    msgs = " ".join(err(build, base_data(routes={"x": {"type": "abyss", "ads": "yes"}})))
    assert "ads must be true/false" in msgs


def test_nav_slug_must_exist(build, base_data):
    msgs = " ".join(err(build, base_data(nav=[{"label": "Nope", "slug": "ghost"}])))
    assert "slug 'ghost' not found in routes" in msgs


def test_nav_child_slug_must_exist(build, base_data):
    nav = [{"label": "Home", "slug": "home", "children": [{"label": "Sub", "slug": "ghost"}]}]
    msgs = " ".join(err(build, base_data(nav=nav)))
    assert "slug 'ghost' not found" in msgs


def test_layout_defaults_are_generic(build, base_data):
    d = base_data()
    build.validate(d)  # not the deepcopy helper — validate() mutates layout in place
    assert d["layout"]["header_img"] == "assets/header.webp"
    assert d["layout"]["nav_img"] == "assets/nav.webp"
    assert "SPDRM" in d["layout"]["footer_html"]
    assert "jessyboo" not in d["layout"]["footer_html"]
