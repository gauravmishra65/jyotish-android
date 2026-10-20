"""calibration.py - Phase 5: base rates, past-event calibration and the birth-time error model.

  time_error_model()  PVR ch. 32.2: for a stated uncertainty of +-m minutes, which varga lagnas, planets in key
                      vargas, special lagnas and dasha dates can change. Engine recomputation, with PVR's
                      rule-of-thumb formulas shown beside it (Vimshottari n*m/4 days; Kalachakra paramayush*m days).
  calibrate()         K.N. Rao's practice via Boney: test the chart's rules on dated past events. For each event,
                      which layers fired, how often each layer is true by chance in this chart (base rate), the
                      expected number of hits and the chance probability of at least the observed hits
                      (Poisson-binomial). Lift = hits / expected.
  RULE_REGISTRY       every timing rule with its evidence grade (A classical + tested figures, B classical text,
                      C author's research, D folk). Grades C and D never raise a window's strength.
"""
import datetime as dt
import math
import swisseph as swe
from common import SIGNS, n360, sign_of, deg_in_sign, jd_to_dt, nak_info
import vedic
import events

KEY_VARGAS = [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]
VARGA_USE = {1: "everything lagna-based", 2: "wealth", 3: "siblings", 4: "home, property, abroad", 7: "children",
             9: "marriage, dharma", 10: "career", 12: "parents", 16: "vehicles, comforts", 20: "spiritual practice",
             24: "education", 27: "strengths", 30: "misfortunes", 40: "maternal legacy", 45: "paternal legacy",
             60: "past karma (needs an exact time)"}
EVENT_AREA = {"marriage": "marriage", "wedding": "marriage", "engagement": "marriage", "child": "children",
              "childbirth": "children", "birth of child": "children", "children": "children", "career": "career",
              "job": "career", "promotion": "career", "money": "money", "windfall": "money", "property": "property",
              "house": "property", "home": "property", "abroad": "abroad", "relocation": "abroad", "emigration": "abroad",
              "education": "education", "degree": "education", "graduation": "education", "spiritual": "spiritual"}
RULE_REGISTRY = [
    {"rule": "Marriage: K.N. Rao steps (Jupiter-Saturn on 1/7, Jupiter on Venus/5th, Mars within 6 months)", "grade": "A",
     "source": "K.N. Rao via Trivedi; Trivedi's 15 cases", "check": "base rate per chart + Trivedi cohort"},
    {"rule": "Children: Jupiter and Saturn on 5, 5L, 9, 9L", "grade": "A", "source": "K.N. Rao rules 1-2 via Boney",
     "check": "base rate per chart"},
    {"rule": "Area dasha lists (marriage, children, career, money, property, education, spiritual)", "grade": "B",
     "source": "Boney; Trivedi; ICAS", "check": "base rate per chart"},
    {"rule": "Career: Jupiter and Saturn on 10/10L or Jupiter over natal Saturn", "grade": "B",
     "source": "Rayudu; Chatterjee rule 19", "check": "base rate per chart"},
    {"rule": "Money, property, education, spiritual transit rules", "grade": "B", "source": "Boney", "check": "base rate per chart"},
    {"rule": "Abroad: Rahu/12th-lord dasha; Saturn or Rahu on Paradesa/Jalapatana saham", "grade": "C",
     "source": "Boney 19/20 (no contrast group); PVR 28.8.2", "check": "base rate per chart"},
    {"rule": "Jaimini sign eligibility for each area", "grade": "B (marriage, children, career, property) / C (money, abroad)",
     "source": "Boney", "check": "base rate per chart"},
    {"rule": "Service or business screen", "grade": "C, contrast-tested", "source": "ICAS, S.N. Kapoor (10 vs 10 charts)",
     "check": "contrast group (9/10 and 8/10)"},
    {"rule": "KP dasha-lord significations of the event houses", "grade": "B", "source": "KP readers", "check": "base rate per chart"},
    {"rule": "Murthis, taras, special nakshatras, latta", "grade": "B", "source": "PVR ch. 26", "check": "no base rate (refines months only)"},
    {"rule": "Kakshya rekhas", "grade": "B", "source": "PVR 25.5.2", "check": "no base rate (refines days only)"},
    {"rule": "Marriage age '7th sign + 8, then multiples of 5'", "grade": "D", "source": "folk rule", "check": "not used"},
]


# ------------------------------------------------------------------ statistics
def poisson_binomial_tail(ps, k):
    """P(X >= k) where X is a sum of independent Bernoulli(p_i)."""
    dist = [1.0]
    for p in ps:
        p = min(max(p, 0.0), 1.0)
        nxt = [0.0] * (len(dist) + 1)
        for i, q in enumerate(dist):
            nxt[i] += q * (1 - p)
            nxt[i + 1] += q * p
        dist = nxt
    return sum(dist[k:]) if k < len(dist) else 0.0


# ------------------------------------------------------------------ PVR 32.2 arithmetic
def varga_lagna_options(asc_lo, asc_hi, n):
    """Varga lagna signs met while the lagna moves from asc_lo to asc_hi (PVR Example 129)."""
    out, step = [], 1.0 / 240.0          # 15 arc-seconds
    x, cur, start = asc_lo, vedic.varga_sign(asc_lo, n), asc_lo
    span = n360(asc_hi - asc_lo)
    k = 0
    while k * step < span:
        k += 1
        y = n360(asc_lo + min(k * step, span))
        s = vedic.varga_sign(y, n)
        if s != cur:
            out.append((SIGNS[cur], round(start, 4), round(y, 4)))
            cur, start = s, y
    out.append((SIGNS[cur], round(start, 4), round(asc_hi, 4)))
    return out


def vimshottari_error_days(full_dasa_years, minutes):
    """PVR 32.2.2: shift of all Vimshottari dates (days) for a birth-time error of m minutes."""
    return full_dasa_years * minutes / 4.0


def kalachakra_error_days(paramayush, minutes):
    return paramayush * minutes


# ------------------------------------------------------------------ time error model
def time_error_model(jd, birth_utc, lat, lon, ayan="lahiri", node="mean", minutes=5):
    swe.set_sid_mode(vedic.AYAN[ayan])
    asc_at = lambda j: vedic._asc_at(j, lat, lon, ayan)
    lo_j, hi_j = jd - minutes / 1440.0, jd + minutes / 1440.0
    step = 0.25 / 1440.0
    n_steps = int(round((hi_j - lo_j) / step))
    ascs = [asc_at(lo_j + i * step) for i in range(n_steps + 1)]
    mins = [-minutes + i * 0.25 for i in range(n_steps + 1)]
    vrows = []
    for n in KEY_VARGAS:
        seq = [vedic.varga_sign(a, n) for a in ascs]
        runs, s0, m0 = [], seq[0], mins[0]
        for s, m in zip(seq[1:], mins[1:]):
            if s != s0:
                runs.append({"sign": SIGNS[s0], "from_min": m0, "to_min": m})
                s0, m0 = s, m
        runs.append({"sign": SIGNS[s0], "from_min": m0, "to_min": mins[-1]})
        vrows.append({"varga": f"D{n}", "use": VARGA_USE[n], "lagna_signs": runs, "stable": len(runs) == 1})
    # planets near varga borders (Moon moves fastest)
    pos_lo = vedic.sidereal_positions(lo_j, ayan, node)
    pos_hi = vedic.sidereal_positions(hi_j, ayan, node)
    prow = []
    for n in (1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 30, 60):
        for p in pos_lo:
            a, b = vedic.varga_sign(pos_lo[p]["lon"], n), vedic.varga_sign(pos_hi[p]["lon"], n)
            if a != b:
                prow.append({"varga": f"D{n}", "planet": p, "signs": [SIGNS[a], SIGNS[b]]})
    # nakshatra / pada of the Moon
    m_lo, m_hi = nak_info(pos_lo["Moon"]["lon"]), nak_info(pos_hi["Moon"]["lon"])
    moon_change = (m_lo["name"], m_lo["pada"]) != (m_hi["name"], m_hi["pada"])
    # special lagnas
    import rasidasa
    sl_lo = rasidasa.special_lagnas(lo_j, lat, lon, ascs[0], pos_lo["Moon"]["lon"], vedic.AYAN[ayan])
    sl_hi = rasidasa.special_lagnas(hi_j, lat, lon, ascs[-1], pos_hi["Moon"]["lon"], vedic.AYAN[ayan])
    sp = {k: {"signs": sorted({sl_lo[k]["sign"], sl_hi[k]["sign"]}), "stable": sl_lo[k]["sign"] == sl_hi[k]["sign"]}
          for k in ("HL", "GL", "SL", "BL") if k in sl_lo and k in sl_hi}   # no BL/HL/GL where the Sun does not rise
    # dasha dates: recompute at both ends
    base = vedic.dashas(vedic.sidereal_positions(jd, ayan, node)["Moon"]["lon"], birth_utc, birth_utc)["vimshottari"]
    first_lord = base["mahadashas"][0]["lord"]
    full = dict(vedic.VIM_ORDER)[first_lord]
    shifts = []
    for sgn, j in ((-1, lo_j), (1, hi_j)):
        bu = birth_utc + dt.timedelta(minutes=sgn * minutes)
        d2 = vedic.dashas(vedic.sidereal_positions(j, ayan, node)["Moon"]["lon"], bu, bu)["vimshottari"]
        a = dt.date.fromisoformat(base["mahadashas"][1]["start"])
        b = dt.date.fromisoformat(d2["mahadashas"][1]["start"])
        shifts.append((b - a).days)
    kc_lo = rasidasa.kalachakra(pos_lo["Moon"]["lon"], birth_utc, birth_utc)
    kc_b = rasidasa.kalachakra(vedic.sidereal_positions(jd, ayan, node)["Moon"]["lon"], birth_utc, birth_utc)
    kshift = (dt.date.fromisoformat(kc_lo["dasas"][1]["start"]) - dt.date.fromisoformat(kc_b["dasas"][1]["start"])).days
    unstable = [r["varga"] for r in vrows if not r["stable"]]
    return {"uncertainty_minutes": minutes,
            "lagna_range": [round(ascs[0], 4), round(ascs[-1], 4)],
            "varga_lagnas": vrows,
            "planets_changing_varga_sign": prow,
            "moon_nakshatra_or_pada_changes": moon_change,
            "special_lagnas": sp,
            "vimshottari_date_shift_days": {"engine_at_minus_and_plus": shifts,
                                            "pvr_formula": round(vimshottari_error_days(full, minutes), 1),
                                            "rule": f"PVR 32.2.2: n x m / 4 days with n = {full} ({first_lord} dasa at birth)"},
            "kalachakra_date_shift_days": {"engine_at_minus": kshift, "pvr_formula": kalachakra_error_days(kc_b["paramayush"], minutes),
                                           "rule": f"PVR 32.2.2: paramayush ({kc_b['paramayush']}) x m days"},
            "do_not_read": [f"{v} lagna and houses" for v in unstable],
            "safe_to_read": [r["varga"] for r in vrows if r["stable"]],
            "rule": ("PVR 32.2: the lagna moves about 1 deg in 4 minutes; D-10 changes every 3 deg (12 min), D-24 every "
                     "1 deg 15' (5 min). Claims that rest on a varga lagna that changes inside the stated uncertainty are "
                     "withheld; known past events can fix it, D-9 or D-10 first, then finer charts (32.3).")}


# ------------------------------------------------------------------ past-event calibration
def _parse_events(txt):
    out = []
    for chunk in [c for c in (txt or "").split(",") if c.strip()]:
        d, _, lab = chunk.partition(":")
        lab = lab.strip().lower()
        area = EVENT_AREA.get(lab) or next((EVENT_AREA[k] for k in EVENT_AREA if k in lab), None)
        out.append({"date": dt.date.fromisoformat(d.strip()), "label": lab or d.strip(), "area": area})
    return out


def _area_base(key, rule, c, v, vo, E, pts, birth, step=61):
    cnt = {"dasha": 0, "transit": 0, "sign": 0, "dasha+transit": 0, "kp": 0}
    n = 0
    for d in events._months(birth + dt.timedelta(days=int(18 * 365.25)), birth + dt.timedelta(days=int(70 * 365.25)), step):
        r = events.evaluate_area(key, rule, c, v, vo, E, pts, d)
        n += 1
        cnt["dasha"] += r["dasha"]
        cnt["transit"] += r["transit"]
        cnt["sign"] += r["sign"]
        cnt["dasha+transit"] += r["dasha"] and r["transit"]
    return {k: x / n for k, x in cnt.items()}, n


def _kp_fires(kpd, v, area, iso):
    if not kpd or area not in events.KP_EVENTS:
        return None
    md, ad = events._lords_at(v, iso)
    pos = events.KP_EVENTS[area][1]
    sig = kpd["planet_significations"]
    return bool(set(sig.get(md, [])) & pos) and bool(set(sig.get(ad, [])) & pos)


def _kp_base(kpd, v, area, birth):
    hits = n = 0
    for d in events._months(birth + dt.timedelta(days=int(18 * 365.25)), birth + dt.timedelta(days=int(70 * 365.25)), 61):
        f = _kp_fires(kpd, v, area, d.isoformat())
        if f is None:
            return None
        hits += f
        n += 1
    return hits / n


def calibrate(v, vo, evlist, jd_birth, birth_utc, lat, lon, gender, ayan="lahiri", node="mean", kp=None):
    E = events.Eph(ayan, node)
    pts, _ = events.reference_points(v, jd_birth, lat, lon, gender)
    A, c = events.area_rules(v, vo)
    birth = birth_utc.date()
    bases, rows, all_ps, all_hits = {}, [], [], 0
    per_rule = {}
    for ev in evlist:
        area = ev["area"]
        if area is None:
            rows.append({"date": ev["date"].isoformat(), "event": ev["label"], "area": None,
                         "note": "event type not mapped to a rule set (use marriage, child, career, money, property, abroad, education, spiritual)"})
            continue
        if area not in bases:
            b, _ = _area_base(area, A[area], c, v, vo, E, pts, birth)
            kb = _kp_base(kp, v, area, birth) if kp else None
            if kb is not None:
                b["kp"] = kb
            bases[area] = b
        b = bases[area]
        r = events.evaluate_area(area, A[area], c, v, vo, E, pts, ev["date"])
        fired = {"dasha": r["dasha"], "transit": r["transit"], "sign": r["sign"], "dasha+transit": r["dasha"] and r["transit"]}
        if "kp" in b:
            fired["kp"] = _kp_fires(kp, v, area, ev["date"].isoformat())
        if area == "marriage":
            jd = events._jd(ev["date"])
            s_ax = events._covers_axis(c, "Saturn", E.lon(jd, "Saturn"))
            j_ax = events._covers_axis(c, "Jupiter", E.lon(jd, "Jupiter"))
            fired["kn_rao_axis_on_the_exact_date"] = s_ax and j_ax
            if "kn_rao_axis_on_the_exact_date" not in b:
                n = h = 0
                for d in events._months(birth + dt.timedelta(days=int(18 * 365.25)), birth + dt.timedelta(days=int(45 * 365.25)), 45):
                    jj = events._jd(d)
                    h += events._covers_axis(c, "Saturn", E.lon(jj, "Saturn")) and events._covers_axis(c, "Jupiter", E.lon(jj, "Jupiter"))
                    n += 1
                b["kn_rao_axis_on_the_exact_date"] = h / n
        tests = [k for k in fired if k != "dasha" and k != "transit"]  # independent-ish summary layers
        ps = [b[k] for k in tests]
        hits = sum(1 for k in tests if fired[k])
        all_ps += ps
        all_hits += hits
        for k in fired:
            pr = per_rule.setdefault(f"{area}: {k}", {"hits": 0, "expected": 0.0, "events": 0})
            pr["hits"] += bool(fired[k])
            pr["expected"] += b[k]
            pr["events"] += 1
        rows.append({"date": ev["date"].isoformat(), "event": ev["label"], "area": area,
                     "dasha": f"{r['md']}-{r['ad']}", "fired": {k: bool(x) for k, x in fired.items()},
                     "base_rates": {k: round(b[k], 2) for k in fired},
                     "hits": hits, "expected_by_chance": round(sum(ps), 2),
                     "chance_of_at_least_these_hits": round(poisson_binomial_tail(ps, hits), 3)})
    for k, pr in per_rule.items():
        pr["expected"] = round(pr["expected"], 2)
        pr["lift"] = round(pr["hits"] / pr["expected"], 2) if pr["expected"] else None
    overall = None
    if all_ps:
        overall = {"hits": all_hits, "expected_by_chance": round(sum(all_ps), 2),
                   "chance_of_at_least_these_hits": round(poisson_binomial_tail(all_ps, all_hits), 3),
                   "reading": None}
        p = overall["chance_of_at_least_these_hits"]
        overall["reading"] = ("the rules fit this chart's past clearly better than chance" if p < 0.05 else
                              "the rules fit this chart's past somewhat better than chance" if p < 0.2 else
                              "the rules do not fit this chart's past better than chance; treat its timing windows lightly "
                              "(or check the birth time)")
    return {"events": rows, "per_rule": per_rule, "overall": overall, "rule_registry": RULE_REGISTRY,
            "method": ("For each dated past event, the summary layers (sign dasha, dasha+transit, KP and, for marriage, "
                       "K.N. Rao's Jupiter-Saturn axis) are checked on the event date and compared with how often each is "
                       "true across this person's adult life. The chance figure is the probability of at least that many "
                       "hits if the rules were unrelated to the events (independent layers assumed, so it is approximate). "
                       "Few events give wide uncertainty: five events is a minimum.")}


# ------------------------------------------------------------------ rectification scoring (PVR 32.3 order)
def chart_at(jd, birth_utc, lat, lon, naive, utc_off, ayan="lahiri", node="mean"):
    import rasidasa
    v = vedic.build_vedic(jd, birth_utc, birth_utc, lat, lon, naive, utc_off, ayan, node)
    vs = {n: {p: SIGNS.index(sg) for p, sg in v["divisional_charts"][f"D{n}"].items() if p != "Lagna"} for n in (9, 10, 4)}
    rd = rasidasa.build(v["planets"], vs, v["_lag_sign"], v["lagna"]["lon"], jd, birth_utc, birth_utc, lat, lon,
                        vedic.AYAN[ayan], "reliable")
    vo = {"rasi_dashas": rd, "jaimini": v["jaimini"]}
    return v, vo


def score_segments(base_jd, base_utc, naive, utc_off, lat, lon, segments, evlist, gender, ayan="lahiri", node="mean"):
    """Chance probability of the past-event hits for each candidate birth-time segment."""
    out = []
    for sg in segments:
        mid = (sg["minutes_from_recorded"][0] + sg["minutes_from_recorded"][1]) / 2.0
        jd = base_jd + mid / 1440.0
        bu = base_utc + dt.timedelta(minutes=mid)
        v, vo = chart_at(jd, bu, lat, lon, naive + dt.timedelta(minutes=mid), utc_off, ayan, node)
        kp = vedic.kp_block(jd, lat, lon)
        v["kp"] = kp
        kpd = events.kp_events(kp, v, jd, lat, lon)
        cal = calibrate(v, vo, evlist, jd, bu, lat, lon, gender, ayan, node, kp=kpd)
        o = cal["overall"] or {}
        out.append({**{k: sg[k] for k in sg if k != "events"}, "hits": o.get("hits"), "expected_by_chance": o.get("expected_by_chance"),
                    "chance_of_at_least_these_hits": o.get("chance_of_at_least_these_hits")})
    ranked = sorted([x for x in out if x["chance_of_at_least_these_hits"] is not None],
                    key=lambda x: x["chance_of_at_least_these_hits"])
    for i, x in enumerate(ranked):
        x["rank"] = i + 1
    return out
