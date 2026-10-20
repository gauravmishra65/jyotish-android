"""yoga_rules.py - the yoga library as data. One entry per yoga; yoga_library.py evaluates them.

Fields: id, name, category, source, text (the rule in plain words), if (condition), cancel (list of
{if, reason}), key (planets that carry it, for the strength grade), tone (supportive | demanding | mixed),
report (False = computed but never surfaced), note.

Sources, cited by short name:
  BJ     Varahamihira, Brihat Jataka (ch. 12 Nabhasa yogas, ch. 13 lunar yogas)
  PD     Mantreswara, Phaladeepika ch. 6
  PVR    P.V.R. Narasimha Rao, Vedic Astrology: An Integrated Approach, ch. 11 (Yogas)
  BVR300 B.V. Raman, Three Hundred Important Combinations (number given where known)
  BPHS   Brihat Parashara Hora Shastra (Santhanam translation)
Where texts differ, the entry says which reading is used.
"""

K = [1, 4, 7, 10]
T = [1, 5, 9]
KT = [1, 4, 5, 7, 9, 10]
DUS = [6, 8, 12]
UPA = [3, 6, 10, 11]
MOV, FIX, DUAL = [0, 3, 6, 9], [1, 4, 7, 10], [2, 5, 8, 11]

R = []


def _ord(n):
    n = int(n)
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def add(id, name, category, source, text, cond, key=(), cancel=(), tone="supportive", report=True, note=None):
    R.append({"id": id, "name": name, "category": category, "source": source, "text": text, "if": cond,
              "key": list(key), "cancel": list(cancel), "tone": tone, "report": report, "note": note})


# =============================================================== Nabhasa yogas (32), BJ ch. 12
NAB = "BJ ch. 12; BPHS Nabhasa yogas"
add("rajju", "Rajju", "Nabhasa (Ashraya)", NAB, "All seven grahas in movable signs", ["seven_signtype", "movable"], tone="mixed")
add("musala", "Musala", "Nabhasa (Ashraya)", NAB, "All seven grahas in fixed signs", ["seven_signtype", "fixed"])
add("nala", "Nala", "Nabhasa (Ashraya)", NAB, "All seven grahas in dual signs", ["seven_signtype", "dual"], tone="mixed")
add("mala", "Mala (Srik)", "Nabhasa (Dala)", NAB, "Three kendras occupied by natural benefics (Jupiter, Venus, Mercury)",
    ["houses_count", K, "natural_benefic3", "Lagna", ">=", 3], key=["Jupiter", "Venus", "Mercury"])
add("sarpa", "Sarpa", "Nabhasa (Dala)", NAB, "Three kendras occupied by natural malefics (Sun, Mars, Saturn)",
    ["houses_count", K, ["Sun", "Mars", "Saturn"], "Lagna", ">=", 3], tone="demanding",
    note="BVR300 no. 102 also counts Rahu and Ketu; the classical Nabhasa rule (BJ) predates them.")
for hs, nm in (([1, 4], "1st and 4th"), ([4, 7], "4th and 7th"), ([7, 10], "7th and 10th"), ([10, 1], "10th and 1st")):
    add(f"gada_{hs[0]}", "Gada", "Nabhasa (Akriti)", NAB, f"All seven grahas in the {nm} houses (two successive kendras)",
        ["seven_exact", hs])
add("shakata_nab", "Shakata (Nabhasa)", "Nabhasa (Akriti)", NAB, "All seven grahas in the 1st and 7th houses", ["seven_exact", [1, 7]], tone="mixed")
add("vihaga", "Vihaga", "Nabhasa (Akriti)", NAB, "All seven grahas in the 4th and 10th houses", ["seven_exact", [4, 10]], tone="mixed")
add("shringataka", "Shringataka", "Nabhasa (Akriti)", NAB, "All seven grahas in the trines 1, 5 and 9", ["seven_exact", T])
add("hala", "Hala", "Nabhasa (Akriti)", NAB, "All seven grahas in one set of trines other than the Lagna's (2-6-10, 3-7-11 or 4-8-12)",
    ["or", ["seven_exact", [2, 6, 10]], ["seven_exact", [3, 7, 11]], ["seven_exact", [4, 8, 12]]])
add("vajra", "Vajra", "Nabhasa (Akriti)", NAB, "Benefics in the 1st and 7th, malefics in the 4th and 10th",
    ["and", ["occupied", [1, 7], "benefic"], ["only", [1, 7], "benefic"], ["occupied", [4, 10], "malefic"], ["only", [4, 10], "malefic"]])
add("yava", "Yava", "Nabhasa (Akriti)", NAB, "Malefics in the 1st and 7th, benefics in the 4th and 10th",
    ["and", ["occupied", [1, 7], "malefic"], ["only", [1, 7], "malefic"], ["occupied", [4, 10], "benefic"], ["only", [4, 10], "benefic"]])
add("kamala", "Kamala", "Nabhasa (Akriti)", NAB, "All seven grahas in the kendras", ["all_in", K, "seven"], note="Reading used: all seven within these houses (not every house need be occupied), as in most modern texts.")
add("vapi", "Vapi", "Nabhasa (Akriti)", NAB, "All seven grahas in the panaparas (2, 5, 8, 11) or all in the apoklimas (3, 6, 9, 12)",
    ["or", ["all_in", [2, 5, 8, 11], "seven"], ["all_in", [3, 6, 9, 12], "seven"]])
add("yupa", "Yupa", "Nabhasa (Akriti)", NAB, "All seven grahas within the 1st to 4th houses", ["all_in", [1, 2, 3, 4], "seven"], note="Reading used: all seven within these houses (not every house need be occupied), as in most modern texts.")
add("ishu", "Ishu (Shara)", "Nabhasa (Akriti)", NAB, "All seven grahas within the 4th to 7th houses", ["all_in", [4, 5, 6, 7], "seven"], note="Reading used: all seven within these houses (not every house need be occupied), as in most modern texts.")
add("shakti", "Shakti", "Nabhasa (Akriti)", NAB, "All seven grahas within the 7th to 10th houses", ["all_in", [7, 8, 9, 10], "seven"], tone="mixed", note="Reading used: all seven within these houses (not every house need be occupied), as in most modern texts.")
add("danda", "Danda", "Nabhasa (Akriti)", NAB, "All seven grahas within the 10th, 11th, 12th and 1st houses", ["all_in", [10, 11, 12, 1], "seven"], tone="demanding", note="Reading used: all seven within these houses (not every house need be occupied), as in most modern texts.")
add("nauka", "Nauka", "Nabhasa (Akriti)", NAB, "All seven grahas fill seven consecutive houses from the 1st", ["seven_run", [1], 7])
add("kuta", "Kuta", "Nabhasa (Akriti)", NAB, "All seven grahas fill seven consecutive houses from the 4th", ["seven_run", [4], 7], tone="mixed")
add("chhatra", "Chhatra", "Nabhasa (Akriti)", NAB, "All seven grahas fill seven consecutive houses from the 7th", ["seven_run", [7], 7])
add("chapa_nab", "Chapa (Nabhasa)", "Nabhasa (Akriti)", NAB, "All seven grahas fill seven consecutive houses from the 10th", ["seven_run", [10], 7])
add("ardhachandra", "Ardhachandra", "Nabhasa (Akriti)", NAB, "All seven grahas fill seven consecutive houses starting from a non-kendra",
    ["seven_run", [2, 3, 5, 6, 8, 9, 11, 12], 7])
add("chakra", "Chakra", "Nabhasa (Akriti)", NAB, "The seven grahas fill the six odd houses 1, 3, 5, 7, 9, 11", ["seven_exact", [1, 3, 5, 7, 9, 11]])
add("samudra", "Samudra", "Nabhasa (Akriti)", NAB, "The seven grahas fill the six even houses 2, 4, 6, 8, 10, 12", ["seven_exact", [2, 4, 6, 8, 10, 12]])
_SANKHYA_NOTE = "Sankhya yogas apply only when no Ashraya, Dala or Akriti Nabhasa yoga is present (BJ 12)."
for n, nm, tone in ((7, "Vallaki (Veena)", "supportive"), (6, "Dama", "supportive"), (5, "Pasha", "mixed"), (4, "Kedara", "supportive"),
                    (3, "Shoola", "demanding"), (2, "Yuga", "demanding"), (1, "Gola", "demanding")):
    add(f"sankhya_{n}", nm, "Nabhasa (Sankhya)", NAB, f"The seven grahas occupy exactly {n} sign{'s' if n > 1 else ''}",
        ["seven_distinct", n], tone=tone, note=_SANKHYA_NOTE)

# =============================================================== Solar yogas, BJ ch. 13 / PD 6
SUN_OTHERS = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
add("vesi", "Vesi", "Solar", "BJ ch. 13; PD ch. 6", "A graha other than the Moon (nodes excluded) in the 2nd from the Sun",
    ["any_in", [2], SUN_OTHERS, "Sun"], key=["Sun"])
add("vasi", "Vasi", "Solar", "BJ ch. 13; PD ch. 6", "A graha other than the Moon (nodes excluded) in the 12th from the Sun",
    ["any_in", [12], SUN_OTHERS, "Sun"], key=["Sun"])
add("ubhayachari", "Ubhayachari", "Solar", "BJ ch. 13; PD ch. 6", "Grahas other than the Moon on both sides of the Sun (2nd and 12th)",
    ["and", ["any_in", [2], SUN_OTHERS, "Sun"], ["any_in", [12], SUN_OTHERS, "Sun"]], key=["Sun"])
add("budha_aditya", "Budha-Aditya (Nipuna)", "Solar", "PD ch. 6; PVR ch. 11", "Sun and Mercury in the same sign",
    ["conj", "Sun", "Mercury"], key=["Sun", "Mercury"],
    cancel=[{"if": ["combust", "Mercury"], "reason": "Mercury is combust, which weakens it (PVR)"}])

# =============================================================== Lunar yogas, BJ ch. 13
MOON_OTHERS = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
add("sunapha", "Sunapha", "Lunar", "BJ ch. 13", "A graha other than the Sun (nodes excluded) in the 2nd from the Moon",
    ["and", ["any_in", [2], MOON_OTHERS, "Moon"], ["not", ["any_in", [12], MOON_OTHERS, "Moon"]]], key=["Moon"])
add("anapha", "Anapha", "Lunar", "BJ ch. 13", "A graha other than the Sun (nodes excluded) in the 12th from the Moon",
    ["and", ["any_in", [12], MOON_OTHERS, "Moon"], ["not", ["any_in", [2], MOON_OTHERS, "Moon"]]], key=["Moon"])
add("durudhara", "Durudhara", "Lunar", "BJ ch. 13", "Grahas other than the Sun on both sides of the Moon",
    ["and", ["any_in", [2], MOON_OTHERS, "Moon"], ["any_in", [12], MOON_OTHERS, "Moon"]], key=["Moon"])
add("kemadruma", "Kemadruma", "Lunar", "BJ ch. 13; PD ch. 6", "No graha other than the Sun (nodes excluded) with the Moon or in the 2nd or 12th from it",
    ["none_in", [1, 2, 12], MOON_OTHERS, "Moon"], key=["Moon"], tone="demanding",
    cancel=[{"if": ["any_in", K, "not:Sun,Moon", "Lagna"], "reason": "a graha (other than Sun and Moon) is in a kendra from the Lagna (PD)"},
            {"if": ["any_in", K, "not:Sun,Moon", "Moon"], "reason": "a graha (other than Sun and Moon) is in a kendra from the Moon"},
            {"if": ["in_house", "Moon", K], "reason": "the Moon itself is in a kendra from the Lagna"},
            {"if": ["aspects", "Jupiter", "Moon"], "reason": "Jupiter aspects the Moon"}])
add("chandra_mangala", "Chandra-Mangala", "Lunar", "PVR ch. 11", "Moon and Mars in the same sign", ["conj", "Moon", "Mars"], key=["Moon", "Mars"])
add("adhi", "Adhi", "Lunar", "BJ ch. 13; PD ch. 6", "Benefics occupy the 6th, 7th and 8th from the Moon (at least two of the three houses, no malefic there)",
    ["and", ["count_in", [6, 7, 8], ["Jupiter", "Venus", "Mercury"], "Moon", ">=", 2], ["none_in", [6, 7, 8], "malefic", "Moon"]],
    key=["Jupiter", "Venus", "Mercury"], note="Readings differ: some require each of the three houses to be occupied.")
add("gaja_kesari", "Gaja Kesari", "Lunar", "PD ch. 6; PVR ch. 11", "Jupiter in a kendra from the Moon",
    ["in_house", "Jupiter", K, "Moon"], key=["Jupiter", "Moon"],
    cancel=[{"if": ["dignity", "Jupiter", ["debilitated"]], "reason": "Jupiter is debilitated (PVR's condition)"},
            {"if": ["combust", "Jupiter"], "reason": "Jupiter is combust (PVR's condition)"},
            {"if": ["dignity", "Jupiter", ["enemy"]], "reason": "Jupiter is in an enemy's sign (PVR's condition)"},
            {"if": ["not", ["or", ["conj_with_kind", "Jupiter", ["Venus", "Mercury", "Moon"]], ["aspected_by_kind", "Jupiter", ["Venus", "Mercury", "Moon"]]]],
             "reason": "no benefic joins or aspects Jupiter (PVR's condition)"}],
    note="BVR300 no. 1 states the yoga from the kendra placement alone; the cancellations are PVR's conditions.")
add("amala_lagna", "Amala", "Lunar", "PD ch. 6; BVR300", "Only natural benefics in the 10th from the Lagna",
    ["only", [10], ["Jupiter", "Venus", "Mercury", "Moon"], "Lagna"], key=["L10"])
add("amala_moon", "Amala (from the Moon)", "Lunar", "PD ch. 6; BVR300", "Only natural benefics in the 10th from the Moon",
    ["only", [10], ["Jupiter", "Venus", "Mercury"], "Moon"], key=["Moon"])
add("vasumati", "Vasumati", "Lunar", "PD ch. 6; BVR300", "Benefics occupy upachayas (3, 6, 10, 11) from the Lagna or the Moon, all three natural benefics there",
    ["or", ["all_in", UPA, ["Jupiter", "Venus", "Mercury"], "Lagna"], ["all_in", UPA, ["Jupiter", "Venus", "Mercury"], "Moon"]],
    key=["Jupiter", "Venus", "Mercury"])
add("shakata", "Shakata", "Lunar", "PD ch. 6; BVR300", "The Moon in the 6th, 8th or 12th from Jupiter",
    ["rel_house", "Jupiter", "Moon", DUS], key=["Moon", "Jupiter"], tone="demanding",
    cancel=[{"if": ["in_house", "Jupiter", K], "reason": "Jupiter is in a kendra from the Lagna"},
            {"if": ["in_house", "Moon", K], "reason": "the Moon is in a kendra from the Lagna (some authorities)"}])
add("subha_kartari", "Shubha Kartari (Lagna)", "Lagna", "PVR ch. 11", "Benefics in both the 2nd and 12th, no malefic there",
    ["and", ["occupied", [2, 12], "benefic"], ["none_in", [2, 12], "malefic"]])
add("papa_kartari", "Papa Kartari (Lagna)", "Lagna", "PVR ch. 11", "Malefics in both the 2nd and 12th, no benefic there",
    ["and", ["occupied", [2, 12], "malefic"], ["none_in", [2, 12], "benefic"]], tone="demanding")
add("subha_lagna", "Shubha (benefic in Lagna)", "Lagna", "PVR ch. 11", "Only benefics occupy the Lagna", ["only", [1], "benefic"], key=["L1"])
add("asubha_lagna", "Ashubha (malefic in Lagna)", "Lagna", "PVR ch. 11", "Only malefics occupy the Lagna", ["only", [1], "malefic"], tone="demanding")

# =============================================================== Pancha Mahapurusha, PD ch. 6
for p, nm in (("Mars", "Ruchaka"), ("Mercury", "Bhadra"), ("Jupiter", "Hamsa"), ("Venus", "Malavya"), ("Saturn", "Sasa")):
    add(f"mahapurusha_{p.lower()}", f"{nm} (Pancha Mahapurusha)", "Pancha Mahapurusha", "PD ch. 6; BPHS",
        f"{p} in its own or exaltation sign in a kendra from the Lagna",
        ["and", ["strong_sign", p], ["in_house", p, K]], key=[p],
        cancel=[{"if": ["combust", p], "reason": f"{p} is combust, which weakens the yoga"}],
        note="Some authorities also count kendras from the Moon; this entry uses the Lagna.")

# =============================================================== Named yogas, PVR ch. 11 and BVR300
SRC = "PVR ch. 11; BVR300"
add("guru_mangala", "Guru-Mangala", "Named", "PVR ch. 11", "Jupiter and Mars together or 7th from each other",
    ["or", ["conj", "Jupiter", "Mars"], ["rel_house", "Jupiter", "Mars", [7]]], key=["Jupiter", "Mars"])
add("parvata", "Parvata", "Named", SRC, "Kendras occupied only by benefics, and the 7th and 8th empty or with benefics only",
    ["and", ["only", K, "benefic"], ["none_in", [7, 8], "malefic"]], key=["L1"])
add("kahala", "Kahala", "Named", SRC, "The 4th lord and Jupiter in mutual kendras, with a strong Lagna lord",
    ["and", ["mutual_kendra", "L4", "Jupiter"], ["strong", "L1"], ["not", ["conj", "L4", "Jupiter"]]], key=["L4", "Jupiter", "L1"],
    note="Second reading (4th lord exalted or own sign with the 10th lord) is also checked as kahala_2.")
add("kahala_2", "Kahala (second reading)", "Named", SRC, "The 4th lord in own or exaltation sign, joined by the 10th lord",
    ["and", ["strong_sign", "L4"], ["conj", "L4", "L10"]], key=["L4", "L10"])
add("chamara", "Chamara", "Named", SRC, "Lagna lord exalted in a kendra and aspected by Jupiter",
    ["and", ["dignity", "L1", ["exalted"]], ["in_house", "L1", K], ["aspects", "Jupiter", "L1"]], key=["L1"])
add("chamara_2", "Chamara (second reading)", "Named", SRC, "Two benefics together in the 7th, 9th or 10th",
    ["or", ["count_in", [7], "benefic", "Lagna", ">=", 2], ["count_in", [9], "benefic", "Lagna", ">=", 2], ["count_in", [10], "benefic", "Lagna", ">=", 2]])
add("shankha", "Shankha", "Named", SRC, "The 5th and 6th lords in mutual kendras, with a strong Lagna lord",
    ["and", ["mutual_kendra", "L5", "L6"], ["strong", "L1"]], key=["L5", "L6", "L1"])
add("shankha_2", "Shankha (second reading)", "Named", SRC, "Lagna lord and 10th lord together in a movable sign, with a strong 9th lord",
    ["and", ["conj", "L1", "L10"], ["sign_type", "L1", "movable"], ["strong", "L9"]], key=["L1", "L10", "L9"])
add("bheri", "Bheri", "Named", SRC, "The 1st, 2nd, 7th and 12th occupied, with a strong 9th lord",
    ["and", ["occupied", [1, 2, 7, 12], "any"], ["strong", "L9"]], key=["L9"])
add("bheri_2", "Bheri (second reading)", "Named", SRC, "Jupiter, Venus and the Lagna lord in mutual kendras, with a strong 9th lord",
    ["and", ["mutual_kendra", "Jupiter", "Venus"], ["mutual_kendra", "Jupiter", "L1"], ["mutual_kendra", "Venus", "L1"], ["strong", "L9"]],
    key=["Jupiter", "Venus", "L9"])
add("mridanga", "Mridanga", "Named", "BVR300 no. 46", "Grahas in own or exaltation signs both in a kendra and in a trine, with a strong Lagna lord",
    ["and", ["strong", "L1"], ["or", *[["and", ["strong_sign", p], ["in_house", p, K]] for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]]],
     ["or", *[["and", ["strong_sign", p], ["in_house", p, T]] for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]]]], key=["L1"],
    note="Rule used: at least one own- or exaltation-sign graha in a kendra and at least one in a trine (the Lagna counts as both).")
add("sreenatha", "Sreenatha", "Named", SRC, "The 7th lord exalted in the 10th, and the 10th lord with the 9th lord",
    ["and", ["dignity", "L7", ["exalted"]], ["in_house", "L7", [10]], ["conj", "L10", "L9"]], key=["L7", "L10", "L9"])
add("matsya", "Matsya", "Named", SRC, "Benefics in the 1st and 9th, a graha in the 5th, malefics in the 4th and 8th",
    ["and", ["occupied", [1, 9], "benefic"], ["occupied", [5], "any"], ["occupied", [4, 8], "malefic"]])
add("kurma", "Kurma", "Named", SRC, "Benefics in the 5th, 6th and 7th in good dignity; malefics in the 1st, 3rd and 11th in own or exaltation signs",
    ["and", ["occupied", [5, 6, 7], "benefic"], ["occupied", [1, 3, 11], "malefic"]], note="Dignity of each occupant is left to the reader.")
add("khadga", "Khadga", "Named", SRC, "2nd lord in the 9th and 9th lord in the 2nd, with the Lagna lord in a kendra or trine",
    ["and", ["in_house", "L2", [9]], ["in_house", "L9", [2]], ["in_house", "L1", KT]], key=["L2", "L9", "L1"])
add("kusuma", "Kusuma", "Named", SRC, "Fixed-sign Lagna, Venus in a kendra, the Moon in a trine with a benefic, Saturn in the 10th",
    ["and", ["sign_type", "Lagna", "fixed"], ["in_house", "Venus", K], ["in_house", "Moon", T], ["in_house", "Saturn", [10]]], key=["Venus", "Saturn"])
add("kalanidhi", "Kalanidhi", "Named", SRC, "Jupiter in the 2nd or 5th, joined or aspected by Mercury and Venus",
    ["and", ["in_house", "Jupiter", [2, 5]], ["assoc", "Jupiter", "Mercury"], ["assoc", "Jupiter", "Venus"]], key=["Jupiter"])
add("kalpadruma", "Kalpadruma", "Named", SRC, "Lagna lord, its dispositor, and that dispositor's dispositor in rasi and navamsa are all in kendras, trines or exaltation",
    ["and", *[["or", ["in_house", t, KT], ["dignity", t, ["exalted"]]] for t in ["L1", "disp:L1", "disp:disp:L1", "nav:disp:disp:L1"]]],
    key=["L1"], note="Simplified to the rasi positions of the four planets.")
add("lagnadhi", "Lagnadhi", "Named", SRC, "Benefics in the 6th, 7th and 8th from the Lagna, with no malefic joining or aspecting them",
    ["and", ["only", [6, 7, 8], "benefic"], *[["not", ["aspects_house", m, h]] for m in ("Sun", "Mars", "Saturn", "Rahu", "Ketu") for h in (6, 7, 8)]],
    key=["L1"], note="Rule used: the 6th to 8th hold only benefics (at least one) and no natural malefic aspects any of the three houses.")
add("hari", "Hari", "Named", SRC, "Benefics in the 2nd, 12th and 8th from the 2nd lord", ["occupied", [2, 8, 12], "benefic", "L2"], key=["L2"])
add("hara", "Hara", "Named", SRC, "Benefics in the 4th, 9th and 8th from the 7th lord", ["occupied", [4, 8, 9], "benefic", "L7"], key=["L7"])
add("brahma", "Brahma", "Named", SRC, "Benefics in the 4th, 10th and 11th from the Lagna lord", ["occupied", [4, 10, 11], "benefic", "L1"], key=["L1"])
add("brahma_2", "Brahma (second reading)", "Named", SRC, "Jupiter in a kendra from the 9th lord, Venus in a kendra from the 11th lord, Mercury in a kendra from the 1st or 10th lord",
    ["and", ["rel_house", "L9", "Jupiter", K], ["rel_house", "L11", "Venus", K], ["or", ["rel_house", "L1", "Mercury", K], ["rel_house", "L10", "Mercury", K]]],
    key=["Jupiter", "Venus", "Mercury"])
add("vishnu", "Vishnu", "Named", SRC, "9th and 10th lords in the 2nd, with the lord of the 9th lord's navamsa sign also in the 2nd",
    ["and", ["in_house", "L9", [2]], ["in_house", "L10", [2]], ["in_house", "nav:L9", [2]]], key=["L9", "L10"])
add("shiva", "Shiva", "Named", SRC, "5th lord in the 9th, 9th lord in the 10th, 10th lord in the 5th",
    ["and", ["in_house", "L5", [9]], ["in_house", "L9", [10]], ["in_house", "L10", [5]]], key=["L5", "L9", "L10"])
add("trilochana", "Trilochana", "Named", SRC, "Sun, Moon and Mars in mutual trines",
    ["and", ["mutual_trine", "Sun", "Moon"], ["mutual_trine", "Sun", "Mars"], ["mutual_trine", "Moon", "Mars"]], key=["Sun", "Moon", "Mars"])
add("gauri", "Gauri", "Named", SRC, "The lord of the 10th lord's navamsa sign exalted in the 10th, joined by the Lagna lord",
    ["and", ["dignity", "nav:L10", ["exalted"]], ["in_house", "nav:L10", [10]], ["conj", "nav:L10", "L1"]], key=["nav:L10", "L1"])
add("chandika", "Chandika", "Named", SRC, "Fixed-sign Lagna aspected by the 6th lord; the Sun with the lords of the 6th and 9th lords' navamsa signs",
    ["and", ["sign_type", "Lagna", "fixed"], ["aspects", "L6", "Lagna"], ["conj", "Sun", "nav:L6"], ["conj", "Sun", "nav:L9"]], key=["Sun"])
add("lakshmi", "Lakshmi", "Named", SRC, "The 9th lord in own or exaltation sign in a kendra, with a strong Lagna lord",
    ["and", ["strong_sign", "L9"], ["in_house", "L9", K], ["strong", "L1"]], key=["L9", "L1"])
add("sarada", "Sarada", "Named", SRC, "10th lord in the 5th, Mercury in a kendra, Sun strong in Leo, Mercury or Jupiter in a trine from the Moon, Mars in the 11th",
    ["and", ["in_house", "L10", [5]], ["in_house", "Mercury", K], ["in_sign", "Sun", [4]], ["or", ["in_house", "Mercury", T, "Moon"], ["in_house", "Jupiter", T, "Moon"]],
     ["in_house", "Mars", [11]]], key=["L10", "Mercury", "Sun"])
add("bharathi", "Bharathi", "Named", SRC, "The lord of the 2nd, 5th or 11th lord's navamsa sign exalted and joined with the 9th lord",
    ["or", *[["and", ["dignity", f"nav:{l}", ["exalted"]], ["conj", f"nav:{l}", "L9"]] for l in ("L2", "L5", "L11")]], key=["L9"])
add("saraswati", "Saraswati", "Named", SRC, "Mercury, Jupiter and Venus each in a kendra, trine or the 2nd, with Jupiter in own, friendly or exaltation sign",
    ["and", ["all_in", KT + [2], ["Mercury", "Jupiter", "Venus"]], ["dignity", "Jupiter", ["own", "moolatrikona", "exalted", "friend"]]],
    key=["Mercury", "Jupiter", "Venus"])
add("amsavatara", "Amsavatara", "Named", SRC, "Jupiter, Venus and an exalted Saturn in kendras",
    ["and", ["in_house", "Jupiter", K], ["in_house", "Venus", K], ["in_house", "Saturn", K], ["dignity", "Saturn", ["exalted"]]], key=["Jupiter", "Venus", "Saturn"])
add("devendra", "Devendra", "Named", SRC, "Fixed-sign Lagna, exchange of the 2nd and 10th lords, exchange of the 1st and 11th lords",
    ["and", ["sign_type", "Lagna", "fixed"], ["exchange", "L2", "L10"], ["exchange", "L1", "L11"]], key=["L1", "L2", "L10", "L11"])
add("indra", "Indra", "Named", SRC, "Exchange of the 5th and 11th lords, with the Moon in the 5th",
    ["and", ["exchange", "L5", "L11"], ["in_house", "Moon", [5]]], key=["L5", "L11", "Moon"])
add("ravi", "Ravi", "Named", SRC, "Sun in the 10th, and the 10th lord in the 3rd with Saturn",
    ["and", ["in_house", "Sun", [10]], ["in_house", "L10", [3]], ["conj", "L10", "Saturn"]], key=["Sun", "L10"])
add("bhaskara", "Bhaskara", "Named", SRC, "Moon 12th from the Sun, Mercury 2nd from the Sun, Jupiter 5th or 9th from the Moon",
    ["and", ["rel_house", "Sun", "Moon", [12]], ["rel_house", "Sun", "Mercury", [2]], ["rel_house", "Moon", "Jupiter", [5, 9]]], key=["Sun", "Moon", "Jupiter"])
add("kulavardhana", "Kulavardhana", "Named", SRC, "Every graha in the 5th from the Lagna, the Moon or the Sun",
    ["each_seven_from_any", 5, ["Lagna", "Moon", "Sun"]], key=["L5"])
add("gandharva", "Gandharva", "Named", SRC, "10th lord in a trine from the 7th, Lagna lord with or aspected by Jupiter, Sun exalted and strong, Moon in the 9th",
    ["and", ["rel_house", "Lagna", "L10", [7, 11, 3]], ["or", ["conj", "L1", "Jupiter"], ["aspects", "Jupiter", "L1"]], ["dignity", "Sun", ["exalted"]],
     ["in_house", "Moon", [9]]], key=["Sun", "L10", "L1"])
add("go", "Go", "Named", SRC, "Jupiter strong in moolatrikona with the 2nd lord, and the Lagna lord exalted",
    ["and", ["dignity", "Jupiter", ["moolatrikona"]], ["conj", "Jupiter", "L2"], ["dignity", "L1", ["exalted"]]], key=["Jupiter", "L2", "L1"])
add("vidyut", "Vidyut", "Named", SRC, "11th lord in deep exaltation, joined with Venus, both in a kendra from the Lagna lord",
    ["and", ["deep_exalt", "L11", 5], ["conj", "L11", "Venus"], ["rel_house", "L1", "Venus", K]], key=["L11", "Venus"],
    note="Deep exaltation taken as within 5 degrees of the exact degree.")
add("chapa", "Chapa", "Named", SRC, "Exchange of the 4th and 10th lords, with the Lagna lord exalted",
    ["and", ["exchange", "L4", "L10"], ["dignity", "L1", ["exalted"]]], key=["L4", "L10", "L1"])
add("pushkala", "Pushkala", "Named", SRC, "Lagna lord with the Moon, the Moon's dispositor in a kendra and aspecting the Lagna, a graha in the Lagna",
    ["and", ["conj", "L1", "Moon"], ["in_house", "disp:Moon", K], ["aspects", "disp:Moon", "Lagna"], ["occupied", [1], "any"]], key=["L1", "Moon"])
add("makuta", "Makuta", "Named", SRC, "Jupiter 9th from the 9th lord, a benefic 9th from Jupiter, Saturn in the 10th",
    ["and", ["rel_house", "L9", "Jupiter", [9]], ["occupied", [9], "benefic", "Jupiter"], ["in_house", "Saturn", [10]]], key=["Jupiter", "Saturn"])
add("jaya", "Jaya", "Named", SRC, "10th lord in deep exaltation and the 6th lord debilitated",
    ["and", ["deep_exalt", "L10", 5], ["dignity", "L6", ["debilitated"]]], key=["L10"])
add("chatussagara", "Chatussagara", "Named", "BVR300", "All four kendras occupied", ["occupied", K, "any"])
add("rajalakshana", "Rajalakshana", "Named", "BVR300", "Jupiter, Venus, Mercury and the Moon all in kendras",
    ["all_in", K, ["Jupiter", "Venus", "Mercury", "Moon"]], key=["Jupiter", "Venus", "Mercury", "Moon"])
add("vanchana", "Vanchana Chora Bheeti", "Named", "BVR300 no. 11", "A malefic in the Lagna with Gulika in a trine; or Gulika with a kendra or trine lord; or the Lagna lord with Rahu, Saturn or Ketu",
    ["or", ["and", ["any_in", [1], ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]], ["in_house", "Gulika", [5, 9]]],
     ["or", *[["conj", "Gulika", f"L{h}"] for h in (1, 4, 5, 7, 9, 10)]],
     ["or", ["conj", "L1", "Rahu"], ["conj", "L1", "Saturn"], ["conj", "L1", "Ketu"]]], key=["L1"], tone="demanding",
    note="Read as a need for care with trust and paperwork, never as a prediction of theft.")
add("mahabhagya", "Mahabhagya", "Named", "BVR300", "Male: day birth with Lagna, Sun and Moon in odd signs. Female: night birth with all three in even signs",
    ["or", ["and", ["male"], ["day_birth"], ["sign_type", "Lagna", "odd"], ["sign_type", "Sun", "odd"], ["sign_type", "Moon", "odd"]],
     ["and", ["female"], ["not", ["day_birth"]], ["sign_type", "Lagna", "even"], ["sign_type", "Sun", "even"], ["sign_type", "Moon", "even"]]],
    key=["Sun", "Moon"])
add("parijata", "Parijata", "Named", "BVR300 no. 47; PD ch. 6", "The dispositor of the Lagna lord's dispositor, or the navamsa lord of the Lagna lord's dispositor, in a kendra, trine, own or exaltation sign",
    ["or", *[["or", ["in_house", t, KT], ["strong_sign", t]] for t in ("disp:disp:L1", "nav:disp:L1")]], key=["disp:disp:L1"])
add("garuda", "Garuda", "Named", "BVR300", "The lord of the Moon's navamsa sign exalted, with a day birth in the waxing Moon",
    ["and", ["dignity", "nav:Moon", ["exalted"]], ["day_birth"], ["waxing"]], key=["nav:Moon"])
add("sareera_soukhya", "Sareera Soukhya", "Named", "BVR300 no. 108", "The Lagna lord, Jupiter or Venus in a kendra",
    ["any_in", K, ["L1", "Jupiter", "Venus"]], key=["L1", "Jupiter", "Venus"])
add("dehapushti", "Dehapushti", "Named", "BVR300", "Lagna lord in a movable sign aspected by a benefic",
    ["and", ["sign_type", "L1", "movable"], ["or", *[["aspects", b, "L1"] for b in ("Jupiter", "Venus", "Mercury", "Moon")]]], key=["L1"])
add("sada_sanchara", "Sada Sanchara", "Named", "BVR300 no. 117", "The Lagna lord, or the lord of the sign it occupies, in a movable sign",
    ["or", ["sign_type", "L1", "movable"], ["sign_type", "disp:L1", "movable"]], key=["L1"], tone="mixed", note="Read as a life with much travel or movement.")

# =============================================================== Malika yogas (twelve), BVR300
HN = ["Lagna", "Dhana", "Vikrama", "Sukha", "Putra", "Shatru", "Kalatra", "Randhra", "Bhagya", "Karma", "Labha", "Vyaya"]
for h in range(1, 13):
    add(f"malika_{h}", f"{HN[h - 1]} Malika", "Malika", "BVR300", f"The seven grahas fill seven consecutive houses starting from house {h}",
        ["seven_run", [h], 7], tone="supportive" if h in (1, 2, 4, 5, 9, 10, 11) else "mixed",
        note="Overlaps the Nauka, Kuta, Chhatra, Chapa and Ardhachandra Nabhasa yogas, which use the same pattern.")

# =============================================================== Raja and Dhana yogas by lordship
for a, b in (("L9", "L10"),):
    add("dharma_karmadhipati", "Dharma-Karmadhipati", "Raja", "BPHS; PVR ch. 11", "9th and 10th lords conjoined, in mutual aspect or exchanging signs",
        ["or", ["conj", a, b], ["and", ["aspects", a, b], ["aspects", b, a]], ["exchange", a, b]],
        key=[a, b], cancel=[{"if": ["and", ["in_house", a, DUS], ["in_house", b, DUS]], "reason": "both lords sit in the 6th, 8th or 12th"}])
for kl in ("L4", "L7", "L10"):
    for tl in ("L5", "L9"):
        add(f"raja_{kl}_{tl}", f"Raja yoga ({_ord(kl[1:])} and {_ord(tl[1:])} lords)", "Raja", "BPHS; PVR ch. 11",
            f"Lords of the {_ord(kl[1:])} (kendra) and {_ord(tl[1:])} (trine) conjoined, in mutual aspect or exchanging signs",
            ["and", ["or", ["conj", kl, tl], ["and", ["aspects", kl, tl], ["aspects", tl, kl]], ["exchange", kl, tl]]], key=[kl, tl],
            note="The engine's Parashari block (raja_yogas) adds orb, blemishes and Dasavarga level; quote that for strength.")
for x, y in (("L1", "L5"), ("L1", "L9")):
    add(f"raja_{x}_{y}", f"Raja yoga (Lagna lord and {_ord(y[1:])} lord)", "Raja", "BPHS; PVR ch. 11",
        f"Lagna lord and {_ord(y[1:])} lord conjoined, in mutual aspect or exchanging signs",
        ["or", ["conj", x, y], ["and", ["aspects", x, y], ["aspects", y, x]], ["exchange", x, y]], key=[x, y])
for a, b in (("L2", "L11"), ("L2", "L5"), ("L2", "L9"), ("L5", "L11"), ("L9", "L11"), ("L1", "L2"), ("L1", "L11"), ("L5", "L9")):
    add(f"dhana_{a}_{b}", f"Dhana yoga ({_ord(a[1:])} and {_ord(b[1:])} lords)", "Dhana", "BPHS; PVR ch. 11",
        f"Lords of the {_ord(a[1:])} and {_ord(b[1:])} conjoined, in mutual aspect or exchanging signs",
        ["or", ["conj", a, b], ["and", ["aspects", a, b], ["aspects", b, a]], ["exchange", a, b]], key=[a, b],
        cancel=[{"if": ["and", ["in_house", a, DUS], ["in_house", b, DUS]], "reason": "both lords sit in the 6th, 8th or 12th"}])
add("viparita_harsha", "Harsha (Viparita Raja)", "Viparita", "BVR300; PVR ch. 11", "The 6th lord in the 6th", ["in_house", "L6", [6]], key=["L6"])
add("viparita_sarala", "Sarala (Viparita Raja)", "Viparita", "BVR300; PVR ch. 11", "The 8th lord in the 8th", ["in_house", "L8", [8]], key=["L8"])
add("viparita_vimala", "Vimala (Viparita Raja)", "Viparita", "BVR300; PVR ch. 11", "The 12th lord in the 12th", ["in_house", "L12", [12]], key=["L12"])
add("viparita_raja", "Viparita Raja (lords in each other's dusthanas)", "Viparita", "PVR ch. 11", "Two of the 6th, 8th and 12th lords together in a dusthana",
    ["or", *[["and", ["conj", a, b], ["in_house", a, DUS]] for a, b in (("L6", "L8"), ("L6", "L12"), ("L8", "L12"))]], key=["L6", "L8", "L12"])
for n, (sg, p, ex) in {123: (4, "Sun", ["Mars", "Jupiter"]), 124: (3, "Moon", ["Jupiter", "Mars"]), 125: ((0, 7), "Mars", ["Moon", "Venus", "Saturn"]),
                       126: ((2, 5), "Mercury", ["Saturn", "Venus"]), 127: ((8, 11), "Jupiter", ["Mercury", "Mars"]), 128: ((1, 6), "Venus", ["Saturn", "Mercury"])}.items():
    sgs = list(sg) if isinstance(sg, tuple) else [sg]
    add(f"dhana_{n}", f"Dhana yoga (BVR300 no. {n})", "Dhana", f"BVR300 no. {n}", f"{p} in the Lagna in its own sign, joined or aspected by {', '.join(ex)}",
        ["and", ["in_house", p, [1]], ["in_sign", p, sgs], *[["assoc", p, q] for q in ex]], key=[p])
for n, (p, sgs, q) in {118: ("Venus", [1, 6], ["Saturn"]), 119: ("Mercury", [2, 5], ["Moon", "Mars"]), 120: ("Saturn", [9, 10], ["Mercury", "Mars"]),
                       121: ("Sun", [4], ["Jupiter", "Moon"]), 122: ("Jupiter", [8, 11], ["Mars", "Moon"])}.items():
    add(f"dhana_{n}", f"Dhana yoga (BVR300 no. {n})", "Dhana", f"BVR300 no. {n}", f"{p} in its own sign in the 5th, with {' and '.join(q)} in the 11th",
        ["and", ["in_house", p, [5]], ["in_sign", p, sgs], *[["in_house", x, [11]] for x in q]], key=[p])
add("bahudravyarjana", "Bahudravyarjana", "Dhana", "BVR300", "Lagna lord in the 2nd, 2nd lord in the 11th, 11th lord in the Lagna",
    ["and", ["in_house", "L1", [2]], ["in_house", "L2", [11]], ["in_house", "L11", [1]]], key=["L1", "L2", "L11"])
add("madhya_vayasi_dhana", "Madhya Vayasi Dhana", "Dhana", "BVR300", "Lords of the 1st, 2nd and 11th in kendras or trines",
    ["all_in", KT, ["L1", "L2", "L11"]], key=["L1", "L2", "L11"], note="Wealth that builds in middle life.")
add("amarananta_dhana", "Amarananta Dhana", "Dhana", "BVR300 no. 142", "Several grahas in the 2nd, with the wealth-giving lords (2nd and 11th) strong or in own or exaltation signs",
    ["and", ["count_in", [2], "seven", "Lagna", ">=", 2], ["or", ["strong", "L2"], ["strong_sign", "L2"]], ["or", ["strong", "L11"], ["strong_sign", "L11"]]],
    key=["L2", "L11"])
add("ayatna_dhana", "Ayatnadhanalabha", "Dhana", "BVR300 no. 143", "The Lagna lord and the 2nd lord exchange signs",
    ["exchange", "L1", "L2"], key=["L1", "L2"])
add("dhur", "Dhur (career needs care)", "Daridra", "BVR300", "The 10th lord in the 6th, 8th or 12th", ["in_house", "L10", DUS], key=["L10"], tone="demanding",
    note="Read as effort needed in career, never as failure.")
add("daridra_11", "Daridra (gains need care)", "Daridra", "BVR300", "The 11th lord in the 6th, 8th or 12th", ["in_house", "L11", DUS], key=["L11"], tone="demanding",
    note="Read as gains that come with effort, never as poverty.")
add("daridra_147", "Daridra (BVR300 no. 147)", "Daridra", "BVR300 no. 147", "Lagna lord in the 8th, joined or aspected by the 2nd or 7th lord",
    ["and", ["in_house", "L1", [8]], ["or", ["assoc", "L1", "L2"], ["assoc", "L1", "L7"]]], key=["L1"], tone="demanding",
    note="Read as money that needs careful handling.")

# =============================================================== Neecha Bhanga (cancellation of debility), PD; BPHS
for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
    import vedic as _V
    es = _V.EXALT[p][0]
    deb = (es + 6) % 12
    from common import SIGN_LORD as _SL
    deb_lord, ex_lord = _SL[deb], _SL[es]
    add(f"neecha_bhanga_{p.lower()}", f"Neecha Bhanga Raja ({p})", "Neecha Bhanga", "PD ch. 7; BPHS",
        f"{p} is debilitated, and its debility is cancelled by at least one classical rule",
        ["and", ["dignity", p, ["debilitated"]],
         ["or", ["in_house", deb_lord, K, "Lagna"], ["in_house", deb_lord, K, "Moon"], ["in_house", ex_lord, K, "Lagna"], ["in_house", ex_lord, K, "Moon"],
          ["mutual_kendra", deb_lord, ex_lord], ["aspects", deb_lord, p], ["nav_dignity", p, ["exalted"]]]],
        key=[p], tone="mixed",
        note=(f"Rules checked: lord of the debilitation sign ({deb_lord}) or of the exaltation sign ({ex_lord}) in a kendra from the Lagna or Moon; "
              "the two in mutual kendras; the debilitation-sign lord aspecting the planet; the planet exalted in the navamsa. The reader judges how much is restored."))

# =============================================================== Parivartana (sign exchange), PVR ch. 11
PL7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
add("maha_parivartana", "Maha Parivartana", "Parivartana", "PVR ch. 11", "Exchange between lords of two houses from 1, 2, 4, 5, 7, 9, 10, 11",
    ["or", *[["exchange", f"L{a}", f"L{b}"] for a in (1, 2, 4, 5, 7, 9, 10, 11) for b in (1, 2, 4, 5, 7, 9, 10, 11) if a < b]])
add("khala_parivartana", "Khala Parivartana", "Parivartana", "PVR ch. 11", "Exchange involving the 3rd lord (and no dusthana lord)",
    ["or", *[["exchange", "L3", f"L{b}"] for b in (1, 2, 4, 5, 7, 9, 10, 11)]], tone="mixed")
add("dainya_parivartana", "Dainya Parivartana", "Parivartana", "PVR ch. 11", "Exchange involving the 6th, 8th or 12th lord",
    ["or", *[["exchange", f"L{a}", f"L{b}"] for a in (6, 8, 12) for b in range(1, 13) if a != b]], tone="demanding")

# =============================================================== House-specific combinations, BVR300 (non-medical only)
add("bhratruvriddhi", "Bhratruvriddhi", "Siblings", "BVR300 no. 177", "The 3rd lord, Mars or the 3rd house joined or aspected by benefics, with the planet concerned strong",
    ["or", ["and", ["assoc_with_kind", "L3", "benefic"], ["strong", "L3"]], ["and", ["assoc_with_kind", "Mars", "benefic"], ["strong", "Mars"]],
     ["and", ["any_in", [3], "benefic"], ["strong", "L3"]]], key=["L3", "Mars"])
add("parakrama", "Parakrama", "Siblings", "BVR300", "The 3rd lord in a benefic's navamsa (or exalted), joined or aspected by benefics, with Mars in a benefic's sign",
    ["and", ["or", ["nav_in_sign", "L3", [1, 2, 3, 5, 6, 8, 11]], ["dignity", "L3", ["exalted"]]], ["assoc_with_kind", "L3", "benefic"], ["in_sign", "Mars", [1, 2, 3, 5, 6, 8, 11]]], key=["L3", "Mars"])
add("uttama_griha", "Uttama Griha", "Home", "BVR300 no. 187", "The 4th lord in a kendra or trine, joined by benefics and aspected by benefics",
    ["and", ["in_house", "L4", KT], ["conj_with_kind", "L4", "benefic"], ["aspected_by_kind", "L4", "benefic"]], key=["L4"])
add("ayatna_griha_189", "Ayatna Griha Prapti (BVR300 no. 189)", "Home", "BVR300 no. 189", "Lords of the 1st and 7th in the 1st or 4th, aspected by benefics",
    ["and", ["in_house", "L1", [1, 4]], ["in_house", "L7", [1, 4]], ["assoc_with_kind", "L1", "benefic"]], key=["L1", "L7"])
add("ayatna_griha_190", "Ayatna Griha Prapti (BVR300 no. 190)", "Home", "BVR300 no. 190", "9th lord in a kendra and the 4th lord in exaltation, moolatrikona or own sign",
    ["and", ["in_house", "L9", K], ["strong_sign", "L4"]], key=["L9", "L4"])
add("vahana_209", "Vahana (BVR300 no. 209)", "Home", "BVR300 no. 209", "The Lagna lord in the 4th, 9th or 11th", ["in_house", "L1", [4, 9, 11]], key=["L1"])
add("vahana_210", "Vahana (BVR300 no. 210)", "Home", "BVR300 no. 210", "The 4th lord exalted, with the lord of its exaltation sign in a kendra or trine",
    ["and", ["dignity", "L4", ["exalted"]], ["in_house", "disp:L4", KT]], key=["L4"])
add("bandhu_pujya_194", "Bandhu Pujya", "Home", "BVR300 no. 194", "The 4th house or its lord joined or aspected by Jupiter",
    ["or", ["in_house", "Jupiter", [4]], ["aspects_house", "Jupiter", 4], ["conj", "Jupiter", "L4"], ["aspects", "Jupiter", "L4"]],
    key=["L4", "Jupiter"])
add("nishkapata_205", "Nishkapata (sincerity)", "Home", "BVR300 no. 205", "A benefic, or a graha in own, friendly or exaltation sign, in the 4th; or the 4th is a benefic's sign",
    ["or", ["any_in", [4], "benefic"], ["in_sign", "Lagna", [(x - 3) % 12 for x in [1, 2, 3, 5, 6, 8, 11]]], *[["and", ["in_house", p, [4]], ["dignity", p, ["own", "moolatrikona", "exalted", "friend"]]] for p in PL7]])
add("matru_sneha", "Matru Sneha", "Home", "BVR300", "Lords of the 1st and 4th the same planet, or natural friends of each other",
    ["or", ["is", "L1", "L4"], ["friends", "L1", "L4"], ["and", ["temp_friends", "L1", "L4"], ["temp_friends", "L4", "L1"]],
     ["and", ["aspected_by_kind", "L1", "benefic"], ["aspected_by_kind", "L4", "benefic"]]], key=["L1", "L4"],
    note="Three readings: one lord for both houses; natural or temporary friends; both lords aspected by benefics.")
add("buddhimaturya", "Buddhimaturya", "Intellect", "BVR300 no. 231", "A benefic 5th lord, aspected by another benefic or in a benefic's sign",
    ["and", ["is", "L5", ["Jupiter", "Venus", "Mercury"]], ["or", ["assoc_with_kind", "L5", "benefic"], ["in_sign", "L5", [1, 2, 3, 5, 6, 8, 11]]]],
    key=["L5"])
add("satkalatra", "Satkalatra", "Marriage", "BVR300 no. 239", "The 7th lord or Venus joined or aspected by Jupiter or Mercury",
    ["or", ["assoc", "L7", "Jupiter"], ["assoc", "L7", "Mercury"], ["assoc", "Venus", "Jupiter"], ["assoc", "Venus", "Mercury"]], key=["L7", "Venus"])
add("bhagya_241", "Bhagya", "Fortune", "BVR300 no. 241", "A strong benefic in the 1st, 3rd or 5th, aspecting the 9th",
    ["or", *[["and", ["in_house", b, [1, 3, 5]], ["strong", b], ["aspects_house", b, 9], ["is", b, ["Jupiter", "Venus", "Mercury", "Moon"]]]
             for b in ("Jupiter", "Venus", "Mercury", "Moon")]],
    key=["L9"])
add("dhatrutwa", "Dhatrutwa (generosity)", "Fortune", "BVR300 no. 243", "The 9th lord exalted and aspected by a benefic, with a benefic in the 9th",
    ["and", ["dignity", "L9", ["exalted"]], ["assoc_with_kind", "L9", "benefic"], ["any_in", [9], "benefic"]], key=["L9"])
add("apakeerti", "Apakeerti (reputation needs care)", "Career", "BVR300 no. 244", "Sun and Saturn in the 10th, aspected by malefics",
    ["and", ["in_house", "Sun", [10]], ["in_house", "Saturn", [10]], ["or", ["aspects", "Mars", "Sun"], ["aspects", "Rahu", "Sun"], ["aspects", "Ketu", "Sun"]]],
    key=["Sun", "Saturn"], tone="demanding", note="Read as reputation that needs protecting, never as disgrace.")
add("sumukha", "Sumukha", "Speech", "BVR300 no. 166", "The 2nd lord in a kendra aspected by benefics, or benefics in the 2nd",
    ["or", ["and", ["in_house", "L2", K], ["aspected_by_kind", "L2", "benefic"]], ["any_in", [2], "benefic"]], key=["L2"])
add("parihasaka", "Parihasaka (wit)", "Speech", "BVR300", "The Lagna lord and 2nd lord together, joined or aspected by benefics",
    ["and", ["conj", "L1", "L2"], ["assoc_with_kind", "L1", "benefic"]], key=["L1", "L2"])
add("marud", "Marud", "Named", "BVR300", "Jupiter 5th or 9th from Venus, the Moon 5th from Jupiter, and the Sun in a kendra from the Moon",
    ["and", ["rel_house", "Venus", "Jupiter", [5, 9]], ["rel_house", "Jupiter", "Moon", [5]], ["rel_house", "Moon", "Sun", K]], key=["Jupiter", "Venus", "Moon"])
add("budha_yoga", "Budha", "Intellect", "BVR300", "Jupiter in the Lagna, the Moon in a kendra, Rahu 2nd from the Moon, and the Sun and Mars 3rd from Rahu",
    ["and", ["in_house", "Jupiter", [1]], ["in_house", "Moon", K], ["rel_house", "Moon", "Rahu", [2]], ["rel_house", "Rahu", "Sun", [3]], ["rel_house", "Rahu", "Mars", [3]]],
    key=["Jupiter", "Moon"])
add("bhojana_soukhya", "Bhojana Soukhya", "Speech", "BVR300", "A strong 2nd lord aspected by Jupiter or Venus",
    ["and", ["strong", "L2"], ["or", ["aspects", "Jupiter", "L2"], ["aspects", "Venus", "L2"]]], key=["L2"],
    note="Raman also wants the 2nd lord in Vaiseshikamsa, which the engine does not compute.")
add("guru_chandal", "Rahu-Jupiter conjunction (Guru Chandal)", "Dosha-like", "PVR ch. 11", "Jupiter and Rahu in the same sign",
    ["conj", "Jupiter", "Rahu"], key=["Jupiter"], tone="mixed", note="Also reported in the doshas section.")

# Yogas deliberately NOT implemented: they concern death, longevity, named diseases, bodily defects, sexual conduct,
# multiple spouses, childlessness or loss of children, imprisonment, punishment or curses. The skill never predicts these.
EXCLUDED = [
    "BVR300 combinations on death, longevity and the manner of death (e.g. Dhurmarana, Yuddha Marana, parent's death before birth)",
    "BVR300 combinations on named diseases and bodily defects (Kshaya, Kushta, Vrana, blindness, mental illness and similar)",
    "BVR300 combinations on adultery, multiple spouses and sexual conduct (Jara, Bahu Sthree, Bhaga Chumbana and similar)",
    "BVR300 combinations on childlessness, loss of children and curses (Anapatya, Aputra, Sarpa / Pitru / Matru Shapa and similar)",
    "BVR300 combinations on imprisonment and mutilation (Bandhana, Karaccheda, Siraccheda)",
    "Combinations needing Shashtiamsa or Vaiseshikamsa grades (Parvatamsa, Gopuramsa and similar), not computed by the engine",
]
RULES = R
