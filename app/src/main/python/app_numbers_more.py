"""app_numbers_more.py - numerology tools (v16): couple compatibility, business names, phone, vehicle and house
numbers, and the personal day. Arithmetic from numerology.py and the number-planet friendships of name_correction.py
(Rahu read as Saturn, Ketu as Mars, as many Indian numerologists do). Output is bilingual sections in app_details.py's
format, so the app shows them with the same cards as the Kundali details. No promise is attached to any number.
"""
import datetime as dt
import json
import re

import hindi_shell as HS
import name_correction as NC
from numerology import CHALDEAN, clean_name, digit_sum, reduce
from app_details import bi, table, para, items, MON_HI
import app_today as AT

with open(__file__.replace("app_numbers_more.py", "app_meanings.json"), encoding="utf-8") as f:
    MEAN = json.load(f)

PLANET = NC.ROOT_PLANET
REL = {"same": ("same number", "एक ही अंक"), "friend": ("friendly", "मित्र"), "neutral": ("neutral", "सम"), "enemy": ("needs understanding", "समझ माँगता है")}
REL_SCORE = {"same": 2, "friend": 2, "neutral": 1, "enemy": 0}
CLASS = {"favourable": ("favourable", "अनुकूल"), "neutral": ("neutral", "सम"), "mixed": ("mixed", "मिश्रित"), "difficult": ("asks for care", "सावधानी माँगता है"),
         "root only": ("read by its root", "मूल अंक से पढ़ा जाता है")}


def _births(dob):
    y, m, d = int(dob[:4]), int(dob[5:7]), int(dob[8:10])
    return reduce(d, False)[0], reduce(digit_sum(y) + digit_sum(m) + digit_sum(d), False)[0]


def _num(n):
    return bi(f"{n} ({PLANET[n]})", f"{n} ({HS.PLANET.get(PLANET[n], PLANET[n])})")


def _rel(a, b):
    """Both directions: a from b's side and b from a's side; the softer of the two is used."""
    r1, r2 = NC.relation(a, b), NC.relation(b, a)
    worst = min((r1, r2), key=lambda r: REL_SCORE[r])
    return worst, (REL_SCORE[r1] + REL_SCORE[r2]) / 2


def _meaning(n):
    o = MEAN["number"].get(str(n))
    return bi(o["en"], o["hi"]) if o else bi("")


# ------------------------------------------------------------------ couple
def pair(a_name, a_dob, b_name, b_dob):
    am, ab = _births(a_dob)
    bm, bb = _births(b_dob)
    an, bn = a_name.split()[0], b_name.split()[0]
    rows, total = [], 0.0
    for label_en, label_hi, x, y in (("Mulank with Mulank", "मूलांक और मूलांक", am, bm), ("Bhagyank with Bhagyank", "भाग्यांक और भाग्यांक", ab, bb),
                                     (f"{an}'s Mulank with {bn}'s Bhagyank", f"{an} का मूलांक और {bn} का भाग्यांक", am, bb),
                                     (f"{bn}'s Mulank with {an}'s Bhagyank", f"{bn} का मूलांक और {an} का भाग्यांक", bm, ab)):
        r, sc = _rel(x, y)
        total += sc
        rows.append([bi(label_en, label_hi), bi(f"{x} and {y}", f"{x} और {y}"), bi(*REL[r])])
    score = round(total / 8 * 100)
    band = ("easy" if score >= 70 else "workable" if score >= 45 else "needs understanding")
    band_hi = {"easy": "सहज", "workable": "निभने योग्य", "needs understanding": "समझ और धैर्य माँगता है"}[band]
    sec1 = {"key": "num_pair", "title": bi(f"{an} and {bn}: number compatibility", f"{an} और {bn}: अंक अनुकूलता"),
            "intro": bi(f"Number harmony {score} out of 100: {band}.", f"अंक सामंजस्य 100 में से {score}: {band_hi}।"),
            "blocks": [table([bi("Pair", "जोड़ी"), bi("Numbers", "अंक"), bi("Relation", "संबंध")], rows),
                       table([bi("Person", "व्यक्ति"), bi("Mulank", "मूलांक"), bi("Bhagyank", "भाग्यांक")],
                             [[bi(a_name), _num(am), _num(ab)], [bi(b_name), _num(bm), _num(bb)]]),
                       para(bi("Friendly numbers share an easy rhythm; a pair that 'needs understanding' simply works best with patience and clear talk.",
                               "मित्र अंकों में सहज तालमेल होता है; 'समझ माँगने वाली' जोड़ी धैर्य और खुली बातचीत से सबसे अच्छा चलती है।"))],
            "note": bi("Numerology compatibility is a light check beside Kundli Milan, not a replacement for it.",
                       "अंक अनुकूलता कुंडली मिलान के साथ एक हल्की जाँच है, उसका विकल्प नहीं।")}
    return [sec1]


# ------------------------------------------------------------------ business name
def business(name, owner_dob):
    letters = clean_name(name)
    total = sum(CHALDEAN.get(c, 0) for c in letters)
    if not total:
        return []
    root = reduce(total, False)[0]
    cls, _desc = NC.compound_class(total)
    om, ob = _births(owner_dob)
    rm, _ = _rel(root, om)
    rb, _ = _rel(root, ob)
    rows = [[bi("Chaldean total", "कैल्डियन योग"), bi(str(total))], [bi("Compound reading", "संयुक्त अंक"), bi(*CLASS.get(cls, (cls, cls)))],
            [bi("Root number", "मूल अंक"), _num(root)], [bi("With the owner's Mulank", "स्वामी के मूलांक से"), bi(f"{om}: {REL[rm][0]}", f"{om}: {REL[rm][1]}")],
            [bi("With the owner's Bhagyank", "स्वामी के भाग्यांक से"), bi(f"{ob}: {REL[rb][0]}", f"{ob}: {REL[rb][1]}")]]
    return [{"key": "num_business", "title": bi(f"Business name: {name}", f"व्यवसाय का नाम: {name}"),
             "intro": _meaning(root),
             "blocks": [table([bi("Check", "जाँच"), bi("Result", "परिणाम")], rows)],
             "note": bi("Compound readings follow Cheiro's Book of Numbers. A name supports a business; the work and the service build it.",
                        "संयुक्त अंक कीरो की 'बुक ऑफ़ नंबर्स' के अनुसार। नाम व्यवसाय का सहारा है; उसे काम और सेवा बनाते हैं।")}]


# ------------------------------------------------------------------ phone, vehicle and house numbers
KIND = {"phone": ("Mobile number", "मोबाइल नंबर"), "vehicle": ("Vehicle number", "वाहन नंबर"), "house": ("House number", "मकान नंबर")}


def number(text, kind, owner_dob):
    digits = re.sub(r"\D", "", text or "")
    letters = re.sub(r"[^A-Za-z]", "", text or "").upper()
    if not digits and not letters:
        return []
    total = sum(int(c) for c in digits) + sum(CHALDEAN.get(c, 0) for c in letters)
    root = reduce(total, False)[0]
    om, ob = _births(owner_dob)
    rm, _ = _rel(root, om)
    rb, _ = _rel(root, ob)
    last = int(digits[-4:]) if kind == "phone" and len(digits) >= 4 else None
    rows = [[bi("Total", "योग"), bi(str(total))], [bi("Root number", "मूल अंक"), _num(root)],
            [bi("With your Mulank", "आपके मूलांक से"), bi(f"{om}: {REL[rm][0]}", f"{om}: {REL[rm][1]}")],
            [bi("With your Bhagyank", "आपके भाग्यांक से"), bi(f"{ob}: {REL[rb][0]}", f"{ob}: {REL[rb][1]}")]]
    if last is not None:
        rows.append([bi("Last four digits", "अंतिम चार अंक"), _num(reduce(sum(int(c) for c in digits[-4:]), False)[0])])
    if letters:
        rows.insert(0, [bi("Letters counted", "गिने गए अक्षर"), bi(f"{letters} (Chaldean values)", f"{letters} (कैल्डियन मान)")])
    return [{"key": f"num_{kind}", "title": bi(f"{KIND[kind][0]}: {text.strip()}", f"{KIND[kind][1]}: {text.strip()}"),
             "intro": _meaning(root),
             "blocks": [table([bi("Check", "जाँच"), bi("Result", "परिणाम")], rows)],
             "note": bi("A friendly or same root is the traditional choice when you have one; no number is bad to keep.",
                        "जब चुनने का अवसर हो तो मित्र या एक-सा मूल अंक परंपरागत पसंद है; कोई भी अंक रखना बुरा नहीं।")}]


# ------------------------------------------------------------------ personal year, month and day
def personal(dob, on_iso):
    d0 = dt.date.fromisoformat(on_iso)
    m, d = int(dob[5:7]), int(dob[8:10])
    py = reduce(digit_sum(m) + digit_sum(d) + digit_sum(d0.year), False)[0]
    pm = reduce(py + d0.month, False)[0]
    days = []
    for i in range(7):
        x = d0 + dt.timedelta(days=i)
        px = reduce(digit_sum(m) + digit_sum(d) + digit_sum(x.year), False)[0]
        pd = reduce(reduce(px + x.month, False)[0] + x.day, False)[0]
        days.append([bi(x.strftime("%a %d %b"), f"{AT.WD_HI[x.weekday()]} {x.day} {MON_HI[x.month - 1]}"), _num(pd), _meaning(pd)])
    return [{"key": "num_personal", "title": bi("Personal year, month and day", "व्यक्तिगत वर्ष, माह और दिन"),
             "intro": bi(f"Personal year {py}, personal month {pm}.", f"व्यक्तिगत वर्ष {py}, व्यक्तिगत माह {pm}।"),
             "blocks": [table([bi("Day", "दिन"), bi("Personal day", "व्यक्तिगत दिन"), bi("Theme", "विषय")], days)],
             "note": bi("Personal year = birth month + birth day + the calendar year, reduced; month adds the month; day adds the day (Pythagorean practice).",
                        "व्यक्तिगत वर्ष = जन्म माह + जन्म दिन + कैलेंडर वर्ष, घटाकर; माह में माह जुड़ता है; दिन में दिन (पाइथागोरियन पद्धति)।")}]


def tools(request_json):
    r = json.loads(request_json)
    k = r.get("kind")
    if k == "pair":
        secs = pair(r["a_name"], r["a_dob"], r["b_name"], r["b_dob"])
    elif k == "business":
        secs = business(r["text"], r["dob"])
    elif k in KIND:
        secs = number(r["text"], k, r["dob"])
    else:
        secs = personal(r["dob"], r.get("on") or dt.date.today().isoformat())
    return json.dumps({"sections": secs}, ensure_ascii=False)
