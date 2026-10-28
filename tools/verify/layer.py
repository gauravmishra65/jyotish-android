"""Checks app_forecast.build across fictional people and edge cases."""
import os, json, re, sys, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "app", "src", "main", "python"))
import engine_api as E, app_forecast as AF

BANNED = re.compile(r"\b(death|die|dies|dying|disease|illness|cancer|divorce|accident|surgery|guarantee[ds]?)\b|मृत्यु|तलाक|रोग|दुर्घटना|बीमारी")
people = [dict(p) for p in E.CASES] + [
    {"name": "Asha Kumari", "date": "2012-05-05", "time": "07:15", "lat": 26.8467, "lon": 80.9462, "tz": "Asia/Kolkata", "gender": "F", "_note": "minor"},
    {"name": "Leap Day", "date": "1992-02-29", "time": "12:00", "lat": -33.8688, "lon": 151.2093, "tz": "Australia/Sydney", "gender": "M", "_note": "leap day, south"},
    {"name": "No Time", "date": "1975-09-09", "time": "12:00", "lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles", "gender": "F", "time_confidence": "unknown"},
    {"name": "Approx Time", "date": "1983-12-31", "time": "23:55", "lat": 19.076, "lon": 72.8777, "tz": "Asia/Kolkata", "gender": "M", "time_confidence": "approximate"},
    {"name": "Older Person", "date": "1950-01-01", "time": "06:00", "lat": 51.5074, "lon": -0.1278, "tz": "Europe/London", "gender": "F"},
]
nows = ["2026-10-28", "2028-02-29"]
issues = collections.defaultdict(list)
leftover = collections.Counter()
n = 0
for p in people:
    for now in nows:
        r = {k: v for k, v in p.items() if not k.startswith("_")}
        c = E.chart_obj(dict(r, now=now, modules=E.FORECAST_MODULES, horizon_years=3))
        out = AF.build(c, birth_date=p["date"])
        n += 1
        tag = f"{p['name']} @{now}"
        raw = json.dumps(out, ensure_ascii=False)
        if BANNED.search(raw):
            issues["banned word"].append(f"{tag}: {BANNED.search(raw).group(0)}")
        if p.get("time_confidence") in ("unknown", "approximate") and not out.get("reliability"):
            issues["missing reliability note"].append(tag)
        w0, w1 = out["window"]["from"], out["window"]["to"]
        ev = c["vedic"]["events"]
        for a in out["areas"]:
            if len(a["years"]) != 3:
                issues["years"].append(tag)
            for y in a["years"]:
                for d in y["drivers"] + y["more"]:
                    if not (d["from"][:10] <= y["to"] and d["to"][:10] >= y["from"]):
                        issues["driver outside its year"].append(f"{tag} {a['key']} {y['id']}: {d['technical']} {d['from']}..{d['to']}")
                    for word in re.findall(r"[A-Za-z]{4,}", d["hi"]):
                        leftover[word] += 1
                    if not re.search("[ऀ-ॿ]", d["hi"]):
                        issues["Hindi driver with no Hindi"].append(f"{tag}: {d['hi'][:80]}")
                # lean recount with the engine's rule
                ind = []
                seen = set()
                for src in next(A for A in AF.AREAS if A["key"] == a["key"])["src"]:
                    for i in c["forecast"]["life_areas"][src]["by_slice"][int(y["id"][1]) - 1]["indicators"]:
                        if (i["system"], i["text"]) not in seen:
                            seen.add((i["system"], i["text"])); ind.append(i)
                if AF._lean(ind)[:2] != (y["lean"], y["convergence"]):
                    issues["lean mismatch"].append(f"{tag} {a['key']} {y['id']}")
                if len(ind) != len(y["drivers"]) + len(y["more"]) + sum(1 for i in ind if i["text"].startswith("Event window")):
                    issues["drivers lost"].append(f"{tag} {a['key']} {y['id']}: {len(ind)} vs {len(y['drivers']) + len(y['more'])}")
            sc = {y["id"]: (y["supportive"] - y["demanding"]) * AF._CONV_W[y["convergence"]] for y in a["years"]}
            if a["outlook"]["best"] and sc[a["outlook"]["best"]] != max(sc.values()):
                issues["best year"].append(tag)
            if a["outlook"]["care"] and sc[a["outlook"]["care"]] != min(sc.values()):
                issues["care year"].append(tag)
            for w in a["windows"]:
                if not (w0 <= w["from"] <= w["to"] <= w1 or (w["kind"] == "kn_rao" and w0[:7] <= w["from"][:7] and w["to"][:7] <= w1[:7])):
                    issues["window outside forecast"].append(f"{tag} {w}")
            if a["key"] == "marriage":
                src = sorted(m["month"] for m in ev["marriage_kn_rao"]["months"] if m["all_steps"] and w0[:7] <= m["month"] <= w1[:7] and m["month"] >= AF.adult_from(p["date"])[:7])
                got = []
                for w in a["windows"]:
                    if w["kind"] == "kn_rao":
                        y_, m_ = int(w["from"][:4]), int(w["from"][5:7])
                        while f"{y_}-{m_:02d}" <= w["to"][:7]:
                            got.append(f"{y_}-{m_:02d}"); m_ += 1
                            if m_ == 13: y_, m_ = y_ + 1, 1
                if src != got:
                    issues["K.N. Rao months"].append(f"{tag}: {src} vs {got}")
        if p.get("_note") == "minor":
            m = next(a for a in out["areas"] if a["key"] == "marriage")
            print(f"MINOR {tag}: marriage windows {[(w['kind'], w['from'], w['to']) for w in m['windows']]}; Y1: {m['years'][0]['summary']['en']} | {m['subtitle']['en']}")
            adult = AF.adult_from(p["date"])
            for a in out["areas"]:
                for w in a["windows"]:
                    if w["kind"] in ("marriage", "kn_rao", "children") and w["from"] < adult:
                        issues["minor: window before 18"].append(f"{tag} {w}")
            for y in m["years"]:
                if y["from"] < adult and re.search(r"wedding|marriage|विवाह", y["summary"]["en"] + y["summary"]["hi"]):
                    issues["minor: wedding talk"].append(f"{tag} {y['id']}")
print(f"{n} forecasts built")
for k, v in issues.items():
    print(f"ISSUE {k}: {len(v)}"); [print("   ", x) for x in v[:5]]
print("English words left in Hindi driver text:", leftover.most_common(25))
sys.exit(1 if any(issues.values()) else 0)
