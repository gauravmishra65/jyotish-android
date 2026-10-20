"""lalkitab_data.py - tables and texts taken from Lal Kitab (Pt. Roop Chand Joshi, 1952 edition, Farman 1-15).

Every table below cites the book page (printed page number, not PDF page). Readings and upay are condensed
from the planet-in-house chapters (book pp. 235-739). Remedies are given as the book gives them; the report
must present them as traditional practice with no promised outcome (SKILL.md Step 8 / Step 7c).
"""

PLANETS = ["Jupiter", "Sun", "Moon", "Venus", "Mars", "Mercury", "Saturn", "Rahu", "Ketu"]
HI = {"Jupiter": "बृहस्पति", "Sun": "सूर्य", "Moon": "चंद्र", "Venus": "शुक्र", "Mars": "मंगल", "Mercury": "बुध",
      "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु"}

# p.51 table "ग्रह व राशि का बाहमी ताल्लुक" - fixed houses (house n = sign n in Lal Kitab)
HOUSE_LORD = {1: ["Mars"], 2: ["Venus"], 3: ["Mercury"], 4: ["Moon"], 5: ["Sun"], 6: ["Mercury", "Ketu"], 7: ["Venus"],
              8: ["Mars"], 9: ["Jupiter"], 10: ["Saturn"], 11: ["Saturn"], 12: ["Jupiter", "Rahu"]}
UCHCH = {1: ["Sun"], 2: ["Moon"], 3: ["Rahu"], 4: ["Jupiter"], 5: [], 6: ["Mercury", "Rahu"], 7: ["Saturn"], 8: [],
         9: ["Ketu"], 10: ["Mars"], 11: [], 12: ["Venus", "Rahu"]}
NEECH = {1: ["Saturn"], 2: [], 3: ["Ketu"], 4: ["Mars"], 5: [], 6: ["Venus", "Ketu"], 7: ["Sun"], 8: ["Moon"],
         9: ["Rahu"], 10: ["Jupiter"], 11: [], 12: ["Mercury", "Rahu"]}
PAKKA_GHAR_OF_HOUSE = {1: ["Sun"], 2: ["Jupiter"], 3: ["Mars"], 4: ["Moon"], 5: ["Jupiter"], 6: ["Ketu"],
                       7: ["Venus", "Mercury"], 8: ["Mars", "Saturn"], 9: ["Jupiter"], 10: ["Saturn"], 11: ["Jupiter"], 12: ["Rahu"]}
KISMAT_JAGANE_WALA = {1: "Mars", 2: "Moon", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Rahu", 7: "Venus", 8: "Moon",
                      9: "Jupiter", 10: "Saturn", 11: "Jupiter", 12: "Ketu"}          # p.51 and p.98 (same list)
GRAHPHAL = {1: ["Mars"], 2: ["Rahu", "Ketu"], 3: ["Saturn"], 4: ["Moon"], 5: ["Jupiter", "Sun"], 6: ["Mercury", "Ketu"],
            7: ["Venus"], 8: ["Mars"], 9: ["Jupiter"], 10: ["Saturn"], 11: ["Jupiter", "Saturn"], 12: ["Rahu", "Mercury"]}
RASHIPHAL = {1: ["Rahu"], 2: [], 3: ["Saturn"], 4: ["Mars", "Ketu"], 5: ["Venus"], 6: ["Saturn"], 7: ["Sun", "Jupiter", "Rahu"],
             8: [], 9: ["Saturn"], 10: ["Ketu", "Mercury"], 11: [], 12: []}
PAKKA_GHAR = {}
for _h, _ps in PAKKA_GHAR_OF_HOUSE.items():
    for _p in _ps:
        PAKKA_GHAR.setdefault(_p, []).append(_h)

# p.31 "ग्रहों की आपसी मित्रता और शत्रुता"
FRIENDS = {"Jupiter": ["Sun", "Mars", "Moon"], "Sun": ["Jupiter", "Mars", "Moon"], "Moon": ["Sun", "Mercury"],
           "Venus": ["Saturn", "Mercury", "Ketu"], "Mars": ["Sun", "Moon", "Jupiter"], "Mercury": ["Sun", "Venus", "Rahu"],
           "Saturn": ["Mercury", "Venus", "Rahu"], "Rahu": ["Mercury", "Saturn", "Ketu"], "Ketu": ["Venus", "Rahu"]}
ENEMIES = {"Jupiter": ["Venus", "Mercury"], "Sun": ["Venus", "Saturn", "Rahu"], "Moon": ["Ketu"],
           "Venus": ["Sun", "Moon", "Rahu"], "Mars": ["Mercury", "Ketu"], "Mercury": ["Moon"],
           "Saturn": ["Sun", "Moon", "Mars"], "Rahu": ["Sun", "Venus", "Mars"], "Ketu": ["Moon", "Mars"]}
EQUAL = {"Jupiter": ["Rahu", "Ketu", "Saturn"], "Sun": ["Mercury"], "Moon": ["Venus", "Saturn", "Mars", "Jupiter"],
         "Venus": ["Mars", "Jupiter"], "Mars": ["Venus", "Saturn", "Rahu"], "Mercury": ["Saturn", "Ketu", "Mars", "Jupiter"],
         "Saturn": ["Ketu", "Jupiter"], "Rahu": ["Jupiter"], "Ketu": ["Jupiter", "Saturn", "Mercury"]}
FRIENDSHIP_NOTES = ["Sun is eclipsed by Rahu (and dimmed by Ketu); Moon is eclipsed by Ketu (and dimmed by Rahu) - p.31.",
                    "Moon and Venus are equal, but Moon is hostile to Venus; Jupiter and Venus equal, but Venus hostile to Jupiter; "
                    "Mars and Saturn equal, but Mars hostile to Saturn; Moon and Mercury friends, but Moon hostile to Mercury - p.31.",
                    "Jupiter falls silent with Rahu; in house 2 Rahu comes under Jupiter. Mercury or Moon in houses 2 or 4 helps financially "
                    "instead of acting as an enemy - p.31."]

# p.27 "बनावटी (मसनुई) ग्रह" - two planets in one house act like a third
MASNUI = [(("Sun", "Venus"), "Jupiter", ""), (("Mercury", "Venus"), "Sun", ""), (("Sun", "Jupiter"), "Moon", ""),
          (("Rahu", "Ketu"), "Venus", ""), (("Sun", "Mercury"), "Mars", "nek (benefic)"), (("Sun", "Saturn"), "Mars", "bad (malefic)"),
          (("Jupiter", "Rahu"), "Mercury", ""), (("Venus", "Jupiter"), "Saturn", "Ketu-natured"),
          (("Mercury", "Mars"), "Saturn", "Rahu-natured"), (("Mars", "Saturn"), "Rahu", "exalted state"),
          (("Sun", "Saturn"), "Rahu", "debilitated state"), (("Venus", "Saturn"), "Ketu", "exalted state"),
          (("Moon", "Saturn"), "Ketu", "debilitated state")]

# p.27 colours, p.30 day timings, p.156 deity / donation table
PLANET_INFO = {
    "Jupiter": {"colour": "yellow", "deity": "Brahma ji", "kind": "male", "items": "chana dal, gold, saffron, turmeric", "day": "Thursday"},
    "Sun": {"colour": "copper red / wheat brown", "deity": "Vishnu ji", "kind": "male", "items": "wheat, jaggery, copper", "day": "Sunday"},
    "Moon": {"colour": "milk white", "deity": "Shiv ji", "kind": "female", "items": "rice, milk, silver", "day": "Monday"},
    "Venus": {"colour": "curd white", "deity": "Lakshmi ji", "kind": "female", "items": "ghee, curd, camphor, white pearl", "day": "Friday"},
    "Mars": {"colour": "blood red", "deity": "Hanuman ji", "kind": "male", "items": "masoor dal (red lentil), honey, sweets", "day": "Tuesday"},
    "Mercury": {"colour": "green", "deity": "Durga ji", "kind": "neuter", "items": "whole moong, green items", "day": "Wednesday"},
    "Saturn": {"colour": "black", "deity": "Bhairon ji", "kind": "papi (malefic)", "items": "whole urad, iron, mustard oil", "day": "Saturday"},
    "Rahu": {"colour": "blue", "deity": "Saraswati ji", "kind": "papi (malefic)", "items": "mustard seed, sapphire (neelam), coal, radish", "day": "Thursday evening"},
    "Ketu": {"colour": "two-coloured (black and white)", "deity": "Shri Ganesh ji", "kind": "papi (malefic)", "items": "sesame, two-coloured blanket", "day": "Sunday dawn"},
}
PLANET_INFO_HI = {
    "Jupiter": {"colour": "पीला", "deity": "ब्रह्मा जी", "items": "चने की दाल, सोना, केसर, हल्दी"},
    "Sun": {"colour": "तांबई / गेहुँआ", "deity": "विष्णु जी", "items": "गेहूँ, गुड़, तांबा"},
    "Moon": {"colour": "दूधिया सफ़ेद", "deity": "शिव जी", "items": "चावल, दूध, चांदी"},
    "Venus": {"colour": "दही जैसा सफ़ेद", "deity": "लक्ष्मी जी", "items": "घी, दही, कपूर, सफ़ेद मोती"},
    "Mars": {"colour": "खूनी लाल", "deity": "हनुमान जी", "items": "मसूर की दाल, शहद, मिठाई"},
    "Mercury": {"colour": "हरा", "deity": "दुर्गा जी", "items": "साबुत मूंग, हरी चीज़ें"},
    "Saturn": {"colour": "काला", "deity": "भैरों जी", "items": "साबुत उड़द, लोहा, सरसों का तेल"},
    "Rahu": {"colour": "नीला", "deity": "सरस्वती जी", "items": "सरसों, नीलम, कोयला, मूली"},
    "Ketu": {"colour": "चितकबरा (काला-सफ़ेद)", "deity": "श्री गणेश जी", "items": "तिल, दोरंगा कंबल"},
}

# p.33 / p.142 planet periods. "awake_age" = age at which a sleeping planet wakes by itself (p.99)
PLANET_YEARS = {"Jupiter": 16, "Sun": 22, "Moon": 24, "Venus": 25, "Mars": 28, "Mercury": 34, "Saturn": 36, "Rahu": 42, "Ketu": 48}
AWAKE = {  # p.99 "सोया ग्रह कब खुद ब खुद जाग पड़ेगा": trigger, age, bad-effect years
    "Jupiter": ("starting own work or business", 16, "6th or 22nd year"),
    "Sun": ("government service or job", 22, "2nd or 24th year"),
    "Moon": ("education", 24, "1st or 25th year"),
    "Venus": ("marriage", 25, "3rd or 28th year"),
    "Mars": ("tie with a woman (marriage)", 28, "6th or 34th year"),
    "Mercury": ("trade, or a sister's or daughter's marriage", 34, "2nd or 36th year"),
    "Saturn": ("building a house", 36, "6th or 42nd year"),
    "Rahu": ("ties with in-laws", 42, "2nd or 48th year"),
    "Ketu": ("birth of a son", 48, "3rd or 51st year"),
}
AWAKE_HI = {"Jupiter": "अपना काम-कारोबार शुरू होना", "Sun": "सरकारी नौकरी या मुलाज़मत", "Moon": "तालीम",
            "Venus": "शादी", "Mars": "औरत से ताल्लुक (शादी)", "Mercury": "व्यापार, बहन या लड़की की शादी",
            "Saturn": "मकान बनना", "Rahu": "ससुराल से ताल्लुक", "Ketu": "लड़के का जन्म"}

# p.215 the 35-year cycle (grah daura): from age 8 Jupiter 6, Sun 2, Moon 1, Venus 3, Mars 6, Mercury 2, Saturn 6,
# Rahu 6, Ketu 3; ages 1-4 run Rahu and 5-7 run Ketu (the tail of the previous cycle).
CYCLE = [("Jupiter", 6), ("Sun", 2), ("Moon", 1), ("Venus", 3), ("Mars", 6), ("Mercury", 2), ("Saturn", 6), ("Rahu", 6), ("Ketu", 3)]

# p.102-107 grah drishti (house to house); strength in percent
DRISHTI = {1: [(7, 100)], 4: [(10, 100)], 3: [(9, 50), (11, 50)], 5: [(9, 50)], 2: [(6, 25)], 6: [(12, 25)], 8: [(2, 25)]}

# p.112 yoga drishti table: relation of house B to house A (by offset), from A's side
#   help (bahami madad) = 5th/9th; general = 7th; collision (takrav) = 8th (A sees) / 6th; foundation (buniyadi) = 9th / 5th;
#   deceit (dhokha) = 10th / 4th; common wall (mushtarka diwar) = 2nd / 12th; sudden strike (achanak chot) = special list
ACHANAK_CHOT = {1: [3, 7, 11], 2: [4], 3: [1], 4: [10, 6], 5: [7], 6: [4], 7: [1, 5, 9], 8: [10], 9: [7], 10: [4, 8, 12],
                11: [1], 12: [10]}

# p.125-129 rin (inherited debts). planet: (houses, enemy planets that trigger it, name)
RIN = {
    "Jupiter": ([2, 5, 9, 12], ["Venus", "Mercury", "Rahu"], "Pitri rin (ancestral debt)", "पितृ ऋण",
                "a family priest wronged, temple or peepal destroyed near the ancestral home"),
    "Sun": ([5], ["Venus", "Rahu", "Ketu", "Saturn*"], "Self debt (zaati rin)", "ज़ाती (स्वयं का) ऋण",
            "disregard of old customs and religion; the house has fire-places or openings toward the sky"),
    "Moon": ([4], ["Ketu"], "Matri rin (mother's debt)", "मातृ ऋण",
             "a mother neglected after the birth of children; neighbourhood wells or streams filled with waste"),
    "Venus": ([2, 7], ["Sun", "Rahu", "Moon"], "Stri rin (debt to a woman)", "स्त्री ऋण",
              "a pregnant woman harmed for greed; family hatred of keeping cows or animals"),
    "Mars": ([1, 8], ["Mercury", "Ketu"], "Rishtedari rin (debt to relatives)", "रिश्तेदारी का ऋण",
             "a friend poisoned or a ready crop burnt; relatives kept away at births and festivals"),
    "Mercury": ([3, 6], ["Moon"], "Behen/beti rin (debt to a sister or daughter)", "लड़की-बहन का ऋण",
                "a girl or sister betrayed or harmed; children sold or bartered for greed"),
    "Saturn": ([10, 11], ["Sun", "Moon", "Mars"], "Zalimana rin (debt of cruelty)", "ज़ालिमाना ऋण",
               "a house or land taken by deceit; killing of living beings for property"),
    "Rahu": ([12], ["Sun", "Venus", "Mars"], "Ajanma rin (debt of the unborn)", "अजन्मे का ऋण",
             "deceit with in-laws or worldly ties that ruined another family"),
    "Ketu": ([6], ["Moon", "Mars"], "Daivik/dargahi rin (debt to nature)", "दरगाही (कुदरती) ऋण",
            "dogs killed, or the descendants of others destroyed for greed"),
}
# p.131-141 collective remedies: every blood member of the family contributes an equal share, done on one day
RIN_UPAY = {
    "Jupiter": ("Collect one coin from every blood member of the family and give it all to a temple on one day; or tend a peepal tree within sixteen steps of the ancestral door.",
                "खानदान के हर खूनी रिश्तेदार से एक-एक सिक्का लेकर एक ही दिन धर्म मंदिर में देना; या पुश्तैनी घर के दरवाज़े से सोलह कदम के अंदर पीपल की सेवा करना।"),
    "Sun": ("A yajna (havan) paid for in equal shares by every member of the family.",
            "कुल खानदान के हर मेंबर के बराबर हिस्से से यज्ञ करना।"),
    "Moon": ("Collect silver in equal shares from every member and float it in a river on one day.",
             "कुल खानदान के हर मेंबर से बराबर हिस्से की चांदी लेकर एक ही दिन दरिया में बहाना।"),
    "Venus": ("Feed one hundred healthy cows on a single day, the cost shared equally by the family.",
              "सौ गायों को एक ही दिन, सारे खानदान के बराबर खर्च से, भोजन खिलाना।"),
    "Mars": ("Collect equal money from the family and give it to a physician (or similar trade) so that he serves people free.",
             "सारे खानदान से बराबर पैसा इकट्ठा करके किसी हकीम या ऐसे पेशे वाले को देना कि वह लोगों का काम मुफ़्त करे।"),
    "Mercury": ("Take one yellow cowrie from each member, burn them together in one place and float the ash in a river the same day.",
                "हर मेंबर से एक-एक पीली कौड़ी लेकर एक ही जगह जलाना और उसी दिन राख दरिया में बहाना।"),
    "Saturn": ("Feed fish at one hundred different places on one day, or feed one hundred labourers, in equal family shares.",
               "एक ही दिन सौ अलग जगहों पर मछलियों को खाना डालना, या सौ मज़दूरों को खाना खिलाना, खानदान के बराबर खर्च से।"),
    "Rahu": ("One coconut from each family member, all floated in a river on one day.",
             "खानदान के हर सदस्य से एक-एक नारियल लेकर एक ही दिन दरिया में बहाना।"),
    "Ketu": ("Feed one hundred dogs on one day with equal family shares; or take the blessing of a widow living to the left of the house.",
             "सौ कुत्तों को एक ही दिन बराबर खर्च से खाना खिलाना; या घर के बाईं ओर रहने वाली किसी विधवा का आशीर्वाद लेना।"),
}

# p.153 Farman 9: the one-line remedy for each planet when its effect is bad
GENERAL_UPAY = {
    "Mars_bad": ("Float revdi (sesame-jaggery sweets) in running water.", "रेवड़ियाँ पानी में बहाना।"),
    "Jupiter": ("Apply saffron on the navel or the tongue, or eat it.", "केसर नाभि या जुबान पर लगाना या खाना।"),
    "Sun": ("Float jaggery in running water.", "पानी में गुड़ बहाना।"),
    "Moon": ("Keep a vessel of milk or water at the head-side overnight and pour it at the root of a keekar (acacia) tree in the morning.",
             "दूध या पानी का बर्तन रात को सिरहाने रखकर सुबह कीकर के पेड़ में डालना।"),
    "Saturn": ("Chhaya-patra: look at your face in oil in a vessel and donate the oil.", "तेल का छाया पात्र दान करना।"),
    "Venus": ("Donate a cow, or jowar (fodder).", "गऊ दान या चरी (ज्वार) दान करना।"),
    "Mars": ("Give or float sweets; feed sweet food.", "मिठाई या मीठा भोजन दान करना या बहाना।"),
    "Mercury": ("Float a copper coin with a hole in it in a river.", "तांबे के पैसे में सुराख़ करके दरिया में बहाना।"),
    "Rahu": ("Donate radish, or float coal in a river.", "मूली दान करना या कोयले दरिया में डालना।"),
    "Ketu": ("Give bread (roti) to dogs.", "कुत्ते को रोटी डालना।"),
}

# p.154-156 rules for doing any upay
UPAY_RULES = [
    ("A remedy runs for 40 days, and at most 43, continuously; a family-wide remedy runs 40-43 weeks instead (p.124, p.154).",
     "उपाय की मियाद कम से कम 40 और ज़्यादा से ज़्यादा 43 दिन लगातार होगी; सारे खानदान के लिए उपाय 40-43 सप्ताह होगा।"),
    ("If a day is missed, even the 39th, the remedy is void and starts again from day one (p.154, p.156).",
     "बीच में एक दिन भी नागा हो जाए, चाहे 39वाँ दिन, तो पूरा उपाय निष्फल; फिर से पहले दिन से शुरू करें।"),
    ("Do remedies by day, between sunrise and sunset; the book advises against remedies at night (p.155).",
     "उपाय सूर्य उदय से अस्त तक दिन में करें; रात को उपाय न करें।"),
    ("Do one remedy at a time; finish its 40-43 days, leave a gap, then start the next (p.124).",
     "एक वक्त में एक ही उपाय करें; 40-43 दिन पूरे करके कुछ दिन छोड़ें, फिर दूसरा।"),
    ("Any blood relative can do the remedy on the native's behalf (p.156).", "कोई भी खूनी रिश्तेदार उपाय कर सकता है।"),
    ("For a sleeping or ruined planet, first remedy the lord of the empty house, then the friends of the afflicted planet; "
     "if that fails strengthen the Sun, then the papi planets, and Mercury last (p.161).",
     "सोए या बर्बाद ग्रह के लिए पहले खाली घर के मालिक ग्रह का उपाय, फिर उसके दोस्त ग्रहों का; काम न बने तो सूर्य कायम करें, फिर पापी ग्रहों का उपाय, सबसे आखिर में बुध का।"),
    ("At marriage, the remedies for the bad planets of both charts should be done; the man's chart dominates after marriage (p.156).",
     "विवाह के समय दोनों कुंडलियों के मंदे ग्रहों का उपाय करें; शादी के बाद मर्द की कुंडली प्रबल हो जाती है।"),
]

# p.226 teva (chart) types
ANDHA_PAIRS = [("Mercury", "Jupiter"), ("Mercury", "Moon"), ("Mercury", "Mars"), ("Venus", "Jupiter"), ("Venus", "Sun"),
               ("Venus", "Moon"), ("Venus", "Rahu"), ("Saturn", "Sun"), ("Saturn", "Moon"), ("Saturn", "Mars"),
               ("Rahu", "Sun"), ("Rahu", "Moon"), ("Rahu", "Mars"), ("Rahu", "Jupiter"), ("Ketu", "Sun"), ("Ketu", "Moon"), ("Ketu", "Mars")]

# The 120-year varshphal table (pp.222-225A). Row = year of life; column n = where the planets of natal house n go.
# Six misprints in the source are corrected so that every row and every 12-year block is a permutation; see
# references/lalkitab_method.md for the exact cells.
VARSHPHAL = {
 1: [1, 9, 10, 3, 5, 2, 11, 7, 6, 12, 4, 8], 2: [4, 1, 12, 9, 3, 7, 5, 6, 2, 8, 10, 11], 3: [9, 4, 1, 2, 8, 3, 10, 5, 7, 11, 12, 6],
 4: [3, 8, 4, 1, 10, 9, 6, 11, 5, 7, 2, 12], 5: [11, 3, 8, 4, 1, 5, 9, 2, 12, 6, 7, 10], 6: [5, 12, 3, 8, 4, 11, 2, 9, 1, 10, 6, 7],
 7: [7, 6, 9, 5, 12, 4, 1, 10, 11, 2, 8, 3], 8: [2, 7, 6, 12, 9, 10, 3, 1, 8, 5, 11, 4], 9: [12, 2, 7, 6, 11, 1, 8, 4, 10, 3, 5, 9],
 10: [10, 11, 2, 7, 6, 12, 4, 8, 3, 1, 9, 5], 11: [8, 5, 11, 10, 7, 6, 12, 3, 9, 4, 1, 2], 12: [6, 10, 5, 11, 2, 8, 7, 12, 4, 9, 3, 1],
}


def _load_varshphal():
    import json
    import os
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lalkitab_varshphal.json")
    with open(p, encoding="utf-8") as f:
        return {int(k): v for k, v in json.load(f).items()}


VARSHPHAL = _load_varshphal()


# ---------------------------------------------------------------- planet-in-house readings (pp.235-739)
# key: (planet, house) -> dict(t=title_hi, te=title_en, g=good_en, gh=good_hi, b=bad_en, bh=bad_hi, u=[(en, hi), ...])
R = {}


def _r(p, h, t, te, g, gh, b, bh, u):
    R[(p, h)] = {"t": t, "te": te, "g": g, "gh": gh, "b": b, "bh": bh, "u": u}


# ---------------- Jupiter
_r("Jupiter", 1, "राजा या फ़कीर - बाकमाल मगर निर्धन", "King or fakir: accomplished, but money is not assured",
   "Learned (a degree or more), healthy and long-lived; rises through intellect and officials; every eighth year brings progress; mother supports the native for decades.",
   "पढ़ा-लिखा, सेहतमंद, लंबी उम्र; अपनी अक्ल और राजदरबारी लोगों से तरक्की; हर आठवाँ साल तरक्की का; माता का लंबा साथ।",
   "With pitri rin (Mercury, Venus, Rahu or Saturn-as-papi in 2-5-9-12) or a bad Sun/Saturn: no degree in the family, losses through Rahu, Venus or Mercury matters, and litigation that eats wealth; a sleeping Jupiter (house 7 empty) gives a bad 24th year.",
   "पितृ ऋण (2-5-9-12 में बुध, शुक्र, राहु या पापी शनि) या मंदे सूर्य-शनि से खानदान में डिग्री नहीं, राहु-शुक्र-बुध की चीज़ों से नुकसान, मुकदमों में धन हानि; सोया बृहस्पति (7 खाली) तो 24वाँ साल मंदा।",
   [("Marriage before 22 is auspicious when Jupiter is asleep (house 7 empty).", "सोए बृहस्पति (खाना 7 खाली) में 22 साल से पहले शादी मुबारक।"),
    ("When Jupiter turns bad, Mars items or relatives help; burying a Mars item in the earth helps.", "बृहस्पति के मंदे असर में मंगल की चीज़ें या रिश्तेदार मददगार; मिट्टी में मंगल की चीज़ दबाना।"),
    ("Do not stretch the hand for charity; the second 35-year cycle (from about 49) restores what was lost.", "खैरात के लिए हाथ न फैलाएँ; दूसरे 35 साला दौर में सब कमी पूरी होगी।")])
_r("Jupiter", 2, "जगत का धरम गुरु, इल्म व तालीम का मालिक", "Teacher to the world, master of learning",
   "Wealth grows through charity and service to travellers; 27 years of good standing with authority; gain through in-laws; hidden wealth or legacy when houses 2-6-8 are good; enemies in 2 or 8 cannot poison it.",
   "दान और मुसाफ़िर की सेवा से धन बढ़ता; 27 साल राजदरबार का उत्तम फल; ससुराल से लाभ; 2-6-8 नेक हों तो दफ़ीना या लावारिस जायदाद।",
   "When house 8 or 2 is afflicted (e.g. Mars-bad in 2): ruins its own family; Saturn in 10 with bad Venus troubles the wife; Mercury in 8 with Saturn in 10/11 brings losses.",
   "खाना 8-2 मंदे (जैसे 2 में मंगल बद) तो अपना ही खानदान तबाह; शनि 10 और मंदा शुक्र तो औरत दुखिया; बुध 8 और शनि 10-11 तो धन हानि।",
   [("Bad Mercury-Rahu in house 1: do Saturn's remedy; Mercury-Venus: Moon's remedy; Mercury-Saturn (papi): Jupiter's own remedy.", "खाना 1 में बुध-राहु मंदे तो शनि का उपाय, बुध-शुक्र तो चंद्र का, बुध-शनि (पापी) तो बृहस्पति का अपना उपाय।"),
    ("Enemies of Jupiter in house 8: use the remedy the book gives for that planet in house 8; otherwise Jupiter's own remedy.", "खाना 8 में बृहस्पति के दुश्मन हों तो उनका खाना 8 वाला उपाय; बाकी हालतों में बृहस्पति का अपना उपाय।")])
_r("Jupiter", 3, "गर्जना शेर व खानदानी गुरु", "Roaring lion, guru of the family",
   "Long life, learning and good health; fortune comes through brothers and sisters, who are useful; wealthy for certain; good from age 26 for twenty years when Mars is good.",
   "लंबी उम्र, इल्म, उम्दा सेहत; भाई-बहनों के ज़रिए किस्मत; दौलतमंद ज़रूर; मंगल नेक तो 26 साल से लंबा सुख।",
   "Ruined by liking flattery; cowardly and quarrelsome when Mars is bad; with Saturn in 4 and bad Mercury, grows rich by robbing others yet stays unlucky.",
   "खुशामद पसंदी से नष्ट; मंगल बद तो बुज़दिल-झगड़ालू; शनि 4 और बुध मंदा तो दूसरों का माल लूटकर भी कम नसीब।",
   [("Durga worship, or serving young girls (kanya) with sweet food and taking their blessing, washes away Mercury's poison.", "दुर्गा पूजन या छोटी कन्याओं को मीठा भोजन देकर आशीर्वाद लेना बुध की ज़हर धोता है।"),
    ("Avoid flattery and sycophants.", "खुशामद से बचें।")])
_r("Jupiter", 4, "चन्द्र की राजधानी का मालिक, बाग-बगीचे", "Lord of the Moon's capital: gardens and abundance (exalted)",
   "Famous in his circle like Raja Indra or Vikramaditya; lands, cattle and wealth arrive without chasing; legacy or lottery; good wife, children and parents; houses 3 and 4 planets turn good.",
   "राजा इंद्र और विक्रमजीत की तरह मशहूर; ज़मीन, मवेशी, दौलत खुद आए; लाटरी-दफ़ीना; उत्तम स्त्री, औलाद, माता-पिता।",
   "Mercury in 10 (or coming to 4 in a year) makes his own intelligence the cause of ruin; bad Saturn or Mercury lowers honour; bad Ketu turns the king into a fakir; illicit affairs destroy the elders.",
   "बुध 10 में (या वर्षफल में 4 में) तो अपनी अक्ल से बर्बादी; मंदे शनि-बुध से इज़्ज़त मंदी; केतु बुरा तो शाह से फ़कीर; गंदे इश्क से बुज़ुर्गों का नाश।",
   [("Keep away from illicit relationships; respect elders' instructions - obedience to elders saves this placement.", "गंदे इश्क से दूर रहें; बुज़ुर्गों की ताबेदारी उसे तार देगी।")])
_r("Jupiter", 5, "बड़ी इज़्ज़त, ब्रह्मज्ञानी, मगर आग का बांस", "Great honour and wisdom, but a bamboo of fire (temper)",
   "Children prosper; a son born on a Thursday makes father and son a pair of lions; honest trade grows; respecting children gives a good old age.",
   "औलाद फलती; वीरवार को लड़का पैदा हो तो बाप-बेटा शेरों का जोड़ा; ईमानदारी का सौदा बढ़ता; औलाद की कदर से बुढ़ापा उम्दा।",
   "Taking food or charity in the name of religion brings childlessness (especially with Ketu in 11); bad Ketu harms children; bad Jupiter brings pitri rin.",
   "धर्म के नाम पर खाना या दान लेना लावल्दी की निशानी (खासकर केतु 11); केतु मंदा तो औलाद मंदी; मंदे गुरु से पितृ ऋण।",
   [("Never take food or charity in the name of religion.", "धर्म के नाम पर खाना या दान न लें।"),
    ("When Ketu is bad (or in 11), Ketu's remedy (feeding dogs) helps.", "केतु मंदा (या 11 में) तो केतु का उपाय (कुत्ते को रोटी) मददगार।")])
_r("Jupiter", 6, "मुफ़्तखोर मगर साधु सुभाव", "Free bread, a sadhu's temperament",
   "Food and water come without effort and he can open a free kitchen for many; father prosperous; charity in the ancestors' name is the base of his luck; Saturn decides king or pauper.",
   "बगैर मेहनत रोटी-पानी हाज़िर, लंगर खोलने की हिम्मत; पिता खुशहाल; बुज़ुर्गों के नाम की खैरात किस्मत की बुनियाद; फ़ैसला शनि पर।",
   "When Ketu is bad: a begging bowl in hand; the maternal side is hostile until about 40.",
   "केतु मंदा तो फ़कीरों की तरह प्याला लिए; मामू खानदान 40 साल तक बेमायनी या दुश्मन।",
   [("Give charity in the name of the ancestors.", "बुज़ुर्गों के नाम पर खैरात करें।"),
    ("In bad times Ketu's remedy helps.", "मंदे वक्त केतु का उपाय मददगार।")])
_r("Jupiter", 7, "पिछले जन्म का साधु, गृहस्थ में राजा जनक", "A sadhu of a past life: Raja Janak in family life",
   "The wife's dowry blesses the home; first to help in religious work; a successful traveller; good for a woman's chart (children and money are not harmed).",
   "औरत के दहेज से बरकत; धर्म कार्य में सबसे आगे; कामयाब मुसाफ़िर; स्त्री की कुंडली में औलाद-धन मंदा नहीं।",
   "In a man's chart: poor sadhu, no help from brothers or authority, works daily for bread though rich; Mercury in 7 with papi brings trouble to in-laws or father.",
   "पुरुष के टेवे में निर्धन साधु, न भाई की मदद न राजदरबार; लखपति होकर भी मेहनत की रोटी; 7 में बुध-पापी तो ससुराल-पिता पर मंदा।",
   [("Keep Jupiter items (yellow cloth, gold) together with the items of the troublesome planet (Mercury or Mars-bad).", "बृहस्पति की चीज़ें (पीला कपड़ा, सोना) मंदे ग्रह (बुध या मंगल बद) की चीज़ों के साथ मिलाकर रखें।"),
    ("In bad times do the Moon's remedy; do not wander away from home.", "मंदी हालत में चंद्र का उपाय; घर से बाहर भटकें नहीं।")])
_r("Jupiter", 8, "वक्त मुसीबत खुदाई मदद, कब्रिस्तान का साधु", "Divine help in crisis: the sadhu of the burial ground",
   "Help arrives in every crisis; elders' blessings; never childless when Venus is in 2 or 6; long-lived family while Mercury is not in 9; knows hidden things ahead of time.",
   "हर मुसीबत में खुदाई मदद; बुज़ुर्गों का साथ; शुक्र 2-6 में तो लावल्द नहीं; बुध 9 में न हो तो खानदान लंबी उम्र; गैबी भेद पहले बता दे।",
   "Bad Mercury, Mars-bad or papi planets make it ruinous; pitri rin with Mercury or Rahu shortens the margin.",
   "बुध, मंगल बद या पापी मंदे तो वीराने; बुध-राहु से पितृ ऋण।",
   [("Keep gold on the body - the book says such a person is never miserable.", "जिस्म पर सोना कायम रखें; वह दुखिया न होगा।"),
    ("Give Jupiter or Venus items at a place of worship.", "बृहस्पति या शुक्र की चीज़ें धर्म स्थान में दें।")])
_r("Jupiter", 9, "धर्मी योगी, सोने का खानदान", "Religious yogi from a golden lineage",
   "Born into a family of means and good blood; his blessing - even his curse - helps others; parents, guidance and health good; wealth shown by houses 3 and 5.",
   "सुनहरी खानदानी ज़मीन का मालिक; उसकी बद्दुआ भी दूसरों को नेक; वाल्दैनी सुख, परहेज़गारी उम्दा; धन की हालत 3-5 से।",
   "Mercury, Venus or papi in 2-5-9-12 spoil it; with Sun weak, no shine to luck; with house 12 empty, blood and money worries.",
   "2-5-9-12 में बुध, शुक्र या पापी हों तो मंदा; सूरज निकम्मा तो किस्मत में चमक नहीं; 12 खाली तो खून-माली परेशानी।",
   [("Visit and serve a place of worship regularly in bad times (the remedy line in the book is partly illegible).", "मंदे वक्त धर्म स्थान में नियम से जाना और सेवा करना।")])
_r("Jupiter", 10, "पहाड़ी इलाके का गृहस्थ, कलपता दरवेश (नीच)", "Debilitated: the householder of the hills, a lamenting dervish",
   "With a good Saturn the native rises in Saturn's period (about 33-39) and through Saturn's trades; gold and silver work helps when Sun is in 3-5 and Saturn in 9.",
   "शनि उम्दा तो शनि की उम्र (33-39) में भागवान; सूरज 3-5 और शनि 9 तो सोने-चांदी के काम से फायदा।",
   "Poverty grows with goodness; even charity is misread; father cannot leave money; house 2 empty with Saturn in 1/10 brings want; wife suffers when Sun is in 5.",
   "नेकी के साथ गरीबी बढ़े; पिता धन न दे सके; शनि 1-10 और 2 खाली तो कुत्ते की खुराक को भी तरसे; सूरज 5 तो औरत पर औरत मरे।",
   [("Apply a saffron tilak on the forehead and keep the nose clean before starting any work.", "माथे पर केसर का तिलक और काम शुरू करने से पहले नाक साफ़।"),
    ("For the father's bad state, float a copper coin in running water daily for 40-43 days.", "पिता की मंदी हालत के लिए 40-43 दिन लगातार चलते पानी में तांबे का पैसा बहाना।"),
    ("Keep Jupiter strong (gold, yellow) or do Ketu's remedy; nose piercing helps.", "बृहस्पति कायम करें या केतु का उपाय; नाक छेदन मददगार।")])
_r("Jupiter", 11, "धर्म अदालत का राजा", "King of the court of dharma",
   "Charity, compassion and keeping promises multiply Jupiter eleven-fold; comfortable while working jointly with the family.",
   "पर-उपकार, गरीब पर दया और वायदे की पालना से बृहस्पति ग्यारह गुणा उत्तम; खानदान में मिलकर काम करने तक खुशगुज़रान।",
   "Living alone like a date palm turns the wind; Sun, Saturn or Mercury in 4-5-9 spoil Venus, Rahu and Ketu matters; Mars in 3 brings family deaths; Mercury in 3, debt despite income.",
   "खजूर के पेड़ की तरह अकेला हो तो मंदी हवा; 4-5-9 में सूरज, शनि या बुध तो शुक्र-राहु-केतु मंदे; मंगल 3 तो खानदानी मौतें; बुध 3 तो कर्ज़ाई।",
   [("Keep Jupiter strong (gold, saffron).", "बृहस्पति कायम रखें (सोना, केसर)।"),
    ("Give shrouds (kafan) at others' deaths, ahead of time.", "पहले से दूसरों की मौत पर कफ़न देते रहना मुबारक।"),
    ("Stay in the joint family.", "खानदान में मिलकर रहें।")])
_r("Jupiter", 12, "दुआएं भले सब की, समाधि से सोने की वर्षा", "Blessing all: gold rains through quiet devotion",
   "Silent meditation brings a rain of gold; opening a kitchen for the world fills his own house; Venus gives good results wherever it is; his service brings blessings.",
   "चुप समाधि से सोने की वर्षा; दुनिया के लिए भंडारे खोले तो घर सोने से भरे; शुक्र हर हाल में मुबारक; सेवा से आशीर्वाद।",
   "Papi in Jupiter's houses with bad Mercury or Venus; Rahu bad (9 or 12) makes skills useless and spending endless; Ketu bad till 34 when Mercury is bad.",
   "गुरु के घरों में पापी और बुध-शुक्र मंदे; राहु मंदा (9-12) तो हुनर बेफ़ायदा, फ़िज़ूल खर्च; बुध मंदा तो केतु 34 तक मंदा।",
   [("Keep water at the head-side at night.", "रात को सिरहाने पानी रखें।"),
    ("Serve sadhus, a guru or a peepal tree; never have a peepal cut.", "साधु, गुरु या पीपल की सेवा; पीपल न कटवाएँ।"),
    ("Saffron tilak and a clean nose; avoid lying, false witness and fraud (Rahu).", "केसर का तिलक, नाक साफ़; झूठी गवाही, धोखा, दगा से परहेज़।")])

# ---------------- Sun
_r("Sun", 1, "सतयुगी राजा, हुक्मरान", "A Satyug king, a ruler",
   "Builds religious places and wells, serves the father to the end, leaves wealth for the son; long life for himself and parents; long favour from authority; self-made and never short of income.",
   "धर्म अर्थ मकान और कुएँ बनवाने वाला; पिता की आखिर तक सेवा; बेटे को दौलत दे जाए; लंबी उम्र; राजदरबार की लंबी मदद; खुद साख्ता अमीर।",
   "Venus in 7: father dies early, wife's health suffers (especially if habituated to daytime intercourse); Mars in 5: sons die one after another; Saturn in 8: wife after wife; all planets deceive when friends are bad.",
   "शुक्र 7 तो पिता छोटी उम्र, औरत की सेहत मंदी (खासकर दिन में स्त्री भोग); मंगल 5 तो लड़के पर लड़का मरे; शनि 8 तो औरत पर औरत मरे।",
   [("If house 7 is empty (sleeping Sun), marry before 24.", "खाना 7 खाली (सोया सूरज) तो 24 से पहले शादी मुबारक।"),
    ("Install natural water (a hand pump) in the ancestral home.", "जद्दी मकान में कुदरती पानी (हैंड पंप) कायम करें।"),
    ("Avoid daytime intercourse.", "दिन के वक्त स्त्री भोग से परहेज़।")])
_r("Sun", 2, "सख़ी दाता - अपने बाजुओं का मालिक", "Generous giver who lives by his own arms",
   "Skilled, hard-working, maintains the whole clan; brave; prefers practical work to trade; maternal uncles do well.",
   "दस्ती मेहनत और हुनर का मालिक, सारे कबीले को पालने वाला; बहादुर; मामू की उम्दा हालत।",
   "Alone here it shuts its good effect on Venus things; women of the house decline; disputes over wealth, women and land make the Sun worse; Moon in 8 and taking charity bring ruin.",
   "अकेला सूरज शुक्र की चीज़ों पर नेक असर बंद करे; घर की औरतें घटें; धन-औरत-ज़मीन के झगड़े सूरज को मंदा करें; चंद्र 8 में दान लेना तबाही।",
   [("Never accept charity or free goods - the book says it brings complete ruin.", "दान या मुफ़्त माल लेना पूरी तबाही; परहेज़ करें।"),
    ("Saturn's remedy: give coconut oil, almonds and similar items at a place of worship.", "शनि का उपाय: नारियल, तेल, बादाम वगैरह धर्म स्थान में देते रहना।"),
    ("Avoid disputes over wealth, women and land.", "धन, औरत और ज़मीन के झगड़ों से बचें।")])
_r("Sun", 3, "दौलत का राजा, खुद कमाकर खाने वाला", "King of wealth who lives on his own earnings",
   "Self-earned wealth and good looks; mathematics or astrology useful; long-lived children; when the Moon is good, the later years are excellent.",
   "खुद कमाई, खूबसूरती; हिसाब या ज्योतिष का ताल्लुक कारआमद; औलाद की लंबी उम्र; चंद्र उम्दा तो आखिरी अवस्था उत्तम।",
   "A bad Moon brings daylight theft of money; bad Mercury with papi harms the maternal uncle's house; bad conduct defames his body and fortune.",
   "चंद्र बुरा तो दिन दहाड़े माया की चोरी; बुध-पापी मंदे तो मामू घर पर मंदा; मंदे चाल चलन से बदनामी।",
   [("Keep clear of stolen goods and keep good conduct.", "चोरी के माल से परहेज़ और नेक चाल चलन।"),
    ("Mars's remedy (sweets) helps.", "मंगल का उपाय (मीठा) मददगार।")])
_r("Sun", 4, "दूसरों के लिए जोड़ने वाला, बच्चों का दफ़ीना", "Saves for others: treasure left for the children",
   "Leaves money for the children, who become crorepatis; clear-minded and generous; wealth flows from the Moon's house; serving parents is the base of surplus money; sea voyages and gold-silver trade pay.",
   "औलाद के लिए दौलत जमा छोड़े, नाम लेवा करोड़पति; रौशन ज़मीर, दरिया दिल; चंद्र के घर से माया; वाल्दैनी सेवा फ़ालतू धन की बुनियाद; समुंदर का सफ़र, सोना-चांदी मुबारक।",
   "Bad papi spoil children; Rahu bad with Saturn in 4 and Jupiter in 10 spoils all the Sun; Jupiter in 10 brings gold theft and fire quarrels.",
   "पापी मंदे तो औलाद मंदी; राहु मंदा, शनि 4, गुरु 10 तो सूरज का सब असर मंदा; गुरु 10 तो सोने की चोरी, आग के झगड़े।",
   [("Distribute free food to the blind.", "अंधों को मुफ़्त खुराक बांटना मुबारक।"),
    ("Do the Moon's remedy; in some cases Mars's remedy through the ancestral house.", "चंद्र का उपाय; कुछ हालतों में जद्दी मकान के ज़रिए मंगल का उपाय।")])
_r("Sun", 5, "परिवार उन्नति का मालिक, बुग़ज़ भरा", "Grows the family, but carries grudges",
   "Bread and water multiply from the day children are born; a kitchen on the east wall helps; with Ketu in 4 or 7 everything is good.",
   "औलाद के दिन से रोटी पानी की बरकत; मशरिकी दीवार से रसोई मुबारक; केतु 4-7 तो सब उम्दा।",
   "Saturn in 3: sons die, children's money troubles; Jupiter in 10: wife after wife; Rahu or Saturn in 1 is a bad state; grudges and envy poison it.",
   "शनि 3 तो लड़के पर लड़का मरे, औलाद पर माली खराबी; गुरु 10 तो शादियाँ एक से ज़्यादा; राहु या शनि 1 मंदा हाल; कीना-हसद ज़हर।",
   [("When Ketu (children, maternal uncle) is troubled, give jaggery to monkeys; otherwise Mercury's remedy.", "केतु (औलाद-मामू) पर मंदे असर में बंदर को गुड़ देना; वरना बुध का उपाय।"),
    ("Keep the kitchen on the east side of the house.", "रसोई घर की पूर्वी दीवार की तरफ़ रखें।")])
_r("Sun", 6, "आग जला, दौलत से बेफ़िक्र, किस्मत पर शाकिर", "Content with fate, careless of wealth",
   "Wealth and kingship are not essential yet he is never childless; keeping old customs keeps the Sun excellent; after 48 bad stories turn good even without remedies.",
   "राज दौलत ज़रूरी नहीं, फिर भी लावल्द नहीं; पुरानी रस्में कायम रखे तो सूरज उत्तम; 48 के बाद बगैर उपाय भी मंदा ज़माना नेक।",
   "At the Sun's age (22) the father or native may suffer when house 2 is empty; Moon bad or papi in 5 harms; Ketu's matters (children, uncle) and own health suffer.",
   "22 साला उम्र में पिता और टेवे वाले में से एक पर भारी (2 खाली); चंद्र बुरा या 5 में पापी तो मंदा; केतु की चीज़ें और अपनी सेहत।",
   [("Keep and serve one of the 'three dogs of the world' (brother at sister's house, son-in-law at in-laws', grandson at maternal grandparents').", "दुनिया के तीन कुत्तों में से किसी की पालना।"),
    ("Continue old family customs.", "पुरानी रस्में चलाए रखें।"),
    ("Give jaggery or wheat to monkeys and Sun items (wheat, bajra) to brown ants.", "बंदर को गुड़-गेहूँ, भूरी चींटी को गेहूँ-बाजरा।"),
    ("Quench the evening kitchen fire with milk; keep Moon items (silver, river water); give dog-food at a place of worship.", "शाम को रोटी पकाकर चूल्हे की आग दूध से बुझाना; चांदी-दरिया का पानी कायम; धर्म स्थान में कुत्ते की खुराक।")])
_r("Sun", 7, "कम कबीला - डरता डरता मर रहे", "Small family, lives in fear",
   "Long life, returns safely from travel; when giving, gives silver or pearls; prosperous from Mercury's age (34); good marriage and family for Venus's 25 years.",
   "उम्र लंबी, सफ़र से ज़िंदा वापस; दान में चांदी या मोती दे; बुध की उम्र (34) से इकबालमंद।",
   "Penance and grief until 34; consumption, fires, embezzlement or flight from family life; cuts Venus's good effect; suicidal counsel though courage is great.",
   "34 साल तक दुखों का पुतला; तपेदिक, आग, गबन के बहाने; गृहस्थ से तंग फ़कीर; शुक्र का नेक असर बंद; खुदकुशी तक की सलाह।",
   [("Bury square pieces of copper in the ground when family or money matters are bad.", "माली-गृहस्थी मंदी में ज़मीन में तांबे के चौकोर टुकड़े दबाना।"),
    ("After cooking in the evening, put out the stove fire with milk and do not relight it before sunrise.", "शाम को रोटी पकाकर चूल्हे की आग दूध से बुझाना; सुबह सूरज निकलने तक दोबारा न जलाएँ।"),
    ("Start work after a little sweet or a few sips of water; serve a black or hornless cow (not white); offer a little food to the fire before eating.", "थोड़ा मीठा या पानी के घूंट लेकर काम शुरू; काली या बगैर सींग गाय की सेवा (सफ़ेद नहीं); भोजन का हिस्सा आग में आहुति।"),
    ("Speak softly; Jupiter's remedy helps.", "नरम ज़ुबान; बृहस्पति का उपाय मददगार।")])
_r("Sun", 8, "तपस्वी राजा, सांच की आंच", "Ascetic king: the heat of truth",
   "Death flees from his house; rises at the Sun's age; becomes a treasurer of wealth; long life when he serves an elder brother and cows.",
   "जिस घर बैठे मौत कोसों भागे; सूरज की उम्र से तरक्की, भंडारी दौलत; बड़े भाई और गाय की सेवा से लंबी उम्र।",
   "A south-facing door is the first sign of deaths; a white cow is unlucky; love of theft, disguise or illicit love destroys the line; Saturn in 3 with bad Jupiter, Venus in 1-5 shorten life.",
   "दक्खन का दरवाज़ा मौतों की पहली निशानी; सफ़ेद गाय मंदभाग; चोरी, बहरूपियापन, गंदा इश्क तबाही; शनि 3 और गुरु मंदा, शुक्र 1-5 तो उम्र छोटी।",
   [("Serve an elder brother and cows (not a white cow).", "बड़े भाई और गाय की सेवा (सफ़ेद गाय नहीं)।"),
    ("Avoid a south-facing door; keep away from theft, disguise and illicit love.", "दक्खन के दरवाज़े से बचें; चोरी, बहरूपियापन, गंदे इश्क से दूर रहें।")])
_r("Sun", 9, "लंबी उम्र, भारी कबीला, ग्रहण के बाद का सूरज", "Long life, large clan: the Sun after an eclipse",
   "His birth ends the family's old bad times; maintains seven generations; sees grandsons prosper; never hungry; helpful to all.",
   "उसके जन्म से खानदान का पुराना मंदा ज़माना खत्म; सात पुश्तों का निगहबान; पोते-पड़पोते सुखी देखे।",
   "Taking silver or living on free goods marks a bad Moon and the setting of the Sun; luck often wakes only after 34.",
   "चांदी का दान लेना या मुफ़्तखोरी मंदे चंद्र और ज़वाल की निशानी; किस्मत अक्सर 34 के बाद जागे।",
   [("Never accept silver or free goods.", "चांदी का दान या मुफ़्त माल न लें।"),
    ("Wear a white or light sherbet-coloured turban or cap; avoid black or blue on the head and going bareheaded.", "सफ़ेद या हलके शरबती रंग की पगड़ी-टोपी; सिर पर काला-नीला या नंगा सिर गैर मुबारक।")])
_r("Sun", 10, "इज़्ज़त, सेहत और दौलत का मालिक मगर वहमी", "Master of honour, health and wealth, but suspicious",
   "Honour, health and wealth when guarding the head colour; river or well water always helps.",
   "इज़्ज़त, सेहत, दौलत का मालिक; दरिया या कुएँ का पानी हमेशा मदद देगा।",
   "Alone it shuts its good effect on Saturn's things (ancestral property, father); black or blue on the head, Saturn's 9-year period, Saturn-Venus bad in 4: short life of father; no recognition at court.",
   "अकेला सूरज शनि की चीज़ों (जद्दी विरासत, पिता) पर नेक असर बंद; सिर पर काला-नीला मनहूस; शनि-शुक्र 4 मंदे तो पिता की उम्र छोटी; राजदरबार में कदर नहीं।",
   [("Wear white or light sherbet colours on the head, never black or blue, and do not go bareheaded.", "सिर पर सफ़ेद या हलका शरबती रंग; काला-नीला या नंगा सिर नहीं।"),
    ("Float (a copper coin) in flowing water for 40-43 days when recognition is blocked.", "दरिया-नदी के चलते पानी में 40-43 दिन तक बहाना।")])
_r("Sun", 11, "पूर्ण धर्मी मगर अपना ही ऐश पसंद", "Fully religious, yet fond of his own comforts",
   "Long-lived; righteous conduct and giving up meat and alcohol make him the father of three sons and keep the family happy.",
   "लंबी उम्र; नेक चलन और शराब-गोश्त छोड़े तो तीन बेटों का बाप, परिवार सुखी।",
   "Meat and alcohol bring childlessness; bad Saturn or Mercury in 3, Moon in 8 or 5 at age 12 make it immoral or childless.",
   "शराब-गोश्त से लावल्दी; शनि-बुध 3 मंदे, चंद्र 8 तो हरामकारी; चंद्र 5 तो औलाद न हो।",
   [("Keep a radish (or carrot, or a Saturn item - not a black one) at the head-side at night and give it at a place of worship in the morning.", "मूली (गाजर या शनि की अश्या, काले रंग की नहीं) रात को सिरहाने रखकर सुबह धर्म स्थान में देना।"),
    ("Give up alcohol and meat.", "शराब और गोश्त छोड़ें।")])
_r("Sun", 12, "सुख की नींद मगर पराई आग में जलने वाला", "Sound sleep, yet burns in others' fires",
   "Righteous and happy at home; while the house keeps an open courtyard the Sun is not bad; trade (not manual craft) is blessed; Venus is not ruined.",
   "जितना धर्म में पक्का उतना सुखिया गृहस्थ; मकान का खुला सेहन कायम तो सूरज मंदा नहीं; तिजारत मुबारक, दस्ती हुनर में ग्रहण।",
   "Papi in house 1 bring trouble with authority and loss of sleep and appetite; standing surety, giving evidence or envy ruins him.",
   "पापी तख्त पर हों तो राज खराबी, नींद-खुराक न मिले; गवाही, ज़मानत और हसद से तबाही।",
   [("Keep an open courtyard in the house.", "मकान का खुला सेहन कायम रखें।"),
    ("Do not stand surety or give evidence for others; forgive enemies in your bad times.", "ज़मानत या शहादत न दें; मंदे वक्त में माफ़ी दें।")])

# ---------------- Moon
_r("Moon", 1, "माता जिंदा होने तक ज़र व दौलत - खालिस दूध", "Wealth while the mother lives: pure milk",
   "Wealth flows like a canal in a desert from birth while the mother lives; at 24-28 rivers of milk; elders' blessings equal a mother's.",
   "जन्म से माता के जिंदा रहते धन की बरकत; 24-28 में दूध की नदियाँ; बूढ़ी माताओं की आशीर्वाद माता के बराबर।",
   "Selling milk for profit shrinks the family; free-loading loses the old glory; however exalted Venus is, the wife suffers while the mother is alive; marriage in the 24th year spoils the Moon.",
   "नफ़े के लिए दूध बेचना परिवार घटाए; मुफ़्तखोरी से पहली शान जाए; शुक्र कितना ही ऊंच, माता के बैठे औरत दुखिया; 24वें साल शादी चंद्र बर्बाद।",
   [("Wake a sleeping Moon (house 7 empty) before 24 by keeping Venus items - a cow or a woman servant - at home.", "सोए चंद्र (7 खाली) को 24 से पहले जगाएँ: घर में गाय या नौकरानी कायम करें।"),
    ("Do not use silver vessels with a spout; give milk in charity rather than selling it.", "नाली वाले चांदी के बर्तन (गंगा सागर, केतली) न बरतें; दूध बेचने की बजाए खैरात करें।"),
    ("When taking children across a river to stay away 100+ days, drop a copper coin in the river.", "औलाद को दरिया पार ले जाते वक्त (100 दिन से ज़्यादा ठहरना हो) तांबे का पैसा दरिया में डालें।"),
    ("Fix copper nails in the four legs of the bed, or pour a little water at a banyan tree from time to time.", "चारपाई के चारों पायों में तांबे की मेखें; या बड़ के पेड़ में पानी डालना।"),
    ("Take rice and silver from the mother's hands as a last blessing; bury a Mars item in the earth.", "माता के हाथों से चावल-चांदी आखिरी आशीर्वाद के तौर पर लेना; मिट्टी में मंगल की चीज़ दबाना।")])
_r("Moon", 2, "खुद पैदा करदा माया की देवी", "Goddess of self-made wealth (exalted)",
   "The family line never ends however weak the children's yoga; ancestral property comes; rich, a fine rider, never defeated; the house where Jupiter sits is always strong.",
   "खानदानी नस्ल कभी बंद नहीं; जद्दी जायदाद का हिस्सा ज़रूर; दौलतमंद, घोड़ों का शहसवार, कभी हार नहीं।",
   "Without Moon items in the house old age suffers; Mercury, Venus and Rahu/Ketu in 1-2-7 are bad; business grows only after quarrels.",
   "चंद्र की चीज़ें न हों तो बुढ़ापा मंदा; 1-2-7 में बुध, शुक्र, राहु-केतु मंदे; कारोबार में बरकत झगड़े के बाद।",
   [("Keep Moon items (silver, rice, running water) at home; bury silver under one's own house for long life.", "चंद्र की चीज़ें घर में कायम; अपनी लंबी उम्र के लिए अपने मकान की तह में चांदी दबाना।"),
    ("Keep the floor of the house of earth (kachcha); serve old women.", "मकान का फ़र्श कच्ची मिट्टी का; बुज़ुर्ग बुढ़िया की सेवा।"),
    ("Give green cloth to girls for 40-43 days when Mercury troubles business.", "कारोबार में बुध की खराबी हो तो 40-43 दिन लड़कियों को हरा कपड़ा देना।")])
_r("Moon", 3, "चोरी व मौत का रक्षक, उम्र का मालिक", "Guardian against theft and death, lord of longevity",
   "Wealthy, long-lived, victorious; never short of food and never robbed; deaths in the family are few; women are honoured and bring progress.",
   "दौलतमंद, लंबी उम्र, मैदाने जंग में फ़तह; रिज़क की कमी और चोरी नहीं; खानदान में मौतें कम; स्त्रियों की पूजा और उन्नति।",
   "Bad Mercury makes servants or brokers disloyal; house 8 bad or papi afflict; loss of money without theft.",
   "बुध मंदा तो नमक हराम दलाल; 8 मंदा या पापी हों तो धन हानि।",
   [("Worship Mercury (honour young girls) while Rahu/Ketu are not bad.", "राहु-केतु मंदे न हों तो बुध की पूजा (कन्या) मुबारक।"),
    ("Give Moon items at a daughter's birth, Sun items at a son's birth, and perform kanyadan when marrying into Rahu ties.", "लड़की के जन्म पर चंद्र की चीज़ों का दान, लड़के के जन्म पर सूरज की चीज़ों का; राहु (ससुराल) के ताल्लुक पर कन्यादान।")])
_r("Moon", 4, "खर्चने पर और बढ़ने वाला माया का दरिया", "A river of wealth that grows as it is spent",
   "The more he spends the more comes; mother (even a stepmother) and her family helpful; cloth trade with the mother profits; a full house of four friends when Venus and Mars are in 4.",
   "जितना खर्चे उतनी माया बढ़े; माता (सौतेली भी) व माता खानदान नेक; बजाज़ी में फ़ायदा; उम्र 85-96।",
   "Selling milk dries the wealth; Jupiter in 10 brings punishment even for giving bread; bad papi or Venus, or houses 8/2 bad spoil it.",
   "दूध बेचे तो ज़र का चश्मा जले; गुरु 10 तो रोटी देकर भी ज़हर का इल्ज़ाम; पापी या शुक्र मंदे।",
   [("Never sell milk; give it free.", "दूध न बेचें; मुफ़्त दें।"),
    ("Keep Moon items; Jupiter-Ketu or elders going together to a place of worship or a yajna helps.", "चंद्र की चीज़ें कायम; बाबा-पोता या बृहस्पति-केतु इकट्ठे धर्म स्थान या यज्ञ में जाएँ।")])
_r("Moon", 5, "बच्चों के दूध की माता व रूहानी नहर", "Mother of children's milk, a spiritual canal",
   "Long life (up to 100); just, compassionate, a judge's scale; makes even forests and hills prosperous; public works bring prosperity to his children's villages.",
   "उम्र पूरी लंबी; अदल-इंसाफ़ का तराज़ू, रहमदिल; जंगल-पहाड़ भी आबाद करने वाला धर्मात्मा।",
   "Harsh speech is the first sign of coming trouble; greed and selfishness destroy; houses 4-8-12 bad keep the Moon bad till 34; bad Venus ruins in-laws, bad Mercury the mother's family, bad Ketu the father's.",
   "मंदा बोल आने वाली मुसीबत की पहली निशानी; लालच-खुदगर्ज़ी नाश; 4-8-12 मंदे तो 34 तक चंद्र मंदा; शुक्र मंदा तो ससुराल, बुध मंदा तो माता खानदान, केतु मंदा तो पिता खानदान मंदा।",
   [("Speak sweetly; before any act that may harm someone, take advice (even 'ask a wall').", "मीठा बोलें; बुरा करने से पहले किसी से सलाह ले लें।"),
    ("Eat something sweet before leaving home on a journey; building a well in a hospital or cremation ground is auspicious.", "घर से चलते वक्त मीठा खाकर निकलें; अस्पताल या श्मशान के अहाते में कुआँ लगाना मुबारक।")])
_r("Moon", 6, "धोखा की माता व खारा पानी", "Mother of deceit: brackish water",
   "Pouring water into a dying person's mouth gives relief - a life-giving touch when houses 2-4-8-12 are good.",
   "जब 2-4-8-12 उम्दा तो तड़पते के मुँह में पानी डालते ही आराम दे।",
   "Milk at night acts like poison; public or farm wells built by him turn bad; children and both families' lives under attack; his silver is worth earth; bad Venus ruins in-laws, bad Ketu the father's family, bad Mercury the mother's.",
   "रात का दूध ज़हर; आम या खेती का कुआँ मंदा; औलाद और माता-पिता खानदान पर हमला; चांदी मिट्टी के बराबर।",
   [("Give items of the Moon's friends (Sun, Mars, Jupiter) at a place of worship now and then, or simply bow there.", "धर्म स्थान में चंद्र के दोस्तों (सूरज, मंगल, बृहस्पति) की कोई चीज़ देना या सिर झुका आना।"),
    ("Drink milk only by day; at night use split-milk water or paneer instead.", "दूध सिर्फ़ दिन में; रात को फटे दूध का पानी या पनीर।"),
    ("A well inside a hospital or cremation ground is allowed; avoid wells for public or farm use.", "अस्पताल-श्मशान के अहाते में कुआँ मना नहीं; आम या खेती का कुआँ मंदा।")])
_r("Moon", 7, "बच्चों की माता खुद लक्ष्मी अवतार", "Mother of children, Lakshmi herself",
   "Shines like silver in earth from birth even if born poor; property and family grow; the wife brings milk and the son grows wealth.",
   "जन्म से मिट्टी में चांदी की तरह चमकदार; जायदाद, परिवार बढ़े; औरत दूध लाए, बेटे से माया बढ़े।",
   "Selling milk or water burns the son's wealth; marriage in the 24th year makes papi, Venus and Mercury bad; papi with Jupiter-Mars bad burns Mercury in 8.",
   "दूध-पानी बेचे तो पूत की माया जले; 24वें साल शादी तो पापी, शुक्र, बुध मंदे।",
   [("At marriage let the bride bring Moon items (milk, silver), or have them already in the groom's house before she enters.", "शादी के दिन औरत के साथ चंद्र की चीज़ें (दूध-चांदी) आएँ या पहले से खाविंद के घर हों।"),
    ("Never sell milk or water.", "दूध या पानी न बेचें।")])
_r("Moon", 8, "मुर्दा माता - जला दूध", "The dead mother: burnt milk",
   "The family line does not end; benefits in-laws, son-in-law and maternal uncle even late in life; long life whatever else happens.",
   "खानदानी नस्ल बंद नहीं; ससुराल, दामाद, मामू को तारे; हार पर हार के बाद भी उम्र न हारे।",
   "Without milk given in the elders' name: asthma, epilepsy or childlessness; building over a well; jewellery trade is unlucky; ancestral property and Venus things do him no good.",
   "बुज़ुर्गों के नाम दूध की खैरात न करे तो दमा-मिरगी-लावल्दी; कुआँ छत कर मकान; जौहरी का काम बदबख्ती।",
   [("Give milk in the name of the elders (shraddh).", "बुज़ुर्गों के नाम पर दूध की खैरात (श्राद्ध)।"),
    ("Keep water from a well inside a cremation ground at home.", "श्मशान के अहाते के कुएँ का पानी घर में रखना।"),
    ("Do not cover a well to build a house; avoid the jewellery trade.", "कुआँ छत कर मकान न बनाएँ; जौहरी का काम न करें।")])
_r("Moon", 9, "घड़े बराबर मोती, दुखियों का रक्षक समंदर", "Pearls by the pot: an ocean protecting the distressed",
   "Ninefold pearls: children and wealth grow; a guide to all however others behave; friends in 3 give wealth, friends in 5 children and dharma; a planet in 4 gives a milk-filled fortune.",
   "नौ गुणा मोती: औलाद, दौलत बढ़े; दुश्मन बैठे फिर भी धर्म पालन; 3 में दोस्त तो धन, 5 में दोस्त तो औलाद-धर्म, 4 में कोई ग्रह तो दूध भरी किस्मत।",
   "If Rahu deceives (milk of cow and of cactus look alike), the ocean shrinks to what a dog or a goat can drink - money weak till 34 or 48.",
   "राहु की हालत से अक्ल धोखा खाए तो समंदर का पानी इतना कि एक कुत्ता या बकरी पी जाए; माली हालत 34-48 तक कमज़ोर।",
   [("Practise dharma; sea or air travel is favourable (no specific upay in the text for the good state).", "धर्म पालना; बहरी-हवाई सफ़र उत्तम।")])
_r("Moon", 10, "आक (मदार) का दूध - ज़हरीला पानी", "Milk of the aak plant: poisoned water",
   "Long life (90+); helped by visiting places of worship; papi have no bad effect on 5 and need no remedy.",
   "उम्र 90 से कम नहीं; धर्म स्थान में आना-जाना किस्मत बुलंद; पापी का 5 पर असर नहीं।",
   "Medicine practised at night or dissolved in water kills; acquiring a house through brothers turns his own well into a cause of death; ruins women he is responsible for.",
   "रात को मरीज़ों का इलाज या पानी में घुली दवाइयाँ मंदी; भाइयों के ज़रिए मकान ले तो अपना कुआँ मौत का बहाना; औरतों की कबूतरबाज़ी से बचें।",
   [("Keep natural water (well, hand pump) continuously - after ten years of keeping it the Moon washes all poison (the book says 45 years).", "कुदरती पानी (कुआँ, हैंड पंप) लगातार कायम रखना।"),
    ("Do not give medicines at night or acquire a house or Saturn items through brothers; keep away from womanising.", "रात को इलाज न करें; भाइयों के ज़रिए मकान या शनि की चीज़ न लें; औरतों से बचकर चलें।")])
_r("Moon", 11, "होते हुए न के बराबर - निरपक्ष (सिफ़र मंदा)", "Present yet as good as absent: neutral",
   "Neither strongly good nor bad unless house 3 is bad or 5 is poisoned; lungs and chest are the weak point when house 2 is empty.",
   "होते हुए न के बराबर; 3 मंदा या 5 में ज़हर हो तो मंदा; 2 खाली तो फेफड़े-छाती की बीमारियाँ।",
   "Theft and deceit around him when Mars is bad; misfortune for the whole clan with Ketu 4, Jupiter 5, Rahu 2/10, Sun 6, Mercury 8.",
   "मंगल बद तो चोर-धोखेबाज़ का ताल्लुक; केतु 4, गुरु 5, राहु 2-10, सूरज 6, बुध 8 तो सारे कबीले पर मुसीबत।",
   [("Wash the eyes with milk, or give milk at a Bhairon temple.", "आँखें दूध से धोना या भैरों के मंदिर में दूध देना।"),
    ("Quench a red-hot gold rod in milk (Ketu is weak with this Moon).", "सोने की सलाख गर्म करके दूध में बुझाना।")])
_r("Moon", 12, "उजड़ा बुढ़ापा - गंदा बरसाती नाला", "A ruined old age: a dirty monsoon drain",
   "With Sun and Mercury in 3, or a good Jupiter or Sun, it becomes a clean river that saves the whole family; rain water helps.",
   "सूरज-बुध 3 या बृहस्पति-सूरज नेक तो कुल घरबार को तारने वाला उम्दा दरिया; मींह का पानी मददगार।",
   "Otherwise a flood that wrecks settled homes: parental wealth burnt or sold, in-laws ruined, false charges; the planet in 2 decides honour, in 5 children, in 6 worldly ties, in 9 ancestry.",
   "वरना बस्तियाँ उजाड़ने वाला गंदा सैलाब; वाल्दैनी माल जले या बिके, ससुराल उजड़े, बेगुनाह पर इल्ज़ाम; 2 का ग्रह इज़्ज़त, 5 का औलाद, 6 का दुनियावी ताल्लुक, 9 का बुज़ुर्गी।",
   [("Keep rain water at home; visit places of worship regularly.", "बारिश का पानी घर में; धर्म स्थान में आते-जाते रहना।")])

# ---------------- Venus
_r("Venus", 1, "काग व मच्छ रेखा की रंग-बिरंगी माया", "Many-coloured wealth of the crow line and the fish line",
   "With houses 7 and 10 well placed (fish line) a Vishnu-like provider and mountains of wealth; a cow or woman servant at home keeps the wealth.",
   "7-10 सही हों (मच्छ रेखा) तो विष्णु की तरह पालने वाला, माया के पहाड़; घर में गाय या नौकरानी तो माया बनी रहे।",
   "Romance at the cost of dharma; mother dies early or suffers when Venus is bad; marriage at 25 loses wealth and wife; bad Saturn makes companions bad.",
   "इश्क को धर्म से परहेज़ नहीं; शुक्र मंदा तो माता बचपन में गुज़रे; 25 में शादी तो दौलत व औरत न रहे; शनि बुरा तो साथी मंदे।",
   [("Keep a cow or a woman servant at home.", "घर में गाय या नौकरानी कायम रखें।"),
    ("At least seven grains or fodder (chari) in charity; for a man kanyadan, for a woman gau daan; a diet of barley and cow urine is recommended in the book.", "कम से कम सात अनाज या चरी का दान; मर्द कन्यादान, औरत गऊ दान; गौ-मूत्र व जौं की खुराक।"),
    ("At marriage the bride should receive pure silver from her parents.", "शादी के वक्त ससुराल से खालिस चांदी औरत को मिले।")])
_r("Venus", 2, "मोहमाया का उम्दा गृहस्थ", "A fine householder of worldly attachment",
   "Wealth walks to his forehead when Ketu, Jupiter and Mercury are good; food never fails - it doubles; the cow's protector.",
   "केतु-गुरु-बुध उम्दा तो दौलत खुद मस्तक चले; रिज़क कभी खराब नहीं, दिन दुगना रात चौगुना।",
   "Houses 9 and 12 empty spoil wife and wealth; papi in Jupiter's house ruin the wife; disease quarrels many.",
   "9-12 खाली तो औरत-दौलत मंदी; गुरु के घर पापी तो औरत बर्बाद।",
   [("Serve cows; ask only of God for what is missing.", "गऊ सेवा; सिर्फ़ मालिक से मांगना ही कमी पूरी करेगा।")])
_r("Venus", 3, "औरत की इज़्ज़त करने वाला - औरत मर्द बनकर मदद करे", "Honours women; the wife stands like a man beside him",
   "Women are drawn to him; his own wife works like a brother beside him; free bread or easy living; Venus then gives Moon's good too.",
   "औरत ज़ात फ़रेफ़्ता; अपनी औरत भाई की तरह मर्द का काम दे; मुफ़्त की रोटी या आसान गुज़रान।",
   "Not honouring his own wife spoils Venus; with Mars-bad, works for every bite though rich; bad Jupiter in 9 ruins health.",
   "अपनी औरत की इज़्ज़त न करे तो शुक्र मंदा; मंगल बद से ताल्लुक तो लखपति होकर भी मेहनत की रोटी।",
   [("Respect your own wife - the book calls this the foundation of Venus's good result.", "अपनी औरत की इज़्ज़त करना शुक्र के नेक फल की बुनियाद।"),
    ("Mars items or relatives help the wife.", "मंगल की चीज़ें या रिश्तेदार औरत को मदद दें।")])
_r("Venus", 4, "नुक्स यार अपना, इश्क औरतों का", "Faults of friends, love of women",
   "Love, friendship and the ability to hide faults and see virtues; one wife alive when a planet sits in 2 or 7.",
   "दोस्ती, उल्फ़त, ऐब पर पर्दा और खूबी पर नज़र; 2-7 में कोई ग्रह तो एक ही औरत।",
   "Two wives at once when 2 and 7 are empty; few children; maternal uncle ruined; covering a well or building over it signals childlessness; marriage in certain years unlucky.",
   "2-7 खाली तो एक वक्त में दो औरतें; किल्लत औलाद; मामू तबाह; कुआँ बंद कर मकान तो लावल्दी।",
   [("If the maternal uncle's house is ruined, do the Moon's remedy; otherwise drop Jupiter items in a well.", "मामू घर तबाह हो चुका तो चंद्र का उपाय; वरना कुएँ में बृहस्पति की चीज़ें गिराना।"),
    ("Performing the marriage rites twice with the same wife removes the 'two wives' condition (the book notes it can harm her health).", "पहली ही औरत से दोबारा शादी की रस्म अदा करना।"),
    ("Keep the roof in good repair; when Venus and Moon are both bad, bury a peach stone filled with surma outside.", "मकान की छत उम्दा रखें; शुक्र-चंद्र दोनों मंदे तो आड़ू की गिटक में सुरमा भरकर बाहर दबाना।"),
    ("Never close a well or build over one.", "कुआँ बंद न करें, उस पर मकान न बनाएँ।")])
_r("Venus", 5, "बच्चों से भरा हुआ घर-परिवार", "A house full of children",
   "Wealth grows with love of homeland and clan; serving cows and the mother with a clean heart brings prosperity; the Moon then gives Venus's support.",
   "वतन और कबीले की मोहब्बत से माया बढ़े; गऊ और माता की सेवा और साफ़ दिल से बरकत।",
   "Children made outside the home turn bad; Moon-Venus quarrel (daughter-in-law and mother-in-law); bad Mercury ruins daughters; loose conduct burns the couple.",
   "बाहर बने बच्चे मंदे; नूँह-सास का झगड़ा; बुध मंदा तो लड़कियाँ बर्बाद; मंदे चाल चलन से जोड़ा जले।",
   [("Serve cows and the mother; keep a clean heart and good conduct.", "गऊ और माता की सेवा, पाक दिल, नेक चाल चलन।"),
    ("The Moon's remedy helps.", "चंद्र का उपाय मददगार।")])
_r("Venus", 6, "शान से रखो तो दौलत के महल, वरना नीच", "Kept with dignity it gives palaces of wealth; otherwise debilitated",
   "Outward dignity brings worldly status; a son born brings two good years; helps the poor; comfort in old age.",
   "ज़ाहिरदारी उम्दा तो दुनियावी शान; गरीबों की मदद; आखिर उम्र में आराम।",
   "Gives little use of own house; deprived of wife's comfort; theft of cattle or money is a sign; with bad Ketu a barren wife; Rahu in 2: first wife dies.",
   "अपने मकान का फ़ायदा न पाए; स्त्री सुख से महरूम; गाय-बैल या धन की चोरी निशानी; केतु मंदा तो बांझ; राहु 2 तो पहली औरत मरे।",
   [("The wife should not walk barefoot; keep pure gold in the wife's hair.", "औरत नंगे पांव ज़मीन पर न चले; औरत के बालों में खालिस सोना कायम रखें।"),
    ("Keep solid silver in the house; the Moon's remedy for comfort in old age.", "ठोस चांदी घर में; बुढ़ापे के आराम के लिए चंद्र का उपाय।"),
    ("For children's troubles the book prescribes cleansing the private parts with curd.", "औलाद की मंदी हालत में जाये महसूरा को दही से साफ़ करते रहना।")])
_r("Venus", 7, "जैसा यार वैसी नार - साथी का फल", "As the partner, so the wife",
   "Marriage and family good for Venus's 25 years; Venus and Mercury good for 37 years; long life (85-96).",
   "शादी, गृहस्थ और खानदान शुक्र की उम्र के 25 साल उत्तम; शुक्र-बुध का 37 साल उम्दा फल; उम्र 85-96।",
   "Partnership with the wife's male relatives in business brings money and family trouble; Rahu in 8 makes the wife unhappy; with Saturn and both luminaries in 1, impotence.",
   "औरत खानदान के मर्दों को कारोबार में हिस्सेदार बनाना माली खराबी; राहु 8 तो औरत का मंदा हाल।",
   [("Avoid business partnerships with the wife's male relatives.", "औरत खानदान के मर्दों को कारोबार में साझी न बनाएँ।"),
    ("With Rahu in 8, the wife should avoid black and blue clothes lifelong.", "राहु 8 तो औरत को उम्र भर काला-नीला कपड़ा गैर मुबारक।"),
    ("Avoid a white cow (or an extremely fair partner) - the book says either brings bad luck here.", "सफ़ेद गाय का ताल्लुक न हो।")])
_r("Venus", 8, "जली मिट्टी की चंडाल औरत", "Burnt earth: a harsh woman",
   "Helps in conflicts; with Moon, Mars and Mercury firm, Venus is not bad.",
   "जंग में मदद; चंद्र, मंगल, बुध कायम तो शुक्र मंदा नहीं।",
   "With house 2 empty, all of Venus is bad: in-laws sink, children's house ruined; a woman's hard words act like Mars-bad; elders' shadow shaky; standing surety ruins.",
   "2 खाली तो शुक्र सब मंदा; ससुराल की नाव डूबे, औलाद का घर बर्बाद; औरत का बोल पत्थर की लकीर; कसम पर ज़मानत न भरें।",
   [("Donate jowar (fodder), or bury it, for the wife's health.", "औरत की सेहत मंदी में चरी (ज्वार) का दान या ज़मीन में दबाना।"),
    ("Stop taking charity and bow at a temple - 'the enemy's head falls by itself'.", "दान लेना छोड़ें, मंदिर में सिर झुकाते रहें।"),
    ("Drop copper coins or flowers in a dirty drain; serve or donate a cow; take the blessings of mother, brother and sister.", "गंदे नाले में तांबे का पैसा या फूल डालना; गऊ सेवा या गऊ दान; माता, भाई, बहन का आशीर्वाद।")])
_r("Venus", 9, "मिट्टी की काली आंधी", "A black dust storm",
   "Wise minister, earns his bread even as a lakhpati; ancestors' wealth grows.",
   "अक्लमंद वज़ीर, लखपति होकर भी मेहनत की रोटी; बुज़ुर्गों का धन बढ़े।",
   "Children not as well-off; in Venus's 25th year marriage or cows make silver walls into burnt earth; Mars-bad, Mercury and Ketu poor; addictions and illness from about 17.",
   "औलाद का हाल अच्छा नहीं; शुक्र की 25 साला उम्र में चांदी की दीवारें जली मिट्टी; मंगल बद, बुध-केतु मंदे।",
   [("Drill a hole in a neem tree, put in square pieces of silver and close it with neem wood.", "नीम के पेड़ में सुराख़ करके चांदी के चौकोर टुकड़े डालें और सुराख़ नीम की लकड़ी से भरें।"),
    ("Keep Moon items (well, silver) or honey in the foundation of the house.", "मकान की बुनियाद में चंद्र की चीज़ें (चांदी) या शहद कायम।"),
    ("Do not overwork or shed blood needlessly.", "हद से ज़्यादा मेहनत या खून बहाना मुबारक नहीं।")])
_r("Venus", 10, "ख़्वाब हूरां - खुद शनि", "Dream of houris: Venus as Saturn",
   "With a good Saturn a righteous person; while the west wall stays kachcha, family and wealth are good; Mercury fine, no accidents.",
   "शनि उम्दा तो धरम मूरत; मगरिबी दीवार कच्ची तो परिवार-दौलत उम्दा।",
   "Many chances of affairs in youth; old age pines for children; illicit ties for 12 years ruin children, brothers and money; with Saturn in 5, eye trouble to the wife.",
   "जवानी में पराई औरतों का मौका; बुढ़ापे में औलाद को तरसे; पराई औरत से ताल्लुक 12 साल केतु, मंगल, चंद्र बर्बाद।",
   [("For illness, donate a cow or a kapila cow; a black kapila cow protects against Saturn.", "मंदी सेहत में गऊ या कपिला गाय का दान; काली कपिला गाय शनि के बुरे असर से बचाए।"),
    ("Avoid illicit relationships; keep the west wall of earth.", "पराई औरत से दूर रहें; मगरिबी दीवार कच्ची रखें।")])
_r("Venus", 11, "हसीं औरत (मर्द) माया के ताल्लुक में घूमता लट्टू", "A spinning top in matters of beauty and money",
   "Three brothers in one; a storekeeper for the world; daughters and wife bring wealth.",
   "तीन भाई खुद; जगत का भंडारी; कन्या-औरत से धन बढ़े।",
   "A man's 12 years are bad when Sun, Moon or Rahu join; with bad Saturn the wife suffers; Venus's 20-year period can be bad for sons; the wife should not keep the house's money.",
   "सूरज-चंद्र-राहु साथ तो मर्द का 12 साला अरसा मंदा; शनि मंदा तो औरत दुखिया; औरत घर की खज़ांची न हो।",
   [("Mars's help - Mars remedy or the wife's brothers' support - protects Venus.", "मंगल की मदद (मंगल का उपाय या औरत के भाइयों की मदद) शुक्र को बचाए।"),
    ("Donate oil in bad times; serve Mercury (girls).", "मंदे वक्त तेल का दान; बुध की पालना।")])
_r("Venus", 12, "आड़े वक्त की देवी - भवसागर पार करने वाली गऊ", "Goddess who helps in hard times: the wish-cow",
   "The wife's fortune rescues him when no one else will; good standing with authority; 37 years of the wife's happiness; enemies vanish; Venus is a Kamdhenu cow.",
   "जहाँ कोई मदद न करे, औरत का नसीबा फ़ौरन कामयाबी दे; राज ताल्लुक ऊंचा; 37 साला सुख औरत; कामधेनु गाय।",
   "With Rahu (in 2-7-6-12) family life is bad till 25; bad Mercury or harsh words of the wife bring smoke-filled nights; houses 7 and 2 empty make Venus all earth.",
   "राहु 2-7-6-12 तो गृहस्थ 25 तक बर्बाद; बुध मंदा या औरत की ज़ुबान तो रात धुएँ से दुखिया; 7-2 खाली तो शुक्र मिट्टी।",
   [("Donate in the wife's name, or have her give with her own hand; cow donation.", "औरत के नाम पर या औरत के हाथ से दान; गऊ दान।"),
    ("Serve cows always; avoid a blue cow and Rahu items.", "गाय की सेवा हमेशा मुबारक; नीली गाय और राहु की चीज़ें नहीं।")])

# ---------------- Mars
_r("Mars", 1, "मैदाने जंग और अदल की तलवार", "Sword of battle and justice",
   "Good health and authority; Saturn's trades (iron, wood, machinery, building) profit; protects in-laws and brothers.",
   "राजदरबार और अपना जिस्म उम्दा; शनि के कारोबार (लोहा, लकड़ी, मशीनरी, मकान) से नफ़ा; ससुराल-भाई को तारे।",
   "Mars-bad turns him into a comet for the family; free goods make his blood worth less than waste; Moon/Sun in 2-12 weigh on the father; Mercury in 3 and houses 7-9 empty sleep the luck.",
   "मंगल बद तो खानदान के लिए दुमदार सितारा; मुफ़्त माल से खून की कीमत फ़ुज़ला से कम; चंद्र-सूरज 2-12 तो पिता पर भारी।",
   [("For house 9 do Jupiter's remedy (keep Jupiter items); for house 7 serve Venus (Venus items or trades).", "घर 9 के लिए गुरु का उपाय या बृहस्पति की चीज़ें; घर 7 के लिए शुक्र की पालना।"),
    ("Keep away from free goods; the in-laws' dog and the company of wandering sadhus harm the brother.", "मुफ़्त माल से दूर; ससुराल का कुत्ता और फ़कीर साधु का साथ भाई के लिए ज़हर।")])
_r("Mars", 2, "धरम मूरत भाइयों की पालना करने वाला", "Righteous, maintains his brothers",
   "Wealth keeps growing and brothers help while Moon items are kept at the in-laws' (well and so on).",
   "भाइयों की पालना करता लोह-लंगर का मालिक; ससुराल के यहाँ चंद्र की चीज़ें कायम तो बरकत बढ़े।",
   "As Mars-bad, a snake in the sleeve; with Sun or Moon in 12, parents' condition bad until 28; idle and poor otherwise.",
   "मंगल बद तो आस्तीन का सांप; सूरज-चंद्र 12 तो 28 तक माता-पिता मंदे; आलसी-निर्धन।",
   [("Keep Moon items (a well and so on) at the in-laws' house.", "ससुराल के यहाँ चंद्र की चीज़ें (कुआँ वगैरह) कायम रहें।")])
_r("Mars", 3, "लोगों के लिए फलों का जंगल", "An orchard for others",
   "Brave, a friend and helper to the world; in-laws prosper through him; with Saturn in 9, protected from illness and death; houses and status good.",
   "शेर की तरह बहादुर, दुनियावी दोस्त और मददगार; ससुराल अमीर; शनि 9 तो मौत-बीमारी से बचाव, मकान उम्दा।",
   "Unlucky for his own comfort; Mars-bad as a caged lion; with Mercury-Saturn in 3/7 money trouble at home.",
   "अपनी माया व आराम में सब्ज़कदम; मंगल बद तो चिड़ियाघर का शेर; बुध-शनि 7-3 तो घर में माली खराबियाँ।",
   [("Keep ivory with you.", "हाथी दांत कायम रखना मुबारक।")])
_r("Mars", 4, "जलती आग - बड़ी का दरिया (मंगलीक)", "A burning fire (manglik)",
   "In the good state Shiva helps and Vishnu sustains; Sun-Jupiter in 8 with Moon in 4/9/3/11 calm it.",
   "नेक हालत में शिवजी मदद दे, विष्णु पालन करे।",
   "Mars-bad / manglik: burns its own flourishing clan by 28, harms mother, grandmother and mother-in-law; bitter tongue; ruins one side of the marriage; blind and weak in old age.",
   "मंगल बद या मंगलीक: 28 तक अपना गुलज़ार कबीला भस्म; माता, नानी, सास पर मंदा; कड़वा स्वभाव; एक तरफ़ का खानदान बर्बाद।",
   [("Clean the teeth with water every morning.", "हर रोज़ सुबह पानी से दांत साफ़ करना।"),
    ("Moon's remedy; or a tilak of banyan-root soil moistened with sweetened milk for stomach troubles.", "चंद्र का उपाय; बड़ की जड़ की मिट्टी का मीठे दूध से गीला तिलक।"),
    ("For fires or childlessness, bury an earthen pot filled with honey in a cremation ground; a deer skin for long illness; a square of silver.", "आग के वाकिआत या लावल्दी में शहद से भरा मिट्टी का बर्तन श्मशान में दबाना; लंबी बीमारी में मृगशाला; चांदी का चौकोर टुकड़ा।"),
    ("Nail iron into a south-facing door; keep away from one-eyed or childless people; feed sweets to sparrows; keep ivory.", "जनूबी दरवाज़े में लोहे की कील; काने-लावल्द से दूर; चिड़ियों को मीठा; हाथी दांत पास रखना।")])
_r("Mars", 5, "रईसों का बाप-दादा", "Father of the wealthy",
   "Every planet in 3-5-9 helps the others; Moon and Venus give good results whatever their state; good and bad both multiply fivefold; family of physicians.",
   "3-5-9 के सब ग्रह बाहमी मददगार; चंद्र-शुक्र हर हाल नेक; नेकी-बदी पाँच गुणा।",
   "Permanent residence away from the ancestral area gives childlessness; the beloved wrecks his fleet; no full night's sleep.",
   "जद्दी इलाके से बाहर मुस्तकिल रिहाइश लावल्दी दे; महबूब ही जहाज़ों की तबाही का बहाना; पूरी नींद नहीं।",
   [("Keep water at the head-side at night.", "रात को सिरहाने पानी रखें।"),
    ("Do not settle permanently away from the ancestral area.", "जद्दी इलाके से बाहर मुस्तकिल रिहाइश न करें।")])
_r("Mars", 6, "तरसिए की औलाद - संन्यासी साधु", "Child of the longing, an ascetic",
   "Fond of Mercury's arts (writing, music, languages) - the pen stronger than the sword; no lack of children or money; brothers prosper with him.",
   "बुध के कारोबार (तहरीर, राग, ज़ुबानदानी) का शौकीन, कलम तलवार से तेज़; औलाद-माया की कमी नहीं।",
   "Celebrations turn to mourning within days; brothers who grow richer than him face sudden loss; celebrating a first son's birth is a bad sign.",
   "जहाँ खुशी की महफ़िल वहाँ चंद दिन में मातम; भाई उससे ज़्यादा हों तो अचानक नुकसान।",
   [("Saturn's remedy for general family trouble; worship of girls (Mercury) for brothers; Moon items for the children.", "आम गृहस्थी मंदी में शनि का उपाय; भाइयों के लिए कन्या पूजन; औलाद के लिए चंद्र की चीज़ें।"),
    ("At a child's birth distribute salt or salty items instead of sweets.", "औलाद के जन्म पर मिठाई की जगह नमक या नमकीन बांटना।"),
    ("Brothers should keep giving him something from their earnings; if he refuses, float it in running water.", "भाई अपनी कमाई से उसे कुछ देते रहें; न ले तो चलते पानी में बहा दें।")])
_r("Mars", 7, "मीठा हलवा - विष्णु पालना", "Sweet halwa: Vishnu's nurture",
   "Everything he needs comes home; sweet food and a sweet life; raising a nephew helps; a minister's blood, master of mathematics; authority grows when Venus or Jupiter is in 1.",
   "सब कुछ घर में मिले; मीठी रोटी-पकवान से उम्दा ज़िंदगी; भतीजे की पालना मुबारक; राज हुकूमत बढ़े।",
   "Joined by Mercury, all turns bad; Mercury-Saturn in 6-7 make him take on others' deaths; company leaves its mark.",
   "बुध मिले तो सब रद्दी; बुध-शनि 6-7 तो पराई मौत लेता हो।",
   [("Build a small wall and keep pulling it down (Saturn's remedy) when Mercury is bad.", "बुध मंदा हो तो छोटी दीवार बनाकर गिराते जाना (शनि का उपाय)।"),
    ("If a widowed sister lives with you, give her something sweet every morning before starting work; raise a nephew.", "बेवा बहन साथ रहती हो तो हर सुबह उसे मीठा देकर काम शुरू; भतीजे की पालना।")])
_r("Mars", 8, "मौत का फंदा - पूरा मंगल बद", "The noose of death: full Mars-bad",
   "Steadfast and hard-working; with house 8's lord fine, harm falls on near relatives rather than himself; long life for himself.",
   "इस्तकलाली, मेहनती; मालिक टेवे पर मंदा नहीं, करीबी खून पर।",
   "The faster Mercury grows the worse Mars-bad becomes; a widow's word burns the house; younger brothers suffer; mother may die young when Mercury is in 6.",
   "बुध जितनी जल्दी बढ़े उतना बुरा मंगल बद; बेवा की बद्दुआ घर जलाए; छोटे भाई दुखी।",
   [("Give sweet tandoor bread to a dog for 40-43 days.", "40-43 दिन तंदूर की मीठी रोटी कुत्ते को देना।"),
    ("Sprinkle cold water on the hot griddle (tawa) every day before cooking.", "हर रोज़ गरम तवे पर ठंडे पानी के छींटे देना।"),
    ("Wear a silver chain on the neck; avoid a south door or a permanent underground furnace at home; the Mars-4 remedies also apply.", "गले में चांदी हर वक्त; दक्खन का दरवाज़ा या ज़मीनदोज़ भट्टी नहीं; मंगल 4 वाले उपाय भी।")])
_r("Mars", 9, "बुजुर्गों से चलता आया तख्त शाही", "A throne handed down from the elders",
   "Status arrives before him; a king himself by 28; Sun's authority always strong; with brothers united, a pair of lions.",
   "हुकूमत का सामान पहले; 28 में खुद राजा; सूरज का राज प्रबल; भाई मिलकर रहें तो शेरों का जोड़ा।",
   "Brothers separating burn like Lanka; Mars-bad makes him atheist and disgraced, begging from jackals; Saturn in 4 brings confinement.",
   "भाइयों की अलहदगी से लंका जले; मंगल बद तो नास्तिक-बदनाम; शनि 4 तो कैद।",
   [("Keep or tend a deer (book: 'हिरण का साथ या पालना').", "हिरण का साथ या पालना मुबारक।"),
    ("Obey the elder brother and keep the family united.", "बड़े भाई की ताबेदारी, मिलकर रहना।")])
_r("Mars", 10, "शेर की आँख - नज़र शनि पर (उच्च)", "Lion's eye, guided by Saturn (exalted)",
   "Like God visiting an ant's house: born to a poor house that becomes rich; a throne from birth; never childless; brother's life brings money.",
   "चींटी के घर भगवान: गरीब घर में जन्म, फिर धनाढ्य; जन्म से राजा की शान; लावल्द नहीं।",
   "Venus, Moon or papi in 2 delay children; Moon/Sun/Jupiter in 3-6 make Mercury a wasteland; with Sun in 4 or Moon in 6, blind in one eye.",
   "2 में शुक्र, चंद्र या पापी तो औलाद देर से; 3-6 में चंद्र-गुरु तो बुध वीरान; सूरज 4 या चंद्र 6 तो एक आँख से काना।",
   [("Keep a deer or tend one.", "हिरण का साथ या पालना।"),
    ("Do not sell gold from the house or let milk boil over ('बिके घर से सोना तो हो दूध जलता').", "घर से सोना न बिके, दूध न जले।")])
_r("Mars", 11, "चीता मंगल, दरबार गुरु के", "A cheetah in Jupiter's court",
   "A pet lion of spiritual temperament yet living like a king; the 'three dogs' and Ketu's things bring luck; parents rich by 13; good at 24 and 28 when Mercury-Saturn are good.",
   "पला हुआ पालतू शेर, फ़कीरी रूहानी हालत मगर भेष में राजा; तीन कुत्ते और केतु की चीज़ें मुबारक।",
   "As Mars-bad, Ketu (son) suffers and papi trouble him till their ages.",
   "मंगल बद तो केतु (लड़का) भला नहीं; पापी अपनी उम्र तक दुखिया करें।",
   [("Keep and serve a dog, or the 'three dogs of the world'.", "कुत्ता या दुनिया के तीन कुत्तों की पालना।")])
_r("Mars", 12, "गरजता शेर, ख़ालिस खून, दमकता परिवार", "Roaring lion, pure blood, a shining family",
   "Serves sadhus and the guru; enemies tremble; houses 8 and 3 stop giving bad results; Mercury and papi fall silent.",
   "साधु-गुरु की सेवा; दुश्मन धड़कें; 8-3 के ग्रह मंदा असर न दें।",
   "Heavy on elder brothers until 28; red clothing on the head harms elder brothers; Mercury keeps its bad effect where it is.",
   "28 तक बड़े भाइयों पर भारी; सिर पर लाल रंग बड़े भाइयों के लिए गैर मुबारक।",
   [("Eat sweets and feed sweets to others; offer water with sugar to the Sun; give sweet roti to dogs.", "मीठा खाना और खिलाना; सूरज को मीठा मिला पानी देना; कुत्ते को मीठी रोटी।"),
    ("Wear Sun or Jupiter colours on the head (khaki, yellow), not red; the elder brother should give him milk instead of water.", "सिर पर सूरज-बृहस्पति के रंग (खाकी, पीला), लाल नहीं; बड़ा भाई उसे पानी की जगह दूध पिलाए।")])

# ---------------- Mercury
_r("Mercury", 1, "राजा या हाकिम मगर ...", "King or officer",
   "Rain of wealth for the Sun's relatives; healthy and in authority even if not religious; never short of food; when house 7 has a planet, Saturn follows Mercury's lead.",
   "सूरज के रिश्तेदारों के लिए धन की बारिश; राज, सेहत, ज़र उम्दा; रिज़क मंदा नहीं।",
   "Mischief and bad name; risk of scandal in youth; Mercury's things may sour, ungrateful.",
   "शरारती-बदनाम; जवानी में तोहमत का खतरा; तोता-चश्म।",
   [("Get the nose pierced and keep the hole open for 4-5 days.", "नाक छेदन करवाकर सिर्फ़ 4-5 दिन सुराख़ कायम रखें।")])
_r("Mercury", 2, "योगी-राजा, मतलबपरस्त ब्रह्मज्ञानी", "Yogi-king, a self-seeking sage",
   "Alone it saves everyone; pearls fall from pen and tongue; benefits in-laws; with 8 and 6 empty an excellent head line.",
   "अकेला सबको तारे; कलम-ज़ुबान से मोती; ससुराल तारे।",
   "Sister, daughter and aunt carry a poisonous effect; a sister-in-law's company is unlucky with Venus in 2-3-8-9.",
   "बहन, लड़की, बुआ ज़हरी असर; साली का साथ गैर मुबारक।",
   [("Nose piercing (keep the hole at least 96 hours), best before age 12 but helpful later too.", "नाक छेदन (कम से कम 96 घंटे सुराख़), 12 साल से पहले ज़्यादा फ़ायदेमंद।")])
_r("Mercury", 3, "थूकने वाला कोढ़ी", "The spitting leper (harsh)",
   "Brothers and kin help him; Mercury's things good with Mars-Mercury good.",
   "भाई-बंद मददगार; मंगल-बुध उम्दा तो दौलत-कबीला बढ़े।",
   "Worse than teeth or a sword to his own clan; father's earnings vanish into the south-east well until about 34; Mercury foods often bring illness; a south door ruins wife, wealth and in-laws.",
   "अपने कबीले पर तलवार से ज़्यादा बुरा; पिता की कमाई 34 तक कुएँ में; मूंग वगैरह बीमारी का बहाना; दक्खन का दरवाज़ा तबाही।",
   [("Clean the teeth with alum every day.", "हर रोज़ फिटकरी से दांत साफ़ करना।"),
    ("Soak whole moong overnight and feed it to animals in the morning for 43 days (business).", "रात को साबुत मूंग भिगोकर सुबह जानवरों को डालना, 43 दिन (व्यापार)।"),
    ("Bury palash leaves washed in milk under a stone in a lonely place by day; float the ash of burnt yellow cowries in a river.", "दूध से धोए ढाक के पत्ते दिन में वीराने में गड्ढे में पत्थर रखकर दबाना; पीली कौड़ियों की राख दरिया में।"),
    ("Donate a goat; serve birds; keep or serve a dog (Ketu).", "बकरी का दान; परिंदों की सेवा; कुत्ता पालना।")])
_r("Mercury", 4, "राजयोग - हुनरमंद", "Raj yoga, the skilled one",
   "An unending river of wealth; sister and daughter bring authority; with Moon in 3-4-6, a priceless diamond; family, age and wealth long.",
   "धन का कभी खत्म न होने वाला दरिया; बहन-बेटी से राज; चंद्र 3-4-6 तो अनमोल हीरा।",
   "Heavy on the mother; with Rahu or Ketu bad, men's condition suffers; travels and advisers mislead.",
   "माता पर मंदा; राहु-केतु मंदे तो मर्दों की हालत मंदी; सफ़र और सलाहकार मंदे।",
   [("When Mercury is bad, Sun items help; for wealth, Jupiter's remedy.", "मंदे बुध में सूरज की चीज़ों का उपाय; दौलत के लिए बृहस्पति का उपाय।")])
_r("Mercury", 5, "खुशहाल - उसके मुँह से निकला ब्रह्म वाक्य", "Prosperous: his words come true",
   "Giver of wealth and family; Moon items rescue; the wife helps in every way; never bad for children.",
   "दौलत और परिवार का दाता; चंद्र की चीज़ें तारें; स्त्री हर तरह मददगार; औलाद के लिए मंदा नहीं।",
   "His own tongue causes trouble; houses 3-4-7-9 spoil when Mercury is afflicted; can be unlucky for the father.",
   "अपनी ही ज़ुबान खराबी का बहाना; पिता के लिए मंदभाग।",
   [("Control the tongue; keep Moon items.", "ज़ुबान पर काबू; चंद्र की चीज़ें कायम।")])
_r("Mercury", 6, "गुमनाम योगी और दिल का राजा (उच्च)", "Unknown yogi, king of hearts (exalted)",
   "Self-made rich from nothing; Mercury gives the effect of whichever planet is firmly placed; honest wealth multiplies; flowers and girls are good omens; never bad for a daughter's chart.",
   "फ़कीरी से खुद साख्ता अमीर; जो ग्रह कायम उसी का असर; ईमानदारी के धन की बरकत; कन्या का शगुन मुबारक।",
   "With Venus bad or Mercury bad: eyesight and old age suffer; mother early when Mars is in 4/8; children after 34.",
   "शुक्र रद्दी या बुध मंदा तो नज़र कमज़ोर, बुढ़ापा मंदा; मंगल 4-8 तो माता छोटी उम्र।",
   [("When Mercury is bad, bury a vessel of milk in a lonely place; when the Moon is helpful, bury a bottle of Ganga water in farmland.", "बुध मंदा तो दूध का बर्तन बाहर वीराने में; चंद्र मददगार तो गंगाजल की बोतल खेती की ज़मीन में।"),
    ("For children, the wife wears a silver ring on her left hand.", "औलाद के लिए स्त्री के बाएँ हाथ में चांदी का छल्ला।")])
_r("Mercury", 7, "दुनिया के लिए पारस", "A philosopher's stone for others",
   "Helps strangers after a brief meeting; old age always good; treasure always helps though cleverness may not; a lineage-saving diamond when awake.",
   "थोड़ी मुलाकात पर बेबहा मदद; बुढ़ापा उत्तम; खज़ाने की दौलत हमेशा मदद पर।",
   "With Mars (7-8) both turn bad; family thin till 34.",
   "मंगल 7-8 से हर दो मंदे; 34 तक खानदानी हाल हल्का।",
   [("No specific upay in the text; keep Mercury awake (a planet in house 1 or keep green items).", "किताब में खास उपाय नहीं।")])
_r("Mercury", 8, "बीमारी, ज़हमत और लानत का घर", "House of illness, trouble and curse",
   "Loss is limited to money - income may halve but never go to zero; Sun or Moon good in 4 wash its poison.",
   "नुकसान सिर्फ़ माली - आमदन आधी, सिफ़र नहीं; 4 में सूरज-चंद्र उम्दा तो ज़हर धुले।",
   "A planet in 2 fills Mercury with poison; sudden deceit at court; house 8 empty sounds the drum of bad news.",
   "2 में कोई ग्रह तो बुध ज़हरी; राजदरबार में अचानक धोखा; 8 खाली तो मंदी का बाजा।",
   [("Float a copper pot filled with whole moong in a river, and give an earthen pot filled with sugar, around the birthday.", "जन्मदिन से पहले-बाद साबुत मूंग भरा तांबे का घड़ा दरिया में बहाना; खांड से भरा मिट्टी का बर्तन।"),
    ("Keep rain water or milk on the roof; a silver nose ring for a daughter; a black mole made with surma (book).", "छत पर वर्षा का पानी या दूध; लड़की की नाक में चांदी का छल्ला; सुरमे से स्याह तिल।"),
    ("Avoid burning-glasses and red clothes for girls of the house.", "आतशी शीशा और लड़की के लाल कपड़े न हों।")])
_r("Mercury", 9, "कोढ़ी तथा राजा मुश्तरका", "Leper and king together",
   "With Moon, Ketu or Jupiter in 3-6-7-9-1, never bad - dry clouds rain pearls.",
   "3-6-7-9-1 में चंद्र, केतु, गुरु तो बुध कभी मंदा नहीं; सूखे बादल मोती बरसाएँ।",
   "Otherwise unreliable promises and deceit; short life when Jupiter is alone in 8-6-10; wife and children trouble.",
   "वादा फ़रामोशी, धोखा; गुरु अकेला 8-6-10 तो अल्पायु; औरत-औलाद में खराबी।",
   [("Nose piercing is the main remedy.", "नाक छेदन सबसे उत्तम।"),
    ("Wear yellow cloth washed in river water; bury silver under the house and wear silver; feed a cow.", "दरिया के पानी से धुला पीला कपड़ा; घर की तह में चांदी, जिस्म पर चांदी; गऊ ग्रास।"),
    ("A round iron object coloured red protects from Mercury's poison; give mushrooms in an earthen pot at a place of worship; avoid green.", "मंगल रंग की लोहे की गोल चीज़; खुम्भ मिट्टी के बर्तन में धर्म स्थान में; हरा रंग मंदा।")])
_r("Mercury", 10, "दुनियादार - मर्दों की बरकत", "Worldly: blessing for men",
   "Work prospers for men; sea voyages bring pearls when house 2 is empty.",
   "मर्दों के काम में बरकत; 2 खाली तो समुंदर के सफ़र से मोती।",
   "Unlucky for women and children; deceit and short life with Jupiter alone in 8-6-10.",
   "औरतों और बच्चों के लिए गैर मुबारक।",
   [("Mercury's general remedy: float a copper coin with a hole in a river (Farman 9).", "बुध का आम उपाय: तांबे के सुराख़ वाले पैसे को दरिया में बहाना।")])
_r("Mercury", 11, "दौलतमंद जन्म से - मगर बुध उल्लू का बच्चा", "Rich from birth, yet Mercury is an owlet",
   "After 34 comfort comes and Mercury becomes a saving diamond.",
   "34 के बाद आराम, बुध मददगार और तारने वाला हीरा।",
   "Before that a foolish, sick Mercury; with bad Saturn twice as bad; papi bad till their ages; father's shadow uncertain.",
   "पहले बुध उल्लू का बच्चा और कोढ़ी; शनि मंदा तो दो गुणा मंदा; पिता के साये का भरोसा नहीं।",
   [("Wear a copper coin (or a small piece of copper) at the neck.", "गले में तांबे का पैसा या तांबे का टुकड़ा।")])
_r("Mercury", 12, "जिसे दुखिया देखकर आसमान भी रो दे", "So troubled the sky weeps",
   "With Saturn or Jupiter together, a pool of nectar; Sun or Saturn in 12 take no poison; a fish line with Jupiter-Saturn makes it excellent.",
   "शनि-गुरु साथ तो बुध अमृत का कुंड; मच्छ रेखा तो उत्तम।",
   "Marriage at 25 makes wife and father weep; tongue, pen and Mercury's things bring disgrace; lying and false promises ruin.",
   "25 में शादी तो औरत-पिता रोएँ; ज़ुबान, कलम बदनामी का बहाना; झूठ और वादाखिलाफ़ी तबाही।",
   [("Keep clean, bright steel (stainless) on the body.", "खालिस फ़ौलाद (ज़ंग न लगे) जिस्म पर, जितना साफ़-चमकदार उतना अच्छा।"),
    ("A saffron or black tilak on the forehead (not ash); float an empty new earthen pot in running water.", "माथे पर केसर या स्याह तिलक (राख का नहीं); कोरा घड़ा चलते पानी में बहाना।"),
    ("Serve dogs / the 'three dogs'; take advice from others; nose piercing; control the tongue and keep promises.", "कुत्ते या तीन कुत्तों की मदद; दूसरों से सलाह; नाक छेदन; ज़ुबान पर काबू, वायदा निभाना।")])

# ---------------- Saturn
_r("Saturn", 1, "जब मंदा हो तो तीन गुणा मंदा, नहीं तो तीनों काल उत्तम", "Thrice bad when bad, otherwise good in all three ages",
   "With houses 7 and 10 empty (fish line), wealth beyond count and a happy life; Saturn's goods prosper in the good state.",
   "7-10 खाली (मच्छ रेखा) तो माल माया बेशुमार, उम्र सुखी; नेक हालत में शनि का सामान उत्तम।",
   "With Venus in 1 (crow line) even a king is brought to dust; Rahu/Ketu in 4 or 10 or Mercury bad: incomplete education; a west-facing house, alcohol or empty romance trigger its worst.",
   "शनि-शुक्र 1 (काग रेखा) तो तख्त हज़ारी भी मिट्टी; राहु-केतु 4-10 या बुध मंदा तो तालीम अधूरी; पश्चिम के दरवाज़े का मकान, शराब से मंदा।",
   [("For money, the Sun's help or keeping a monkey.", "माली मदद के लिए सूरज की मदद या बंदर पालना।"),
    ("For health and studies, a tilak of banyan-root soil wet with sweetened milk; bury surma in the ground.", "सेहत-तालीम के लिए मीठे दूध से बड़ की जड़ की मिट्टी का तिलक; ज़मीन में सुरमा दबाना।"),
    ("Avoid alcohol and a house with a west-facing door.", "शराब और पश्चिम दरवाज़े वाले मकान से परहेज़।")])
_r("Saturn", 2, "गुरु शरण", "Under the guru's shelter",
   "Lives according to means; good health; let houses be built as and when they come; good for in-laws in the right conditions.",
   "हस्ब हैसियत जीवन; उम्दा सेहत; मकान जैसा और जब बने बनने दें।",
   "As Mars-bad: cheat and quarreller, eye trouble; fire at the in-laws at the time of marriage; oil on the tilak spot is unlucky.",
   "मंगल बद तो चोर-फ़रेबी; शादी के वक्त सास-ससुर घर आग; तिलक की जगह तेल गैर मुबारक।",
   [("Walk barefoot to a temple and confess your faults - it protects from sudden calamity.", "नंगे पांव मंदिर जाकर भूल मान लेना नागहानी बला से बचाए।"),
    ("Feed milk to a snake (Moon's remedy) for the in-laws; a milk or curd tilak instead of oil; a brown buffalo is lucky (not black or two-coloured).", "सांप को दूध पिलाना; तेल की जगह दूध-दही का तिलक; भूरी भैंस मुबारक।")])
_r("Saturn", 3, "अगर हुए तो दो गुणा मंदा", "If bad, doubly bad",
   "Houses are always good, especially when a dog is kept; wealth and eyesight grow; a dark room at the end of the house is lucky for money.",
   "मकानों का असर उत्तम, खासकर कुत्ता रखें; धन बढ़े, नज़र उम्दा; मकान के आखिर में अंधेरी कोठरी मुबारक।",
   "Without a dog, Ketu bites; east or south doors are unlucky - a stone at the south door brings deaths; doubly bad in money matters.",
   "कुत्ता न रखें तो केतु काटे; पूर्व या दक्षिण का दरवाज़ा गैर मुबारक; माली हालत में दो गुणा मंदा।",
   [("Keep a dog, or serve the 'three dogs of the world'.", "कुत्ता रखें या दुनिया के तीन कुत्तों की सेवा।"),
    ("Ketu's remedy helps (not needed if Ketu is in 10 or 3); keep a dark room at the end of the house; avoid east and south doors.", "केतु का उपाय मददगार; मकान के आखिर में अंधेरी कोठरी; पूर्व-दक्षिण दरवाज़े से बचें।")])
_r("Saturn", 4, "पानी का सांप", "A water snake",
   "Saturn's trades and medicine help in bad health and poverty; poison becomes its own medicine; all forms of love present.",
   "शनि के कारोबार और हकीमी मददगार; ज़हर खुद अपनी दवाई।",
   "A new house of his own brings snake-bite to the mother and poison to the maternal uncle; milk at night poisonous; selling snake oil or drinking alcohol brings childlessness.",
   "नया मकान बने तो माता को सांप लड़े, मामू को ज़हर; रात का दूध ज़हरी; सांप का तेल बेचना या शराब लावल्दी।",
   [("Feed milk to a snake, or serve fish, buffaloes, crows and labourers - it washes Saturn's poison and protects the mother's family.", "सांप को दूध, या मछली, भैंस, कौवा, मज़दूर की पालना शनि की ज़हर धोए।"),
    ("Pour milk into a well.", "कुएँ में दूध गिराना।"),
    ("Avoid alcohol, milk at night, and building a new house in a hurry.", "शराब, रात का दूध और नया मकान बनाने से परहेज़।")])
_r("Saturn", 5, "बच्चे खाने वाला सांप", "The snake that eats children",
   "All other results of Saturn and Jupiter good; with Ketu good children grow, with Rahu houses get built.",
   "बाकी सब फल उत्तम, शनि-बृहस्पति दोनों का; केतु भले तो औलाद, राहु से मकान।",
   "Building a new house of his own brings childlessness; harms sons; Mars-bad kills children.",
   "नया मकान बने तो लावल्दी का सामान; शनि का सांप लड़के खाए; मंगल बद तो बच्चे मारे।",
   [("Keep items of Saturn's enemies (Sun: jaggery, copper; Moon; Mars: fennel, sugar, honey) in the west part of the ancestral house.", "जद्दी मकान के पश्चिमी हिस्से में शनि के दुश्मनों (सूरज: गुड़-तांबा; मंगल: सौंफ़-खांड-शहद) की चीज़ें कायम।"),
    ("Take almonds to a temple and bring half back home to keep (do not eat them).", "बादाम धर्म स्थान में ले जाकर आधे वापस घर में कायम रखें (खाएँ नहीं)।"),
    ("For children, keep Mars or Jupiter items in the ancestral house.", "औलाद के लिए जद्दी मकान में मंगल या बृहस्पति की चीज़ें।")])
_r("Saturn", 6, "लेख के स्याह", "Dark writing of fate",
   "Results follow Ketu's state; a famous sportsman, better than the father; travel brings good results; after 42 the sky is washed.",
   "जैसा केतु वैसा शनि; बाप से उम्दा नामवर खिलाड़ी; सफ़र से उम्दा नतीजे; 42 के बाद उम्दा।",
   "Marriage before 28 acts like a snake on the chest; building a house before 48 (or before Saturn's age) is unlucky; leather goods bought bring trouble.",
   "28 से पहले शादी तो छाती पर सांप; 48 तक मकान बनाना मुबारक नहीं; चमड़े की चीज़ें खरीदना मंदा।",
   [("Bury an earthen pot filled with mustard oil under the bed of a pond or river.", "सरसों के तेल से भरा मिट्टी का बर्तन तालाब या दरिया के पानी के अंदर ज़मीन में दबाना।"),
    ("Float coconut or almonds in water; keep a fully black dog; serving snakes increases children.", "नारियल या बादाम पानी में बहाना; पूरा काला कुत्ता; सांप की सेवा से औलाद बढ़े।"),
    ("Do not build a house before 48; avoid marriage before 28.", "48 तक मकान न बनाएँ; 28 से पहले शादी न करें।")])
_r("Saturn", 7, "कलम विधाता (रिज़क)", "Pen of destiny: livelihood (exalted)",
   "With friends (Mercury, Venus, Rahu) in 3-5-7, all good; government brings wealth equal to marrying five daughters; even if everything is sold, the old threshold brings it back.",
   "दोस्त ग्रह 3-5-7 में तो सब उम्दा; राजदरबार से धन; पुरानी दहलीज़ कायम तो सब वापस।",
   "Alcohol is the first sign of the crow line and Saturn's bad effect; danger from weapons.",
   "शराबखोरी काग रेखा और मंदे शनि की निशानी; हथियार से नुकसान का डर।",
   [("Bury a flute filled with sugar (khand) outside, if Saturn is awake; if asleep, the honey-pot remedy.", "खांड से भरी बांसुरी बाहर दबाना (शनि सोया न हो); सोया हो तो शहद के बर्तन का उपाय।"),
    ("Avoid alcohol.", "शराब से परहेज़।")])
_r("Saturn", 8, "हैडक्वार्टर", "Saturn's headquarters",
   "Effects depend on Mercury and papi; when Ketu is in earlier houses Saturn helps.",
   "चाल वैसी जैसा बुध या पाप; केतु पहले घरों में तो शनि मददगार।",
   "Enemies with it make the snake full of poison; house 2 empty: miserable till the grave; more chest hair means a life of servitude.",
   "शत्रु साथ हों तो ज़हर भरा नाग; 2 खाली तो कब्र तक दुखिया।",
   [("Keep a pure square piece of silver with you (Moon's remedy) - it also reveals Saturn's true nature.", "खालिस चांदी का चौकोर टुकड़ा पास रखना।"),
    ("Bathe with milk sitting on a stone (not on bare earth).", "पत्थर पर बैठकर दूध से स्नान; मिट्टी पर बैठकर नहीं।"),
    ("Avoid alcohol.", "शराब से परहेज़।")])
_r("Saturn", 9, "कलम विधाता - मकान", "Pen of destiny: houses",
   "Estates and a large clan for three generations; 60 good years, even all life, if he is helpful to others; a stone buried in the birth house is a lucky sign; children born later live.",
   "जागीर, भारी कबीला, तीन पुश्त; 60 साल उम्दा, शर्त पर-उपकारी; घर में जन्म का गड़ा पत्थर मुबारक।",
   "Firewood or lumber on the roof is the first sign of trouble; fires; Saturn's goods bad while Jupiter's and Moon's goods profit.",
   "छत पर ईंधन-लकड़ी मंदे असर की पहली निशानी; आग के वाकिआत; शनि की चीज़ें मंदी।",
   [("When trouble comes after the parents, Jupiter's remedy.", "माता-पिता के बाद तकलीफ़ तो बृहस्पति का उपाय।"),
    ("Do not store firewood or lumber on the roof; be helpful to others.", "छत पर ईंधन-लकड़ी न रखें; पर-उपकारी रहें।")])
_r("Saturn", 10, "लेख का कोरा खाली कागज़", "The blank paper of fate",
   "If it helps the planet in house 1 it is twice as good - Saturn as Sheshnag's throne for one who works patiently and steadily; in-laws rich when Mercury comes to 7.",
   "खाना 1 के ग्रह का मददगार हो तो 2 गुना उम्दा; स्थिर होकर बैठकर काम करने वाले के लिए शेषनाग सिंहासन।",
   "Otherwise twice the enemy of house 1; killing with weapons brings 27 bad years for wealth; Sun/Moon/Mars with it blind all planets.",
   "वरना खाना 1 के ग्रह का 2 गुना दुश्मन; हथियार से हत्या तो 27 साल धन मंदा।",
   [("When Saturn's effect is bad, Jupiter's help.", "शनि का असर मंदा तो बृहस्पति की मदद मुबारक।"),
    ("Work steadily and patiently; avoid violence.", "स्थिर होकर काम; हिंसा से दूर।")])
_r("Saturn", 11, "लिखे विधाता - खुद विधाता", "Destiny itself writes",
   "Decides on the basis of Rahu and Ketu; increases good planets; at 11-23-36-48... years the verdict comes - if good, earth turns to gold.",
   "राहु-केतु के हाल पर फ़ैसला; उत्तम ग्रह बढ़ाए; नेक हुआ तो मिट्टी को हाथ डाले तो सोना।",
   "If bad, gold turns to earth; Mercury's things (daughter, sister) suffer; fraudulent money becomes one's shroud; a south door spoils money.",
   "मंदा हुआ तो सोना भी मिट्टी; बुध की चीज़ें (लड़की, बहन) मंदी; बेईमानी का धन कफ़न का बहाना।",
   [("In general Jupiter's remedy; keep a pitcher (kumbh) filled with water - good in all bad states.", "आम हालत में बृहस्पति का उपाय; पानी से भरा घड़ा (कुंभ) कायम रखना।"),
    ("Pour Saturn's liquids (mustard oil, alcohol) on the ground at sunrise; never drink alcohol - pour it on the ground instead.", "सुबह सूरज निकलते वक्त सरसों का तेल या शराब ज़मीन पर गिराना; शराब मुँह में न डालें, ज़मीन पर गिरा दें।"),
    ("When Rahu or Ketu show bad signs, Mars's remedy plus strict celibacy (control of the langot) for a year.", "राहु-केतु मंदे हों तो मंगल का उपाय और एक साल लंगोटे पर पूरा काबू।")])
_r("Saturn", 12, "कलम विधाता - आराम", "Pen of destiny: rest",
   "No enemies remain; Saturn guards him at night like a protecting serpent; many houses get built - let them; brave like a trident-bearer.",
   "ज़माने में दुश्मन बाकी न रहे; रात को सिरहाने बैठकर रक्षा करने वाला अज़दहा; मकानात बहुत बनेंगे।",
   "Lying, adultery and alcohol cancel even the fish line; eye trouble comes first, then Saturn's bad phase; love of taste ruins.",
   "झूठ, ज़िनाकारी, शराब से मच्छ रेखा का भी नेक असर नहीं; दर्द आँख पहली निशानी; ज़ुबान का चस्का बर्बादी।",
   [("Keep almonds in the south-east corner of a dark room.", "अँधेरी कोठरी के जुनूब-मशरिकी कोने में बादाम।"),
    ("Avoid lies, adultery and alcohol.", "झूठ, ज़िनाकारी, शराब से परहेज़।")])

# ---------------- Rahu
_r("Rahu", 1, "सीढ़ी पर चढ़ने वाला हाथी", "An elephant climbing the stairs",
   "Wealth with Rahu's help to the Sun; children certain; a rich man when Venus is in 7; while Mercury and Venus are good, the eclipse is mild.",
   "राहु सूरज की मदद करे तो धन; औलाद ज़रूर; शुक्र 7 तो आला मालदार; बुध-शुक्र उम्दा तो ग्रहण मंदा नहीं।",
   "Eclipses the house where the Sun sits; blocks the mother's family and own income; needless expense; transfers many but limited promotion; litigation trouble.",
   "सूरज बैठा होने वाले घर में ग्रहण; माता खानदान और आमदन में रोड़ा; बेवजह खर्च; तबदीली ज़्यादा, तरक्की महदूद।",
   [("Keep a cat's placenta wrapped in Sun-coloured cloth (book); donate Sun items in good and bad times.", "बिल्ली की जेर सूरज रंग कपड़े में; सूरज की चीज़ों का दान।"),
    ("The Moon's remedy (silver).", "चंद्र का उपाय (चांदी)।")])
_r("Rahu", 2, "राजा गुरु के मातहत - बरसाती बादल", "Under a royal guru: a monsoon cloud",
   "Long life and good living, a king even if of a jungle; never imprisoned; does no mischief at night.",
   "उम्र लंबी, गुज़रान उम्दा; जंगल का ही सही राजा; कैद नहीं।",
   "Lives on free goods yet avoids giving charity; sins even in a temple; a new kitchen chimney in the north-west corner smokes out him, his in-laws and family between 36 and 42.",
   "मुफ़्त माल खाए, खैरात से परहेज़; धर्म मंदिर में बैठा पापी; शुमाल-मगरिबी कोने में नया रसोई धुआँ 36-42 में खानदान का धुआँ।",
   [("Keep a solid silver ball with you (against theft and in-law trouble).", "चांदी की ठोस गोली पास रखना।"),
    ("Keep Jupiter items (gold, saffron, yellow) on the body; avoid a new kitchen in the north-west corner.", "बृहस्पति की चीज़ें (सोना, केसर, पीली) जिस्म पर या पास; शुमाल-मगरिबी कोने में नई रसोई नहीं।")])
_r("Rahu", 3, "उम्र व दौलत का मालिक रईस - गोली बंदूक लिए पहरेदार", "Rich master of life and wealth: an armed guard (exalted)",
   "Dreams come true two years ahead; never childless; estates when the Sun is good.",
   "दो साल पहले खबर देने वाला सच्चा ख़्वाब; लावल्द नहीं; जागीरों का मालिक।",
   "A foolish friend harms more than an enemy; with Mercury-Sun in 3 a widowed sister; Mercury and Ketu poor till 34 when house 12 has a planet.",
   "बुरा यार अहमक से कम नहीं; बुध-सूरज 3 तो बहन दुखी; 12 में कोई ग्रह तो 34 तक बुध-केतु मंदे।",
   [("In bad times the Moon's remedy.", "मंदे वक्त चंद्र का उपाय।")])
_r("Rahu", 4, "धर्मी मगर धन-दौलत के आग-ग़म", "Religious, yet grieves over money",
   "Religious until Rahu is 'raised'; when the Moon is good the elephant bathes in wealth; wealth from in-laws and marriage.",
   "राहु खड़ा न करे तो धर्मी; चंद्र उत्तम तो हाथी माया में नहाए; ससुराल से धन।",
   "Raising Rahu - building toilets or furnaces, stockpiling coal, changing only the roof - brings money loss.",
   "राहु खड़ा करना - टट्टी खाना, भट्टी बनाना, कोयले के अंबार, सिर्फ़ छत बदलना - धन हानि।",
   [("Do not build toilets or furnaces, stockpile coal, or change only the roof; when repairing a roof, reuse some of the old material.", "टट्टी, भट्टी, कोयले के अंबार और सिर्फ़ छत बदलने से बचें; छत की मरम्मत में पुराना सामान थोड़ा शामिल करें।")])
_r("Rahu", 5, "शरारती औलाद - गर्क मगर ...", "Mischievous children",
   "Bad times pass like a thought and wealth rains when the Moon or a male planet is in 10, or the Moon in 4.",
   "चंद्र या नर ग्रह 10 में या चंद्र 4 में तो मंदा ज़माना ख़्याल की तरह गुज़रे, धन की बारिश।",
   "Not celebrating children's festivals extinguishes the son's lamp; first wife may not see children when Saturn is bad; much spent on illness.",
   "औलाद के त्योहार न मनाने वाले को नर औलाद का चिराग बुझा; शनि मंदा तो पहली स्त्री औलाद न देखे।",
   [("Perform the marriage rites twice with the same wife.", "एक ही औरत से दो बार शादी की रस्म।"),
    ("Place a silver strip under the first threshold of the ancestral house, keep a cow, or keep a small solid silver elephant; avoid Saturn's misdeeds.", "जद्दी मकान की पहली दहलीज़ के नीचे चांदी का पतरा, गाय कायम, या चांदी का ठोस हाथी; शनि की मंदी कारवाइयों से परहेज़।"),
    ("Celebrate children's birthdays and festivals.", "औलाद के त्योहार और खुशी के दिन मनाएँ।")])
_r("Rahu", 6, "फांसी काटने वाला मददगार (उच्च)", "The helper who cuts the noose (exalted)",
   "Breaks even a hangman's rope; kills enemies on high mountains; high mental power; always guards the native.",
   "गले में फांसी की रस्सी भी तोड़ने वाला; पहाड़ ऊंचे जा दुश्मन मारे; दिमागी ताकत उत्तम।",
   "With Mercury or Mars in 2 bad, burns itself; illness hard to diagnose; money declines; the house is robbed.",
   "बुध-मंगल 2 मंदे तो आग जली; बीमारी का पता न चले; माया घटे, घर लुटे।",
   [("A fully black dog is a good omen; keep a lead or coin ball or a piece of black glass.", "पूरा काला कुत्ता उम्दा शगुन; सीसे या सिक्के की गोली या काला शीशा।")])
_r("Rahu", 7, "चंडाल - लक्ष्मी का धुआँ निकालने वाला", "The chandal who smokes out Lakshmi",
   "Rich and protected by Saturn; enemies die at court; high status in government.",
   "दौलत का राखा; शनि देव रक्षा करें; शत्रु दरबार में मरें; राज ताल्लुक ऊंचा।",
   "Marriage before 21 (or in the 21st year) brings a ruined married life and affairs; wife and family unhappy; even the tree he sits under is uprooted; Ketu worst.",
   "21 साल से पहले या 21वें साल शादी बेमानी; अय्याश; जिस दरख्त तले बैठे वह जड़ से उखड़े; केतु सबसे मंदा।",
   [("At the wedding, the girl's parents give her a piece of pure silver at the moment of kanyadan; she keeps it for life and never sells it.", "शादी के वक्त कन्यादान के साथ लड़की को खालिस चांदी की डली दी जाए; वह उम्र भर रखे, बेचे नहीं।"),
    ("Keep a silver brick at home and a sealed vessel of river water with silver in it; float coconut in a river (Saturn's remedy).", "घर में चांदी की ईंट और दरिया के पानी में चांदी डालकर बंद बर्तन; नारियल दरिया में बहाना।"),
    ("If married before 21, place a silver glass of Ganga or river water with silver in it at a place of worship, and keep another at home.", "21 से पहले शादी हो चुकी हो तो चांदी के गिलास में गंगाजल और चांदी का टुकड़ा धर्म स्थान में और एक घर में।")])
_r("Rahu", 8, "कूच नक्कारा व मौत के पैगाम का मालिक - कड़वा धुआँ", "Drum of departure: bitter smoke",
   "Not bad when Mars nek is in 12; its secret opens by keeping a square silver piece for 43 days.",
   "मंगल नेक 12 में तो राहु मंदा नहीं; चौकोर चांदी 43 दिन पास रखने से भेद खुले।",
   "Mars-bad elsewhere sounds the drum of death; quarrels, litigation and waste; a south door, changing only the roof, or a furnace near the house are bad.",
   "बाकी घरों में मंगल बद तो मौत का नक्कारा; झगड़े, अदालती खर्च; दक्खन का दरवाज़ा, सिर्फ़ छत बदलना, भड़भूँजे की भट्टी मंदी।",
   [("Keep a square piece of silver with you for 43 days.", "चौकोर चांदी का टुकड़ा 43 दिन पास रखना।"),
    ("In a year when Rahu comes to 8, from the 8th month after the birthday take almonds to a temple daily and bring half back, until the next birthday.", "जिस साल राहु 8 में आए, जन्मदिन के बाद 8वें महीने से बादाम रोज़ मंदिर ले जाकर आधे वापस लाना, अगले जन्मदिन तक।"),
    ("Float worthless or lead coins in a river (one a day for 43 days); put a copper coin in a nearby furnace; avoid a south door.", "खोटे या सीसे के सिक्के दरिया में (43 दिन रोज़ एक); भट्टी में तांबे का पैसा; दक्खन का दरवाज़ा नहीं।")])
_r("Rahu", 9, "पागलों का सरताज हाकिम", "Chief physician of the mad",
   "With Jupiter in 5 or 1, a healer of the disturbed; dislikes any confinement.",
   "बृहस्पति 5-1 में तो पागलों के इलाज का सरताज हकीम।",
   "Turns religion into smoke; children's yoga weak (neither die nor are born); quarrels with elders, disease to children, a dirty drain under the threshold, a lost black dog are signs.",
   "धर्म को भट्टी का धुआँ; औलाद का योग मंदा; दहलीज़ के नीचे गंदा पानी, काला कुत्ता गुम होना निशानियाँ।",
   [("Keep and care for a dog (or the 'three dogs') with sincerity - even if the dog dies several times, it protects the children.", "कुत्ते या तीन कुत्तों की पूरी नेक नीयत से पालना; कुत्ता मरता जाए मगर औलाद की उम्र बख्शे।"),
    ("Stay in the joint family, do not cut ties with in-laws, avoid Mars-bad advice, keep Jupiter (a choti, gold).", "खानदान में मुश्तरका रहना, ससुराल से संबंध न तोड़ना, मंगल बद की सलाह से बचना, बृहस्पति कायम (चोटी, सोना)।")])
_r("Rahu", 10, "सांप की मणि (मददगार) - सांप की सिरी (खतरनाक)", "The snake's jewel or the snake's head",
   "Twice as good with a good Saturn: a jewel that sucks out Saturn's poison; a sign of wealth.",
   "शनि नेक तो दुगना नेक; सांप की मणि जो शनि की ज़हर भी चूसे; धनी होने की निशानी।",
   "With Mars-bad, elephant dung fills the house; meanness breeds enmity; bareheadedness brings money loss.",
   "मंगल बद तो हाथी की लीद घर भरे; तंगदिली अदावत; नंगा सिर धन हानि।",
   [("Mars's remedy helps; keep the door big.", "मंगल का उपाय; दरवाज़ा बड़ा रखना।"),
    ("Do not go bareheaded; avoid black on the head.", "नंगा सिर न रहें; सिर पर काला नहीं।")])
_r("Rahu", 11, "पिता को गोली मारे या मुँह न देखे", "Hard on the father",
   "Good with Saturn in 3/5 (a yogi's ornament); self-made, neither asks nor takes from parents.",
   "शनि 3-5 में तो योगी अलंकार; खुद साख्ता अमीर, माँ-बाप से धन न मांगे।",
   "Hard on the father's life and comfort; locked-up wealth rots; Ketu (children) bad till Jupiter's time.",
   "पिता की उम्र और सुख पर भारी; बंद पड़ा धन सड़े; औलाद गुरु के वक्त तक मंदी।",
   [("After the father, keep Jupiter (gold on the body) - the book calls it necessary; if Jupiter is in 3 or 11, keep iron instead.", "पिता के बाद बृहस्पति कायम (जिस्म पर सोना) ज़रूरी; गुरु 3-11 में तो सोने की बजाय लोहा।"),
    ("Give coins to a sweeper as charity; drink from a silver glass.", "भंगी को खैरात में पैसा देना; चांदी के गिलास में पीना।"),
    ("Religion and charity always help.", "धर्म मंदिर और दान हमेशा मददगार।")])
_r("Rahu", 12, "शेख चिल्ली - ख़याली पुलाव", "Castles in the air",
   "Good night's rest and good in-laws; spends on sisters and daughters; spiritual when Saturn is good.",
   "रात का आराम उम्दा, ससुराल की गुज़रान भली; बहन-बेटियों की पालना।",
   "Hidden expenses that cannot be stopped; baseless hopes; the clan's waste falls on him; the roof seems to shake.",
   "रोकने से न रुकने वाला खुफ़िया खर्च; बेबुनियाद उम्मीदें; कबीले के फ़िज़ूल खर्च का बोझ।",
   [("Keep Mars items (a bag of sugar or fennel) at the sleeping place.", "सोने की जगह मंगल की चीज़ें (खांड या सौंफ़ की बोरी)।"),
    ("Jupiter's remedy always helps; avoid lies and fraud.", "बृहस्पति का उपाय हमेशा मददगार; झूठ-फ़रेब से बचें।")])

# ---------------- Ketu
_r("Ketu", 1, "हर वक्त बच्चे बनाने की फ़िक्र वाला", "Always worried about children",
   "Helps father and guru however bad the time; Jupiter's effect stays good; serving dervishes and the father brings divine help; Ketu not bad with Mars in 12.",
   "वक्त कितना ही मंदा, पिता-गुरु को तारे; बृहस्पति का असर उत्तम; दरवेश सेवा खुदाई मदद; मंगल 12 तो केतु बुरा नहीं।",
   "Planned journeys and transfers do not happen; houses 6-7 empty bring storms to the birth home; Mercury, Venus and Rahu poor; after marriage a bad Ketu can bite even the father.",
   "सफ़र-तबदीली तैयार मगर न हो; 6-7 खाली तो जन्म घर तूफ़ान; बुध, शुक्र, राहु मंदे।",
   [("Give Sun items - jaggery, or copper coins for spending - to boys at dusk (Mercury's time) and dawn (Ketu's time).", "लड़कों को कच्ची शाम और सुबह सादिक के वक्त सूरज की चीज़ (गुड़) या खर्च के लिए तांबे के पैसे देना।"),
    ("Serve dervishes and wash the father's feet; after marriage, if Ketu turns bad, Saturn's remedy.", "दरवेश सेवा, पिता के चरण धोना; शादी के बाद केतु मंदा तो शनि का उपाय।")])
_r("Ketu", 2, "आसूदा हुक्मरान - बहुत सफ़र", "A comfortable ruler who travels a lot",
   "Much travel and authority; with house 8 empty, nature's tilak helps; Venus's share always good; self-earning and lively after 24 with Sun in 12.",
   "सफ़र बहुत, हुक्मरान आसूदा; 8 खाली तो कुदरती तिलक मदद पर; शुक्र का भाग उम्दा।",
   "A planet in 8 brings short life or trouble; earns lakhs but saves nothing, like a broker; having children in every house leaves no helper in old age.",
   "8 में कोई ग्रह तो अल्पायु-ज़हमती; लाखों की आई-चलाई, नतीजा दलाली; बुढ़ापे में मददगार बच्चा नहीं।",
   [("A tilak on the forehead is auspicious (the book: Ketu's mark at the tilak place).", "तिलक की जगह केतु का निशान मुबारक; माथे पर तिलक।")])
_r("Ketu", 3, "टूं-टूं करता रहने वाला कुत्ता मगर नेक दरवेश", "A whining dog, but a good dervish",
   "Good at 24 or with the first son; brothers help even with broken arms; with Mars in 12 the fish line supports.",
   "24 में या पहले लड़के से उत्तम; टूटे बाजू भी भाई मददगार।",
   "Troubled by brothers, wanders abroad; destroys its own age and wealth with excuses; long civil cases; needless separation from wife and sisters-in-law.",
   "भाइयों से दुखिया, परदेस में मारा-मारा; उम्र-दौलत हीले बहाने बर्बाद; दीवानी मुकदमों में दौलत बर्बाद।",
   [("For lung trouble or poor health, float Jupiter items in running water or apply a saffron tilak.", "फेफड़े या मंदी सेहत में बृहस्पति की चीज़ें चलते पानी में बहाना या केसर का तिलक।"),
    ("Wear gold for finances.", "माली हालत के लिए जिस्म पर सोना।")])
_r("Ketu", 4, "बच्चों को डराने वाला कुत्ता - ज्वार भाटा", "The dog that frightens children: a tide",
   "Good for the father; the reward of patience is sweet; a son born late lives a full century; many daughters, wise.",
   "पिता के लिए उम्दा; सब्र का फल मीठा; लड़का देर से, सदी पूरी उम्र।",
   "Spoils Moon's things; sons late or not at all; own health weak (sugar), mother and children both suffer with Moon/Mars in 3-4.",
   "चंद्र की चीज़ें रद्दी; लड़का देर से; अपनी सेहत हल्की, माता और औलाद दोनों मंदे।",
   [("Jupiter's remedy: give gold at a temple or yellow items to the family priest and take his blessing.", "गुरु उपाय: मंदिर में सोना या कुल पुरोहित को पीली चीज़ देकर आशीर्वाद।")])
_r("Ketu", 5, "अपनी रोटी के टुकड़े के लिए गुरु निगरान", "Jupiter oversees its bread",
   "After 24 Ketu is good by itself; the number and fortune of children follow Jupiter.",
   "24 के बाद केतु खुद उत्तम; औलाद की हालत बृहस्पति पर।",
   "With Moon or Mars in 3-4 and Saturn in 5/9, sons are lost; with pitri rin family life suffers; a dog's cry instead of a son's voice.",
   "चंद्र-मंगल 3-4 और शनि 5-9 तो लड़के खत्म; पितृ ऋण तो गृहस्थ मंदा।",
   [("Donate Moon and Mars items (when Saturn is in 5 or 9).", "चंद्र और मंगल की चीज़ों का दान (शनि 5 या 9 में हो तो)।")])
_r("Ketu", 6, "शेर कद खूंखार कुत्ता - दो रंगी दुनिया", "A lion-sized fierce dog: a two-coloured world",
   "Alone it gives every good result; own children and advisers give good results; long life (70+); Saturn good.",
   "अकेला हर तरह से उत्तम; अपनी औलाद और सलाहकार नेक; उम्र 70 से कम नहीं।",
   "Bad for Ketu's own things; with a planet beside it, bad for others; maternal side may suffer; Venus in 6 makes both bad.",
   "केतु की चीज़ों पर मंदा; साथी ग्रह हो तो दूसरों पर बुरा; मामू खानदान पर मंदा।",
   [("Wear a gold ring on the left hand.", "बाएँ हाथ में सोने की अंगूठी।")])
_r("Ketu", 7, "गडरिये का पालतू कुत्ता, बच्चों का साथी", "The shepherd's dog, friend of children",
   "Kills enemies like a dog; wealth fourfold by 24 and growing with the second son; Jupiter helps, Saturn not bad; enemies cling till 34 then leave.",
   "कुत्ते की तरह दुश्मन मारे; 24 में चार गुना धन, दूसरा लड़का बढ़े तो धन बढ़े; 34 तक दुश्मन फिर छूटें।",
   "Bad when Mercury, Venus or Jupiter is bad; Venus in 6 spoils both.",
   "बुध, शुक्र या बृहस्पति मंदे तो मंदा।",
   [("Keep Jupiter strong (the book names Jupiter as its helper here).", "बृहस्पति कायम रखें (मददगार)।")])
_r("Ketu", 8, "बच्चों की मोहब्बत के ग़म में छत पर रोने वाला कुत्ता", "The dog that cries on the roof for its children",
   "Long life (70+); not bad with Mars in 12 or while Mercury is good; children like rain when the Moon is in 2.",
   "उम्र 70 से कम नहीं; मंगल 12 या बुध उम्दा तो मंदा नहीं; चंद्र 2 तो औलाद का मींह।",
   "Sons lost; 34 decides whether a son survives; a dog crying on the roof is the first sign of bad times.",
   "नर औलाद कब्र में; 34 साला उम्र फ़ैसलाकुन; छत पर कुत्ते का रोना पहली निशानी।",
   [("Give a two-coloured (black and white) blanket at a place of worship; if another planet is with Ketu, tie that planet's items in a piece of such blanket and bury it in a lonely place.", "दोरंगा (स्याह-सफ़ेद) कंबल धर्म स्थान में देना; साथी ग्रह हो तो कंबल के टुकड़े में उसकी चीज़ें बांधकर वीराने में दबाना।"),
    ("Jupiter's remedy for children; ear piercing (keep the hole 96 hours); Moon worship if the Moon is bad.", "औलाद के लिए बृहस्पति का उपाय; कान छेदन (96 घंटे सुराख़); चंद्र मंदा तो चंद्र पूजन।")])
_r("Ketu", 9, "इंसान की ज़ुबान समझने वाला कुत्ता", "The dog that understands human speech",
   "Saves the father; three sons, happy and good; abroad living good; self-made rich through hand skills; his blessing gives children to the childless.",
   "पिता को तारे; तीन लड़के सुखिया; परदेस में गुज़रान उम्दा; दस्ती मेहनत से अमीर; लावल्दों को औलाद की आशीर्वाद।",
   "In the bad state it cuts the maternal uncle's roots; enemies (Moon, Mars) in 3 kill sons; with bad Saturn, a thief.",
   "मंदी हालत में मामू की जड़ काटे; 3 में शत्रु (चंद्र, मंगल) तो लड़के मरें।",
   [("Keep a gold brick at home, or gold in the ears and on the body.", "घर में सोने की ईंट, कानों या जिस्म पर सोना।"),
    ("Serve dogs and the 'three dogs'.", "कुत्ते और तीन कुत्तों की पालना।")])
_r("Ketu", 10, "चुपचाप अपने रास्ते चलने वाला - मौकाबाज़ / मौकाशनास", "Goes quietly its own way: opportunist or opportune",
   "Saturn in good houses turns earth to gold; with Saturn alone in 6, a famous player; money not bad - only children may suffer.",
   "शनि अच्छे घरों में तो मिट्टी सोना; शनि अकेला 6 तो नामी खिलाड़ी; माया-दौलत में मंदा नहीं।",
   "Saturn in bad houses: gold eaten by earth; a son born 3rd dies with Saturn in 4; an immoral rich man ruined by another's wife.",
   "शनि बुरे घरों में तो सोना मिट्टी खाए; शनि 4 तो लड़का तीसरा होकर मरे।",
   [("Before 48, bury a silver vessel filled with honey in a lonely place; after 48 keeping a dog is necessary.", "48 से पहले चांदी का बर्तन शहद से भरकर बाहर वीराने में दबाना; 48 के बाद कुत्ता रखना ज़रूरी।"),
    ("Guard your conduct between 45 and 48; Ketu-8 remedies apply; Mars helps when Ketu alone is bad; bury milk and honey in foundations if needed.", "45-48 में चाल चलन की संभाल; केतु 8 वाला उपाय; मकान की बुनियाद में दूध-शहद।")])
_r("Ketu", 11, "गीदड़ स्वभाव कुत्ता - गुरु का आसन", "Jackal-natured dog, Jupiter's seat",
   "Fourfold strength: good wealth; with Saturn in 3, elevenfold wealth; in a woman's chart good regardless.",
   "ताकत चार गुना, उम्दा दौलत; शनि 3 तो ग्यारह गुणा धन; औरत के टेवे में हर हाल नेक।",
   "With Saturn-Mercury in 3, Ketu bad; with Ketu-Jupiter in 5-11, stillbirths; mother at risk in Ketu's period.",
   "शनि-बुध 3 तो केतु मंदा; केतु-गुरु 5-11 तो लड़का मुर्दा पैदा।",
   [("Keep a white radish (Saturn item) at the wife's head-side at night and give it at a place of worship in the morning.", "सफ़ेद मूली रात को औरत के सिरहाने रखकर सुबह धर्म स्थान में देना।")])
_r("Ketu", 12, "ऐश व आराम, जद्दी विरासत (उच्च)", "Comfort and inherited ease (exalted)",
   "Grows with its companions; family flourishes; Saturn, Venus and Jupiter all give blessings; houses and travel good.",
   "आप बढ़े, साथी बढ़ें, कुल परिवार बढ़े; शनि, शुक्र, गुरु का असर मुबारक।",
   "Rahu's enemies with it make sons doubtful; with Rahu in 6, children ruined; killing dogs spoils even this exalted Ketu.",
   "राहु के दुश्मन साथ तो औलाद शक्की; राहु 6 तो औलाद बर्बाद; कुत्ते मरवाए तो मंदा।",
   [("For children, Rahu's remedy; for money troubles once children are settled, suck the thumb dipped in milk (book).", "औलाद के लिए राहु का उपाय; माली तकलीफ़ में दूध में अंगूठा डालकर चूसना।"),
    ("Never harm dogs; keep a dog - the book says dogs bear the children's misfortune.", "कुत्ते न मरवाएँ; कुत्ता कायम रखें।")])
