"""horary.py - v30: a Western horary workspace (F061).

The chart of the moment a question is asked, with the considerations before judgement that the tradition asks a reader
to check first, the significators of the querent and of the thing asked about, and whether those two are applying to
each other. Nothing is judged for the user: the tradition's checks are listed and the answer is left to the reader.
"""
import datetime as dt
import json

import swisseph as swe

import hindi_shell as HS
from app_details import bi, items, para, table

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
RULER = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
BODY = {"Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS, "Mars": swe.MARS,
        "Jupiter": swe.JUPITER, "Saturn": swe.SATURN}
ASPECTS = [(0, "conjunction", "युति", 8.0), (60, "sextile", "षष्ठांश", 4.0), (90, "square", "केंद्र", 6.0),
           (120, "trine", "त्रिकोण", 6.0), (180, "opposition", "सम्मुख", 8.0)]
HOUSE_OF = [("the querent, the body, the self", "प्रश्नकर्ता, शरीर, स्वयं"), ("money and movable goods", "धन और चल संपत्ति"),
            ("brothers, sisters, short journeys, news", "भाई-बहन, छोटी यात्रा, समाचार"), ("father, land, the home, the end of the matter", "पिता, भूमि, घर, मामले का अंत"),
            ("children, pleasure, a wager", "संतान, आनंद, दाँव"), ("work, servants, small animals, the body's state", "काम, सेवक, छोटे पशु, शरीर की दशा"),
            ("the other person, the partner, an opponent", "दूसरा व्यक्ति, साथी, प्रतिपक्षी"), ("what is shared, debts, the other's money", "साझा वस्तु, ऋण, दूसरे का धन"),
            ("long journeys, learning, the law, strangers", "लंबी यात्रा, विद्या, विधि, अपरिचित"), ("the career, the mother, those in charge", "करियर, माता, अधिकारी"),
            ("friends, hopes, what is wished for", "मित्र, आशाएँ, जो चाहा गया"), ("what is hidden, loss, confinement", "जो छिपा है, हानि, बंधन")]
MONTH_HI = ["जन", "फ़र", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अग", "सित", "अक्टू", "नव", "दिस"]


def _s(lon):
    s = SIGNS[int(lon % 360 // 30)]
    return f"{s} {lon % 30:.1f}°", f"{HS.SIGN.get(s, s)} {lon % 30:.1f}°"


def _p(name):
    return bi(name, HS.PLANET.get(name, name))


def _house(lon, cusps):
    for h in range(12):
        a, b = cusps[h], cusps[(h + 1) % 12]
        if (lon - a) % 360 < (b - a) % 360:
            return h + 1
    return 12


def ask(request_json):
    """{"date","time","lat","lon","tz","house": 1-12, "question"?} -> {"sections": [...]}."""
    r = json.loads(request_json)
    import common
    t = common.resolve_time(r["date"], r["time"], float(r["lat"]), float(r["lon"]), r.get("tz"))
    jd = t["jd_ut"]
    lat, lon = float(r["lat"]), float(r["lon"])
    cusps, ascmc = swe.houses(jd, lat, lon, b"R")        # Regiomontanus, the usual houses for horary
    asc, mc = ascmc[0], ascmc[1]
    pos = {n: swe.calc_ut(jd, b, swe.FLG_SWIEPH | swe.FLG_SPEED)[0] for n, b in BODY.items()}
    qh = max(1, min(12, int(r.get("house", 7))))
    asc_sign = int(asc // 30)
    querent = RULER[asc_sign]
    quesited_sign = int(cusps[qh - 1] // 30)
    quesited = RULER[quesited_sign]

    rows = [[bi("Ascendant", "लग्न"), bi(*_s(asc)), bi(f"ruled by {RULER[asc_sign]}", f"स्वामी {HS.PLANET.get(RULER[asc_sign], '')}")],
            [bi(f"House {qh}", f"भाव {qh}"), bi(*_s(cusps[qh - 1])), bi(f"ruled by {quesited}", f"स्वामी {HS.PLANET.get(quesited, '')}")],
            [bi("Midheaven", "दशम"), bi(*_s(mc)), bi("")]]
    prows = []
    for n in BODY:
        l, sp = pos[n][0], pos[n][3]
        prows.append([_p(n), bi(*_s(l)), bi(str(_house(l, cusps))),
                      bi("retrograde", "वक्री") if sp < 0 else bi("direct", "मार्गी")])

    # considerations before judgement
    cons = []
    adeg = asc % 30
    if adeg < 3:
        cons.append(bi("The Ascendant is in the first three degrees: the matter may be too early to judge.",
                       "लग्न पहले तीन अंशों में है: मामला अभी निर्णय के लिए जल्दी हो सकता है।"))
    if adeg > 27:
        cons.append(bi("The Ascendant is in the last three degrees: the matter may already be settled or past helping.",
                       "लग्न अंतिम तीन अंशों में है: मामला शायद तय हो चुका है या अब सहायता से परे है।"))
    ml = pos["Moon"][0]
    if 195 <= ml < 225:
        cons.append(bi("The Moon is in the Via Combusta (15° Libra to 15° Scorpio): the tradition counts this an unsettled chart.",
                       "चंद्र 'वाया कोम्बुस्ता' (तुला 15° से वृश्चिक 15°) में है: परंपरा इसे अस्थिर कुंडली मानती है।"))
    sat_h = _house(pos["Saturn"][0], cusps)
    if sat_h in (1, 7):
        cons.append(bi(f"Saturn is in house {sat_h}: the tradition warns the reader (house 1) or doubts the reading (house 7).",
                       f"शनि भाव {sat_h} में है: परंपरा पाठक को सावधान करती है (भाव 1) या फल पर संदेह करती है (भाव 7)।"))
    # the Moon's next aspect, and whether she is void of course
    left = 30 - ml % 30
    nxt = None
    for n in BODY:
        if n == "Moon":
            continue
        for ang, en, hi, orb in ASPECTS:
            for target in ((pos[n][0] + ang) % 360, (pos[n][0] - ang) % 360):
                gap = (target - ml) % 360
                if gap < left and (nxt is None or gap < nxt[0]):
                    nxt = (gap, n, en, hi)
    if nxt is None:
        cons.append(bi("The Moon makes no more aspects before she leaves her sign (void of course): the tradition says nothing will come of the matter.",
                       "चंद्र अपनी राशि छोड़ने से पहले कोई दृष्टि नहीं बनाता (शून्य मार्ग): परंपरा कहती है कि मामले से कुछ नहीं निकलेगा।"))
        moon_line = bi("The Moon is void of course.", "चंद्र शून्य मार्ग में है।")
    else:
        hrs = nxt[0] / 13.2 * 24
        unit = "hour" if round(hrs) == 1 else "hours"
        moon_line = bi(f"The Moon applies next to {nxt[1]} by {nxt[2]}, about {hrs:.0f} {unit} away.",
                       f"चंद्र अगली दृष्टि {HS.PLANET.get(nxt[1], nxt[1])} से {nxt[3]} बनाता है, लगभग {hrs:.0f} घंटे बाद।")
    # do the two significators apply to each other?
    a, b = pos[querent], pos[quesited]
    link = bi("The two rulers are the same planet, so the matter turns on one significator.",
              "दोनों स्वामी एक ही ग्रह हैं, इसलिए मामला एक ही कारक पर टिकता है।")
    if querent != quesited:
        sep = (b[0] - a[0]) % 360
        best = None
        for ang, en, hi, orb in ASPECTS:
            for d in (sep, 360 - sep):
                o = abs(d - ang)
                if o <= orb and (best is None or o < best[0]):
                    applying = (a[3] - b[3]) * (1 if (b[0] - a[0]) % 360 < 180 else -1) > 0
                    best = (o, en, hi, applying)
        if best:
            link = bi(f"{querent} and {quesited} are in {best[1]} within {best[0]:.1f}°, and "
                      + ("applying, which the tradition reads as the matter coming together." if best[3] else "separating, which the tradition reads as the matter moving apart."),
                      f"{HS.PLANET.get(querent, querent)} और {HS.PLANET.get(quesited, quesited)} {best[2]} में {best[0]:.1f}° के भीतर हैं, और "
                      + ("निकट आ रहे हैं, जिसे परंपरा मामले के बनने के रूप में पढ़ती है।" if best[3] else "दूर हो रहे हैं, जिसे परंपरा मामले के बिखरने के रूप में पढ़ती है।"))
        else:
            link = bi(f"{querent} and {quesited} make no aspect to each other.",
                      f"{HS.PLANET.get(querent, querent)} और {HS.PLANET.get(quesited, quesited)} के बीच कोई दृष्टि नहीं।")
    d = dt.datetime.fromisoformat(t["local_civil"])
    asked = bi(d.strftime("%d %b %Y, %H:%M"), f"{d.day} {MONTH_HI[d.month - 1]} {d.year}, {d:%H:%M}")
    secs = [{"key": "horary_chart", "title": bi("Western horary: the moment of the question", "पाश्चात्य प्रश्न: प्रश्न का क्षण"),
             "intro": bi(f"Asked at {asked['en']}. The question was put to house {qh}: {HOUSE_OF[qh - 1][0]}.",
                         f"{asked['hi']} को पूछा गया। प्रश्न भाव {qh} को दिया गया: {HOUSE_OF[qh - 1][1]}।"),
             "blocks": [table([bi("Point", "बिंदु"), bi("At", "स्थान"), bi("", "")], rows),
                        table([bi("Planet", "ग्रह"), bi("At", "स्थान"), bi("House", "भाव"), bi("Motion", "गति")], prows)],
             "note": bi("Regiomontanus houses and the seven traditional planets, as horary is usually cast.",
                        "रेजियोमोंटेनस भाव और सात पारंपरिक ग्रह, जैसे प्रश्न कुंडली सामान्यतः बनाई जाती है।")},
            {"key": "horary_judgement", "title": bi("Before judging", "निर्णय से पहले"),
             "blocks": [items(cons) if cons else para(bi("None of the traditional cautions apply to this chart.",
                                                         "इस कुंडली पर परंपरा की कोई चेतावनी लागू नहीं होती।")),
                        para(moon_line), para(link)],
             "note": bi("The tradition asks a reader to check these before reading anything else, and to set the chart aside when they weigh against it. "
                        "The app does not answer the question; it lays out what the chart shows.",
                        "परंपरा कहती है कि कुछ भी पढ़ने से पहले ये जाँच लें, और प्रतिकूल होने पर कुंडली छोड़ दें। "
                        "ऐप प्रश्न का उत्तर नहीं देता; वह केवल दिखाता है कि कुंडली में क्या है।")}]
    return json.dumps({"sections": secs, "houses": [bi(*HOUSE_OF[i]) for i in range(12)]}, ensure_ascii=False)
