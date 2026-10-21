"""muhurta_report.py - turn muhurta.json into a branded, self-contained HTML page (English or Hindi).

The page reuses the report template's stylesheet so it matches the life reading. You write two short pieces
in plain words and pass them as files: the summary (which window you recommend and why, in two or three
paragraphs) and the advice (how to use the chosen time, and what the timing cannot do). The renderer refuses
to run without them, so an unfinished page cannot be delivered.

Usage:
  python scripts/muhurta_report.py --in muhurta.json --summary summary.html --advice advice.html \
      [--lang hi] [--client "Name"] [--author "Gaurav Mishra"] [--site authorgaurav.com] --out muhurta.html
"""
import argparse
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
E = html.escape

L = {
    "en": {"title": "Muhurta: Choosing an Auspicious Time", "for": "Prepared for", "event": "Event", "range": "Dates searched",
           "place": "Place", "people": "Checked against the birth charts of", "best": "The best windows found",
           "cols": ["Date", "Time (local)", "Nakshatra", "Tithi", "Rising sign", "Why it works", "Cautions"],
           "summary": "Recommendation", "advice": "How to use the time", "why_not": "Why other times were ruled out",
           "why_cols": ["Reason", "Hours ruled out"], "rules": "Rules used", "show": "Show the detailed calculation",
           "hide": "Hide the detailed calculation", "none": "none", "shukla": "Shukla", "krishna": "Krishna",
           "found": "acceptable windows were found in the range; the table shows the strongest.",
           "conv": "Conventions", "lead": "A muhurta is a moment chosen so that the day's panchang and the rising sign support a new beginning. "
           "Times that break a classical rule are ruled out; the rest are ranked by how many supporting factors they have."},
    "hi": {"title": "मुहूर्त: शुभ समय का चयन", "for": "किसके लिए", "event": "कार्य", "range": "खोजी गई तिथियाँ",
           "place": "स्थान", "people": "इनकी जन्म-कुंडलियों से मिलान", "best": "सबसे अच्छे मुहूर्त",
           "cols": ["दिनांक", "समय (स्थानीय)", "नक्षत्र", "तिथि", "लग्न", "क्यों शुभ", "सावधानियाँ"],
           "summary": "सुझाव", "advice": "इस समय का उपयोग कैसे करें", "why_not": "दूसरे समय क्यों छोड़े गए",
           "why_cols": ["कारण", "छोड़े गए घंटे"], "rules": "प्रयुक्त नियम", "show": "विस्तृत गणना देखें",
           "hide": "विस्तृत गणना छिपाएँ", "none": "कोई नहीं", "shukla": "शुक्ल", "krishna": "कृष्ण",
           "found": "उपयुक्त समय-खंड इस अवधि में मिले; तालिका में सबसे प्रबल दिखाए गए हैं।",
           "conv": "परिपाटी", "lead": "मुहूर्त वह क्षण है जिसमें उस दिन का पंचांग और उदित लग्न नए आरंभ का साथ दें। "
           "जो समय किसी शास्त्रीय नियम को तोड़ता है उसे छोड़ दिया जाता है; बाकी को सहायक कारकों के आधार पर क्रम दिया जाता है।"},
}
EVENT_HI = {"marriage": "विवाह", "griha_pravesh": "गृह प्रवेश", "vehicle": "वाहन क्रय", "business": "व्यापार आरंभ"}
YOGA_HI = {"Vishkambha": "विष्कुम्भ", "Atiganda": "अतिगण्ड", "Shula": "शूल", "Ganda": "गण्ड", "Vyaghata": "व्याघात",
           "Vajra": "वज्र", "Vyatipata": "व्यतीपात", "Parigha": "परिघ", "Vaidhriti": "वैधृति"}
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
RULE_LABELS = {  # key: (English, Hindi)
    "nakshatras": ("Nakshatras allowed", "स्वीकृत नक्षत्र"), "weekdays": ("Preferred weekdays", "श्रेष्ठ वार"),
    "avoid_weekdays": ("Weekdays traditionally avoided", "परंपरा से वर्जित वार"), "tithis": ("Preferred tithis (in each paksha)", "श्रेष्ठ तिथियाँ (प्रत्येक पक्ष में)"),
    "avoid_tithis": ("Tithis ruled out", "वर्जित तिथियाँ"), "lagnas_best": ("Best rising signs", "श्रेष्ठ लग्न"),
    "lagnas_avoid": ("Rising signs ruled out", "वर्जित लग्न"), "shukla_preferred": ("Shukla paksha preferred", "शुक्ल पक्ष श्रेष्ठ"),
    "kharmas": ("Kharmas ruled out", "खरमास वर्जित"), "panchaka": ("Panchaka ruled out", "पंचक वर्जित"),
    "combust_forbid": ("Must not be combust", "अस्त न हों"), "empty_houses": ("Houses from the lagna that should be empty", "लग्न से रिक्त रहने वाले भाव"),
    "forbidden_nitya_yogas": ("Nitya yogas ruled out", "वर्जित नित्य योग"), "rikta_tithis": ("Rikta tithis (always ruled out)", "रिक्ता तिथियाँ (सदा वर्जित)"),
    "weekday_rule": ("Weekday rule", "वार का नियम"),
}


def _rule_value(k, v, hi):
    """Readable value for one rules_used entry."""
    import hindi_shell as HS
    if isinstance(v, bool):
        return ("हाँ" if v else "नहीं") if hi else ("yes" if v else "no")
    if k == "weekday_rule":
        return {"soft": ("penalty only", "केवल अंक घटते हैं"), "hard": ("ruled out", "पूर्णतः वर्जित")}[v][hi]
    if not v:
        return "कोई नहीं" if hi else "none"
    items = list(v)
    if k.startswith("lagnas"):
        items = [SIGNS[i] for i in items]
    if k == "empty_houses":
        items = [(f"{h}वाँ" if hi else f"{h}th") for h in items]
    if hi:
        items = [HS.SIGN.get(x) or HS.NAK.get(x) or HS.PLANET.get(x) or WD_HI.get(x) or YOGA_HI.get(x) or str(x) for x in items]
    return ", ".join(map(str, items))


WD_HI = {"Monday": "सोमवार", "Tuesday": "मंगलवार", "Wednesday": "बुधवार", "Thursday": "गुरुवार", "Friday": "शुक्रवार",
         "Saturday": "शनिवार", "Sunday": "रविवार"}


def _hi_text(s):
    """Translate the engine's short reason phrases into Hindi."""
    import hindi_shell as HS
    s = re.sub(r"(\d+)th from the lagna", lambda m: f"लग्न से {m.group(1)}वाँ भाव", s)
    rep = [("benefics in kendra or trine from the lagna: ", "लग्न से केंद्र या त्रिकोण में शुभ ग्रह: "), (" lagna avoided for this event", " लग्न इस कार्य के लिए वर्जित"),
           (" lagna", " लग्न"), ("Krishna paksha (Shukla preferred)", "कृष्ण पक्ष (शुक्ल पक्ष श्रेष्ठ)"), ("occupied: ", "ग्रह स्थित: "),
           ("malefic in the lagna: ", "लग्न में पाप ग्रह: "), ("Moon in the लग्न से", "चंद्र लग्न से"),
           ("Abhijit muhurta", "अभिजित मुहूर्त"), ("tithi ", "तिथि "), ("(Shukla)", "(शुक्ल)"), ("(Krishna)", "(कृष्ण)"),
           ("nakshatra not in the event's list", "नक्षत्र इस कार्य की सूची में नहीं"), (" avoided for this event", " इस कार्य के लिए वर्जित"),
           ("Rikta tithi", "रिक्ता तिथि"), ("Amavasya", "अमावस्या"), ("Purnima", "पूर्णिमा"), ("Vishti (Bhadra) karana", "विष्टि (भद्रा) करण"),
           (" yoga", " योग"), ("Rahu Kalam", "राहु काल"), ("Yamaganda", "यमगंड"), ("Gulika Kalam", "गुलिक काल"), (" combust", " अस्त"),
           ("Kharmas (Sun in Sagittarius or Pisces)", "खरमास (सूर्य धनु या मीन में)"), ("Panchaka", "पंचक"),
           ("Tarabala fails for ", "तारा बल अनुकूल नहीं: "), (" (traditionally avoided for this event)", " (इस कार्य के लिए परंपरा से वर्जित)"), ("Chandrabala fails for ", "चंद्र बल अनुकूल नहीं: ")]
    for a, b in sorted(rep, key=lambda x: -len(x[0])):  # longest first, so a phrase is not split by a shorter one
        s = s.replace(a, b)
    for en, h in sorted(list(HS.SIGN.items()) + list(HS.PLANET.items()) + list(HS.NAK.items()) + list(WD_HI.items()) + list(YOGA_HI.items()),
                        key=lambda x: -len(x[0])):
        s = re.sub(r"(?<![A-Za-z])" + re.escape(en) + r"(?![A-Za-z])", h, s)
    return s


def render(data, summary, advice, lang="en", client="", author="Gaurav Mishra", site="authorgaurav.com"):
    T = L[lang]
    hi = lang == "hi"
    X = _hi_text if hi else (lambda s: s)
    tpl = open(os.path.join(HERE, "..", "assets", "report_template.html"), encoding="utf-8").read()
    style = tpl[tpl.index("<style>"): tpl.index("</style>") + len("</style>")]
    rows = []
    for w in data["best_windows"]:
        pk = T["shukla"] if w["paksha"] == "Shukla" else T["krishna"]
        t15 = w["tithi"] if w["tithi"] <= 15 else w["tithi"] - 15
        rows.append("<tr>" + "".join(f"<td>{c}</td>" for c in (
            f"{w['start_local'][:10]}<br><small>{E(X(w['weekday']))}</small>", f"{w['start_local'][11:]} &ndash; {w['end_local'][11:]}", E(X(w["nakshatra"])),
            f"{t15} {pk}", E(X(w["lagna"])), E(X("; ".join(w["supports"]))), E(X("; ".join(w["weaknesses"])) or T["none"]))) + "</tr>")
    why = "".join(f"<tr><td>{E(X(k))}</td><td>{v / 60:.0f}</td></tr>" for k, v in list(data["time_rejected_minutes_by_reason"].items())[:14])
    ru = data["rules_used"]
    rules = "".join(f"<tr><td>{E(RULE_LABELS.get(k, (k.replace('_', ' '),) * 2)[hi])}</td><td>{E(_rule_value(k, v, hi))}</td></tr>" for k, v in ru.items())
    ev = EVENT_HI.get(data["event"], data["event_label"]) if hi else data["event_label"]
    calc = lambda inner: (f'<div class="calc"><button type="button" class="calc-toggle" aria-expanded="false"><span class="lbl-show">{T["show"]}</span>'  # noqa: E731
                          f'<span class="lbl-hide">{T["hide"]}</span></button><div class="calc-body">{inner}</div></div>')
    head = "".join(f"<th>{c}</th>" for c in T["cols"])
    page = f"""<!DOCTYPE html>
<html lang="{lang}">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>{E(T['title'])}</title>
{style}
</head>
<body>
<div id="topbar"><div class="brand">{E(author)}<span class="site">&nbsp;|&nbsp;{E(site)}</span></div></div>
<main>
<section class="page" id="muhurta">
<h1 class="section">{E(T['title'])}</h1>
<div class="lead"><p class="lead-what">{T['lead']}</p></div>
<div class="table-scroll"><table class="data"><tbody>
<tr><td>{T['for']}</td><td>{E(client or ', '.join(data['people']) or '-')}</td></tr>
<tr><td>{T['event']}</td><td>{E(ev)}</td></tr>
<tr><td>{T['range']}</td><td>{E(data['range'][0])} &ndash; {E(data['range'][1])}</td></tr>
<tr><td>{T['place']}</td><td>{data['place']['lat']:.3f}, {data['place']['lon']:.3f} ({E(data['place']['tz'])})</td></tr>
<tr><td>{T['people']}</td><td>{E(', '.join(data['people'])) or T['none']}</td></tr>
</tbody></table></div>
<h2 class="sub">{T['summary']}</h2>
{summary}
<h2 class="sub">{T['best']}</h2>
<p>{data['windows_found']} {T['found']}</p>
<div class="table-scroll"><table class="data"><thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<h2 class="sub">{T['advice']}</h2>
{advice}
<h3 class="area">{T['why_not']}</h3>
{calc(f'<div class="table-scroll"><table class="data"><thead><tr><th>{T["why_cols"][0]}</th><th>{T["why_cols"][1]}</th></tr></thead><tbody>{why}</tbody></table></div>')}
<h3 class="area">{T['rules']}</h3>
{calc(f'<div class="table-scroll"><table class="data"><tbody>{rules}</tbody></table></div><p class="guidance">{E(data["conventions"])}</p>')}
<p class="guidance">{E(data['disclaimer'])}</p>
</section>
</main>
<script>document.querySelectorAll('.calc-toggle').forEach(b=>b.addEventListener('click',()=>{{const c=b.closest('.calc');c.classList.toggle('open');b.setAttribute('aria-expanded',c.classList.contains('open'));}}));</script>
</body></html>"""
    return page


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--advice", required=True)
    ap.add_argument("--lang", default="en", choices=["en", "hi"])
    ap.add_argument("--client", default="")
    ap.add_argument("--author", default="Gaurav Mishra")
    ap.add_argument("--site", default="authorgaurav.com")
    ap.add_argument("--out", default="muhurta.html")
    a = ap.parse_args()
    summary, advice = open(a.summary, encoding="utf-8").read().strip(), open(a.advice, encoding="utf-8").read().strip()
    for nm, txt in (("summary", summary), ("advice", advice)):
        if len(re.sub(r"<[^>]+>", "", txt).split()) < 25 or "@@WRITE" in txt:
            raise SystemExit(f"--{nm} is missing or too short: write it in plain words (at least a short paragraph) before rendering")
    page = render(json.load(open(a.inp, encoding="utf-8")), summary, advice, a.lang, a.client, a.author, a.site)
    open(a.out, "w", encoding="utf-8").write(page)
    print(f"wrote {a.out} ({len(page) // 1024} KB)")


if __name__ == "__main__":
    main()
