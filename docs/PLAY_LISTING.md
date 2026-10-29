# Play Store listing and data safety (draft for 1.0)

The app is not published yet. Before it is: choose the Swiss Ephemeris licence (AGPL, which means publishing this
app's source, or Astrodienst's professional licence), and create the upload key.

## Listing (English)

**App name (30 characters, the Play maximum):** Gaurav Jyotish by AuthorGaurav

**Launcher label:** Gaurav Jyotish (long labels are cut off under the icon)

**Store icon:** `docs/store/icon-512.png` (512 x 512, made from the same vector as the launcher icon)

**Short description (80 characters max):** Kundali, matching, muhurta and numerology, worked out on your phone.

**Full description:**

Gaurav Jyotish works out a Vedic birth chart, kundali matching, muhurta and numerology on your phone, with no account
and no internet connection.

- **Kundali.** North or South Indian chart, planets with nakshatra and pada, Vimshottari dashas with the
  current period marked, yogas with how common each one is, and Shadbala strength.
- **Kundali milan.** Ashtakoota Guna Milan out of 36 with each koota explained, the ten Porutham of South Indian
  practice, and the Mangal check from the lagna, Moon and Venus, with the cancellations stated.
- **Muhurta.** Good windows for a wedding, griha pravesh, a new venture and more, checked against tithi,
  nakshatra, yoga, karana, weekday, lagna, Rahu Kaal, and Tarabala and Chandrabala for the people involved.
- **Numerology.** Mulank, Bhagyank, the Chaldean name number, Life Path and the other Pythagorean numbers, the
  Loshu grid and Kua number, and name spelling options that keep the name's sound.
- **English and Hindi**, switchable at any time.

Calculations use the Swiss Ephemeris, with Lahiri ayanamsa and whole-sign houses by default; the ayanamsa and the node type can be changed in Settings. Readings
describe what each factor is traditionally associated with; they are not predictions, and the app never
forecasts death, illness or divorce. Confirm important dates with your family's astrologer or panchang.

**Category:** Lifestyle. **Content rating:** Everyone. **Ads:** none. **In-app purchases:** yes (one-time full version, Play edition).

## Listing (Hindi)

**ऐप का नाम:** गौरव ज्योतिष, AuthorGaurav द्वारा

**संक्षिप्त विवरण:** कुंडली, गुण मिलान, मुहूर्त और अंक ज्योतिष, आपके फ़ोन पर ही।

**पूरा विवरण:**

गौरव ज्योतिष आपके फ़ोन पर ही वैदिक जन्म कुंडली, कुंडली मिलान, मुहूर्त और अंक ज्योतिष की गणना करता है। न खाता
बनाना पड़ता है, न इंटरनेट चाहिए।

- **कुंडली।** उत्तर या दक्षिण भारतीय चार्ट, नक्षत्र और पद के साथ ग्रह, चालू अवधि के साथ विंशोत्तरी दशा, योग
  (हर योग कितना सामान्य है, यह भी), और षड्बल।
- **कुंडली मिलान।** 36 में से अष्टकूट गुण मिलान, हर कूट का अर्थ, दक्षिण भारतीय परंपरा के दस पोरुत्तम, और लग्न,
  चंद्र व शुक्र से मंगल दोष की जाँच, परिहार के साथ।
- **मुहूर्त।** विवाह, गृह प्रवेश, नए काम आदि के लिए शुभ समय: तिथि, नक्षत्र, योग, करण, वार, लग्न, राहु काल,
  और संबंधित लोगों के तारा बल व चंद्र बल की जाँच के साथ।
- **अंक ज्योतिष।** मूलांक, भाग्यांक, कैल्डियन नामांक, जीवन पथ और अन्य पाइथागोरियन अंक, लोशु ग्रिड और कुआ
  अंक, और ऐसे नाम विकल्प जिनसे नाम की ध्वनि न बदले।
- **हिंदी और अंग्रेज़ी**, कभी भी बदलें।

गणना स्विस एफ़ेमेरिस से होती है, सामान्यतः लाहिड़ी अयनांश और पूर्ण राशि भाव के साथ; अयनांश और राहु-केतु का प्रकार सेटिंग्स में बदला जा सकता है। फल यह बताते हैं
कि परंपरा से किस योग या स्थिति को किससे जोड़ा जाता है; ये भविष्यवाणी नहीं हैं, और ऐप कभी मृत्यु, रोग या
तलाक़ की बात नहीं करता। महत्वपूर्ण तिथियाँ अपने पारिवारिक ज्योतिषी या पंचांग से अवश्य मिला लें।

## Editions and selling

| Edition | File | How it opens fully |
|---|---|---|
| Demo | `app-demo-release.apk` (shared directly) | Unlock code for the buyer's email (`tools/licence/`) |
| Full | `app-full-release.apk` (sent to buyers directly) | Already open |
| Play | `app-play-release.aab` (upload to Play) | In-app product `full_unlock`, bought through Google Play |

All three share the application ID `com.gauravmishra.jyotish` and the signing key, so one installs over another and
keeps saved Kundlis. In Play Console: create a one-time in-app product with the ID `full_unlock`, set its price,
and add licence testers to try a purchase before release. The Play listing must say "In-app purchases: yes".

## Data safety form

| Question | Answer | Why |
|---|---|---|
| Does the app collect or share any of the required user data types? | **No** | Birth details, names and places, and the optional registration (name, email, phone), are stored only in the app's private storage on the phone. After registering, the person may choose to open their own email app with their name, email and phone filled in, addressed to the author; they send it themselves, and the app transmits nothing. |
| Is data sent off the device? | No | The app has no INTERNET permission; the engine and the place list are bundled. |
| Is data encrypted in transit? | Not applicable | Nothing is transmitted. |
| Can users request that data be deleted? | Yes, on the device | Deleting a profile removes it and its cached chart; uninstalling removes everything. |
| Backups | Excluded | `allowBackup="false"` and data extraction rules exclude cloud backup and device transfer. |

Permissions requested: none in the demo and full editions. The Play edition adds Google Play Billing (the BILLING permission); Play itself handles payment and keeps the purchase history, which the data-safety form should list as "Purchase history, collected, not shared, required for the purchase". Other third-party SDKs: none (no analytics, crash reporting or ads).

## Before uploading

1. The Play edition is signed with the private upload key when the repository secrets
   `JYOTISH_UPLOAD_KEYSTORE_B64`, `JYOTISH_UPLOAD_KEYSTORE_PASSWORD` and `JYOTISH_UPLOAD_KEY_ALIAS` are set (the CI log
   says "signed with the private upload key"). Without them it falls back to the committed test key. The demo and
   full APKs always use the test key so they install over earlier copies. Raise `versionCode` for every upload.
2. Enrol in Play App Signing.
3. Upload `mapping.txt` from the same build, so crash reports are readable.
4. Screenshots: the CI run's `ci-results` branch has current ones (Home, Kundali, Milan, Muhurta, Numerology in
   English and Hindi).
5. Privacy policy URL: Play requires one even when nothing is collected; the data-safety table above is the
   content it needs.
