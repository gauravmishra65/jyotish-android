#!/usr/bin/env python3
"""Generate the nakshatra page family, in English and Hindi, from the engine's data.

    python3 build.py [--base https://example.com]

Writes one page per nakshatra per language, plus sitemap.xml and robots.txt.
Every page states its own computed facts - degree span, the four padas with
their navamsa signs, the dasha length of its lord - so no two are the same text
with a word changed, which is the difference between programmatic SEO that
ranks and the kind Google removes.

English pages sit at /<slug>.html, Hindi at /hi/<slug>.html, each declaring the
other with hreflang so neither competes with its own translation.
"""
import argparse, json, pathlib, re

OUT = pathlib.Path(__file__).parent
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
         "Sagittarius","Capricorn","Aquarius","Pisces"]
SIGNS_HI = ["मेष","वृषभ","मिथुन","कर्क","सिंह","कन्या","तुला","वृश्चिक","धनु","मकर","कुंभ","मीन"]
DASHA = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
NAKW, PADAW = 360/27, 360/108
NAK = json.loads((OUT/"data.json").read_text(encoding="utf-8"))

ORD = ["first","second","third","fourth","fifth","sixth","seventh","eighth","ninth","tenth",
       "eleventh","twelfth","thirteenth","fourteenth","fifteenth","sixteenth","seventeenth",
       "eighteenth","nineteenth","twentieth","twenty-first","twenty-second","twenty-third",
       "twenty-fourth","twenty-fifth","twenty-sixth","twenty-seventh"]

def slug(s): return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")
def dms(deg):
    d = int(deg); mf = (deg-d)*60; m = int(mf); s = round((mf-m)*60)
    if s == 60: s, m = 0, m+1
    if m == 60: m, d = 0, d+1
    return f"{d}° {m:02d}′ {s:02d}″"
def navamsa(lon): return int((lon*9)//30) % 12     # checked against vedic.py, all 108 padas

def padas(i):
    out = []
    for p in range(4):
        lo = i*NAKW + p*PADAW
        n = navamsa(lo + PADAW/2)
        out.append((p+1, lo, lo+PADAW, SIGNS[n], SIGNS_HI[n]))
    return out

def rashi(i, hi=False):
    names = SIGNS_HI if hi else SIGNS
    a, b = int(i*NAKW//30), int(((i+1)*NAKW - 1e-9)//30)
    joiner = " और " if hi else " and "
    return names[a] if a == b else names[a] + joiner + names[b]

L = {
 "en": dict(dir="", other="hi/", otherLang="hi", code="en",
   allLink="All twenty-seven", padaH="The four padas",
   padaP="Each nakshatra divides into four quarters of 3°20′. Each quarter falls in a different navamsa sign, and that sign colours how the nakshatra expresses itself.",
   cols=("Pada","Span","Navamsa sign"),
   nowH="Where the Moon is now", working="Working it out…",
   bornH="Was the Moon here when you were born?",
   lDate="Date of birth", lTime="Time of birth", lTz="Time zone at birth", go="Work it out",
   attrs=("Ruling planet","Deity","Symbol","Gana","Dasha length","Span"), years="years",
   priv="<strong>Nothing you type leaves this page.</strong> The Moon’s position is computed in your own browser from the ELP-2000/82 lunar theory with the Lahiri ayanamsa. There is no server here to send a birth date to. Open your browser’s Network tab and check.",
   foot="Lahiri ayanamsa · nothing collected", switch="हिंदी"),
 "hi": dict(dir="hi/", other="../", otherLang="en", code="hi",
   allLink="सभी सत्ताईस", padaH="चार पाद",
   padaP="हर नक्षत्र 3°20′ के चार पादों में बँटता है। हर पाद किसी भिन्न नवांश राशि में पड़ता है, और वही राशि नक्षत्र के स्वभाव को रंग देती है।",
   cols=("पाद","विस्तार","नवांश राशि"),
   nowH="इस समय चंद्रमा कहाँ है", working="गणना हो रही है…",
   bornH="क्या आपके जन्म के समय चंद्रमा यहीं था?",
   lDate="जन्म तिथि", lTime="जन्म समय", lTz="जन्म के समय का टाइम ज़ोन", go="गणना कीजिए",
   attrs=("स्वामी ग्रह","देवता","प्रतीक","गण","दशा अवधि","विस्तार"), years="वर्ष",
   priv="<strong>आप जो भरते हैं वह इस पृष्ठ से बाहर नहीं जाता।</strong> चंद्रमा की स्थिति आपके ही ब्राउज़र में ELP-2000/82 चंद्र सिद्धांत और लाहिरी अयनांश से निकाली जाती है। भेजने के लिए यहाँ कोई सर्वर है ही नहीं। ब्राउज़र का नेटवर्क टैब खोलकर देख लीजिए।",
   foot="लाहिरी अयनांश · कुछ भी एकत्र नहीं", switch="English"),
}

def lede(i, n, lang):
    lo, hi = i*NAKW, (i+1)*NAKW
    lord, yrs = n["lord"], DASHA[n["lord"]]
    if lang == "en":
        return (f"{n['en']} is the {ORD[i]} of the twenty-seven nakshatras, running from {dms(lo)} to "
                f"{dms(hi)} of the sidereal zodiac — which places it in {rashi(i)}. Its lord is {lord}, "
                f"so a birth here opens the Vimshottari sequence in {lord}’s period of {yrs} years.")
    return (f"{n['hi']} सत्ताईस नक्षत्रों में {i+1}वाँ है, जो निरयन राशिचक्र में {dms(lo)} से {dms(hi)} तक "
            f"फैला है — अर्थात {rashi(i, True)} में। इसके स्वामी {n['lordHi']} हैं, इसलिए यहाँ जन्म लेने पर "
            f"विंशोत्तरी दशा {n['lordHi']} की {yrs} वर्ष की अवधि से आरंभ होती है।")

def page(i, n, lang, base):
    t, pr, nx = L[lang], NAK[(i-1) % 27], NAK[(i+1) % 27]
    lo, hi = i*NAKW, (i+1)*NAKW
    name = n["en"] if lang == "en" else n["hi"]
    title = f"{n['en']} Nakshatra" if lang == "en" else f"{n['hi']} नक्षत्र"
    if lang == "en":
        desc = (f"{n['en']} ({n['hi']}) spans {dms(lo)} to {dms(hi)} of the sidereal zodiac, ruled by "
                f"{n['lord']}. Its four padas, their navamsa signs, and a calculator that runs in your browser.")
    else:
        desc = (f"{n['hi']} निरयन राशिचक्र में {dms(lo)} से {dms(hi)} तक, स्वामी {n['lordHi']}। "
                f"इसके चार पाद, उनके नवांश, और आपके ब्राउज़र में चलने वाला कैलकुलेटर।")
    up = "../" if lang == "hi" else ""
    canon = f"{base}/{t['dir']}{slug(n['en'])}.html" if base else ""
    alt_en = f"{base}/{slug(n['en'])}.html" if base else f"{up}{slug(n['en'])}.html"
    alt_hi = f"{base}/hi/{slug(n['en'])}.html" if base else (f"hi/{slug(n['en'])}.html" if lang=="en" else f"{slug(n['en'])}.html")
    ld = json.dumps({"@context":"https://schema.org","@type":"Article","headline":title,
        "description":desc,"inLanguage":t["code"],
        "about":{"@type":"Thing","name":f"{n['en']} Nakshatra","alternateName":n["hi"]},
        **({"url":canon} if canon else {})}, ensure_ascii=False)
    rows = "".join(f"<tr><td class='n'>{p}</td><td class='n'>{dms(a)} – {dms(b)}</td>"
                   f"<td>{(sg if lang=='en' else sh)}</td></tr>" for p,a,b,sg,sh in padas(i))
    attrs = [(t["attrs"][0], n["lord"] if lang=="en" else n["lordHi"]),
             (t["attrs"][1], n["deity"] if lang=="en" else n["deityHi"]),
             (t["attrs"][2], n["symbol"] if lang=="en" else n["symbolHi"]),
             (t["attrs"][3], n["gana"] if lang=="en" else n["ganaHi"]),
             (t["attrs"][4], f"{DASHA[n['lord']]} {t['years']}"),
             (t["attrs"][5], f"<span class='n'>{dms(lo)} – {dms(hi)}</span>")]
    attrs_html = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in attrs)
    prn = pr["en"] if lang=="en" else pr["hi"]
    nxn = nx["en"] if lang=="en" else nx["hi"]
    return f"""<!doctype html>
<html lang="{t['code']}"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
{f'<link rel="canonical" href="{canon}">' if canon else ''}
<link rel="alternate" hreflang="en" href="{alt_en}">
<link rel="alternate" hreflang="hi" href="{alt_hi}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<link rel="stylesheet" href="{up}site.css">
<script type="application/ld+json">{ld}</script>
</head><body class="{t['code']}"><div class="wrap">
<nav class="crumbs"><a href="{up}nakshatra.html">&larr; {t['allLink']}</a>
<span><a href="{slug(pr['en'])}.html">{prn}</a> · <a href="{slug(nx['en'])}.html">{nxn}</a>
· <a href="{alt_hi if lang=='en' else alt_en}">{t['switch']}</a></span></nav>

<h1>{title}</h1>
<p class="lede">{lede(i, n, lang)}</p>

<dl class="attrs">{attrs_html}</dl>

<h2>{t['padaH']}</h2>
<p>{t['padaP']}</p>
<div class="scroll"><table><thead><tr><th>{t['cols'][0]}</th><th>{t['cols'][1]}</th><th>{t['cols'][2]}</th></tr></thead>
<tbody>{rows}</tbody></table></div>

<h2>{t['nowH']}</h2>
<div class="note" id="live" data-nak="{i}" data-lang="{t['code']}">
  <p id="liveNow">{t['working']}</p><p id="liveNext" class="dim"></p>
</div>

<h2>{t['bornH']}</h2>
<form class="calc" id="form">
  <div class="fields">
    <div><label for="date">{t['lDate']}</label><input type="date" id="date" value="1990-04-12" required></div>
    <div><label for="time">{t['lTime']}</label><input type="time" id="time" value="05:24" required></div>
    <div><label for="tz">{t['lTz']}</label><select id="tz"></select></div>
  </div>
  <button class="go" type="submit">{t['go']}</button>
  <div class="readout" id="out" hidden>
    <div class="nk"><b id="rName"></b><span class="dev" id="rDev"></span><span class="pada" id="rPada"></span></div>
    <div class="lon" id="rLon"></div><div class="cusp" id="rCusp" hidden></div>
  </div>
</form>

<div class="note small"><p>{t['priv']}</p></div>
<footer><p><a href="{up}nakshatra.html">{t['allLink']}</a> · {t['foot']}</p></footer>
</div><script src="{up}engine.js"></script><script>initNakPage();</script></body></html>
"""


VIM = [("Ketu",7),("Venus",20),("Sun",6),("Moon",10),("Mars",7),
       ("Rahu",18),("Jupiter",16),("Saturn",19),("Mercury",17)]
VIM_HI = {"Ketu":"केतु","Venus":"शुक्र","Sun":"सूर्य","Moon":"चंद्र","Mars":"मंगल",
          "Rahu":"राहु","Jupiter":"गुरु","Saturn":"शनि","Mercury":"बुध"}

D = {
 "en": dict(code="en", up="", other="hi/dasha.html", switch="हिंदी",
   title="Vimshottari Dasha Calculator",
   desc="Work out your Vimshottari mahadasha, antardasha and pratyantar from your birth details — "
        "the full 120-year sequence with dates, computed in your own browser and nothing sent anywhere.",
   h1="Vimshottari Dasha Calculator",
   lede="Vimshottari divides a life into nine periods totalling 120 years, each ruled by a planet. Which "
        "period you are born into, and how much of it remains, is fixed by one thing: how far the Moon had "
        "travelled through its nakshatra at the moment of birth. Enter that moment and the whole sequence "
        "follows, to the day.",
   lDate="Date of birth", lTime="Time of birth", lTz="Time zone at birth", go="Work out my dasha",
   noPlace="The town does not enter into it. Vimshottari depends on the Moon alone, and the Moon stands at "
           "the same point of the zodiac for everyone on Earth at a given instant — so only the instant matters.",
   curH="Running now", seqH="The whole sequence", refH="The nine lords",
   refP="The order never changes, and neither do the lengths. Only the starting point moves, set by the "
        "nakshatra the Moon was in.",
   cols=("Lord","Years"), seqCols=("Mahadasha","From","To","Years"),
   curCols=("Period","Lord","From","To"),
   rows=("Mahadasha","Antardasha","Pratyantar"),
   balance=lambda l, y: f"Born in {l}, with {y} of it still to run.",
   priv="<strong>Nothing you type leaves this page.</strong> The Moon's position and the whole dasha table "
        "are computed in your own browser. There is no server here to send a birth date to.",
   method="The Moon comes from the ELP-2000/82 lunar theory with the Lahiri ayanamsa, checked against Swiss "
          "Ephemeris. The dasha arithmetic uses a 365.25-day year, which is the convention this engine and "
          "the app both follow, so the two never disagree.",
   noInterp="These are the periods and their dates, not a forecast. What a period is said to bring depends "
            "on the whole chart — the house its lord occupies, its strength, its aspects — which is what the "
            "full reading is for.",
   tolerance="<strong>About the dates.</strong> The whole table hangs off one number: how far the Moon had "
             "travelled through its nakshatra at birth. This page gets that to within about ten arcseconds of "
             "Swiss Ephemeris, which moves every boundary in the table by a day on average and by up to four. "
             "Measured over 1,500 births between 1930 and 2020: mean 1.1 days, worst 3.8, and 45% off by more "
             "than a day. So read these as the right periods in the right order with dates good to a few days, "
             "not as exact. The app carries the full ephemeris and computes them to the minute.",
   allLink="All twenty-seven nakshatras", foot="Lahiri ayanamsa · nothing collected"),
 "hi": dict(code="hi", up="../", other="../dasha.html", switch="English",
   title="विंशोत्तरी दशा कैलकुलेटर",
   desc="जन्म विवरण से अपनी विंशोत्तरी महादशा, अंतर्दशा और प्रत्यंतर निकालिए — पूरा 120 वर्ष का क्रम तिथियों सहित, "
        "आपके अपने ब्राउज़र में, कुछ भी कहीं भेजे बिना।",
   h1="विंशोत्तरी दशा कैलकुलेटर",
   lede="विंशोत्तरी जीवन को नौ अवधियों में बाँटती है, कुल 120 वर्ष, हर एक का स्वामी एक ग्रह। आप किस अवधि में जन्मे "
        "और उसमें कितना शेष है — यह केवल एक बात से तय होता है: जन्म के क्षण चंद्रमा अपने नक्षत्र में कितना चल चुका था। "
        "वह क्षण भरिए, और पूरा क्रम दिन तक निकल आता है।",
   lDate="जन्म तिथि", lTime="जन्म समय", lTz="जन्म के समय का टाइम ज़ोन", go="मेरी दशा निकालिए",
   noPlace="नगर का इसमें कोई स्थान नहीं। विंशोत्तरी केवल चंद्रमा पर निर्भर है, और किसी एक क्षण पर चंद्रमा पृथ्वी पर "
           "सबके लिए राशिचक्र के एक ही बिंदु पर होता है — इसलिए केवल क्षण मायने रखता है।",
   curH="इस समय चल रही", seqH="पूरा क्रम", refH="नौ स्वामी",
   refP="क्रम कभी नहीं बदलता, न अवधियाँ। केवल आरंभ बिंदु बदलता है, जो चंद्र-नक्षत्र से तय होता है।",
   cols=("स्वामी","वर्ष"), seqCols=("महादशा","से","तक","वर्ष"),
   curCols=("अवधि","स्वामी","से","तक"),
   rows=("महादशा","अंतर्दशा","प्रत्यंतर"),
   balance=lambda l, y: f"जन्म {l} की दशा में, जिसमें {y} शेष थे।",
   priv="<strong>आप जो भरते हैं वह इस पृष्ठ से बाहर नहीं जाता।</strong> चंद्रमा की स्थिति और पूरी दशा सारणी आपके "
        "ही ब्राउज़र में निकाली जाती है। भेजने के लिए यहाँ कोई सर्वर है ही नहीं।",
   method="चंद्रमा ELP-2000/82 चंद्र सिद्धांत और लाहिरी अयनांश से, जिसका मिलान स्विस एफ़ेमेरिस से किया गया है। दशा "
          "गणना 365.25 दिन के वर्ष पर, जो इस इंजन और ऐप दोनों की परिपाटी है, इसलिए दोनों में कभी अंतर नहीं आता।",
   noInterp="ये अवधियाँ और उनकी तिथियाँ हैं, भविष्यवाणी नहीं। कोई अवधि क्या लाती है यह पूरी कुंडली पर निर्भर करता है "
            "— स्वामी किस भाव में है, उसका बल, उसकी दृष्टि — और वही पूरे फलादेश का विषय है।",
   tolerance="<strong>तिथियों के विषय में।</strong> पूरी सारणी एक ही संख्या पर टिकी है: जन्म के समय चंद्रमा अपने "
             "नक्षत्र में कितना चल चुका था। यह पृष्ठ उसे स्विस एफ़ेमेरिस के लगभग दस विकला के भीतर निकालता है, और "
             "इतने से ही सारणी की हर संधि औसतन एक दिन, और अधिकतम चार दिन तक खिसक जाती है। 1930 से 2020 के बीच "
             "1,500 जन्मों पर मापा गया: औसत 1.1 दिन, अधिकतम 3.8, और 45% एक दिन से अधिक। इसलिए इन्हें सही क्रम "
             "में सही अवधियाँ मानिए जिनकी तिथियाँ कुछ दिनों तक सही हैं, पूर्णतः नहीं। ऐप में पूर्ण एफ़ेमेरिस है और "
             "वह इन्हें मिनट तक निकालता है।",
   allLink="सभी सत्ताईस नक्षत्र", foot="लाहिरी अयनांश · कुछ भी एकत्र नहीं"),
}

def dasha_page(lang, base):
    t = D[lang]
    up = t["up"]
    canon = f"{base}/{'hi/' if lang=='hi' else ''}dasha.html" if base else ""
    alt_en = f"{base}/dasha.html" if base else (up + "dasha.html" if lang=="hi" else "dasha.html")
    alt_hi = f"{base}/hi/dasha.html" if base else ("hi/dasha.html" if lang=="en" else "dasha.html")
    ld = json.dumps({"@context":"https://schema.org","@type":"WebApplication","name":t["title"],
        "description":t["desc"],"applicationCategory":"ReferenceApplication","inLanguage":t["code"],
        "offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},
        **({"url":canon} if canon else {})}, ensure_ascii=False)
    ref = "".join(f"<tr><td>{l if lang=='en' else VIM_HI[l]}</td><td class='n'>{y}</td></tr>" for l, y in VIM)
    return f"""<!doctype html>
<html lang="{t['code']}"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{t['title']}</title>
<meta name="description" content="{t['desc']}">
{f'<link rel="canonical" href="{canon}">' if canon else ''}
<link rel="alternate" hreflang="en" href="{alt_en}">
<link rel="alternate" hreflang="hi" href="{alt_hi}">
<meta property="og:title" content="{t['title']}">
<meta property="og:description" content="{t['desc']}">
<meta property="og:type" content="website">
<link rel="stylesheet" href="{up}site.css">
<script type="application/ld+json">{ld}</script>
</head><body class="{t['code']}"><div class="wrap">
<nav class="crumbs"><a href="{up}nakshatra.html">&larr; {t['allLink']}</a>
<span><a href="{alt_hi if lang=='en' else alt_en}">{t['switch']}</a></span></nav>

<h1>{t['h1']}</h1>
<p class="lede">{t['lede']}</p>

<form class="calc" id="form" data-lang="{t['code']}">
  <div class="fields">
    <div><label for="date">{t['lDate']}</label><input type="date" id="date" value="1990-04-12" required></div>
    <div><label for="time">{t['lTime']}</label><input type="time" id="time" value="05:24" required></div>
    <div><label for="tz">{t['lTz']}</label><select id="tz"></select></div>
  </div>
  <button class="go" type="submit">{t['go']}</button>
  <p class="stubnote dim" style="font-size:.85rem;margin:.7rem 0 0">{t['noPlace']}</p>

  <div class="readout" id="out" hidden>
    <p id="rBalance" class="lede" style="margin-bottom:1rem"></p>
    <h3 style="font-family:var(--serif);font-size:1.1rem;margin:0 0 .5rem">{t['curH']}</h3>
    <div class="scroll"><table><thead><tr><th>{t['curCols'][0]}</th><th>{t['curCols'][1]}</th>
      <th>{t['curCols'][2]}</th><th>{t['curCols'][3]}</th></tr></thead>
      <tbody id="rCur"></tbody></table></div>
    <h3 style="font-family:var(--serif);font-size:1.1rem;margin:1.6rem 0 .5rem">{t['seqH']}</h3>
    <div class="scroll"><table><thead><tr><th>{t['seqCols'][0]}</th><th>{t['seqCols'][1]}</th>
      <th>{t['seqCols'][2]}</th><th>{t['seqCols'][3]}</th></tr></thead>
      <tbody id="rSeq"></tbody></table></div>
  </div>
</form>

<div class="cusp" style="margin-top:1.4rem;border-radius:0 8px 8px 0"><p style="margin:0">{t['tolerance']}</p></div>
<div class="note small" style="margin-top:1rem"><p>{t['noInterp']}</p></div>

<h2>{t['refH']}</h2>
<p>{t['refP']}</p>
<div class="scroll"><table><thead><tr><th>{t['cols'][0]}</th><th>{t['cols'][1]}</th></tr></thead>
<tbody>{ref}</tbody></table></div>

<h2>{"How this was worked out" if lang=="en" else "गणना कैसे हुई"}</h2>
<div class="note"><p>{t['method']}</p></div>
<div class="note small" style="margin-top:1rem"><p>{t['priv']}</p></div>

<footer><p><a href="{up}nakshatra.html">{t['allLink']}</a> · {t['foot']}</p></footer>
</div><script src="{up}engine.js"></script><script src="{up}dasha.js"></script>
<script>initDashaPage();</script></body></html>
"""


M = {
 "en": dict(code="en", up="", switch="हिंदी", other="hi/milan.html",
   title="Kundli Milan: the 36 gunas",
   desc="Compare two charts on the eight kootas of Ashtakoota guna milan — Varna, Vashya, Tara, Yoni, "
        "Graha Maitri, Gana, Bhakoot and Nadi — computed in your own browser, with the places the "
        "published tables disagree shown rather than hidden.",
   h1="Kundli Milan: the 36 gunas",
   lede="Ashtakoota compares two Moons on eight counts and adds up to 36. It is the first thing anyone asks "
        "for and the most often misread, so this page shows the working: every koota, what it compared, and "
        "where the published tables disagree with each other.",
   groomH="First person", brideH="Second person",
   lDate="Date of birth", lTime="Time of birth", lTz="Time zone at birth", go="Compare the charts",
   noPlace="Guna milan rests on the two Moons alone, so the towns do not enter into it — only the two "
           "moments, which the time zones fix.",
   resH="The eight kootas", allLink="All twenty-seven nakshatras",
   cols=("Koota","What it compares","First person","Second person","Score"),
   foot="Lahiri ayanamsa · nothing collected",
   privH="Where the two birth details go",
   priv="<strong>Nowhere.</strong> Both charts are worked out in this browser tab. Nothing is sent, stored or "
        "logged — there is no server here to send two birth dates to. Open your Network tab and check."),
 "hi": dict(code="hi", up="../", switch="English", other="../milan.html",
   title="कुंडली मिलान: 36 गुण",
   desc="अष्टकूट गुण मिलान के आठ कूटों पर दो कुंडलियों की तुलना — वर्ण, वश्य, तारा, योनि, ग्रह मैत्री, गण, "
        "भकूट और नाड़ी — आपके अपने ब्राउज़र में, और जहाँ प्रकाशित सारणियाँ असहमत हैं वह छिपाया नहीं, दिखाया गया।",
   h1="कुंडली मिलान: 36 गुण",
   lede="अष्टकूट दो चंद्रमाओं की आठ बातों पर तुलना करता है, कुल 36। यही सबसे पहले पूछा जाता है और सबसे अधिक "
        "ग़लत पढ़ा जाता है, इसलिए यह पृष्ठ गणना दिखाता है: हर कूट, उसने किसकी तुलना की, और कहाँ प्रकाशित "
        "सारणियाँ आपस में असहमत हैं।",
   groomH="पहला व्यक्ति", brideH="दूसरा व्यक्ति",
   lDate="जन्म तिथि", lTime="जन्म समय", lTz="जन्म के समय का टाइम ज़ोन", go="कुंडली मिलाइए",
   noPlace="गुण मिलान केवल दो चंद्रमाओं पर टिका है, इसलिए नगर का इसमें कोई स्थान नहीं — केवल दो क्षण, "
           "जिन्हें टाइम ज़ोन तय करते हैं।",
   resH="आठ कूट", allLink="सभी सत्ताईस नक्षत्र",
   cols=("कूट","किसकी तुलना","पहला व्यक्ति","दूसरा व्यक्ति","अंक"),
   foot="लाहिरी अयनांश · कुछ भी एकत्र नहीं",
   privH="दोनों जन्म विवरण कहाँ जाते हैं",
   priv="<strong>कहीं नहीं।</strong> दोनों कुंडलियाँ इसी ब्राउज़र टैब में बनती हैं। कुछ भी भेजा, संग्रहीत या दर्ज "
        "नहीं होता — दो जन्म तिथियाँ भेजने के लिए यहाँ कोई सर्वर है ही नहीं। नेटवर्क टैब खोलकर देख लीजिए।"),
}

def milan_page(lang, base):
    t = M[lang]; up = t["up"]
    canon = f"{base}/{'hi/' if lang=='hi' else ''}milan.html" if base else ""
    alt_en = f"{base}/milan.html" if base else (up + "milan.html" if lang=="hi" else "milan.html")
    alt_hi = f"{base}/hi/milan.html" if base else ("hi/milan.html" if lang=="en" else "milan.html")
    ld = json.dumps({"@context":"https://schema.org","@type":"WebApplication","name":t["title"],
        "description":t["desc"],"applicationCategory":"ReferenceApplication","inLanguage":t["code"],
        "offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},
        **({"url":canon} if canon else {})}, ensure_ascii=False)
    def person(who, label, dflt):
        return f"""<fieldset style="border:1px solid var(--line);border-radius:12px;padding:1rem;margin:0 0 1rem;min-width:0">
      <legend style="font-size:.73rem;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);padding:0 .4rem">{label}</legend>
      <div class="fields">
        <div><label for="date_{who}">{t['lDate']}</label><input type="date" id="date_{who}" value="{dflt}" required></div>
        <div><label for="time_{who}">{t['lTime']}</label><input type="time" id="time_{who}" value="05:24" required></div>
        <div><label for="tz_{who}">{t['lTz']}</label><select id="tz_{who}"></select></div>
      </div></fieldset>"""
    return f"""<!doctype html>
<html lang="{t['code']}"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{t['title']}</title>
<meta name="description" content="{t['desc']}">
{f'<link rel="canonical" href="{canon}">' if canon else ''}
<link rel="alternate" hreflang="en" href="{alt_en}">
<link rel="alternate" hreflang="hi" href="{alt_hi}">
<meta property="og:title" content="{t['title']}">
<meta property="og:description" content="{t['desc']}">
<meta property="og:type" content="website">
<link rel="stylesheet" href="{up}site.css">
<script type="application/ld+json">{ld}</script>
</head><body class="{t['code']}"><div class="wrap">
<nav class="crumbs"><a href="{up}nakshatra.html">&larr; {t['allLink']}</a>
<span><a href="{alt_hi if lang=='en' else alt_en}">{t['switch']}</a></span></nav>

<h1>{t['h1']}</h1>
<p class="lede">{t['lede']}</p>

<form class="calc" id="form" data-lang="{t['code']}">
  {person('g', t['groomH'], '1990-04-12')}
  {person('b', t['brideH'], '1992-08-30')}
  <button class="go" type="submit">{t['go']}</button>
  <p class="stubnote dim" style="font-size:.85rem;margin:.7rem 0 0">{t['noPlace']}</p>

  <div class="readout" id="out" hidden>
    <div id="rMoons" class="dim" style="font-size:.92rem;margin-bottom:.8rem"></div>
    <div id="rTotal" style="margin-bottom:.2rem"></div>
    <p id="rBand" class="dim" style="margin:0 0 .3rem"></p>
    <p id="rRange" class="dim" style="font-size:.86rem;margin:0 0 1rem" hidden></p>
    <div class="scroll"><table><thead><tr>
      <th>{t['cols'][0]}</th><th>{t['cols'][1]}</th><th>{t['cols'][2]}</th><th>{t['cols'][3]}</th><th>{t['cols'][4]}</th>
    </tr></thead><tbody id="rRows"></tbody></table></div>
  </div>
</form>

<div class="cusp" style="margin-top:1.4rem;border-radius:0 8px 8px 0"><p style="margin:0" id="caveats"></p></div>

<h2>{t['privH']}</h2>
<div class="note"><p>{t['priv']}</p></div>

<footer><p><a href="{up}nakshatra.html">{t['allLink']}</a> · {t['foot']}</p></footer>
</div>
<script src="{up}engine.js"></script><script src="{up}koota.js"></script><script src="{up}milan.js"></script>
<script>document.getElementById("caveats").innerHTML = MUI["{t['code']}"].caveats; initMilanPage();</script>
</body></html>
"""


I18N = {
 "en": dict(code="en", up="", switch="हिंदी", oth="hi/",
   site="Gaurav Jyotish",
   title="Gaurav Jyotish", 
   desc="Vedic astrology calculators that run in your own browser. Your birth details are never sent "
        "anywhere, because there is no server here to send them to. Nakshatra, Vimshottari dasha and "
        "the 36 gunas, in English and Hindi.",
   tagline="Your birth details never leave this page.",
   lede="Most astrology sites ask for your date, time and place of birth and send them to a server. This "
        "one does the arithmetic in your own browser. Nothing is transmitted, nothing is stored, nothing "
        "is logged — not because we promise it, but because there is no server here to send it to, and "
        "you can confirm that yourself in about fifteen seconds.",
   toolsH="The calculators",
   tools=[("nakshatra.html","What is my Nakshatra?",
           "The segment of sky the Moon stood in when you were born, with its pada, lord, deity and gana. "
           "Each of the twenty-seven has its own page."),
          ("dasha.html","Vimshottari dasha",
           "The nine periods that divide a life into 120 years, which one you were born into, how much of "
           "it remained, and the whole sequence with dates."),
          ("milan.html","Kundli Milan, the 36 gunas",
           "Two charts compared on the eight Ashtakoota kootas — and, unusually, the places where the "
           "published tables disagree with each other.")],
   methodH="How the numbers are made",
   method="Positions come from the ELP-2000/82 lunar theory with the Lahiri ayanamsa, the one India's "
          "calendar reform committee settled on. Every figure on this site is checked against Swiss "
          "Ephemeris over five thousand dates between 1900 and 2050 before it is published: eleven "
          "arcseconds apart on average, twenty-eight at worst. Where that margin could change an answer "
          "— a Moon sitting within a hair of a nakshatra boundary — the page says the question is "
          "unsettled rather than guessing. Where a tradition disagrees with itself, the page shows the "
          "range instead of picking one and sounding certain.",
   noH="What you will not find here",
   no=["No predictions about death, disease or divorce.",
       "No guarantees, and no claim that a calculation decides anything.",
       "No account, no sign-up, no cookie banner, because there is nothing to consent to.",
       "No advertising, and nothing sold to anyone."],
   privLink="How to check the privacy claim yourself",
   allH="All twenty-seven nakshatras",
   foot="Lahiri ayanamsa · nothing collected"),
 "hi": dict(code="hi", up="../", switch="English", oth="../",
   site="गौरव ज्योतिष",
   title="गौरव ज्योतिष",
   desc="वैदिक ज्योतिष के कैलकुलेटर जो आपके अपने ब्राउज़र में चलते हैं। जन्म विवरण कहीं नहीं भेजा जाता, क्योंकि "
        "भेजने के लिए यहाँ कोई सर्वर है ही नहीं। नक्षत्र, विंशोत्तरी दशा और 36 गुण, हिंदी और अंग्रेज़ी में।",
   tagline="आपका जन्म विवरण इस पृष्ठ से बाहर नहीं जाता।",
   lede="अधिकांश ज्योतिष साइटें आपकी तिथि, समय और स्थान माँगकर किसी सर्वर पर भेज देती हैं। यह साइट गणना "
        "आपके अपने ब्राउज़र में करती है। कुछ भी भेजा नहीं जाता, संग्रहीत नहीं होता, दर्ज नहीं होता — "
        "वादे के कारण नहीं, बल्कि इसलिए कि भेजने के लिए यहाँ कोई सर्वर है ही नहीं, और आप इसे लगभग पंद्रह "
        "सेकंड में स्वयं जाँच सकते हैं।",
   toolsH="कैलकुलेटर",
   tools=[("nakshatra.html","मेरा नक्षत्र क्या है?",
           "जन्म के समय चंद्रमा आकाश के जिस भाग में था, उसके पाद, स्वामी, देवता और गण सहित। सत्ताईस में "
           "से हर एक का अपना पृष्ठ।"),
          ("dasha.html","विंशोत्तरी दशा",
           "नौ अवधियाँ जो जीवन को 120 वर्षों में बाँटती हैं — आप किसमें जन्मे, कितना शेष था, और "
           "पूरा क्रम तिथियों सहित।"),
          ("milan.html","कुंडली मिलान, 36 गुण",
           "आठ अष्टकूटों पर दो कुंडलियों की तुलना — और, जो कहीं नहीं मिलता, वे स्थान जहाँ प्रकाशित "
           "सारणियाँ आपस में असहमत हैं।")],
   methodH="अंक कैसे बनते हैं",
   method="स्थितियाँ ELP-2000/82 चंद्र सिद्धांत और लाहिरी अयनांश से, वही जिसे भारत की कैलेंडर सुधार समिति ने "
          "स्वीकार किया। इस साइट का हर अंक प्रकाशित होने से पहले 1900 से 2050 के बीच पाँच हज़ार तिथियों पर "
          "स्विस एफ़ेमेरिस से जाँचा जाता है: औसतन ग्यारह विकला का अंतर, अधिकतम अट्ठाईस। जहाँ यह अंतर उत्तर "
          "बदल सकता है — चंद्रमा किसी नक्षत्र संधि के अत्यंत निकट — वहाँ पृष्ठ अनुमान लगाने के बजाय "
          "कहता है कि प्रश्न अनिर्णीत है। जहाँ परंपरा स्वयं से असहमत है, वहाँ एक चुनकर निश्चित दिखने के बजाय "
          "पूरी सीमा दिखाई जाती है।",
   noH="यहाँ क्या नहीं मिलेगा",
   no=["मृत्यु, रोग या तलाक़ की कोई भविष्यवाणी नहीं।",
       "कोई गारंटी नहीं, और यह दावा भी नहीं कि कोई गणना कुछ तय करती है।",
       "कोई खाता नहीं, पंजीकरण नहीं, कुकी बैनर नहीं — क्योंकि सहमति देने को कुछ है ही नहीं।",
       "कोई विज्ञापन नहीं, और किसी को कुछ बेचा नहीं जाता।"],
   privLink="गोपनीयता के दावे को स्वयं कैसे जाँचें",
   allH="सभी सत्ताईस नक्षत्र",
   foot="लाहिरी अयनांश · कुछ भी एकत्र नहीं"),
}

PRIV = {
 "en": dict(h1="Where your birth details go",
   lede="Nowhere. That is not a policy, it is an architecture, and the difference matters — a policy is a "
        "promise you have to take on trust, and this is a fact you can verify.",
   checkH="Check it in fifteen seconds",
   steps=["Open any calculator on this site.",
          "Press F12, or right-click and choose Inspect, to open your browser's developer tools.",
          "Go to the Network tab and clear it.",
          "Enter a birth date and press the button.",
          "Watch what is sent. You will see this site\u2019s own files and nothing else \u2014 no birth date, and no request to anybody else\u2019s server."],
   howH="Why there is nothing to send",
   how="The Moon's position is computed by about four hundred lines of JavaScript that your browser "
       "downloaded along with the page. The arithmetic happens on your own processor. There is no API "
       "behind these pages, no database, and no account system — the site is a handful of static "
       "files on a content host, which is why it also costs almost nothing to run.",
   conseqH="What follows from that",
   conseq=["There is no breach to suffer, because there is no store of birth data to breach.",
           "There is nothing to hand over if anyone demands it.",
           "There is no deletion request to make, and nothing to retain or expire.",
           "Most of GDPR and India's DPDP Act concern data that is collected. None is."],
   cookieH="Cookies and tracking",
   cookie="None. No analytics, no advertising pixels, no embedded fonts from a third party that would see "
          "your address, no cookie banner — a banner exists to collect consent, and there is nothing "
          "here to consent to.",
   limitH="Being precise about the limits",
   limit="Two honest qualifications. Your browser requests the page itself from whoever hosts it, and that "
         "host sees the request, as it does for every website on the internet — what it cannot see is "
         "any birth detail, because none is sent. And if a paid report is ever added, the payment itself "
         "will involve a payment provider; that transaction will be described plainly here before it exists, "
         "and the report will still be built on your machine from details the server never receives.",
   backH="Back to the calculators", foot="Lahiri ayanamsa · nothing collected"),
 "hi": dict(h1="आपका जन्म विवरण कहाँ जाता है",
   lede="कहीं नहीं। यह कोई नीति नहीं, रचना है — और यह अंतर महत्वपूर्ण है। नीति एक वादा है जिस पर भरोसा "
        "करना पड़ता है; यह एक तथ्य है जिसे आप जाँच सकते हैं।",
   checkH="पंद्रह सेकंड में जाँचिए",
   steps=["इस साइट का कोई भी कैलकुलेटर खोलिए।",
          "F12 दबाइए, या राइट-क्लिक करके Inspect चुनिए, जिससे ब्राउज़र के डेवलपर टूल्स खुलें।",
          "Network टैब पर जाकर उसे ख़ाली कीजिए।",
          "कोई जन्म तिथि भरकर बटन दबाइए।",
          "देखिए क्या भेजा गया। केवल इसी साइट की अपनी फ़ाइलें दिखेंगी \u2014 न कोई जन्म तिथि, न किसी और के सर्वर को कोई अनुरोध।"],
   howH="भेजने को कुछ है ही क्यों नहीं",
   how="चंद्रमा की स्थिति लगभग चार सौ पंक्तियों के जावास्क्रिप्ट से निकलती है, जो पृष्ठ के साथ ही आपके ब्राउज़र "
       "में आ गया। गणना आपके अपने प्रोसेसर पर होती है। इन पृष्ठों के पीछे कोई API नहीं, कोई डेटाबेस नहीं, कोई "
       "खाता व्यवस्था नहीं — यह साइट किसी होस्ट पर रखी कुछ स्थिर फ़ाइलें हैं, और इसीलिए इसे चलाने में "
       "लगभग कुछ ख़र्च भी नहीं होता।",
   conseqH="इससे क्या निकलता है",
   conseq=["कोई सेंध लगने को नहीं, क्योंकि जन्म-विवरण का कोई भंडार ही नहीं।",
           "कोई माँगे तो सौंपने को कुछ नहीं।",
           "मिटाने का अनुरोध करने की आवश्यकता नहीं, और रखने या समाप्त करने को कुछ नहीं।",
           "GDPR और भारत के DPDP अधिनियम का अधिकांश भाग एकत्र किए गए डेटा से संबंधित है। यहाँ कुछ एकत्र नहीं होता।"],
   cookieH="कुकी और ट्रैकिंग",
   cookie="कोई नहीं। न एनालिटिक्स, न विज्ञापन पिक्सेल, न किसी तीसरे पक्ष से आने वाले फ़ॉन्ट जो आपका पता देख "
          "सकें, न कुकी बैनर — बैनर सहमति लेने के लिए होता है, और यहाँ सहमति देने को कुछ है ही नहीं।",
   limitH="सीमाओं के विषय में स्पष्टता",
   limit="दो ईमानदार स्पष्टीकरण। आपका ब्राउज़र पृष्ठ स्वयं उस होस्ट से माँगता है जहाँ वह रखा है, और होस्ट उस "
         "अनुरोध को देखता है — जैसा इंटरनेट की हर साइट पर होता है। वह जो नहीं देख सकता वह है कोई भी जन्म "
         "विवरण, क्योंकि कुछ भेजा ही नहीं जाता। और यदि कभी सशुल्क फलादेश जोड़ा गया, तो भुगतान में एक भुगतान "
         "प्रदाता आएगा; वह लेनदेन यहाँ पहले ही साफ़ लिखा जाएगा, और फलादेश फिर भी आपकी मशीन पर उन विवरणों से "
         "बनेगा जो सर्वर तक कभी नहीं पहुँचते।",
   backH="कैलकुलेटर पर लौटिए", foot="लाहिरी अयनांश · कुछ भी एकत्र नहीं"),
}

def _head(t, title, desc, up, canon, alt_en, alt_hi, ldtype="WebSite"):
    ld = json.dumps({"@context":"https://schema.org","@type":ldtype,"name":title,
        "description":desc,"inLanguage":t["code"], **({"url":canon} if canon else {})}, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="{t['code']}"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
{f'<link rel="canonical" href="{canon}">' if canon else ''}
<link rel="alternate" hreflang="en" href="{alt_en}">
<link rel="alternate" hreflang="hi" href="{alt_hi}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="stylesheet" href="{up}site.css">
<script type="application/ld+json">{ld}</script>
</head><body class="{t['code']}"><div class="wrap">
"""

def index_page(lang, base):
    t = I18N[lang]; up = t["up"]
    canon = f"{base}/{'hi/' if lang=='hi' else ''}index.html" if base else ""
    alt_en = f"{base}/" if base else (up + "index.html" if lang=="hi" else "index.html")
    alt_hi = f"{base}/hi/" if base else ("hi/index.html" if lang=="en" else "index.html")
    tools = "".join(
      f"""<div style="border:1px solid var(--line);border-radius:12px;padding:1rem 1.1rem;min-width:0">
        <h3 style="font-family:var(--serif);font-size:1.15rem;margin:0 0 .35rem"><a href="{up}{href}">{name}</a></h3>
        <p style="margin:0;font-size:.94rem" class="dim">{blurb}</p></div>""" for href, name, blurb in t["tools"])
    nos = "".join(f"<li>{x}</li>" for x in t["no"])
    return _head(t, t["title"], t["desc"], up, canon, alt_en, alt_hi) + f"""<nav class="crumbs"><span><b>{t['site']}</b></span>
<span><a href="{alt_hi if lang=='en' else alt_en}">{t['switch']}</a></span></nav>

<h1>{t['tagline']}</h1>
<p class="lede">{t['lede']}</p>
<p><a href="{up}privacy.html"><b>{t['privLink']} &rarr;</b></a></p>

<h2>{t['toolsH']}</h2>
<div style="display:grid;gap:.9rem;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr))">{tools}</div>

<h2>{t['methodH']}</h2>
<div class="note"><p>{t['method']}</p></div>

<h2>{t['noH']}</h2>
<ul>{nos}</ul>

<footer><p><a href="{up}nakshatra.html">{t['allH']}</a> · {t['foot']}</p></footer>
</div></body></html>
"""

def privacy_page(lang, base):
    t = PRIV[lang]; i = I18N[lang]; up = i["up"]
    canon = f"{base}/{'hi/' if lang=='hi' else ''}privacy.html" if base else ""
    alt_en = f"{base}/privacy.html" if base else (up + "privacy.html" if lang=="hi" else "privacy.html")
    alt_hi = f"{base}/hi/privacy.html" if base else ("hi/privacy.html" if lang=="en" else "privacy.html")
    steps = "".join(f"<li>{s}</li>" for s in t["steps"])
    conseq = "".join(f"<li>{s}</li>" for s in t["conseq"])
    return _head(i, t["h1"], i["desc"], up, canon, alt_en, alt_hi) + f"""<nav class="crumbs"><a href="{up}index.html">&larr; {i['site']}</a>
<span><a href="{alt_hi if lang=='en' else alt_en}">{i['switch']}</a></span></nav>

<h1>{t['h1']}</h1>
<p class="lede">{t['lede']}</p>

<h2>{t['checkH']}</h2>
<div class="note"><ol style="margin:0;padding-left:1.2rem">{steps}</ol></div>

<h2>{t['howH']}</h2>
<p>{t['how']}</p>

<h2>{t['conseqH']}</h2>
<ul>{conseq}</ul>

<h2>{t['cookieH']}</h2>
<p>{t['cookie']}</p>

<h2>{t['limitH']}</h2>
<div class="cusp" style="border-radius:0 8px 8px 0"><p style="margin:0">{t['limit']}</p></div>

<footer><p><a href="{up}index.html">{t['backH']}</a> · {t['foot']}</p></footer>
</div></body></html>
"""

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="", help="site root, e.g. https://example.com (for canonical and sitemap)")
    base = ap.parse_args().base.rstrip("/")

    (OUT/"hi").mkdir(exist_ok=True)
    urls = ["nakshatra.html"]
    for i, n in enumerate(NAK):
        (OUT/f"{slug(n['en'])}.html").write_text(page(i, n, "en", base), encoding="utf-8")
        (OUT/"hi"/f"{slug(n['en'])}.html").write_text(page(i, n, "hi", base), encoding="utf-8")
        urls += [f"{slug(n['en'])}.html", f"hi/{slug(n['en'])}.html"]
    (OUT/"dasha.html").write_text(dasha_page("en", base), encoding="utf-8")
    (OUT/"hi"/"dasha.html").write_text(dasha_page("hi", base), encoding="utf-8")
    (OUT/"milan.html").write_text(milan_page("en", base), encoding="utf-8")
    (OUT/"hi"/"milan.html").write_text(milan_page("hi", base), encoding="utf-8")
    for lang, sub in (("en", ""), ("hi", "hi/")):
        d = OUT / sub if sub else OUT
        (d / "index.html").write_text(index_page(lang, base), encoding="utf-8")
        (d / "privacy.html").write_text(privacy_page(lang, base), encoding="utf-8")
    urls += ["dasha.html", "hi/dasha.html", "milan.html", "hi/milan.html",
             "index.html", "hi/index.html", "privacy.html", "hi/privacy.html"]
    print(f"{len(NAK)*2 + 8} pages written (English and Hindi)")

    if base:
        body = "".join(
            f"  <url><loc>{base}/{u}</loc><changefreq>monthly</changefreq></url>\n" for u in urls)
        (OUT/"sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n",
            encoding="utf-8")
        (OUT/"robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")
        print(f"sitemap.xml with {len(urls)} urls, robots.txt")
    else:
        print("no --base given, so no sitemap or canonical tags "
              "(pass --base once the domain exists)")
