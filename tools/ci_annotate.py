"""Emit the error part of a Gradle log as GitHub annotations (readable through the checks API)."""
import re
import sys

text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
chunks = []
m = re.search(r"\* What went wrong:(.*?)(\* Try:|\Z)", text, re.S)
if m:
    chunks.append(("What went wrong", m.group(1).strip()))
errs = [ln for ln in text.splitlines() if re.match(r"^(e: |ERROR|error:|.*FAILED|Caused by:|.*Exception)", ln.strip())]
if errs:
    chunks.append(("Error lines", "\n".join(dict.fromkeys(errs))[:6000]))
chunks.append(("Last lines", "\n".join(text.splitlines()[-60:])))
for title, body in chunks[:9]:
    body = body[:6000].replace("%", "%25").replace("\r", "").replace("\n", "%0A")
    print(f"::error title={title}::{body}")
