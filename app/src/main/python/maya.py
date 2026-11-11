"""maya.py - the Maya calendar of the birth date (v23): Long Count, Tzolk'in day sign and number, Haab' date and the
Lord of the Night, using the GMT correlation (JDN 584283 = 13.0.0.0.0 4 Ajaw 8 Kumk'u). Pure arithmetic, checked against
13.0.0.0.0 = 21 December 2012. Day-sign keywords are the common modern ones and are shown as a cultural note only.
"""
import datetime as dt

from app_details import bi, table

GMT = 584283
SIGNS = [("Imix", "इमिश", "water lily, beginnings", "आरंभ"), ("Ik'", "इक", "wind, communication", "वायु, संवाद"),
         ("Ak'b'al", "अकबाल", "night, inner life", "रात्रि, भीतरी जीवन"), ("K'an", "कान", "seed, growth", "बीज, विकास"),
         ("Chikchan", "चिकचान", "serpent, life force", "सर्प, जीवन शक्ति"), ("Kimi", "किमी", "change and letting go", "परिवर्तन और छोड़ना"),
         ("Manik'", "मानिक", "deer, healing hands", "हिरण, सेवा"), ("Lamat", "लामात", "star, harmony", "तारा, सामंजस्य"),
         ("Muluk", "मुलुक", "water, feeling", "जल, भावना"), ("Ok", "ओक", "dog, loyalty", "श्वान, निष्ठा"),
         ("Chuwen", "चुवेन", "monkey, play and craft", "वानर, खेल और कला"), ("Eb'", "एब", "road, the path", "मार्ग"),
         ("B'en", "बेन", "reed, home and growth", "सरकंडा, घर और विकास"), ("Ix", "इश", "jaguar, the earth", "जगुआर, धरती"),
         ("Men", "मेन", "eagle, vision", "गरुड़, दृष्टि"), ("Kib'", "किब", "owl, wisdom", "उल्लू, विवेक"),
         ("Kab'an", "काबान", "earth, thought", "पृथ्वी, विचार"), ("Etz'nab'", "एत्ज़नाब", "flint, clarity", "चकमक, स्पष्टता"),
         ("Kawak", "कावाक", "storm, renewal", "तूफ़ान, नवीनीकरण"), ("Ajaw", "अजाव", "sun, leadership", "सूर्य, नेतृत्व")]
MONTHS = [("Pop", "पोप"), ("Wo'", "वो"), ("Sip", "सिप"), ("Sotz'", "सोत्ज़"), ("Sek", "सेक"), ("Xul", "शुल"), ("Yaxk'in", "याशकिन"),
          ("Mol", "मोल"), ("Ch'en", "चेन"), ("Yax", "याश"), ("Sak'", "साक"), ("Keh", "केह"), ("Mak", "माक"), ("K'ank'in", "कानकिन"),
          ("Muwan", "मुवान"), ("Pax", "पाश"), ("K'ayab'", "कायाब"), ("Kumk'u", "कुमकू"), ("Wayeb'", "वायेब")]


def jdn(d):
    return d.toordinal() + 1721425


def maya(d):
    n = jdn(d) - GMT
    lc, r = [], n
    for unit in (144000, 7200, 360, 20, 1):
        lc.append(r // unit)
        r %= unit
    tz_num = (n + 3) % 13 + 1
    tz_sign = (n + 19) % 20
    h = (n + 348) % 365
    night = (n + 8) % 9 + 1          # G9 on 13.0.0.0.0
    return {"long_count": ".".join(map(str, lc)), "tz_num": tz_num, "tz_sign": tz_sign, "haab_day": h % 20, "haab_month": h // 20,
            "night": night}


def section(date_iso):
    m = maya(dt.date.fromisoformat(date_iso))
    s = SIGNS[m["tz_sign"]]
    mo = MONTHS[m["haab_month"]]
    return {"key": "maya", "title": bi("Maya calendar", "माया पंचांग"),
            "intro": bi(f"Your Tzolk'in day is {m['tz_num']} {s[0]}: {s[2]}.", f"आपका त्ज़ोल्किन दिन {m['tz_num']} {s[1]} है: {s[3]}।"),
            "blocks": [table([bi("Item", "विवरण"), bi("Value", "मान")], [
                [bi("Long Count", "लंबी गणना"), bi(m["long_count"])],
                [bi("Tzolk'in (260-day count)", "त्ज़ोल्किन (260 दिन)"), bi(f"{m['tz_num']} {s[0]}", f"{m['tz_num']} {s[1]}")],
                [bi("Haab' (365-day year)", "हाब (365 दिन)"), bi(f"{m['haab_day']} {mo[0]}", f"{m['haab_day']} {mo[1]}")],
                [bi("Lord of the Night", "रात्रि स्वामी"), bi(f"G{m['night']}")]])],
            "note": bi("GMT correlation 584283 (13.0.0.0.0 = 21 December 2012). Day-sign keywords are a modern cultural note, not a reading.",
                       "GMT सहसंबंध 584283 (13.0.0.0.0 = 21 दिसंबर 2012)। दिन-चिह्न के शब्द एक आधुनिक सांस्कृतिक टिप्पणी हैं, फलादेश नहीं।")}
