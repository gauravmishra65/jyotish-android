"""Builds every focused report (Daily, Monthly, Annual, Mahadasha, Mangal Dosh, Kaal Sarp, Sade Sati, Chandra Rashi)
for the fictional people and edge cases in both languages and checks the wording and structure."""
import collections, html, json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "app", "src", "main", "python"))
import engine_api as E
import app_reports
# the same banned words and people as report_check.py
BANNED = re.compile(r"\b(death|die|dies|dying|disease|illness|cancer|divorce|accident|surgery|guarantee[ds]?|will cure|leper)\b|(?<![\u0900-\u097F])(?:मृत्यु|मौत|तलाक|रोग|दुर्घटना|बीमार|विधवा)")
people = [dict(p, place=pl) for p, pl in zip(E.CASES, ["Varanasi, India", "New Delhi, India", "Singapore", "London, UK", "Kochi, India"])]
people[0].update(residence="Singapore", current_lat=1.3521, current_lon=103.8198)   # one person living away from the birthplace
people += [
    {"name": "Asha Kumari", "date": "2012-05-05", "time": "07:15", "lat": 26.8467, "lon": 80.9462, "tz": "Asia/Kolkata", "gender": "F", "place": "Lucknow"},
    {"name": "Leap Day", "date": "1992-02-29", "time": "12:00", "lat": -33.8688, "lon": 151.2093, "tz": "Australia/Sydney", "gender": "M", "place": "Sydney"},
    {"name": "No Time", "date": "1975-09-09", "time": "12:00", "lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles", "gender": "F", "time_confidence": "unknown"},
    {"name": "Older Person", "date": "1950-01-01", "time": "06:00", "lat": 51.5074, "lon": -0.1278, "tz": "Europe/London", "gender": "F"},
]

issues = collections.defaultdict(list)
latin_in_hi = collections.Counter()
for i, p in enumerate(people):
    for kind in app_reports.KINDS:
        for lang in ("en", "hi"):
            if i >= 2 and lang == "hi" and kind not in ("daily", "mangal", "sade_sati"):
                continue      # Hindi for every kind on the first two people, a sample on the rest
            tag = f"{p['name']}/{kind}/{lang}"
            try:
                page = json.loads(E.special_report(json.dumps(dict(p, now="2026-11-10", lang=lang, kind=kind))))["html"]
            except Exception:
                import traceback; issues["crash"].append(f"{tag}: {traceback.format_exc()[-700:]}"); continue
            body = re.sub(r"<script.*?</script>|<style.*?</style>", "", page, flags=re.S)
            body = body.replace("<td>रोग</td>", "<td></td>").replace("<td>Rog</td>", "<td></td>")   # the Rog choghadiya is a name, not a prediction
            body = re.sub(r'<div class="cover-line"><span class="label">[^<]*</span><span class="value">[A-Z0-9/-]+</span></div>', "", body)   # the report reference
            text = html.unescape(re.sub("<[^>]+>", " ", body))
            if BANNED.search(text): issues["banned"].append(f"{tag}: {BANNED.search(text).group(0)}")
            if 'id="sec1"' not in page or 'id="sec3"' not in page: issues["missing section"].append(tag)
            for bad in ("None", "nan", "{", "}", "[", "]"):
                m = re.search(r"\b" + bad + r"\b" if bad.isalpha() else re.escape(bad), text)
                if m: issues[f"stray '{bad}'"].append(f"{tag}: …{text[max(0, m.start() - 40): m.end() + 40]}…")
            if lang == "hi":
                allowed = set(re.findall(r"[A-Za-z]+", p["name"] + " " + p.get("place", "") + " " + p.get("residence", ""))) | {"Gaurav", "Mishra", "authorgaurav", "com", "UTC", "KP", "S", "K"}
                for w in re.findall(r"[A-Za-z]{2,}", text):
                    if w not in allowed: latin_in_hi[w] += 1
if latin_in_hi:
    issues["English in Hindi"].append(", ".join(f"{w}×{n}" for w, n in latin_in_hi.most_common(30)))
for k, v in issues.items():
    print(f"{k}: {len(v)}"); [print("   ", x) for x in v[:8]]
print("special reports: " + ("problems found" if issues else "all clean"))
sys.exit(1 if issues else 0)
