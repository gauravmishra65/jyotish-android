"""hindi_shell.py - Hindi (Devanagari) text for the report shell and for the labels the renderer generates.

Register: professional consultation, आप-form, accepted mixed vocabulary (करियर, साढ़े साती), technical terms in
standard transliteration. Keys in SHELL are the exact raw strings between tags in assets/report_template.html.
"""
import re

SHELL = {
    '2.1&nbsp; Your Birth Charts (Kundli)': '2.1&nbsp; आपकी जन्म कुंडलियाँ',
    'These are your charts drawn in the traditional way. Every chapter that follows reads from them.': 'ये आपकी कुंडलियाँ हैं, पारंपरिक ढंग से बनाई गईं। आगे के सभी अध्याय इन्हीं से पढ़े गए हैं।',
    'This is your birth chart (Janam Kundli). Section 2.1 shows all your charts and explains how to read them.': 'यह आपकी जन्म कुंडली है। खंड 2.1 में आपकी सभी कुंडलियाँ हैं और उन्हें पढ़ने का तरीका बताया गया है।',
    'Planet (Graha)': 'ग्रह',
    'Birth Star (Nakshatra)': 'नक्षत्र (जन्म-तारा)',
    'Quarter (Pada)': 'चरण',
    'Strength / Needed (rupas)': 'बल / आवश्यक (रूप)',
    'Open all detailed calculations': 'सभी विस्तृत गणनाएँ खोलें',
    'Fold all detailed calculations': 'सभी विस्तृत गणनाएँ समेटें',
    'Show the detailed calculation': 'विस्तृत गणना देखें',
    'Hide the detailed calculation': 'विस्तृत गणना छिपाएँ',
    'Skip to your reading': 'सीधे अपनी रिपोर्ट पर जाएँ',
    'Start Here': 'यहाँ से शुरू करें',
    'Start here': 'यहाँ से शुरू करें',
    'Start reading': 'पढ़ना शुरू करें',
    'G · Glossary': 'G · शब्दावली',
    'YOUR READING AT A GLANCE': 'आपकी रिपोर्ट एक नज़र में',
    'Your Key Facts': 'आपके मुख्य तथ्य',
    'The few facts the rest of the report builds on, each with what it means in everyday terms.': 'वे कुछ तथ्य जिन पर पूरी रिपोर्ट टिकी है, हर एक का रोज़मर्रा की भाषा में अर्थ।',
    'Your Strengths': 'आपकी खूबियाँ',
    'Worth Watching': 'ध्यान देने योग्य',
    'The Next Twelve Months': 'अगले बारह महीने',
    'Your Five Years in One View': 'आपके पाँच वर्ष एक नज़र में',
    'Green means a helpful year, red a year that asks for more care, amber a mixed year and grey a quiet one. Section 9 explains every cell.': 'हरा रंग सहायक वर्ष, लाल अधिक सावधानी वाला वर्ष, पीला मिश्रित वर्ष और धूसर शांत वर्ष बताता है। खंड 9 में हर खाने की व्याख्या है।',
    'Three Things to Do': 'करने योग्य तीन बातें',
    'How to Read This Report': 'इस रिपोर्ट को कैसे पढ़ें',
    'In ten minutes:': 'दस मिनट में:',
    'read this page, the Final Summary (section 8) and the Prediction Summary (9.1).': 'यह पृष्ठ, अंतिम सारांश (खंड 8) और भविष्यफल का सार (9.1) पढ़ें।',
    'In half an hour:': 'आधे घंटे में:',
    'also read the box at the top of each section, which says what the section covers and what it found.': 'हर खंड के ऊपर का बॉक्स भी पढ़ें, जो बताता है कि खंड में क्या है और उसमें क्या निकला।',
    'The full reading:': 'पूरी रिपोर्ट:',
    'read every section. Technical tables are folded away; open them only if you want to see the working.': 'हर खंड पढ़ें। तकनीकी तालिकाएँ समेटी हुई हैं; गणना देखनी हो तभी उन्हें खोलें।',
    'New words:': 'नए शब्द:',
    'every astrology term is explained in plain language in the Glossary (section G). You never need the Calculation Audit (section A) to use this report.': 'ज्योतिष के हर शब्द का सरल अर्थ शब्दावली (खंड G) में दिया गया है। इस रिपोर्ट के उपयोग के लिए गणना-परीक्षण (खंड A) पढ़ना ज़रूरी नहीं है।',
    'In short': 'संक्षेप में',
    'Every calculation in this report starts from these birth details. If any of them is wrong, please say so before reading further, because a different time or place can change the results.': 'इस रिपोर्ट की हर गणना इन्हीं जन्म-विवरणों से शुरू होती है। इनमें कुछ भी गलत हो तो आगे पढ़ने से पहले बताएँ, क्योंकि अलग समय या स्थान से परिणाम बदल सकते हैं।',
    "Vedic astrology (Jyotish) is India's traditional system. It uses the stars' actual positions in the sky and is especially strong at timing: it divides life into planetary periods called dashas and reads what each one brings.": 'वैदिक ज्योतिष भारत की पारंपरिक पद्धति है। यह आकाश में तारों की वास्तविक स्थिति लेता है और समय बताने में विशेष रूप से सक्षम है: यह जीवन को दशा नामक ग्रह-कालों में बाँटकर बताता है कि हर काल क्या लाता है।',
    'Western astrology uses the season-based zodiac behind the familiar "star signs". It is strongest at describing personality and at showing how the planets\' current movements are likely to feel.': 'पश्चिमी ज्योतिष ऋतुओं पर आधारित राशिचक्र लेता है, जिससे जानी-पहचानी "स्टार साइन" बनती हैं। यह व्यक्तित्व के वर्णन में और यह बताने में सबसे सक्षम है कि ग्रहों की वर्तमान चाल कैसी महसूस होगी।',
    'BaZi, the Four Pillars of Destiny, is a Chinese system. It turns the year, month, day and hour of birth into eight characters made of five elements: wood, fire, earth, metal and water. The balance between them shows natural strengths and what you need more of.': 'बाज़ी, यानी भाग्य के चार स्तंभ, चीनी पद्धति है। यह जन्म के वर्ष, मास, दिन और घंटे को पाँच तत्वों (काष्ठ, अग्नि, पृथ्वी, धातु और जल) से बने आठ अक्षरों में बदलती है। उनका संतुलन स्वाभाविक खूबियाँ और आपकी ज़रूरतें बताता है।',
    'Numerology turns your birth date and name into a few key numbers, each with a traditional meaning. Three schools are used and read separately.': 'अंक ज्योतिष आपकी जन्म-तिथि और नाम को कुछ मुख्य अंकों में बदलता है, हर अंक का पारंपरिक अर्थ है। तीन पद्धतियाँ ली गई हैं और अलग-अलग पढ़ी गई हैं।',
    'Each tradition was calculated on its own. This section sets them side by side. Where they agree, the reading is most confident; where they differ, it says which signal to trust.': 'हर पद्धति की गणना अलग से की गई। यह खंड उन्हें साथ रखता है। जहाँ वे सहमत हैं, वहाँ रिपोर्ट सबसे अधिक आश्वस्त है; जहाँ वे अलग हैं, वहाँ बताया गया है कि किस संकेत पर भरोसा करें।',
    'Doshas are difficult patterns in a Vedic chart. Each one found here is rated from none to severe, and traditional remedies are suggested. Remedies are optional and never replace practical action or professional advice.': 'दोष वैदिक कुंडली की कठिन स्थितियाँ हैं। यहाँ मिले हर दोष को "नहीं" से "गंभीर" तक आँका गया है और पारंपरिक उपाय सुझाए गए हैं। उपाय वैकल्पिक हैं और व्यावहारिक कदम या विशेषज्ञ सलाह की जगह नहीं लेते।',
    'The whole reading brought together in plain words: what matters most, and what to do about it.': 'पूरी रिपोर्ट सरल शब्दों में एक साथ: सबसे ज़रूरी क्या है, और उसके लिए क्या करें।',
    'What the next five years look like for each part of life, worked out from all four traditions together. Start with the Prediction Summary (9.1); the rest of the section shows how each conclusion was reached.': 'अगले पाँच वर्ष जीवन के हर क्षेत्र के लिए कैसे दिखते हैं, चारों पद्धतियों को मिलाकर निकाला गया। भविष्यफल के सार (9.1) से शुरू करें; बाकी खंड बताता है कि हर निष्कर्ष तक कैसे पहुँचे।',
    'Lal Kitab ("the red book") is a twentieth-century astrology book from Punjab, written in Urdu. It reads the chart in its own way and is known for simple household remedies called upay.': 'लाल किताब बीसवीं सदी की पंजाब की ज्योतिष पुस्तक है, जो उर्दू में लिखी गई। यह कुंडली को अपने ढंग से पढ़ती है और सरल घरेलू उपायों के लिए जानी जाती है।',
    'Every specialist word used in this report, in plain language. Terms that belong only to the five-year forecast are explained in 9.7.': 'इस रिपोर्ट में आए हर विशेष शब्द का सरल अर्थ। केवल पंचवर्षीय भविष्यफल से जुड़े शब्द 9.7 में समझाए गए हैं।',
    'GLOSSARY: THE WORDS IN THIS REPORT': 'शब्दावली: इस रिपोर्ट के शब्द',
    'Word': 'शब्द',
    'For the curious, or for another astrologer: the exact methods, checks and limits behind every number in this report. You do not need this section to use the reading.': 'जिज्ञासु पाठकों या किसी अन्य ज्योतिषी के लिए: इस रिपोर्ट के हर अंक के पीछे की सटीक पद्धतियाँ, जाँचें और सीमाएँ। रिपोर्ट के उपयोग के लिए यह खंड ज़रूरी नहीं है।',
    "What a Birth-Time Error Can Change": "जन्म-समय की त्रुटि क्या बदल सकती है", "Range": "सीमा", "Effect": "प्रभाव",
    "A.4&nbsp; Past-Event Check": "A.4&nbsp; पिछली घटनाओं की जाँच", "A.5&nbsp; What Was Not Computed": "A.5&nbsp; जिनकी गणना नहीं हुई",
    "Rule Layers on That Date": "उस दिन के नियम-स्तर", "Hits / Chance": "मेल / संयोग",
    "Each layer is checked on the client's own dated event and compared with how often it is true across their adult life. p is the chance of at least these hits if the rules were unrelated to the events: the smaller, the better the chart's rules fit this life.":
        "हर स्तर को जातक की अपनी तिथि वाली घटना पर जाँचा गया है और इसकी तुलना की गई है कि वह उनके वयस्क जीवन में कितनी बार सच रहता है। p बताता है कि यदि नियमों का घटनाओं से कोई संबंध न होता तो कम से कम इतने मेल संयोग से मिलने की संभावना कितनी है: जितना छोटा, कुंडली के नियम इस जीवन पर उतने ही ठीक बैठते हैं।",
    "9.6&nbsp; Event Timing by Classical Rules": "9.6&nbsp; शास्त्रीय नियमों से घटना-समय", "What It Means": "इसका अर्थ",
    "Matter": "विषय-क्षेत्र", "Windows": "खिड़कियाँ", "How Often True in This Chart": "इस कुंडली में कितनी बार सच", "Grade": "श्रेणी",
    "A window needs a dasha that is eligible for the matter and a confirming Jupiter-Saturn transit; &quot;+ Jaimini&quot; marks a fitting Jaimini sign as well. The base rate is how often each layer is true across this person's adult life: the rarer it is, the more a window means.":
        "खिड़की के लिए उस विषय की योग्य दशा और गुरु-शनि के गोचर की पुष्टि चाहिए; &quot;+ जैमिनी&quot; का अर्थ है कि जैमिनी राशि भी मेल खाती है। आधार दर बताती है कि हर परत इस व्यक्ति के वयस्क जीवन में कितनी बार सच रहती है: जितनी दुर्लभ, खिड़की उतनी अर्थपूर्ण।",
    "Shadbala &mdash; Six-fold Strength": "षड्बल &mdash; छह प्रकार का बल", "Ratio &middot; Rank": "अनुपात &middot; क्रम",
    "Strongest Parts": "सबसे प्रबल अंश", "Ishta / Kashta": "इष्ट / कष्ट",
    "BPHS method as in B.V. Raman's Graha and Bhava Balas. A ratio of 1 or more means the planet meets the classical minimum and can deliver its results.":
        "बी.वी. रमन की 'ग्रह और भाव बल' के अनुसार बृहत् पाराशर पद्धति। अनुपात 1 या अधिक हो तो ग्रह शास्त्रीय न्यूनतम बल पूरा करता है और अपना फल दे सकता है।",
    "Raja Yogas, Functional Nature &amp; Dasha Lords": "राजयोग, कार्यात्मक स्वभाव एवं दशा स्वामी",
    "Item": "विषय", "Link / Nature": "संबंध / स्वभाव", "Level / Navamsa": "स्तर / नवांश",
    "Other Sign Dashas &amp; Special Lagnas": "अन्य राशि दशाएँ और विशेष लग्न", "System": "पद्धति", "Running Now": "अभी चल रही",
    "Next Periods": "आगे की दशाएँ", "What It Shows": "क्या दिखाती है",
    "These follow P.V.R. Narasimha Rao's rules. Narayana shows what happens, Kalachakra how connected one feels to it, Sudasa money and status. They are separate views of one life, not extra votes.":
        "ये पी.वी.आर. नरसिंह राव के नियमों से हैं। नारायण दशा बताती है कि क्या घटता है, कालचक्र कि मन उससे कितना जुड़ता है, सुदशा धन और प्रतिष्ठा। ये एक ही जीवन के अलग-अलग दृष्टिकोण हैं, अतिरिक्त वोट नहीं।",
    "K.N. Rao Chara Dasha": "के.एन. राव चर दशा", "Sign Period": "राशि दशा", "Years": "वर्ष",
    "How the Length Was Counted": "अवधि कैसे गिनी गई",
    "Sign periods follow K.N. Rao: count from the sign to its lord, minus one year; whole years from the birth date. Each period has twelve sub-periods, and the period's own sign comes last.":
        "राशि दशाएँ के.एन. राव की पद्धति से हैं: राशि से उसके स्वामी तक गिनकर एक वर्ष घटाया जाता है; जन्म-तिथि से पूरे वर्ष। हर दशा में बारह अंतर्दशाएँ होती हैं और दशा-राशि की अपनी अंतर्दशा सबसे अंत में आती है।",
    "10 \u00b7 Lal Kitab": "10 \u00b7 लाल किताब",
    "LAL KITAB READING": "लाल किताब विवेचन",
    "10.1&nbsp; Lal Kitab Kundli": "10.1&nbsp; लाल किताब कुंडली",
    "In Lal Kitab the first house is always read as Aries, so the houses below are the whole-sign houses from your lagna, without signs or degrees.":
        "लाल किताब में पहला खाना हमेशा मेष माना जाता है, इसलिए नीचे के खाने आपके लग्न से गिने गए भाव हैं, राशि और अंश के बिना।",
    "Planets": "ग्रह", "Book status": "किताब के अनुसार हालत",
    "10.2&nbsp; Chart Type &amp; Special Conditions": "10.2&nbsp; टेवे की किस्म और खास हालतें",
    "10.3&nbsp; Inherited Debts (Rin)": "10.3&nbsp; पितृ आदि ऋण", "Debt": "ऋण", "Why it shows": "क्यों बनता है",
    "Family remedy (book)": "खानदानी उपाय (किताब)",
    "10.4&nbsp; Planet by Planet": "10.4&nbsp; ग्रहवार फल",
    "10.5&nbsp; Varshphal &mdash; The Coming Years": "10.5&nbsp; वर्षफल &mdash; आने वाले साल",
    "Each row is one year of life, from birthday to birthday. The cells show where the planets move in that year's Lal Kitab chart.":
        "हर पंक्ति उम्र का एक साल है, एक जन्मदिन से अगले तक। खानों में उस साल के लाल किताब वर्षफल में ग्रहों की जगह दिखाई गई है।",
    "10.6&nbsp; Upay &mdash; Remedies as the Book Gives Them": "10.6&nbsp; उपाय &mdash; जैसे किताब में दिए हैं",
    "About these remedies": "इन उपायों के बारे में",
    "9 \u00b7 Forecast": "9 \u00b7 भविष्यफल",
    "FIVE-YEAR FORECAST BY LIFE AREA": "जीवन-क्षेत्रवार पंचवर्षीय भविष्यफल",
    "9.1&nbsp; Prediction Summary": "9.1&nbsp; भविष्यफल का सार",
    "The five years for each life area, in plain words. The strongest year and the year needing care are chosen by how many of the four traditions agree. The working behind every line follows in 9.2 to 9.6, and 9.7 explains each term.":
        "हर जीवन-क्षेत्र के पाँच वर्ष, सरल शब्दों में। सबसे अच्छा वर्ष और सावधानी वाला वर्ष इस आधार पर चुना गया है कि चारों में से कितनी पद्धतियाँ एक ही बात कहती हैं। हर पंक्ति के पीछे की गणना 9.2 से 9.6 में है, और 9.7 में हर शब्द का अर्थ समझाया गया है।",
    "Life Area": "जीवन-क्षेत्र", "Five-Year Outlook": "पाँच वर्ष का रुझान", "Strongest Year": "सबसे अच्छा वर्ष", "Year Needing Care": "सावधानी का वर्ष", "In Plain Words": "सरल शब्दों में",
    "9.2&nbsp; The Five Years at a Glance": "9.2&nbsp; पाँच वर्ष एक नज़र में",
    "Each cell shows how the four systems lean in that 12-month period and how strongly they agree. &#9650; supportive &nbsp;&middot;&nbsp; &#9660; demanding &nbsp;&middot;&nbsp; &#9670; mixed &nbsp;&middot;&nbsp; &#9679; activated (the period is switched on; its tone depends on the rest of the chart).":
        "हर खाना बताता है कि उस 12 महीने की अवधि में चारों पद्धतियों का झुकाव किस ओर है और वे आपस में कितनी सहमत हैं। &#9650; अनुकूल &nbsp;&middot;&nbsp; &#9660; चुनौतीपूर्ण &nbsp;&middot;&nbsp; &#9670; मिश्रित &nbsp;&middot;&nbsp; &#9679; सक्रिय (अवधि जाग्रत है; उसका फल कुंडली के बाकी संकेतों पर निर्भर है)।",
    "How to read this forecast": "इस भविष्यफल को कैसे पढ़ें",
    "Every date here was calculated, not estimated. The leanings are a fixed checklist applied the same way to every chart, and the strongest windows are those where several independent systems agree. They describe climate and timing, not certainties, and they work best alongside your own judgement and professional advice.":
        "यहाँ की हर तिथि गणना से निकली है, अनुमान से नहीं। झुकाव एक निश्चित जाँच-सूची से तय होते हैं जो हर कुंडली पर एक ही तरह लागू होती है, और सबसे मज़बूत अवधियाँ वे हैं जहाँ कई स्वतंत्र पद्धतियाँ एक ही दिशा में संकेत करती हैं। ये समय और वातावरण बताते हैं, निश्चित परिणाम नहीं; इन्हें अपने विवेक और विशेषज्ञ सलाह के साथ पढ़ें।",
    "9.3&nbsp; Life Area by Life Area": "9.3&nbsp; क्षेत्रवार विस्तार",
    "Each life area opens with its strongest year and the year that needs care. In its table every row is one 12-month period: the indicators are grouped by system, &#9650; helps, &#9660; asks for effort, &#9670; is mixed and &#9679; switches the area on. Dates in brackets are when each indicator is active. Every term is explained in 9.7.":
        "हर जीवन-क्षेत्र की शुरुआत उसके सबसे अच्छे वर्ष और सावधानी वाले वर्ष से होती है। उसकी तालिका में हर पंक्ति 12 महीने की एक अवधि है: संकेत पद्धति के अनुसार समूहों में हैं; &#9650; सहायक है, &#9660; मेहनत माँगता है, &#9670; मिश्रित है और &#9679; उस क्षेत्र को सक्रिय करता है। कोष्ठक की तिथियाँ बताती हैं कि हर संकेत कब सक्रिय रहता है। हर शब्द का अर्थ 9.7 में दिया गया है।",
    "9.4&nbsp; Key Dates": "9.4&nbsp; प्रमुख तिथियाँ", "Date": "तिथि", "System": "पद्धति", "Event": "घटना",
    "9.5&nbsp; Best Windows &amp; Careful Windows": "9.5&nbsp; अनुकूल एवं सावधानी की अवधियाँ",
    "9.7&nbsp; Understanding the Calculations": "9.7&nbsp; गणनाओं को समझें",
    "Every term used in this section, in plain words, with how to read it.": "इस खंड में आए हर शब्द का सरल अर्थ, और उसे कैसे पढ़ें।",
    "Term": "शब्द", "How to Read It": "कैसे पढ़ें",
    "1 \u00b7 Birth": "1 \u00b7 जन्म", "2 \u00b7 Vedic": "2 \u00b7 वैदिक", "3 \u00b7 Western": "3 \u00b7 पश्चिमी",
    "4 \u00b7 BaZi": "4 \u00b7 बाज़ी", "5 \u00b7 Numerology": "5 \u00b7 अंक", "6 \u00b7 Comparison": "6 \u00b7 तुलना",
    "7 \u00b7 Remedies": "7 \u00b7 उपाय", "8 \u00b7 Summary": "8 \u00b7 सार", "A \u00b7 Audit": "A \u00b7 जाँच",
    "ASTROLOGICAL &amp; NUMEROLOGICAL": "ज्योतिषीय एवं अंक-ज्योतिषीय",
    "LIFE READING": "जीवन परामर्श",
    "A Multi-System Consultation Report": "बहु-पद्धति परामर्श रिपोर्ट",
    "Vedic Jyotish &nbsp;|&nbsp; Western Astrology &nbsp;|&nbsp; Chinese BaZi &nbsp;|&nbsp; Numerology":
        "वैदिक ज्योतिष &nbsp;&middot;&nbsp; पश्चिमी ज्योतिष &nbsp;&middot;&nbsp; चीनी बाज़ी &nbsp;&middot;&nbsp; अंक ज्योतिष",
    "PREPARED FOR": "किनके लिए तैयार", "PREPARED BY": "द्वारा तैयार", "CONSULTATION DATE": "परामर्श की तिथि",
    "REPORT REFERENCE": "रिपोर्ट संदर्भ",
    "This reading is prepared for personal guidance and reflection.": "यह परामर्श व्यक्तिगत मार्गदर्शन और चिंतन के लिए तैयार किया गया है।",
    "CLIENT &amp; BIRTH DETAILS": "क्लाइंट एवं जन्म विवरण", "Field": "विषय", "Details": "विवरण",
    "Data reliability note": "जन्म-विवरण की विश्वसनीयता",
    "VEDIC ASTROLOGY &mdash; JYOTISH": "वैदिक ज्योतिष &mdash; जन्म कुंडली",
    "2.2&nbsp; Core Placements": "2.2&nbsp; मुख्य स्थितियाँ", "Placement": "स्थिति", "Sign": "राशि", "Notes": "टिप्पणी",
    "2.3&nbsp; Planetary Placements (Navagraha)": "2.3&nbsp; ग्रह स्थिति (नवग्रह)", "Graha": "ग्रह", "House": "भाव",
    "Degree": "अंश",
    "2.4&nbsp; Chart Strength, Yogas &amp; Doshas": "2.4&nbsp; कुंडली का बल, योग एवं दोष",
    "2.5&nbsp; Vimshottari Dasha / Antardasha": "2.5&nbsp; विंशोत्तरी महादशा / अंतर्दशा", "Period": "अवधि",
    "Mahadasha": "महादशा", "Antardasha": "अंतर्दशा", "Duration": "दशा स्तर",
    "What This Phase Activates": "यह अवधि क्या सक्रिय करती है",
    "2.6&nbsp; Divisional Chart Cross-Check": "2.6&nbsp; वर्ग कुंडलियों से मिलान",
    "2.7&nbsp; House-by-House Reading": "2.7&nbsp; भाव-दर-भाव फल", "Signifies": "कारकत्व", "Reading": "फल",
    "2.8&nbsp; Strength Layer &mdash; Ashtakavarga": "2.8&nbsp; बल का आकलन &mdash; अष्टकवर्ग",
    "Sarva Bindus": "सर्व बिंदु", "Transit / Natal Occupants": "गोचर / जन्मकालीन ग्रह",
    "Sarva Ashtakavarga totals 337 across the twelve signs; roughly 28 per sign is average. Signs well above that support what transits through them, signs well below strain it.":
        "सर्वाष्टकवर्ग के कुल बिंदु बारह राशियों में 337 होते हैं; प्रति राशि लगभग 28 का औसत माना जाता है। इससे काफ़ी ऊपर की राशियाँ अपने से गुज़रने वाले गोचर को सहारा देती हैं, और काफ़ी नीचे की राशियाँ उस पर दबाव डालती हैं।",
    "2.9&nbsp; Second Dasha Lens &mdash; Yogini": "2.9&nbsp; दूसरी दशा-दृष्टि &mdash; योगिनी", "Level": "स्तर",
    "Yogini (Planet)": "योगिनी (ग्रह)", "Dates": "तिथियाँ", "Agrees or Differs from Vimshottari": "विंशोत्तरी से मेल या अंतर",
    "2.10&nbsp; Jaimini Layer &mdash; Karakas &amp; Arudhas": "2.10&nbsp; जैमिनी दृष्टि &mdash; कारक एवं आरूढ़",
    "2.11&nbsp; Annual Chart &mdash; Varshaphal": "2.11&nbsp; वार्षिक कुंडली &mdash; वर्षफल",
    "2.12&nbsp; Ashtakoota Matching (Two-Person Readings Only)": "2.12&nbsp; अष्टकूट मिलान (केवल दो व्यक्तियों के परामर्श में)",
    "Koota": "कूट", "Max": "अधिकतम", "Score": "प्राप्तांक",
    "South Indian Ten Porutham": "दक्षिण भारतीय दस पोरुथम", "Porutham": "पोरुथम", "Agrees?": "मेल है?", "Rule used": "प्रयुक्त नियम",
    "2.13&nbsp; KP Sub-Lord Layer (Krishnamurti Paddhati)": "2.13&nbsp; केपी उप-स्वामी विश्लेषण (कृष्णमूर्ति पद्धति)",
    "WESTERN ASTROLOGY &mdash; TROPICAL": "पश्चिमी ज्योतिष &mdash; सायन",
    "3.1&nbsp; Sun &middot; Moon &middot; Rising": "3.1&nbsp; सूर्य &middot; चंद्र &middot; लग्न", "Point": "बिंदु", "Meaning": "अर्थ",
    "3.2&nbsp; Major Aspects": "3.2&nbsp; प्रमुख दृष्टि-योग", "Planet A": "ग्रह क", "Aspect": "दृष्टि", "Planet B": "ग्रह ख",
    "Orb": "ऑर्ब (अंश-अंतर)", "Interpretation": "व्याख्या",
    "3.3&nbsp; Elemental &amp; Modality Balance": "3.3&nbsp; तत्त्व एवं गुण-संतुलन", "Element": "तत्त्व", "Count": "संख्या",
    "3.4&nbsp; Current Transits": "3.4&nbsp; वर्तमान गोचर", "Transit": "गोचर", "Natal Contact": "जन्मकालीन संपर्क",
    "Window": "अवधि", "Significance": "महत्त्व",
    "3.5&nbsp; Synastry (Two-Person Readings Only)": "3.5&nbsp; सिनैस्ट्री &mdash; परस्पर संबंध-विश्लेषण (केवल दो व्यक्तियों के परामर्श में)",
    "3.6&nbsp; Hellenistic Time-Lords": "3.6&nbsp; हेलेनिस्टिक काल-स्वामी",
    "3.7&nbsp; Solar Return, Progressions &amp; Solar Arc": "3.7&nbsp; सोलर रिटर्न, प्रोग्रेशन एवं सोलर आर्क",
    "CHINESE FOUR PILLARS &mdash; BAZI": "चीनी चार स्तंभ &mdash; बाज़ी",
    "4.1&nbsp; The Four Pillars": "4.1&nbsp; चार स्तंभ", "Pillar": "स्तंभ", "Heavenly Stem": "स्वर्गीय स्तंभ (\u5929\u5e72)",
    "Earthly Branch": "पार्थिव शाखा (\u5730\u652f)",
    "4.2&nbsp; Day Master &amp; Structural Strength": "4.2&nbsp; डे मास्टर एवं संरचनात्मक बल",
    "4.3&nbsp; Five Element Balance": "4.3&nbsp; पंचतत्त्व संतुलन", "Count Across 8 Characters": "आठों अक्षरों में संख्या",
    "Excess / Missing Implication": "अधिकता / कमी का प्रभाव",
    "4.4&nbsp; Ten Gods (&#21313;&#31070;) Analysis": "4.4&nbsp; दस देवता (&#21313;&#31070;) विश्लेषण",
    "4.5&nbsp; Luck Pillar &amp; Annual Pillar": "4.5&nbsp; भाग्य स्तंभ एवं वार्षिक स्तंभ", "Cycle": "चक्र",
    "Stem / Branch": "स्तंभ / शाखा", "Years": "वर्ष", "What It Supports or Strains": "क्या सहारा देता है, क्या कठिन बनाता है",
    "4.6&nbsp; BaZi Compatibility (Two-Person Readings Only)": "4.6&nbsp; बाज़ी अनुकूलता (केवल दो व्यक्तियों के परामर्श में)",
    "4.7&nbsp; Branch Interactions &amp; Special Stars": "4.7&nbsp; शाखाओं के पारस्परिक संबंध एवं विशेष तारे",
    "4.8&nbsp; Zi Wei Dou Shu (&#32043;&#24494;&#26007;&#25976;)": "4.8&nbsp; ज़ी वेई डू शू (&#32043;&#24494;&#26007;&#25976;)",
    "NUMEROLOGY": "अंक ज्योतिष", "5.1&nbsp; Core Numbers": "5.1&nbsp; मुख्य अंक", "Number": "अंक", "Value": "मान",
    "Core Meaning": "मूल अर्थ", "5.2&nbsp; Loshu Grid": "5.2&nbsp; लोशू ग्रिड",
    "5.3&nbsp; Three Systems, Read Separately": "5.3&nbsp; तीन पद्धतियाँ, अलग-अलग पढ़ी गईं", "System": "पद्धति",
    "Number(s)": "अंक", "What It Says": "क्या कहती है",
    "Pythagorean, Chaldean and Indian numerology use different letter values and reduction rules, so they are not expected to agree. Where they diverge, the reading names which one it leans on and why.":
        "पाइथागोरियन, कैल्डियन और भारतीय अंक-पद्धतियाँ अक्षरों के अलग मान और जोड़ने के अलग नियम अपनाती हैं, इसलिए उनसे एक जैसे उत्तर की अपेक्षा नहीं की जाती। जहाँ वे अलग हों, वहाँ परामर्श बताता है कि किस पर भरोसा किया गया और क्यों।",
    "CROSS-SYSTEM COMPARISON": "पद्धतियों की तुलना",
    "6.1&nbsp; Convergence Map": "6.1&nbsp; समन्वय-मानचित्र", "Vedic": "वैदिक", "Western": "पश्चिमी", "BaZi": "बाज़ी",
    "Numerology": "अंक ज्योतिष", "Weight": "वज़न", "6.2&nbsp; Reading the Pattern": "6.2&nbsp; पैटर्न की व्याख्या",
    "DOSHA IDENTIFICATION &amp; REMEDIES &mdash; DOSH NIVARAN": "दोष पहचान एवं उपाय &mdash; दोष निवारण",
    "Dosha / Affliction": "दोष / पीड़ा", "Severity": "तीव्रता", "Summary": "सार",
    "Traditional Remedy Set": "पारंपरिक उपाय", "Timed, Practical Remedies": "समयानुसार व्यावहारिक उपाय",
    "Honesty note": "ईमानदार टिप्पणी",
    "Remedies can support steadiness, focus and intent. They cannot guarantee outcomes, and they are no substitute for practical action or professional advice.":
        "उपाय स्थिरता, एकाग्रता और संकल्प में सहारा दे सकते हैं। वे परिणाम की गारंटी नहीं देते, और व्यावहारिक प्रयास या पेशेवर सलाह का विकल्प भी नहीं हैं।",
    "FINAL SUMMARY": "अंतिम सार", "In summary": "संक्षेप में",
    "CALCULATION AUDIT &amp; METHOD NOTES": "गणना की जाँच एवं पद्धति संबंधी टिप्पणियाँ",
    "A.1&nbsp; Conventions Used": "A.1&nbsp; अपनाई गई मान्यताएँ", "Convention": "मान्यता", "Choice Made": "चुना गया विकल्प",
    "Why It Matters": "इसका महत्त्व",
    "A.2&nbsp; Sensitivity to Birth Time &amp; Method": "A.2&nbsp; जन्म-समय एवं पद्धति के प्रति संवेदनशीलता",
    "A.3&nbsp; Independent Checks Run": "A.3&nbsp; की गई स्वतंत्र जाँचें", "Check": "जाँच", "Result": "परिणाम",
    "What \"accurate\" means here": "यहाँ \"सटीक\" का अर्थ",
    "Positions, dashas, pillars and numbers in this report were calculated by software and cross-checked, and every convention is stated above so another astrologer can reproduce them. Interpretation is a different matter: it is judgement informed by tradition, not a measurement, and no honest practitioner can promise outcomes.":
        "इस रिपोर्ट की स्थितियाँ, दशाएँ, स्तंभ और अंक सॉफ़्टवेयर से निकाले गए और आपस में जाँचे गए हैं, और हर मान्यता ऊपर लिखी है ताकि कोई दूसरा ज्योतिषी भी इन्हें दोहरा सके। व्याख्या अलग बात है: वह परंपरा से सधा हुआ विवेक है, कोई माप नहीं, और कोई ईमानदार ज्योतिषी परिणामों का वादा नहीं कर सकता।",
    "Disclaimer: This reading is offered for guidance, reflection and entertainment purposes and draws on traditional astrological and numerological systems. It is not a substitute for professional medical, legal, financial or psychological advice. Gemstone and remedial recommendations should be confirmed with a qualified practitioner before use.":
        "अस्वीकरण: यह परामर्श मार्गदर्शन, चिंतन और मनोरंजन के उद्देश्य से है और पारंपरिक ज्योतिषीय एवं अंक-ज्योतिषीय पद्धतियों पर आधारित है। यह चिकित्सा, कानूनी, वित्तीय या मनोवैज्ञानिक सलाह का विकल्प नहीं है। रत्न और उपाय संबंधी सुझाव धारण करने से पहले किसी योग्य विशेषज्ञ से पुष्टि करा लें।",
}

PLANET = {"Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगल", "Mercury": "बुध", "Jupiter": "गुरु", "Venus": "शुक्र",
          "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु", "Lagna": "लग्न", "Ascendant": "लग्न",
          "Midheaven": "मध्य-आकाश", "Uranus": "यूरेनस", "Neptune": "नेपच्यून", "Pluto": "प्लूटो", "North Node": "नॉर्थ नोड", "South Node": "साउथ नोड"}
SIGN = {"Aries": "मेष", "Taurus": "वृषभ", "Gemini": "मिथुन", "Cancer": "कर्क", "Leo": "सिंह", "Virgo": "कन्या",
        "Libra": "तुला", "Scorpio": "वृश्चिक", "Sagittarius": "धनु", "Capricorn": "मकर", "Aquarius": "कुंभ", "Pisces": "मीन"}
NAK = {"Ashwini": "अश्विनी", "Bharani": "भरणी", "Krittika": "कृत्तिका", "Rohini": "रोहिणी", "Mrigashira": "मृगशिरा",
       "Ardra": "आर्द्रा", "Punarvasu": "पुनर्वसु", "Pushya": "पुष्य", "Ashlesha": "आश्लेषा", "Magha": "मघा",
       "Purva Phalguni": "पूर्वा फाल्गुनी", "Uttara Phalguni": "उत्तरा फाल्गुनी", "Hasta": "हस्त", "Chitra": "चित्रा",
       "Swati": "स्वाति", "Vishakha": "विशाखा", "Anuradha": "अनुराधा", "Jyeshtha": "ज्येष्ठा", "Mula": "मूल",
       "Purva Ashadha": "पूर्वाषाढ़ा", "Uttara Ashadha": "उत्तराषाढ़ा", "Shravana": "श्रवण", "Dhanishta": "धनिष्ठा",
       "Shatabhisha": "शतभिषा", "Purva Bhadrapada": "पूर्वा भाद्रपद", "Uttara Bhadrapada": "उत्तरा भाद्रपद", "Revati": "रेवती"}
YOGINI = {"Mangala": "मंगला", "Pingala": "पिंगला", "Dhanya": "धान्या", "Bhramari": "भ्रामरी", "Bhadrika": "भद्रिका",
          "Ulka": "उल्का", "Siddha": "सिद्धा", "Sankata": "संकटा"}
SARPA = {"Anant": "अनंत", "Kulik": "कुलिक", "Vasuki": "वासुकि", "Shankhpal": "शंखपाल", "Padma": "पद्म", "Mahapadma": "महापद्म",
         "Takshak": "तक्षक", "Karkotak": "कर्कोटक", "Shankhachud": "शंखचूड़", "Ghatak": "घातक", "Vishdhar": "विषधर",
         "Sheshnag": "शेषनाग"}
BAZI = {"Wood": "काष्ठ", "Fire": "अग्नि", "Earth": "पृथ्वी", "Metal": "धातु", "Water": "जल", "Air": "वायु",
        "Yang": "यांग", "Yin": "यिन", "Cardinal": "चर", "Fixed": "स्थिर", "Mutable": "द्विस्वभाव",
        "Rat": "चूहा", "Ox": "बैल", "Tiger": "बाघ", "Rabbit": "खरगोश", "Dragon": "ड्रैगन", "Snake": "साँप",
        "Horse": "घोड़ा", "Goat": "बकरी", "Monkey": "बंदर", "Rooster": "मुर्गा", "Dog": "कुत्ता", "Pig": "सूअर"}
ASPECT = {"conjunction": "युति", "opposition": "प्रतियोग", "trine": "त्रिकोण", "square": "चतुष्कोण",
          "sextile": "सेक्स्टाइल", "quincunx": "क्विंकंक्स"}
TAGS = {"exalted": "उच्च", "debilitated": "नीच", "moolatrikona": "मूलत्रिकोण", "own sign": "स्वराशि",
        "friend's sign": "मित्र राशि", "enemy's sign": "शत्रु राशि", "neutral sign": "सम राशि",
        "retrograde": "वक्री", "combust": "अस्त", "vargottama": "वर्गोत्तम"}
LABELS = {
    "Name": "नाम", "Date &amp; time of birth (local)": "जन्म की तिथि एवं समय (स्थानीय)", "Place": "स्थान",
    "Time zone applied": "लागू समय-क्षेत्र", "True solar time": "वास्तविक सौर समय",
    "Birth-time reliability": "जन्म-समय की विश्वसनीयता", "Reading prepared for": "परामर्श की तैयारी की तिथि",
    "certificate": "प्रमाणित", "reliable": "विश्वसनीय", "approximate": "अनुमानित", "unknown": "अज्ञात",
    "Lagna (Ascendant)": "लग्न", "Moon (Rashi)": "चंद्र (राशि)", "Now": "अभी", "current": "वर्तमान",
    "antardasha": "अंतर्दशा", "mahadasha": "महादशा", "pratyantar": "प्रत्यंतर", "Pratyantar": "प्रत्यंतर",
    "Mahadasha": "महादशा", "Antardasha": "अंतर्दशा", "natal:": "जन्मकालीन:", "transit:": "गोचर:",
    "exact:": "सटीक:", "orb": "ऑर्ब", "applying": "निकट आ रहा", "separating": "दूर जा रहा",
    "visible": "दृश्य", "incl. hidden stems": "छिपे स्तंभ सहित", "hidden:": "छिपे:",
    "current luck pillar": "वर्तमान भाग्य स्तंभ", "luck pillar": "भाग्य स्तंभ", "annual": "वार्षिक",
    "Year": "वर्ष", "Month": "मास", "Day (Day Master)": "दिन (डे मास्टर)", "Hour": "समय",
    "Life Path": "जीवन पथ अंक", "Destiny / Expression": "भाग्य / अभिव्यक्ति अंक", "Soul Urge": "आत्म-इच्छा अंक",
    "Personality": "व्यक्तित्व अंक", "karmic debt": "कार्मिक ऋण", "life path": "जीवन पथ", "destiny": "भाग्य", "soul urge": "आत्म-इच्छा", "personality": "व्यक्तित्व", "birthday": "जन्मदिन", "Birthday Number": "जन्मदिन अंक", "Personal Year": "व्यक्तिगत वर्ष",
    "Mulank / Bhagyank": "मूलांक / भाग्यांक", "Pythagorean": "पाइथागोरियन", "Chaldean": "कैल्डियन",
    "Indian (Mulank / Bhagyank / Loshu)": "भारतीय (मूलांक / भाग्यांक / लोशू)", "Destiny": "भाग्य",
    "missing": "अनुपस्थित", "none": "कोई नहीं", "not scored": "अंक नहीं दिए",
    "Varna": "वर्ण", "Vashya": "वश्य", "Tara": "तारा", "Yoni": "योनि", "Graha Maitri": "ग्रह मैत्री", "Gana": "गण",
    "Bhakoot": "भकूट", "Nadi": "नाड़ी",
    "Rajju": "रज्जु", "Vedha": "वेध", "Mahendra": "माहेंद्र", "Stree-deergha": "स्त्री दीर्घ", "Nadi exception": "नाड़ी अपवाद",
    "Graha melapak": "ग्रह मेलापक", "Bhava melapak": "भाव मेलापक", "different": "भिन्न", "present": "उपस्थित", "absent": "अनुपस्थित",
    "Mangal (Kuja) Dosha": "मंगल (कुज) दोष", "Kaal Sarp": "काल सर्प", "Shani Sade Sati": "शनि साढ़े साती",
    "Guru Chandal": "गुरु चांडाल", "Shani-Rahu (Shrapit)": "शनि-राहु (श्रापित)",
    "Pitra Dosha indicators": "पितृ दोष के संकेत", "Gandanta / Gandmool (Moon)": "गंडांत / गंडमूल (चंद्र)",
    "Not running now": "अभी नहीं चल रही", "12th from Moon (rising phase)": "चंद्र से 12वें (आरंभिक चरण)",
    "over natal Moon (peak phase)": "जन्म चंद्र के ऊपर (मध्य चरण)", "2nd from Moon (setting phase)": "चंद्र से दूसरे (अंतिम चरण)",
    "Partial only.": "केवल आंशिक।", "Not formed.": "नहीं बना।",
    "empty": "रिक्त", "A: ": "क: ", "B: ": "ख: ", "natal": "जन्मकालीन", "Rising": "लग्न (उदय राशि)",
}
HOUSE_SIGNIFIES_HI = ["स्वयं, शरीर, जीवन-शक्ति", "धन, वाणी, परिवार", "साहस, भाई-बहन, पराक्रम", "गृह, माता, मन की शांति",
                      "बुद्धि, संतान, पूर्व-पुण्य", "ऋण, रोग, सेवा", "विवाह, साझेदारी", "परिवर्तन, आयु",
                      "भाग्य, धर्म, पिता", "कर्म, करियर, प्रतिष्ठा", "लाभ, मित्र-मंडली", "व्यय, मोक्ष, विदेश"]
TITLE_HI = "ज्योतिषीय एवं अंक-ज्योतिषीय जीवन परामर्श"

PATTERNS = [
    (r"Mars in house (\d+) from Lagna, (\d+) from Moon, (\d+) from Venus\.", r"मंगल लग्न से \1वें, चंद्र से \2वें और शुक्र से \3वें भाव में है।"),
    (r"Complete pattern: (\w+)\.", lambda m: "पूर्ण योग: " + SARPA.get(m.group(1), m.group(1)) + "।"),
    (r"Saturn in (\w+), house (\d+) from the Moon\.", r"शनि \1 में, चंद्र से \2वें भाव में है।"),
    (r"(\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})", r"\1 से \2"),
    (r"\bage (\d+)(&ndash;|-)(\d+)", r"आयु \1\2\3"),
    (r"\bpada (\d)", r"चरण \1"),
    (r"\(month (\d+)\)", r"(माह \1)"),
    (r"Life Path (\d+), Destiny (\d+)", r"जीवन पथ \1, भाग्य \2"),
    (r"missing ([0-9, ]+)", r"अनुपस्थित अंक: \1"),
    (r"(\d+) visible &middot; ([\d.]+) incl\. hidden stems", r"\1 दृश्य &middot; \2 छिपे स्तंभ सहित"),
    (r"([\d.]+)\u00b0, (applying|separating)", lambda m: m.group(1) + "\u00b0, " + LABELS[m.group(2)]),
]


def _words():
    d = {}
    for src in (PLANET, SIGN, NAK, YOGINI, SARPA, BAZI, ASPECT, TAGS):
        d.update(src)
    for k, v in LABELS.items():
        d[k] = v
    return sorted(d.items(), key=lambda kv: -len(kv[0])), d


_WORDS, _DICT = _words()


def to_hindi(s):
    """Translate engine-generated labels in a fragment of HTML; @@WRITE: ...@@ tokens are left untouched."""
    out = []
    for part in re.split(r"(@@WRITE:.*?@@)", s, flags=re.S):
        if part.startswith("@@WRITE"):
            out.append(part)
            continue
        for pat, rep in PATTERNS:
            part = re.sub(pat, rep, part)
        for en, hi in _WORDS:
            part = re.sub(r"(?<![A-Za-z\u0900-\u097F])" + re.escape(en) + r"(?![A-Za-z])", hi, part)
        out.append(part)
    return "".join(out)


AUDIT_WARN = [
    (r"Forecast: Birth time is (unknown|approximate):.*", lambda m: "भविष्यफल: जन्म-समय " + ("अज्ञात" if m.group(1) == "unknown" else "अनुमानित")
     + " है, इसलिए लग्न से गिने जाने वाले सभी संकेत (लग्न से भाव, लग्न से दोहरा गोचर, वर्ष-लग्न, मुंथा का भाव, प्रोफ़ेक्शन, सोलर रिटर्न के कोण, भाव-प्रवेश, लॉट से ज़ोडिएकल रिलीज़िंग, ग्रहण का भाव) "
     + ("उपयोग योग्य नहीं हैं" if m.group(1) == "unknown" else "सशर्त हैं") + "। चंद्र-आधारित गोचर, दशाएँ (यदि चंद्र का नक्षत्र सुनिश्चित है), बाज़ी के वर्ष व मास स्तंभ और अंक ज्योतिष इससे प्रभावित नहीं होते।"),
    (r"Lagna sign flips within (\d+) minutes.*", lambda m: f"लग्न राशि रिकॉर्ड किए गए समय के {m.group(1)} मिनट के भीतर बदल जाती है &mdash; उदित लग्न छोटी समय-त्रुटि के प्रति नाज़ुक है।"),
    (r"Navamsa lagna flips within (\d+) minutes.*", lambda m: f"नवांश लग्न {m.group(1)} मिनट के भीतर बदल जाता है &mdash; नवांश लग्न और कारकांश पर आधारित कथनों को सावधानी से लें।"),
    (r"Moon is within ~2 hours of a nakshatra boundary.*", lambda m: "चंद्रमा नक्षत्र की सीमा से लगभग 2 घंटे के भीतर है: विंशोत्तरी क्रम सटीक जन्म-समय पर निर्भर है।"),
    (r"(\d+) placement\(s\) change sign/nakshatra/pada under alternative ayanamsas.*", lambda m: f"{m.group(1)} स्थितियाँ वैकल्पिक अयनांश में राशि, नक्षत्र या चरण बदल लेती हैं &mdash; A.2 देखें।"),
    (r"Birth is within 24 hours of a solar-term boundary.*", lambda m: "जन्म सौर-पर्व की सीमा से 24 घंटे के भीतर है; मास (और संभवतः वर्ष) स्तंभ समय और स्थान की त्रुटि के प्रति संवेदनशील है।"),
    (r"Birth is within 15 minutes of a two-hour boundary.*", lambda m: "जन्म दो-घंटे की सीमा से 15 मिनट के भीतर है; समय (घंटा) स्तंभ छोटी समय-त्रुटि के प्रति संवेदनशील है।"),
    (r"Daylight/war-time of (\S+) was in force.*", lambda m: f"उस समय डेलाइट/युद्धकालीन समय (+{m.group(1)} घं:मि:से) लागू था; उसे घटाकर विश्व-समय (UT) निकाला गया है।"),
    (r"Zi Wei Dou Shu is sensitive to the shichen.*", lambda m: "ज़ी वेई डू शू दो-घंटे की सीमा (शिचेन) के प्रति संवेदनशील है; जन्म-घंटे की पुष्टि करें।"),
    (r"Placidus is undefined at this latitude.*", lambda m: "इस अक्षांश पर प्लासिडस भाव-पद्धति परिभाषित नहीं है; पोरफ़िरी का उपयोग किया गया।"),
    (r"BIRTH TIME UNKNOWN:.*", lambda m: "जन्म-समय अज्ञात: दोपहर 12:00 (स्थानीय) केवल स्थान-पूरक के रूप में लिया गया है। लग्न, भाव, भाव चलित, केपी भाव-संधियाँ, वर्ग-लग्न, समय (घंटा) स्तंभ, ज़ी वेई डू शू, वर्ष-लग्न और लग्न पर आधारित हर कथन विश्वसनीय नहीं है और उनकी व्याख्या नहीं की जानी चाहिए। चंद्र-आधारित बातें (नक्षत्र, दशा) तभी उपयोगी हैं जब उस दिन चंद्रमा ने नक्षत्र न बदला हो।"),
    (r"Birth time is approximate: read the lagna-sensitivity window.*", lambda m: "जन्म-समय अनुमानित है: लग्न, वर्ग-कुंडलियों या समय-निर्धारण पर भरोसा करने से पहले लग्न-संवेदनशीलता की अवधि देखें और जन्म-समय शोधन (रेक्टिफ़िकेशन) पर विचार करें।"),
    (r"(Day|Hour) pillar differs between standard time \((\S+)\) and true solar time \((\S+)\).*", lambda m: ("दिन" if m.group(1) == "Day" else "समय (घंटा)") + f" स्तंभ मानक समय ({m.group(2)}) और वास्तविक सौर समय ({m.group(3)}) में अलग है। जातक की परंपरा कौन-सी पद्धति मानती है, इसकी पुष्टि करें।"),
    (r"Born in the 23:00-24:00 late-Zi hour\. Day pillar depends on convention: (\S+) \(23:00 rollover\) vs (\S+) \(midnight rollover\).*", lambda m: f"जन्म 23:00-24:00 के उत्तर-ज़ी घंटे में है। दिन स्तंभ पद्धति पर निर्भर है: {m.group(1)} (23:00 पर दिन बदलना) बनाम {m.group(2)} (मध्यरात्रि पर दिन बदलना)।"),
    (r"Life Path differs by method: component method (\d+), total-digit method (\d+).*", lambda m: f"भाग्यांक (लाइफ़ पाथ) पद्धति के अनुसार बदलता है: घटक-पद्धति से {m.group(1)}, कुल-अंक पद्धति से {m.group(2)}। रिपोर्ट में कौन-सी पद्धति ली गई है, यह स्पष्ट करें।"),
]


def warn_hi(w):
    for pat, fn in AUDIT_WARN:
        m = re.match(pat, w, flags=re.S)
        if m:
            return fn(m)
    return None  # not translated: caller decides


NOT_COMPUTED_HI = {
    "Patyayini dasha, Harsha bala and Tajika yogas beyond Ithasala, Ishrafa, Nakta, Yamaya and Kamboola":
        "पात्यायिनी दशा, हर्ष बल और इत्थशाल, ईसराफ, नक्त, यमया व कंबूल के अलावा अन्य ताजिक योग",
    "Fixed-star parans (stars are matched by ecliptic longitude only); asteroids beyond Ceres, Pallas, Juno and Vesta":
        "स्थिर तारों के पैरान (तारों का मिलान केवल क्रांतिवृत्त देशांतर से); सेरीज़, पैलस, जूनो और वेस्टा के अलावा अन्य क्षुद्रग्रह",
    "Ashtottari and conditional dashas; Shoola and other longevity dashas (excluded by design)": "अष्टोत्तरी व सशर्त दशाएँ; शूल व अन्य आयु-दशाएँ (जान-बूझकर शामिल नहीं)",
    "Varsheshwara selection, Mudda and Patyayini dashas, Tajika yogas": "वर्षेश्वर का चयन, मुद्दा एवं पात्यायिनी दशाएँ, ताजिक योग",
    "Zodiacal releasing beyond Level 2": "ज़ोडिएकल रिलीज़िंग स्तर 2 से आगे",
    "Nobleman and most other Shen Sha": "नोबलमैन और अधिकांश अन्य शेन शा",
    "Special-structure BaZi (\u4ece\u683c/\u5316\u6c14\u683c) and Useful God selection - interpretive":
        "विशेष संरचना वाली बाज़ी (\u4ece\u683c/\u5316\u6c14\u683c) और उपयोगी देवता का चयन &mdash; व्याख्यात्मक निर्णय",
}


AYAN_HI = {"lahiri": "लाहिरी", "true_chitra": "ट्रू चित्रा", "true chitra": "ट्रू चित्रा", "krishnamurti": "कृष्णमूर्ति", "raman": "रमन"}


# ------------------------------------------------- five-year forecast (Section 9)
TEN_GOD_HI = {"Friend (比肩)": "मित्र (比肩)", "Rob Wealth (劫财)": "धन-प्रतिद्वंद्वी (劫财)", "Eating God (食神)": "भोज देव (食神)",
              "Hurting Officer (伤官)": "आहत अधिकारी (伤官)", "Indirect Wealth (偏财)": "अप्रत्यक्ष धन (偏财)",
              "Direct Wealth (正财)": "प्रत्यक्ष धन (正财)", "Seven Killings (七杀)": "सप्त-घातक (七杀)",
              "Direct Officer (正官)": "प्रत्यक्ष अधिकारी (正官)", "Indirect Resource (偏印)": "अप्रत्यक्ष संसाधन (偏印)",
              "Direct Resource (正印)": "प्रत्यक्ष संसाधन (正印)"}
REL_HI = [("six harmony (六合)", "षड्-मेल (六合)"), ("clash (冲)", "टकराव (冲)"), ("harm (害)", "हानि (害)"),
          ("destruction (破)", "विनाश (破)"), ("self-punishment (自刑)", "आत्म-दंड (自刑)"),
          ("uncivil punishment (子卯刑)", "अशिष्ट दंड (子卯刑)"), ("half three-harmony", "अर्ध त्रि-मेल"),
          ("three harmony (三合)", "त्रि-मेल (三合)"), ("three meeting (三会)", "त्रि-संगम (三会)"),
          ("three-branch ungrateful punishment (三刑)", "त्रि-शाखा कृतघ्न दंड (三刑)"),
          ("three-branch bullying punishment (三刑)", "त्रि-शाखा दबंग दंड (三刑)"),
          ("partial ungrateful punishment (two of three)", "आंशिक कृतघ्न दंड (तीन में से दो)"),
          ("partial bullying punishment (two of three)", "आंशिक दबंग दंड (तीन में से दो)"),
          ("stem combination (合)", "स्तंभ-मेल (合)"), ("stem clash (冲)", "स्तंभ-टकराव (冲)")]
PALACE_HI = {"Year": "वर्ष", "Month": "मास", "Day": "दिन", "Hour": "समय"}
SHANI_HI = {"Sade Sati - rising phase": "साढ़े साती &mdash; आरंभिक चरण", "Sade Sati - peak phase": "साढ़े साती &mdash; मध्य चरण",
            "Sade Sati - setting phase": "साढ़े साती &mdash; अंतिम चरण", "Ashtama Shani": "अष्टम शनि",
            "Kantaka Shani (4th)": "कंटक शनि (चौथा)", "Kantaka Shani (7th)": "कंटक शनि (सातवाँ)", "Kantaka Shani (10th)": "कंटक शनि (दसवाँ)"}
ECL_HI = {"Total": "पूर्ण", "Annular": "वलयाकार", "Hybrid": "संकर", "Partial": "आंशिक", "Penumbral": "उपछाया", "Other": "अन्य",
          "solar": "सूर्य", "lunar": "चंद्र"}
BAND_HI = {"strong": "प्रबल", "good": "अच्छा", "moderate": "मध्यम", "weak": "दुर्बल"}
AREA_HI = {"Career and status": "करियर एवं प्रतिष्ठा", "Money and assets": "धन एवं संपत्ति", "Love and marriage": "प्रेम एवं विवाह",
           "Family and home": "परिवार एवं घर", "Children and creativity": "संतान एवं सृजनशीलता",
           "Health and vitality": "स्वास्थ्य एवं जीवन-शक्ति", "Travel and relocation": "यात्रा एवं स्थान-परिवर्तन",
           "Learning and spirituality": "शिक्षा एवं आध्यात्म"}
LEAN_HI = {"supportive": "अनुकूल", "demanding": "चुनौतीपूर्ण", "mixed": "मिश्रित", "quiet": "शांत",
           "strong": "प्रबल", "moderate": "मध्यम", "weak": "दुर्बल"}
FC_LABELS_HI = {"Life Area": "जीवन-क्षेत्र", "Slice": "अवधि", "Vedic": "वैदिक", "Western": "पश्चिमी", "BaZi": "बाज़ी",
                "Numerology": "अंक", "Lean": "झुकाव", "Indicators": "संकेत", "systems": "पद्धतियाँ", "of": "में से", "more": "और",
                "nothing flagged": "कोई विशेष संकेत नहीं", "Date": "तिथि", "System": "पद्धति", "Event": "घटना"}


def _tg(s):
    return TEN_GOD_HI.get(s, s)


def _rel(s):
    for en, hi in REL_HI:
        s = s.replace(en, hi)
    return to_hindi(s)


def _P(x):
    return PLANET.get(x, x)


def _S(x):
    return SIGN.get(x, x)


def _hs(m):
    return ", ".join(m.split(", ")) if m else m


EV_AREA_HI = {'marriage': 'विवाह', 'children': 'संतान', 'career': 'करियर', 'money': 'धन', 'property': 'संपत्ति',
              'abroad': 'विदेश', 'education': 'शिक्षा', 'spiritual': 'आध्यात्मिक मोड़'}
FORECAST_PATTERNS = [
    (r"^Event window \((\w+)\): eligible dasha (.+?) with transit confirmation( and a fitting Jaimini sign)? \(base rate (\d+)%\)$",
     lambda m: f"घटना-खिड़की ({EV_AREA_HI.get(m[1], m[1])}): योग्य दशा "
               + ", ".join("-".join(_P(x) for x in pr.split("-")) for pr in m[2].split(", "))
               + " और गोचर की पुष्टि" + (" तथा उपयुक्त जैमिनी राशि" if m[3] else "") + f" (आधार दर {m[4]}%)"),
    (r"^(\w+) mahadasha: lord (\w+) in H(\d+), owns (.+?) \((?:BAV (\d+), )?SAV (\d+), (\w+)\)$",
     lambda m: f"{_P(m[1])} महादशा: स्वामी भाव {m[3]} में, स्वामित्व {m[4] if m[4] != '-' else '&ndash;'} ("
               + (f"स्व-बिंदु {m[5]}, " if m[5] else "") + f"सर्व बिंदु {m[6]}, {BAND_HI.get(m[7], m[7])})"),
    (r"^(\w+)-(\w+) antardasha: lord (\w+) in H(\d+), owns (.+?) \((?:BAV (\d+), )?SAV (\d+), (\w+)\)$",
     lambda m: f"{_P(m[1])}-{_P(m[2])} अंतर्दशा: स्वामी {_P(m[3])} भाव {m[4]} में, स्वामित्व {m[5] if m[5] != '-' else '&ndash;'} ("
               + (f"स्व-बिंदु {m[6]}, " if m[6] else "") + f"सर्व बिंदु {m[7]}, {BAND_HI.get(m[8], m[8])})"),
    (r"^(\w+) in (\w+) \(H(\d+) from Lagna, H(\d+) from Moon\)(?:, aspecting (.+?))? \((?:own bindus (\d+), )?SAV (\d+)\)$",
     lambda m: f"{_P(m[1])} {_S(m[2])} में (लग्न से भाव {m[3]}, चंद्र से भाव {m[4]})"
               + (", " + " और ".join(re.sub(r"H(\d+) from (Lagna|Moon)", lambda x: ("लग्न" if x[2] == "Lagna" else "चंद्र") + f" से भाव {x[1]}", y)
                                       for y in m[5].split(" and ")) + " पर दृष्टि" if m[5] else "")
               + " (" + (f"स्व-बिंदु {m[6]}, " if m[6] else "") + f"सर्व बिंदु {m[7]})"),
    (r"^Double transit \(Jupiter \+ Saturn\) on H(\d+) from (moon|lagna)$",
     lambda m: f"दोहरा गोचर (गुरु + शनि) {'चंद्र' if m[2] == 'moon' else 'लग्न'} से भाव {m[1]} पर"),
    (r"^Varshaphal age (\d+): Muntha in H(\d+) of the year chart$", lambda m: f"वर्षफल आयु {m[1]}: मुंथा वर्ष-कुंडली के भाव {m[2]} में"),
    (r"^(\w+) (conjunction|opposition|square|trine|sextile) natal (\w+)(?: \((\d+) passes, last (\S+)\))?$",
     lambda m: f"{_P(m[1])} की जन्मकालीन {_P(m[3])} से {ASPECT[m[2]]}" + (f" ({m[4]} बार, अंतिम {m[5]})" if m[4] else "")),
    (r"^(\w+) (conjunction|opposition|square|trine|sextile) natal (\w+) \((.+)\)$",
     lambda m: f"{_P(m[1])} की जन्मकालीन {_P(m[3])} से {ASPECT[m[2]]} ({m[4]})"),
    (r"^Profection to H(\d+) \((\w+)\), year lord (\w+)$", lambda m: f"प्रोफ़ेक्शन भाव {m[1]} ({_S(m[2])}), वर्ष-स्वामी {_P(m[3])}"),
    (r"^ZR from (Spirit|Fortune): L2 (\w+)( - (major|moderate|minor) peak)?( - loosing of the bond)? \(L1 (\w+)\)$",
     lambda m: f"ज़ेडआर ({'स्पिरिट' if m[1] == 'Spirit' else 'फ़ॉर्च्यून'} से): स्तर-2 {_S(m[2])}"
               + (f" &mdash; {({'major': 'प्रमुख', 'moderate': 'मध्यम', 'minor': 'लघु'})[m[4]]} शिखर" if m[3] else "")
               + (" &mdash; बंधन-मुक्ति" if m[5] else "") + f" (स्तर-1 {_S(m[6])})"),
    (r"^(\w+) (solar|lunar) eclipse in H(\d+)(?:, on natal (.+))?$",
     lambda m: f"{ECL_HI.get(m[1], m[1])} {ECL_HI[m[2]]} ग्रहण भाव {m[3]} में" + (f", जन्मकालीन {', '.join(_P(x) for x in m[4].split(', '))} पर" if m[4] else "")),
    (r"^(\S+) year stem is (.+)$", lambda m: f"{m[1]} वर्ष का स्तंभ {_tg(m[2])} है"),
    (r"^(\S+) year: (.+) with (\w+) pillar$", lambda m: f"{m[1]} वर्ष: {PALACE_HI.get(m[3], m[3])} स्तंभ से {_rel(m[2])}"),
    (r"^(\S+) is a Peach Blossom year$", lambda m: f"{m[1]} पीच ब्लॉसम (प्रेम-संकेत) वर्ष है"),
    (r"^(\S+) is a Travelling Horse year$", lambda m: f"{m[1]} ट्रैवलिंग हॉर्स (यात्रा-संकेत) वर्ष है"),
    (r"^Personal Year (\d+) \((\d{4})\)$", lambda m: f"व्यक्तिगत वर्ष {m[1]} ({m[2]})"),
    (r"^(\w+) enters (\w+) \(H(\d+) from Lagna, H(\d+) from Moon\)$",
     lambda m: f"{_P(m[1])} का {_S(m[2])} में प्रवेश (लग्न से भाव {m[3]}, चंद्र से भाव {m[4]})"),
    (r"^Vimshottari (\w+)-(\w+) begins$", lambda m: f"विंशोत्तरी {_P(m[1])}-{_P(m[2])} आरंभ"),
    (r"^Varshaphal age (\d+): Varsha Lagna (\w+), Muntha H(\d+)$", lambda m: f"वर्षफल आयु {m[1]}: वर्ष-लग्न {_S(m[2])}, मुंथा भाव {m[3]}"),
    (r"^(\w+) (solar|lunar) eclipse on natal (.+)$",
     lambda m: f"{ECL_HI.get(m[1], m[1])} {ECL_HI[m[2]]} ग्रहण जन्मकालीन {', '.join(_P(x) for x in m[3].split(', '))} पर"),
    (r"^Luck pillar changes to (\S+) \((.+)\)$", lambda m: f"भाग्य स्तंभ बदलकर {m[1]} ({_tg(m[2])})"),
    (r"^ZR from Spirit: loosing of the bond into (\w+)$", lambda m: f"ज़ेडआर (स्पिरिट से): {_S(m[1])} में बंधन-मुक्ति"),
]


def forecast_hi(text):
    """Translate one engine-generated forecast indicator or key-date line. Unknown lines fall back to to_hindi()."""
    if text in SHANI_HI:
        return SHANI_HI[text]
    for pat, fn in FORECAST_PATTERNS:
        m = re.match(pat, text)
        if m:
            return fn(m)
    return to_hindi(text)
