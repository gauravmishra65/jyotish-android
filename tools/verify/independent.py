"""Independent cross-check of the forecast's dated facts, using pyswisseph directly (not the engine's code)."""
import os, json, sys, datetime as dt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "app", "src", "main", "python"))
import swisseph as swe
import engine_api as E

swe.set_ephe_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "app", "src", "main", "python", "ephe"))
swe.set_sid_mode(swe.SIDM_LAHIRI)
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
PID = {"Jupiter": swe.JUPITER, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE}
FL = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

def lon(jd, p):
    return swe.calc_ut(jd, PID[p], FL)[0][0]

def jd(d):  # date at 00:00 UT
    return swe.julday(d.year, d.month, d.day, 0)

def sign_runs(p, d0, d1):
    runs, d, cur = [], d0, None
    while d <= d1:
        s = int(lon(jd(d), p) // 30)
        if cur is None or s != cur[0]:
            if cur: runs.append(cur)
            cur = [s, d, d]
        cur[2] = d
        d += dt.timedelta(days=1)
    runs.append(cur)
    return [(SIGNS[s], a.isoformat(), b.isoformat()) for s, a, b in runs]

r = dict(E.CASES[0], now="2027-01-14", modules=E.FORECAST_MODULES, horizon_years=3)
c = E.chart_obj(r)
F = c["forecast"]
d0, d1 = dt.date(2027, 1, 14), dt.date(2030, 1, 13)
problems, checks = [], 0

# 1. Slow-planet sign changes: engine gochar segments vs a day-by-day independent scan (allow 1 day for the UT cut).
for p in ("Jupiter", "Saturn", "Rahu"):
    mine = sign_runs(p, d0, d1)
    eng = [(g["sign"], g["from"], g["to"]) for g in F["vedic"]["gochar_segments"][p]]
    for (s1, a1, b1) in mine:
        hit = [g for g in eng if g[0] == s1 and abs((dt.date.fromisoformat(max(g[1], d0.isoformat())) - dt.date.fromisoformat(a1)).days) <= 1]
        checks += 1
        if not hit:
            problems.append(f"{p} in {s1} from {a1}: engine has {eng}")
    print(p, "independent:", mine)

# 2. Vimshottari antardashas from the birth Moon, independently.
VIM = [("Ketu",7),("Venus",20),("Sun",6),("Moon",10),("Mars",7),("Rahu",18),("Jupiter",16),("Saturn",19),("Mercury",17)]
bt = dt.datetime(1988, 7, 14, 14, 35) - dt.timedelta(hours=5, minutes=30)
jb = swe.julday(bt.year, bt.month, bt.day, bt.hour + bt.minute / 60)
moon = swe.calc_ut(jb, swe.MOON, FL)[0][0]
nak = int(moon // (360 / 27)); frac = (moon % (360 / 27)) / (360 / 27)
i0 = nak % 9
Y = 365.2425
t = jb - frac * VIM[i0][1] * Y
seq = []
for k in range(9):
    lord, yrs = VIM[(i0 + k) % 9]
    for j in range(9):
        al, ay = VIM[(i0 + k + j) % 9]
        dur = yrs * ay / 120 * Y
        seq.append((lord, al, t, t + dur)); t += dur
def jdate(x):
    y, m, d, _ = swe.revjul(x); return dt.date(y, m, d).isoformat()
eng = {(a["maha"], a["antar"]): (a["from"], a["to"]) for a in F["vedic"]["vimshottari_antardashas"]}
for ma, an, a, b in seq:
    if (ma, an) in eng:
        checks += 1
        ef, et = eng[(ma, an)]
        if abs((dt.date.fromisoformat(ef) - dt.date.fromisoformat(jdate(a))).days) > 2 and ef > "2027-01-14":
            problems.append(f"{ma}-{an} start {jdate(a)} vs engine {ef}")
        print(f"  {ma}-{an}: independent {jdate(a)} – {jdate(b)} | engine {ef} – {et}")

# 3. Double transit, sampled on the 15th of every month: both Jupiter (1,5,7,9) and Saturn (1,3,7,10) on house h.
lag = c["vedic"]["lagna"]["sign"]; L = SIGNS.index(lag)
M = SIGNS.index(c["vedic"]["planets"]["Moon"]["sign"])
def touches(p, s, h_sign):
    return (h_sign - s) % 12 + 1 in ({1, 5, 7, 9} if p == "Jupiter" else {1, 3, 7, 10})
d = dt.date(2027, 1, 15)
while d < d1:
    js, ss = int(lon(jd(d), "Jupiter") // 30), int(lon(jd(d), "Saturn") // 30)
    for ref, base in (("from_lagna", L), ("from_moon", M)):
        for h in range(1, 13):
            mine = touches("Jupiter", js, (base + h - 1) % 12) and touches("Saturn", ss, (base + h - 1) % 12)
            runs = F["vedic"]["double_transit"][ref].get(str(h), [])
            eng_ = any(x["from"] <= d.isoformat() <= x["to"] for x in runs)
            checks += 1
            if mine != eng_:
                problems.append(f"double transit {ref} H{h} on {d}: independent {mine}, engine {eng_}")
    d = (d.replace(day=1) + dt.timedelta(days=32)).replace(day=15)

# 4. Saturn phases from the Moon (Sade Sati 12/1/2, Kantaka 4/7/10, Ashtama 8) on the 15th of each month.
d = dt.date(2027, 1, 15)
while d < d1:
    hm = (int(lon(jd(d), "Saturn") // 30) - M) % 12 + 1
    want = {12: "Sade", 1: "Sade", 2: "Sade", 4: "Kantaka Shani (4th)", 7: "Kantaka Shani (7th)", 10: "Kantaka Shani (10th)", 8: "Ashtama"}.get(hm)
    got = [x["kind"] for x in F["vedic"]["saturn_from_moon"] if x["from"] <= d.isoformat() <= x["to"]]
    checks += 1
    if bool(want) != bool(got) or (want and not any(g.startswith(want) for g in got)):
        problems.append(f"Saturn phase on {d}: house {hm} from Moon, independent {want}, engine {got}")
    d = (d.replace(day=1) + dt.timedelta(days=32)).replace(day=15)

# 5. Personal Year: reduce(day + month + year).
def red(n):
    while n > 9 and n not in (11, 22): n = sum(map(int, str(n)))
    return n
for py in F["numerology"]["personal_years"]:
    checks += 1
    want = red(red(14) + red(7) + red(int(py["year"])))
    want2 = red(sum(map(int, f"1407{py['year']}")))
    if py["personal_year"] not in (want, want2):
        problems.append(f"Personal Year {py['year']}: engine {py['personal_year']}, independent {want}/{want2}")

print(f"\n{checks} checks, {len(problems)} problems")
for p in problems[:30]: print(" -", p)
sys.exit(1 if problems else 0)
