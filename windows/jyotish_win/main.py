"""The window.

This file is as small as it is on purpose. It is the one part of the Windows edition that cannot be
tested on a headless CI runner, so it does as little as possible: open a window, hand it the API, and get
out of the way. Everything that can go wrong in a way worth catching lives in api.py, bridge.py and
storage.py, all of which are tested.

Run from a checkout:  python -m jyotish_win.main
"""
import os
import sys
from pathlib import Path

from .api import Api

TITLE = "Gaurav Jyotish"


def web_dir() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in (here / "web", here.parent / "web"):
        if (candidate / "index.html").exists():
            return candidate
    raise RuntimeError("The interface files were not found next to the application.")


def main() -> int:
    try:
        import webview
    except ImportError:
        print("pywebview is not installed. Run: pip install -r windows/requirements.txt", file=sys.stderr)
        return 1

    api = Api()
    index = web_dir() / "index.html"
    webview.create_window(
        TITLE,
        url=index.as_uri(),
        js_api=api,
        width=1180,
        height=820,
        min_size=(900, 640),
    )
    # JYOTISH_DEBUG opens the WebView2 developer tools, which is the only way to see a JavaScript error.
    webview.start(debug=bool(os.environ.get("JYOTISH_DEBUG")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
