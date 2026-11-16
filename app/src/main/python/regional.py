"""regional.py - v27: the regional almanacs and the name systems the app did not cover.

Regional eras and year names beside the Vikram and Shaka years the panchang already gives: the Tamil, Malayalam
(Kollam), Bengali and Nepali eras, and the sixty-year Jovian year name used across the south. Then the numerology
schools side by side, and the Katapayadi value of a name written in Devanagari.

Era rules: Kollam = CE - 824 from Chingam (Sun into Leo); Bengali San = CE - 593 from Boishakh (Sun into Aries);
Tamil and Nepali years start at the same Mesha sankranti; the Jovian name runs from Prabhava in 1987-88.
"""
import datetime as dt

import swisseph as swe

from app_details import bi, para, table

JOVIAN = ["Prabhava", "Vibhava", "Shukla", "Pramoduta", "Prajapati", "Angirasa", "Shrimukha", "Bhava", "Yuva", "Dhata",
          "Ishvara", "Bahudhanya", "Pramathi", "Vikrama", "Vrisha", "Chitrabhanu", "Svabhanu", "Tarana", "Parthiva", "Vyaya",
          "Sarvajit", "Sarvadhari", "Virodhi", "Vikriti", "Khara", "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukhi",
          "Hevilambi", "Vilambi", "Vikari", "Sharvari", "Plava", "Shubhakrit", "Shobhakrit", "Krodhi", "Vishvavasu", "Parabhava",
          "Plavanga", "Kilaka", "Saumya", "Sadharana", "Virodhikrit", "Paridhavi", "Pramadicha", "Ananda", "Rakshasa", "Nala",
          "Pingala", "Kalayukti", "Siddharthi", "Raudra", "Durmati", "Dundubhi", "Rudhirodgari", "Raktakshi", "Krodhana", "Akshaya"]
JOVIAN_HI = ["प्रभव", "विभव", "शुक्ल", "प्रमोदूत", "प्रजापति", "आंगिरस", "श्रीमुख", "भाव", "युव", "धाता",
             "ईश्वर", "बहुधान्य", "प्रमाथी", "विक्रम", "वृष", "चित्रभानु", "स्वभानु", "तारण", "पार्थिव", "व्यय",
             "सर्वजित", "सर्वधारी", "विरोधी", "विकृति", "खर", "नंदन", "विजय", "जय", "मन्मथ", "दुर्मुखी",
             "हेविलंबी", "विलंबी", "विकारी", "शार्वरी", "प्लव", "शुभकृत", "शोभकृत", "क्रोधी", "विश्ववसु", "पराभव",
             "प्लवंग", "कीलक", "सौम्य", "साधारण", "विरोधीकृत", "परिधावी", "प्रमादीच", "आनंद", "राक्षस", "नल",
             "पिंगल", "कालयुक्ति", "सिद्धार्थी", "रौद्र", "दुर्मति", "दुंदुभि", "रुधिरोद्गारी", "रक्ताक्षी", "क्रोधन", "अक्षय"]
TAMIL_MONTH = [("Chithirai", "चित्तिरै"), ("Vaikasi", "वैकासि"), ("Aani", "आनि"), ("Aadi", "आडि"), ("Aavani", "आवणि"),
               ("Purattasi", "पुरट्टासि"), ("Aippasi", "ऐप्पसि"), ("Karthigai", "कार्तिगै"), ("Margazhi", "मार्गऴि"),
               ("Thai", "तै"), ("Maasi", "मासि"), ("Panguni", "पंगुनि")]
MALAYALAM_MONTH = [("Medam", "मेडम"), ("Edavam", "एडवम"), ("Midhunam", "मिथुनम"), ("Karkidakam", "कर्किडकम"), ("Chingam", "चिंगम"),
                   ("Kanni", "कन्नि"), ("Thulam", "तुलम"), ("Vrischikam", "वृश्चिकम"), ("Dhanu", "धनु"), ("Makaram", "मकरम"),
                   ("Kumbham", "कुंभम"), ("Meenam", "मीनम")]
BENGALI_MONTH = [("Boishakh", "बोइशाख"), ("Jyoishtho", "ज्यैष्ठ"), ("Asharh", "आषाढ़"), ("Shrabon", "श्रावण"), ("Bhadro", "भाद्र"),
                 ("Ashwin", "आश्विन"), ("Kartik", "कार्तिक"), ("Ogrohayon", "अग्रहायण"), ("Poush", "पौष"), ("Magh", "माघ"),
                 ("Falgun", "फाल्गुन"), ("Choitro", "चैत्र")]
# Katapayadi: the classical Sanskrit letter-to-number table (ka-ta-pa-ya rows, na and nya zero).
KATAPAYADI = {}
for _row, _start in ((["क", "ख", "ग", "घ", "ङ", "च", "छ", "ज", "झ", "ञ"], 1),
                     (["ट", "ठ", "ड", "ढ", "ण", "त", "थ", "द", "ध", "न"], 1),
                     (["प", "फ", "ब", "भ", "म"], 1),
                     (["य", "र", "ल", "व", "श", "ष", "स", "ह"], 1)):
    for _i, _ch in enumerate(_row):
        KATAPAYADI[_ch] = (_start + _i) % 10
KATAPAYADI["ङ"] = 0
KATAPAYADI["ञ"] = 0
KATAPAYADI["न"] = 0
CHALDEAN = {**{c: v for v, grp in enumerate(["AIJQY", "BKR", "CGLS", "DMT", "EHNX", "UVW", "OZ"], 1) for c in grp}}
PYTHAG = {chr(65 + i): (i % 9) + 1 for i in range(26)}
# Kabbalah name numerology: the Hebrew-letter method reduced modulo 22, as used in the Western Kabbalistic school.
KABBALAH_MOD = 22
MONTH_HI = ["जन", "फ़र", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अग", "सित", "अक्टू", "नव", "दिस"]


def _sun_sign_index(jd):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    lon = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0]
    return int(lon // 30)


def eras(c):
    """The regional year and month for the birth date, from the Sun's sidereal sign."""
    t = c["time_pipeline"]
    jd = t["jd_ut"]
    d = dt.date.fromisoformat(t["local_civil"][:10])
    si = _sun_sign_index(jd)                      # 0 = Mesha; the solar months of the south start here
    y = d.year
    # a solar year that starts at Mesha sankranti (mid-April): before it, the year number is one less
    solar_year = y if si >= 0 and (d.month > 4 or (d.month == 4 and d.day >= 14)) else y - 1
    kollam = y - 824 if (d.month > 8 or (d.month == 8 and d.day >= 17)) else y - 825
    bengali = solar_year - 593
    nepali = solar_year + 57                      # Bikram Sambat as used in Nepal, from the Baisakh new year
    jov = (solar_year - 1987) % 60
    rows = [[bi("Tamil year", "तमिल वर्ष"), bi(f"{JOVIAN[jov]} ({solar_year}–{str(solar_year + 1)[-2:]})",
                                                 f"{JOVIAN_HI[jov]} ({solar_year}–{str(solar_year + 1)[-2:]})")],
            [bi("Tamil month", "तमिल माह"), bi(*TAMIL_MONTH[si])],
            [bi("Malayalam era (Kollam)", "मलयालम संवत् (कोल्लम)"), bi(f"ME {kollam}", f"कोल्लम {kollam}")],
            [bi("Malayalam month", "मलयालम माह"), bi(*MALAYALAM_MONTH[si])],
            [bi("Bengali San", "बंगाब्द"), bi(f"BS {bengali}", f"बंगाब्द {bengali}")],
            [bi("Bengali month", "बंगाली माह"), bi(*BENGALI_MONTH[si])],
            [bi("Nepali Bikram Sambat", "नेपाली विक्रम संवत्"), bi(f"BS {nepali}", f"वि.सं. {nepali}")]]
    return {"key": "regional_eras", "title": bi("Regional almanacs", "क्षेत्रीय पंचांग"),
            "intro": bi("The same birth date in the solar almanacs of the south and east, beside the Vikram and Shaka years in the panchang.",
                        "वही जन्म तिथि दक्षिण और पूर्व के सौर पंचांगों में, पंचांग के विक्रम और शक वर्षों के साथ।"),
            "blocks": [table([bi("Almanac", "पंचांग"), bi("Value", "मान")], rows)],
            "note": bi("Solar months run from each sankranti (the Sun entering a sidereal sign) with the Lahiri ayanamsa. "
                       "The sixty-year Jovian name runs from Prabhava in 1987-88. Local practice can differ by a day at the turn.",
                       "सौर माह हर संक्रांति (सूर्य का निरयण राशि में प्रवेश) से चलते हैं, लाहिड़ी अयनांश के साथ। "
                       "साठ वर्ष का बार्हस्पत्य नाम 1987-88 के प्रभव से चलता है। मोड़ पर स्थानीय प्रथा एक दिन भिन्न हो सकती है।")}


def _reduce(n, keep_master=True):
    while n > 9 and not (keep_master and n in (11, 22, 33)):
        n = sum(int(ch) for ch in str(n))
    return n


def name_schools(c):
    name = (c["meta"].get("name") or "").upper()
    letters = [ch for ch in name if ch.isalpha() and ch in PYTHAG]
    if not letters:
        return None
    py = _reduce(sum(PYTHAG[ch] for ch in letters))
    ch_total = sum(CHALDEAN.get(ch, 0) for ch in letters)
    cha = _reduce(ch_total, keep_master=False)
    kab = (sum(PYTHAG[ch] for ch in letters) % KABBALAH_MOD) or KABBALAH_MOD
    vowels = [ch for ch in letters if ch in "AEIOU"]
    soul = _reduce(sum(PYTHAG[ch] for ch in vowels)) if vowels else 0
    rows = [[bi("Pythagorean (A=1…I=9, repeating)", "पाइथागोरस (A=1…I=9, दोहराव)"), bi(str(py))],
            [bi("Chaldean (compound kept)", "कैल्डियन (यौगिक रखा जाता है)"), bi(f"{ch_total} → {cha}")],
            [bi("Kabbalah (name total modulo 22)", "कबाला (नाम योग, 22 का शेष)"), bi(str(kab))],
            [bi("Soul number (vowels only)", "आत्मा अंक (केवल स्वर)"), bi(str(soul))]]
    return {"key": "num_schools", "title": bi("Numerology: the schools side by side", "अंक ज्योतिष: पद्धतियाँ साथ-साथ"),
            "blocks": [table([bi("School", "पद्धति"), bi("Number for this name", "इस नाम का अंक")], rows)],
            "note": bi("The same letters counted by four different tables. They disagree by design; the Indian system in the report uses the birth date, not the name.",
                       "वही अक्षर चार अलग तालिकाओं से गिने गए। ये जान-बूझकर अलग हैं; रिपोर्ट की भारतीय पद्धति नाम नहीं, जन्म तिथि लेती है।")}


def katapayadi(name_devanagari):
    """The classical Katapayadi value of a name written in Devanagari: consonants only, read left to right."""
    digits = [KATAPAYADI[ch] for ch in name_devanagari if ch in KATAPAYADI]
    if not digits:
        return None
    total = sum(digits)
    return {"digits": digits, "total": total, "reduced": _reduce(total)}


def devanagari_name(name_devanagari):
    k = katapayadi(name_devanagari)
    if not k:
        return None
    return {"key": "num_devanagari", "title": bi("Devanagari name by Katapayadi", "देवनागरी नाम: कटपयादि से"),
            "intro": bi(f"{name_devanagari}: the consonants give {'+'.join(str(d) for d in k['digits'])} = {k['total']}, which reduces to {k['reduced']}.",
                        f"{name_devanagari}: व्यंजनों से {'+'.join(str(d) for d in k['digits'])} = {k['total']}, जो घटकर {k['reduced']} होता है।"),
            "blocks": [para(bi("Katapayadi counts consonants only: ka-ta-pa-ya rows give 1 to 9, and na, nya and nga give nothing.",
                               "कटपयादि केवल व्यंजन गिनता है: क-ट-प-य वर्ग 1 से 9 देते हैं, और न, ञ, ङ शून्य देते हैं।"))],
            "note": bi("The classical Sanskrit letter-number table, used in verse to record numbers. Vowels are not counted.",
                       "संस्कृत की शास्त्रीय अक्षर-अंक तालिका, जो श्लोकों में संख्याएँ रखने के लिए प्रयुक्त होती थी। स्वर नहीं गिने जाते।")}


def build(c):
    out = []
    for f in (eras, name_schools):
        try:
            r = f(c)
        except Exception:
            r = None
        if r:
            out.append(r)
    nm = c["meta"].get("name") or ""
    if any("ऀ" <= ch <= "ॿ" for ch in nm):
        try:
            r = devanagari_name(nm)
            if r:
                out.append(r)
        except Exception:
            pass
    return out
