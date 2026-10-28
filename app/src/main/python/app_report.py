"""app_report.py - the full multi-system reading as one self-contained HTML page, in English or Hindi.

The layout follows Gaurav Mishra's consultation report: a cover, then 1 birth details, 2 Vedic, 3 Western, 4 BaZi,
5 numerology, 6 comparison across systems, 7 doshas and remedies, 8 summary. Every number comes from the engine
(the chart, its forecast and life-event layers, and app_forecast); the prose is assembled from fixed templates, so
the same chart always gives the same report and nothing is invented.

House rules, as everywhere in the app: tendencies, not certainties; no illness, death or divorce is ever named;
remedies are optional practices with no promised outcome; gemstones only with a pointer to an expert.
"""
import datetime as dt
import html
import json
import os

import app_details as AD
import app_forecast as AF
import hindi_shell as HS
from app_report_style import CSS, JS

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "app_meanings.json"), encoding="utf-8") as _f:
    MEAN = json.load(_f)

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGN_LORD = {"Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
             "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"}
EXALT = {"Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn", "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra"}
DEBIL = {"Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer", "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo", "Saturn": "Aries"}
OWN = {p: [s for s, l in SIGN_LORD.items() if l == p] for p in EXALT}
SEVEN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
NINE = SEVEN + ["Rahu", "Ketu"]
KENDRA = {1, 4, 7, 10}
TRIKONA = {1, 5, 9}
DUSTHANA = {6, 8, 12}

# Short themes for tables (the long ones are in app_meanings.json).
THEME = {"Sun": ("authority, father, vitality", "अधिकार, पिता, ऊर्जा"), "Moon": ("mind, mother, feelings", "मन, माता, भावनाएँ"),
         "Mars": ("courage, energy, property", "साहस, ऊर्जा, भूमि"), "Mercury": ("intellect, speech, trade", "बुद्धि, वाणी, व्यापार"),
         "Jupiter": ("wisdom, teachers, children, growth", "ज्ञान, गुरु, संतान, विकास"),
         "Venus": ("love, comfort, the arts, partnership", "प्रेम, सुख, कला, साझेदारी"),
         "Saturn": ("duty, patience, long effort", "कर्तव्य, धैर्य, दीर्घ परिश्रम"),
         "Rahu": ("ambition, the unusual, the foreign", "महत्वाकांक्षा, असामान्य, विदेश"),
         "Ketu": ("detachment, insight, the spiritual", "वैराग्य, अंतर्दृष्टि, आध्यात्म")}
HOUSE_THEME = {1: ("self, body, temperament", "व्यक्तित्व, शरीर, स्वभाव"), 2: ("money, speech, family", "धन, वाणी, परिवार"),
               3: ("courage, siblings, effort, skills", "साहस, भाई-बहन, प्रयास, कौशल"),
               4: ("home, mother, education, peace of mind", "घर, माता, शिक्षा, मानसिक शांति"),
               5: ("children, intellect, creativity, romance", "संतान, बुद्धि, रचनात्मकता, प्रेम"),
               6: ("competition, service, daily work, debts", "प्रतिस्पर्धा, सेवा, दैनिक कार्य, ऋण"),
               7: ("marriage, partnership", "विवाह, साझेदारी"), 8: ("hidden matters, change, shared resources", "गुह्य विषय, परिवर्तन, साझा संसाधन"),
               9: ("fortune, dharma, teachers, long journeys", "भाग्य, धर्म, गुरु, लंबी यात्राएँ"),
               10: ("career, reputation, status", "करियर, कीर्ति, पद"), 11: ("income, gains, networks, hopes", "आय, लाभ, संपर्क, इच्छाएँ"),
               12: ("expenses, foreign lands, rest, release", "व्यय, विदेश, विश्राम, मोक्ष")}
SIGN_TRAIT = {
    "Aries": ("direct, energetic, quick to start", "सीधा, ऊर्जावान, जल्दी शुरुआत करने वाला"),
    "Taurus": ("steady, practical, loyal, fond of comfort", "स्थिर, व्यावहारिक, निष्ठावान, सुख-प्रिय"),
    "Gemini": ("curious, talkative, quick-minded", "जिज्ञासु, बातूनी, तेज़ दिमाग़"),
    "Cancer": ("caring, protective, emotionally deep", "देखभाल करने वाला, रक्षक, भावनात्मक रूप से गहरा"),
    "Leo": ("warm, proud, generous, likes to lead", "उदार, स्वाभिमानी, नेतृत्व-प्रिय"),
    "Virgo": ("precise, helpful, analytical", "सटीक, सहायक, विश्लेषणात्मक"),
    "Libra": ("fair, sociable, seeks balance", "न्यायप्रिय, मिलनसार, संतुलन चाहने वाला"),
    "Scorpio": ("intense, private, determined", "तीव्र, निजी, दृढ़"),
    "Sagittarius": ("optimistic, frank, philosophical", "आशावादी, स्पष्टवादी, दार्शनिक"),
    "Capricorn": ("disciplined, ambitious, responsible", "अनुशासित, महत्वाकांक्षी, ज़िम्मेदार"),
    "Aquarius": ("independent, inventive, humane", "स्वतंत्र, आविष्कारशील, मानवतावादी"),
    "Pisces": ("imaginative, compassionate, intuitive", "कल्पनाशील, करुणामय, अंतर्ज्ञानी"),
}
ASPECT_SENSE = {
    "conjunction": ("merge: the two work as one", "मिलकर एक साथ काम करते हैं"),
    "trine": ("work together easily", "सहजता से साथ देते हैं"),
    "sextile": ("support each other when used", "प्रयास करने पर एक-दूसरे को सहारा देते हैं"),
    "square": ("pull against each other, which pushes growth", "एक-दूसरे को खींचते हैं, जिससे विकास का दबाव बनता है"),
    "opposition": ("ask for balance between them", "आपस में संतुलन माँगते हैं"),
}
W_THEME = {"Uranus": ("change, freedom", "परिवर्तन, स्वतंत्रता"), "Neptune": ("ideals, imagination", "आदर्श, कल्पना"),
           "Pluto": ("deep transformation", "गहरा रूपांतरण"), "North Node": ("life direction", "जीवन-दिशा"),
           "Ascendant": ("how you meet the world", "दुनिया से मिलने का ढंग"), "Midheaven": ("career and public life", "करियर और सार्वजनिक जीवन")}
ELEMENT_HI = {"Fire": "अग्नि", "Earth": "पृथ्वी", "Air": "वायु", "Water": "जल", "Wood": "काष्ठ", "Metal": "धातु"}
ELEMENT_COLOUR = {"Wood": ("green, east", "हरा, पूर्व दिशा"), "Fire": ("red, south", "लाल, दक्षिण दिशा"),
                  "Earth": ("yellow and brown, the centre", "पीला और भूरा, मध्य"), "Metal": ("white and silver, west", "सफ़ेद और चाँदी, पश्चिम दिशा"),
                  "Water": ("black and blue, north", "काला और नीला, उत्तर दिशा")}
PRODUCES = {"Wood": "Fire", "Fire": "Earth", "Earth": "Metal", "Metal": "Water", "Water": "Wood"}
CONTROLS = {"Wood": "Earth", "Earth": "Water", "Water": "Fire", "Fire": "Metal", "Metal": "Wood"}
TEN_GOD = {"Friend": ("peers, independence", "साथी, स्वतंत्रता"), "Rob Wealth": ("competition, bold moves", "प्रतिस्पर्धा, साहसी क़दम"),
           "Eating God": ("creativity, enjoyment, expression", "सृजन, आनंद, अभिव्यक्ति"),
           "Hurting Officer": ("talent, outspokenness", "प्रतिभा, खरी अभिव्यक्ति"), "Indirect Wealth": ("opportunity, business", "अवसर, व्यवसाय"),
           "Direct Wealth": ("steady earnings, responsibility", "नियमित आय, ज़िम्मेदारी"),
           "Seven Killings": ("pressure, ambition, authority", "दबाव, महत्वाकांक्षा, अधिकार"),
           "Direct Officer": ("career, discipline, institutions", "करियर, अनुशासन, संस्थाएँ"),
           "Indirect Resource": ("unusual learning, intuition", "असामान्य विद्या, अंतर्ज्ञान"),
           "Direct Resource": ("learning, support, protection", "विद्या, सहारा, संरक्षण")}
REMEDY = {  # mantra, day, charity (en, hi), gemstone (en, hi), finger (en, hi)
    "Sun": ("ॐ सूर्याय नमः", ("Sunday", "रविवार"), ("wheat, jaggery or copper; respect for father and elders", "गेहूँ, गुड़ या ताँबा; पिता और बड़ों का सम्मान"),
            ("ruby", "माणिक्य"), ("ring finger", "अनामिका")),
    "Moon": ("ॐ सों सोमाय नमः", ("Monday", "सोमवार"), ("rice, milk or white cloth; time with mother", "चावल, दूध या सफ़ेद वस्त्र; माता के साथ समय"),
             ("pearl", "मोती"), ("little finger", "कनिष्ठा")),
    "Mars": ("ॐ अं अंगारकाय नमः", ("Tuesday", "मंगलवार"), ("red lentils (masoor) or red cloth; Hanuman Chalisa", "मसूर दाल या लाल वस्त्र; हनुमान चालीसा"),
             ("red coral", "मूँगा"), ("ring finger", "अनामिका")),
    "Mercury": ("ॐ बुं बुधाय नमः", ("Wednesday", "बुधवार"), ("green moong or green cloth; help a student", "हरी मूँग या हरा वस्त्र; किसी विद्यार्थी की सहायता"),
                ("emerald", "पन्ना"), ("little finger", "कनिष्ठा")),
    "Jupiter": ("ॐ बृं बृहस्पतये नमः", ("Thursday", "गुरुवार"),
                ("turmeric, chana dal, yellow cloth or books; Vishnu Sahasranama", "हल्दी, चने की दाल, पीला वस्त्र या पुस्तकें; विष्णु सहस्रनाम"),
                ("yellow sapphire", "पुखराज"), ("index finger", "तर्जनी")),
    "Venus": ("ॐ शुं शुक्राय नमः", ("Friday", "शुक्रवार"), ("white sweets, curd or white cloth", "सफ़ेद मिठाई, दही या सफ़ेद वस्त्र"),
              ("diamond or white sapphire", "हीरा या सफ़ेद पुखराज"), ("middle finger", "मध्यमा")),
    "Saturn": ("ॐ शं शनैश्चराय नमः", ("Saturday", "शनिवार"), ("black sesame, mustard oil or iron; help workers and the elderly", "काला तिल, सरसों का तेल या लोहा; श्रमिकों और बुज़ुर्गों की सहायता"),
               ("blue sapphire", "नीलम"), ("middle finger", "मध्यमा")),
    "Rahu": ("ॐ रां राहवे नमः", ("Saturday", "शनिवार"), ("a blanket or black urad", "कंबल या काली उड़द"), ("hessonite", "गोमेद"), ("middle finger", "मध्यमा")),
    "Ketu": ("ॐ कें केतवे नमः", ("Tuesday", "मंगलवार"), ("a multi-coloured blanket or sesame", "रंग-बिरंगा कंबल या तिल"), ("cat's eye", "लहसुनिया"), ("ring finger", "अनामिका")),
}
MON_EN = AF.MON_EN
MON_HI = AF.MON_HI
ORD_EN = {1: "1st", 2: "2nd", 3: "3rd"}


def add_years_iso(iso, k):
    y = int(iso[:4]) + k
    return f"{y}{iso[4:]}" if iso[5:] != "02-29" else f"{y}-02-28"


SEASON = {"旺": ("at its peak (旺)", "अपने चरम पर (旺)"), "相": ("supported (相)", "सहायक (相)"), "休": ("resting (休)", "विश्राम में (休)"),
          "囚": ("restrained (囚)", "बँधा हुआ (囚)"), "死": ("at its weakest (死)", "सबसे क्षीण (死)")}
WBODY_HI = {"Uranus": "यूरेनस", "Neptune": "नेप्च्यून", "Pluto": "प्लूटो", "North Node": "उत्तर नोड", "Ascendant": "लग्न",
            "Midheaven": "दशम-बिंदु", "Chiron": "काइरन"}
PALACE_EN = {"Year": "year", "Month": "month", "Day": "day", "Hour": "hour", "Annual": "this year", "LuckPillar": "luck pillar"}
PALACE_HI2 = {"Year": "वर्ष", "Month": "माह", "Day": "दिन", "Hour": "समय", "Annual": "वार्षिक", "LuckPillar": "लक पिलर"}
WHY_HI = {"debilitated": "नीच", "combust": "अस्त", "enemy's sign": "शत्रु राशि में", "weak shadbala": "षड्बल में दुर्बल"}


def dm(dms):
    """6°33'09" -> 6°33′"""
    d, _, rest = dms.partition("°")
    return f"{d}°{rest.split(chr(39))[0]}′" if rest else dms


DIG_EN = {"exalted": "exalted", "debilitated": "debilitated", "own sign": "in its own sign", "moolatrikona": "in its moolatrikona sign",
          "friend's sign": "in a friend's sign", "enemy's sign": "in an enemy's sign"}


def lc(s):
    return s[:1].lower() + s[1:] if s else s


def E(s):
    return html.escape(str(s), quote=False)


class R:
    """One report in one language."""

    def __init__(self, hi):
        self.hi = hi

    def t(self, en, hi_):
        return hi_ if self.hi else en

    def P(self, p):
        return HS.PLANET.get(p, p) if self.hi else p

    def S(self, s):
        return HS.SIGN.get(s, s) if self.hi else s

    def N(self, n):
        return HS.NAK.get(n, n) if self.hi else n

    def tag(self, d):
        return HS.TAGS.get(d, d) if self.hi else d

    def el(self, e):
        return ELEMENT_HI.get(e, e) if self.hi else e

    def house(self, h):
        return f"{AF.ORD_HI[h]} भाव" if self.hi else f"{ORD_EN.get(h, f'{h}th')} house"

    def houses(self, hs):
        hs = list(hs)
        if self.hi:
            return " और ".join(f"{AF.ORD_HI[h]}" for h in hs) + " भाव"
        words = [ORD_EN.get(h, f"{h}th") for h in hs]
        return (" and ".join(words) if len(words) < 3 else ", ".join(words[:-1]) + " and " + words[-1]) + (" houses" if len(words) > 1 else " house")

    def length(self, a, b):
        """Length of a period from its dates: "19 years", "3 years 1 month" (the first dasha is only the balance left at birth)."""
        da, db = dt.date.fromisoformat(a[:10]), dt.date.fromisoformat(b[:10])
        months = round((db - da).days / 30.4375)
        y, m = divmod(months, 12)
        if self.hi:
            return " ".join(x for x in (f"{y} वर्ष" if y else "", f"{m} माह" if m else "") if x)
        return " ".join(x for x in (f"{y} year{'s' if y != 1 else ''}" if y else "", f"{m} month{'s' if m != 1 else ''}" if m else "") if x)

    def count(self, n, en_one, en_many, hi_word):
        return f"{n} {hi_word}" if self.hi else f"{n} {en_one if n == 1 else en_many}"

    def hth(self, h):  # house with its themes
        return f"{self.house(h)} ({HOUSE_THEME[h][1 if self.hi else 0]})"

    def body(self, p):
        """Any chart body: Vedic planets via the Hindi table, outer planets, nodes and angles via WBODY_HI."""
        if not self.hi:
            return p
        return HS.PLANET.get(p) or WBODY_HI.get(p, p)

    def rel(self, x):
        """A BaZi relation {"type", "between"} in words."""
        typ = x["type"]
        if self.hi:
            for en, hi_ in HS.REL_HI:
                typ = typ.replace(en, hi_)
            for en, hi_ in ELEMENT_HI.items():
                typ = typ.replace(en, hi_)
        who = []
        for b in x["between"]:
            k, _, ch = b.partition(" ")
            who.append(f"{(PALACE_HI2 if self.hi else PALACE_EN).get(k, k)} {ch}".strip())
        return f"{typ} ({', '.join(who)})"

    def theme(self, p):
        return THEME.get(p, W_THEME.get(p, (p, p)))[1 if self.hi else 0]

    def date(self, iso):
        y, m, d = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
        return f"{d} {(MON_HI if self.hi else MON_EN)[m - 1]} {y}"

    def month(self, iso):
        return AF.month(iso, self.hi)

    def yoga_name(self, n):
        return MEAN["yoga_name_hi"].get(n, n) if self.hi else n

    def ten_god(self, g):
        if self.hi:
            return HS.TEN_GOD_HI.get(g, g)
        return g

    def tg_theme(self, g):
        k = next((k for k in TEN_GOD if g.startswith(k)), None)
        return TEN_GOD[k][1 if self.hi else 0] if k else ""

    def lang_key(self):
        return "hi" if self.hi else "en"

    def mean(self, table, key):
        o = MEAN.get(table, {}).get(str(key))
        return o[self.lang_key()] if o else ""


# ------------------------------------------------------------------ small HTML helpers
def table(head, rows, cls=None):
    th = "".join(f"<th>{h}</th>" for h in head)
    body = []
    for r in rows:
        if isinstance(r, tuple) and len(r) == 2 and isinstance(r[1], dict):
            cells, attrs = r
            body.append(f'<tr class="{attrs.get("cls", "")}">' + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
        else:
            body.append("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
    return f'<div class="table-scroll"><table class="data"><thead><tr>{th}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def para(*texts):
    return "".join(f"<p>{t}</p>" for t in texts if t)


def callout(title, body, orange=False):
    return (f'<div class="callout{" orange" if orange else ""}"><p class="callout-title">{title}</p>'
            f'<p class="callout-body">{body}</p></div>')


def bullets(items):
    return '<ul class="bullets">' + "".join(f"<li>{i}</li>" for i in items if i) + "</ul>"


def section(n, title, inner, tinted=False):
    if tinted:
        return f'<section class="page tinted" id="sec{n}"><div class="inner"><h1 class="section"><span class="num">{n}</span>{title}</h1>{inner}</div></section>'
    return f'<section class="page" id="sec{n}"><h1 class="section"><span class="num">{n}</span>{title}</h1>{inner}</section>'


def sub(num, title):
    return f'<h2 class="sub">{num}&nbsp; {title}</h2>'


def pill(sev, label):
    return f'<span class="pill {sev}">{label}</span>'


# ------------------------------------------------------------------ chart facts
def sign_dignity(p, s):
    if p not in EXALT:
        return None
    if EXALT[p] == s:
        return "exalted"
    if DEBIL[p] == s:
        return "debilitated"
    if s in OWN[p]:
        return "own sign"
    return None


def first_name(name):
    return (name or "").strip().split()[0] if name and name.strip() else ""


def age_on(birth, now):
    b, n = dt.date.fromisoformat(birth), dt.date.fromisoformat(now)
    return n.year - b.year - ((n.month, n.day) < (b.month, b.day))


# ------------------------------------------------------------------ sections
def cover(r, ctx):
    t = r.t
    lines = [(t("PREPARED FOR", "हेतु तैयार"), E(ctx["name"])), (t("PREPARED BY", "द्वारा तैयार"), E(ctx["by"])),
             (t("CONSULTATION DATE", "परामर्श तिथि"), r.date(ctx["now"])), (t("REPORT REFERENCE", "रिपोर्ट संदर्भ"), ctx["ref"])]
    return f"""
<section class="cover-page">
  <div class="cover-title-1">{t("Astrological and Numerological", "ज्योतिषीय एवं अंकशास्त्रीय")}</div>
  <div class="cover-title-2">{t("Life Analysis", "जीवन विश्लेषण")}</div>
  <p class="cover-sub">{t("A multi-system consultation report", "एक बहु-प्रणाली परामर्श रिपोर्ट")}</p>
  <p class="cover-systems">{t("Vedic astrology &nbsp;&middot;&nbsp; Western astrology &nbsp;&middot;&nbsp; Chinese BaZi &nbsp;&middot;&nbsp; Numerology",
                               "वैदिक ज्योतिष &nbsp;&middot;&nbsp; पाश्चात्य ज्योतिष &nbsp;&middot;&nbsp; चीनी बाज़ी &nbsp;&middot;&nbsp; अंकशास्त्र")}</p>
  <div class="divider">&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&nbsp; &#10022; &nbsp;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;</div>
  <div class="cover-lines">{"".join(f'<div class="cover-line"><span class="label">{a}</span><span class="value">{b}</span></div>' for a, b in lines)}</div>
  <div class="cover-site">{E(ctx["site"])}</div>
  <p class="cover-foot-note">{t("This analysis is prepared for personal guidance and reflection.", "यह विश्लेषण व्यक्तिगत मार्गदर्शन एवं चिंतन हेतु तैयार किया गया है।")}</p>
  <p class="scroll-hint">&darr; {t("Scroll down to begin", "विश्लेषण आरंभ करने हेतु नीचे स्क्रॉल करें")} &darr;</p>
</section>"""


def sec1(r, c, ctx):
    t = r.t
    conf = c["meta"].get("birth_time_confidence", "reliable")
    conf_txt = {"certificate": t("confirmed by the birth certificate", "जन्म प्रमाण-पत्र से पुष्ट"),
                "reliable": t("reliable", "विश्वसनीय"), "approximate": t("approximate", "अनुमानित"),
                "unknown": t("not known (noon used)", "अज्ञात (दोपहर 12 बजे माना गया)")}.get(conf, conf)
    lat, lon = ctx["lat"], ctx["lon"]
    coord = f"{abs(lat):.2f}&deg; {t('N' if lat >= 0 else 'S', 'उ.' if lat >= 0 else 'द.')}, {abs(lon):.2f}&deg; {t('E' if lon >= 0 else 'W', 'पू.' if lon >= 0 else 'प.')}"
    hh, mm = ctx["time"].split(":")
    rows = [(t("Full name", "पूरा नाम"), E(ctx["name"])), (t("Date of birth", "जन्म तिथि"), r.date(ctx["date"])),
            (t("Time of birth", "जन्म समय"), f"{hh}:{mm} ({E(ctx['tz'])}) &mdash; {conf_txt}"),
            (t("Place of birth", "जन्म स्थान"), (E(ctx["place"]) + " " if ctx["place"] else "") + f"({coord})"),
            *([(t("Current residence", "वर्तमान निवास"), E(ctx["residence"]))] if ctx.get("residence") else []),
            (t("Gender", "लिंग"), t("Male", "पुरुष") if ctx["gender"] == "M" else t("Female", "स्त्री")),
            (t(f"Age (on {r.date(ctx['now'])})", f"वर्तमान आयु ({r.date(ctx['now'])} तक)"), t(f"{ctx['age']} years", f"{ctx['age']} वर्ष"))]
    fn = first_name(ctx["name"])
    intro = t(f"Dear {E(fn)}, this report reads your birth chart and date of birth through four separate traditions: Vedic astrology, "
              "Western astrology, Chinese BaZi and numerology. The aim is not four reports in one file, but to see where four independent "
              "calculations of the same life speak with one voice and where they differ.",
              f"{E(fn)} जी, यह रिपोर्ट आपकी जन्म-कुंडली और जन्म-तिथि के आधार पर चार अलग-अलग परंपराओं — वैदिक ज्योतिष, पाश्चात्य ज्योतिष, चीनी बाज़ी "
              "और अंकशास्त्र — को एक साथ रखकर तैयार की गई है। लक्ष्य चार अलग रिपोर्टों को एक फ़ाइल में जोड़ना नहीं, बल्कि यह देखना है कि जब चार स्वतंत्र "
              "गणनाएँ एक ही जीवन को अलग-अलग कोण से देखती हैं तो वे कहाँ एक स्वर में बोलती हैं और कहाँ अलग राय रखती हैं।")
    if conf in ("certificate", "reliable"):
        g = t("With a reliable birth time, the rising sign, the house boundaries and the BaZi hour pillar, the three things a 15 to 20 minute "
              "error spoils first, can be used with confidence.",
              "जन्म समय विश्वसनीय होने का सीधा फ़ायदा यह है कि लग्न, भाव-सीमाएँ और बाज़ी का घंटा-स्तंभ — ये तीनों जो सबसे पहले 15-20 मिनट के फ़र्क़ से "
              "बिगड़ते हैं — यहाँ भरोसे के साथ इस्तेमाल किए जा सकते हैं।")
    else:
        g = t("Because the birth time is not exact, the rising sign, the houses and the BaZi hour pillar may be different; read those parts "
              "as provisional. Planet signs, the Moon's star (if not near a boundary), the BaZi year, month and day, and numerology still hold.",
              "जन्म समय सटीक न होने से लग्न, भाव और बाज़ी का घंटा-स्तंभ बदल सकते हैं; उन हिस्सों को अस्थायी मानें। ग्रहों की राशियाँ, चंद्र नक्षत्र "
              "(यदि सीमा के पास नहीं), बाज़ी के वर्ष, माह व दिन स्तंभ और अंकशास्त्र फिर भी लागू हैं।")
    ayan = c["vedic"]["conventions"]["ayanamsa"]
    note = t(f"Calculated with the Swiss Ephemeris: a sidereal Vedic chart ({E(ayan)} ayanamsa, whole-sign houses), a tropical Western chart, "
             "a BaZi chart on the solar calendar, and standard numerology. This is guidance-level analysis; before a major decision "
             "(marriage, property, health) consult a qualified astrologer, and for any health matter a doctor.",
             f"गणनाएँ स्विस एफ़ेमेरिस से की गई हैं: {E(HS.AYAN_HI.get(ayan.lower(), ayan))} अयनांश पर आधारित सिडेरियल वैदिक कुंडली (संपूर्ण-राशि भाव), ट्रॉपिकल पाश्चात्य कुंडली, "
             "सौर पंचांग पर बाज़ी और मानक अंकशास्त्र पद्धति। यह एक मार्गदर्शन-स्तर का विश्लेषण है — किसी बड़े निर्णय (विवाह, संपत्ति, स्वास्थ्य) से पहले किसी योग्य "
             "ज्योतिषी से परामर्श लें, और स्वास्थ्य के किसी भी विषय में डॉक्टर से।")
    inner = (para(intro) + table([t("Detail", "विवरण"), t("Information", "जानकारी")], rows) + f'<p class="guidance">{g}</p>'
             + callout(t("Note on data reliability", "डेटा विश्वसनीयता संबंधी टिप्पणी"), note))
    return section(1, t("Client and Birth Details", "क्लाइंट एवं जन्म विवरण"), inner)


def dignity_word(r, p):
    d = p.get("dignity", "")
    if d in ("exalted", "debilitated", "own sign", "moolatrikona"):
        return r.tag(d)
    return ""


def sec2(r, c, ctx):
    t = r.t
    v = c["vedic"]
    L = v["lagna"]
    pl = v["planets"]
    lag = L["sign"]
    ll = SIGN_LORD[lag]
    llp = pl[ll]
    deg = int(L["dms"].split("°")[0])
    intro = t(f"Your rising sign (lagna) is {lag}: at {ctx['time']} on {r.date(ctx['date'])}"
              + (f" in {E(ctx['place'])}" if ctx["place"] else "") + f", about {deg}° of {lag} was rising in the east. "
              f"{ll} is your lagna lord; it sits in your {r.hth(llp['house'])} in {llp['sign']}"
              + (f", {DIG_EN[llp['dignity']]}" if llp.get("dignity") in DIG_EN else "") + ".",
              f"आपकी लग्न {r.S(lag)} है — {r.date(ctx['date'])} को {ctx['time']} बजे"
              + (f" {E(ctx['place'])} में" if ctx["place"] else "") + f" जन्म के समय पूर्व दिशा में {r.S(lag)} राशि का लगभग {deg}° भाग उदय हो रहा था। "
              f"{r.P(ll)} आपका लग्नेश है; वह {r.S(llp['sign'])} राशि में, आपके {r.hth(llp['house'])} में बैठा है"
              + (f" ({r.tag(llp['dignity'])})" if llp.get("dignity") not in (None, "n/a", "neutral sign") else "") + "।")
    # 2.1 key points
    def comment(pn):
        p = pl[pn]
        bits = [t(f"in {p['sign_lord']}'s sign", f"{r.P(p['sign_lord'])} की राशि में")]
        dw = dignity_word(r, p)
        if dw:
            bits.append(dw)
        bits.append(t(f"in the {r.house(p['house'])}", f"{r.house(p['house'])} में"))
        tr = SIGN_TRAIT[p["sign"]][1 if r.hi else 0]
        return ", ".join(bits) + f" &mdash; {tr}"
    keyrows = [(t("Lagna", "लग्न"), f"{r.S(lag)} {dm(L['dms'])}", t(f"lagna lord {ll} &mdash; ", f"लग्नेश {r.P(ll)} &mdash; ") + SIGN_TRAIT[lag][1 if r.hi else 0]),
               (t("Moon sign", "चंद्र राशि"), f"{r.S(pl['Moon']['sign'])} {dm(pl['Moon']['dms'])}", comment("Moon")),
               (t("Sun sign", "सूर्य राशि"), f"{r.S(pl['Sun']['sign'])} {dm(pl['Sun']['dms'])}", comment("Sun"))]
    s21 = sub("2.1", t("Key positions", "मूल ग्रह स्थितियाँ")) + table([t("Point", "बिंदु"), t("Sign", "राशि"), t("Note", "टिप्पणी")], keyrows)
    # 2.2 planets
    prow = []
    for pn in NINE:
        p = pl[pn]
        s = r.S(p["sign"])
        extra = [x for x in (dignity_word(r, p), r.tag("retrograde") if p.get("retrograde") and pn not in ("Rahu", "Ketu") else "",
                             r.tag("combust") if p.get("combust") else "", r.tag("vargottama") if p.get("vargottama") else "") if x]
        prow.append((r.P(pn), s + (f" ({', '.join(extra)})" if extra else ""), p["house"], dm(p["dms"]), r.N(p["nakshatra"]), p["pada"]))
    s22 = sub("2.2", t("The nine planets", "नवग्रह स्थितियाँ")) + table(
        [t("Planet", "ग्रह"), t("Sign", "राशि"), t("House", "भाव"), t("Degree", "अंश"), t("Nakshatra", "नक्षत्र"), t("Pada", "पद")], prow)
    # 2.3 strengths, yogas, doshas
    paras = []
    sb = (v.get("shadbala") or {}).get("bphs", {}).get("planets", {})
    for pn in SEVEN:
        p = pl[pn]
        d = p.get("dignity")
        if d not in ("exalted", "own sign", "moolatrikona", "debilitated"):
            continue
        h = p["house"]
        if d == "debilitated":
            nb = any(y["id"] == f"neecha_bhanga_{pn.lower()}" and y["status"] == "present" for y in v["yoga_library"]["found"])
            paras.append(t(f"{pn} is debilitated in {p['sign']}, in your {r.hth(h)}. Its themes ({r.theme(pn)}) ask for more conscious effort"
                           + (", though classical rules cancel the debility here (Neecha Bhanga), so the start may be slow and the result firm." if nb else "."),
                           f"{r.P(pn)} {r.S(p['sign'])} में नीच का है, आपके {r.hth(h)} में। इसके विषय ({r.theme(pn)}) अधिक सचेत प्रयास माँगते हैं"
                           + ("; पर शास्त्रीय नियमों से यहाँ नीचभंग होता है, यानी शुरुआत धीमी और परिणाम दृढ़।" if nb else "।")))
            continue
        word = {"exalted": t("exalted", "उच्च का"), "own sign": t("in its own sign", "स्वराशि में"), "moolatrikona": t("in its moolatrikona sign", "मूलत्रिकोण राशि में")}[d]
        lordof = [x["house"] for x in v["houses"] if x["lord"] == pn]
        role = t(f"lord of the {r.houses(lordof)}", f"{r.houses(lordof)} का स्वामी") if lordof else ""
        paras.append(t(f"{pn} is {word} in {p['sign']}, in your {r.hth(h)}" + (f", as {role}" if role else "") + ". "
                       f"This is a strong placement for {lc(r.mean('planet', pn)).rstrip('.')}; the matters of the {r.house(h)} get steady support.",
                       f"{r.P(pn)} {r.S(p['sign'])} में {word} है, आपके {r.hth(h)} में" + (f", {role} होकर" if role else "") + "। "
                       f"यह बलवान स्थिति है: {r.mean('planet', pn).rstrip('।')}; और {r.house(h)} के विषयों को स्थिर सहारा मिलता है।"))
    if v["divisional_charts"]["D9"].get("Lagna") == lag:
        paras.append(t(f"Your lagna is vargottama: {lag} rises in both the birth chart and the navamsa (D9), a classical sign of a steady temperament.",
                       f"आपकी लग्न वर्गोत्तम है: जन्म कुंडली और नवमांश (D9), दोनों में {r.S(lag)} — यह स्थिर स्वभाव का शास्त्रीय संकेत है।"))
    if sb:
        ranked = sorted((x for x in sb.items() if x[0] in SEVEN), key=lambda kv: -kv[1]["ratio"])
        top, low = ranked[0], ranked[-1]
        paras.append(t(f"By Shadbala (six-fold strength), {top[0]} is the strongest planet ({top[1]['ratio']:.2f} times its required strength) and "
                       f"{low[0]} the least ({low[1]['ratio']:.2f}).",
                       f"षड्बल के अनुसार {r.P(top[0])} सबसे बलवान ग्रह है (आवश्यक बल का {top[1]['ratio']:.2f} गुना) और "
                       f"{r.P(low[0])} सबसे कम ({low[1]['ratio']:.2f})।"))
    found = sorted((y for y in v["yoga_library"]["found"] if y.get("report") and y["status"] == "present"),
                   key=lambda y: (y["tone"] != "supportive", y.get("base_rate_present") or 1))
    yitems = []
    for y in found[:7]:
        m = MEAN["yoga"].get(y["id"], MEAN["yoga_category"].get(y["category"], {})).get(r.lang_key(), "")
        rate = y.get("base_rate_present")
        pct = "&lt;1" if rate is not None and rate < 0.005 else (round(rate * 100) if rate is not None else None)
        rtxt = t(f" Found in {pct}% of charts.", f" लगभग {pct}% कुंडलियों में मिलता है।") if rate is not None else ""
        yitems.append(f"<strong>{E(r.yoga_name(y['name']))}</strong> &mdash; {E(m)}{rtxt}")
    dos = v["doshas"]
    md = dos["mangal_dosha"]
    refs = [k for k, on in md["present_by_reference"].items() if on]
    mars = pl["Mars"]
    soft = mars["sign"] in ("Aries", "Scorpio", "Capricorn")
    REFN = {"from_lagna": t("the lagna", "लग्न"), "from_moon": t("the Moon", "चंद्र"), "from_venus": t("Venus", "शुक्र")}
    if refs:
        mtext = t(f"Mangal dosha check: Mars is in a dosha house counted from {' and '.join(REFN[x] for x in refs)}. "
                  + ("Mars is in its own or exaltation sign, which classically calms the dosha a great deal." if soft else
                     "For matching, the other person's chart is checked for the same; classical cancellations then apply."),
                  f"मंगल दोष की जाँच: {' और '.join(REFN[x] for x in refs)} से गिनने पर मंगल दोष वाले भाव में है। "
                  + ("मंगल स्वराशि या उच्च राशि में है, जो शास्त्रीय रूप से दोष को काफ़ी हद तक शांत करता है।" if soft else
                     "कुंडली मिलान में दूसरे व्यक्ति की कुंडली में भी यही देखा जाता है; तब शास्त्रीय परिहार लागू होते हैं।"))
    else:
        mtext = t("Mangal dosha check: Mars is not in a dosha house from the lagna, the Moon or Venus.",
                  "मंगल दोष की जाँच: लग्न, चंद्र और शुक्र, तीनों से गिनने पर मंगल दोष वाले भाव में नहीं है।")
    ks = dos["kaal_sarp"]
    if ks["present"]:
        ktext = t("All seven planets sit on one side of the Rahu-Ketu axis: the Kaal Sarp pattern is present.",
                  "सातों ग्रह राहु-केतु धुरी के एक ही ओर हैं: कालसर्प योग उपस्थित है।")
    elif ks.get("partial"):
        out = ", ".join(r.P(x) for x in ks.get("planet_outside_axis", []))
        ktext = t(f"Kaal Sarp check: {out} stands outside the Rahu-Ketu axis, so the full classical pattern is not formed, though the other planets cluster on one side.",
                  f"कालसर्प की जाँच: {out} राहु-केतु धुरी से बाहर है, इसलिए पूर्ण शास्त्रीय योग नहीं बनता, भले शेष ग्रह एक ओर जमा हों।")
    else:
        ktext = t("Kaal Sarp check: the planets are spread on both sides of the Rahu-Ketu axis; the pattern is not present.",
                  "कालसर्प की जाँच: ग्रह राहु-केतु धुरी के दोनों ओर फैले हैं; यह योग नहीं बनता।")
    s23 = (sub("2.3", t("Strengths, yogas and doshas", "कुंडली बल, योग एवं दोष")) + para(*paras)
           + (f"<p><strong>{t('Main yogas, the rarest first', 'प्रमुख योग, सबसे दुर्लभ पहले')}</strong></p>" + bullets(yitems) if yitems else "")
           + para(mtext, ktext))
    # 2.4 dashas
    vim = v["dashas"]["vimshottari"]
    now = ctx["now"]
    drows = []
    for m in vim["mahadashas"]:
        if m["start"] > add_years_iso(now, 25):
            break
        is_now = m["start"] <= now < m["end"]
        lordof = [x["house"] for x in v["houses"] if x["lord"] == m["lord"]]
        what = r.theme(m["lord"]) + t(f"; sits in the {r.house(pl[m['lord']]['house'])}", f"; {r.house(pl[m['lord']]['house'])} में") + \
            (t(f", rules the {r.houses(lordof)}", f", {r.houses(lordof)} का स्वामी") if lordof else "")
        span_ = f"{m['start'][:4]}&ndash;{m['end'][:4]}"
        drows.append(((span_, r.P(m["lord"]), "&mdash;", r.length(m["start"], m["end"]) + (t(" (current)", " (चालू)") if is_now else ""), what),
                      {"cls": "now" if is_now else ""}))
        if is_now:
            for a in m.get("antardashas", []):
                if a["end"] <= now or a["start"] > add_years_iso(now, 4):
                    continue
                cur = a["start"] <= now < a["end"]
                drows.append(((f"{r.month(a['start'])} &ndash; {r.month(a['end'])}", r.P(m["lord"]), r.P(a["lord"]),
                               t("current", "वर्तमान") if cur else "", r.theme(a["lord"])), {"cls": "now" if cur else ""}))
    s24 = sub("2.4", t("Vimshottari dasha and antardasha", "विंशोत्तरी दशा/अंतर्दशा")) + table(
        [t("Period", "अवधि"), t("Mahadasha", "महादशा"), t("Antardasha", "अंतर्दशा"), t("Length", "समयावधि"), t("What this phase brings forward", "यह चरण क्या सक्रिय करता है")], drows)
    # 2.5 vargas
    D9, D10 = v["divisional_charts"]["D9"], v["divisional_charts"]["D10"]
    def strong_in(D):
        out = []
        for pn in SEVEN:
            d = sign_dignity(pn, D[pn])
            if d in ("exalted", "own sign"):
                out.append(f"{r.P(pn)} ({r.S(D[pn])}, {r.tag(d)})")
        return out
    s9, s10 = strong_in(D9), strong_in(D10)
    vtxt = [t(f"In the navamsa (D9, marriage and inner strength) the lagna is {D9['Lagna']}"
              + (", the same as the birth chart (vargottama)" if D9["Lagna"] == lag else "") + "."
              + (f" Strong here: {', '.join(s9)}." if s9 else ""),
              f"नवमांश (D9, विवाह और आंतरिक बल) में लग्न {r.S(D9['Lagna'])} है" + (", जन्म कुंडली के समान (वर्गोत्तम)" if D9["Lagna"] == lag else "") + "।"
              + (f" यहाँ बलवान: {', '.join(s9)}।" if s9 else "")),
            t(f"In the dashamsa (D10, career) the lagna is {D10['Lagna']}, ruled by {SIGN_LORD[D10['Lagna']]}."
              + (f" Strong here: {', '.join(s10)}." if s10 else ""),
              f"दशमांश (D10, करियर) में लग्न {r.S(D10['Lagna'])} है, जिसका स्वामी {r.P(SIGN_LORD[D10['Lagna']])} है।"
              + (f" यहाँ बलवान: {', '.join(s10)}।" if s10 else ""))]
    vg = [r.P(pn) for pn in SEVEN if pl[pn].get("vargottama")]
    if vg:
        vtxt.append(t(f"Vargottama planets (same sign in D1 and D9, a mark of steadiness): {', '.join(vg)}.",
                      f"वर्गोत्तम ग्रह (D1 और D9 में एक ही राशि, स्थिरता का संकेत): {', '.join(vg)}।"))
    s25 = sub("2.5", t("Divisional chart cross-check", "वर्ग कुंडली क्रॉस-चेक")) + para(*vtxt)
    # 2.6 houses
    sav = v["ashtakavarga"]["sarva"]
    hrows = []
    for x in v["houses"]:
        occ = [o for o in x["occupants"] if o in NINE]
        if occ:
            parts = []
            for o in occ:
                dw = dignity_word(r, pl[o])
                parts.append(r.P(o) + (f" ({dw})" if dw else ""))
            a = ", ".join(parts) + " &mdash; " + "; ".join(r.theme(o) for o in occ[:2])
        else:
            a = t(f"empty; its lord {x['lord']} sits in the {r.house(x['lord_placed_in_house'])}",
                  f"ख़ाली भाव; भाव-स्वामी {r.P(x['lord'])} {r.house(x['lord_placed_in_house'])} में")
        pts = sav.get(x["sign"])
        if pts is not None:
            band = t("strong", "बलवान") if pts >= 28 else t("needs effort", "प्रयास माँगता है") if pts < 25 else t("average", "सामान्य")
            a += t(f" &middot; Ashtakavarga {pts} ({band})", f" &middot; अष्टकवर्ग {pts} ({band})")
        hrows.append((f"{x['house']} ({r.S(x['sign'])})", HOUSE_THEME[x["house"]][1 if r.hi else 0], a))
    s26 = sub("2.6", t("House by house", "भावानुसार विश्लेषण")) + table([t("House", "भाव"), t("Signifies", "कारकत्व"), t("Analysis", "विश्लेषण")], hrows)
    extra = ""
    secs = {x["key"]: x for x in ctx.get("details", {}).get("sections", [])}
    for i, key in enumerate(("panchang", "ashtakavarga", "yogini", "jaimini", "varshaphal", "kp")):
        if key in secs:
            extra += detail_html(r, secs[key], f"2.{7 + i}")
    return section(2, t("Vedic Astrology", "वैदिक ज्योतिष"), para(intro) + s21 + s22 + s23 + s24 + s25 + s26 + extra, tinted=True)


def sec3(r, c, ctx):
    t = r.t
    w = c["western"]
    P = w["planets"]
    intro = t("In the tropical Western system the Sun, Moon and rising sign often fall in different signs from the Vedic chart. That is not an error: "
              "the two systems count the zodiac from different starting points (about 24° apart today).",
              "पाश्चात्य ट्रॉपिकल पद्धति में सूर्य, चंद्र और लग्न अक्सर वैदिक सिडेरियल गणना से अलग राशियों में आ जाते हैं — यह ग़लती नहीं, दो अलग शून्य-बिंदु "
              "(आज लगभग 24° का अंतर) चुनने का परिणाम है।")
    asc_sign = w["ascendant"]["sign"]
    asc_deg = w["ascendant"]["dms"].split("°")[0]
    rows = [(t("Sun", "सूर्य"), f"{r.S(P['Sun']['sign'])} {P['Sun']['dms'].split('°')[0]}°", t("core identity: ", "मूल पहचान: ") + SIGN_TRAIT[P["Sun"]["sign"]][1 if r.hi else 0]),
            (t("Moon", "चंद्र"), f"{r.S(P['Moon']['sign'])} {P['Moon']['dms'].split('°')[0]}°", t("emotional nature: ", "भावनात्मक स्वभाव: ") + SIGN_TRAIT[P["Moon"]["sign"]][1 if r.hi else 0]),
            (t("Rising", "लग्न (राइज़िंग)"), f"{r.S(asc_sign)} {asc_deg}°", t("the face you show the world: ", "दुनिया के सामने प्रस्तुत चेहरा: ") + SIGN_TRAIT[asc_sign][1 if r.hi else 0])]
    s31 = sub("3.1", t("Sun &middot; Moon &middot; Rising", "सूर्य &middot; चंद्र &middot; लग्न")) + table([t("Point", "बिंदु"), t("Sign", "राशि"), t("Meaning", "अर्थ")], rows)
    major = [a for a in w["natal_aspects"] if a["aspect"] in ASPECT_SENSE]
    major.sort(key=lambda a: a["orb"])
    arows = []
    for a in major[:8]:
        sense = ASPECT_SENSE[a["aspect"]][1 if r.hi else 0]
        arows.append((r.body(a["a"]), HS.ASPECT.get(a["aspect"], a["aspect"]) if r.hi else a["aspect"], r.body(a["b"]),
                      f"{a['orb']:.1f}°",
                      f"{r.theme(a['a'])} + {r.theme(a['b'])}: {sense}"))
    s32 = sub("3.2", t("Key aspects", "प्रमुख दृष्टि संबंध (एस्पेक्ट्स)")) + table(
        [t("Planet A", "ग्रह अ"), t("Aspect", "एस्पेक्ट"), t("Planet B", "ग्रह ब"), t("Orb", "ऑर्ब"), t("Reading", "व्याख्या")], arows)
    by_el, by_mod = {}, {}
    for pn in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        by_el.setdefault(P[pn]["element"], []).append(r.P(pn))
        by_mod.setdefault(P[pn]["modality"], []).append(r.P(pn))
    erows = [(t(f"{e} element", f"{ELEMENT_HI[e]} तत्व"), r.count(len(by_el.get(e, [])), "planet", "planets", "ग्रह") + (f" ({', '.join(by_el[e])})" if by_el.get(e) else ""))
             for e in ("Fire", "Earth", "Air", "Water")]
    MODH = {"Cardinal": "चर गुण (कार्डिनल)", "Fixed": "स्थिर गुण (फ़िक्स्ड)", "Mutable": "द्विस्वभाव (म्यूटेबल)"}
    erows += [(t(m, MODH[m]), r.count(len(by_mod.get(m, [])), "planet", "planets", "ग्रह") + (f" ({', '.join(by_mod[m])})" if by_mod.get(m) else ""))
              for m in ("Cardinal", "Fixed", "Mutable")]
    dom = max(("Fire", "Earth", "Air", "Water"), key=lambda e: len(by_el.get(e, [])))
    miss = [e for e in ("Fire", "Earth", "Air", "Water") if not by_el.get(e)]
    etxt = t(f"{dom} is the strongest element." + (f" {', '.join(miss)} is missing among the seven classical planets, a quality to develop consciously." if miss else ""),
             f"{ELEMENT_HI[dom]} सबसे प्रबल तत्व है।" + (f" सात शास्त्रीय ग्रहों में {', '.join(ELEMENT_HI[e] for e in miss)} अनुपस्थित है — इसे सचेत रूप से विकसित करना होगा।" if miss else ""))
    s33 = sub("3.3", t("Element and modality balance", "तत्व एवं गुण संतुलन")) + table([t("Element / mode", "तत्व/गुण"), t("Detail", "विवरण")], erows) + para(etxt)
    hits = (w.get("transits_now") or {}).get("hits_to_natal", [])
    trows = []
    for h in hits:
        dates = ", ".join(r.date(d) for d in h.get("exact_dates", [])[:3])
        natal = r.body(h["natal"])
        sense = ASPECT_SENSE.get(h["aspect"], (h["aspect"], h["aspect"]))[1 if r.hi else 0]
        trows.append((r.body(h["transit"]),
                      f"{natal} ({HS.ASPECT.get(h['aspect'], h['aspect']) if r.hi else h['aspect']}, {h['orb']:.1f}°)", dates,
                      f"{r.theme(h['transit'])} &rarr; {r.theme(h['natal'])}: {sense}"))
    sr = w["returns"]["saturn_returns"]
    past = [x for x in sr if x["last"] <= ctx["now"]]
    nxt = [x for x in sr if x["first"] > ctx["now"]]
    srt = t((f"Last Saturn return: {r.month(past[-1]['first'])}" + (f" to {r.month(past[-1]['last'])}" if past[-1]["last"] != past[-1]["first"] else "") + ". " if past else "")
            + (f"Next: {r.month(nxt[0]['first'])}. A Saturn return is a time to review and rebuild structures." if nxt else ""),
            (f"पिछली शनि-वापसी: {r.month(past[-1]['first'])}" + (f" से {r.month(past[-1]['last'])}" if past[-1]["last"] != past[-1]["first"] else "") + "। " if past else "")
            + (f"अगली: {r.month(nxt[0]['first'])}। शनि-वापसी ढाँचों की समीक्षा और पुनर्निर्माण का समय है।" if nxt else ""))
    s34 = sub("3.4", t("Current transits", "वर्तमान गोचर (ट्रांज़िट)")) + (table(
        [t("Transiting planet", "गोचर ग्रह"), t("To natal point", "जन्म बिंदु से संबंध"), t("Exact dates", "सटीक तिथियाँ"), t("Meaning", "महत्व")], trows) if trows else
        para(t("No major outer-planet transit is exact on a natal point right now.", "अभी किसी जन्म-बिंदु पर कोई बड़ा बाहरी-ग्रह गोचर सटीक नहीं है।"))) + para(srt)
    s35 = sub("3.5", t("Synastry (two-person readings only)", "सिनास्ट्री (केवल द्वि-व्यक्ति विश्लेषण हेतु)")) + para(t(
        "This is a single-person reading, so synastry does not apply. Use Kundali Milan in the app with a partner's details for compatibility.",
        "यह एकल-व्यक्ति विश्लेषण है, इसलिए सिनास्ट्री यहाँ लागू नहीं होती। अनुकूलता के लिए ऐप में साथी के विवरण के साथ कुंडली मिलान देखें।"))
    wt = next((x for x in ctx.get("details", {}).get("sections", []) if x["key"] == "western_timing"), None)
    s36 = detail_html(r, wt, "3.6") if wt else ""
    return section(3, t("Western Astrology (Tropical)", "पाश्चात्य ज्योतिष (ट्रॉपिकल)"), para(intro) + s31 + s32 + s33 + s34 + s36 + s35)


def sec4(r, c, ctx, F):
    t = r.t
    b = c["bazi"]
    PIL = [("year", t("Year pillar", "वर्ष स्तंभ")), ("month", t("Month pillar", "माह स्तंभ")), ("day", t("Day pillar (Day Master)", "दिन स्तंभ (डे मास्टर)")),
           ("hour", t("Hour pillar", "समय स्तंभ"))]
    intro = t("BaZi divides the moment of birth into four pairs (year, month, day, hour), each a heavenly stem over an earthly branch, "
              "on the Chinese solar calendar.",
              "चीनी बाज़ी पद्धति में जन्म-क्षण को चार जोड़ों (वर्ष, माह, दिन, समय) में बाँटा जाता है, हर जोड़े में एक स्वर्गीय स्टेम और एक पार्थिव ब्रांच; "
              "यह गणना चीनी सौर पंचांग पर आधारित है।")
    rows = []
    for k, lab in PIL:
        p = b["pillars"][k]
        st, br = p["text"][0], p["text"][1]
        sp, bp = p["pinyin"].split("-")
        rows.append((lab, f"{st} {sp} ({HS.BAZI[p['polarity']] if r.hi else p['polarity']} {r.el(p['stem_element'])})",
                     f"{br} {bp} &mdash; {HS.BAZI.get(p['animal'], p['animal']) if r.hi else p['animal']} ({r.el(p['branch_element'])})",
                     "" if k == "day" else r.ten_god(p["ten_god_stem"])))
    s41 = sub("4.1", t("The four pillars", "चार स्तंभ")) + table(
        [t("Pillar", "स्तंभ"), t("Heavenly stem", "स्वर्गीय स्टेम"), t("Earthly branch", "पार्थिव ब्रांच"), t("Ten God of the stem", "स्टेम का दस देवता")], rows)
    dm = b["day_master"]
    hs = b["day_master_strength_heuristic"]
    verdict = hs["verdict"]
    vtxt = (t("leans strong", "बलवान की ओर") if "strong" in verdict else t("leans weak", "दुर्बल की ओर") if "weak" in verdict
            else t("balanced or mixed", "संतुलित या मिश्रित"))
    sea = SEASON.get(hs["month_season_status"][:1], (hs["month_season_status"], hs["month_season_status"]))[1 if r.hi else 0]
    s42 = sub("4.2", t("Day Master and its strength", "डे मास्टर एवं संरचनात्मक बल")) + para(t(
        f"Your Day Master is {dm['polarity']} {dm['element']} ({dm['stem']}), the element that stands for you. In the season of your birth it is "
        f"{sea}; weighing support ({hs['supporters']}) against drain ({hs['drainers']}), it {vtxt}.",
        f"आपका डे मास्टर {HS.BAZI[dm['polarity']]} {r.el(dm['element'])} ({dm['stem']}) है — वह तत्व जो आपका प्रतीक है। जन्म के मौसम में यह "
        f"{sea} है; सहारा ({hs['supporters']}) और क्षय ({hs['drainers']}) तौलने पर यह {vtxt} है।"))
    bal = b["element_balance_visible_8"]
    srt = sorted(bal.items(), key=lambda kv: -kv[1])
    erows = []
    for e, n in srt:
        if e == dm["element"]:
            note = t("the Day Master's own element", "डे मास्टर का अपना तत्व")
        elif n == 0:
            note = t("absent from the eight characters: a quality to bring in consciously", "आठ अक्षरों में अनुपस्थित — सचेत प्रयास से लाना")
        elif n == srt[0][1]:
            note = t("the heaviest element", "सबसे भारी तत्व")
        else:
            note = ""
        erows.append((r.el(e), f"{n} / 8", note))
    s43 = sub("4.3", t("Five-element balance", "पंचतत्व संतुलन")) + table([t("Element", "तत्व"), t("Count in eight characters", "आठ अक्षरों में संख्या"), t("Note", "टिप्पणी")], erows)
    tg = []
    for k, lab in PIL:
        if k == "day":
            continue
        g = b["pillars"][k]["ten_god_stem"]
        tg.append(t(f"{lab}: {g} &mdash; {r.tg_theme(g)}.", f"{lab}: {r.ten_god(g)} &mdash; {r.tg_theme(g)}।"))
    s44 = sub("4.4", t("Ten Gods", "दस देवता (&#21313;&#31070;) विश्लेषण")) + bullets(tg)
    lrows = []
    cur = b["luck_pillars"].get("current") or {}
    for lp in b["luck_pillars"]["pillars"]:
        isnow = cur and lp["from"] == cur.get("from")
        lrows.append(((f"{lp['from'][:4]}&ndash;{lp['to'][:4]}" + (t(" (current)", " (वर्तमान)") if isnow else ""), f"{lp['text']} {lp['pinyin']}",
                       t(f"age {lp['start_age']:.0f}&ndash;{lp['end_age']:.0f}", f"आयु {lp['start_age']:.0f}&ndash;{lp['end_age']:.0f}"),
                       f"{r.ten_god(lp['ten_god_stem'])} &mdash; {r.tg_theme(lp['ten_god_stem'])}"), {"cls": "now" if isnow else ""}))
    for yr in (F or {}).get("bazi", {}).get("annual", [])[:3]:
        rel = "; ".join(r.rel(x) for x in yr["new_branch_relations"][:2])
        lrows.append((t(f"Year from Feb {yr['from'][:4]}", f"फ़रवरी {yr['from'][:4]} से वर्ष"), f"{yr['text']} {yr['pinyin']}", "",
                      f"{r.ten_god(yr['ten_god_stem'])} &mdash; {r.tg_theme(yr['ten_god_stem'])}" + (f"; {rel}" if rel else "")))
    s45 = sub("4.5", t("Luck pillars and annual pillars", "लक पिलर एवं वार्षिक स्तंभ")) + table(
        [t("Cycle", "चक्र"), t("Stem / branch", "स्टेम/ब्रांच"), t("Ages", "आयु"), t("Theme", "विषय")], lrows)
    s46 = sub("4.6", t("BaZi compatibility (two-person readings only)", "बाज़ी अनुकूलता (केवल द्वि-व्यक्ति विश्लेषण हेतु)")) + para(t(
        "This is a single-person reading, so BaZi compatibility does not apply here.", "यह एकल-व्यक्ति विश्लेषण है, इसलिए बाज़ी अनुकूलता यहाँ लागू नहीं होती।"))
    return section(4, t("Chinese BaZi (Four Pillars)", "चीनी बाज़ी (चार स्तंभ)"), para(intro) + s41 + s42 + s43 + s44 + s45 + s46, tinted=True)


def sec5(r, c, ctx):
    t = r.t
    n = c["numerology"]
    py = n["pythagorean"]
    ind = n["indian"]
    def row(label, key, val):
        base = val if val in (11, 22, 33) or val <= 9 else AF_reduce(val)
        return (label, val, " ".join(x for x in (r.mean("number_type", key), r.mean("number", base)) if x))
    rows = [row(t("Life Path", "जीवन-पथ अंक"), "life_path", n["life_path"]["value"]),
            row(t("Destiny (Expression)", "भाग्य/अभिव्यक्ति अंक"), "destiny", py["destiny_expression"]),
            row(t("Soul Urge", "आत्मा की चाह अंक"), "soul", py["soul_urge"]),
            row(t("Personality", "व्यक्तित्व अंक"), "personality", py["personality"]),
            row(t("Mulank (day of birth)", "मूलांक"), "mulank", ind["mulank_driver"]),
            row(t("Bhagyank (full date)", "भाग्यांक"), "bhagyank", ind["bhagyank_conductor"]),
            row(t("Chaldean name number", "कैल्डियन नामांक"), "name", n["chaldean"]["single_digit"]),
            row(t(f"Personal Year ({ctx['now'][:4]})", f"वर्तमान वैयक्तिक वर्ष ({ctx['now'][:4]})"), "personal_year", n["personal_cycles"]["personal_year"])]
    rows[6] = (rows[6][0], f"{n['chaldean']['compound_number']}/{n['chaldean']['single_digit']}", rows[6][2])
    lp = n["life_path"]
    alt = lp.get("alternate_method_value")
    notes = []
    if alt and alt != lp["value"]:
        notes.append(t(f"Counting all digits of the date together gives {alt} instead of {lp['value']}; both readings are shown in the app.",
                       f"तिथि के सभी अंक एक साथ जोड़ने पर {lp['value']} के स्थान पर {alt} आता है; ऐप में दोनों दिखाए गए हैं।"))
    miss = ind.get("missing_numbers") or []
    if miss:
        notes.append(t(f"Loshu grid: the numbers {', '.join(map(str, miss))} are missing from the date of birth; traditionally these are qualities to build.",
                       f"लोशु ग्रिड: जन्म-तिथि में {', '.join(map(str, miss))} अंक अनुपस्थित हैं; परंपरा से इन्हें विकसित करने योग्य गुण माना जाता है।"))
    kua = n.get("kua") or {}
    if kua.get("value"):
        notes.append(t(f"Kua number {kua['value']} ({kua['group']} group).", f"कुआ अंक {kua['value']} ({'पूर्व' if kua['group'] == 'East' else 'पश्चिम'} समूह)।"))
    notes.append(t(f"Name numbers are calculated from \"{E(py['name_used'])}\". If an official document spells the name differently, the Destiny number may change.",
                   f"नाम के अंक \"{E(py['name_used'])}\" वर्तनी पर आधारित हैं। किसी औपचारिक दस्तावेज़ में वर्तनी अलग हो तो भाग्य अंक बदल सकता है।"))
    inner = table([t("Number", "अंक"), t("Value", "मान"), t("Meaning", "मूल अर्थ")], rows) + para(*notes)
    return section(5, t("Numerology", "अंकशास्त्र"), inner)


def AF_reduce(n):
    while n > 9 and n not in (11, 22, 33):
        n = sum(map(int, str(n)))
    return n


# Theme families used to compare systems.
FAMILY = {"drive": ("drive and courage", "उत्साह और साहस"), "structure": ("discipline and structure", "अनुशासन और संरचना"),
          "mind": ("intellect and communication", "बुद्धि और संवाद"), "heart": ("feeling and relationships", "भावना और संबंध"),
          "growth": ("wisdom and growth", "ज्ञान और विकास")}
PLANET_FAMILY = {"Sun": "drive", "Mars": "drive", "Saturn": "structure", "Mercury": "mind", "Moon": "heart", "Venus": "heart", "Jupiter": "growth"}
ELEMENT_FAMILY = {"Fire": "drive", "Earth": "structure", "Air": "mind", "Water": "heart", "Wood": "growth", "Metal": "structure"}
NUMBER_FAMILY = {1: "drive", 9: "drive", 4: "structure", 8: "structure", 22: "structure", 3: "mind", 5: "mind", 2: "heart", 6: "heart",
                 7: "growth", 11: "growth", 33: "heart"}


def sec6(r, c, ctx, fc):
    t = r.t
    v, w, b, n = c["vedic"], c["western"], c["bazi"], c["numerology"]
    sb = v["shadbala"]["bphs"]["planets"]
    strong = [p for p in SEVEN if v["planets"][p].get("dignity") in ("exalted", "own sign", "moolatrikona")]
    top = max((p for p in SEVEN), key=lambda p: sb.get(p, {}).get("ratio", 0))
    vfam = PLANET_FAMILY[strong[0] if strong else top]
    by_el = {}
    for pn in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        by_el[w["planets"][pn]["element"]] = by_el.get(w["planets"][pn]["element"], 0) + 1
    wel = max(by_el, key=by_el.get)
    wfam = ELEMENT_FAMILY[wel]
    bal = b["element_balance_visible_8"]
    bel = max(bal, key=bal.get)
    bfam = ELEMENT_FAMILY[bel]
    lpv = n["life_path"]["value"]
    nfam = NUMBER_FAMILY.get(lpv, "growth")
    votes = {}
    for sys_, fam in (("vedic", vfam), ("western", wfam), ("bazi", bfam), ("numerology", nfam)):
        votes.setdefault(fam, []).append(sys_)
    best_fam, systems = max(votes.items(), key=lambda kv: len(kv[1]))
    SYS = {"vedic": t("Vedic", "वैदिक"), "western": t("Western", "पाश्चात्य"), "bazi": t("BaZi", "बाज़ी"), "numerology": t("numerology", "अंकशास्त्र")}
    ev = {"vedic": t(f"{'strong ' + ', '.join(strong) if strong else top + ' as the strongest planet'}",
                     f"{'बलवान ' + ', '.join(r.P(x) for x in strong) if strong else r.P(top) + ' सबसे बलवान ग्रह'}"),
          "western": t(f"{wel} as the leading element", f"{ELEMENT_HI[wel]} प्रमुख तत्व"),
          "bazi": t(f"{bel} as the heaviest element", f"{ELEMENT_HI[bel]} सबसे भारी तत्व"),
          "numerology": t(f"Life Path {lpv}", f"जीवन-पथ {lpv}")}
    if len(systems) >= 2:
        agree = t(f"The clearest pattern: {len(systems)} of the four systems point to <strong>{FAMILY[best_fam][0]}</strong> "
                  f"({'; '.join(SYS[s] + ': ' + ev[s] for s in systems)}). When independent calculations agree like this, it is worth taking seriously.",
                  f"सबसे साफ़ पैटर्न: चार में से {len(systems)} प्रणालियाँ <strong>{FAMILY[best_fam][1]}</strong> की ओर इशारा करती हैं "
                  f"({'; '.join(SYS[s] + ': ' + ev[s] for s in systems)})। जब स्वतंत्र गणनाएँ इस तरह सहमत हों, तो बात गंभीरता से लेने योग्य है।")
    else:
        agree = t("The four systems each stress a different theme here (" + "; ".join(SYS[s] + ": " + ev[s] for s in ("vedic", "western", "bazi", "numerology"))
                  + "), so no single theme dominates; the chart is many-sided.",
                  "यहाँ चारों प्रणालियाँ अलग-अलग विषय पर ज़ोर देती हैं (" + "; ".join(SYS[s] + ": " + ev[s] for s in ("vedic", "western", "bazi", "numerology"))
                  + "), इसलिए कोई एक विषय हावी नहीं; कुंडली बहुआयामी है।")
    others = [s for s in ("vedic", "western", "bazi", "numerology") if s not in systems]
    differ = ""
    if len(systems) >= 2 and others:
        differ = t("Where they differ: " + "; ".join(f"{SYS[s]} stresses {FAMILY[{'vedic': vfam, 'western': wfam, 'bazi': bfam, 'numerology': nfam}[s]][0]} ({ev[s]})" for s in others)
                   + ". Read this as a second side of the same person, not a contradiction.",
                   "जहाँ वे अलग हैं: " + "; ".join(f"{SYS[s]} {FAMILY[{'vedic': vfam, 'western': wfam, 'bazi': bfam, 'numerology': nfam}[s]][1]} पर ज़ोर देता है ({ev[s]})" for s in others)
                   + "। इसे विरोधाभास नहीं, उसी व्यक्ति का दूसरा पहलू समझें।")
    cur = v["dashas"]["vimshottari"]["current"]
    md, ad = cur["mahadasha"], cur["antardasha"]
    nxt = None
    for m in v["dashas"]["vimshottari"]["mahadashas"]:
        for a in m.get("antardashas", []):
            if a["start"] == ad["end"]:
                nxt = (m["lord"], a["lord"], a["start"])
    ss = v["sade_sati"]
    sat = (t("Saturn is in its Sade Sati passage over the natal Moon.", "शनि जन्म-चंद्र पर साढ़े साती में है।") if ss.get("sade_sati_now") else
           t("Saturn is 8th from the Moon (Ashtama Shani).", "शनि चंद्र से अष्टम है (अष्टम शनि)।") if ss.get("ashtama_shani_now") else
           t("Saturn is in a Kantaka position from the Moon (4th, 7th or 10th).", "शनि चंद्र से कंटक स्थान (4, 7 या 10) में है।") if ss.get("kantaka_shani_now") else
           t(f"Saturn is {ORD_EN.get(ss['saturn_house_from_moon'], str(ss['saturn_house_from_moon']) + 'th')} from the Moon, with no Sade Sati now.",
             f"शनि चंद्र से {AF.ORD_HI[ss['saturn_house_from_moon']]} स्थान पर है; अभी साढ़े साती नहीं।"))
    ann = next((y for y in b["annual_pillars"] if y["year"] == b.get("current_annual_year")), None)
    pyr = n["personal_cycles"]["personal_year"]
    timing = t(f"Timing now: in the Vedic system you are in the {md['lord']} mahadasha (to {r.month(md['end'])}), {ad['lord']} antardasha to {r.month(ad['end'])}"
               + (f", then {nxt[1]} from {r.month(nxt[2])}" if nxt else "") + f". {sat}"
               + (f" The BaZi year {ann['text']} brings {ann['ten_god_stem']} ({r.tg_theme(ann['ten_god_stem'])})." if ann else "")
               + f" Numerology: Personal Year {pyr}.",
               f"समय की दृष्टि से अभी: वैदिक पद्धति में {r.P(md['lord'])} महादशा ({r.month(md['end'])} तक), {r.P(ad['lord'])} अंतर्दशा {r.month(ad['end'])} तक"
               + (f", फिर {r.month(nxt[2])} से {r.P(nxt[1])} अंतर्दशा" if nxt else "") + f"। {sat}"
               + (f" बाज़ी वर्ष {ann['text']} में {r.ten_god(ann['ten_god_stem'])} ({r.tg_theme(ann['ten_god_stem'])}) सक्रिय है।" if ann else "")
               + f" अंकशास्त्र: वैयक्तिक वर्ष {pyr}।")
    rows = []
    for a in fc["areas"]:
        o = a["outlook"]
        best = next((y for y in a["years"] if y["id"] == o["best"]), None)
        care = next((y for y in a["years"] if y["id"] == o["care"]), None)
        rows.append((a["title"][r.lang_key()], o[r.lang_key()],
                     f"{r.month(best['from'])} &ndash; {r.month(best['to'])}" if best else t("none clearly ahead", "कोई स्पष्ट नहीं"),
                     f"{r.month(care['from'])} &ndash; {r.month(care['to'])}" if care else t("none stands out", "कोई विशेष नहीं")))
    glance = (f"<p><strong>{t('The next three years at a glance', 'अगले तीन वर्ष एक नज़र में')}</strong></p>"
              + table([t("Area", "क्षेत्र"), t("Outlook", "रुझान"), t("Strongest year", "सबसे अच्छा वर्ष"), t("Year needing care", "सावधानी का वर्ष")], rows)
              + f'<p class="guidance">{t("The app&#39;s Forecast screen shows each year with its reasons.", "ऐप की भविष्यफल स्क्रीन पर हर वर्ष उसके कारणों के साथ दिखाया गया है।")}</p>')
    inner = para(t("This is the section that turns four reports into one reading.", "यही वह खंड है जो चार अलग रिपोर्टों को एक विश्लेषण बनाता है।"), agree, differ, timing) + glance
    return section(6, t("Comparison Across the Systems", "प्रणालियों की तुलनात्मक समीक्षा"), inner, tinted=True)


def needs_support(v):
    """Planets that classically ask for support, strongest reason first: debilitated, combust, enemy sign, weak Shadbala."""
    sb = v["shadbala"]["bphs"]["planets"]
    out = []
    for p in SEVEN:
        x = v["planets"][p]
        why = []
        if x.get("dignity") == "debilitated":
            why.append("debilitated")
        if x.get("combust"):
            why.append("combust")
        if x.get("dignity") == "enemy's sign":
            why.append("enemy's sign")
        if sb.get(p, {}).get("ratio", 2) < 1:
            why.append("weak shadbala")
        if why:
            out.append((p, why))
    order = {"debilitated": 0, "combust": 1, "weak shadbala": 2, "enemy's sign": 3}
    out.sort(key=lambda pw: min(order[w] for w in pw[1]))
    return out


def sec7(r, c, ctx, fc):
    t = r.t
    v, b = c["vedic"], c["bazi"]
    lk = next((x for x in ctx.get("details", {}).get("sections", []) if x["key"] == "lalkitab"), None)
    dos = v["doshas"]
    pl = v["planets"]
    SEV = {"none": t("Not present", "नहीं है"), "mild": t("Mild", "हल्का"), "moderate": t("Moderate", "मध्यम")}
    rows = []
    md = dos["mangal_dosha"]
    refs = [k for k, on in md["present_by_reference"].items() if on]
    soft = pl["Mars"]["sign"] in ("Aries", "Scorpio", "Capricorn")
    if refs:
        sev = "mild" if soft or len(refs) == 1 else "moderate"
        rows.append((t("Mangal dosha", "मंगल दोष"), pill(sev, SEV[sev]),
                     t(f"Mars in a dosha house from {len(refs)} of 3 references" + ("; Mars in its own or exaltation sign calms it." if soft else "."),
                       f"3 में से {len(refs)} गणनाओं से मंगल दोष वाले भाव में" + ("; स्वराशि/उच्च मंगल इसे शांत करता है।" if soft else "।"))))
    else:
        rows.append((t("Mangal dosha", "मंगल दोष"), pill("none", SEV["none"]), t("Mars is outside the dosha houses from the lagna, Moon and Venus.", "लग्न, चंद्र और शुक्र से मंगल दोष वाले भावों से बाहर है।")))
    ks = dos["kaal_sarp"]
    if ks["present"]:
        rows.append((t("Kaal Sarp", "कालसर्प दोष"), pill("moderate", SEV["moderate"]), t("All seven planets on one side of Rahu-Ketu.", "सातों ग्रह राहु-केतु के एक ओर।")))
    else:
        rows.append((t("Kaal Sarp", "पूर्ण कालसर्प दोष"), pill("none", SEV["none"]),
                     t("Partial pattern only: one planet outside the axis." if ks.get("partial") else "Planets on both sides of the axis.",
                       "केवल आंशिक पैटर्न: एक ग्रह धुरी से बाहर।" if ks.get("partial") else "ग्रह धुरी के दोनों ओर।")))
    pi = dos["pitra_dosha_indicators"]
    pind = [k for k in ("sun_with_rahu_or_ketu", "rahu_or_ketu_in_9th") if pi.get(k)]
    rows.append((t("Pitru dosha", "पितृ दोष"), pill("mild" if pind else "none", SEV["mild" if pind else "none"]),
                 t("Indicator present: " + ", ".join(x.replace("_", " ") for x in pind) if pind else "No Sun-node conjunction and no node in the 9th.",
                   "संकेत उपस्थित: " + ", ".join({"sun_with_rahu_or_ketu": "सूर्य-राहु/केतु युति", "rahu_or_ketu_in_9th": "नवम में राहु/केतु"}[x] for x in pind) if pind
                   else "सूर्य-राहु/केतु युति या नवम भाव में राहु/केतु नहीं।")))
    if dos.get("guru_chandal"):
        rows.append((t("Guru Chandal (Jupiter with Rahu)", "गुरु चांडाल (गुरु-राहु युति)"), pill("mild", SEV["mild"]),
                     t("A caution about advice and ethics; many astrologers give it little weight.", "सलाह और नैतिकता के प्रति सावधानी; कई ज्योतिषी इसे कम महत्व देते हैं।")))
    if dos.get("shani_rahu"):
        rows.append((t("Shani-Rahu (Shrapit) pattern", "शनि-राहु (श्रापित) योग"), pill("mild", SEV["mild"]),
                     t("Asks for patience where Saturn and Rahu meet.", "जहाँ शनि और राहु मिलते हैं, वहाँ धैर्य माँगता है।")))
    ss = v["sade_sati"]
    if ss.get("sade_sati_now"):
        rows.append((t("Sade Sati (now)", "साढ़े साती (अभी)"), pill("moderate", SEV["moderate"]),
                     t("Saturn's passage around the Moon: responsibility and slower results, not disaster.", "चंद्र के आसपास शनि का गोचर: ज़िम्मेदारी और धीमे परिणाम, विपत्ति नहीं।")))
    elif ss.get("ashtama_shani_now") or ss.get("kantaka_shani_now"):
        rows.append((t("Saturn from the Moon (now)", "चंद्र से शनि (अभी)"), pill("mild", SEV["mild"]),
                     t("Ashtama or Kantaka Shani: pace yourself and keep plans simple.", "अष्टम या कंटक शनि: अपनी गति संभालें और योजनाएँ सरल रखें।")))
    for p, why in needs_support(v)[:2]:
        if "debilitated" in why or "combust" in why:
            rows.append((t(f"{p} needs support", f"{r.P(p)} को सहारा चाहिए"), pill("mild", SEV["mild"]),
                         t(f"{p} is {' and '.join(why)}; its themes ({r.theme(p)}) take more conscious effort.",
                           f"{r.P(p)} {' और '.join(WHY_HI[w] for w in why)} है; इसके विषय ({r.theme(p)}) अधिक सचेत प्रयास माँगते हैं।")))
    clash = [x for x in b["interactions"].get("annual_pillar_vs_natal", []) if "clash" in x["type"]]
    if clash:
        rows.append((t(f"BaZi year clash ({b.get('current_annual_year')})", f"बाज़ी वार्षिक टकराव ({b.get('current_annual_year')})"), pill("mild", SEV["mild"]),
                     t("A clash this year: " + r.rel(clash[0]) + ". Read it as a year of change in that part of life, not loss.",
                       "इस वर्ष टकराव: " + r.rel(clash[0]) + "। इसे जीवन के उस हिस्से में बदलाव का वर्ष समझें, हानि का नहीं।")))
    s_table = table([t("Dosha", "दोष"), t("Severity", "गंभीरता"), t("Summary", "सारांश")], rows)
    # remedies
    lag_lord = SIGN_LORD[v["lagna"]["sign"]]
    fb = set(v["parashari"]["functional_nature"].get("functional_benefics", [])) | {lag_lord}
    rem = []
    chosen = [p for p, _ in needs_support(v)]
    cur = v["dashas"]["vimshottari"]["current"]
    for p in (cur["mahadasha"]["lord"], cur["antardasha"]["lord"]):
        if p not in chosen:
            chosen.append(p)
    for p in chosen[:4]:
        m, day, gift, gem, finger = REMEDY[p]
        why = t("to support the running period" if p in (cur["mahadasha"]["lord"], cur["antardasha"]["lord"]) and p not in dict(needs_support(v)) else "to steady a planet that needs support",
                "चालू दशा को सहारा देने के लिए" if p in (cur["mahadasha"]["lord"], cur["antardasha"]["lord"]) and p not in dict(needs_support(v)) else "सहारा माँगने वाले ग्रह को स्थिर करने के लिए")
        give_en, _, also_en = gift[0].partition("; ")
        give_hi, _, also_hi = gift[1].partition("; ")
        line = t(f"<strong>{p}</strong> ({why}): mantra \"{m}\" on {day[0]}s; give {give_en}" + (f"; also {also_en}" if also_en else "") + ".",
                 f"<strong>{r.P(p)}</strong> ({why}): {day[1]} को मंत्र \"{m}\" का जाप; {give_hi} का दान" + (f"; साथ में {also_hi}" if also_hi else "") + "।")
        if p in fb and p not in ("Rahu", "Ketu") and p in dict(needs_support(v)):
            line += t(f" Gemstone: {gem[0]} on the {finger[0]}, only after a qualified astrologer confirms it for this chart.",
                      f" रत्न: {gem[1]}, {finger[1]} में — केवल किसी योग्य ज्योतिषी द्वारा इस कुंडली के लिए पुष्टि के बाद।")
        rem.append(line)
    dm = b["day_master"]["element"]
    verdict = b["day_master_strength_heuristic"]["verdict"]
    bal = b["element_balance_visible_8"]
    if "strong" in verdict:
        fav = [PRODUCES[dm], CONTROLS[dm]]
    elif "weak" in verdict:
        fav = [next(k for k, v_ in PRODUCES.items() if v_ == dm), dm]
    else:
        fav = [e for e, k in bal.items() if k == 0][:1] or [min(bal, key=bal.get)]
    rem.append(t("BaZi: bring in " + " and ".join(f"{e} ({ELEMENT_COLOUR[e][0]})" for e in fav) + " through colours, objects and places you choose.",
                 "बाज़ी: " + " और ".join(f"{ELEMENT_HI[e]} ({ELEMENT_COLOUR[e][1]})" for e in fav) + " तत्व को रंगों, वस्तुओं और स्थानों के माध्यम से जीवन में लाएँ।"))
    timed = []
    nxt = None
    for m in v["dashas"]["vimshottari"]["mahadashas"]:
        for a in m.get("antardashas", []):
            if a["start"] == cur["antardasha"]["end"]:
                nxt = (m["lord"], a["lord"], a["start"], a["end"])
    if nxt:
        timed.append(t(f"From {r.month(nxt[2])} the {nxt[0]}–{nxt[1]} period runs to {r.month(nxt[3])}: it brings forward {r.theme(nxt[1])}. Plan for it rather than letting it simply arrive.",
                       f"{r.month(nxt[2])} से {r.P(nxt[0])}–{r.P(nxt[1])} दशा {r.month(nxt[3])} तक चलेगी: यह {r.theme(nxt[1])} को आगे लाती है। इसके लिए पहले से योजना बनाएँ।"))
    for a in fc["areas"]:
        care = next((y for y in a["years"] if y["id"] == a["outlook"]["care"]), None)
        best = next((y for y in a["years"] if y["id"] == a["outlook"]["best"]), None)
        if care:
            timed.append(t(f"{a['title']['en']}: {r.month(care['from'])} to {r.month(care['to'])} needs care. {care['summary']['en']}",
                           f"{a['title']['hi']}: {r.month(care['from'])} से {r.month(care['to'])} सावधानी का समय। {care['summary']['hi']}"))
        elif best and a["key"] in ("work", "marriage"):
            timed.append(t(f"{a['title']['en']}: {r.month(best['from'])} to {r.month(best['to'])} is the strongest year. {best['summary']['en']}",
                           f"{a['title']['hi']}: {r.month(best['from'])} से {r.month(best['to'])} सबसे अच्छा वर्ष। {best['summary']['hi']}"))
    inner = (s_table + f'<h2 class="sub">{t("Traditional remedies", "पारंपरिक उपाय")}</h2>' + bullets(rem)
             + f'<h2 class="sub">{t("Timed, practical steps", "समयबद्ध, व्यावहारिक उपाय")}</h2>' + bullets(timed[:5])
             + (f'<h2 class="sub">{t("Lal Kitab and its remedies", "लाल किताब और उसके उपाय")}</h2>' + detail_html(r, lk) if lk else "")
             + callout(t("A note on clarity", "स्पष्टता संबंधी टिप्पणी"),
                       t("Remedies are optional practices that support attention and steadiness. No remedy can promise a result; "
                         "for health, money or legal matters, consult a qualified professional.",
                         "उपाय वैकल्पिक अभ्यास हैं जो ध्यान और स्थिरता को सहारा देते हैं। कोई भी उपाय निश्चित परिणाम का वचन नहीं देता; "
                         "स्वास्थ्य, धन या क़ानूनी विषयों में किसी योग्य विशेषज्ञ से परामर्श लें।"), orange=True))
    return section(7, t("Doshas and Remedies", "दोष पहचान एवं उपाय &mdash; दोष निवारण"), inner)


def sec8(r, c, ctx, fc):
    t = r.t
    v, n = c["vedic"], c["numerology"]
    pl = v["planets"]
    fn = first_name(ctx["name"])
    strong = [p for p in SEVEN if pl[p].get("dignity") in ("exalted", "own sign", "moolatrikona")]
    lag = v["lagna"]["sign"]
    cur = v["dashas"]["vimshottari"]["current"]
    supp = needs_support(v)
    found = sorted((y for y in v["yoga_library"]["found"] if y.get("report") and y["status"] == "present" and y["tone"] == "supportive"),
                   key=lambda y: y.get("base_rate_present") or 1)
    best_areas = [a for a in fc["areas"] if a["outlook"]["best"]]
    s1 = t(f"{E(fn)}, the four systems together describe someone {SIGN_TRAIT[lag][0]} ({lag} rising)"
           + (f" whose strongest planets are {', '.join(strong)}" if strong else "")
           + (f", with {found[0]['name']} among the rarer yogas" if found else "") + f", and Life Path {n['life_path']['value']}.",
           f"{E(fn)} जी, चारों प्रणालियाँ मिलकर एक {SIGN_TRAIT[lag][1]} व्यक्ति की तस्वीर बनाती हैं ({r.S(lag)} लग्न)"
           + (f", जिनके सबसे बलवान ग्रह {', '.join(r.P(x) for x in strong)} हैं" if strong else "")
           + (f", और दुर्लभ योगों में {r.yoga_name(found[0]['name'])}" if found else "") + f"; जीवन-पथ अंक {n['life_path']['value']}।")
    s2 = t(f"The current chapter is the {cur['mahadasha']['lord']} mahadasha with {cur['antardasha']['lord']} running to {r.month(cur['antardasha']['end'])}: "
           f"a time that brings forward {r.theme(cur['antardasha']['lord'])}.",
           f"वर्तमान अध्याय {r.P(cur['mahadasha']['lord'])} महादशा है, जिसमें {r.P(cur['antardasha']['lord'])} अंतर्दशा {r.month(cur['antardasha']['end'])} तक चलेगी: "
           f"यह समय {r.theme(cur['antardasha']['lord'])} को आगे लाता है।")
    s3 = ""
    if supp:
        p, why = supp[0]
        s3 = t(f"What to watch: {p} ({r.theme(p)}) asks for more conscious effort; recognising the pattern is half the work.",
               f"ध्यान देने योग्य: {r.P(p)} ({r.theme(p)}) अधिक सचेत प्रयास माँगता है; पैटर्न पहचान लेना आधा काम है।")
    todo = []
    care_area = next((a for a in fc["areas"] if a["outlook"]["care"]), None)
    if care_area:
        y = next(y for y in care_area["years"] if y["id"] == care_area["outlook"]["care"])
        todo.append(t(f"From {r.month(y['from'])} to {r.month(y['to'])}, give {care_area['title']['en'].lower()} extra care: {y['summary']['en']}",
                      f"{r.month(y['from'])} से {r.month(y['to'])} में {care_area['title']['hi']} पर विशेष ध्यान दें: {y['summary']['hi']}"))
    if supp:
        p = supp[0][0]
        todo.append(t(f"Take up one steady practice for {p}: the mantra \"{REMEDY[p][0]}\" on {REMEDY[p][1][0]}s, or its charity.",
                      f"{r.P(p)} के लिए एक नियमित अभ्यास अपनाएँ: {REMEDY[p][1][1]} को मंत्र \"{REMEDY[p][0]}\", या इससे जुड़ा दान।"))
    if best_areas:
        a = max(best_areas, key=lambda a: {"mostly_supportive": 3, "gently_supportive": 2, "ups_and_downs": 1}.get(a["outlook"]["class"], 0))
        y = next(y for y in a["years"] if y["id"] == a["outlook"]["best"])
        todo.append(t(f"Use {r.month(y['from'])} to {r.month(y['to'])}, the strongest year for {a['title']['en'].lower()}, for the steps that matter most there.",
                      f"{a['title']['hi']} के लिए सबसे अच्छे वर्ष, {r.month(y['from'])} से {r.month(y['to'])}, का उपयोग वहाँ के सबसे महत्वपूर्ण कदमों के लिए करें।"))
    short = t(f"Your real strength lies in {FAMILY[PLANET_FAMILY[strong[0]]][0] if strong else SIGN_TRAIT[lag][0]}; plan the next three years around the strongest windows and take the slower stretches patiently.",
              f"आपकी असली ताक़त {FAMILY[PLANET_FAMILY[strong[0]]][1] if strong else SIGN_TRAIT[lag][1]} में है; अगले तीन वर्षों की योजना सबसे अच्छी खिड़कियों के आसपास बनाएँ और धीमे समय को धैर्य से लें।")
    inner = (para(s1, s2, s3) + f"<p><strong>{t('If you do only two or three things', 'अगर सिर्फ़ दो-तीन काम करने हों')}</strong></p>" + bullets(todo)
             + callout(t("In short", "संक्षेप में"), short, orange=True)
             + '<hr class="closing-rule">'
             + f'<p class="disclaimer">{t("Disclaimer: this analysis is offered for guidance, reflection and entertainment, based on traditional astrological and numerological systems. It is not a substitute for professional medical, legal, financial or psychological advice. Confirm gemstones and other remedies with a qualified expert before adopting them.", "अस्वीकरण: यह विश्लेषण मार्गदर्शन, चिंतन एवं मनोरंजन हेतु प्रस्तुत किया गया है और पारंपरिक ज्योतिषीय व अंकशास्त्रीय प्रणालियों पर आधारित है। यह किसी पेशेवर चिकित्सीय, क़ानूनी, आर्थिक या मनोवैज्ञानिक सलाह का विकल्प नहीं है। रत्न व अन्य उपाय अपनाने से पहले किसी योग्य विशेषज्ञ से पुष्टि अवश्य करें।")}</p>'
             + f'<div class="closing-brand"><span class="name">{E(ctx["by"])}</span> &nbsp;|&nbsp; <span class="site">{E(ctx["site"])}</span></div>')
    return section(8, t("Final Summary", "अंतिम सारांश"), inner, tinted=True)


def detail_html(r, sec, num=None, title=None):
    """One app_details section as report HTML (subsection heading, intro, tables, paragraphs, lists, note)."""
    k = r.lang_key()
    out = [sub(num, title or sec["title"][k]) if num else ""]
    if sec.get("intro"):
        out.append(f'<p class="guidance">{E(sec["intro"][k])}</p>')
    for b in sec["blocks"]:
        if b["type"] == "table":
            out.append(table([E(h[k]) for h in b["head"]], [[E(c[k]) for c in row] for row in b["rows"]]))
        elif b["type"] == "para":
            out.append(f"<p>{E(b['text'][k])}</p>")
        else:
            out.append(bullets([E(i[k]) for i in b["items"]]))
    if sec.get("note") and sec["note"][k]:
        out.append(f'<p class="guidance">{E(sec["note"][k])}</p>')
    return "".join(out)


def initials(s):
    w = [x for x in (s or "").split() if x]
    return (w[0][0] + (w[-1][0] if len(w) > 1 else "")).upper() if w else "X"


def build(c, fc, req, lang="en", by="Gaurav Mishra", site="authorgaurav.com"):
    """c: chart with forecast layers; fc: app_forecast.build output; req: the chart request (name, date, time, place, tz, gender)."""
    r = R(lang == "hi")
    t = r.t
    now = c["meta"]["generated_for_date"]
    ctx = {"name": req["name"], "date": req["date"], "time": req["time"], "tz": req["tz"], "place": req.get("place", ""),
           "lat": float(req["lat"]), "lon": float(req["lon"]), "gender": req.get("gender", "M"), "now": now,
           "age": age_on(req["date"], now), "by": by, "site": site, "residence": req.get("residence", ""),
           "ref": f"{initials(by)}/{now[:4]}/{initials(req['name'])}-{req['date'][:4]}"}
    F = c.get("forecast")
    ctx["details"] = c.get("details") or AD.build(c)
    nav = [(1, t("Birth details", "जन्म विवरण")), (2, t("Vedic", "वैदिक")), (3, t("Western", "पाश्चात्य")), (4, t("BaZi", "बाज़ी")),
           (5, t("Numerology", "अंकशास्त्र")), (6, t("Comparison", "तुलना")), (7, t("Remedies", "उपाय")), (8, t("Summary", "सारांश"))]
    title = (f"{E(ctx['name'])} — " + t("Astrological and Numerological Life Analysis", "ज्योतिषीय एवं अंकशास्त्रीय जीवन विश्लेषण"))
    body = (cover(r, ctx) + sec1(r, c, ctx) + sec2(r, c, ctx) + sec3(r, c, ctx) + sec4(r, c, ctx, F) + sec5(r, c, ctx)
            + sec6(r, c, ctx, fc) + sec7(r, c, ctx, fc) + sec8(r, c, ctx, fc))
    return f"""<!DOCTYPE html>
<html lang="{'hi' if r.hi else 'en'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><style>{CSS}</style></head>
<body>
<div id="progress"></div>
<div id="topbar">
  <div class="brand">{E(by)}<span class="site">&nbsp;·&nbsp;{E(site)}</span></div>
  <nav>{"".join(f'<a href="#sec{i}">{i} · {lab}</a>' for i, lab in nav)}</nav>
</div>
{body}
<script>{JS}</script>
</body></html>"""
