"""Builds the full report for fictional people and edge cases in both languages and checks it."""
import os, json, re, sys, html, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "app", "src", "main", "python"))
import engine_api as E
BANNED = re.compile(r"\b(death|die|dies|dying|disease|illness|cancer|divorce|accident|surgery|guarantee[ds]?|will cure)\b|मृत्यु|तलाक|रोग|दुर्घटना|बीमारी")
people = [dict(p, place=pl) for p, pl in zip(E.CASES, ["Varanasi, India", "New Delhi, India", "Singapore", "London, UK", "Kochi, India"])] + [
    {"name": "Asha Kumari", "date": "2012-05-05", "time": "07:15", "lat": 26.8467, "lon": 80.9462, "tz": "Asia/Kolkata", "gender": "F", "place": "Lucknow"},
    {"name": "Leap Day", "date": "1992-02-29", "time": "12:00", "lat": -33.8688, "lon": 151.2093, "tz": "Australia/Sydney", "gender": "M", "place": "Sydney"},
    {"name": "No Time", "date": "1975-09-09", "time": "12:00", "lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles", "gender": "F", "time_confidence": "unknown"},
    {"name": "Older Person", "date": "1950-01-01", "time": "06:00", "lat": 51.5074, "lon": -0.1278, "tz": "Europe/London", "gender": "F"},
]
OUT = os.environ.get("VERIFY_OUT") or __import__("tempfile").mkdtemp()
issues = collections.defaultdict(list)
eng_in_hi = collections.Counter()
for p in people:
    for lang in ("en", "hi"):
        tag = f"{p['name']}/{lang}"
        try:
            page = json.loads(E.report(json.dumps(dict(p, now="2026-10-28", lang=lang))))["html"]
        except Exception as e:
            import traceback; issues["crash"].append(f"{tag}: {traceback.format_exc()[-600:]}"); continue
        body = re.sub(r"<script.*?</script>|<style.*?</style>", "", page, flags=re.S)
        text = html.unescape(re.sub("<[^>]+>", " ", body))
        if BANNED.search(text): issues["banned"].append(f"{tag}: {BANNED.search(text).group(0)}")
        for k in range(1, 9):
            if f'id="sec{k}"' not in page: issues["missing section"].append(f"{tag} sec{k}")
        for bad in ("None", "nan", "{", "}", "[", "]"):
            for m in re.finditer(r"\b" + re.escape(bad) + r"\b" if bad.isalpha() else re.escape(bad), text):
                ctx = text[max(0, m.start() - 40): m.end() + 40].replace("\n", " ")
                if bad == "_" and "_" in p["name"]: continue
                issues[f"stray '{bad}'"].append(f"{tag}: …{ctx}…"); break
        if lang == "hi":
            # English words left in Hindi text, ignoring the person's own name/place, pinyin and fixed labels.
            allowed = set(re.findall(r"[A-Za-z]+", p["name"] + " " + p.get("place", ""))) | {"Gaurav", "Mishra", "authorgaurav", "com", "BVR", "Asia", "Kolkata", "Singapore",
                       "Europe", "London", "Australia", "Sydney", "America", "Los_Angeles", "Los", "Angeles", "UK", "India", "New", "Delhi", "Kochi", "Lucknow", "GM", "D9", "D10", "D1"}
            for w in re.findall(r"\b[A-Za-z]{3,}\b", text):
                if w not in allowed and not re.fullmatch(r"(Wu|Chen|Ji|Wei|Geng|Gui|Xin|You|Ren|Xu|Jia|Zi|Yi|Chou|Bing|Yin|Ding|Mao|Si|Shen|Hai|Wu|Yang|Xu|Jia)", w):
                    eng_in_hi[w] += 1
        if p["name"] == "Asha Kumari" and re.search(r"wedding|विवाह की योजना", text):
            issues["minor wedding talk"].append(tag)
        if p.get("time_confidence") == "unknown" and lang == "en" and "not exact" not in text:
            issues["unknown time note"].append(tag)
        open(os.path.join(OUT, f"rep_{p['name'].split()[0]}_{lang}.html"), "w", encoding="utf-8").write(page)
print("people x languages:", len(people) * 2)
for k, v in issues.items():
    print(f"ISSUE {k}: {len(v)}"); [print("   ", x[:300]) for x in v[:4]]
print("English words in Hindi:", eng_in_hi.most_common(30))
sys.exit(1 if any(issues.values()) else 0)
