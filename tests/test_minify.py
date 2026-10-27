def test_minify_js_strips_comments_and_collapses_whitespace(build):
    src = """
    // a line comment
    function  hello ( name ) {
        /* block
           comment */
        return name + 1;
    }
    """
    out = build.minify_js(src)
    assert "//" not in out and "/*" not in out
    assert "function hello ( name ) {" in out
    assert "return name + 1;" in out


def test_minify_js_preserves_string_internals(build):
    src = 'const url = "https://example.com/a//b /* not a comment */";'
    out = build.minify_js(src)
    assert "https://example.com/a//b /* not a comment */" in out


def test_minify_js_preserves_template_literals(build):
    src = "const t = `a  b // c`;"
    out = build.minify_js(src)
    assert "`a  b // c`" in out


def test_minify_js_handles_escaped_quotes(build):
    src = 'const s = "say \\"hi//ho\\""; const n = 1;'
    out = build.minify_js(src)
    assert '"say \\"hi//ho\\""' in out


def test_minify_css_strips_comments_and_squeezes(build):
    src = """
    /* header */
    body {
        color : #333 ;
        background : url( "img test.png" ) ;
    }
    """
    out = build.minify_css(src)
    assert "/*" not in out
    assert "body{" in out
    assert "color:#333;" in out
    # string content survives the space-squeezing
    assert '"img test.png"' in out


def test_conservative_strip_collapses_blank_runs(build):
    src = "a\n\n\n\nb\n\nc"
    assert build.conservative_strip(src) == "a\n\nb\n\nc"


def test_conservative_strip_trims_lines(build):
    assert build.conservative_strip("  x  \n    y") == "x\ny"
