"""Predictions page (app_predict): every period for the fictional people and edge cases in both languages.
Checks: six areas, stars 2-5, a reading and a reason for each, no banned word, no English left in the Hindi text."""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "app", "src", "main", "python"))
import app_details as AD
import app_predict as P
import engine_api as E

people = list(E.CASES) + [
    {"name": "No Time", "date": "1975-09-09", "time": "12:00", "lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles", "gender": "F", "time_confidence": "unknown"},
    {"name": "Older Person", "date": "1950-01-01", "time": "06:00", "lat": 51.5074, "lon": -0.1278, "tz": "Europe/London", "gender": "F"},
]
problems = []
for p in people:
    for per in ("day", "week", "month", "year", "three"):
        try:
            o = P.predict_json(json.dumps(dict(p, now="2026-11-10", period=per)))
        except Exception as e:
            problems.append(f"{p['name']} {per}: crash {e!r}"[:300])
            continue
        j = json.loads(o)
        if len(j["areas"]) != 6:
            problems.append(f"{p['name']} {per}: {len(j['areas'])} areas")
        for a in j["areas"]:
            if not 2 <= a["stars"] <= 5 or not a["reading"]["en"] or not a["why"]["hi"]:
                problems.append(f"{p['name']} {per} {a['key']}: {a['stars']} stars or empty text")
        for lang in ("en", "hi"):
            for v in re.findall(r'"%s": "([^"]*)"' % lang, o):
                if AD.UNSAFE.search(v):
                    problems.append(f"{p['name']} {per} {lang}: banned word in: {v[:80]}")
                if lang == "hi" and re.search(r"[A-Za-z]{3,}", v):
                    problems.append(f"{p['name']} {per}: English in Hindi: {v[:80]}")
for x in problems[:20]:
    print("ISSUE", x)
print(f"predictions: {len(problems)} problems")
sys.exit(1 if problems else 0)
