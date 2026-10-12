from utils.html_safety import escape_html_text, safe_filename_component


def test_html_escape_blocks_tags_and_attribute_breakout():
    raw = '<img src=x onerror="alert(1)"><script>alert(2)</script>'
    escaped = escape_html_text(raw)
    assert "<img" not in escaped
    assert "<script>" not in escaped
    assert "&lt;img" in escaped
    assert "&quot;" in escaped


def test_html_escape_bounds_text_and_removes_nulls():
    escaped = escape_html_text("hello\x00" + "x" * 100, max_length=12)
    assert "\x00" not in escaped
    assert len(escaped) <= 12


def test_safe_filename_removes_path_and_extension_control():
    filename = safe_filename_component("../../report/../Aryan <script>.png")
    assert "/" not in filename and "\\" not in filename
    assert "<" not in filename and ">" not in filename
    assert filename
    assert len(safe_filename_component("x" * 200)) <= 60
