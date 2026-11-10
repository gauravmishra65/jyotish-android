"""app_rectify.py - the Birth time check screen (v16): narrow an uncertain birth time with dated life events.

The same groundwork as tools' rectify_windows.py, as a function: the window around the recorded time is cut into
segments in which the Lagna, Navamsa Lagna and Dashamsa Lagna stay the same; each dated event is shown with the
Vimshottari periods running for that segment; with events, each segment is scored by how far its hits exceed chance
(calibration.score_segments). It never picks a time: the screen says that the astrologer and the family judge.
Only positive life events are offered (marriage, child, career, property, move abroad, education).
"""
import datetime as dt
import json

import calibration
import common
import hindi_shell as HS
import vedic

KINDS = {"marriage": ("Marriage", "विवाह"), "child": ("Birth of a child", "संतान का जन्म"), "job": ("Job or promotion", "नौकरी या पदोन्नति"),
         "property": ("Bought a home", "घर ख़रीदा"), "abroad": ("Moved abroad", "विदेश गए"), "education": ("Degree completed", "डिग्री पूरी हुई")}


def rectify(req):
    window = max(10, min(int(req.get("window_min", 30)), 120))
    ayan = req.get("ayanamsa") or "lahiri"
    t = common.resolve_time(req["date"], req["time"], float(req["lat"]), float(req["lon"]), req.get("tz"), None)
    base_jd, base_utc, naive = t["jd_ut"], t["_utc_dt"], t["_naive"]
    lat, lon = float(req["lat"]), float(req["lon"])
    events = []
    for e in req.get("events", []):
        kind = e.get("kind")
        if kind in KINDS and e.get("date"):
            events.append((dt.datetime.fromisoformat(e["date"][:10]).replace(hour=12), kind))

    def key_at(m):
        jd = base_jd + m / 1440.0
        asc = vedic._asc_at(jd, lat, lon, ayan)
        return asc, (common.sign_of(asc), vedic.varga_sign(asc, 9), vedic.varga_sign(asc, 10))

    segs, cur = [], None
    for m in range(-window, window + 1):
        asc, key = key_at(m)
        if cur and cur["key"] == key:
            cur["to"] = m
        else:
            if cur:
                segs.append(cur)
            cur = {"key": key, "from": m, "to": m}
    segs.append(cur)
    out_segs = []
    for s in segs:
        mid = (s["from"] + s["to"]) // 2
        jd = base_jd + mid / 1440.0
        utc_mid = base_utc + dt.timedelta(minutes=mid)
        moon = vedic.sidereal_positions(jd, ayan)["Moon"]["lon"]
        lag = s["key"][0]
        rec = {"from": (naive + dt.timedelta(minutes=s["from"])).strftime("%H:%M"),
               "to": (naive + dt.timedelta(minutes=s["to"] + 1)).strftime("%H:%M"),
               "minutes": [s["from"], s["to"]], "contains_recorded": s["from"] <= 0 <= s["to"],
               "lagna": common.SIGNS[lag], "d9": common.SIGNS[s["key"][1]], "d10": common.SIGNS[s["key"][2]],
               "moon_nakshatra": common.nak_info(moon)["name"], "events": []}
        for ev_dt, kind in events:
            cd = vedic.dashas(moon, utc_mid, ev_dt)["vimshottari"]["current"]
            md, ad = cd["mahadasha"]["lord"], cd["antardasha"]["lord"]
            rules = lambda pl: [((i - lag) % 12) + 1 for i in range(12) if vedic.SIGN_LORD[i] == pl]  # noqa: E731
            rec["events"].append({"kind": kind, "date": ev_dt.date().isoformat(), "mahadasha": md, "antardasha": ad,
                                  "md_rules": rules(md), "ad_rules": rules(ad)})
        out_segs.append(rec)
    scored = []
    if events:
        txt = ",".join(f"{d.date().isoformat()}:{k if k != 'job' else 'career'}" for d, k in events)
        try:
            evl = calibration._parse_events(txt)
            raw = calibration.score_segments(base_jd, base_utc, naive, t["utc_offset_hours"], lat, lon,
                                             [{"from_local": s["from"], "to_local": s["to"], "minutes_from_recorded": s["minutes"],
                                               "lagna_sign": s["lagna"], "D9_lagna": s["d9"], "D10_lagna": s["d10"]} for s in out_segs],
                                             evl, req.get("gender", "M"), ayan)
            for r in raw:
                scored.append({"from": r.get("from_local"), "to": r.get("to_local"), "hits": r.get("hits"),
                               "expected": r.get("expected_by_chance"), "p": r.get("chance_of_at_least_these_hits")})
        except Exception as e:      # scoring is a bonus; the segments still stand
            scored = [{"error": str(e)[:200]}]
    return {"recorded": t["local_civil"][11:16], "window_min": window, "segments": out_segs, "scored": scored,
            "kinds": {k: {"en": v[0], "hi": v[1]} for k, v in KINDS.items()},
            "signs_hi": {s: HS.SIGN.get(s, s) for s in common.SIGNS}, "planets_hi": dict(HS.PLANET),
            "naks_hi": {n: HS.NAK.get(n, n) for n in HS.NAK},
            "note": {"en": "Each row is a span of birth times that gives the same Lagna, Navamsa Lagna and Dashamsa Lagna. With dated events, a lower "
                           "chance figure means that span explains the events better than chance. It narrows the time; it does not prove it. "
                           "Confirm with an experienced astrologer.",
                     "hi": "हर पंक्ति जन्म समय की वह अवधि है जिसमें लग्न, नवांश लग्न और दशमांश लग्न एक-से रहते हैं। तिथि-सहित घटनाओं के साथ, कम "
                           "संयोग-अंक का अर्थ है कि वह अवधि घटनाओं को संयोग से बेहतर समझाती है। यह समय को सीमित करता है, सिद्ध नहीं करता। "
                           "किसी अनुभवी ज्योतिषी से पुष्टि करें।"}}


def rectify_json(request_json):
    return json.dumps(rectify(json.loads(request_json)), ensure_ascii=False)
