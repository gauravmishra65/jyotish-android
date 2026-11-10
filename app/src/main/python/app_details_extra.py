"""app_details_extra.py - Kundali sections for values the engine computes that the app did not show before (v16):
upagrahas, planetary avasthas, functional nature with baadhakas, more sign dashas (Kalachakra, Sudasa, Drig and
Lagna Kendradi), and Western extras (solar arc and the four main asteroids with Chiron). App-owned, bilingual.

House rules apply: no sentence names death, illness or divorce. The Mrityu upagraha is left out for that reason, and
the fifth Baaladi state (Mrita) is described only as the weakest state.
"""
import datetime as dt

import hindi_shell as HS
from app_details import bi, P, S, date, table, para, items, pos, house_word, SIGNS

SIGN_HI = HS.SIGN


def _span_years(a, b):
    return bi(f"{a[:4]}–{b[:4]}", f"{a[:4]}–{b[:4]}")


# ------------------------------------------------------------------ upagrahas
UPA = {
    "Gulika": ("Gulika", "गुलिक", "Saturn's sub-planet; the house it sits in asks for patience", "शनि का उपग्रह; जिस भाव में हो वहाँ धैर्य माँगता है"),
    "Mandi": ("Mandi", "मांदि", "Saturn's sub-planet by the other common rule", "दूसरे प्रचलित नियम से शनि का उपग्रह"),
    "Kaala": ("Kaala", "काल", "the Sun's sub-planet", "सूर्य का उपग्रह"),
    "Artha Prahara": ("Artha Prahara", "अर्ध प्रहर", "Mercury's sub-planet", "बुध का उपग्रह"),
    "Yama Ghantaka": ("Yama Ghantaka", "यमघंटक", "Jupiter's sub-planet", "गुरु का उपग्रह"),
    "Dhuma": ("Dhuma", "धूम", "Sun-based point", "सूर्य पर आधारित बिंदु"),
    "Vyatipata": ("Vyatipata", "व्यतीपात", "Sun-based point", "सूर्य पर आधारित बिंदु"),
    "Parivesha": ("Parivesha", "परिवेष", "Sun-based point", "सूर्य पर आधारित बिंदु"),
    "Indrachapa": ("Indrachapa", "इंद्रचाप", "Sun-based point", "सूर्य पर आधारित बिंदु"),
    "Upaketu": ("Upaketu", "उपकेतु", "Sun-based point", "सूर्य पर आधारित बिंदु"),
}


def upagrahas(v):
    u = v.get("upagrahas") or {}
    rows = []
    for group in ("time_based", "dhuma_group"):
        for k, o in (u.get(group) or {}).items():
            if k not in UPA:
                continue      # Mrityu is left out by house rule
            en, hi, use_en, use_hi = UPA[k]
            rows.append([bi(en, hi), pos(o.get("position")), house_word(o["house"]), bi(o.get("nakshatra", ""), HS.NAK.get(o.get("nakshatra", ""), o.get("nakshatra", ""))),
                         bi(use_en, use_hi)])
    if not rows:
        return None
    return {"key": "upagrahas", "title": bi("Upagrahas (sub-planets)", "उपग्रह"),
            "intro": bi("Upagrahas are sensitive points worked out from the day of birth. Gulika and Mandi are the ones most astrologers read.",
                        "उपग्रह जन्म के दिन से निकाले गए संवेदनशील बिंदु हैं। अधिकतर ज्योतिषी गुलिक और मांदि को पढ़ते हैं।"),
            "blocks": [table([bi("Upagraha", "उपग्रह"), bi("Position", "स्थिति"), bi("House", "भाव"), bi("Nakshatra", "नक्षत्र"), bi("What it is", "क्या है")], rows)],
            "note": bi("Gulika at the start and Mandi at the middle of Saturn's part of the day (Jagannatha Hora's default); some texts swap them.",
                       "गुलिक शनि के दिन-भाग के आरंभ में और मांदि मध्य में (जगन्नाथ होरा का सामान्य नियम); कुछ ग्रंथ दोनों को उलट देते हैं।")}


# ------------------------------------------------------------------ avasthas
BAAL = {"Saisava": ("Bala (infant): about a quarter of its results", "बाल (शिशु): लगभग एक-चौथाई फल"),
        "Kumaara": ("Kumara (adolescent): about half", "कुमार (किशोर): लगभग आधा फल"),
        "Yuva": ("Yuva (youth): full results", "युवा: पूर्ण फल"),
        "Vriddha": ("Vriddha (old): some results", "वृद्ध: कुछ फल"),
        "Mrita": ("Mrita: the weakest state, few results", "पाँचवीं अवस्था: सबसे क्षीण, कम फल")}
JAAG = {"Jaagrita": ("Jaagrita (awake): full results", "जाग्रत: पूर्ण फल"),
        "Swapna": ("Swapna (dreaming): medium results", "स्वप्न: मध्यम फल"),
        "Sushupta": ("Sushupta (deep sleep): little result", "सुषुप्त: अल्प फल")}
MOOD = {"Deepta": ("Deepta (bright)", "दीप्त"), "Swastha": ("Swastha (content)", "स्वस्थ (संतुष्ट)"), "Mudita": ("Mudita (delighted)", "मुदित"),
        "Saanta": ("Saanta (peaceful)", "शांत"), "Deena": ("Deena (low)", "दीन"), "Duhkhita": ("Duhkhita (distressed)", "दुःखित"),
        "Vikala": ("Vikala (joined by malefics)", "विकल"), "Khala": ("Khala (in a malefic's sign)", "खल"),
        "Kopita": ("Kopita (close to the Sun)", "कोपित"), "Lajjita": ("Lajjita (ashamed)", "लज्जित"), "Garvita": ("Garvita (proud)", "गर्वित"),
        "Kshudhita": ("Kshudhita (hungry)", "क्षुधित"), "Trishita": ("Trishita (thirsty)", "तृषित"), "Kshobhita": ("Kshobhita (agitated)", "क्षोभित")}
SAYANA = {"Nidraa": ("Nidra (sleeping)", "निद्रा"), "Sayana": ("Sayana (lying down)", "शयन"), "Upavesana": ("Upaveshana (sitting)", "उपवेशन"),
          "Netrapaani": ("Netrapani (eyes and hands)", "नेत्रपाणि"), "Prakaasana": ("Prakashana (shining)", "प्रकाशन"), "Gamana": ("Gamana (going)", "गमन"),
          "Aagamana": ("Agamana (returning)", "आगमन"), "Sabhaa": ("Sabha (at an assembly)", "सभा"), "Aagama": ("Agama (acquiring)", "आगम"),
          "Bhojana": ("Bhojana (eating)", "भोजन"), "Nriyalipsaa": ("Nrityalipsa (longing to dance)", "नृत्यलिप्सा"), "Kautuka": ("Kautuka (eager)", "कौतुक")}


def _lab(table_, text):
    key = (text or "").split(" ")[0]
    en, hi = table_.get(key, (key, key))
    return bi(en, hi)


def avasthas(v):
    av = (v.get("parashari") or {}).get("avasthas") or {}
    rows = []
    for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"):
        o = av.get(p)
        if not o:
            continue
        moods = [_lab(MOOD, o["deeptaadi"])] if o.get("deeptaadi") else []
        moods += [_lab(MOOD, f) for f in o.get("mood_flags", [])]
        rows.append([P(p), _lab(BAAL, o.get("baaladi")) if o.get("baaladi") else bi("–"),
                     _lab(JAAG, o.get("jaagradaadi")) if o.get("jaagradaadi") else bi("–"),
                     bi(", ".join(m["en"] for m in moods) or "–", ", ".join(m["hi"] for m in moods) or "–"),
                     _lab(SAYANA, o.get("sayanaadi")) if o.get("sayanaadi") else bi("–")])
    if not rows:
        return None
    return {"key": "avasthas", "title": bi("Planetary states (avasthas)", "ग्रह अवस्थाएँ"),
            "intro": bi("Avasthas describe how freely a planet can give its results: its age by degree (Baaladi), its awareness (Jagradadi), "
                        "its mood (Deeptadi) and its activity (Shayanadi).",
                        "अवस्थाएँ बताती हैं कि ग्रह कितनी सहजता से फल दे सकता है: अंश से उसकी आयु (बालादि), जागृति (जाग्रदादि), "
                        "मनोदशा (दीप्तादि) और क्रिया (शयनादि)।"),
            "blocks": [table([bi("Planet", "ग्रह"), bi("Baaladi (age)", "बालादि (आयु)"), bi("Jagradadi (awareness)", "जाग्रदादि (जागृति)"),
                              bi("Deeptadi (mood)", "दीप्तादि (मनोदशा)"), bi("Shayanadi (activity)", "शयनादि (क्रिया)")], rows)],
            "note": bi("BPHS rules as given by P.V.R. Narasimha Rao. Avasthas refine a reading; they do not override dignity and house.",
                       "बीपीएचएस के नियम, पी.वी.आर. नरसिंह राव के अनुसार। अवस्थाएँ फलादेश को परिष्कृत करती हैं; राशि-स्थिति और भाव से ऊपर नहीं।")}


# ------------------------------------------------------------------ functional nature and baadhakas
def functional(v):
    pa = v.get("parashari") or {}
    fn = pa.get("functional_nature")
    if not fn:
        return None
    def names(lst):
        return bi(", ".join(lst) or "–", ", ".join(HS.PLANET.get(x, x) for x in lst) or "–")
    rows = [[bi("Yogakaraka", "योगकारक"), names([fn["yogakaraka"]] if fn.get("yogakaraka") else [])],
            [bi("Functional benefics", "कार्यात्मक शुभ"), names(fn.get("functional_benefics", []))],
            [bi("Neutral", "सम"), names(fn.get("functional_neutrals", []))],
            [bi("Functional malefics", "कार्यात्मक पाप"), names(fn.get("functional_malefics", []))]]
    blocks = [table([bi("Role for this Lagna", "इस लग्न के लिए भूमिका"), bi("Planets", "ग्रह")], rows)]
    bd = (pa.get("baadhakas") or {}).get("H1")
    if bd:
        blocks.append(para(bi(f"Baadhaka (obstructing) house for the Lagna: the sign {bd['baadhaka_sthaana']}, ruled by {', '.join(bd['baadhaka'])}. "
                              "Its periods can bring delays that patience resolves.",
                              f"लग्न के लिए बाधक भाव: {SIGN_HI.get(bd['baadhaka_sthaana'], bd['baadhaka_sthaana'])} राशि, स्वामी "
                              f"{', '.join(HS.PLANET.get(x, x) for x in bd['baadhaka'])}। इसकी दशाएँ देरी ला सकती हैं, जिन्हें धैर्य से पार किया जाता है।")))
    return {"key": "functional", "title": bi("Functional benefics and malefics", "कार्यात्मक शुभ और पाप ग्रह"),
            "intro": bi("For each Lagna some planets work as friends and some as obstacles, whatever their natural nature. A yogakaraka rules both a kendra and a trikona.",
                        "हर लग्न के लिए कुछ ग्रह मित्र और कुछ बाधक की तरह काम करते हैं, उनका नैसर्गिक स्वभाव कुछ भी हो। योगकारक केंद्र और त्रिकोण दोनों का स्वामी होता है।"),
            "blocks": blocks, "note": bi(f"Source: {fn.get('source', 'P.V.R. Narasimha Rao')}.", f"स्रोत: {fn.get('source', 'P.V.R. Narasimha Rao')}।")}


# ------------------------------------------------------------------ more sign dashas
def _cycle_dates(first_cycle, birth, balance=1.0):
    """Turn a first cycle [{sign, years}] into dated periods from birth; the first period runs only for its balance."""
    out, t = [], dt.date.fromisoformat(birth[:10])
    for i, x in enumerate(first_cycle):
        yrs = x["years"] * (balance if i == 0 else 1.0)
        e = t + dt.timedelta(days=round(yrs * 365.2425))
        out.append((x["sign"], t.isoformat(), e.isoformat()))
        t = e
    return out


def more_dashas(v, now, birth):
    rd = v.get("rasi_dashas") or {}
    blocks = []
    kc = rd.get("kalachakra")
    if kc and kc.get("dasas"):
        rows = [[S(d["sign"]), _span_years(d["start"], d["end"]), bi("now", "चालू") if d["start"] <= now < d["end"] else bi("")] for d in kc["dasas"]]
        blocks += [para(bi(f"Kalachakra dasha (group {kc.get('group', '')}; deha {kc.get('deha_rasi', '')}, jeeva {kc.get('jeeva_rasi', '')}):",
                           f"कालचक्र दशा (समूह {kc.get('group', '').replace('Apasavya', 'अपसव्य').replace('Savya', 'सव्य')}; देह {SIGN_HI.get(kc.get('deha_rasi', ''), '')}, जीव {SIGN_HI.get(kc.get('jeeva_rasi', ''), '')}):")),
                   table([bi("Sign", "राशि"), bi("Years", "वर्ष"), bi("", "")], rows)]
    for key, en, hi, why_en, why_hi in (("sudasa", "Sudasa", "सुदशा", "read for wealth and status, from the Sree Lagna", "धन और प्रतिष्ठा के लिए, श्री लग्न से"),
                                        ("drigdasa", "Drig dasha", "दृग दशा", "read for spiritual growth", "आध्यात्मिक उन्नति के लिए"),
                                        ("lagna_kendradi", "Lagna Kendradi dasha", "लग्न केंद्रादि दशा", "a general sign dasha from the stronger of Lagna and 7th", "लग्न और सप्तम में से बली राशि से सामान्य राशि दशा")):
        d = rd.get(key)
        if not d or not d.get("first_cycle"):
            continue
        per = _cycle_dates(d["first_cycle"], birth, d.get("first_dasa_balance_fraction", 1.0) if key == "sudasa" else 1.0)
        rows = [[S(sg), _span_years(a, b), bi("now", "चालू") if a <= now < b else bi("")] for sg, a, b in per]
        blocks += [para(bi(f"{en}, {why_en}:", f"{hi}, {why_hi}:")), table([bi("Sign", "राशि"), bi("Years", "वर्ष"), bi("", "")], rows)]
    if not blocks:
        return None
    return {"key": "more_dashas", "title": bi("More sign dashas", "अन्य राशि दशाएँ"),
            "intro": bi("Sign-based dashas used beside Vimshottari, each for its own purpose. Read them as timing for themes, never alone.",
                        "विंशोत्तरी के साथ प्रयुक्त राशि आधारित दशाएँ, हर एक का अपना उद्देश्य। इन्हें विषयों के समय के रूप में पढ़ें, अकेले नहीं।"),
            "blocks": blocks, "note": bi("Rules from P.V.R. Narasimha Rao, 'Vedic Astrology: An Integrated Approach'. The first Sudasa period is the balance left at birth.",
                                         "नियम पी.वी.आर. नरसिंह राव की 'वैदिक एस्ट्रोलॉजी: एन इंटीग्रेटेड अप्रोच' से। पहली सुदशा अवधि जन्म के समय शेष भाग है।")}


# ------------------------------------------------------------------ western extras
def _dm(dms):
    """'2°07'03"' -> '2°07′'."""
    d, _, rest = (dms or "").partition("°")
    return f"{d}°{rest[:2]}′" if rest else dms

def western_extra(c):
    w = c.get("western") or {}
    blocks = []
    sa = w.get("solar_arc") or {}
    if sa.get("directed_angles"):
        rows = [[bi(k, {"Ascendant": "लग्न (असेंडेंट)", "Midheaven": "मध्याकाश (MC)"}.get(k, k)), pos(x)] for k, x in sa["directed_angles"].items()]
        blocks += [para(bi(f"Solar arc directions: everything moves forward by the Sun's progressed arc, now {sa.get('arc_degrees', 0):.1f}°.",
                           f"सोलर आर्क दिशाएँ: हर बिंदु सूर्य के प्रोग्रेस्ड चाप जितना आगे, अभी {sa.get('arc_degrees', 0):.1f}°।")),
                   table([bi("Directed angle", "निर्देशित कोण"), bi("Now at", "अभी")], rows)]
        hits = sa.get("hits_within_1_degree") or []
        asp_hi = HS.ASPECT
        ang_hi = {"Ascendant": "लग्न", "Midheaven": "मध्याकाश"}
        if hits:
            blocks.append(para(bi("Directed angles now within 1° of a natal planet:", "अभी किसी जन्म ग्रह से 1° के भीतर निर्देशित कोण:")))
            blocks.append(items([bi(f"Directed {h['directed']} {h['aspect']} natal {h['natal']} (orb {h['orb']:.1f}°)",
                                    f"निर्देशित {ang_hi.get(h['directed'], HS.PLANET.get(h['directed'], h['directed']))} – जन्म {HS.PLANET.get(h['natal'], h['natal'])}: "
                                    f"{asp_hi.get(h['aspect'], h['aspect'])} (अंतर {h['orb']:.1f}°)") for h in hits[:8]]))
    ep = (w.get("extra_points") or {}).get("points") or {}
    names = {"Chiron": ("Chiron: where old hurts become the gift of helping others", "काइरॉन: जहाँ पुराने घाव दूसरों की सहायता का गुण बनते हैं"),
             "Ceres": ("Ceres: nurturing and care", "सेरेस: पालन और देखभाल"), "Pallas": ("Pallas: strategy and pattern-seeing", "पलास: रणनीति और पैटर्न की समझ"),
             "Juno": ("Juno: commitment in partnership", "जूनो: साझेदारी में प्रतिबद्धता"), "Vesta": ("Vesta: focus and devotion", "वेस्टा: एकाग्रता और समर्पण")}
    rows = [[bi(names[k][0].split(":")[0], names[k][1].split(":")[0]), bi(f"{o['sign']} {_dm(o['dms'])}" + (" (R)" if o.get("retrograde") else ""),
             f"{SIGN_HI.get(o['sign'], o['sign'])} {_dm(o['dms'])}" + (" (व)" if o.get("retrograde") else "")),
             house_word(o.get("house_placidus") or o.get("house_whole_sign")), bi(names[k][0].split(": ")[1], names[k][1].split(": ")[1])]
            for k, o in ep.items() if k in names]
    if rows:
        blocks += [para(bi("Chiron and the main asteroids (tropical, Placidus houses):", "काइरॉन और मुख्य क्षुद्रग्रह (सायन, प्लेसिडस भाव):")),
                   table([bi("Point", "बिंदु"), bi("Position", "स्थिति"), bi("House", "भाव"), bi("Theme", "विषय")], rows)]
    if not blocks:
        return None
    return {"key": "western_extra", "title": bi("Western: solar arc and asteroids", "पाश्चात्य: सोलर आर्क और क्षुद्रग्रह"), "blocks": blocks,
            "note": bi("Western positions are tropical, so their signs differ from the Vedic chart above by about 24°.",
                       "पाश्चात्य स्थितियाँ सायन हैं, इसलिए उनकी राशियाँ ऊपर की वैदिक कुंडली से लगभग 24° अलग हैं।")}


def build_extra(c):
    v = c["vedic"]
    now = c["meta"].get("generated_for_date", "")
    birth = v["dashas"]["vimshottari"]["mahadashas"][0]["start"]
    out = []
    for f in ((lambda: functional(v)), (lambda: avasthas(v)), (lambda: upagrahas(v)), (lambda: more_dashas(v, now, birth)), (lambda: western_extra(c))):
        try:
            s = f()
        except (KeyError, TypeError, ValueError, IndexError):
            s = None
        if s:
            out.append(s)
    return out
