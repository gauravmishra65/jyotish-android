#!/usr/bin/env python3
"""Generate the nakshatra page family from the engine's own data.

    python3 build.py

Writes one page per nakshatra plus the shared stylesheet and script. Every page
states its own computed facts - degree span, the four padas with their navamsa
signs, the dasha length of its lord - so no two pages are the same text with a
word changed, which is the difference between programmatic SEO that ranks and
the kind Google removes.
"""
import json, pathlib, re

OUT = pathlib.Path(__file__).parent
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
         "Sagittarius","Capricorn","Aquarius","Pisces"]
SIGNS_HI = ["मेष","वृषभ","मिथुन","कर्क","सिंह","कन्या","तुला","वृश्चिक","धनु","मकर","कुंभ","मीन"]
DASHA = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
NAKW, PADAW = 360/27, 360/108

NAK = json.loads((OUT/"data.json").read_text(encoding="utf-8"))

def slug(name): return re.sub(r"[^a-z0-9]+","-",name.lower()).strip("-")
def dms(deg):
    d = int(deg); m_f = (deg-d)*60; m = int(m_f); s = round((m_f-m)*60)
    if s == 60: s, m = 0, m+1
    if m == 60: m, d = 0, d+1
    return f"{d}° {m:02d}′ {s:02d}″"
def navamsa(lon): return int((lon*9)//30) % 12      # verified against the app engine, all 108 padas

def padas(i):
    rows = []
    for p in range(4):
        lo = i*NAKW + p*PADAW
        n = navamsa(lo + PADAW/2)
        rows.append({"n":p+1,"lo":lo,"hi":lo+PADAW,"sign":SIGNS[n],"signHi":SIGNS_HI[n]})
    return rows

def rashi_span(i):
    lo, hi = i*NAKW, (i+1)*NAKW
    a, b = int(lo//30), int((hi-1e-9)//30)
    return SIGNS[a] if a == b else f"{SIGNS[a]} and {SIGNS[b]}"

HEAD = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;500;600&family=Noto+Sans+Devanagari:wght@400;600&display=swap">
<link rel="stylesheet" href="site.css">
</head><body><div class="wrap">
"""

NAV = """<nav class="crumbs"><a href="nakshatra.html">&larr; All twenty-seven</a>
<span><a href="{prev}.html">{prevName}</a> · <a href="{next}.html">{nextName}</a></span></nav>
"""

def page(i, n):
    nm, dev, lord = n["en"], n["hi"], n["lord"]
    pr, nx = NAK[(i-1) % 27], NAK[(i+1) % 27]
    lo, hi = i*NAKW, (i+1)*NAKW
    pd = padas(i)
    title = f"{nm} Nakshatra"
    desc = (f"{nm} ({dev}) spans {dms(lo)} to {dms(hi)} of the sidereal zodiac, ruled by {lord}. "
            f"Its four padas, their navamsa signs, and a calculator that works out your nakshatra in your own browser.")
    rows = "".join(
        f"<tr><td class='n'>{p['n']}</td><td class='n'>{dms(p['lo'])} – {dms(p['hi'])}</td>"
        f"<td>{p['sign']} <span class='hi dim'>{p['signHi']}</span></td></tr>" for p in pd)
    return (HEAD.format(title=title, desc=desc)
      + NAV.format(prev=slug(pr["en"]), prevName=pr["en"], next=slug(nx["en"]), nextName=nx["en"])
      + f"""<h1>{nm} Nakshatra <span class="dev">{dev}</span></h1>
<p class="lede">{nm} is the {ordinal(i+1)} of the twenty-seven nakshatras, running from {dms(lo)} to {dms(hi)}
of the sidereal zodiac — which places it in {rashi_span(i)}. Its lord is {lord}, so a birth here opens the
Vimshottari sequence in {lord}'s period of {DASHA[lord]} years.</p>

<dl class="attrs">
  <div><dt>Ruling planet</dt><dd>{lord} <span class="hi dim">{n['lordHi']}</span></dd></div>
  <div><dt>Deity</dt><dd>{n['deity']}</dd></div>
  <div><dt>Symbol</dt><dd>{n['symbol']}</dd></div>
  <div><dt>Gana</dt><dd>{n['gana']}</dd></div>
  <div><dt>Dasha length</dt><dd>{DASHA[lord]} years</dd></div>
  <div><dt>Span</dt><dd class="n">{dms(lo)} – {dms(hi)}</dd></div>
</dl>

<h2>The four padas</h2>
<p>Each nakshatra divides into four quarters of 3°20′. Each quarter falls in a different navamsa sign,
and that sign colours how the nakshatra expresses itself.</p>
<div class="scroll"><table><thead><tr><th>Pada</th><th>Span</th><th>Navamsa sign</th></tr></thead>
<tbody>{rows}</tbody></table></div>

<h2>Where the Moon is now</h2>
<div class="note" id="live" data-nak="{i}">
  <p id="liveNow">Working it out…</p>
  <p id="liveNext" class="dim"></p>
</div>

<h2>Was the Moon here when you were born?</h2>
<form class="calc" id="form">
  <div class="fields">
    <div><label for="date">Date of birth</label><input type="date" id="date" value="1990-04-12" required></div>
    <div><label for="time">Time of birth</label><input type="time" id="time" value="05:24" required></div>
    <div><label for="tz">Time zone at birth</label><select id="tz"></select></div>
  </div>
  <button class="go" type="submit">Work it out</button>
  <div class="readout" id="out" hidden>
    <div class="nk"><b id="rName"></b><span class="dev" id="rDev"></span><span class="pada" id="rPada"></span></div>
    <div class="lon" id="rLon"></div>
    <div class="cusp" id="rCusp" hidden></div>
  </div>
</form>

<div class="note small"><p><strong>Nothing you type leaves this page.</strong> The Moon's position is computed
in your own browser from the ELP-2000/82 lunar theory with the Lahiri ayanamsa. There is no server here to
send a birth date to. Open your browser's Network tab and check.</p></div>

<footer><p><a href="nakshatra.html">All twenty-seven nakshatras</a> · Lahiri ayanamsa · nothing collected</p></footer>
</div><script src="engine.js"></script><script>initNakPage();</script></body></html>
""")

def ordinal(k):
    words = ["first","second","third","fourth","fifth","sixth","seventh","eighth","ninth","tenth",
             "eleventh","twelfth","thirteenth","fourteenth","fifteenth","sixteenth","seventeenth",
             "eighteenth","nineteenth","twentieth","twenty-first","twenty-second","twenty-third",
             "twenty-fourth","twenty-fifth","twenty-sixth","twenty-seventh"]
    return words[k-1]

if __name__ == "__main__":
    n_written = 0
    for i, n in enumerate(NAK):
        (OUT/f"{slug(n['en'])}.html").write_text(page(i, n), encoding="utf-8")
        n_written += 1
    print(f"{n_written} nakshatra pages written")
    index = [{"slug":slug(n["en"]),"en":n["en"],"hi":n["hi"],"lord":n["lord"],
              "lordHi":n["lordHi"],"deity":n["deity"],"symbol":n["symbol"],
              "lo":i*NAKW,"hi":(i+1)*NAKW,"dasha":DASHA[n["lord"]]} for i, n in enumerate(NAK)]
    (OUT/"index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    print("index.json written")
