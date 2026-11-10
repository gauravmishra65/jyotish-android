"""app_reports.py - focused reports beside the full Life reading: Daily, Monthly, Annual, Mahadasha, Mangal Dosh,
Kaal Sarp, Sade Sati and Chandra Rashi. Each is one self-contained HTML page in English or Hindi, in the same style as
the full reading (app_report), built only from what the engine computes, with fixed wording.

House rules, as everywhere in the app: tendencies, not certainties; no illness, death or divorce is ever named;
remedies are optional practices with no promised outcome, and families are pointed to their own priest or astrologer.
"""
import datetime as dt
import json
import re
from zoneinfo import ZoneInfo

import swisseph as swe

import app_details as AD
import app_details_more as ADM
import app_report as AR
import app_today as AT
import hindi_shell as HS
import vedic
from app_report import E, R, table, para, callout, bullets, section, sub, initials
from app_report import pill as _pill
from app_report_style import CSS, JS

SIGNS = AR.SIGNS
PILL_CLASS = {"good": "none", "mixed": "mild", "care": "moderate"}


def pill(kind, label):
    return _pill(PILL_CLASS.get(kind, kind), label)


NINE = AR.NINE
KINDS = ("daily", "monthly", "annual", "mahadasha", "mangal", "kaal_sarp", "sade_sati", "chandra")

TITLES = {
    "daily": ("Daily Report", "दैनिक रिपोर्ट"),
    "monthly": ("Monthly Report", "मासिक रिपोर्ट"),
    "annual": ("Annual Report", "वार्षिक रिपोर्ट"),
    "mahadasha": ("Mahadasha Report", "महादशा रिपोर्ट"),
    "mangal": ("Mangal Dosh Report", "मंगल दोष रिपोर्ट"),
    "kaal_sarp": ("Kaal Sarp Dosh Report", "काल सर्प दोष रिपोर्ट"),
    "sade_sati": ("Sade Sati Report", "साढ़े साती रिपोर्ट"),
    "chandra": ("Chandra Rashi Report", "चंद्र राशि रिपोर्ट"),
}
SARPA_BY_HOUSE = ["Anant", "Kulik", "Vasuki", "Shankhpal", "Padma", "Mahapadma", "Takshak", "Karkotak", "Shankhachud",
                  "Ghatak", "Vishdhar", "Sheshnag"]
VIM_YEARS = ADM.VIM_YEARS
VIM_ORDER = ADM.VIM_ORDER
GOOD_HOUSES = {1, 4, 5, 7, 9, 10, 11}
HARD_HOUSES = {6, 8, 12}


# ------------------------------------------------------------------ shared pieces
def _sign_index(s):
    return SIGNS.index(s)


def _house_from(base_sign, sign):
    return (_sign_index(sign) - _sign_index(base_sign)) % 12 + 1


def _ruled_houses(v, planet):
    return [h["house"] for h in v["houses"] if h["lord"] == planet]


def _dignity(v, p):
    d = v["planets"][p].get("dignity") or ""
    return "" if d in ("n/a", "neutral sign") else d


def _tone(r, v, p):
    """A calm word for how a planet's period tends to feel, from its house and dignity (a tendency, not a verdict)."""
    pl = v["planets"][p]
    h, dig = pl["house"], _dignity(v, p)
    score = (1 if h in GOOD_HOUSES else -1 if h in HARD_HOUSES else 0) + (1 if dig in ("exalted", "own sign", "moolatrikona") else
                                                                        -1 if dig == "debilitated" else 0)
    if score >= 1:
        return pill("good", r.t("supportive", "अनुकूल"))
    if score <= -1:
        return pill("care", r.t("asks for effort", "प्रयास माँगती है"))
    return pill("mixed", r.t("mixed", "मिश्रित"))


def _vim_sub(lord, start, end):
    """The nine sub-periods of a Vimshottari period [start, end] starting from its own lord: [(lord, from, to)]."""
    a, b = dt.date.fromisoformat(start[:10]), dt.date.fromisoformat(end[:10])
    total = (b - a).days
    i0 = VIM_ORDER.index(lord)
    out, t, acc = [], a, 0
    for k in range(9):
        lk = VIM_ORDER[(i0 + k) % 9]
        acc += VIM_YEARS[lk]
        e = a + dt.timedelta(days=round(total * acc / 120))
        out.append((lk, t.isoformat(), e.isoformat()))
        t = e
    return out


def _antardashas(v):
    """Every (mahadasha lord, antardasha lord, from, to), from the chart's Vimshottari list."""
    out = []
    for m in v["dashas"]["vimshottari"]["mahadashas"]:
        subs = m.get("antardashas") or [(x[0], x[1], x[2]) for x in _vim_sub(m["lord"], m["start"], m["end"])]
        for a in subs:
            if isinstance(a, dict):
                out.append((m["lord"], a["lord"], a["start"], a["end"]))
            else:
                out.append((m["lord"],) + tuple(a))
    return out


def _dasha_on(v, iso):
    for md, ad, a, b in _antardashas(v):
        if a <= iso < b:
            pd = next(((l, x, y) for l, x, y in _vim_sub(ad, a, b) if x <= iso < y), None)
            return md, ad, pd
    return None, None, None


def _place_for_day(req):
    if req.get("today_lat") is not None:
        return float(req["today_lat"]), float(req["today_lon"]), req.get("today_tz") or req["tz"], req.get("today_place", "")
    if req.get("current_lat") is not None:
        return float(req["current_lat"]), float(req["current_lon"]), req["tz"], req.get("residence", "")
    return float(req["lat"]), float(req["lon"]), req["tz"], req.get("place", "")


def _person(c):
    v = c["vedic"]
    return {"name": c["meta"]["name"], "moon_lon": v["planets"]["Moon"]["lon"], "lagna_lon": v["lagna"]["lon"]}


def _sid_sign(jd, body):
    return int(AT._sid(jd, body)[0] // 30)


def _rahu_sign(jd):
    return int((swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] % 360) // 30)


def _ingresses(start, days, bodies, tz):
    """Sign changes of the given bodies over the days from start (noon to noon): [(date, planet, new sign)]."""
    out = []
    def jd_of(d):
        return swe.julday(d.year, d.month, d.day, 12.0)
    prev = {p: (_rahu_sign(jd_of(start)) if p == "Rahu" else _sid_sign(jd_of(start), b)) for p, b in bodies}
    for i in range(1, days + 1):
        d = start + dt.timedelta(days=i)
        for p, b in bodies:
            s = _rahu_sign(jd_of(d)) if p == "Rahu" else _sid_sign(jd_of(d), b)
            if s != prev[p]:
                out.append((d.isoformat(), p, SIGNS[s]))
                if p == "Rahu":
                    out.append((d.isoformat(), "Ketu", SIGNS[(s + 6) % 12]))
                prev[p] = s
    return out


SLOW = [("Jupiter", swe.JUPITER), ("Saturn", swe.SATURN), ("Rahu", None)]
FAST = [("Sun", swe.SUN), ("Mars", swe.MARS), ("Mercury", swe.MERCURY), ("Venus", swe.VENUS)] + SLOW


# ------------------------------------------------------------------ page
def _page(r, kind, ctx, sections, intro):
    t = r.t
    title_en, title_hi = TITLES[kind]
    lines = [(t("PREPARED FOR", "हेतु तैयार"), E(ctx["name"])), (t("PREPARED BY", "द्वारा तैयार"), E(ctx["by"])),
             (t("DATE", "तिथि"), r.date(ctx["now"])), (t("REPORT REFERENCE", "रिपोर्ट संदर्भ"), ctx["ref"])]
    cover = f"""
<section class="cover-page">
  <div class="cover-title-1">{t("Gaurav Jyotish", "गौरव ज्योतिष")}</div>
  <div class="cover-title-2">{t(title_en, title_hi)}</div>
  <p class="cover-sub">{intro}</p>
  <div class="divider">&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&nbsp; &#10022; &nbsp;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;</div>
  <div class="cover-lines">{"".join(f'<div class="cover-line"><span class="label">{a}</span><span class="value">{b}</span></div>' for a, b in lines)}</div>
  <div class="cover-site">{E(ctx["site"])}</div>
  <p class="cover-foot-note">{t("Prepared for personal guidance and reflection. Tendencies, not certainties.", "व्यक्तिगत मार्गदर्शन और चिंतन हेतु। झुकाव, निश्चितता नहीं।")}</p>
</section>"""
    body = "".join(section(i + 1, title, inner) for i, (title, inner) in enumerate(sections))
    close = section(len(sections) + 1, t("Please note", "कृपया ध्यान दें"), para(
        t("Astrology describes tendencies and timing; it does not decide outcomes. Use this report alongside your own judgement, and for "
          "important decisions also the advice of people who know your situation. Remedies are optional practices with no promised result.",
          "ज्योतिष झुकाव और समय बताता है; परिणाम तय नहीं करता। इस रिपोर्ट को अपनी समझ के साथ पढ़ें, और महत्वपूर्ण निर्णयों में उन लोगों की सलाह भी लें "
          "जो आपकी स्थिति जानते हैं। उपाय वैकल्पिक अभ्यास हैं; इनसे किसी परिणाम का वादा नहीं है।"),
        t(f"Prepared with Gaurav Jyotish: Swiss Ephemeris, {ctx['ayan']} ayanamsa, whole-sign houses.",
          f"गौरव ज्योतिष द्वारा तैयार: स्विस एफ़ेमेरिस, {ctx['ayan']} अयनांश, पूर्ण राशि भाव।")))
    nav = [(i + 1, s[0]) for i, s in enumerate(sections)]
    return f"""<!DOCTYPE html>
<html lang="{'hi' if r.hi else 'en'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(ctx['name'])} — {t(title_en, title_hi)}</title><style>{CSS}</style></head>
<body>
<div id="progress"></div>
<div id="topbar">
  <div class="brand">{E(ctx['by'])}<span class="site">&nbsp;·&nbsp;{E(ctx['site'])}</span></div>
  <nav>{"".join(f'<a href="#sec{i}">{i} · {lab}</a>' for i, lab in nav)}</nav>
</div>
{cover}{body}{close}
<script>{JS}</script>
</body></html>"""


def _birth_block(r, c, ctx):
    v = c["vedic"]
    t = r.t
    moon = v["planets"]["Moon"]
    rows = [[t("Name", "नाम"), E(ctx["name"])], [t("Born", "जन्म"), f"{r.date(ctx['date'])}, {E(ctx['time'])}"],
            [t("Place", "स्थान"), E(ctx["place"])], [t("Lagna", "लग्न"), r.S(v["lagna"]["sign"])],
            [t("Moon sign and nakshatra", "चंद्र राशि और नक्षत्र"), f"{r.S(moon['sign'])}, {r.N(moon['nakshatra'])} {t('pada', 'पद')} {moon['pada']}"]]
    md, ad, pd = _dasha_on(v, ctx["now"])
    if md:
        rows.append([t("Dasha now", "चालू दशा"), f"{r.P(md)} – {r.P(ad)}" + (f" – {r.P(pd[0])}" if pd else "")])
    return table([t("Detail", "विवरण"), t("Value", "मान")], rows)


# ------------------------------------------------------------------ Daily
def daily(r, c, req, ctx):
    t = r.t
    lat, lon, tz, place = _place_for_day(req)
    now_local = req.get("now_time")
    q = {"date": ctx["now"], "lat": lat, "lon": lon, "tz": tz, "place": place, "ayanamsa": req.get("ayanamsa") or "lahiri",
         "festival_days": 7, "person": _person(c)}
    if now_local:
        q["now"] = now_local
    o = json.loads(AT.today(json.dumps(q)))
    k = r.lang_key()
    p = o["panchang"]
    pr = o["periods"]
    pe = o["person"]
    s1 = [para(f"<b>{E(pe['guidance'][k])}</b>"),
          table([t("Check", "जाँच"), t("Today", "आज")], [
              [t("Tarabala", "तारा बल"), f"{E(pe['tarabala']['tara'][k])} · " + (pill("good", t("favourable", "अनुकूल")) if pe["tarabala"]["ok"] else pill("care", t("not favourable", "अनुकूल नहीं")))],
              [t("Chandrabala", "चंद्र बल"), t(f"house {pe['chandrabala']['house']} from the birth Moon", f"जन्म चंद्र से {pe['chandrabala']['house']}वाँ भाव") + " · " +
               (pill("good", t("favourable", "अनुकूल")) if pe["chandrabala"]["ok"] else pill("care", t("not favourable", "अनुकूल नहीं")))],
              [t("Moon today", "आज चंद्र"), f"{E(pe['moon_transit']['sign'][k])}, " + t(f"house {pe['moon_transit']['house_from_lagna']} from the Lagna", f"लग्न से {pe['moon_transit']['house_from_lagna']}वाँ भाव")],
          ] + ([[t("Saturn", "शनि"), E(pe["saturn"]["phase"][k])]] if pe["saturn"].get("phase") else []))]
    s2 = [table([t("Element", "अंग"), t("Today", "आज"), t("Until", "तक")], [
        [t("Tithi", "तिथि"), f"{E(p['tithi']['name'][k])} ({E(p['tithi']['paksha'][k])})", p["tithi"]["ends"] or "–"],
        [t("Nakshatra", "नक्षत्र"), E(p["nakshatra"]["name"][k]), p["nakshatra"]["ends"] or "–"],
        [t("Yoga", "योग"), E(p["yoga"]["name"][k]), p["yoga"]["ends"] or "–"],
        [t("Karana", "करण"), E(p["karana"]["name"][k]), p["karana"]["ends"] or "–"],
        [t("Weekday", "वार"), E(p["weekday"][k]), ""],
        [t("Month (amanta / purnimanta)", "मास (अमांत / पूर्णिमांत)"), f"{E(p['month_amanta'][k])} / {E(p['month_purnimanta'][k])}", ""],
        [t("Sunrise · sunset", "सूर्योदय · सूर्यास्त"), f"{o['sun']['rise'] or '–'} · {o['sun']['set'] or '–'}", ""],
    ]), para(t(f"For {E(place)} (UTC{o['utc_offset']}).", f"{E(place)} के लिए (UTC{o['utc_offset']})।"))]
    s3 = []
    if "rahu_kalam" in pr:
        s3.append(table([t("Period", "काल"), t("Time", "समय"), ""], [
            [t("Brahma muhurta", "ब्रह्म मुहूर्त"), f"{pr['brahma_muhurta']['from']} – {pr['brahma_muhurta']['to']}", pill("good", t("good", "शुभ")) if "brahma_muhurta" in pr else ""],
            [t("Abhijit muhurta", "अभिजित मुहूर्त"), f"{pr['abhijit']['from']} – {pr['abhijit']['to']}", pill("good", t("good", "शुभ")) if not pr["abhijit"].get("wednesday") else t("(not on Wednesdays)", "(बुधवार को नहीं)")],
            [t("Rahu Kaal", "राहु काल"), f"{pr['rahu_kalam']['from']} – {pr['rahu_kalam']['to']}", pill("care", t("avoid for beginnings", "शुरुआत के लिए टालें"))],
            [t("Yamaganda", "यमगंड"), f"{pr['yamaganda']['from']} – {pr['yamaganda']['to']}", pill("care", t("avoid for beginnings", "शुरुआत के लिए टालें"))],
            [t("Gulika Kaal", "गुलिक काल"), f"{pr['gulika_kalam']['from']} – {pr['gulika_kalam']['to']}", pill("care", t("avoid for beginnings", "शुरुआत के लिए टालें"))],
        ]))
        kind_word = {"good": pill("good", t("good", "शुभ")), "neutral": pill("mixed", t("neutral", "सामान्य")), "avoid": pill("care", t("avoid", "वर्जित"))}
        s3.append(sub("", t("Choghadiya (day)", "चौघड़िया (दिन)")))
        s3.append(table([t("Time", "समय"), t("Choghadiya", "चौघड़िया"), ""], [[f"{x['from']} – {x['to']}", E(x["name"][k]), kind_word[x["kind"]]] for x in pr["choghadiya_day"]]))
        s3.append(sub("", t("Choghadiya (night)", "चौघड़िया (रात)")))
        s3.append(table([t("Time", "समय"), t("Choghadiya", "चौघड़िया"), ""], [[f"{x['from']} – {x['to']}", E(x["name"][k]), kind_word[x["kind"]]] for x in pr["choghadiya_night"]]))
    else:
        s3.append(para(E(pr.get("status", ""))))
    s4 = [table([t("Planet", "ग्रह"), t("Sign", "राशि"), t("From Lagna", "लग्न से"), t("From Moon", "चंद्र से")],
                [[E(x["planet"][k]) + (t(" (R)", " (व)") if x["retrograde"] else ""), f"{E(x['sign'][k])} {x['deg']:.0f}°", x["house_from_lagna"], x["house_from_moon"]] for x in pe["transits"]])]
    fest = [f for f in o["festivals"] if not f["monthly"] or f["key"] in ("ekadashi_s", "ekadashi_k", "purnima", "amavasya")]
    s5 = [table([t("Date", "तिथि"), t("Festival or vrat", "त्योहार या व्रत")], [[r.date(f["date"]), E(f["name"][k])] for f in fest])
          if fest else para(t("No festival in the next seven days.", "अगले सात दिनों में कोई त्योहार नहीं।"))]
    return [(t("Your day", "आपका दिन"), "".join(s1)), (t("Panchang", "पंचांग"), "".join(s2)),
            (t("Good and avoided times", "शुभ और वर्जित समय"), "".join(s3)), (t("Planets over the chart", "कुंडली के ऊपर ग्रह"), "".join(s4)),
            (t("This week's festivals", "इस सप्ताह के त्योहार"), "".join(s5))]


# ------------------------------------------------------------------ Monthly
def monthly(r, c, req, ctx):
    t = r.t
    v = c["vedic"]
    lat, lon, tz_name, place = _place_for_day(req)
    tz = ZoneInfo(tz_name)
    swe.set_sid_mode(vedic.AYAN.get(req.get("ayanamsa") or "lahiri", swe.SIDM_LAHIRI))
    start = dt.date.fromisoformat(ctx["now"])
    first = start.replace(day=1)
    nxt = (first + dt.timedelta(days=32)).replace(day=1)
    days = (nxt - first).days
    person = _person(c)
    bnak = int(person["moon_lon"] // AT.NAK_SPAN)
    msign = int(person["moon_lon"] // 30)
    fest = {}
    for f in AT.festivals(first, days - 1, lat, lon, tz):
        if not f["monthly"] or f["key"] in ("ekadashi_s", "ekadashi_k", "purnima", "amavasya", "sankranti"):
            fest.setdefault(f["date"], []).append(f["name"][r.lang_key()])
    rows, good_days, routine_days = [], [], []
    for i in range(days):
        d = first + dt.timedelta(days=i)
        day = AT.Day(d, lat, lon, tz)
        jd = day.sunrise or day.jd_mid + 0.25
        ti = AT._tithi(jd)
        tp = ti if ti <= 15 else ti - 15
        tname = ((t("Purnima", "पूर्णिमा") if ti == 15 else t("Amavasya", "अमावस्या")) if tp == 15 else t(AT.TITHI_EN[tp - 1], AT.TITHI_HI[tp - 1]))
        pk = t("S", "शु") if ti <= 15 else t("K", "कृ")
        nk = AT._nak(jd)
        r9 = ((nk - bnak) % 27 + 1) % 9 or 9
        tara_ok = r9 not in (3, 5, 7)
        ch = (int(AT._sid(jd, swe.MOON)[0] // 30) - msign) % 12 + 1
        ch_ok = ch in (1, 3, 6, 7, 10, 11) or (ti <= 15 and ch in (2, 5, 9))
        mark = pill("good", t("good", "शुभ")) if tara_ok and ch_ok else pill("mixed", t("mixed", "मिश्रित")) if tara_ok or ch_ok else pill("care", t("routine", "सामान्य कार्य"))
        (good_days if tara_ok and ch_ok else routine_days if not (tara_ok or ch_ok) else []).append(d)
        wd = d.weekday()
        rows.append([f"{d.day} {t(AT.WD_EN[wd][:3], AT.WD_HI[wd])}", f"{tname} ({pk})", r.N(AT.NAKSHATRAS[nk]), mark, E(" · ".join(fest.get(d.isoformat(), [])))])
    month_name = r.month(first.isoformat())
    s1 = [para(t(f"Good days for beginnings this month (Tarabala and Chandrabala both favourable): ", "इस माह शुरुआत के लिए शुभ दिन (तारा बल और चंद्र बल दोनों अनुकूल): ") +
               (", ".join(str(d.day) for d in good_days) or t("none", "कोई नहीं")) + "."),
          para(t("Days marked routine are better for ongoing work and preparation than for new beginnings.",
                 "'सामान्य कार्य' वाले दिन नई शुरुआत की बजाय चल रहे काम और तैयारी के लिए बेहतर हैं।"))]
    s2 = [table([t("Day", "दिन"), t("Tithi (sunrise)", "तिथि (सूर्योदय)"), t("Nakshatra", "नक्षत्र"), t("For you", "आपके लिए"), t("Festival", "त्योहार")], rows),
          para(t(f"Panchang at sunrise for {E(place)}. S = Shukla, K = Krishna paksha.", f"{E(place)} के सूर्योदय का पंचांग। शु = शुक्ल, कृ = कृष्ण पक्ष।"))]
    ing = _ingresses(first - dt.timedelta(days=1), days, FAST, tz)
    lag = v["lagna"]["sign"]
    moon = v["planets"]["Moon"]["sign"]
    s3 = [table([t("Date", "तिथि"), t("Planet", "ग्रह"), t("Enters", "प्रवेश"), t("House from Lagna", "लग्न से भाव"), t("From Moon", "चंद्र से")],
                [[r.date(d), r.P(p), r.S(s), _house_from(lag, s), _house_from(moon, s)] for d, p, s in ing])
          if ing else para(t("No planet changes sign this month.", "इस माह कोई ग्रह राशि नहीं बदलता।"))]
    changes = []
    for md, ad, a, b in _antardashas(v):
        for lk, x, y in _vim_sub(ad, a, b):
            if first.isoformat() <= x < nxt.isoformat():
                changes.append([r.date(x), f"{r.P(md)} – {r.P(ad)} – {r.P(lk)}"])
    md, ad, pd = _dasha_on(v, first.isoformat())
    s4 = [para(t(f"At the start of {month_name}: ", "माह के आरंभ में: ") + (f"{r.P(md)} – {r.P(ad)} – {r.P(pd[0])}" if pd else "–") + "."),
          table([t("From", "से"), t("Period (maha – antar – pratyantar)", "अवधि (महा – अंतर – प्रत्यंतर)")], changes) if changes else ""]
    return [(t(f"{month_name} at a glance", f"{month_name} एक नज़र में"), "".join(s1)),
            (t("Day by day", "दिन-प्रतिदिन"), "".join(s2)), (t("Planets changing sign", "राशि बदलते ग्रह"), "".join(s3)),
            (t("Dasha this month", "इस माह की दशा"), "".join(s4))]


# ------------------------------------------------------------------ Annual
def annual(r, c, req, ctx, fc):
    t = r.t
    v = c["vedic"]
    k = r.lang_key()
    start = dt.date.fromisoformat(ctx["now"])
    end = start + dt.timedelta(days=365)
    swe.set_sid_mode(vedic.AYAN.get(req.get("ayanamsa") or "lahiri", swe.SIDM_LAHIRI))
    s1 = []
    if fc:
        rows = []
        for a in fc["areas"]:
            y1 = next((y for y in a["years"] if y["id"] == "Y1"), None)
            if y1:
                lean = {"supportive": pill("good", t("supportive", "अनुकूल")), "demanding": pill("care", t("demanding", "चुनौतीपूर्ण")),
                        "mixed": pill("mixed", t("mixed", "मिश्रित"))}.get(y1["lean"], pill("mixed", t("quiet", "शांत")))
                rows.append([E(a["title"][k]), lean, E(AD.safe(y1["summary"][k]))])
        s1.append(table([t("Area", "क्षेत्र"), t("This year", "यह वर्ष"), t("In short", "संक्षेप में")], rows))
        s1.append(para(t("From the three-year forecast; a theme is marked only where several systems agree.", "तीन वर्ष के भविष्यफल से; कोई बात तभी उभारी गई है जब कई पद्धतियाँ सहमत हों।")))
    vs = next((s for s in (c.get("details") or AD.build(c))["sections"] if s["key"] == "varshaphal"), None)
    s2 = AR.detail_html(r, vs) if vs else para(t("Varshaphal is not available for this chart.", "इस कुंडली के लिए वर्षफल उपलब्ध नहीं।"))
    lag, moon = v["lagna"]["sign"], v["planets"]["Moon"]["sign"]
    ing = _ingresses(start, 365, SLOW, ZoneInfo(req["tz"]))
    s3 = [table([t("Date", "तिथि"), t("Planet", "ग्रह"), t("Enters", "प्रवेश"), t("House from Lagna", "लग्न से भाव"), t("From Moon", "चंद्र से")],
                [[r.date(d), r.P(p), r.S(s), _house_from(lag, s), _house_from(moon, s)] for d, p, s in ing])
          if ing else para(t("Jupiter, Saturn and Rahu–Ketu stay in their signs all year.", "गुरु, शनि और राहु–केतु पूरे वर्ष अपनी राशियों में रहते हैं।")),
          para(t("Jupiter moving through houses 2, 5, 7, 9 or 11 from the Moon is traditionally helpful; Saturn's slow transits reward patient effort.",
                 "चंद्र से 2, 5, 7, 9 या 11वें भाव में गुरु का गोचर परंपरा से सहायक माना जाता है; शनि का धीमा गोचर धैर्यपूर्ण परिश्रम का फल देता है।"))]
    months = []
    for i in range(12):
        m0 = (start.replace(day=1) + dt.timedelta(days=32 * i)).replace(day=1)
        mid = (m0 + dt.timedelta(days=14)).isoformat()
        md, ad, pd = _dasha_on(v, mid)
        jd = swe.julday(m0.year, m0.month, 15, 12.0)
        js, ss = SIGNS[_sid_sign(jd, swe.JUPITER)], SIGNS[_sid_sign(jd, swe.SATURN)]
        months.append([r.month(m0.isoformat()), f"{r.P(md)} – {r.P(ad)}" + (f" – {r.P(pd[0])}" if pd else ""),
                       f"{r.S(js)} ({_house_from(moon, js)})", f"{r.S(ss)} ({_house_from(moon, ss)})"])
    s4 = [table([t("Month", "माह"), t("Dasha (mid-month)", "दशा (मध्य माह)"), t("Jupiter (house from Moon)", "गुरु (चंद्र से भाव)"),
                 t("Saturn (house from Moon)", "शनि (चंद्र से भाव)")], months)]
    ss_ = v.get("sade_sati", {})
    cyc = [x for x in ss_.get("cycles_in_window", []) if x["start"] <= end.isoformat() and x["end"] >= start.isoformat()]
    s5 = [para(t("Sade Sati runs during part of this year: ", "इस वर्ष के कुछ भाग में साढ़े साती चल रही है: ") +
               ", ".join(f"{r.date(x['start'])} – {r.date(x['end'])}" for x in cyc) + "." if cyc else
               t("Sade Sati does not run this year.", "इस वर्ष साढ़े साती नहीं चल रही।"))]
    return [(t("The year at a glance", "वर्ष एक नज़र में"), "".join(s1) or para("–")), (t("Varshaphal (this year's chart)", "वर्षफल (इस वर्ष की कुंडली)"), s2),
            (t("Major transits", "प्रमुख गोचर"), "".join(s3)), (t("Month by month", "माह-दर-माह"), "".join(s4)),
            (t("Saturn this year", "इस वर्ष शनि"), "".join(s5))]


# ------------------------------------------------------------------ Mahadasha
def mahadasha(r, c, req, ctx):
    t = r.t
    v = c["vedic"]
    now = ctx["now"]
    mds = v["dashas"]["vimshottari"]["mahadashas"]
    rows = []
    for m in mds:
        p = m["lord"]
        cur = m["start"] <= now < m["end"]
        rows.append(([f"{r.date(m['start'])} – {r.date(m['end'])}", r.P(p) + (t(" (current)", " (चालू)") if cur else ""), r.length(m["start"], m["end"]),
                      r.house(v["planets"][p]["house"]), _tone(r, v, p)], {"cls": "hl" if cur else ""}))
    s1 = [para(t("Vimshottari dasha divides life into nine planetary periods. The first is only the balance left at birth.",
                 "विंशोत्तरी दशा जीवन को नौ ग्रह-अवधियों में बाँटती है। पहली दशा जन्म के समय बची हुई अवधि ही है।")),
          table([t("Period", "अवधि"), t("Mahadasha", "महादशा"), t("Length", "अवधि"), t("Lord sits in", "स्वामी स्थित"), t("Tends to be", "प्रायः")], rows)]
    secs = [(t("All mahadashas", "सभी महादशाएँ"), "".join(s1))]
    for m in mds:
        if m["end"] <= now:
            continue
        p = m["lord"]
        pl = v["planets"][p]
        ruled = _ruled_houses(v, p)
        dig = _dignity(v, p)
        text = [t(f"{p} is placed in {r.S(pl['sign'])}, in the {r.hth(pl['house'])}", f"{r.P(p)} {r.S(pl['sign'])} में, {r.hth(pl['house'])} में स्थित है") +
                (t(f", {dig}", f", {r.tag(dig)}") if dig else "") + "." +
                (t(f" It rules the {r.houses(ruled)}.", f" यह {r.houses(ruled)} का स्वामी है।") if ruled else ""),
                t(f"Its period brings forward {r.theme(p)}, and the matters of the houses it sits in and rules.",
                  f"इसकी अवधि {r.theme(p)} को आगे लाती है, और उन भावों के विषयों को जिनमें यह स्थित है और जिनका यह स्वामी है।"),
                E(r.mean("planet", p))]
        ads = [(lk, x, y) for md_, lk, x, y in _antardashas(v) if md_ == p]
        ad_rows = [([f"{r.date(x)} – {r.date(y)}", r.P(lk) + (t(" (current)", " (चालू)") if x <= now < y else ""), _tone(r, v, lk)],
                    {"cls": "hl" if x <= now < y else ""}) for lk, x, y in ads]
        inner = para(*text) + sub("", t("Antardashas", "अंतर्दशाएँ")) + table([t("Period", "अवधि"), t("Antardasha", "अंतर्दशा"), t("Tends to be", "प्रायः")], ad_rows)
        if m["start"] <= now < m["end"]:
            cur = next(((lk, x, y) for lk, x, y in ads if x <= now < y), None)
            if cur:
                pds = _vim_sub(cur[0], cur[1], cur[2])
                inner += sub("", t(f"Pratyantar dashas of {cur[0]}", f"{r.P(cur[0])} की प्रत्यंतर दशाएँ")) + table(
                    [t("Period", "अवधि"), t("Pratyantar", "प्रत्यंतर")],
                    [([f"{r.date(x)} – {r.date(y)}", r.P(lk) + (t(" (current)", " (चालू)") if x <= now < y else "")], {"cls": "hl" if x <= now < y else ""}) for lk, x, y in pds])
        secs.append((t(f"{p} mahadasha", f"{r.P(p)} महादशा") + f" ({m['start'][:4]}–{m['end'][:4]})", inner))
        if len(secs) >= 5:
            break
    return secs


# ------------------------------------------------------------------ Mangal Dosh
def mangal(r, c, req, ctx):
    t = r.t
    v = c["vedic"]
    m = v["doshas"]["mangal_dosha"]
    mars = v["planets"]["Mars"]
    h, pres = m["mars_house"], m["present_by_reference"]
    refs = [(t("Lagna", "लग्न"), h["from_lagna"], pres["from_lagna"]), (t("Moon", "चंद्र"), h["from_moon"], pres["from_moon"]),
            (t("Venus", "शुक्र"), h["from_venus"], pres["from_venus"])]
    any_present = any(x[2] for x in refs)
    s1 = [para(t("Mangal Dosh is counted when Mars is in the 1st, 2nd, 4th, 7th, 8th or 12th house from the Lagna, the Moon or Venus. "
                 "Some South Indian schools leave out the 2nd.", "मंगल दोष तब माना जाता है जब मंगल लग्न, चंद्र या शुक्र से 1, 2, 4, 7, 8 या 12वें भाव में हो। "
                 "कुछ दक्षिण भारतीय परंपराएँ 2रे भाव को नहीं गिनतीं।")),
          table([t("Counted from", "से गिनती"), t("Mars in house", "मंगल भाव"), t("Mangal Dosh", "मंगल दोष")],
                [[a, b, pill("care", t("present", "उपस्थित")) if p_ else pill("good", t("not present", "उपस्थित नहीं"))] for a, b, p_ in refs]),
          callout(t("In this chart", "इस कुंडली में"), t("Mangal Dosh is present from: ", "मंगल दोष उपस्थित है: ") + ", ".join(a for a, _, p_ in refs if p_) + "."
                  if any_present else t("Mangal Dosh is not present from the Lagna, the Moon or Venus.", "लग्न, चंद्र या शुक्र से मंगल दोष उपस्थित नहीं है।"), orange=any_present)]
    sign = mars["sign"]
    hl = h["from_lagna"]
    jup = v["planets"]["Jupiter"]
    jup_aspects = {(jup["house"] + k - 2) % 12 + 1 for k in (5, 7, 9)} | {jup["house"]}
    checks = [
        (t("Mars in its own sign (Aries, Scorpio) or exalted (Capricorn)", "मंगल स्वराशि (मेष, वृश्चिक) या उच्च (मकर) में"), sign in ("Aries", "Scorpio", "Capricorn")),
        (t("Jupiter with Mars or aspecting it", "गुरु मंगल के साथ या उस पर दृष्टि"), mars["house"] in jup_aspects),
        (t("A house-and-sign exception from the common list (2nd in Gemini or Virgo, 4th in Aries or Scorpio, 7th in Cancer or Capricorn, "
           "8th in Sagittarius or Pisces, 12th in Taurus or Libra)", "सामान्य सूची का भाव-राशि अपवाद (2रे में मिथुन या कन्या, 4थे में मेष या वृश्चिक, 7वें में कर्क या मकर, "
           "8वें में धनु या मीन, 12वें में वृषभ या तुला)"),
         (hl == 2 and sign in ("Gemini", "Virgo")) or (hl == 4 and sign in ("Aries", "Scorpio")) or (hl == 7 and sign in ("Cancer", "Capricorn")) or
         (hl == 8 and sign in ("Sagittarius", "Pisces")) or (hl == 12 and sign in ("Taurus", "Libra"))),
        (t("Mars in Leo or Aquarius (cited by some texts)", "मंगल सिंह या कुंभ में (कुछ ग्रंथों में)"), sign in ("Leo", "Aquarius")),
    ]
    s2 = [para(t("The classical texts list several conditions that cancel or soften Mangal Dosh. Families and astrologers differ on which they accept.",
                 "शास्त्रों में कई स्थितियाँ बताई गई हैं जो मंगल दोष को निरस्त या हल्का करती हैं। परिवार और ज्योतिषी इनमें से किन्हें मानते हैं, इसमें मतभेद है।")),
          table([t("Condition", "स्थिति"), t("In this chart", "इस कुंडली में")],
                [[a, pill("good", t("yes", "हाँ")) if ok else t("no", "नहीं")] for a, ok in checks]),
          para(t("Many families also hold that the effect softens after the age of 28.", "कई परिवार यह भी मानते हैं कि 28 वर्ष की आयु के बाद इसका प्रभाव हल्का हो जाता है।"))]
    s3 = [bullets([
        t("In Kundli Milan, Mangal Dosh in both charts is traditionally taken to balance out. Use the app's Milan screen to check a pair.",
          "कुंडली मिलान में दोनों कुंडलियों में मंगल दोष हो तो परंपरा से इसे संतुलित माना जाता है। किसी जोड़े की जाँच के लिए ऐप का मिलान स्क्रीन देखें।"),
        t("Mars stands for energy and courage. Channel it into sport, work and clear communication rather than haste.",
          "मंगल ऊर्जा और साहस का प्रतीक है। इसे जल्दबाज़ी की बजाय खेल, काम और स्पष्ट संवाद में लगाएँ।"),
        t("Optional practices many families follow: Hanuman Chalisa on Tuesdays, the Mangal mantra 'Om Angarakaya Namah', donating red lentils on Tuesdays. "
          "Ask your family priest before any ritual.", "कई परिवार ये वैकल्पिक अभ्यास करते हैं: मंगलवार को हनुमान चालीसा, मंगल मंत्र 'ॐ अंगारकाय नमः', मंगलवार को मसूर दाल का दान। "
          "किसी अनुष्ठान से पहले अपने पारिवारिक पुरोहित से पूछें।"),
    ])]
    return [(t("Mangal Dosh in this chart", "इस कुंडली में मंगल दोष"), "".join(s1)), (t("Cancellations", "परिहार"), "".join(s2)),
            (t("Guidance", "मार्गदर्शन"), "".join(s3))]


# ------------------------------------------------------------------ Kaal Sarp
def kaal_sarp(r, c, req, ctx):
    t = r.t
    v = c["vedic"]
    k = v["doshas"]["kaal_sarp"]
    rahu_h = v["planets"]["Rahu"]["house"]
    name = SARPA_BY_HOUSE[rahu_h - 1]
    state = "present" if k.get("present") else "partial" if k.get("partial") else "absent"
    s1 = [para(t("Kaal Sarp is the pattern in which all seven planets lie on one side of the Rahu–Ketu axis.",
                 "काल सर्प वह स्वरूप है जिसमें सातों ग्रह राहु–केतु अक्ष के एक ही ओर हों।")),
          table([t("Detail", "विवरण"), t("In this chart", "इस कुंडली में")], [
              [t("Pattern", "स्वरूप"), {"present": pill("care", t("present", "उपस्थित")), "partial": pill("mixed", t("partial (not counted)", "आंशिक (नहीं गिना जाता)")),
                                         "absent": pill("good", t("not present", "उपस्थित नहीं"))}[state]],
              [t("Rahu in", "राहु"), f"{r.S(v['planets']['Rahu']['sign'])}, {r.house(rahu_h)}"],
              [t("Ketu in", "केतु"), f"{r.S(v['planets']['Ketu']['sign'])}, {r.house(v['planets']['Ketu']['house'])}"],
          ] + ([[t("Type by Rahu's house", "राहु के भाव से प्रकार"), t(name, HS.SARPA.get(name, name))]] if state == "present" else []) +
              ([[t("Planet outside the axis", "अक्ष के बाहर का ग्रह"), ", ".join(r.P(p) for p in k.get("planet_outside_axis", []))]] if state == "partial" else []))]
    if state == "present":
        msg = t(f"The full pattern is present ({name} type). Many charts with this pattern show strong drive and late but lasting results; it is one factor among many.",
                f"पूरा स्वरूप उपस्थित है ({HS.SARPA.get(name, name)} प्रकार)। इस स्वरूप वाली कई कुंडलियों में प्रबल लगन और देर से पर टिकाऊ परिणाम दिखते हैं; यह कई कारकों में से एक है।")
    elif state == "partial":
        msg = t("Only a partial pattern: at least one planet lies outside the axis, so it is not counted as Kaal Sarp Dosh.",
                "केवल आंशिक स्वरूप: कम से कम एक ग्रह अक्ष के बाहर है, इसलिए इसे काल सर्प दोष नहीं गिना जाता।")
    else:
        msg = t("The planets lie on both sides of the Rahu–Ketu axis, so there is no Kaal Sarp Dosh.", "ग्रह राहु–केतु अक्ष के दोनों ओर हैं, इसलिए काल सर्प दोष नहीं है।")
    s1.append(callout(t("In this chart", "इस कुंडली में"), msg, orange=state == "present"))
    s2 = [bullets([
        t("Rahu shows where ambition and the unusual pull you; Ketu shows where you are already skilled and may detach.",
          "राहु दिखाता है कि महत्वाकांक्षा और असामान्य चीज़ें आपको कहाँ खींचती हैं; केतु दिखाता है कि आप कहाँ पहले से कुशल हैं और विरक्त हो सकते हैं।"),
        t(f"Rahu here works through the {r.hth(rahu_h)}.", f"यहाँ राहु {r.hth(rahu_h)} के माध्यम से काम करता है।"),
        t("Optional practices many families follow: Shiva puja on Mondays or on Nag Panchami, chanting 'Om Namah Shivaya', a Rahu–Ketu shanti puja at a temple. "
          "Ask your family priest before any ritual.", "कई परिवार ये वैकल्पिक अभ्यास करते हैं: सोमवार या नाग पंचमी को शिव पूजा, 'ॐ नमः शिवाय' का जाप, मंदिर में राहु–केतु शांति पूजा। "
          "किसी अनुष्ठान से पहले अपने पारिवारिक पुरोहित से पूछें।"),
    ])]
    return [(t("Kaal Sarp in this chart", "इस कुंडली में काल सर्प"), "".join(s1)), (t("Guidance", "मार्गदर्शन"), "".join(s2))]


# ------------------------------------------------------------------ Sade Sati
def sade_sati(r, c, req, ctx):
    t = r.t
    v = c["vedic"]
    ss = v.get("sade_sati", {})
    now = ctx["now"]
    moon = v["planets"]["Moon"]["sign"]
    sat = v["planets"]["Saturn"]
    phase_word = {"rising": t("first phase (Saturn 12th from the Moon)", "पहला चरण (चंद्र से 12वाँ शनि)"),
                  "peak": t("middle phase (Saturn over the Moon)", "मध्य चरण (चंद्र पर शनि)"),
                  "setting": t("last phase (Saturn 2nd from the Moon)", "अंतिम चरण (चंद्र से दूसरा शनि)")}
    def phase_of(pos):
        return "rising" if "rising" in pos else "peak" if "peak" in pos else "setting"
    cur = None
    for cy in ss.get("cycles_in_window", []):
        for ph in cy["phases"]:
            if ph["from"] <= now < ph["to"]:
                cur = (cy, ph)
    if cur:
        status = t("Sade Sati is running now: ", "साढ़े साती अभी चल रही है: ") + phase_word[phase_of(cur[1]["position"])] + \
                 t(f", until {r.date(cur[0]['end'])}.", f", {r.date(cur[0]['end'])} तक।")
    elif ss.get("ashtama_shani_now"):
        status = t("Sade Sati is not running; Saturn is 8th from the Moon (Ashtama Shani).", "साढ़े साती नहीं चल रही; शनि चंद्र से आठवें (अष्टम शनि) है।")
    elif ss.get("kantaka_shani_now"):
        status = t("Sade Sati is not running; Saturn is 4th from the Moon (Kantaka Shani).", "साढ़े साती नहीं चल रही; शनि चंद्र से चौथे (कंटक शनि) है।")
    else:
        status = t("Sade Sati is not running now.", "साढ़े साती अभी नहीं चल रही।")
    s1 = [para(t(f"Sade Sati is the seven and a half years in which Saturn passes through the sign before your Moon sign ({r.S(SIGNS[(_sign_index(moon) - 1) % 12])}), "
                 f"the Moon sign itself ({r.S(moon)}) and the sign after it ({r.S(SIGNS[(_sign_index(moon) + 1) % 12])}).",
                 f"साढ़े साती वे साढ़े सात वर्ष हैं जब शनि आपकी चंद्र राशि से पहली राशि ({r.S(SIGNS[(_sign_index(moon) - 1) % 12])}), "
                 f"चंद्र राशि ({r.S(moon)}) और उसके बाद की राशि ({r.S(SIGNS[(_sign_index(moon) + 1) % 12])}) से गुज़रता है।")),
          callout(t("Now", "अभी"), status, orange=bool(cur))]
    rows = []
    for cy in ss.get("cycles_in_window", []):
        merged = []
        for ph in cy["phases"]:
            ph_key = phase_of(ph["position"])
            if merged and merged[-1][0] == ph_key:
                merged[-1][2] = ph["to"]
            else:
                merged.append([ph_key, ph["from"], ph["to"]])
        for ph_key, a, b in merged:
            rows.append(([f"{r.date(a)} – {r.date(b)}", phase_word[ph_key], r.S(SIGNS[(_sign_index(moon) + {'rising': -1, 'peak': 0, 'setting': 1}[ph_key]) % 12])],
                         {"cls": "hl" if a <= now < b else ""}))
    s2 = [table([t("Dates", "तिथियाँ"), t("Phase", "चरण"), t("Saturn in", "शनि")], rows) if rows else para(t("No Sade Sati in the window computed.", "गणना की अवधि में साढ़े साती नहीं।")),
          para(t("Saturn moves back and forth near sign edges, so a phase can begin, pause and resume; the dates are Saturn's sign changes.",
                 "राशि-संधि के पास शनि आगे-पीछे चलता है, इसलिए कोई चरण शुरू होकर रुक और फिर शुरू हो सकता है; तिथियाँ शनि के राशि परिवर्तन की हैं।"))]
    dig = _dignity(v, "Saturn")
    s3 = [para(t(f"Natal Saturn is in {r.S(sat['sign'])}, in the {r.hth(sat['house'])}", f"जन्म का शनि {r.S(sat['sign'])} में, {r.hth(sat['house'])} में है") +
               (t(f", {dig}", f", {r.tag(dig)}") if dig else "") + ". " +
               (t("A well-placed Saturn usually makes Sade Sati a period of steady, rewarded effort.", "अच्छी स्थिति का शनि प्रायः साढ़े साती को स्थिर और फलदायी परिश्रम का समय बनाता है।")
                if dig in ("exalted", "own sign", "moolatrikona") or sat["house"] in (3, 6, 10, 11) else
                t("Patience, routine and honest work are the classic way to meet Saturn's periods.", "धैर्य, नियमितता और ईमानदार परिश्रम शनि की अवधियों का पारंपरिक उत्तर हैं।")))]
    s4 = [bullets([
        t("The first phase often brings changes in expenses and routine; the middle phase asks for steadiness of mind; the last phase settles money and family matters.",
          "पहला चरण प्रायः व्यय और दिनचर्या में बदलाव लाता है; मध्य चरण मन की स्थिरता माँगता है; अंतिम चरण धन और परिवार के विषयों को स्थिर करता है।"),
        t("Keep commitments realistic, look after rest and sleep, and avoid shortcuts.", "प्रतिबद्धताएँ व्यावहारिक रखें, आराम और नींद का ध्यान रखें, और शॉर्टकट से बचें।"),
        t("Optional practices many families follow: Hanuman Chalisa or Shani mantra 'Om Sham Shanaishcharaya Namah' on Saturdays, lighting a sesame-oil lamp, "
          "helping workers and the elderly. Ask your family priest before any ritual.",
          "कई परिवार ये वैकल्पिक अभ्यास करते हैं: शनिवार को हनुमान चालीसा या शनि मंत्र 'ॐ शं शनैश्चराय नमः', तिल के तेल का दीपक, श्रमिकों और बुज़ुर्गों की सहायता। "
          "किसी अनुष्ठान से पहले अपने पारिवारिक पुरोहित से पूछें।"),
    ])]
    return [(t("Sade Sati now", "अभी साढ़े साती"), "".join(s1)), (t("Sade Sati cycles", "साढ़े साती के चक्र"), "".join(s2)),
            (t("Your natal Saturn", "जन्म का शनि"), "".join(s3)), (t("Guidance", "मार्गदर्शन"), "".join(s4))]


# ------------------------------------------------------------------ Chandra Rashi
def chandra(r, c, req, ctx):
    t = r.t
    v = c["vedic"]
    k = r.lang_key()
    moon = v["planets"]["Moon"]
    sign = moon["sign"]
    trait = AR.SIGN_TRAIT.get(sign, ("", ""))
    pc = v["panchang"]
    paksha = "Shukla" if pc["tithi_number_1_30"] <= 15 else "Krishna"
    dig = _dignity(v, "Moon")
    s1 = [callout(t(f"Moon sign: {sign}", f"चंद्र राशि: {r.S(sign)}"), t(f"{sign} Moon: {trait[0]}.", f"{r.S(sign)} का चंद्र: {trait[1]}।")),
          para(t("In Vedic astrology the Moon sign (rashi) describes the mind and feelings, and it is the sign used for daily horoscopes, Sade Sati and Kundli Milan.",
                 "वैदिक ज्योतिष में चंद्र राशि मन और भावनाओं का वर्णन करती है, और यही राशि दैनिक राशिफल, साढ़े साती और कुंडली मिलान में ली जाती है।"),
               E(r.mean("planet", "Moon")))]
    av = ADM.avakahada(v)
    s2 = AR.detail_html(r, av)
    s3 = [table([t("Detail", "विवरण"), t("Value", "मान")], [
        [t("Moon's house from the Lagna", "लग्न से चंद्र का भाव"), r.hth(moon["house"])],
        [t("Dignity", "स्थिति"), r.tag(dig) if dig else t("neutral", "सम")],
        [t("Born in", "जन्म"), t(f"{paksha} paksha ({'waxing' if paksha == 'Shukla' else 'waning'} Moon)", f"{'शुक्ल' if paksha == 'Shukla' else 'कृष्ण'} पक्ष ({'बढ़ता' if paksha == 'Shukla' else 'घटता'} चंद्र)")],
        [t("Rashi lord", "राशि स्वामी"), f"{r.P(moon['sign_lord'])}: {r.theme(moon['sign_lord'])}"],
        [t("Nakshatra lord", "नक्षत्र स्वामी"), f"{r.P(moon['nakshatra_lord'])}: {r.theme(moon['nakshatra_lord'])}"],
    ])]
    swe.set_sid_mode(vedic.AYAN.get(req.get("ayanamsa") or "lahiri", swe.SIDM_LAHIRI))
    d = dt.date.fromisoformat(ctx["now"])
    jd = swe.julday(d.year, d.month, d.day, 12.0)
    rows = []
    for p, b in (("Jupiter", swe.JUPITER), ("Saturn", swe.SATURN), ("Rahu", None)):
        s = SIGNS[_rahu_sign(jd) if p == "Rahu" else _sid_sign(jd, b)]
        hm = _house_from(sign, s)
        good = {"Jupiter": {2, 5, 7, 9, 11}, "Saturn": {3, 6, 11}, "Rahu": {3, 6, 11}}[p]
        rows.append([r.P(p), r.S(s), hm, pill("good", t("traditionally helpful", "परंपरा से सहायक")) if hm in good else pill("mixed", t("ordinary", "सामान्य"))])
    s4 = [table([t("Planet", "ग्रह"), t("Now in", "अभी"), t("House from the Moon", "चंद्र से भाव"), ""], rows),
          para(t("Gochar (transits) is read from the Moon sign. Jupiter in the 2nd, 5th, 7th, 9th or 11th, and Saturn or Rahu in the 3rd, 6th or 11th, are the classic helpful positions.",
                 "गोचर चंद्र राशि से पढ़ा जाता है। गुरु 2, 5, 7, 9 या 11वें, और शनि या राहु 3, 6 या 11वें — ये पारंपरिक सहायक स्थितियाँ हैं।"))]
    return [(t("Your Moon sign", "आपकी चंद्र राशि"), "".join(s1)), (t("Avakahada chakra and name syllable", "अवकहड़ा चक्र और नामाक्षर"), s2),
            (t("The Moon in your chart", "आपकी कुंडली में चंद्र"), "".join(s3)), (t("Gochar from the Moon now", "अभी चंद्र से गोचर"), "".join(s4))]


INTRO = {
    "daily": ("The day's panchang, good times and how the day sits with your chart.", "दिन का पंचांग, शुभ समय और दिन आपकी कुंडली के साथ कैसा है।"),
    "monthly": ("Each day of the month for you, the planets changing sign and the dasha periods.", "माह का हर दिन आपके लिए, राशि बदलते ग्रह और दशा अवधियाँ।"),
    "annual": ("The year ahead: life areas, Varshaphal, major transits and month-by-month dashas.", "आने वाला वर्ष: जीवन-क्षेत्र, वर्षफल, प्रमुख गोचर और माह-दर-माह दशा।"),
    "mahadasha": ("Your Vimshottari periods: every mahadasha, its antardashas and the current pratyantar.", "आपकी विंशोत्तरी अवधियाँ: हर महादशा, उसकी अंतर्दशाएँ और चालू प्रत्यंतर।"),
    "mangal": ("Mars from the Lagna, the Moon and Venus, with the classical cancellations.", "लग्न, चंद्र और शुक्र से मंगल, शास्त्रीय परिहारों के साथ।"),
    "kaal_sarp": ("The Rahu–Ketu axis and whether the planets form the Kaal Sarp pattern.", "राहु–केतु अक्ष और क्या ग्रह काल सर्प स्वरूप बनाते हैं।"),
    "sade_sati": ("Saturn's seven and a half years over your Moon sign: when, which phase, and how to meet it.", "आपकी चंद्र राशि पर शनि के साढ़े सात वर्ष: कब, कौन-सा चरण और कैसे सामना करें।"),
    "chandra": ("Your Moon sign, nakshatra, name syllable and the transits read from the Moon.", "आपकी चंद्र राशि, नक्षत्र, नामाक्षर और चंद्र से पढ़ा गया गोचर।"),
}


def build(kind, c, req, lang="en", by="Gaurav Mishra", site="authorgaurav.com", fc=None):
    if kind not in KINDS:
        raise ValueError(f"unknown report {kind}")
    r = R(lang == "hi")
    now = c["meta"]["generated_for_date"]
    ctx = {"name": req["name"], "date": req["date"], "time": req["time"], "place": req.get("place", ""), "now": now, "by": by, "site": site,
           "ayan": {"lahiri": r.t("Lahiri", "लाहिरी"), "raman": r.t("Raman", "रमन"), "krishnamurti": "KP", "true_chitra": r.t("True Chitra", "ट्रू चित्रा")}.get(
               req.get("ayanamsa") or "lahiri", "Lahiri"),
           "ref": f"{initials(by)}/{now[:4]}/{initials(req['name'])}-{kind[:3].upper()}"}
    head = (r.t("Birth details", "जन्म विवरण"), _birth_block(r, c, ctx))
    fn = {"daily": daily, "monthly": monthly, "mahadasha": mahadasha, "mangal": mangal, "kaal_sarp": kaal_sarp,
          "sade_sati": sade_sati, "chandra": chandra}.get(kind)
    secs = annual(r, c, req, ctx, fc) if kind == "annual" else fn(r, c, req, ctx)
    if r.hi:   # times past midnight carry "(11 Nov)" from the day engine; give the month in Hindi
        mon = dict(zip(("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"), AR.MON_HI))
        secs = [(a, re.sub(r"\((\d{1,2}) ([A-Z][a-z]{2})\)", lambda m: f"({m.group(1)} {mon.get(m.group(2), m.group(2))})", b)) for a, b in secs]
    page = _page(r, kind, ctx, [head] + secs, r.t(*INTRO[kind]))
    return page
