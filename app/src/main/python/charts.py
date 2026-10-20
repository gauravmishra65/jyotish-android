"""charts.py - draw kundli diagrams (North Indian diamond or South Indian grid) as inline SVG.

Everything comes from the engine JSON: the sign of each house and the planets in it. No calculation here.
Charts: Janam Kundli (Lagna, D-1), Chandra Kundli (from the Moon), Navamsa (D-9), Dashamsa (D-10),
Bhava Chalit (planets by house cusp) and the Lal Kitab kundli (house 1 always read as Aries).
"""
import html

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
AB = {"en": {"Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me", "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke",
             "Lagna": "Asc", "R": "R"},
      "hi": {"Sun": "सू", "Moon": "चं", "Mars": "मं", "Mercury": "बु", "Jupiter": "गु", "Venus": "शु", "Saturn": "श", "Rahu": "रा", "Ketu": "के",
             "Lagna": "लग्न", "R": "व"}}
INK, LINE, SIGN, ACC, BG = "#1A1A1A", "#A9560A", "#7A7068", "#A9560A", "#FFFDF8"

# North Indian geometry on a 400 x 400 square: house -> polygon, and the inner vertex the sign number sits near.
A, B, C, D = (0, 0), (400, 0), (400, 400), (0, 400)
T, R, Bm, L, O = (200, 0), (400, 200), (200, 400), (0, 200), (200, 200)
P1, P2, P3, P4 = (100, 100), (300, 100), (300, 300), (100, 300)
NORTH = {1: ([T, P2, O, P1], O), 2: ([A, T, P1], P1), 3: ([A, P1, L], P1), 4: ([L, P1, O, P4], O), 5: ([L, P4, D], P4), 6: ([D, P4, Bm], P4),
         7: ([Bm, P4, O, P3], O), 8: ([Bm, P3, C], P3), 9: ([C, P3, R], P3), 10: ([R, P3, O, P2], O), 11: ([R, P2, B], P2), 12: ([B, P2, T], P2)}
# South Indian: fixed sign cells on a 4 x 4 grid (column, row), Pisces top left, running clockwise.
SOUTH = {11: (0, 0), 0: (1, 0), 1: (2, 0), 2: (3, 0), 3: (3, 1), 4: (3, 2), 5: (3, 3), 6: (2, 3), 7: (1, 3), 8: (0, 3), 9: (0, 2), 10: (0, 1)}


def _c(pts):
    return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)


def _lines(labels, cap):
    """Stack labels into lines; two per line once a house holds more than `cap`."""
    if len(labels) <= cap:
        return labels
    return ["  ".join(labels[k:k + 2]) for k in range(0, len(labels), 2)]


def _txt(x, y, s, size, fill, weight=400):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="middle" dominant-baseline="middle">{html.escape(s)}</text>'


# Fixed text anchors (planets) and sign-number spots (near each house's inner corner), as on hand-drawn charts.
N_TEXT = {1: (200, 96), 2: (100, 40), 3: (40, 100), 4: (96, 200), 5: (40, 300), 6: (100, 360), 7: (200, 304), 8: (300, 360),
          9: (360, 300), 10: (304, 200), 11: (360, 100), 12: (300, 40)}
N_SIGN = {1: (200, 168), 2: (100, 84), 3: (84, 100), 4: (168, 200), 5: (84, 300), 6: (100, 316), 7: (200, 232), 8: (300, 316),
          9: (316, 300), 10: (232, 200), 11: (316, 100), 12: (300, 84)}


def north_svg(houses, signs, title, desc, mark_lagna=True, lang="en"):
    """houses: {1..12: [labels]}, signs: {1..12: sign number 1..12 (or house number for Lal Kitab)}."""
    out = [f'<svg viewBox="-4 -4 408 408" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{html.escape(title + ". " + desc)}" '
           f'font-family="Calibri, Segoe UI, Noto Sans, Noto Sans Devanagari, Arial, sans-serif">',
           f'<rect x="0" y="0" width="400" height="400" fill="{BG}" stroke="{LINE}" stroke-width="2.5"/>',
           f'<path d="M0 0 L400 400 M400 0 L0 400 M200 0 L400 200 L200 400 L0 200 Z" fill="none" stroke="{LINE}" stroke-width="1.6"/>']
    for h in range(1, 13):
        sx, sy = N_SIGN[h]
        out.append(_txt(sx, sy, str(signs[h]), 14, SIGN, 600))
        labs = list(houses.get(h, []))
        if h == 1 and mark_lagna:
            labs = [AB[lang]["Lagna"]] + labs
        rhomb = h in (1, 4, 7, 10)
        lines = _lines(labs, 5 if rhomb else 3)
        lh, fs = (19, 16.5) if rhomb else (17, 15)
        cx, cy = N_TEXT[h]
        if h in (2, 12):
            cy = 22 + (len(lines) - 1) * lh / 2 if len(lines) > 1 else cy
        if h in (6, 8):
            cy = 378 - (len(lines) - 1) * lh / 2 if len(lines) > 1 else cy
        y0 = cy - (len(lines) - 1) * lh / 2
        for k, t in enumerate(lines):
            is_lg = h == 1 and mark_lagna and k == 0
            out.append(_txt(cx, y0 + k * lh, t, fs - (1.5 if is_lg else 0), ACC if is_lg else INK, 600 if is_lg else 700))
    out.append("</svg>")
    return "".join(out)


def south_svg(by_sign, lagna_idx, title, desc, lang="en", centre="", label=True):
    """by_sign: {0..11: [labels]}; lagna_idx: sign index of the rising sign (marked with a diagonal and the Asc label)."""
    out = [f'<svg viewBox="-4 -4 408 408" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{html.escape(title + ". " + desc)}" '
           f'font-family="Calibri, Segoe UI, Noto Sans, Noto Sans Devanagari, Arial, sans-serif">',
           f'<rect x="0" y="0" width="400" height="400" fill="{BG}" stroke="{LINE}" stroke-width="2.5"/>']
    for s, (col, row) in SOUTH.items():
        x, y = col * 100, row * 100
        out.append(f'<rect x="{x}" y="{y}" width="100" height="100" fill="none" stroke="{LINE}" stroke-width="1.6"/>')
        out.append(f'<text x="{x + 7}" y="{y + 16}" font-size="13" font-weight="600" fill="{SIGN}">{s + 1}</text>')
        labs = list(by_sign.get(s, []))
        if lagna_idx is not None and s == lagna_idx:
            out.append(f'<path d="M{x} {y + 22} L{x + 22} {y}" stroke="{ACC}" stroke-width="1.6"/>')
            if label:
                labs = [AB[lang]["Lagna"]] + labs
        lines = _lines(labs, 4)
        y0 = y + 56 - (len(lines) - 1) * 9
        for k, t in enumerate(lines):
            lg = label and lagna_idx is not None and s == lagna_idx and k == 0
            out.append(_txt(x + 50, y0 + k * 18, t, 15, ACC if lg else INK, 600 if lg else 700))
    if centre:
        out.append(_txt(200, 200, centre, 15, SIGN, 600))
    out.append("</svg>")
    return "".join(out)


def _lab(p, pd, lang, deg=True):
    s = AB[lang][p]
    if deg and pd and "deg_in_sign" in pd:
        s += f" {int(pd['deg_in_sign'])}"
    if pd and pd.get("retrograde") and p not in ("Rahu", "Ketu"):
        s += f"({AB[lang]['R']})"
    return s


def chart_specs(c, lang="en"):
    """Return the list of charts for one person: (key, title, caption, houses, signs, by_sign, lagna_idx, mark_lagna)."""
    v = c["vedic"]
    P = v["planets"]
    hi = lang == "hi"
    unknown = c["meta"].get("birth_time_confidence") == "unknown"
    out = []

    def from_signs(sign_of, first_sign, deg):
        f = SIGNS.index(first_sign)
        houses, by_sign = {h: [] for h in range(1, 13)}, {k: [] for k in range(12)}
        for p in ORDER:
            si = SIGNS.index(sign_of[p])
            lab = _lab(p, P.get(p) if deg else {"retrograde": P.get(p, {}).get("retrograde")}, lang, deg)
            houses[(si - f) % 12 + 1].append(lab)
            by_sign[si].append(lab)
        signs = {h: (f + h - 1) % 12 + 1 for h in range(1, 13)}
        return houses, signs, by_sign, f

    T = {
        "D1": (("Janam Kundli (Lagna chart)", "जन्म कुंडली (लग्न कुंडली)"),
               ("The sky at the moment of birth. The top diamond is house 1, your rising sign; the number beside each planet is its degree.",
                "जन्म के क्षण का आकाश। ऊपर का बीच वाला खाना पहला भाव (लग्न) है; ग्रह के साथ की संख्या राशि में उसका अंश है।")),
        "Moon": (("Chandra Kundli (Moon chart)", "चंद्र कुंडली"),
                 ("The same planets counted from the Moon's sign. Used for the mind and feelings, and for transits such as Sade Sati.",
                  "वही ग्रह, चंद्र राशि को पहला भाव मानकर। मन और भावनाओं के लिए, और साढ़े साती जैसे गोचर के लिए देखी जाती है।")),
        "D9": (("Navamsa (D-9)", "नवांश कुंडली (D-9)"),
               ("A finer chart for marriage, partnership and inner strength.", "विवाह, साझेदारी और आंतरिक बल के लिए बारीक कुंडली।")),
        "D10": (("Dashamsa (D-10)", "दशमांश कुंडली (D-10)"),
                ("A finer chart for career, status and public life.", "करियर, पद और सार्वजनिक जीवन के लिए बारीक कुंडली।")),
        "Chalit": (("Bhava Chalit", "भाव चलित"),
                   ("Planets placed by house boundaries instead of whole signs. A planet that changes house here also acts for the new house.",
                    "ग्रह पूरी राशि के बजाय भाव-सीमाओं के अनुसार। जो ग्रह यहाँ भाव बदलता है, वह नए भाव का फल भी देता है।")),
    }
    i = 1 if hi else 0
    if not unknown:
        h, s, bs, f = from_signs({p: P[p]["sign"] for p in ORDER}, v["lagna"]["sign"], True)
        out.append(("D1", T["D1"][0][i], T["D1"][1][i], h, s, bs, f, True))
    h, s, bs, f = from_signs({p: P[p]["sign"] for p in ORDER}, P["Moon"]["sign"], True)
    mh = {k: [x for x in v_ if not x.startswith(AB[lang]["Moon"])] for k, v_ in h.items()}
    mh[1] = [_lab("Moon", P["Moon"], lang)] + mh[1]
    out.append(("Moon", T["Moon"][0][i], T["Moon"][1][i], mh, s, bs, f, False))
    if not unknown:
        dc = v.get("divisional_charts", {})
        for k in ("D9", "D10"):
            if k in dc:
                h, s, bs, f = from_signs({p: dc[k][p] for p in ORDER}, dc[k]["Lagna"], False)
                out.append((k, T[k][0][i], T[k][1][i], h, s, bs, f, True))
        sh = v.get("bhava_chalit_shifts", {}) or {}
        f = SIGNS.index(v["lagna"]["sign"])
        houses = {hh: [] for hh in range(1, 13)}
        for p in ORDER:
            hh = sh.get(p, {}).get("chalit_house", P[p]["house"])
            houses[hh].append(_lab(p, P[p], lang, False))
        signs = {hh: (f + hh - 1) % 12 + 1 for hh in range(1, 13)}
        out.append(("Chalit", T["Chalit"][0][i], T["Chalit"][1][i], houses, signs, None, f, True))
    return out


def legend(lang="en", style="north"):
    if lang == "hi":
        how = ("उत्तर भारतीय शैली: ऊपर का बीच वाला खाना पहला भाव है और भाव घड़ी की उल्टी दिशा में चलते हैं: बाईं ओर ऊपर 2, बायाँ खाना 4, नीचे 7, दायाँ 10। "
               if style == "north" else "दक्षिण भारतीय शैली: राशियाँ स्थिर रहती हैं (ऊपर बाएँ मीन, फिर घड़ी की दिशा में मेष, वृषभ...)। तिरछी रेखा और \"लग्न\" वाला खाना आपकी लग्न राशि है। ")
        return (how + "हर खाने की छोटी धूसर संख्या राशि है: 1 मेष, 2 वृषभ, 3 मिथुन, 4 कर्क, 5 सिंह, 6 कन्या, 7 तुला, 8 वृश्चिक, 9 धनु, 10 मकर, 11 कुंभ, 12 मीन। "
                "ग्रह: सू सूर्य, चं चंद्र, मं मंगल, बु बुध, गु गुरु, शु शुक्र, श शनि, रा राहु, के केतु; (व) का अर्थ वक्री है।")
    how = ("North Indian style: the top centre diamond is house 1, and the houses run anticlockwise: house 2 is just to its upper left, the left diamond is house 4, the bottom diamond house 7 and the right diamond house 10. "
           if style == "north" else "South Indian style: the signs stay in fixed boxes (Pisces top left, then clockwise Aries, Taurus and so on). The box with the diagonal line and \"Asc\" holds your rising sign. ")
    return (how + "The small grey number in each box is the sign: 1 Aries, 2 Taurus, 3 Gemini, 4 Cancer, 5 Leo, 6 Virgo, 7 Libra, 8 Scorpio, 9 Sagittarius, 10 Capricorn, 11 Aquarius, 12 Pisces. "
            "Planets: Su Sun, Mo Moon, Ma Mars, Me Mercury, Ju Jupiter, Ve Venus, Sa Saturn, Ra Rahu, Ke Ketu; (R) means retrograde.")


def _figure(svg, title, cap, small=False):
    return (f'<figure class="kundli{" small" if small else ""}">{svg}<figcaption><strong>{html.escape(title)}</strong>'
            f'<span>{html.escape(cap)}</span></figcaption></figure>')


def _draw(spec, style, lang):
    key, title, cap, houses, signs, by_sign, f, mark = spec
    desc = "; ".join(f"house {h}: sign {signs[h]}" + (", " + ", ".join(houses[h]) if houses[h] else "") for h in range(1, 13))
    if style == "south" and by_sign is not None:
        return south_svg(by_sign, f, title, desc, lang, centre={"D1": "D-1", "D9": "D-9", "D10": "D-10", "Moon": AB[lang]["Moon"]}.get(key, ""), label=mark)
    return north_svg(houses, signs, title, desc, mark, lang)


def charts_html(charts, lang="en", style="north"):
    """Section 2 block: every chart for every person, then how to read them."""
    out = []
    for name, c in charts:
        specs = chart_specs(c, lang)
        if len(charts) > 1:
            out.append(f'<p class="kundli-person">{html.escape(name)}</p>')
        out.append('<div class="kundli-grid">' + "".join(_figure(_draw(s, style, lang), s[1], s[2]) for s in specs) + "</div>")
        if c["meta"].get("birth_time_confidence") == "unknown":
            out.append("<p class=\"guidance\">" + ("जन्म-समय अज्ञात है, इसलिए लग्न पर आधारित कुंडलियाँ (लग्न, नवांश, दशमांश, चलित) नहीं दिखाई गईं।" if lang == "hi" else
                       "The birth time is unknown, so the charts that depend on the rising sign (Lagna, Navamsa, Dashamsa, Chalit) are not shown.") + "</p>")
    out.append(f'<p class="guidance kundli-legend">{html.escape(legend(lang, style))}</p>')
    return "".join(out)


def start_chart(c, lang="en", style="north"):
    """The Lagna chart (or the Moon chart when the time is unknown) for the Start Here page."""
    s = chart_specs(c, lang)[0]
    return _figure(_draw(s, style, lang), s[1], s[2], small=True)


def lalkitab_chart(c, lang="en"):
    """Lal Kitab kundli: house 1 is always Aries, so the numbers are houses; planets from lalkitab.kundli."""
    k = c["lalkitab"]["kundli"]
    houses = {h: [AB[lang][p] for p in ORDER if p in k.get(str(h), [])] for h in range(1, 13)}
    title = "लाल किताब कुंडली" if lang == "hi" else "Lal Kitab Kundli"
    cap = ("लाल किताब में पहला भाव हमेशा मेष माना जाता है, इसलिए यहाँ संख्याएँ भाव हैं, राशियाँ नहीं।" if lang == "hi" else
           "Lal Kitab always reads house 1 as Aries, so the numbers here are houses, not signs.")
    desc = "; ".join(f"house {h}" + (": " + ", ".join(houses[h]) if houses[h] else "") for h in range(1, 13))
    return _figure(north_svg(houses, {h: h for h in range(1, 13)}, title, desc, False, lang), title, cap, small=True)
