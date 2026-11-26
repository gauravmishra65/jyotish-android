#!/usr/bin/env python3
"""Stage the built site for a claude.ai artifact preview.

    python3 web/build.py && python3 web/stage.py /some/empty/dir

A real static host serves index.html as the front door. An artifact does not: its
entry page is the one published as the page itself, and `index.html` is reserved for
that slot - so the artifact's front door is nakshatra.html, the calculator most search
traffic would land on anyway, and the home page is published beside it as home.html
with its internal links rewritten to match. Nothing else differs between the staged
copy and what a domain would serve, and a real deployment uses the web directory
directly and ignores this script.

Writes files.json: the {published path: source path} map to hand to the Artifact tool.
"""
import json, pathlib, re, shutil, sys

SRC = pathlib.Path(__file__).parent
# data.json and koota-data.json are build inputs, not served files, so they stay behind
KEEP_SUFFIX = {".html", ".js", ".css", ".xml", ".txt"}
SKIP = {"build.py", "stage.py", "verify.py", "files.json", "index.json", "ui.js"}  # ui.js is folded into engine.js


def home_from_index(text):
    """The home page, with links to itself pointing at home.html instead."""
    return re.sub(r'(href=")((?:\.\./|hi/)?)index\.html(")', r'\1\2home.html\3', text)


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    (out / "hi").mkdir(exist_ok=True)
    copied = []
    for f in sorted(SRC.rglob("*")):
        if f.is_dir() or f.name in SKIP or f.suffix not in KEEP_SUFFIX:
            continue
        rel = f.relative_to(SRC)
        if rel.parts[0] == "wasm":
            continue
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dst)
        copied.append(rel.as_posix())

    # Every page's links to the home page have to move with it, or they point at the
    # one path an artifact will not serve.
    for rel in list(copied):
        if rel.endswith(".html"):
            f = out / rel
            f.write_text(home_from_index(f.read_text(encoding="utf-8")), encoding="utf-8")
    for sub in ("", "hi/"):
        idx = out / sub / "index.html"
        if not idx.exists():
            continue
        (out / sub / "home.html").write_text(idx.read_text(encoding="utf-8"), encoding="utf-8")
        idx.unlink()
        copied.remove(f"{sub}index.html")
        copied.append(f"{sub}home.html")

    # nakshatra.html is the artifact's entry page, so it is not one of the extra files
    files = {p: p for p in sorted(set(copied)) if p != "nakshatra.html"}
    (out / "files.json").write_text(json.dumps(files, ensure_ascii=False), encoding="utf-8")
    print(f"{len(files) + 1} files staged in {out}  (entry page: nakshatra.html)")
    print("files.json written for the Artifact publish")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(pathlib.Path(sys.argv[1]))
