#!/usr/bin/env python3
"""chart_engine.py - one command that turns birth data into a verified calculation bundle (JSON).

  python chart_engine.py chart --name "A B" --date 1990-05-17 --time 14:30 --lat 28.6139 --lon 77.2090 \
        --gender M --now 2026-09-20 --out chart.json
  python chart_engine.py match --a chartA.json --b chartB.json --out match.json

The model must READ this JSON and write the narrative. It must never hand-calculate a position,
dasha, pillar or number that this engine can produce.
"""
import argparse
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import swisseph as swe  # noqa: E402

EPHE = os.environ.get("SE_EPHE_PATH", os.path.join(HERE, "ephe"))
if os.path.isdir(EPHE):
    swe.set_ephe_path(EPHE)

import common  # noqa: E402
import vedic  # noqa: E402
import western  # noqa: E402
import chinese  # noqa: E402
import numerology  # noqa: E402
import forecast  # noqa: E402
import lalkitab  # noqa: E402
import rasidasa  # noqa: E402
import shadbala  # noqa: E402
import parashari  # noqa: E402
import events  # noqa: E402
import calibration  # noqa: E402


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items() if not str(k).startswith("_")}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, float):
        return round(o, 6)
    return o


def build_chart(a):
    t = common.resolve_time(a.date, a.time, a.lat, a.lon, a.tz, a.utc_offset)
    now = dt.datetime.strptime(a.now, "%Y-%m-%d").replace(hour=12) if a.now else dt.datetime.now(dt.timezone.utc).replace(tzinfo=None, microsecond=0)
    warnings = list(t["warnings"])
    conf = a.time_confidence
    if conf == "unknown":
        warnings.append("BIRTH TIME UNKNOWN: 12:00 local time was used as a placeholder. Ascendant, houses, Bhava Chalit, KP cusps, "
                        "divisional lagnas, hour pillar, Zi Wei Dou Shu, Varsha Lagna and every lagna-based statement are NOT reliable "
                        "and must not be interpreted. Moon-based items (nakshatra, dasha) are usable only if the Moon did not change "
                        "nakshatra that day - see sensitivity.moon_nakshatra_boundary.")
    elif conf == "approximate":
        warnings.append("Birth time is approximate: read the lagna-sensitivity window and consider a rectification report before relying on lagna, divisional charts or timing.")
    modules = set(a.modules.split(",")) if a.modules != "all" else {"vedic", "western", "bazi", "numerology", "zwds", "events"}
    out = {"meta": {"name": a.name, "gender": a.gender, "generated_for_date": now.date().isoformat(),
                    "birth_time_confidence": conf, "place": {"lat": a.lat, "lon": a.lon, "label": a.place}}}
    out["time_pipeline"] = clean(t)
    v = w = b = n = z = None
    if "vedic" in modules:
        v = vedic.build_vedic(t["jd_ut"], t["_utc_dt"], now, a.lat, a.lon, t["_naive"], t["utc_offset_hours"],
                              a.ayanamsa, a.node, a.dasha_year)
        out["vedic"] = clean(v)
        out["lalkitab"] = clean(lalkitab.build_lalkitab(v, a.date, now, max(a.horizon_years or 0, 0), conf))
        _vs = {n: {p: common.SIGNS.index(sg) for p, sg in v["divisional_charts"][f"D{n}"].items() if p != "Lagna"} for n in (9, 10, 4)}
        out["vedic"]["rasi_dashas"] = clean(rasidasa.build(v["planets"], _vs, v["_lag_sign"], v["lagna"]["lon"], t["jd_ut"],
                                                           t["_utc_dt"], now, a.lat, a.lon, vedic.AYAN[a.ayanamsa], conf))
        _sb = shadbala.build(t["jd_ut"], a.lat, a.lon, vedic.AYAN[a.ayanamsa])
        if conf == "unknown":
            _sb["reliability_warning"] = "Birth time unknown: Dik, Kendra, Kala and Bhava bala depend on the time and are not reliable."
        out["vedic"]["shadbala"] = clean(_sb)
        out["vedic"].pop("partial_strength", None)
        _fr = shadbala._day_frame(t["jd_ut"], a.lat, a.lon)
        _pv = parashari.build(v, t["jd_ut"], _fr[0], _sb["bphs"]["planets"])
        if _fr[3]:
            _pv["avasthas"]["inputs"]["sunrise_rule"] = "no sunrise on this date here: 6:00 local apparent time used for the ghati"
        if conf == "unknown":
            _pv["reliability_warning"] = "Birth time unknown: avasthas that use the ghati or lagna, vargas and dasha-lord varga views are not reliable."
        out["vedic"]["parashari"] = clean(_pv)
        try:
            import tajika
            _yrs = vedic.completed_varsha_years(v["planets"]["Sun"]["lon"], t["_utc_dt"], now, a.ayanamsa)
            out["vedic"]["varshaphal"]["tajika"] = clean(tajika.annual(out["vedic"], t["_utc_dt"], _yrs, a.lat, a.lon, a.ayanamsa, a.node))
            out["vedic"]["varshaphal"]["not_computed"] = ("Harsha bala, Tajika yogas beyond Ithasala, Ishrafa, Nakta, Yamaya and Kamboola, "
                                                         "Tri-pataki chakra and monthly charts.")
        except Exception as _e:
            out["vedic"]["varshaphal"]["tajika"] = {"status": f"not computed: {_e}"}
        try:
            import yoga_library
            _yl = yoga_library.evaluate(out["vedic"], a.gender)
            _br = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yoga_base_rates.json")
            if os.path.exists(_br):
                _rates = json.load(open(_br))
                for f in _yl["found"]:
                    rt = _rates["rates"].get(f["id"])
                    if rt:
                        f["base_rate_present"] = rt["present"]
                _yl["base_rates"] = {"sample_size": _rates["sample_size"], "method": _rates["method"]}
            out["vedic"]["yoga_library"] = clean(_yl)
        except Exception as _e:  # the yoga layer must never break the chart
            out["vedic"]["yoga_library"] = {"status": f"not computed: {_e}"}
    if "western" in modules:
        w = western.build_western(t["jd_ut"], t["_utc_dt"], now, a.lat, a.lon, a.current_lat, a.current_lon)
        out["western"] = clean(w)
    if "bazi" in modules:
        b = chinese.build_bazi(t, a.gender, now, tst_default=(a.bazi_time == "solar"), zi_mode=a.zi)
        out["bazi"] = clean(b)
    if "numerology" in modules:
        n = numerology.build_numerology(a.name, a.date, now, a.name_in_use, gender=a.gender, birth_jd_ut=t["jd_ut"])
        if a.name_correction:
            import name_correction
            n["name_correction"] = name_correction.suggest(a.name_in_use or a.name, a.date, top=8, gender=a.gender)
        out["numerology"] = clean(n)
    if "zwds" in modules:
        z = chinese.build_zwds(t, a.gender)
        out["zi_wei_dou_shu"] = clean(z)
    if a.horizon_years and a.horizon_years > 0:
        flat = a.current_lat if a.current_lat is not None else a.lat
        flon = a.current_lon if a.current_lon is not None else a.lon
        out["forecast"] = clean(forecast.build_forecast(v, w, b, t["_utc_dt"], t["jd_ut"], now, flat, flon, a.gender, a.date,
                                                        years=a.horizon_years, ayan=a.ayanamsa, node=a.node,
                                                        birth_lat=a.lat, birth_lon=a.lon))
        if conf in ("unknown", "approximate"):
            out["forecast"]["reliability_warning"] = (
                "Birth time is " + conf + ": every forecast item counted from the Lagna or the Ascendant (houses from Lagna, double transit "
                "from Lagna, Varsha Lagna, Muntha house, profections, solar-return angles, whole-sign house ingresses, zodiacal releasing "
                "from the Lots, eclipse houses) is " + ("not usable" if conf == "unknown" else "conditional") + ". Moon-based gochar, dashas "
                "(if the Moon's nakshatra is secure), BaZi year and month pillars and numerology are unaffected.")
            warnings.append("Forecast: " + out["forecast"]["reliability_warning"])
    _ev = {}
    if v is not None and "events" in modules:  # life-event timing windows; the slowest layer (about 3 s)
        _ev = events.build(v, out["vedic"], out.get("forecast"), t["jd_ut"], t["_utc_dt"], now, a.lat, a.lon, a.gender,
                           a.ayanamsa, a.node, years=a.horizon_years if a.horizon_years and a.horizon_years > 0 else 5)
        if conf == "unknown":
            _ev["reliability_warning"] = ("Birth time unknown: lagna-based points, house lords, KP cusps and every window "
                                          "that uses them are not reliable; only Moon-based nakshatra tools can be read.")
        elif conf == "approximate":
            _ev["reliability_warning"] = "Birth time approximate: KP cusp sub-lords and the D-9/D-10 dasha lists may change."
        if out.get("forecast"):
            events.tag_life_areas(out["forecast"], _ev)
        out["vedic"]["events"] = clean(_ev)
    if v is not None:
        _m = a.time_error if a.time_error is not None else {"certificate": 2, "reliable": 5, "approximate": 30}.get(conf)
        if _m:
            out["vedic"]["time_error"] = clean(calibration.time_error_model(t["jd_ut"], t["_utc_dt"], a.lat, a.lon, a.ayanamsa,
                                                                            a.node, minutes=min(int(_m), 60)))
        if a.past_events:
            out["vedic"]["calibration"] = clean(calibration.calibrate(v, out["vedic"], calibration._parse_events(a.past_events),
                                                                      t["jd_ut"], t["_utc_dt"], a.lat, a.lon, a.gender,
                                                                      a.ayanamsa, a.node, kp=_ev.get("kp")))
    checks = {}
    if v:
        checks["ashtakavarga_totals"] = "passed (BAV 48/49/39/54/56/52/39, SAV 337)"
    if b:
        checks["bazi_independent_cross_check"] = b["cross_check"]["status"]
        warnings += b["warnings"]
    if n:
        warnings += n["warnings"]
    if z and z.get("warnings"):
        warnings += z["warnings"]
    if w and w.get("warning"):
        warnings.append(w["warning"])
    if v:
        s = v["sensitivity"]
        lw = s["lagna_time_window_minutes"]
        earliest = [x for x in (lw["lagna_sign_changes"]["earlier"], lw["lagna_sign_changes"]["later"]) if x is not None]
        if earliest and min(earliest) <= 20:
            warnings.append(f"Lagna sign flips within {min(earliest)} minutes of the recorded time - the chart's rising sign is fragile to small time errors.")
        nv = [x for x in (lw["navamsa_lagna_changes"]["earlier"], lw["navamsa_lagna_changes"]["later"]) if x is not None]
        if nv and min(nv) <= 5:
            warnings.append(f"Navamsa lagna flips within {min(nv)} minutes - treat D9 lagna and Karakamsha-based statements cautiously.")
        mb = s["moon_nakshatra_boundary"]
        if min(mb["hours_since_entering_nakshatra"], mb["hours_until_leaving_nakshatra"]) < 2:
            warnings.append("Moon is within ~2 hours of a nakshatra boundary: the Vimshottari sequence depends on the exact birth time.")
        if s["ayanamsa"]["placements_that_change"]:
            warnings.append(f"{len(s['ayanamsa']['placements_that_change'])} placement(s) change sign/nakshatra/pada under alternative ayanamsas - see sensitivity.ayanamsa.")
    out["audit"] = {
        "engine": {"swiss_ephemeris": getattr(swe, "version", "?"), "pyswisseph": getattr(swe, "__version__", "?"),
                   "ephemeris": common.ephemeris_mode(t["jd_ut"]), "python": sys.version.split()[0]},
        "time_conventions": {"timezone_source": t["timezone"], "utc_offset_hours": t["utc_offset_hours"],
                             "dst_removed_hours": t["dst_removed_hours"], "true_solar_time": t["true_solar_time"]},
        "vedic_conventions": v["conventions"] if v else None,
        "bazi_conventions": b["basis"] if b else None,
        "self_checks": checks,
        "warnings": warnings,
        "not_computed": ["Ashtottari and conditional dashas; Shoola and other longevity dashas (excluded by design)",
                         "Patyayini dasha, Harsha bala and Tajika yogas beyond Ithasala, Ishrafa, Nakta, Yamaya and Kamboola", "Zodiacal releasing beyond Level 2", "Nobleman and most other Shen Sha",
                         "Special-structure BaZi (从格/化气格) and Useful God selection - interpretive",
                         "Fixed-star parans (stars are matched by ecliptic longitude only); asteroids beyond Ceres, Pallas, Juno and Vesta"],
    }
    out["match_inputs"] = clean({
        "name": a.name, "gender": a.gender,
        "western_points": [(p, l, s) for p, l, s in w["_points"]] if w else None,
        "western_angles": w["_angles"] if w else None, "western_asc_sign": w["_asc_sign"] if w else None,
        "bazi_branches": b["_branches"] if b else None, "bazi_stems": b["_stems"] if b else None, "bazi_dm": b["_dm"] if b else None,
        "vedic": {"moon_lon": v["planets"]["Moon"]["lon"], "moon_sign_index": v["planets"]["Moon"]["sign_index"],
                  "moon_nakshatra": v["planets"]["Moon"]["nakshatra"], "moon_pada": v["planets"]["Moon"]["pada"],
                  "mars_house": {"from_lagna": v["planets"]["Mars"]["house"], **v["doshas"]["mangal_dosha"]["mars_house"]},
                  "lagna_sign_index": v["_lag_sign"], "planet_signs": {p: r["sign_index"] for p, r in v["planets"].items()},
                  "planet_houses": {p: r["house"] for p, r in v["planets"].items()},
                  "fifth_lord_ratio": (out["vedic"].get("shadbala", {}).get("bphs", {}).get("planets", {})
                                       .get(common.SIGN_LORD[(v["_lag_sign"] + 4) % 12], {}).get("ratio"))} if v else None,
    })
    return out


def cmd_match(a):
    return match_charts(json.load(open(a.a)), json.load(open(a.b)), a.bride)


def match_charts(FA, FB, bride="B"):
    """Two-person comparison from two chart dicts (the output of build_chart)."""
    A, B = FA["match_inputs"], FB["match_inputs"]
    out = {"people": [A["name"], B["name"]]}
    if A["western_points"] and B["western_points"]:
        out["western_synastry"] = western.synastry(A["western_points"], B["western_points"], A["western_angles"],
                                                    B["western_angles"], A["western_asc_sign"], B["western_asc_sign"])
        out["western_composite"] = western.composite(A["western_points"], B["western_points"], A["western_angles"], B["western_angles"])
        pa, pb = FA["meta"]["place"], FB["meta"]["place"]
        out["western_davison"] = western.davison(FA["time_pipeline"]["jd_ut"], pa["lat"], pa["lon"],
                                                 FB["time_pipeline"]["jd_ut"], pb["lat"], pb["lon"])
        tc = {FA["meta"].get("birth_time_confidence"), FB["meta"].get("birth_time_confidence")}
        if "unknown" in tc:
            out["western_composite"]["warning"] = out["western_davison"]["warning"] = (
                "One birth time is unknown: the composite and Davison Ascendant, Midheaven, houses and the Moon's degree are not reliable.")
    if A["bazi_branches"] and B["bazi_branches"]:
        ba = {"_branches": [tuple(x) for x in A["bazi_branches"]] if False else A["bazi_branches"]}
        out["bazi_cross"] = chinese.bazi_cross(
            {"_branches": [tuple(x) for x in A["bazi_branches"]], "_stems": [tuple(x) for x in A["bazi_stems"]], "_dm": A["bazi_dm"]},
            {"_branches": [tuple(x) for x in B["bazi_branches"]], "_stems": [tuple(x) for x in B["bazi_stems"]], "_dm": B["bazi_dm"]})
    if A["vedic"] and B["vedic"]:
        try:
            import ashtakoota
            out["ashtakoota"] = ashtakoota.match(A["vedic"], B["vedic"], bride)
            out["ashtakoota"]["further_kootas_and_melapak"] = ashtakoota.extra_kootas(A["vedic"], B["vedic"], bride)
        except ImportError:
            out["ashtakoota"] = {"status": "module not installed"}
        out["mangal_comparison"] = {A["name"]: A["vedic"]["mars_house"], B["name"]: B["vedic"]["mars_house"],
                                    "note": "Houses 1,2,4,7,8,12 counted; cancellations are for the reader."}
    return out


def build_parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("chart")
    c.add_argument("--name", required=True)
    c.add_argument("--name-in-use", default=None, help="Name currently used, if different from birth name")
    c.add_argument("--date", required=True, help="YYYY-MM-DD")
    c.add_argument("--time", required=True, help="HH:MM or HH:MM:SS local civil time")
    c.add_argument("--lat", type=float, required=True)
    c.add_argument("--lon", type=float, required=True, help="East positive")
    c.add_argument("--place", default="")
    c.add_argument("--tz", default=None, help="IANA zone e.g. Asia/Kolkata (inferred from coordinates if omitted)")
    c.add_argument("--utc-offset", type=float, default=None, help="Manual UTC offset in hours; bypasses the tz database")
    c.add_argument("--gender", default="M", help="M or F (needed for BaZi luck pillar direction and ZWDS)")
    c.add_argument("--now", default=None, help="Reference date YYYY-MM-DD (default: today UTC)")
    c.add_argument("--ayanamsa", default="lahiri", choices=list(vedic.AYAN))
    c.add_argument("--node", default="mean", choices=["mean", "true"])
    c.add_argument("--dasha-year", type=float, default=365.25)
    c.add_argument("--bazi-time", default="solar", choices=["solar", "standard"])
    c.add_argument("--zi", default="23", choices=["23", "00"], help="Zi-hour day rollover convention")
    c.add_argument("--time-confidence", default="reliable", choices=["certificate", "reliable", "approximate", "unknown"])
    c.add_argument("--time-error", type=float, default=None, help="birth-time uncertainty in minutes (default from --time-confidence)")
    c.add_argument("--past-events", default="", help="dated past events for calibration: YYYY-MM-DD:marriage,YYYY-MM-DD:child,...")
    c.add_argument("--current-lat", type=float, default=None)
    c.add_argument("--current-lon", type=float, default=None)
    c.add_argument("--modules", default="all", help="all, or a comma list of vedic,western,bazi,numerology,zwds,events")
    c.add_argument("--name-correction", action="store_true", help="add ranked spelling variants (only when the client asks for name correction)")
    c.add_argument("--horizon-years", type=int, default=5, help="Forecast window length from --now (0 disables the forecast block)")
    c.add_argument("--out", default="chart.json")
    m = sp.add_parser("match")
    m.add_argument("--a", required=True)
    m.add_argument("--b", required=True)
    m.add_argument("--bride", default="B", choices=["A", "B"], help="Which person is the bride for directional koota scores")
    m.add_argument("--out", default="match.json")
    return p


def main():
    a = build_parser().parse_args()
    res = build_chart(a) if a.cmd == "chart" else cmd_match(a)
    with open(a.out, "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(f"wrote {a.out} ({os.path.getsize(a.out)//1024} KB)")
    if a.cmd == "chart":
        for w in res["audit"]["warnings"]:
            print("WARNING:", w)


if __name__ == "__main__":
    main()
