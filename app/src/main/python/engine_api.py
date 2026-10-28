"""engine_api.py - the only Python module the Android app calls.

Each function takes and returns a JSON string, so the Kotlin side never handles Python objects.
The calculation modules beside this file are copied unchanged from the astrology-numerology-reading
skill by tools/sync_engine.py; ENGINE_VERSION.txt records which commit.
"""
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("SE_EPHE_PATH", os.path.join(HERE, "ephe"))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

_T_IMPORT = time.perf_counter()
import chart_engine  # noqa: E402
import muhurta  # noqa: E402
import name_correction  # noqa: E402
IMPORT_SECONDS = time.perf_counter() - _T_IMPORT

DEFAULT_MODULES = "vedic,western,numerology"


def _chart_args(r):
    args = ["chart", "--name", r["name"], "--date", r["date"], "--time", r["time"],
            "--lat", str(r["lat"]), "--lon", str(r["lon"]), "--tz", r["tz"],
            "--gender", r.get("gender", "M"), "--modules", r.get("modules", DEFAULT_MODULES),
            "--time-confidence", r.get("time_confidence", "reliable"),
            "--horizon-years", str(r.get("horizon_years", 0))]
    if r.get("now"):
        args += ["--now", r["now"]]
    if r.get("ayanamsa"):
        args += ["--ayanamsa", r["ayanamsa"]]
    if r.get("node"):
        args += ["--node", r["node"]]
    if r.get("place"):
        args += ["--place", r["place"]]
    if r.get("name_correction"):
        args.append("--name-correction")
    return chart_engine.build_parser().parse_args(args)


def chart_obj(r):
    return chart_engine.build_chart(_chart_args(r))


def chart(request_json):
    """{"name","date":"YYYY-MM-DD","time":"HH:MM","lat","lon","tz","gender"?,"modules"?,"now"?} -> chart JSON."""
    return json.dumps(chart_obj(json.loads(request_json)), ensure_ascii=False)


def match(chart_a_json, chart_b_json, bride="B"):
    return json.dumps(chart_engine.match_charts(json.loads(chart_a_json), json.loads(chart_b_json), bride), ensure_ascii=False)


def find_muhurta(request_json, *chart_jsons):
    """{"event","from","to","lat","lon","tz","weekday_rule"?,"top"?,"lang"?} plus zero or more chart JSON strings.

    With "lang": "hi" every window's weekday, nakshatra, lagna, reasons and cautions are also given in Hindi
    (fields ending in _hi), using the same translator as the skill's muhurta report.
    """
    r = json.loads(request_json)
    people = [muhurta.person_from_chart(json.loads(c)) for c in chart_jsons]
    res = muhurta.find(r["event"], r["from"], r["to"], r["lat"], r["lon"], r["tz"], people,
                       r.get("step", 10), r.get("top", 12), r.get("weekday_rule", "soft"))
    if r.get("lang") == "hi":
        import muhurta_report as MR
        for w in res["all_windows"]:
            for k in ("weekday", "nakshatra", "lagna"):
                w[k + "_hi"] = MR._hi_text(w[k])
            w["supports_hi"] = [MR._hi_text(x) for x in w["supports"]]
            w["weaknesses_hi"] = [MR._hi_text(x) for x in w["weaknesses"]]
    return json.dumps(res, ensure_ascii=False)


FORECAST_MODULES = "vedic,western,bazi,numerology,events"


def forecast(request_json):
    """The chart request plus "years" (default 3) and "now" -> the app's forecast by life area (app_forecast.build).

    Runs the forecast and life-event layers, which the ordinary chart call leaves out; about 2 s on a desktop.
    """
    import app_forecast
    r = json.loads(request_json)
    r = dict(r, modules=FORECAST_MODULES, horizon_years=int(r.get("years", 3)))
    return json.dumps(app_forecast.build(chart_obj(r), birth_date=r["date"]), ensure_ascii=False)


def engine_version():
    p = os.path.join(HERE, "ENGINE_VERSION.txt")
    return open(p).read().strip() if os.path.exists(p) else "unknown"


def names(name, dob, gender=None):
    return json.dumps(name_correction.suggest(name, dob, gender=gender), ensure_ascii=False)


# ---- self-test used by the instrumented test and the spike screen -------------------------------

def fingerprint(c):
    """The values a packaging fault would disturb, rounded so desktop and phone compare exactly."""
    v = c["vedic"]
    cur = v["dashas"]["vimshottari"]["current"]
    return {
        "lagna": round(v["lagna"]["lon"], 6),
        "planets": {p: round(x["lon"], 6) for p, x in v["planets"].items()},
        "nakshatras": {p: f'{x["nakshatra"]} {x["pada"]}' for p, x in v["planets"].items()},
        "dasha": [cur["mahadasha"]["lord"], cur["antardasha"]["lord"], cur["mahadasha"]["end"]],
        "yogas": sorted(y["id"] for y in v["yoga_library"].get("found", [])),
        "tajika_year_lord": (v.get("varshaphal", {}).get("tajika") or {}).get("varsheshwara"),
        "western_asc": c["western"]["angles"]["Ascendant"]["lon"] if "angles" in c.get("western", {}) else None,
        "numbers": [c["numerology"]["indian"]["mulank_driver"], c["numerology"]["indian"]["bhagyank_conductor"],
                    c["numerology"]["chaldean"]["compound_number"]],
        "tz": c["time_pipeline"].get("tz_label") or c["time_pipeline"].get("tz"),
    }


CASES = [
    {"name": "Ravi Shankar Tiwari", "date": "1988-07-14", "time": "14:35", "lat": 25.3176, "lon": 82.9739, "tz": "Asia/Kolkata", "gender": "M"},
    {"name": "Neha Agarwal", "date": "1991-03-02", "time": "09:10", "lat": 28.6139, "lon": 77.2090, "tz": "Asia/Kolkata", "gender": "F"},
    {"name": "Mei Lin Tan", "date": "1979-11-23", "time": "23:50", "lat": 1.3521, "lon": 103.8198, "tz": "Asia/Singapore", "gender": "F"},
    {"name": "Arjun Mehta", "date": "1996-06-30", "time": "01:30", "lat": 51.5074, "lon": -0.1278, "tz": "Europe/London", "gender": "M"},
    {"name": "Priya Nair", "date": "1972-03-12", "time": "06:05", "lat": 40.7128, "lon": -74.0060, "tz": "America/New_York", "gender": "F"},
]
NOW = "2026-10-20"
MUHURTA = {"event": "marriage", "from": "2027-01-01", "to": "2027-03-31", "lat": 25.3176, "lon": 82.9739, "tz": "Asia/Kolkata"}


def run_suite():
    """Compute every case and time each step. Returns (results, timings)."""
    t, out = {}, {}
    charts = []
    for i, case in enumerate(CASES):
        t0 = time.perf_counter()
        c = chart_obj(dict(case, now=NOW))
        t[f"chart_{i}"] = round(time.perf_counter() - t0, 3)
        charts.append(c)
        out[case["name"]] = fingerprint(c)
    t0 = time.perf_counter()
    m = chart_engine.match_charts(charts[0], charts[1], "B")
    t["match"] = round(time.perf_counter() - t0, 3)
    out["match"] = {"total_36": m["ashtakoota"]["total_36"]["score"], "range": m["ashtakoota"]["total_36"]["range_across_vashya_tables"]}
    t0 = time.perf_counter()
    mu = muhurta.find(MUHURTA["event"], MUHURTA["from"], MUHURTA["to"], MUHURTA["lat"], MUHURTA["lon"], MUHURTA["tz"],
                      [muhurta.person_from_chart(charts[0]), muhurta.person_from_chart(charts[1])], 10, 12)
    t["muhurta_3_months"] = round(time.perf_counter() - t0, 3)
    out["muhurta"] = [w["start_local"] for w in mu["all_windows"]]
    t0 = time.perf_counter()
    nc = name_correction.suggest("Ravi Shankar Tiwari", "1988-07-14")
    t["names"] = round(time.perf_counter() - t0, 3)
    out["names"] = [s["spelling"] for s in nc["suggestions"]]
    return out, t


def _time_forecast(t):
    """Add the three-year forecast for the first test person to a timings dict (not compared with the snapshot)."""
    t0 = time.perf_counter()
    forecast(json.dumps(dict(CASES[0], now="2027-01-14", years=3)))
    t["forecast_3_years"] = round(time.perf_counter() - t0, 3)
    return t


def timings():
    """Run the suite and return only the timings, as JSON (for the spike screen)."""
    _, t = run_suite()
    _time_forecast(t)
    return json.dumps({"timings_s": t, "import_s": round(IMPORT_SECONDS, 3)})


def selftest(snapshot_json):
    """Compare this device's results with the desktop snapshot. Returns a JSON report."""
    expected = json.loads(snapshot_json)
    got, timings = run_suite()
    _time_forecast(timings)
    mismatches = []
    for k, v in expected["results"].items():
        if got.get(k) != v:
            mismatches.append({"case": k, "expected": v, "got": got.get(k)})
    return json.dumps({
        "ok": not mismatches, "mismatches": mismatches, "timings_s": timings,
        "import_s": round(IMPORT_SECONDS, 3), "python": sys.version.split()[0],
        "engine_version": open(os.path.join(HERE, "ENGINE_VERSION.txt")).read().strip()
        if os.path.exists(os.path.join(HERE, "ENGINE_VERSION.txt")) else "unknown",
        "ephe_files": sorted(os.listdir(os.environ["SE_EPHE_PATH"])) if os.path.isdir(os.environ["SE_EPHE_PATH"]) else [],
        "base_rates_present": os.path.exists(os.path.join(HERE, "yoga_base_rates.json")),
        "tempdir": tempfile.gettempdir(),
    }, ensure_ascii=False)


def make_snapshot():
    """Run on the desktop to produce the expected results (tools/make_snapshot.py)."""
    got, timings = run_suite()
    return {"results": got, "desktop_timings_s": timings, "python": sys.version.split()[0]}
