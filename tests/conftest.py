import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def build():
    """Load spdrm/build.py as a module (it's a script, not a package import)."""
    spec = importlib.util.spec_from_file_location("spdrm_build", REPO_ROOT / "spdrm" / "build.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["spdrm_build"] = mod
    spec.loader.exec_module(mod)
    return mod


def _base_data(**overrides):
    """Minimal valid site_data dict; override or extend per test."""
    data = {
        "url": "https://example.com",
        "lastmod": "2026-10-27",
        "site": {"title": "Example", "seo_title": " • Example", "tagline": ""},
        "meta": {"description": "an example site", "keywords": "", "author": ""},
        "layout": {},
        "pwa": {},
        "ads": [],
        "routes": {
            "home": {
                "type": "content",
                "title": "Home",
                "meta": ["Home", "", ""],
                "cards": [{"title": "hello", "body": "world"}],
            }
        },
        "nav": [{"label": "Home", "slug": "home"}],
    }
    for k, v in overrides.items():
        data[k] = v
    return data


@pytest.fixture
def base_data():
    """Factory fixture: base_data(**overrides) -> dict."""
    return _base_data
