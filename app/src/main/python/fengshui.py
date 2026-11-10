"""fengshui.py - Xuan Kong Flying Stars (玄空飞星) (v19): the year's and the month's stars over the nine sectors, and the
natal star chart of a building from its facing direction and its period.

Rules:
* The Lo Shu flight path from the centre: NW, W, NE, S, N, SW, E, SE (forward); a reverse flight subtracts.
* The year's centre star is the Nine Star Ki year star (the year from Li Chun); the month's is the month star.
* Periods of 20 years from 1864: Period 8 is Feb 2004 - Feb 2024, Period 9 is Feb 2024 - Feb 2044.
* House chart: the period number sits in the centre and flies forward. The period chart's stars in the facing and the
  sitting sectors go to the centre as the water (facing) and mountain (sitting) stars. Each flies forward if the
  facing or sitting mountain is yang for that star's home sector, else in reverse. Cardinal sectors (N, S, E, W) run
  yang-yin-yin over their three mountains, the corner sectors yin-yang-yang; a 5 takes the period number's sector.
* Not applied: replacement charts (替卦) near mountain boundaries; the page warns within 3 degrees of a boundary.
"""
import datetime as dt
import json

import chinese_more as CM

ORDER = ["C", "NW", "W", "NE", "S", "N", "SW", "E", "SE"]
HOME = {1: "N", 2: "SW", 3: "E", 4: "SE", 6: "NW", 7: "W", 8: "NE", 9: "S"}
CARDINAL = {"N", "S", "E", "W"}
SECTOR = {"N": ("North", "उत्तर"), "NE": ("North-east", "उत्तर-पूर्व"), "E": ("East", "पूर्व"), "SE": ("South-east", "दक्षिण-पूर्व"),
          "S": ("South", "दक्षिण"), "SW": ("South-west", "दक्षिण-पश्चिम"), "W": ("West", "पश्चिम"), "NW": ("North-west", "उत्तर-पश्चिम"),
          "C": ("Centre", "मध्य")}
MOUNTAINS = ["子", "癸", "丑", "艮", "寅", "甲", "卯", "乙", "辰", "巽", "巳", "丙", "午", "丁", "未", "坤", "申", "庚", "酉", "辛", "戌", "乾", "亥", "壬"]
STARS = {
    1: ("1 White", "1 श्वेत", "good", "career and new opportunities", "करियर और नए अवसर"),
    2: ("2 Black", "2 कृष्ण", "care", "low energy: keep this area quiet and tidy", "कम ऊर्जा: इस क्षेत्र को शांत और साफ़ रखें"),
    3: ("3 Jade", "3 हरित", "care", "arguments: avoid holding meetings or disputes here", "विवाद: यहाँ बैठकें या बहस न रखें"),
    4: ("4 Green", "4 हरा", "good", "study, writing and romance", "पढ़ाई, लेखन और प्रेम"),
    5: ("5 Yellow", "5 पीला", "care", "obstacles: avoid renovation and noise here this period", "बाधाएँ: इस अवधि में यहाँ तोड़-फोड़ और शोर से बचें"),
    6: ("6 White", "6 श्वेत", "good", "authority and help from mentors", "अधिकार और मार्गदर्शकों की सहायता"),
    7: ("7 Red", "7 लाल", "care", "caution with money and security", "धन और सुरक्षा में सावधानी"),
    8: ("8 White", "8 श्वेत", "good", "steady wealth and property", "स्थिर धन और संपत्ति"),
    9: ("9 Purple", "9 बैंगनी", "good", "celebration and recognition; the star of the current period", "उत्सव और पहचान; वर्तमान अवधि का तारा"),
}


def fly(center, forward=True):
    out = {}
    for i, sec in enumerate(ORDER):
        n = (center + i - 1) % 9 + 1 if forward else (center - i - 1) % 9 + 1
        out[sec] = n
    return out


def period_of(year):
    return (year - 1864) // 20 + 1 if year >= 1864 else 1


def mountain(deg):
    """24-mountain index (0 = 子 at 352.5-7.5) and its sector and position (1-3) in the sector."""
    i = int(((deg + 7.5) % 360) // 15)
    sec = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"][int(((deg + 22.5) % 360) // 45)]
    first = {"N": 23, "NE": 2, "E": 5, "SE": 8, "S": 11, "SW": 14, "W": 17, "NW": 20}[sec]
    pos = (i - first) % 24 + 1
    edge = min(abs(((deg - (j * 15 - 7.5)) + 180) % 360 - 180) for j in range(24))
    return i, sec, pos, edge


def _forward(star, pos, period):
    sec = HOME.get(star) or HOME.get(period, "N")
    yang = (pos == 1) if sec in CARDINAL else (pos in (2, 3))
    return yang


def house_chart(facing_deg, built_year):
    period = period_of(built_year)
    base = fly(period)
    fi, fsec, fpos, edge = mountain(facing_deg)
    si, ssec, spos, _ = mountain((facing_deg + 180) % 360)
    water_c, mount_c = base[fsec], base[ssec]
    water = fly(water_c, _forward(water_c, fpos, period))
    mount = fly(mount_c, _forward(mount_c, spos, period))
    return {"period": period, "facing": {"sector": fsec, "mountain": MOUNTAINS[fi], "degrees": round(facing_deg % 360, 1)},
            "sitting": {"sector": ssec, "mountain": MOUNTAINS[si]}, "base": base, "water": water, "mountain": mount,
            "near_boundary": edge < 3}


def year_month(on_date, tz_hours=8.0):
    ns = CM.nine_star(on_date, tz_hours)
    return {"year": fly(ns["year_star"]), "month": fly(ns["month_star"]), "year_star": ns["year_star"], "month_star": ns["month_star"]}


def bi(en, hi=None):
    return {"en": en, "hi": en if hi is None else hi}


def sections(on_iso, facing_deg=None, built_year=None, tz_hours=8.0):
    from app_details import table, para
    d = dt.date.fromisoformat(on_iso)
    ym = year_month(d, tz_hours)
    rows = []
    for sec in ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "C"]:
        y, m = ym["year"][sec], ym["month"][sec]
        rows.append([bi(*SECTOR[sec]), bi(STARS[y][0], STARS[y][1]), bi(STARS[m][0], STARS[m][1]), bi(STARS[y][3], STARS[y][4])])
    out = [{"key": "fs_year", "title": bi(f"Flying stars for {d.year}", f"{d.year} के उड़ते तारे"),
            "intro": bi(f"This year's centre star is {STARS[ym['year_star']][0]}, this month's {STARS[ym['month_star']][0]}.",
                        f"इस वर्ष का केंद्रीय तारा {STARS[ym['year_star']][1]}, इस माह का {STARS[ym['month_star']][1]}।"),
            "blocks": [table([bi("Sector", "दिशा"), bi("Year star", "वर्ष तारा"), bi("Month star", "माह तारा"), bi("This year", "इस वर्ष")], rows)],
            "note": bi("Use the good sectors (1, 4, 6, 8, 9) for the desk, the bed or the entrance; keep 2 and 5 quiet and avoid renovation there. "
                       "Traditional practice places metal (a brass bell or wind chime) on 2 and 5; it is optional.",
                       "अच्छी दिशाएँ (1, 4, 6, 8, 9) मेज़, पलंग या प्रवेश के लिए उपयोग करें; 2 और 5 को शांत रखें और वहाँ तोड़-फोड़ से बचें। "
                       "परंपरा में 2 और 5 पर धातु (पीतल की घंटी या विंड चाइम) रखी जाती है; यह वैकल्पिक है।")}]
    if facing_deg is not None and built_year:
        h = house_chart(float(facing_deg), int(built_year))
        p = h["period"]
        rows = []
        for sec in ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "C"]:
            mo, wa, ba = h["mountain"][sec], h["water"][sec], h["base"][sec]
            tag = []
            if wa in (p, p % 9 + 1, 1) and sec != "C":
                tag.append(("good for activity and income (water star)", "गतिविधि और आय के लिए अच्छा (जल तारा)"))
            if mo in (p, p % 9 + 1, 8) and sec != "C":
                tag.append(("good for rest and relationships (mountain star)", "विश्राम और संबंधों के लिए अच्छा (पर्वत तारा)"))
            rows.append([bi(*SECTOR[sec]), bi(f"{mo}–{wa} ({ba})"), bi("; ".join(t[0] for t in tag) or "–", "; ".join(t[1] for t in tag) or "–")])
        fs, ss = SECTOR[h["facing"]["sector"]], SECTOR[h["sitting"]["sector"]]
        special = []
        if h["water"][h["facing"]["sector"]] == p and h["mountain"][h["sitting"]["sector"]] == p:
            special = [bi("The period star sits at both the facing and the sitting side (旺山旺向): a well-timed house.", "अवधि का तारा आगे और पीछे दोनों ओर (旺山旺向): समय के अनुकूल घर।")]
        elif h["water"][h["facing"]["sector"]] == p and h["mountain"][h["facing"]["sector"]] == p:
            special = [bi("Both period stars meet at the facing side (双星会向): keep the front open and active.", "दोनों अवधि तारे सामने मिलते हैं (双星会向): सामने का भाग खुला और सक्रिय रखें।")]
        elif h["water"][h["sitting"]["sector"]] == p and h["mountain"][h["sitting"]["sector"]] == p:
            special = [bi("Both period stars meet at the sitting side (双星会坐): the back of the home matters most.", "दोनों अवधि तारे पीछे मिलते हैं (双星会坐): घर का पिछला भाग सबसे महत्वपूर्ण है।")]
        blocks = [table([bi("Sector", "दिशा"), bi("Mountain–water (base)", "पर्वत–जल (आधार)"), bi("Use", "उपयोग")], rows)] + [para(x) for x in special]
        if h["near_boundary"]:
            blocks.append(para(bi("The facing direction is within 3° of a mountain boundary; a replacement chart may apply, so check the compass reading.",
                                  "सामने की दिशा पर्वत सीमा से 3° के भीतर है; प्रतिस्थापन चार्ट लागू हो सकता है, इसलिए कंपास दोबारा देखें।")))
        out.append({"key": "fs_house", "title": bi(f"Your home's star chart (Period {p})", f"आपके घर का तारा चार्ट (अवधि {p})"),
                    "intro": bi(f"Facing {fs[0]} ({h['facing']['mountain']}, {h['facing']['degrees']}°), sitting {ss[0]} ({h['sitting']['mountain']}).",
                                f"सामने {fs[1]} ({h['facing']['mountain']}, {h['facing']['degrees']}°), पीछे {ss[1]} ({h['sitting']['mountain']})।"),
                    "blocks": blocks,
                    "note": bi("Each cell gives mountain star, water star and the period base star. A practitioner also weighs the real layout and landforms.",
                               "हर पंक्ति में पर्वत तारा, जल तारा और अवधि का आधार तारा। जानकार वास्तविक नक्शा और आसपास का परिवेश भी देखते हैं।")})
    return out


def sections_json(request_json):
    r = json.loads(request_json)
    return json.dumps({"sections": sections(r.get("today") or dt.date.today().isoformat(), r.get("facing"), r.get("built_year"),
                                            float(r.get("tz_hours", 8.0)))}, ensure_ascii=False)
