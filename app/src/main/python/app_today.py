"""app_today.py - the daily dashboard ("Today"): the day's panchang for a place, its good and avoided periods,
and, for a chosen person, how the day relates to their chart. App-owned (not synced from the skill).

Conventions, stated so a reader can compare with their own almanac:
* Sunrise and sunset: the Sun's upper edge with standard refraction, as almanacs such as Drik Panchang print them
  (the birth panchang uses the centre of the disc, a minute or two later at sunrise).
* Panchang elements are those prevailing at sunrise (udaya), each with the local time it ends.
* Sidereal positions use the user's ayanamsa (Lahiri by default); tithi, karana and yoga do not depend on it.
* Rahu Kalam, Yamaganda and Gulika Kalam are the customary eighth-parts of daylight by weekday.
* Choghadiya: day and night each cut into eight parts; day parts follow the hora order from the weekday lord,
  night parts start from the lord of the fifth weekday and step by five.
* Hora: twelve day and twelve night horas in the order Sun, Venus, Mercury, Moon, Saturn, Jupiter, Mars.
* Brahma muhurta: 96 to 48 minutes before sunrise (two muhurtas of 48 minutes), as almanacs print it.
* Lunar months are amanta (new moon to new moon), named by the Sun's sidereal sign at the new moon that starts
  them; a month with no Sun sign change is adhika. Purnimanta names are given too.
* Festival and vrat dates follow the usual rule for each (the tithi prevailing at sunrise, sunset, midnight
  or moonrise). Temple and regional calendars can differ by a day; that is said with the list.
* Tarabala and Chandrabala follow the muhurta module (Vipat, Pratyari, Vadha fail; Chandrabala 1,3,6,7,10,11,
  plus 2,5,9 in Shukla paksha).
"""
import datetime as dt
import json
from zoneinfo import ZoneInfo

import swisseph as swe
import hindi_shell as HS
import vedic
from common import SIGNS, NAKSHATRAS, NAK_SPAN, n360

MIN = 1.0 / 1440.0
_RISE = swe.CALC_RISE
_SET = swe.CALC_SET

TITHI_EN = ["Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami", "Ashtami", "Navami",
            "Dashami", "Ekadashi", "Dvadashi", "Trayodashi", "Chaturdashi"]
TITHI_HI = ["प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पंचमी", "षष्ठी", "सप्तमी", "अष्टमी", "नवमी", "दशमी", "एकादशी",
            "द्वादशी", "त्रयोदशी", "चतुर्दशी"]
YOGA_HI = {"Vishkambha": "विष्कुंभ", "Priti": "प्रीति", "Ayushman": "आयुष्मान", "Saubhagya": "सौभाग्य", "Shobhana": "शोभन",
           "Atiganda": "अतिगंड", "Sukarma": "सुकर्मा", "Dhriti": "धृति", "Shula": "शूल", "Ganda": "गंड", "Vriddhi": "वृद्धि",
           "Dhruva": "ध्रुव", "Vyaghata": "व्याघात", "Harshana": "हर्षण", "Vajra": "वज्र", "Siddhi": "सिद्धि",
           "Vyatipata": "व्यतीपात", "Variyana": "वरीयान", "Parigha": "परिघ", "Shiva": "शिव", "Siddha": "सिद्ध",
           "Sadhya": "साध्य", "Shubha": "शुभ", "Shukla": "शुक्ल", "Brahma": "ब्रह्म", "Indra": "इंद्र", "Vaidhriti": "वैधृति"}
KARANA_HI = {"Bava": "बव", "Balava": "बालव", "Kaulava": "कौलव", "Taitila": "तैतिल", "Gara": "गर", "Vanija": "वणिज",
             "Vishti (Bhadra)": "विष्टि (भद्रा)", "Kimstughna": "किंस्तुघ्न", "Shakuni": "शकुनि", "Chatushpada": "चतुष्पद",
             "Naga": "नाग"}
WD_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WD_HI = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]
WD_LORD = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
MONTH_EN = ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada", "Ashvin", "Kartika",
            "Margashirsha", "Pausha", "Magha", "Phalguna"]
MONTH_HI = ["चैत्र", "वैशाख", "ज्येष्ठ", "आषाढ़", "श्रावण", "भाद्रपद", "आश्विन", "कार्तिक", "मार्गशीर्ष", "पौष", "माघ",
            "फाल्गुन"]
PAKSHA = {"Shukla": "शुक्ल", "Krishna": "कृष्ण"}
HORA_ORDER = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
CHOG = {"Sun": "Udveg", "Venus": "Chal", "Mercury": "Labh", "Moon": "Amrit", "Saturn": "Kaal", "Jupiter": "Shubh",
        "Mars": "Rog"}
CHOG_HI = {"Udveg": "उद्वेग", "Chal": "चल", "Labh": "लाभ", "Amrit": "अमृत", "Kaal": "काल", "Shubh": "शुभ", "Rog": "रोग"}
CHOG_KIND = {"Amrit": "good", "Shubh": "good", "Labh": "good", "Chal": "neutral", "Udveg": "avoid", "Rog": "avoid",
             "Kaal": "avoid"}
RAHU_KALAM = [2, 7, 5, 6, 4, 3, 8]      # eighth-part of daylight by python weekday (Mon=0)
YAMAGANDA = [4, 3, 2, 1, 7, 6, 5]
GULIKA_KALAM = [6, 5, 4, 3, 2, 1, 7]
TARA = [("Janma", "जन्म"), ("Sampat", "संपत"), ("Vipat", "विपत"), ("Kshema", "क्षेम"), ("Pratyari", "प्रत्यरि"),
        ("Sadhana", "साधना"), ("Vadha", "वध"), ("Mitra", "मित्र"), ("Parama Mitra", "परम मित्र")]
PLANETS = [("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS), ("Mercury", swe.MERCURY),
           ("Jupiter", swe.JUPITER), ("Venus", swe.VENUS), ("Saturn", swe.SATURN)]


def bi(en, hi=None):
    return {"en": str(en), "hi": str(en if hi is None else hi)}


# ------------------------------------------------------------------ positions

def _tropical(jd, body):
    return swe.calc_ut(jd, body, swe.FLG_SWIEPH | swe.FLG_SPEED)[0]


def _sid(jd, body):
    r = swe.calc_ut(jd, body, swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED)[0]
    return r[0], r[3]


def _elong(jd):
    return n360(_tropical(jd, swe.MOON)[0] - _tropical(jd, swe.SUN)[0])


def _tithi(jd):          # 1..30
    return int(_elong(jd) // 12) + 1


def _nak(jd):            # 0..26
    return int(_sid(jd, swe.MOON)[0] // NAK_SPAN)


def _yoga(jd):           # 0..26
    return int(n360(_sid(jd, swe.SUN)[0] + _sid(jd, swe.MOON)[0]) // NAK_SPAN)


def _karana(jd):         # 1..60
    return int(_elong(jd) // 6) + 1


def _next_change(jd, fn, limit_days=2.0):
    """Julian day when fn(jd) next changes value (to the minute), or None within the limit."""
    v0 = fn(jd)
    step = 1.0 / 24
    a, t = jd, jd + step
    while t - jd <= limit_days:
        if fn(t) != v0:
            b = t
            while b - a > MIN / 2:
                m = (a + b) / 2
                if fn(m) == v0:
                    a = m
                else:
                    b = m
            return b
        a, t = t, t + step
    return None


def _new_moon_before(jd):
    """The new moon (elongation 0) at or before jd."""
    t = jd - _elong(jd) / 12.19
    for _ in range(3):           # Newton-like refinement on elongation
        e = _elong(t)
        if e > 180:
            e -= 360
        t -= e / 12.19
    return t


# ------------------------------------------------------------------ time helpers

class Day:
    def __init__(self, date, lat, lon, tz):
        self.date, self.lat, self.lon, self.tz = date, lat, lon, tz
        local_mid = dt.datetime(date.year, date.month, date.day, tzinfo=tz)
        self.jd_mid = self._jd(local_mid)
        self.sunrise = self._event(self.jd_mid - 0.02, swe.SUN, _RISE)
        self.sunset = self._event(self.sunrise or self.jd_mid, swe.SUN, _SET)
        self.next_sunrise = self._event((self.sunset or self.jd_mid + 0.5) + 0.01, swe.SUN, _RISE)
        self.prev_sunset = self._event(self.jd_mid - 1.0, swe.SUN, _SET)
        self.moonrise = self._event(self.jd_mid, swe.MOON, swe.CALC_RISE)
        self.moonset = self._event(self.jd_mid, swe.MOON, swe.CALC_SET)

    @staticmethod
    def _jd(d):
        u = d.astimezone(dt.timezone.utc)
        return swe.julday(u.year, u.month, u.day, u.hour + u.minute / 60 + u.second / 3600)

    def _event(self, start, body, flag):
        try:
            res = swe.rise_trans(start, body, flag, (self.lon, self.lat, 0.0), 1013.25, 15.0)
        except Exception:
            return None
        if res[0] < 0 or res[1][0] <= 1:
            return None
        return res[1][0]

    def local(self, jd):
        if jd is None:
            return None
        y, m, d, h = swe.revjul(jd)
        u = dt.datetime(y, m, d, tzinfo=dt.timezone.utc) + dt.timedelta(hours=h)
        return u.astimezone(self.tz)

    def hm(self, jd):
        t = self.local(jd)
        if t is None:
            return None
        s = t.strftime("%H:%M")
        if t.date() != self.date:
            s += " (" + t.strftime("%d %b") + ")"
        return s

    def iso(self, jd):
        t = self.local(jd)
        return t.strftime("%Y-%m-%dT%H:%M") if t else None


def _span(day, a, b, **extra):
    d = {"from": day.hm(a), "to": day.hm(b), "from_iso": day.iso(a), "to_iso": day.iso(b)}
    d.update(extra)
    return d


# ------------------------------------------------------------------ the day itself

def lunar_month(jd):
    """Amanta month index (0 = Chaitra), whether it is adhika, and the jd of the new moon that starts it."""
    nm = _new_moon_before(jd)
    nxt = _new_moon_before(nm + 31)
    s1 = int(_sid(nm, swe.SUN)[0] // 30)
    s2 = int(_sid(nxt, swe.SUN)[0] // 30)
    return (s1 + 1) % 12, s1 == s2, nm


def _samvat(nm_jd, month):
    y, m, d, _ = swe.revjul(nm_jd - month * 29.53)    # approximate start of this Chaitra
    vikram = y + 57
    return vikram, vikram - 135


def panchang(day):
    jd = day.sunrise or day.jd_mid + 0.25
    t = _tithi(jd)
    paksha = "Shukla" if t <= 15 else "Krishna"
    tp = t if t <= 15 else t - 15
    tname = ("Purnima" if t == 15 else "Amavasya") if tp == 15 else TITHI_EN[tp - 1]
    thi = ("पूर्णिमा" if t == 15 else "अमावस्या") if tp == 15 else TITHI_HI[tp - 1]
    nk = _nak(jd)
    yg = _yoga(jd)
    kr = _karana(jd)
    kname = vedic.karana_name(kr)
    wd = day.date.weekday()
    month, adhika, nm = lunar_month(jd)
    pmonth = month if paksha == "Shukla" else (month + 1) % 12
    vik, shaka = _samvat(nm, month)
    moon_sign = int(_sid(jd, swe.MOON)[0] // 30)
    sun_sign = int(_sid(jd, swe.SUN)[0] // 30)
    adh_en, adh_hi = ("Adhika ", "अधिक ") if adhika else ("", "")
    out = {
        "weekday": bi(WD_EN[wd], WD_HI[wd]), "weekday_lord": bi(WD_LORD[wd], HS.PLANET.get(WD_LORD[wd])),
        "tithi": {"name": bi(tname, thi), "paksha": bi(paksha, PAKSHA[paksha]), "number": t,
                  "ends": day.hm(_next_change(jd, _tithi))},
        "nakshatra": {"name": bi(NAKSHATRAS[nk], HS.NAK.get(NAKSHATRAS[nk])), "index": nk,
                      "ends": day.hm(_next_change(jd, _nak))},
        "yoga": {"name": bi(vedic.YOGA_NAMES[yg], YOGA_HI.get(vedic.YOGA_NAMES[yg])),
                 "ends": day.hm(_next_change(jd, _yoga))},
        "karana": {"name": bi(kname, KARANA_HI.get(kname)), "ends": day.hm(_next_change(jd, _karana))},
        "moon_sign": bi(SIGNS[moon_sign], HS.SIGN.get(SIGNS[moon_sign])),
        "sun_sign": bi(SIGNS[sun_sign], HS.SIGN.get(SIGNS[sun_sign])),
        "month_amanta": bi(adh_en + MONTH_EN[month], adh_hi + MONTH_HI[month]),
        "month_purnimanta": bi(adh_en + MONTH_EN[pmonth], adh_hi + MONTH_HI[pmonth]),
        "vikram_samvat": vik, "shaka_samvat": shaka,
    }
    return out


def periods(day):
    sr, ss, nsr = day.sunrise, day.sunset, day.next_sunrise
    if not (sr and ss and nsr):
        return {"status": "No sunrise or sunset at this latitude today; day periods are not computed."}
    wd = day.date.weekday()
    part = (ss - sr) / 8
    npart = (nsr - ss) / 8

    def eighth(n):
        return _span(day, sr + (n - 1) * part, sr + n * part)

    out = {
        "rahu_kalam": eighth(RAHU_KALAM[wd]), "yamaganda": eighth(YAMAGANDA[wd]), "gulika_kalam": eighth(GULIKA_KALAM[wd]),
        "abhijit": _span(day, sr + 7 * (ss - sr) / 15, sr + 8 * (ss - sr) / 15, wednesday=(wd == 2)),
    }
    out["brahma_muhurta"] = _span(day, sr - 96 * MIN, sr - 48 * MIN)
    lord = WD_LORD[wd]
    i0 = HORA_ORDER.index(lord)
    n0 = HORA_ORDER.index(WD_LORD[(wd + 4) % 7])
    day_ch, night_ch = [], []
    for k in range(8):
        name = CHOG[HORA_ORDER[(i0 + k) % 7]]
        day_ch.append(_span(day, sr + k * part, sr + (k + 1) * part, name=bi(name, CHOG_HI[name]), kind=CHOG_KIND[name]))
        name = CHOG[HORA_ORDER[(n0 + 5 * k) % 7]]
        night_ch.append(_span(day, ss + k * npart, ss + (k + 1) * npart, name=bi(name, CHOG_HI[name]), kind=CHOG_KIND[name]))
    out["choghadiya_day"], out["choghadiya_night"] = day_ch, night_ch
    hd, hn = (ss - sr) / 12, (nsr - ss) / 12
    horas = []
    for k in range(24):
        p = HORA_ORDER[(i0 + k) % 7]
        a = sr + k * hd if k < 12 else ss + (k - 12) * hn
        b = a + (hd if k < 12 else hn)
        horas.append(_span(day, a, b, lord=bi(p, HS.PLANET.get(p)), night=k >= 12))
    out["hora"] = horas
    return out


# ------------------------------------------------------------------ festivals and vrats

# (key, English, Hindi, amanta month or None, paksha "S"/"K", tithi in paksha, moment)
RULES = [
    ("ekadashi_s", "Ekadashi (Shukla)", "एकादशी (शुक्ल)", None, "S", 11, "sunrise"),
    ("ekadashi_k", "Ekadashi (Krishna)", "एकादशी (कृष्ण)", None, "K", 11, "sunrise"),
    ("pradosh_s", "Pradosh vrat", "प्रदोष व्रत", None, "S", 13, "sunset"),
    ("pradosh_k", "Pradosh vrat", "प्रदोष व्रत", None, "K", 13, "sunset"),
    ("purnima", "Purnima", "पूर्णिमा", None, "S", 15, "sunrise"),
    ("amavasya", "Amavasya", "अमावस्या", None, "K", 15, "sunrise"),
    ("sankashti", "Sankashti Chaturthi", "संकष्टी चतुर्थी", None, "K", 4, "moonrise"),
    ("vinayaka", "Vinayaka Chaturthi", "विनायक चतुर्थी", None, "S", 4, "sunrise"),
    ("shivaratri", "Masik Shivaratri", "मासिक शिवरात्रि", None, "K", 14, "midnight"),
    ("ram_navami", "Ram Navami", "राम नवमी", 0, "S", 9, "midday"),
    ("chaitra_navratri", "Chaitra Navratri begins", "चैत्र नवरात्रि आरंभ", 0, "S", 1, "sunrise"),
    ("hanuman_jayanti", "Hanuman Jayanti", "हनुमान जयंती", 0, "S", 15, "sunrise"),
    ("akshaya_tritiya", "Akshaya Tritiya", "अक्षय तृतीया", 1, "S", 3, "sunrise"),
    ("guru_purnima", "Guru Purnima", "गुरु पूर्णिमा", 3, "S", 15, "sunrise"),
    ("raksha_bandhan", "Raksha Bandhan", "रक्षा बंधन", 4, "S", 15, "sunrise"),
    ("janmashtami", "Krishna Janmashtami", "कृष्ण जन्माष्टमी", 4, "K", 8, "midnight"),
    ("ganesh_chaturthi", "Ganesh Chaturthi", "गणेश चतुर्थी", 5, "S", 4, "midday"),
    ("navratri", "Sharad Navratri begins", "शारदीय नवरात्रि आरंभ", 6, "S", 1, "sunrise"),
    ("dussehra", "Dussehra (Vijayadashami)", "दशहरा (विजयादशमी)", 6, "S", 10, "aparahna"),
    ("karva_chauth", "Karva Chauth", "करवा चौथ", 6, "K", 4, "moonrise"),
    ("dhanteras", "Dhanteras", "धनतेरस", 6, "K", 13, "sunset"),
    ("narak_chaturdashi", "Narak Chaturdashi", "नरक चतुर्दशी", 6, "K", 14, "sunrise"),
    ("diwali", "Diwali (Lakshmi Puja)", "दीपावली (लक्ष्मी पूजा)", 6, "K", 15, "sunset"),
    ("govardhan", "Govardhan Puja", "गोवर्धन पूजा", 7, "S", 1, "sunrise"),
    ("bhai_dooj", "Bhai Dooj", "भाई दूज", 7, "S", 2, "sunrise"),
    ("chhath", "Chhath Puja", "छठ पूजा", 7, "S", 6, "sunrise"),
    ("dev_uthani", "Dev Uthani Ekadashi", "देवउठनी एकादशी", 7, "S", 11, "sunrise"),
    ("vasant_panchami", "Vasant Panchami", "वसंत पंचमी", 10, "S", 5, "sunrise"),
    ("maha_shivaratri", "Maha Shivaratri", "महाशिवरात्रि", 10, "K", 14, "midnight"),
    ("holika_dahan", "Holika Dahan", "होलिका दहन", 11, "S", 15, "sunset"),
]
SANKRANTI_SPECIAL = {9: ("Makar Sankranti", "मकर संक्रांति"), 0: ("Mesha Sankranti (Baisakhi)", "मेष संक्रांति (बैसाखी)")}
MONTHLY_KEYS = {"ekadashi_s", "ekadashi_k", "pradosh_s", "pradosh_k", "purnima", "amavasya", "sankashti", "vinayaka",
                "shivaratri"}


def _moments(day):
    m = {"sunrise": day.sunrise, "sunset": day.sunset}
    if day.sunrise and day.sunset:
        m["midday"] = (day.sunrise + day.sunset) / 2                       # madhyahna
        m["aparahna"] = day.sunrise + 0.7 * (day.sunset - day.sunrise)      # middle of the afternoon fifth
    if day.sunset and day.next_sunrise:
        m["midnight"] = (day.sunset + day.next_sunrise) / 2
    m["moonrise"] = day.moonrise if day.moonrise and day.next_sunrise and day.moonrise < day.next_sunrise else None
    return m


def festivals(start, days, lat, lon, tz):
    """Vrat and festival days from start for the given number of days, oldest first."""
    cache = []
    for i in range(days + 2):
        d = Day(start + dt.timedelta(days=i), lat, lon, tz)
        mo = _moments(d)
        tith = {k: (_tithi(v) if v else None) for k, v in mo.items()}
        jd = d.sunrise or d.jd_mid + 0.25
        month, adhika, _ = lunar_month(jd)
        sun_sign = int(_sid(jd, swe.SUN)[0] // 30)
        cache.append((d, tith, month, adhika, sun_sign))
    found = []
    for i in range(days + 1):
        d, tith, month, adhika, sun_sign = cache[i]
        nd, ntith, _, _, nsun = cache[i + 1]
        for key, en, hi, mon, pk, tp, moment in RULES:
            target = tp if pk == "S" else tp + 15
            cur, nxt = tith.get(moment) or tith.get("sunrise"), ntith.get(moment) or ntith.get("sunrise")
            if cur is None:
                continue
            j, mi = None, None
            if cur == target:
                j = mi = i
            elif nxt is not None and cur % 30 + 1 == target and nxt == target % 30 + 1:
                # the tithi covers no such moment: keep the day it holds at sunrise, else the day it begins;
                # its lunar month is the one in force after it begins
                j = i + 1 if ntith.get("sunrise") == target else i
                mi = i + 1
            if j is None:
                continue
            jd_ = cache[j][0]
            jmonth, jadhika = cache[mi][2], cache[mi][3]
            if mon is not None and (jmonth != mon or jadhika):   # annual days: amanta month must match; none in adhika months
                continue
            if any(f["key"] == key and abs((jd_.date - dt.date.fromisoformat(f["date"])).days) < 3 for f in found):
                continue
            found.append({"key": key, "date": jd_.date.isoformat(), "name": bi(en, hi), "monthly": key in MONTHLY_KEYS})
        if nsun != sun_sign:
            # the civil date on which the Sun enters the new sign
            ingress = _next_change(d.sunrise or d.jd_mid, lambda j: int(_sid(j, swe.SUN)[0] // 30), limit_days=1.5)
            on = d.local(ingress).date() if ingress else d.date
            en, hi = SANKRANTI_SPECIAL.get(nsun, (SIGNS[nsun] + " Sankranti", HS.SIGN.get(SIGNS[nsun]) + " संक्रांति"))
            found.append({"key": "sankranti", "date": on.isoformat(), "name": bi(en, hi), "monthly": nsun not in SANKRANTI_SPECIAL,
                          "time": d.hm(ingress) if ingress else None})
    # Holi (colours) follows Holika Dahan
    for f in list(found):
        if f["key"] == "holika_dahan":
            found.append({"key": "holi", "date": (dt.date.fromisoformat(f["date"]) + dt.timedelta(days=1)).isoformat(),
                          "name": bi("Holi", "होली"), "monthly": False})
    # a festival that falls on a monthly vrat replaces it (Dev Uthani is that month's Ekadashi, and so on)
    same = {"dev_uthani": ("ekadashi_s",), "maha_shivaratri": ("shivaratri",), "diwali": ("amavasya",),
            "ganesh_chaturthi": ("vinayaka",), "guru_purnima": ("purnima",), "raksha_bandhan": ("purnima",),
            "hanuman_jayanti": ("purnima",), "holika_dahan": ("purnima",)}
    drop = {(m, f["date"]) for f in found for m in same.get(f["key"], ())}
    found = [f for f in found if (f["key"], f["date"]) not in drop]
    found = [f for f in found if start <= dt.date.fromisoformat(f["date"]) <= start + dt.timedelta(days=days)]
    found.sort(key=lambda f: (f["date"], f["monthly"]))
    return found


# ------------------------------------------------------------------ the person

def _house(from_sign, sign):
    return (sign - from_sign) % 12 + 1


def person_view(day, person, now_jd):
    moon_lon = float(person["moon_lon"])
    lag_sign = int(float(person["lagna_lon"]) // 30)
    msign = int(moon_lon // 30)
    bnak = int(moon_lon // NAK_SPAN)
    out = {"name": person.get("name", "")}
    # tara and chandra bala at the time asked, and when the Moon's nakshatra next changes
    nk = _nak(now_jd)
    count = (nk - bnak) % 27 + 1
    r = count % 9 or 9
    tara_ok = r not in (3, 5, 7)
    tmoon = int(_sid(now_jd, swe.MOON)[0] // 30)
    ch_house = _house(msign, tmoon)
    shukla = _tithi(now_jd) <= 15
    chandra_ok = ch_house in (1, 3, 6, 7, 10, 11) or (shukla and ch_house in (2, 5, 9))
    nxt = _next_change(now_jd, _nak)
    out["tarabala"] = {"tara": bi(*TARA[r - 1]), "number": r, "ok": tara_ok, "changes": day.hm(nxt) if nxt else None}
    out["chandrabala"] = {"house": ch_house, "ok": chandra_ok}
    out["moon_transit"] = {"sign": bi(SIGNS[tmoon], HS.SIGN.get(SIGNS[tmoon])), "house_from_moon": ch_house,
                           "house_from_lagna": _house(lag_sign, tmoon)}
    # all transits
    tr = []
    rahu_lon = n360(swe.calc_ut(now_jd, swe.MEAN_NODE, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0])
    pos = [(p, *_sid(now_jd, b)) for p, b in PLANETS] + [("Rahu", rahu_lon, -0.05), ("Ketu", n360(rahu_lon + 180), -0.05)]
    for p, lon, speed in pos:
        s = int(lon // 30)
        tr.append({"planet": bi(p, HS.PLANET.get(p)), "key": p, "sign": bi(SIGNS[s], HS.SIGN.get(SIGNS[s])),
                   "deg": round(lon % 30, 2), "retrograde": speed < 0 and p not in ("Rahu", "Ketu"),
                   "house_from_lagna": _house(lag_sign, s), "house_from_moon": _house(msign, s)})
    out["transits"] = tr
    # Saturn from the Moon
    sat = int(_sid(now_jd, swe.SATURN)[0] // 30)
    h = _house(msign, sat)
    phase = {12: ("Sade Sati, first phase", "साढ़े साती, पहला चरण"), 1: ("Sade Sati, middle phase", "साढ़े साती, मध्य चरण"),
             2: ("Sade Sati, last phase", "साढ़े साती, अंतिम चरण"), 8: ("Ashtama Shani (Saturn 8th from the Moon)", "अष्टम शनि (चंद्र से आठवाँ शनि)"),
             4: ("Kantaka Shani (Saturn 4th from the Moon)", "कंटक शनि (चंद्र से चौथा शनि)")}.get(h)
    out["saturn"] = {"house_from_moon": h, "phase": bi(*phase) if phase else None}
    if person.get("dasha"):
        out["dasha"] = person["dasha"]
    # a short, calm line about the day: never fear, never a guarantee
    if tara_ok and chandra_ok:
        g = bi("A supportive day by Tarabala and Chandrabala for beginnings that matter to you.",
               "तारा बल और चंद्र बल के अनुसार आज का दिन आपके लिए महत्वपूर्ण शुरुआत के अनुकूल है।")
    elif tara_ok or chandra_ok:
        g = bi("A mixed day: fine for ongoing work. For an important beginning, use a good Choghadiya or Abhijit muhurta.",
               "मिला-जुला दिन: चल रहे काम के लिए ठीक। किसी महत्वपूर्ण शुरुआत के लिए शुभ चौघड़िया या अभिजित मुहूर्त चुनें।")
    else:
        when = out["tarabala"]["changes"]
        g = bi("A day for routine work and preparation. If you can choose, begin important things on a day with better Tarabala"
               + (f" (the Moon's nakshatra changes at {when})." if when else "."),
               "आज नियमित काम और तैयारी का दिन है। संभव हो तो महत्वपूर्ण शुरुआत बेहतर तारा बल वाले दिन करें"
               + (f" (चंद्र का नक्षत्र {when} पर बदलता है)।" if when else "।"))
    out["guidance"] = g
    return out


# ------------------------------------------------------------------ entry point

def today(request_json):
    """{"date": "YYYY-MM-DD", "now": "YYYY-MM-DDTHH:MM" (local, optional), "lat", "lon", "tz", "place"?,
        "ayanamsa"?, "festival_days"? (default 45),
        "person"?: {"name", "moon_lon", "lagna_lon" (sidereal, same ayanamsa), "dasha"?}}"""
    r = json.loads(request_json)
    tz = ZoneInfo(r["tz"])
    date = dt.date.fromisoformat(r["date"])
    swe.set_sid_mode(vedic.AYAN.get(r.get("ayanamsa") or "lahiri", swe.SIDM_LAHIRI))
    day = Day(date, float(r["lat"]), float(r["lon"]), tz)
    if r.get("now"):
        now_jd = Day._jd(dt.datetime.fromisoformat(r["now"]).replace(tzinfo=tz))
    else:
        now_jd = day.sunrise or day.jd_mid + 0.25
    out = {
        "date": date.isoformat(), "place": r.get("place", ""), "tz": r["tz"],
        "utc_offset": dt.datetime(date.year, date.month, date.day, 12, tzinfo=tz).strftime("%z"),
        "sun": {"rise": day.hm(day.sunrise), "set": day.hm(day.sunset)},
        "moon": {"rise": day.hm(day.moonrise), "set": day.hm(day.moonset)},
        "panchang": panchang(day),
        "periods": periods(day),
        "festivals": festivals(date, int(r.get("festival_days", 45)), day.lat, day.lon, tz),
        "conventions": bi("Sunrise: centre of the Sun's disc with refraction. Panchang at sunrise, with end times. "
                          "Festival dates follow the usual rule for each; your temple's calendar may differ by a day.",
                          "सूर्योदय: सूर्य बिंब का केंद्र, अपवर्तन सहित। पंचांग सूर्योदय के समय का, समाप्ति समय के साथ। "
                          "त्योहारों की तिथियाँ सामान्य नियम से हैं; आपके मंदिर के पंचांग में एक दिन का अंतर हो सकता है।"),
    }
    if r.get("person"):
        out["person"] = person_view(day, r["person"], now_jd)
    return json.dumps(out, ensure_ascii=False)
