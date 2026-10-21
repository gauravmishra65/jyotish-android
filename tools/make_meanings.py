"""Build app/src/main/assets/meanings.json: the plain-words meanings the app shows, in English and Hindi.

Usage:  python tools/make_meanings.py

Rules for every line here (the same as the skill's readings): describe what a factor is traditionally associated
with; never predict death, disease, divorce or other outcomes; no promises; a demanding factor is a reason for
care, not a verdict. Hindi is written to be read, not transliterated word by word.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "app", "src", "main", "assets", "meanings.json")
sys.path.insert(0, os.path.join(HERE, "..", "app", "src", "main", "python"))

PLANETS = {
    "Sun": ("Self, vitality, father and authority: how a person leads and is seen.",
            "आत्मा, ऊर्जा, पिता और अधिकार: व्यक्ति कैसे नेतृत्व करता है और कैसे देखा जाता है।"),
    "Moon": ("Mind, feelings, mother and comfort: how a person reacts and what reassures them.",
             "मन, भावनाएँ, माता और सुख: व्यक्ति कैसे प्रतिक्रिया करता है और किससे आश्वस्त होता है।"),
    "Mars": ("Energy, courage, siblings and property: how a person acts and competes.",
             "ऊर्जा, साहस, भाई-बहन और भूमि: व्यक्ति कैसे कर्म करता है और कैसे स्पर्धा करता है।"),
    "Mercury": ("Intellect, speech, trade and learning: how a person thinks and communicates.",
                "बुद्धि, वाणी, व्यापार और शिक्षा: व्यक्ति कैसे सोचता है और कैसे संवाद करता है।"),
    "Jupiter": ("Wisdom, teachers, children and good fortune: what a person believes and how they grow.",
                "ज्ञान, गुरु, संतान और सौभाग्य: व्यक्ति क्या मानता है और कैसे आगे बढ़ता है।"),
    "Venus": ("Love, beauty, comforts, the arts and partnership: what a person enjoys and values.",
              "प्रेम, सौंदर्य, सुख-सुविधाएँ, कला और साझेदारी: व्यक्ति किसका आनंद लेता है और किसे महत्व देता है।"),
    "Saturn": ("Duty, patience, work and endurance: where effort is asked for and steadily rewarded.",
               "कर्तव्य, धैर्य, परिश्रम और सहनशक्ति: जहाँ प्रयास माँगा जाता है और धीरे-धीरे फल देता है।"),
    "Rahu": ("Ambition, the unusual and the foreign: where a person reaches beyond the familiar.",
             "महत्वाकांक्षा, असामान्य और विदेशी: जहाँ व्यक्ति परिचित से आगे बढ़ना चाहता है।"),
    "Ketu": ("Detachment, insight and the spiritual: where a person lets go or looks inward.",
             "वैराग्य, अंतर्दृष्टि और आध्यात्मिकता: जहाँ व्यक्ति छोड़ना या भीतर देखना सीखता है।"),
}

HOUSES = {
    1: ("self, body and outlook", "स्वयं, शरीर और दृष्टिकोण"),
    2: ("family, speech, savings and food", "परिवार, वाणी, संचित धन और भोजन"),
    3: ("courage, effort, siblings, short journeys and communication", "साहस, प्रयास, भाई-बहन, छोटी यात्राएँ और संवाद"),
    4: ("home, mother, comfort, property and peace of mind", "घर, माता, सुख, संपत्ति और मन की शांति"),
    5: ("children, learning, creativity and good judgement", "संतान, विद्या, रचनात्मकता और विवेक"),
    6: ("daily work, service, health habits and competition", "दैनिक कार्य, सेवा, स्वास्थ्य की आदतें और प्रतिस्पर्धा"),
    7: ("partnership, marriage and dealings with others", "साझेदारी, विवाह और दूसरों से व्यवहार"),
    8: ("change, research, hidden matters and shared resources", "परिवर्तन, शोध, गूढ़ विषय और साझा संसाधन"),
    9: ("fortune, father, teachers, faith and long journeys", "भाग्य, पिता, गुरु, आस्था और लंबी यात्राएँ"),
    10: ("career, status and public life", "करियर, प्रतिष्ठा और सार्वजनिक जीवन"),
    11: ("gains, friends, networks and hopes", "लाभ, मित्र, संपर्क और आकांक्षाएँ"),
    12: ("expenses, rest, foreign lands and letting go", "व्यय, विश्राम, विदेश और त्याग"),
}

YOGA_CATEGORIES = {
    "Nabhasa (Ashraya)": ("A Nabhasa yoga, from how the planets are spread across movable, fixed and dual signs. It describes a general temperament rather than events.",
                          "नाभस योग, जो चर, स्थिर और द्विस्वभाव राशियों में ग्रहों के फैलाव से बनता है। यह घटनाएँ नहीं, सामान्य स्वभाव बताता है।"),
    "Nabhasa (Dala)": ("A Nabhasa yoga, from benefics or malefics filling the kendras. It colours the general tone of life.",
                       "नाभस योग, जो केंद्रों में शुभ या पाप ग्रहों के होने से बनता है। यह जीवन के सामान्य स्वर को रंगता है।"),
    "Nabhasa (Akriti)": ("A Nabhasa yoga, named after the shape the planets make across the houses. It colours the overall pattern of life.",
                         "नाभस योग, जिसका नाम भावों में ग्रहों से बनी आकृति पर है। यह जीवन के समग्र ढाँचे को रंगता है।"),
    "Nabhasa (Sankhya)": ("A Nabhasa yoga, from how many signs the planets occupy. Every chart has one, so on its own it says little about a person.",
                          "नाभस योग, जो इससे बनता है कि ग्रह कितनी राशियों में हैं। हर कुंडली में ऐसा एक योग होता है, इसलिए अकेले यह किसी व्यक्ति के बारे में कम बताता है।"),
    "Solar": ("Formed by planets on either side of the Sun: about how a person acts and how they are supported.",
              "सूर्य के दोनों ओर के ग्रहों से बनता है: व्यक्ति कैसे कर्म करता है और उसे कैसा सहारा मिलता है।"),
    "Lunar": ("Formed around the Moon: about the mind, emotional support and resources.",
              "चंद्र के आसपास के ग्रहों से बनता है: मन, भावनात्मक सहारा और साधन।"),
    "Lagna": ("About planets beside or in the lagna: it colours outlook and how life is approached.",
              "लग्न के दोनों ओर या लग्न में ग्रहों से: यह दृष्टिकोण और जीवन जीने के ढंग को रंगता है।"),
    "Pancha Mahapurusha": ("One of the five 'great person' yogas: a strong planet in its own or exaltation sign in a kendra. It brings that planet's qualities forward.",
                           "पाँच महापुरुष योगों में से एक: अपनी या उच्च राशि में केंद्र में स्थित बलवान ग्रह। यह उस ग्रह के गुणों को आगे लाता है।"),
    "Named": ("A classical combination named in the texts. Read it as one supporting thread among many.",
              "शास्त्रों में नाम से वर्णित एक योग। इसे कई सहायक सूत्रों में से एक मानें।"),
    "Malika": ("A garland: planets in seven signs in a row, named after the house where the garland starts.",
               "मालिका: लगातार सात राशियों में ग्रह, जिसका नाम उस भाव पर है जहाँ से माला शुरू होती है।"),
    "Raja": ("A raja yoga links the lords of kendras and trikonas. It is traditionally associated with status and recognition, especially in the periods of the planets involved.",
             "राज योग केंद्र और त्रिकोण के स्वामियों को जोड़ता है। परंपरा से इसे प्रतिष्ठा और पहचान से जोड़ा जाता है, विशेषकर संबंधित ग्रहों की दशा में।"),
    "Dhana": ("A dhana yoga links the houses of wealth (2, 5, 9, 11). It is traditionally associated with earning and keeping resources, more so in the related periods.",
              "धन योग धन के भावों (2, 5, 9, 11) को जोड़ता है। परंपरा से इसे कमाने और सँभालने से जोड़ा जाता है, संबंधित दशाओं में अधिक।"),
    "Viparita": ("A viparita raja yoga: lords of difficult houses placed in difficult houses. It is traditionally read as gains that come after setbacks.",
                 "विपरीत राज योग: कठिन भावों के स्वामी कठिन भावों में। परंपरा से इसे बाधाओं के बाद मिलने वाले लाभ के रूप में पढ़ा जाता है।"),
    "Daridra": ("A combination the texts read as needing care in this area. It is a reason for steady effort, not a fixed outcome; supportive yogas and periods weigh against it.",
                "ऐसा योग जिसे शास्त्र इस क्षेत्र में सावधानी का संकेत मानते हैं। यह निरंतर प्रयास का कारण है, तय परिणाम नहीं; सहायक योग और दशाएँ इसका प्रभाव घटाती हैं।"),
    "Neecha Bhanga": ("A debilitated planet whose weakness is cancelled by classical rules. It is traditionally read as a slow start that turns into strength.",
                      "नीच ग्रह जिसकी दुर्बलता शास्त्रीय नियमों से भंग होती है। परंपरा से इसे धीमी शुरुआत के बाद बढ़ती शक्ति के रूप में पढ़ा जाता है।"),
    "Parivartana": ("Two planets in each other's signs, linking their houses. Its effect depends on which houses are exchanged.",
                    "दो ग्रह एक-दूसरे की राशि में, जो उनके भावों को जोड़ते हैं। इसका प्रभाव इस पर निर्भर है कि कौन-से भाव जुड़े हैं।"),
    "Siblings": ("About siblings, courage and initiative.", "भाई-बहन, साहस और पहल से संबंधित।"),
    "Home": ("About home, vehicles, comforts and family support.", "घर, वाहन, सुख-सुविधा और परिवार के सहारे से संबंधित।"),
    "Intellect": ("About intelligence, learning and judgement.", "बुद्धि, विद्या और विवेक से संबंधित।"),
    "Marriage": ("About partnership and the spouse.", "साझेदारी और जीवनसाथी से संबंधित।"),
    "Fortune": ("About luck, generosity and dharma.", "भाग्य, उदारता और धर्म से संबंधित।"),
    "Career": ("About reputation and work. It asks for care with how one is seen.", "प्रतिष्ठा और कार्य से संबंधित। यह छवि के प्रति सावधानी माँगता है।"),
    "Speech": ("About speech, food and the manner of expression.", "वाणी, भोजन और अभिव्यक्ति के ढंग से संबंधित।"),
    "Dosha-like": ("A combination many astrologers treat with caution and others give little weight. It is not a prediction.",
                   "ऐसा योग जिसे कई ज्योतिषी सावधानी से देखते हैं और कुछ कम महत्व देते हैं। यह कोई भविष्यवाणी नहीं है।"),
}

YOGAS = {  # by yoga id: the specific meaning shown before the category's
    "gaja_kesari": ("Jupiter in a kendra from the Moon. Traditionally associated with good sense, respect and helpful connections.",
                    "चंद्र से केंद्र में गुरु। परंपरा से इसे सद्बुद्धि, सम्मान और सहायक संबंधों से जोड़ा जाता है।"),
    "budha_aditya": ("Mercury with the Sun. Traditionally associated with intelligence, skill with words and practical cleverness.",
                     "सूर्य के साथ बुध। परंपरा से इसे बुद्धि, वाणी-कौशल और व्यावहारिक चतुराई से जोड़ा जाता है।"),
    "chandra_mangala": ("Moon with Mars. Traditionally associated with drive and enterprise in earning.",
                        "चंद्र के साथ मंगल। परंपरा से इसे कमाई में उत्साह और उद्यम से जोड़ा जाता है।"),
    "sunapha": ("A planet in the 2nd from the Moon. Traditionally associated with self-made resources and steadiness.",
                "चंद्र से दूसरे भाव में ग्रह। परंपरा से इसे स्वअर्जित साधनों और स्थिरता से जोड़ा जाता है।"),
    "anapha": ("A planet in the 12th from the Moon. Traditionally associated with good manners, ease and a sense of self.",
               "चंद्र से बारहवें भाव में ग्रह। परंपरा से इसे शिष्टता, सहजता और आत्मविश्वास से जोड़ा जाता है।"),
    "durudhara": ("Planets on both sides of the Moon. Traditionally associated with comfort and support from many sides.",
                  "चंद्र के दोनों ओर ग्रह। परंपरा से इसे सुख और कई ओर से मिलने वाले सहारे से जोड़ा जाता है।"),
    "kemadruma": ("No planet beside the Moon. Traditionally read as times of feeling unsupported; it is often cancelled by planets in kendras, and many charts carry it.",
                  "चंद्र के दोनों ओर कोई ग्रह नहीं। परंपरा से इसे कभी-कभी अकेलेपन की अनुभूति के रूप में पढ़ा जाता है; केंद्र के ग्रह अक्सर इसे भंग करते हैं, और यह बहुत-सी कुंडलियों में मिलता है।"),
    "vesi": ("A planet in the 2nd from the Sun. Traditionally associated with balance and a truthful nature.",
             "सूर्य से दूसरे भाव में ग्रह। परंपरा से इसे संतुलन और सत्यनिष्ठा से जोड़ा जाता है।"),
    "vasi": ("A planet in the 12th from the Sun. Traditionally associated with generosity and skill. Very common.",
             "सूर्य से बारहवें भाव में ग्रह। परंपरा से इसे उदारता और कौशल से जोड़ा जाता है। यह बहुत सामान्य है।"),
    "ubhayachari": ("Planets on both sides of the Sun. Traditionally associated with eloquence and a balanced life.",
                    "सूर्य के दोनों ओर ग्रह। परंपरा से इसे वाक्पटुता और संतुलित जीवन से जोड़ा जाता है।"),
    "adhi": ("Benefics in the 6th, 7th and 8th from the Moon. Traditionally associated with leadership and comfort.",
             "चंद्र से छठे, सातवें और आठवें भाव में शुभ ग्रह। परंपरा से इसे नेतृत्व और सुख से जोड़ा जाता है।"),
    "amala_lagna": ("A benefic in the 10th from the lagna. Traditionally associated with a good name earned through conduct.",
                    "लग्न से दसवें भाव में शुभ ग्रह। परंपरा से इसे अच्छे आचरण से मिली कीर्ति से जोड़ा जाता है।"),
    "amala_moon": ("A benefic in the 10th from the Moon. Traditionally associated with a good name earned through conduct.",
                   "चंद्र से दसवें भाव में शुभ ग्रह। परंपरा से इसे अच्छे आचरण से मिली कीर्ति से जोड़ा जाता है।"),
    "mahapurusha_mars": ("Ruchaka: a strong Mars. Traditionally associated with courage, energy and leadership in action.",
                         "रुचक: बलवान मंगल। परंपरा से इसे साहस, ऊर्जा और कर्म में नेतृत्व से जोड़ा जाता है।"),
    "mahapurusha_mercury": ("Bhadra: a strong Mercury. Traditionally associated with intellect, speech and skill in trade or learning.",
                            "भद्र: बलवान बुध। परंपरा से इसे बुद्धि, वाणी और व्यापार या विद्या में कौशल से जोड़ा जाता है।"),
    "mahapurusha_jupiter": ("Hamsa: a strong Jupiter. Traditionally associated with wisdom, good character and respect.",
                            "हंस: बलवान गुरु। परंपरा से इसे ज्ञान, सच्चरित्र और सम्मान से जोड़ा जाता है।"),
    "mahapurusha_venus": ("Malavya: a strong Venus. Traditionally associated with a taste for beauty, comfort and the arts, and an easy charm with people.",
                          "मालव्य: बलवान शुक्र। परंपरा से इसे सौंदर्य, सुख और कला के प्रति रुचि तथा लोगों से सहज आकर्षण से जोड़ा जाता है।"),
    "mahapurusha_saturn": ("Sasa: a strong Saturn. Traditionally associated with authority gained through discipline and patient work.",
                           "शश: बलवान शनि। परंपरा से इसे अनुशासन और धैर्यपूर्ण परिश्रम से मिले अधिकार से जोड़ा जाता है।"),
    "lakshmi": ("Traditionally associated with prosperity, refinement and generosity.", "परंपरा से इसे समृद्धि, परिष्कार और उदारता से जोड़ा जाता है।"),
    "saraswati": ("Traditionally associated with learning, the arts and eloquence.", "परंपरा से इसे विद्या, कला और वाक्पटुता से जोड़ा जाता है।"),
    "parijata": ("Traditionally associated with steady rise and contentment. Very common, so it says little on its own.",
                 "परंपरा से इसे क्रमिक उन्नति और संतोष से जोड़ा जाता है। यह बहुत सामान्य है, इसलिए अकेले कम बताता है।"),
    "kalpadruma": ("Traditionally associated with wishes fulfilled through one's own effort, and a principled nature.",
                   "परंपरा से इसे अपने प्रयास से इच्छापूर्ति और सिद्धांतप्रिय स्वभाव से जोड़ा जाता है।"),
    "chamara": ("Traditionally associated with learning, eloquence and recognition.", "परंपरा से इसे विद्या, वाक्पटुता और सम्मान से जोड़ा जाता है।"),
    "chamara_2": ("Traditionally associated with learning, eloquence and recognition.", "परंपरा से इसे विद्या, वाक्पटुता और सम्मान से जोड़ा जाता है।"),
    "mridanga": ("Traditionally associated with a respected position and comforts.", "परंपरा से इसे सम्मानित स्थान और सुख-सुविधाओं से जोड़ा जाता है।"),
    "matru_sneha": ("Traditionally associated with affection between mother and child. Very common.", "परंपरा से इसे माता और संतान के स्नेह से जोड़ा जाता है। यह बहुत सामान्य है।"),
    "satkalatra": ("Traditionally associated with a good-natured spouse. Very common.", "परंपरा से इसे सुशील जीवनसाथी से जोड़ा जाता है। यह बहुत सामान्य है।"),
    "sareera_soukhya": ("Traditionally associated with physical ease and vitality. Common.", "परंपरा से इसे शारीरिक सुख और स्फूर्ति से जोड़ा जाता है। यह सामान्य है।"),
    "buddhimaturya": ("Traditionally associated with sharp intelligence.", "परंपरा से इसे तीक्ष्ण बुद्धि से जोड़ा जाता है।"),
    "guru_chandal": ("Jupiter with Rahu. Traditionally a caution about advice and ethics; many astrologers give it little weight. It is not a prediction.",
                     "राहु के साथ गुरु। परंपरा से यह सलाह और नैतिकता के प्रति सावधानी का संकेत है; कई ज्योतिषी इसे कम महत्व देते हैं। यह भविष्यवाणी नहीं है।"),
    "shakata": ("Moon in the 6th or 8th from Jupiter. Traditionally read as ups and downs that settle with effort; it is often cancelled.",
                "गुरु से छठे या आठवें भाव में चंद्र। परंपरा से इसे उतार-चढ़ाव के रूप में पढ़ा जाता है जो प्रयास से स्थिर होते हैं; यह अक्सर भंग होता है।"),
    "subha_kartari": ("Benefics on both sides of the lagna. Traditionally associated with protection and support.",
                      "लग्न के दोनों ओर शुभ ग्रह। परंपरा से इसे सुरक्षा और सहारे से जोड़ा जाता है।"),
    "papa_kartari": ("Malefics on both sides of the lagna. Traditionally read as pressure that asks for patience; benefic aspects soften it.",
                     "लग्न के दोनों ओर पाप ग्रह। परंपरा से इसे ऐसे दबाव के रूप में पढ़ा जाता है जो धैर्य माँगता है; शुभ दृष्टि इसे कोमल करती है।"),
    "dharma_karmadhipati": ("The lords of the 9th and 10th joined. Traditionally one of the most valued raja yogas: work aligned with purpose.",
                            "नवमेश और दशमेश का संबंध। परंपरा से यह सबसे मूल्यवान राज योगों में है: उद्देश्य के अनुरूप कर्म।"),
    "maha_parivartana": ("An exchange between the lords of good houses. Traditionally associated with mutual support between those areas of life.",
                         "शुभ भावों के स्वामियों का परिवर्तन। परंपरा से इसे जीवन के उन क्षेत्रों के परस्पर सहयोग से जोड़ा जाता है।"),
    "dhur": ("The texts read this as career needing care. It is a reason for steady effort and good choices, not a fixed outcome.",
             "शास्त्र इसे करियर में सावधानी का संकेत मानते हैं। यह निरंतर प्रयास और अच्छे निर्णयों का कारण है, तय परिणाम नहीं।"),
    "daridra_11": ("The texts read this as gains needing care. It is a reason for careful planning, not a fixed outcome.",
                   "शास्त्र इसे लाभ में सावधानी का संकेत मानते हैं। यह सोच-समझकर योजना बनाने का कारण है, तय परिणाम नहीं।"),
    "sankhya_5": ("Pasha: planets in five signs. Traditionally associated with being busy and well-connected. Very common.",
                  "पाश: ग्रह पाँच राशियों में। परंपरा से इसे व्यस्तता और अच्छे संपर्कों से जोड़ा जाता है। यह बहुत सामान्य है।"),
}

# Hindi names for the yogas the skill's report does not name in Hindi yet.
YOGA_NAME_HI = {
    "Rajju": "रज्जु", "Musala": "मुसल", "Nala": "नल", "Mala (Srik)": "माला (स्रक्)", "Sarpa": "सर्प", "Gada": "गदा",
    "Shakata (Nabhasa)": "शकट (नाभस)", "Vihaga": "विहग", "Shringataka": "शृंगाटक", "Hala": "हल", "Vajra": "वज्र", "Yava": "यव",
    "Kamala": "कमल", "Vapi": "वापी", "Yupa": "यूप", "Ishu (Shara)": "इषु (शर)", "Shakti": "शक्ति", "Danda": "दंड", "Nauka": "नौका",
    "Kuta": "कूट", "Chhatra": "छत्र", "Chapa (Nabhasa)": "चाप (नाभस)", "Ardhachandra": "अर्धचंद्र", "Chakra": "चक्र", "Samudra": "समुद्र",
    "Vallaki (Veena)": "वल्लकी (वीणा)", "Dama": "दाम", "Kedara": "केदार", "Shoola": "शूल", "Yuga": "युग", "Gola": "गोल",
    "Shubha (benefic in Lagna)": "शुभ (लग्न में शुभ ग्रह)", "Ashubha (malefic in Lagna)": "अशुभ (लग्न में पाप ग्रह)",
    "Shubha Kartari (Lagna)": "शुभ कर्तरी (लग्न)", "Papa Kartari (Lagna)": "पाप कर्तरी (लग्न)", "Vasumati": "वसुमती", "Shakata": "शकट",
    "Amala (from the Moon)": "अमला (चंद्र से)", "Guru-Mangala": "गुरु-मंगल", "Parvata": "पर्वत", "Kahala": "काहल",
    "Kahala (second reading)": "काहल (दूसरा पाठ)", "Chamara (second reading)": "चामर (दूसरा पाठ)", "Shankha (second reading)": "शंख (दूसरा पाठ)",
    "Bheri (second reading)": "भेरी (दूसरा पाठ)", "Sreenatha": "श्रीनाथ", "Matsya": "मत्स्य", "Kurma": "कूर्म", "Khadga": "खड्ग",
    "Kusuma": "कुसुम", "Kalanidhi": "कलानिधि", "Lagnadhi": "लग्नाधि", "Hari": "हरि", "Hara": "हर", "Brahma": "ब्रह्म",
    "Brahma (second reading)": "ब्रह्म (दूसरा पाठ)", "Vishnu": "विष्णु", "Shiva": "शिव", "Trilochana": "त्रिलोचन", "Gauri": "गौरी",
    "Chandika": "चंडिका", "Sarada": "शारदा", "Bharathi": "भारती", "Amsavatara": "अंशावतार", "Devendra": "देवेंद्र", "Indra": "इंद्र",
    "Ravi": "रवि", "Bhaskara": "भास्कर", "Kulavardhana": "कुलवर्धन", "Gandharva": "गंधर्व", "Go": "गो", "Vidyut": "विद्युत",
    "Chapa": "चाप", "Pushkala": "पुष्कल", "Makuta": "मकुट", "Jaya": "जय", "Chatussagara": "चतुःसागर", "Rajalakshana": "राजलक्षण",
    "Vanchana Chora Bheeti": "वंचन चोर भीति", "Mahabhagya": "महाभाग्य", "Garuda": "गरुड़", "Dehapushti": "देहपुष्टि",
    "Sada Sanchara": "सदा संचार", "Dharma-Karmadhipati": "धर्म-कर्माधिपति", "Harsha (Viparita Raja)": "हर्ष (विपरीत राज)",
    "Vimala (Viparita Raja)": "विमल (विपरीत राज)", "Viparita Raja (lords in each other's dusthanas)": "विपरीत राज (स्वामी परस्पर दुःस्थान में)",
    "Bahudravyarjana": "बहुद्रव्यार्जन", "Madhya Vayasi Dhana": "मध्य वयसि धन", "Amarananta Dhana": "अमरानंत धन",
    "Ayatnadhanalabha": "अयत्नधनलाभ", "Dhur (career needs care)": "धुर (करियर में सावधानी)", "Daridra (gains need care)": "दरिद्र (लाभ में सावधानी)",
    "Maha Parivartana": "महा परिवर्तन", "Khala Parivartana": "खल परिवर्तन", "Dainya Parivartana": "दैन्य परिवर्तन",
    "Bhratruvriddhi": "भ्रातृवृद्धि", "Parakrama": "पराक्रम", "Uttama Griha": "उत्तम गृह", "Bandhu Pujya": "बंधु पूज्य",
    "Nishkapata (sincerity)": "निष्कपट (सरलता)", "Bhagya": "भाग्य", "Dhatrutwa (generosity)": "दातृत्व (उदारता)",
    "Apakeerti (reputation needs care)": "अपकीर्ति (छवि में सावधानी)", "Sumukha": "सुमुख", "Parihasaka (wit)": "परिहासक (विनोद)",
    "Marud": "मरुद्", "Budha": "बुध", "Bhojana Soukhya": "भोजन सौख्य", "Rahu-Jupiter conjunction (Guru Chandal)": "राहु-गुरु युति (गुरु चांडाल)",
}
ORD_HI = {1: "लग्न", 2: "द्वितीय", 3: "तृतीय", 4: "चतुर्थ", 5: "पंचम", 6: "षष्ठ", 7: "सप्तम", 8: "अष्टम", 9: "नवम", 10: "दशम", 11: "एकादश", 12: "द्वादश"}
LORD_HI = {1: "लग्नेश", 2: "द्वितीयेश", 4: "चतुर्थेश", 5: "पंचमेश", 7: "सप्तमेश", 9: "नवमेश", 10: "दशमेश", 11: "एकादशेश"}
PLANET_HI = {"Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगल", "Mercury": "बुध", "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि"}
MALIKA_HI = {"Lagna": "लग्न", "Dhana": "धन", "Vikrama": "विक्रम", "Sukha": "सुख", "Putra": "पुत्र", "Shatru": "शत्रु", "Kalatra": "कलत्र",
             "Randhra": "रंध्र", "Bhagya": "भाग्य", "Karma": "कर्म", "Labha": "लाभ", "Vyaya": "व्यय"}


def generated_name_hi(name):
    """Hindi for the systematic families: Malika, Raja and Dhana yogas by lords, BVR300 numbers, Neecha Bhanga by planet."""
    import re
    m = re.fullmatch(r"(\w+) Malika", name)
    if m and m.group(1) in MALIKA_HI:
        return MALIKA_HI[m.group(1)] + " मालिका"
    m = re.fullmatch(r"(Raja|Dhana) yoga \((?:Lagna lord|(\d+)\w\w|1st)(?: lord)? and (\d+)\w\w lords?\)", name)
    if m:
        a = 1 if m.group(2) is None else int(m.group(2))
        return f"{'राज' if m.group(1) == 'Raja' else 'धन'} योग ({LORD_HI.get(a, ORD_HI[a])} और {LORD_HI.get(int(m.group(3)), ORD_HI[int(m.group(3))])})"
    m = re.fullmatch(r"(\w[\w ]*?) \(BVR300 no\. (\d+)\)", name)
    if m:
        base = {"Dhana yoga": "धन योग", "Daridra": "दरिद्र", "Ayatna Griha Prapti": "अयत्न गृह प्राप्ति", "Vahana": "वाहन"}.get(m.group(1))
        if base:
            return f"{base} (BVR300 क्र. {m.group(2)})"
    m = re.fullmatch(r"Neecha Bhanga Raja \((\w+)\)", name)
    if m:
        return f"नीचभंग राज योग ({PLANET_HI[m.group(1)]})"
    return None


KOOTAS = {
    "varna": ("Compares the temperament groups of the two Moon signs.", "दोनों चंद्र राशियों के वर्ण (स्वभाव वर्ग) की तुलना।"),
    "vashya": ("Mutual attraction and influence between the two.", "दोनों के बीच परस्पर आकर्षण और प्रभाव।"),
    "tara": ("How the two birth nakshatras sit from each other.", "दोनों जन्म नक्षत्र एक-दूसरे से कैसे स्थित हैं।"),
    "yoni": ("Instinctive nature and closeness, from the animal symbols of the nakshatras.", "नक्षत्रों के पशु प्रतीकों से स्वाभाविक प्रकृति और निकटता।"),
    "graha_maitri": ("Friendship between the lords of the two Moon signs: how well the two minds get along.",
                     "दोनों चंद्र राशियों के स्वामियों की मित्रता: दोनों के मन कितने मेल खाते हैं।"),
    "gana": ("Temperament: Deva, Manushya or Rakshasa nature.", "स्वभाव: देव, मनुष्य या राक्षस गण।"),
    "bhakoot": ("How the two Moon signs sit from each other: welfare and prosperity together.", "दोनों चंद्र राशियाँ एक-दूसरे से कैसे स्थित हैं: साथ में कल्याण और समृद्धि।"),
    "nadi": ("The three nadis; the same nadi is traditionally avoided, with known exceptions.", "तीन नाड़ियाँ; एक ही नाड़ी परंपरा से टाली जाती है, कुछ ज्ञात अपवादों के साथ।"),
}

PORUTHAM = {
    "dina": ("Day-to-day harmony, from the count between the two birth stars.", "दोनों जन्म नक्षत्रों की गिनती से दैनिक तालमेल।"),
    "gana": ("Temperament.", "स्वभाव।"),
    "mahendra": ("Growth of the family.", "परिवार की वृद्धि।"),
    "stree_deergha": ("Wellbeing and prosperity of the couple over time.", "समय के साथ दंपति का कल्याण और समृद्धि।"),
    "yoni": ("Instinctive nature and closeness.", "स्वाभाविक प्रकृति और निकटता।"),
    "rasi": ("How the two Moon signs sit from each other.", "दोनों चंद्र राशियों की परस्पर स्थिति।"),
    "rasi_adhipati": ("Friendship between the lords of the Moon signs.", "चंद्र राशियों के स्वामियों की मित्रता।"),
    "vasya": ("Mutual attraction.", "परस्पर आकर्षण।"),
    "rajju": ("The most weighted Porutham in Tamil practice: different rajjus are wanted. It is never read here as a prediction.",
              "तमिल परंपरा में सबसे महत्वपूर्ण पोरुत्तम: अलग रज्जु वांछित है। यहाँ इसे कभी भविष्यवाणी के रूप में नहीं पढ़ा जाता।"),
    "vedha": ("Nakshatra pairs said to obstruct each other.", "ऐसे नक्षत्र युग्म जो एक-दूसरे में बाधक माने जाते हैं।"),
}

NUMBERS = {
    1: ("Independence, leadership and fresh starts (the Sun).", "स्वतंत्रता, नेतृत्व और नई शुरुआत (सूर्य)।"),
    2: ("Cooperation, sensitivity and partnership (the Moon).", "सहयोग, संवेदनशीलता और साझेदारी (चंद्र)।"),
    3: ("Expression, learning and optimism (Jupiter).", "अभिव्यक्ति, विद्या और आशावाद (गुरु)।"),
    4: ("Structure, hard work and the unconventional (Rahu).", "व्यवस्था, परिश्रम और अपरंपरागत सोच (राहु)।"),
    5: ("Change, travel, communication and trade (Mercury).", "परिवर्तन, यात्रा, संवाद और व्यापार (बुध)।"),
    6: ("Love, family, beauty and responsibility (Venus).", "प्रेम, परिवार, सौंदर्य और ज़िम्मेदारी (शुक्र)।"),
    7: ("Reflection, research and the spiritual (Ketu).", "चिंतन, शोध और आध्यात्मिकता (केतु)।"),
    8: ("Discipline, ambition and patience (Saturn).", "अनुशासन, महत्वाकांक्षा और धैर्य (शनि)।"),
    9: ("Courage, compassion and completion (Mars).", "साहस, करुणा और पूर्णता (मंगल)।"),
    11: ("A master number: intuition and inspiration, with high sensitivity.", "मास्टर अंक: अंतर्ज्ञान और प्रेरणा, गहरी संवेदनशीलता के साथ।"),
    22: ("A master number: the practical builder of large plans.", "मास्टर अंक: बड़ी योजनाओं का व्यावहारिक निर्माता।"),
    33: ("A master number: service and teaching.", "मास्टर अंक: सेवा और शिक्षण।"),
}

NUMBER_TYPES = {
    "mulank": ("From the day of birth: how a person tends to act day to day.", "जन्म तिथि के दिन से: व्यक्ति रोज़मर्रा में कैसे व्यवहार करता है।"),
    "bhagyank": ("From the full date of birth: the direction life tends to take.", "पूरी जन्म तिथि से: जीवन किस दिशा में जाता है।"),
    "name": ("The Chaldean value of the name in use: how the name is said to resonate.", "प्रचलित नाम का कैल्डियन मान: नाम का कंपन कैसा माना जाता है।"),
    "life_path": ("The Pythagorean Life Path from the birth date: the main lesson and path.", "जन्म तिथि से पाइथागोरियन जीवन पथ: मुख्य पाठ और मार्ग।"),
    "destiny": ("From all the letters of the birth name: natural abilities.", "जन्म नाम के सभी अक्षरों से: स्वाभाविक क्षमताएँ।"),
    "personal_year": ("The theme of the current year in a nine-year cycle.", "नौ वर्ष के चक्र में चालू वर्ष का विषय।"),
    "soul": ("From the vowels of the name: inner wishes.", "नाम के स्वरों से: भीतरी इच्छाएँ।"),
    "personality": ("From the consonants of the name: how others first see a person.", "नाम के व्यंजनों से: दूसरे व्यक्ति को पहली बार कैसे देखते हैं।"),
    "maturity": ("Life Path plus Destiny: what comes forward in later life.", "जीवन पथ और भाग्य अंक का योग: बाद के जीवन में क्या उभरता है।"),
}


def main():
    import yoga_rules
    names_hi = {}
    missing = []
    existing = json.load(open(os.path.join(HERE, "..", "app", "src", "main", "assets", "hindi_names.json"), encoding="utf-8"))["yoga"]
    for r in yoga_rules.RULES:
        n = r["name"]
        if n in existing:
            continue
        h = YOGA_NAME_HI.get(n) or generated_name_hi(n)
        if h:
            names_hi[n] = h
        else:
            missing.append(n)
    if missing:
        sys.exit("no Hindi name for: " + ", ".join(missing))
    ids = {r["id"] for r in yoga_rules.RULES}
    unknown = set(YOGAS) - ids
    if unknown:
        sys.exit("meanings for unknown yoga ids: " + ", ".join(sorted(unknown)))
    cats = {r["category"] for r in yoga_rules.RULES}
    if cats - set(YOGA_CATEGORIES):
        sys.exit("categories without a meaning: " + ", ".join(sorted(cats - set(YOGA_CATEGORIES))))
    pair = lambda t: {"en": t[0], "hi": t[1]}  # noqa: E731
    out = {
        "planet": {k: pair(v) for k, v in PLANETS.items()},
        "house": {str(k): pair(v) for k, v in HOUSES.items()},
        "yoga_category": {k: pair(v) for k, v in YOGA_CATEGORIES.items()},
        "yoga": {k: pair(v) for k, v in YOGAS.items()},
        "yoga_name_hi": names_hi,
        "koota": {k: pair(v) for k, v in KOOTAS.items()},
        "porutham": {k: pair(v) for k, v in PORUTHAM.items()},
        "number": {str(k): pair(v) for k, v in NUMBERS.items()},
        "number_type": {k: pair(v) for k, v in NUMBER_TYPES.items()},
    }
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"wrote {OUT}: {len(names_hi)} more Hindi yoga names (all 195 covered), {len(YOGAS)} yoga meanings, "
          f"{len(YOGA_CATEGORIES)} categories, {os.path.getsize(OUT) // 1024} KB")


if __name__ == "__main__":
    main()
