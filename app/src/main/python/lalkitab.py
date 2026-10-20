"""lalkitab.py - Lal Kitab (1952) layer built on the vedic whole-sign chart.

In Lal Kitab house 1 always counts as Aries (sign 1), so the Lal Kitab house of a planet is simply its whole-sign house from
the lagna (vedic.planets[P].house). Signs and degrees are not used. All rules below cite the book page; tables live in
lalkitab_data.py. Nothing here predicts outcomes by itself: it reports what the book says applies to this chart.
"""
import datetime as dt

import lalkitab_data as D

PAPI = ("Saturn", "Rahu", "Ketu")
H = D.HI
RIN_CAUSE_HI = {"Jupiter": "कुल पुरोहित से बुरा बर्ताव, पुश्तैनी घर के पास मंदिर या पीपल नष्ट होना",
                "Sun": "पुरानी रस्मों और धर्म की अवहेलना; घर में आसमान की ओर खुले चूल्हे या सुराख़",
                "Moon": "औलाद होने के बाद माता की उपेक्षा; पड़ोस के कुएँ या नाले में गंदगी भरना",
                "Venus": "लालच में किसी गर्भवती स्त्री को कष्ट; परिवार में गाय या जानवर रखने से नफ़रत",
                "Mars": "किसी दोस्त को ज़हर देना या पकी फ़सल जलाना; जन्म और त्योहारों पर रिश्तेदारों को दूर रखना",
                "Mercury": "किसी लड़की या बहन से धोखा या ज़ुल्म; लालच में बच्चों का सौदा",
                "Saturn": "धोखे से मकान या ज़मीन हथियाना; जायदाद के लिए जीव हत्या",
                "Rahu": "ससुराल या दुनियावी रिश्तों से धोखा जिससे किसी का घर उजड़ा",
                "Ketu": "कुत्ते मरवाना, या लालच में किसी का वंश नष्ट करना"}


def _hn(h):
    return ((h - 1) % 12) + 1


def _age(birth, on):
    yrs = on.year - birth.year - ((on.month, on.day) < (birth.month, birth.day))
    return yrs


def _birthday(birth, year):
    try:
        return dt.date(year, birth.month, birth.day)
    except ValueError:            # 29 Feb
        return dt.date(year, 3, 1)


def kundli(v):
    pos = {p: int(v["planets"][p]["house"]) for p in D.PLANETS}
    houses = {h: [p for p in D.PLANETS if pos[p] == h] for h in range(1, 13)}
    return pos, houses


def aspected_by(houses):
    """house -> list of (from_house, planets, strength%) that aspect it (p.102-107)."""
    out = {h: [] for h in range(1, 13)}
    for src, tgts in D.DRISHTI.items():
        if houses[src]:
            for t, pc in tgts:
                out[t].append((src, houses[src], pc))
    return out


def sleeping(pos, houses):
    """p.96-99. Returns (planet -> (awake, reason)), sleeping houses."""
    asp = aspected_by(houses)
    lower_empty = all(not houses[h] for h in range(1, 7))
    upper_empty = all(not houses[h] for h in range(7, 13))
    res = {}
    for p in D.PLANETS:
        h = pos[p]
        if h in D.PAKKA_GHAR.get(p, []):
            res[p] = (True, "in its pakka ghar (permanent house) - always awake", "पक्के घर में - हमेशा जागता")
            continue
        reasons, rh = [], []
        if h in D.DRISHTI and not any(houses[t] for t, _ in D.DRISHTI[h]):
            rh.append("जिन घरों (%s) पर इसकी नज़र है वे खाली हैं" % ", ".join(str(t) for t, _ in D.DRISHTI[h]))
            reasons.append("the house%s it aspects (%s) %s empty" % (
                "s" if len(D.DRISHTI[h]) > 1 else "", ", ".join(str(t) for t, _ in D.DRISHTI[h]),
                "are" if len(D.DRISHTI[h]) > 1 else "is"))
        if h >= 7 and lower_empty:
            reasons.append("houses 1-6 are all empty"); rh.append("खाना 1-6 सब खाली")
        if h <= 6 and upper_empty:
            reasons.append("houses 7-12 are all empty"); rh.append("खाना 7-12 सब खाली")
        if h == 2 and not houses[10]:
            reasons.append("house 10 is empty"); rh.append("खाना 10 खाली")
        if h in (1, 9) and not houses[2]:
            reasons.append("house 2 is empty"); rh.append("खाना 2 खाली")
        res[p] = (False, "; ".join(reasons), "; ".join(rh)) if reasons else (True, "", "")
    sleeping_houses = [h for h in range(1, 13) if not houses[h] and not asp[h]]
    return res, sleeping_houses, asp


def status_of(p, h):
    s = []
    if p in D.UCHCH[h]:
        s.append("uchch")
    if p in D.NEECH[h]:
        s.append("neech")
    if h in D.PAKKA_GHAR.get(p, []):
        s.append("pakka_ghar")
    if p in D.HOUSE_LORD[h]:
        s.append("own_house")
    if D.KISMAT_JAGANE_WALA[h] == p:
        s.append("kismat_jagane_wala")
    return s


def masnui(houses):
    out = []
    for h in range(1, 13):
        ps = set(houses[h])
        for (a, b), res, note in D.MASNUI:
            if a in ps and b in ps:
                out.append({"house": h, "from": [a, b], "acts_as": res, "note": note})
    return out


def mangal_bad(pos, houses):
    ind = []
    for h in range(1, 13):
        ps = set(houses[h])
        if {"Sun", "Saturn"} <= ps:
            ind.append(("Sun and Saturn together in house %d make an artificial Mars-bad (p.27)" % h,
                        "खाना %d में सूर्य-शनि साथ: मसनूई मंगल बद" % h))
        if {"Mars", "Mercury"} <= ps or {"Mars", "Ketu"} <= ps:
            e = "Mercury" if "Mercury" in ps else "Ketu"
            ind.append(("Mars with its enemy %s in house %d (p.31)" % (e, h), "खाना %d में मंगल के साथ दुश्मन %s" % (h, H[e])))
    if pos["Mars"] in (4, 8):
        ind.append(("Mars in house %d - the book calls this Mars-bad / manglik (pp.494, 512)" % pos["Mars"],
                    "मंगल खाना %d में - किताब इसे मंगल बद / मंगलीक कहती है" % pos["Mars"]))
    return ind


def teva(pos, houses):
    """p.226 chart types. Each item: type, label/why/upay in English and Hindi."""
    t = []

    def add(typ, label, label_hi, why, why_hi, upay, upay_hi):
        t.append({"type": typ, "label": label, "label_hi": label_hi, "why": why, "why_hi": why_hi, "upay": upay, "upay_hi": upay_hi})

    for a, b in D.ANDHA_PAIRS:
        if a in houses[10] and b in houses[10]:
            add("andha", "Andha (blind) teva", "अंधा टेवा", "%s and %s together in house 10" % (a, b),
                "खाना 10 में %s और %s साथ" % (H[a], H[b]),
                "Feed ten blind people at one time (p.226).", "दस अंधों को एक ही वक्त भोजन खिलाना।")
            break
    if pos["Saturn"] == 7 and pos["Sun"] == 4:
        add("ardh_andha", "Half-blind teva", "अर्ध अंधा टेवा", "Saturn in 7 and Sun in 4", "शनि खाना 7 और सूर्य खाना 4", "", "")
    kendra = [houses[h] for h in (1, 4, 7, 10)]
    if all(all(p in ("Mercury",) + PAPI for p in ps) for ps in kendra):
        add("nabalig", "Nabalig (minor) teva", "नाबालिग टेवा",
            "houses 1, 4, 7 and 10 are empty or hold only Mercury / papi planets",
            "खाना 1, 4, 7, 10 खाली हैं या उनमें सिर्फ़ बुध / पापी ग्रह हैं",
            "The book counts such a chart 'minor' for life and advises going forward with others' help (p.226).",
            "किताब के अनुसार ऐसा टेवा सारी उम्र नाबालिग गिना जाता है; दूसरों की सहायता लेकर चलते रहना मदद देगा।")
    if pos["Mercury"] == 6 and pos["Sun"] in (1, 5, 11):
        add("balig", "Balig (adult) teva", "बालिग टेवा", "Mercury in 6 with Sun in %d" % pos["Sun"],
            "बुध खाना 6 और सूर्य खाना %d" % pos["Sun"], "Its effect runs by itself; no effort is needed (p.226).",
            "इसका असर खुद-बख़ुद होता रहता है, कोशिश की ज़रूरत नहीं।")
    papi_moon4 = pos["Moon"] == 4 and any(pos[p] == 4 for p in ("Rahu", "Ketu"))
    if pos["Saturn"] == 11 or pos["Jupiter"] == 7 or papi_moon4:
        why, why_hi = (("Saturn in 11", "शनि खाना 11") if pos["Saturn"] == 11 else
                       ("Jupiter in 7", "बृहस्पति खाना 7") if pos["Jupiter"] == 7 else ("Rahu/Ketu with Moon in 4", "चंद्र के साथ राहु/केतु खाना 4"))
        add("dharmi", "Dharmi (religious) teva", "धर्मी टेवा", why, why_hi,
            "The book says a dharmi teva helps and comforts everyone around it (p.226).",
            "धर्मी टेवे वाले हर किसी के लिए मददगार और सुख देने वाले होते हैं।")
    if pos["Jupiter"] == pos["Venus"]:
        add("guru_shukra", "Jupiter and Venus together", "बृहस्पति-शुक्र साथ", "both in house %d" % pos["Jupiter"],
            "दोनों खाना %d में" % pos["Jupiter"], "The book: after age 42 the shocks of past lives no longer come (p.226).",
            "42 साल की उम्र के बाद पिछले जन्मों के धक्कों का डर न होगा।")
    return t


def rin(pos, houses):
    out = []
    for p, (hs, enemies, name, name_hi, cause) in D.RIN.items():
        hits, hits_hi = [], []
        for h in hs:
            for e in enemies:
                e0 = e.rstrip("*")
                if e0 not in houses[h]:
                    continue
                if p == "Jupiter" and e0 == "Saturn":
                    continue
                if e.endswith("*") and not any(x in houses[h] for x in ("Rahu", "Ketu")):
                    continue
                hits.append("%s in house %d" % (e0, h)); hits_hi.append("%s खाना %d में" % (H[e0], h))
            if p == "Jupiter" and "Saturn" in houses[h] and any(x in houses[h] for x in ("Rahu", "Ketu")):
                hits.append("Saturn as papi (with Rahu/Ketu) in house %d" % h); hits_hi.append("पापी शनि (राहु/केतु के साथ) खाना %d में" % h)
        if hits:
            out.append({"planet": p, "rin": name, "rin_hi": name_hi, "triggers": hits, "triggers_hi": hits_hi, "book_cause": cause,
                        "book_cause_hi": RIN_CAUSE_HI[p],
                        "upay": D.RIN_UPAY[p][0], "upay_hi": D.RIN_UPAY[p][1],
                        "note": ("The book leaves the Moon's enemy column blank; Ketu (the Moon's enemy, p.31) is used here."
                                 if p == "Moon" else ""),
                        "note_hi": ("किताब में चंद्र के दुश्मन का खाना खाली है; यहाँ केतु (चंद्र का दुश्मन) लिया गया है।" if p == "Moon" else "")})
    return out


def cycle_planet(year_of_life):
    n = year_of_life
    if n <= 4:
        return "Rahu", "years 1-4 run on Rahu (tail of the previous cycle)"
    if n <= 7:
        return "Ketu", "years 5-7 run on Ketu"
    k = (n - 8) % 35
    cyc = (n - 8) // 35 + 1
    start = 8 + (cyc - 1) * 35
    for p, yrs in D.CYCLE:
        if k < yrs:
            return p, "cycle %d (from year %d): %s rules years %d-%d" % (cyc, start, p, n - k, n - k + yrs - 1)
        k -= yrs
    return None, ""


def varsh(pos, year_of_life):
    row = D.VARSHPHAL[((year_of_life - 1) % 120) + 1]
    vp = {p: row[pos[p] - 1] for p in D.PLANETS}
    vh = {h: [p for p in D.PLANETS if vp[p] == h] for h in range(1, 13)}
    return vp, vh


def drishti_pairs(houses):
    out = []
    for src, tgts in D.DRISHTI.items():
        for t, pc in tgts:
            if houses[src] and houses[t]:
                out.append({"from": src, "to": t, "strength": pc, "from_planets": houses[src], "to_planets": houses[t]})
    for src, tgts in D.ACHANAK_CHOT.items():
        for t in tgts:
            if houses[src] and houses[t]:
                out.append({"from": src, "to": t, "strength": "achanak chot (sudden strike)", "from_planets": houses[src],
                            "to_planets": houses[t]})
    return out


def build_lalkitab(v, birth_date, now, horizon_years=5, time_confidence="reliable"):
    birth = dt.date.fromisoformat(birth_date) if isinstance(birth_date, str) else birth_date
    today = now.date() if isinstance(now, dt.datetime) else now
    pos, houses = kundli(v)
    awake, sleeping_houses, asp = sleeping(pos, houses)
    age = _age(birth, today)
    yol = age + 1

    planets = {}
    for p in D.PLANETS:
        h = pos[p]
        st = status_of(p, h)
        mates = [q for q in houses[h] if q != p]
        enemies_with = [q for q in mates if q in D.ENEMIES[p]]
        friends_with = [q for q in mates if q in D.FRIENDS[p]]
        rd = D.R[(p, h)]
        aw, why, why_hi = awake[p]
        planets[p] = {"house": h, "status": st, "awake": aw, "sleep_reason": why, "sleep_reason_hi": why_hi, "with": mates,
                      "enemies_with": enemies_with, "friends_with": friends_with,
                      "title_hi": rd["t"], "title_en": rd["te"], "good": rd["g"], "good_hi": rd["gh"],
                      "bad": rd["b"], "bad_hi": rd["bh"], "upay": [u[0] for u in rd["u"]], "upay_hi": [u[1] for u in rd["u"]],
                      "wakes_at_age": D.AWAKE[p][1], "wake_trigger": D.AWAKE[p][0], "wake_trigger_hi": D.AWAKE_HI[p],
                      "bad_years": D.AWAKE[p][2]}

    rins = rin(pos, houses)
    mb = mangal_bad(pos, houses)
    rin_planets = {r["planet"] for r in rins}
    for p, d in planets.items():
        flags, fh = [], []
        if "neech" in d["status"]:
            flags.append("neech"); fh.append("नीच")
        if not d["awake"]:
            flags.append("sleeping"); fh.append("सोया")
        if d["enemies_with"]:
            flags.append("with enemy " + ", ".join(d["enemies_with"])); fh.append("दुश्मन साथ: " + ", ".join(H[q] for q in d["enemies_with"]))
        if p in rin_planets:
            flags.append("rin"); fh.append("ऋण")
        if p == "Mars" and mb:
            flags.append("mangal bad"); fh.append("मंगल बद")
        d["afflictions"] = flags
        d["afflictions_hi"] = fh
        d["needs_upay"] = bool(flags)

    years = []
    for i in range(0, max(0, horizon_years) + 1):
        n = yol + i
        start = _birthday(birth, birth.year + n - 1)
        vp, vh = varsh(pos, n)
        sun_h = vp["Sun"]
        peak = start.replace(day=1)
        m = peak.month - 1 + (sun_h - 1)
        peak = dt.date(peak.year + m // 12, m % 12 + 1, 1)
        cp, cnote = cycle_planet(n)
        years.append({"year_of_life": n, "age_completed": n - 1, "from": start.isoformat(),
                      "to": (_birthday(birth, birth.year + n) - dt.timedelta(days=1)).isoformat(),
                      "positions": vp, "houses": {str(h): vh[h] for h in range(1, 13)},
                      "sun_house": sun_h, "peak_month_index": sun_h, "peak_month": peak.strftime("%Y-%m"),
                      "cycle_planet": cp, "cycle_note": cnote,
                      "planets_in_1": vh[1], "planets_in_8": vh[8]})

    cp, cnote = cycle_planet(yol)
    order = []          # p.161 order of remedies
    empty_lords = []
    for h in sleeping_houses:
        for l in D.HOUSE_LORD[h]:
            if l not in empty_lords:
                empty_lords.append(l)
    out = {
        "conventions": {"house_basis": "Lal Kitab houses = whole-sign houses from the lagna; house 1 is always treated as Aries (sign 1).",
                        "source": "Lal Kitab, Pt. Roop Chand Joshi, 1952 edition (Farman 1-15)",
                        "varshphal_basis": "Year of life N = completed years + 1; row N of the 120-year table (pp.222-225A).",
                        "lagna_dependence": ("Every Lal Kitab position depends on the lagna; with an unknown birth time this section "
                                             "is not usable." if time_confidence == "unknown" else
                                             "Depends on the lagna; with an approximate time, a planet near a sign edge of the lagna can shift house."
                                             if time_confidence == "approximate" else "")},
        "kundli": {str(h): houses[h] for h in range(1, 13)},
        "planets": planets,
        "sleeping_houses": [{"house": h, "waker": D.KISMAT_JAGANE_WALA[h], "lords": D.HOUSE_LORD[h]} for h in sleeping_houses],
        "aspects": drishti_pairs(houses),
        "masnui": masnui(houses),
        "mangal_bad": [x[0] for x in mb],
        "mangal_bad_hi": [x[1] for x in mb],
        "teva": teva(pos, houses),
        "rin": rins,
        "age_completed": age,
        "year_of_life": yol,
        "cycle_now": {"planet": cp, "note": cnote},
        "varshphal": years,
        "remedy_order_hint": {"empty_house_lords": empty_lords,
                              "afflicted": [p for p in D.PLANETS if planets[p]["needs_upay"]]},
        "general_upay": {k: {"en": a, "hi": b} for k, (a, b) in D.GENERAL_UPAY.items()},
        "upay_rules": [{"en": a, "hi": b} for a, b in D.UPAY_RULES],
        "planet_info": {p: dict(D.PLANET_INFO[p], **{k + "_hi": v2 for k, v2 in D.PLANET_INFO_HI[p].items()}) for p in D.PLANETS},
        "disclaimer": ("Remedies (upay) are reproduced as Lal Kitab gives them, as traditional practice. They are not medical, "
                       "legal or financial advice and no outcome is promised. Skip anything unsafe, unlawful, cruel to animals "
                       "or against your own beliefs; never stop medical treatment for a remedy."),
        "disclaimer_hi": ("उपाय लाल किताब में जैसे लिखे हैं वैसे ही, पारंपरिक प्रथा के रूप में दिए गए हैं। ये चिकित्सा, कानूनी या "
                          "वित्तीय सलाह नहीं हैं और किसी नतीजे का वादा नहीं है। जो असुरक्षित, गैरकानूनी, जानवरों के लिए क्रूर या आपकी "
                          "आस्था के विरुद्ध हो उसे न करें; किसी उपाय के लिए इलाज कभी न छोड़ें।"),
    }
    return out
