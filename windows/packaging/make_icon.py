"""Render icon.svg to app.ico.

Run only when the mark changes; the .ico is committed so that neither the build nor CI needs a browser.

    python windows/packaging/make_icon.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
#: Windows picks the nearest size: 16 and 32 for the taskbar and title bar, 48 for the desktop, 256 for
#: the large view in Explorer. Below 32 the kundali's lines close up, so the small sizes are drawn from
#: a render of their own rather than squeezed down from 256.
SIZES = (16, 24, 32, 48, 64, 128, 256)


def main() -> int:
    try:
        from PIL import Image
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        print(f"Needs Pillow and Playwright: {e}", file=sys.stderr)
        return 1

    svg = (HERE / "icon.svg").read_text(encoding="utf-8")
    frames = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        for size in SIZES:
            page.set_viewport_size({"width": size, "height": size})
            page.set_content(
                f'<body style="margin:0">{svg.replace("width=\"512\" height=\"512\"", f"width=\"{size}\" height=\"{size}\"")}</body>')
            png = HERE / f".icon-{size}.png"
            page.screenshot(path=str(png), omit_background=True)
            frames.append(Image.open(png).convert("RGBA"))
        browser.close()

    frames[-1].save(HERE / "app.ico", format="ICO",
                    sizes=[(f.width, f.height) for f in frames], append_images=frames[:-1])
    for size in SIZES:
        (HERE / f".icon-{size}.png").unlink(missing_ok=True)
    print(f"app.ico written with {len(frames)} sizes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
