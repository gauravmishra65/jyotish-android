"""Catch string-resource mistakes the Android resource compiler rejects or that break a language.

Usage: python tools/check_strings.py   (exit code 1 on any problem)
"""
import glob
import re
import sys
import xml.etree.ElementTree as ET

bad = []
files = sorted(glob.glob("app/src/main/res/values*/strings.xml"))
tables = {}
for f in files:
    raw = open(f, encoding="utf-8").read()
    for m in re.finditer(r'<string name="([^"]+)"[^>]*>(.*?)</string>', raw, re.S):
        if re.search(r"(?<!\\)'", m.group(2)):
            bad.append(f"{f}: unescaped apostrophe in {m.group(1)}")
        if re.search(r'(?<!\\)"', m.group(2)):
            bad.append(f"{f}: unescaped double quote in {m.group(1)}")
    tables[f] = {e.get("name"): (e.text or "") for e in ET.parse(f).getroot()}
base = tables.get("app/src/main/res/values/strings.xml", {})
for f, t in tables.items():
    for k in set(base) ^ set(t):
        bad.append(f"{f}: {k} is in only one language")
    for k in set(base) & set(t):
        if sorted(re.findall(r"%\d\$[sd]", base[k])) != sorted(re.findall(r"%\d\$[sd]", t[k])):
            bad.append(f"{f}: placeholders differ in {k}")
used = set()
for f in glob.glob("app/src/main/java/**/*.kt", recursive=True):
    used |= set(re.findall(r"R\.string\.(\w+)", open(f, encoding="utf-8").read()))
bad += [f"R.string.{k} is used but not defined" for k in sorted(used - set(base))]
print("\n".join(bad) or f"strings ok ({len(base)} per language)")
sys.exit(1 if bad else 0)
