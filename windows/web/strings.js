/* Every word the interface says, in both languages.
 *
 * The engine already answers in English and Hindi - every reading, every table cell. It would be an odd
 * app that spoke Hindi about your chart and English about the button you press to see it, so the shell
 * is translated too. The wording is taken from the Android app's strings.xml where the same label exists
 * there, so somebody moving between the phone and the desktop reads the same words.
 *
 * t("key") gives the current language; setLang() changes it.
 */

const STRINGS = {
  // the sidebar
  people_one:      { en: "1 person",                       hi: "1 व्यक्ति" },
  people_many:     { en: "%1 people",                      hi: "%1 व्यक्ति" },
  nobody_yet:      { en: "No birth charts yet. Add one to begin.",
                     hi: "अभी कोई कुंडली नहीं है। शुरू करने के लिए एक जोड़ें।" },
  add_person:      { en: "Add a person",                   hi: "व्यक्ति जोड़ें" },
  language:        { en: "Language",                       hi: "भाषा" },

  // the form
  edit_person:     { en: "Edit %1",                        hi: "%1 में बदलाव" },
  data_note:       { en: "Birth details are stored only on this computer. Nothing is sent anywhere.",
                     hi: "जन्म का विवरण केवल इसी कंप्यूटर पर रहता है। कुछ भी कहीं भेजा नहीं जाता।" },
  name:            { en: "Name",                           hi: "नाम" },
  date_of_birth:   { en: "Date of birth",                  hi: "जन्म तिथि" },
  time_of_birth:   { en: "Time of birth",                  hi: "जन्म समय" },
  birthplace:      { en: "Birthplace",                     hi: "जन्म स्थान" },
  latitude:        { en: "Latitude (north +)",             hi: "अक्षांश (उत्तर +)" },
  longitude:       { en: "Longitude (east +)",             hi: "देशांतर (पूर्व +)" },
  time_zone:       { en: "Time zone",                      hi: "समय क्षेत्र" },
  place_hint:      { en: "Varanasi, or Sitapur UP, or वाराणसी",
                     hi: "वाराणसी, या सीतापुर यूपी, या Varanasi" },
  place_note:      { en: "Choosing a birthplace fills in the coordinates and the time zone. They stay "
                       + "editable for a village the list does not carry.",
                     hi: "जन्म स्थान चुनने पर अक्षांश, देशांतर और समय क्षेत्र अपने आप भर जाते हैं। "
                       + "जो गाँव सूची में न हो, उसके लिए इन्हें बदला जा सकता है।" },
  save_build:      { en: "Save and build the chart",       hi: "सहेजें और कुंडली बनाएँ" },
  save_rebuild:    { en: "Save and rebuild the chart",     hi: "सहेजें और कुंडली फिर से बनाएँ" },

  // deleting
  delete_person:   { en: "Delete this person",             hi: "इस व्यक्ति को हटाएँ" },
  delete_again:    { en: "Click again to delete — this cannot be undone",
                     hi: "हटाने के लिए फिर क्लिक करें — यह वापस नहीं होगा" },
  edit_details:    { en: "Edit details",                   hi: "विवरण बदलें" },
  fix_details:     { en: "Fix these details",              hi: "यह विवरण ठीक करें" },

  // the chart
  building:        { en: "Building the chart…",            hi: "कुंडली बन रही है…" },
  chart:           { en: "Chart",                          hi: "कुंडली" },
  the_chart:       { en: "The chart",                      hi: "कुंडली" },
  lagna:           { en: "Lagna",                          hi: "लग्न" },
  moon_sign:       { en: "Moon sign",                      hi: "चंद्र राशि" },
  nakshatra:       { en: "Nakshatra",                      hi: "नक्षत्र" },
  pada:            { en: "pada %1",                        hi: "पाद %1" },
  sunrise:         { en: "Sunrise",                        hi: "सूर्योदय" },
  tithi:           { en: "Tithi",                          hi: "तिथि" },
  vara:            { en: "Weekday",                        hi: "वार" },
  planets:         { en: "Planets",                        hi: "ग्रह" },
  north_indian:    { en: "North Indian",                   hi: "उत्तर भारतीय" },
  south_indian:    { en: "South Indian",                   hi: "दक्षिण भारतीय" },

  // dashas
  dashas:          { en: "Vimshottari dasha",              hi: "विंशोत्तरी दशा" },
  mahadasha:       { en: "Mahadasha",                      hi: "महादशा" },
  antardasha:      { en: "Antardasha",                     hi: "अंतर्दशा" },
  period:          { en: "%1 · %2 to %3",                  hi: "%1 · %2 से %3 तक" },

  // divisional charts
  vargas:          { en: "Divisional charts",              hi: "वर्ग कुंडलियाँ" },
  varga_use:       { en: "Read for %1.",                   hi: "%1 के लिए पढ़ा जाता है।" },

  // reports saved as files
  reports:         { en: "Reports",                        hi: "रिपोर्ट" },
  report_note:     { en: "Each report is saved as one page you can open, print or send. "
                       + "Nothing leaves this computer.",
                     hi: "हर रिपोर्ट एक पृष्ठ के रूप में सहेजी जाती है, जिसे खोला, छापा या भेजा जा सकता है। "
                       + "कुछ भी इस कंप्यूटर से बाहर नहीं जाता।" },
  report_working:  { en: "Writing the %1 report. This takes a few seconds.",
                     hi: "%1 रिपोर्ट तैयार हो रही है। इसमें कुछ सेकंड लगते हैं।" },
  report_saved:    { en: "Saved as %1",                    hi: "%1 के रूप में सहेजी गई" },
  report_failed:   { en: "The report could not be written: %1",
                     hi: "रिपोर्ट तैयार नहीं हो सकी: %1" },
  open_report:     { en: "Open",                           hi: "खोलें" },
  open_folder:     { en: "Open the folder",                hi: "फ़ोल्डर खोलें" },

  // Kundli Milan
  milan:           { en: "Kundali Milan",                  hi: "कुंडली मिलान" },
  milan_sub:       { en: "Match two charts",               hi: "दो कुंडलियों का मिलान" },
  groom:           { en: "Groom",                          hi: "वर" },
  bride:           { en: "Bride",                          hi: "वधू" },
  match_now:       { en: "Match these two",                hi: "इन दोनों का मिलान करें" },
  matching:        { en: "Matching…",                      hi: "मिलान हो रहा है…" },
  match_failed:    { en: "Could not match: %1",            hi: "मिलान नहीं हो सका: %1" },
  need_two:        { en: "Add a second person before matching two charts.",
                     hi: "दो कुंडलियों के मिलान के लिए दूसरा व्यक्ति जोड़ें।" },
  same_person:     { en: "Choose two different people.",   hi: "दो अलग-अलग व्यक्ति चुनें।" },
  eight_kootas:    { en: "The eight kootas",               hi: "आठ कूट" },
  koota:           { en: "Koota",                          hi: "कूट" },
  points:          { en: "Points",                         hi: "अंक" },
  score_of:        { en: "%1 of %2",                       hi: "%2 में से %1" },
  koota_varna:     { en: "Varna",                          hi: "वर्ण" },
  koota_vashya:    { en: "Vashya",                         hi: "वश्य" },
  koota_tara:      { en: "Tara",                           hi: "तारा" },
  koota_yoni:      { en: "Yoni",                           hi: "योनि" },
  koota_graha_maitri: { en: "Graha Maitri",                hi: "ग्रह मैत्री" },
  koota_gana:      { en: "Gana",                           hi: "गण" },
  koota_bhakoot:   { en: "Bhakoot",                        hi: "भकूट" },
  koota_nadi:      { en: "Nadi",                           hi: "नाड़ी" },
  mangal_compare:  { en: "Mangal, counted both ways",      hi: "मंगल, दोनों ओर से गिना गया" },
  from_lagna:      { en: "From the Lagna",                 hi: "लग्न से" },
  from_moon:       { en: "From the Moon",                  hi: "चंद्र से" },
  from_venus:      { en: "From Venus",                     hi: "शुक्र से" },
  house_n:         { en: "House %1",                       hi: "भाव %1" },
  milan_note:      { en: "The /36 score is the Moon-based count alone. It is one reading among several, "
                       + "not a verdict on a marriage.",
                     hi: "36 में से अंक केवल चंद्र आधारित गणना है। यह कई दृष्टियों में से एक है, "
                       + "विवाह पर कोई निर्णय नहीं।" },

  // Muhurta
  muhurta:         { en: "Muhurta",                        hi: "मुहूर्त" },
  muhurta_sub:     { en: "Find a good time",               hi: "शुभ समय खोजें" },
  what_for:        { en: "What for",                       hi: "किसके लिए" },
  from_date:       { en: "From",                           hi: "से" },
  to_date:         { en: "To",                             hi: "तक" },
  where:           { en: "Where",                          hi: "कहाँ" },
  who_involved:    { en: "Checked against",                hi: "किनके लिए जाँचा जाए" },
  who_involved_note: { en: "Tarabala and Chandrabala are counted from each person's own Moon, so "
                         + "choosing the people narrows the windows considerably.",
                       hi: "तारा बल और चंद्र बल हर व्यक्ति के अपने चंद्र से गिने जाते हैं, इसलिए "
                         + "व्यक्ति चुनने पर शुभ समय काफ़ी कम हो जाते हैं।" },
  find_times:      { en: "Find the times",                 hi: "शुभ समय खोजें" },
  searching:       { en: "Searching. A few months can take a moment.",
                     hi: "खोज चल रही है। कुछ महीनों में थोड़ा समय लग सकता है।" },
  no_windows:      { en: "Nothing in this range passes the rules for %1. Try a wider range, or fewer "
                       + "people to check against.",
                     hi: "इस अवधि में %1 के लिए कोई शुभ समय नियमों पर खरा नहीं उतरा। अवधि बढ़ाएँ, "
                       + "या कम लोगों के लिए जाँचें।" },
  windows_found:   { en: "%1 windows",                     hi: "%1 शुभ समय" },
  window_when:     { en: "When",                           hi: "कब" },
  window_detail:   { en: "Chart at that time",             hi: "उस समय की स्थिति" },
  supports:        { en: "In favour",                      hi: "पक्ष में" },
  weaknesses:      { en: "Against",                        hi: "विपक्ष में" },
  minutes_n:       { en: "%1 min",                         hi: "%1 मिनट" },

  // numerology
  numbers:         { en: "Numerology",                     hi: "अंक ज्योतिष" },
  numbers_sub:     { en: "Numbers for a person, a name or a number",
                     hi: "व्यक्ति, नाम या संख्या के अंक" },
  person:          { en: "Person",                         hi: "व्यक्ति" },
  second_person:   { en: "And",                            hi: "और" },
  tool:            { en: "Tool",                           hi: "साधन" },
  the_text:        { en: "Name or number",                 hi: "नाम या संख्या" },
  look:            { en: "Work it out",                    hi: "गणना करें" },

  // the Chinese side
  chinese:         { en: "Chinese",                        hi: "चीनी" },
  chinese_sub:     { en: "Lunar date, Zi Wei, Nine Star Ki",
                     hi: "चंद्र तिथि, ज़ी वेई, नौ तारा की" },

  // settings
  settings:        { en: "Settings",                       hi: "सेटिंग्स" },
  settings_sub:    { en: "Calculation, appearance and your data",
                     hi: "गणना, रूप-रंग और आपका विवरण" },
  calculation:     { en: "Calculation",                    hi: "गणना" },
  ayanamsa:        { en: "Ayanamsa",                       hi: "अयनांश" },
  house_system:    { en: "House system",                   hi: "भाव पद्धति" },
  node:            { en: "Rahu and Ketu",                  hi: "राहु और केतु" },
  orb_scale:       { en: "Aspect orbs",                    hi: "दृष्टि की सीमा" },
  calc_note:       { en: "Changing these works out every chart again. Nothing already saved is lost.",
                     hi: "ये बदलने पर हर कुंडली फिर से बनती है। सहेजा हुआ कुछ भी नहीं जाता।" },
  appearance:      { en: "Appearance",                     hi: "रूप-रंग" },
  theme:           { en: "Theme",                          hi: "रंग-रूप" },
  chart_style:     { en: "Chart style",                    hi: "कुंडली शैली" },
  credits:         { en: "On every report",                hi: "हर रिपोर्ट पर" },
  report_by:       { en: "Prepared by",                    hi: "द्वारा तैयार" },
  report_site:     { en: "Website",                        hi: "वेबसाइट" },
  saved:           { en: "Saved",                          hi: "सहेजा गया" },

  // backup
  backup:          { en: "Backup",                         hi: "बैकअप" },
  backup_note:     { en: "Everyone saved here, in one encrypted file. The same file opens on the "
                       + "Android app. The password is not stored anywhere: if it is lost, so is the file.",
                     hi: "यहाँ सहेजे सभी लोग, एक एन्क्रिप्टेड फ़ाइल में। यही फ़ाइल एंड्रॉइड ऐप में भी खुलती है। "
                       + "पासवर्ड कहीं नहीं रखा जाता: खो गया तो फ़ाइल भी गई।" },
  password:        { en: "Password (at least 6 characters)", hi: "पासवर्ड (कम से कम 6 अक्षर)" },
  make_backup:     { en: "Write the backup",               hi: "बैकअप बनाएँ" },
  backup_done:     { en: "%1 people saved as %2",          hi: "%1 लोग %2 में सहेजे गए" },
  restore:         { en: "Restore",                        hi: "पुनर्स्थापित करें" },
  restore_note:    { en: "A restore adds to what is already here and never removes anyone.",
                     hi: "पुनर्स्थापना पहले से मौजूद विवरण में जोड़ती है, किसी को हटाती नहीं।" },
  choose_file:     { en: "Choose a backup file",           hi: "बैकअप फ़ाइल चुनें" },
  restore_now:     { en: "Restore from this file",         hi: "इस फ़ाइल से पुनर्स्थापित करें" },
  restore_done:    { en: "%1 added, %2 updated, %3 skipped", hi: "%1 जोड़े, %2 बदले, %3 छोड़े" },

  // about
  about:           { en: "About",                          hi: "जानकारी" },
  engine_version:  { en: "Engine",                         hi: "इंजन" },
  where_data:      { en: "Your details are in",            hi: "आपका विवरण यहाँ है" },
  where_reports:   { en: "Reports are written to",         hi: "रिपोर्ट यहाँ बनती हैं" },

  // the demo and unlocking it
  demo:            { en: "Demo",                           hi: "डेमो" },
  demo_one:        { en: "Demo · saves %1 chart",          hi: "डेमो · %1 कुंडली सहेजता है" },
  demo_many:       { en: "Demo · saves %1 charts",         hi: "डेमो · %1 कुंडलियाँ सहेजता है" },
  full_version:    { en: "Full version",                   hi: "पूर्ण संस्करण" },
  unlocked_to:     { en: "Unlocked for %1",                hi: "%1 के लिए खुला" },
  unlock:          { en: "Unlock",                         hi: "खोलें" },
  unlock_title:    { en: "The full version",               hi: "पूर्ण संस्करण" },
  unlock_sub:      { en: "One payment. Everything keeps working without the internet.",
                     hi: "एक बार भुगतान। सब कुछ बिना इंटरनेट के चलता रहता है।" },
  unlock_what:     { en: "As many charts as you like, with the place lookup and every reading; "
                       + "Kundali Milan for any two people; Muhurta checked against the people involved; "
                       + "all nine reports saved as files; backup and restore.",
                     hi: "जितनी चाहें उतनी कुंडलियाँ, स्थान खोज और हर विश्लेषण के साथ; किन्हीं दो लोगों का "
                       + "कुंडली मिलान; संबंधित लोगों के अनुसार जाँचा गया मुहूर्त; सभी नौ रिपोर्ट फ़ाइल के रूप में; "
                       + "बैकअप और पुनर्स्थापना।" },
  unlock_where:    { en: "A code comes with the purchase and is tied to the email address it was bought "
                       + "with. The same code works on the Android app.",
                     hi: "कोड खरीद के साथ मिलता है और उसी ईमेल पते से जुड़ा होता है जिससे खरीदा गया। "
                       + "यही कोड एंड्रॉइड ऐप पर भी चलता है।" },
  your_email:      { en: "The email you bought with",      hi: "जिस ईमेल से खरीदा" },
  your_code:       { en: "Unlock code",                    hi: "अनलॉक कोड" },
  unlock_now:      { en: "Unlock",                         hi: "खोलें" },
  unlock_done:     { en: "Unlocked. There is no limit now.",
                     hi: "खुल गया। अब कोई सीमा नहीं।" },
  unlock_offline:  { en: "This is checked on this computer. Nothing is sent anywhere.",
                     hi: "यह जाँच इसी कंप्यूटर पर होती है। कुछ भी कहीं नहीं भेजा जाता।" },
  waiting_people:  { en: "%1 more are in the file and will be restored once this is unlocked.",
                     hi: "फ़ाइल में %1 और हैं, जो पूर्ण संस्करण खुलने पर आ जाएँगे।" },

  // today
  today:           { en: "Today",                          hi: "आज" },
  today_sub:       { en: "Panchang and the day's periods", hi: "पंचांग और दिन के समय" },
  today_where:     { en: "Read for %1",                    hi: "%1 के लिए" },
  change_place:    { en: "Change the place",               hi: "स्थान बदलें" },
  set_place_first: { en: "Choose where you are, so the panchang and the periods are for your own sunrise.",
                     hi: "आप कहाँ हैं यह चुनें, ताकि पंचांग और समय आपके अपने सूर्योदय के अनुसार हों।" },
  sun_moon:        { en: "Sun and Moon",                   hi: "सूर्य और चंद्र" },
  sunrise_set:     { en: "Sunrise · sunset",               hi: "सूर्योदय · सूर्यास्त" },
  moonrise_set:    { en: "Moonrise · moonset",             hi: "चंद्रोदय · चंद्रास्त" },
  panchang:        { en: "Panchang",                       hi: "पंचांग" },
  weekday:         { en: "Weekday",                        hi: "वार" },
  yoga:            { en: "Yoga",                           hi: "योग" },
  karana:          { en: "Karana",                         hi: "करण" },
  sun_sign:        { en: "Sun sign",                       hi: "सूर्य राशि" },
  lunar_month:     { en: "Lunar month",                    hi: "चंद्र मास" },
  samvat:          { en: "Samvat",                         hi: "संवत" },
  periods_good:    { en: "Times to use",                   hi: "शुभ समय" },
  periods_avoid:   { en: "Times to avoid",                 hi: "त्याज्य समय" },
  abhijit:         { en: "Abhijit",                        hi: "अभिजित" },
  brahma_muhurta:  { en: "Brahma muhurta",                 hi: "ब्रह्म मुहूर्त" },
  rahu_kalam:      { en: "Rahu kalam",                     hi: "राहु काल" },
  yamaganda:       { en: "Yamaganda",                      hi: "यमगंड" },
  gulika_kalam:    { en: "Gulika kalam",                   hi: "गुलिक काल" },
  choghadiya:      { en: "Choghadiya",                     hi: "चौघड़िया" },
  by_day:          { en: "Day",                            hi: "दिन" },
  by_night:        { en: "Night",                          hi: "रात" },
  festivals:       { en: "Coming up",                      hi: "आगे" },

  // the outlook
  forecast:        { en: "Three-year outlook",             hi: "तीन वर्ष का भविष्यफल" },
  predictions:     { en: "Predictions",                    hi: "भविष्यफल" },
  outlook_for:     { en: "Outlook",                        hi: "रुझान" },
  show_forecast:   { en: "Work out the outlook",           hi: "रुझान निकालें" },
  dasha_now:       { en: "%1 mahadasha, %2 antardasha",    hi: "%1 महादशा, %2 अंतर्दशा" },

  // prashna
  prashna:         { en: "Prashna",                        hi: "प्रश्न" },
  prashna_sub:     { en: "A chart for the moment you ask", hi: "प्रश्न के क्षण की कुंडली" },
  the_question:    { en: "The question",                   hi: "प्रश्न" },
  method:          { en: "Method",                         hi: "पद्धति" },
  method_prashna:  { en: "Prashna (the moment)",           hi: "प्रश्न (वर्तमान क्षण)" },
  method_kp:       { en: "KP number (1 to 249)",           hi: "केपी संख्या (1 से 249)" },
  kp_number:       { en: "Number",                         hi: "संख्या" },
  ask_now:         { en: "Ask",                            hi: "पूछें" },
  lean_favourable: { en: "The signs lean favourable",      hi: "संकेत अनुकूल हैं" },
  lean_against:    { en: "The signs ask for patience",      hi: "संकेत धैर्य माँगते हैं" },
  lean_mixed:      { en: "The signs are mixed",             hi: "संकेत मिश्रित हैं" },
  checks_passed:   { en: "%1 of %2 checks favour it",      hi: "%2 में से %1 जाँच अनुकूल" },
  prashna_note:    { en: "A prashna answers the moment it was asked in, not the future. Read it as one "
                       + "view among several.",
                     hi: "प्रश्न उस क्षण का उत्तर देता है जिसमें पूछा गया, भविष्य का नहीं। इसे कई दृष्टियों "
                       + "में से एक मानें।" },

  // comparing several people
  compare:         { en: "Compare",                        hi: "तुलना" },
  compare_sub:     { en: "Several people side by side",    hi: "कई लोग साथ-साथ" },
  choose_people:   { en: "Choose two or more",             hi: "दो या अधिक चुनें" },
  compare_now:     { en: "Compare them",                   hi: "तुलना करें" },

  // flying stars
  flying_stars:    { en: "Flying Stars",                   hi: "उड़ते तारे" },

  // life events and the birth-time check
  life_events:     { en: "Life events",                    hi: "जीवन की घटनाएँ" },
  events_note:     { en: "Dated events are what a birth time can be checked against. They stay on this "
                       + "computer with everything else.",
                     hi: "तिथि सहित घटनाएँ ही वह आधार हैं जिनसे जन्म समय जाँचा जा सकता है। ये बाकी सब की "
                       + "तरह इसी कंप्यूटर पर रहती हैं।" },
  add_event:       { en: "Add an event",                   hi: "घटना जोड़ें" },
  remove:          { en: "Remove",                         hi: "हटाएँ" },
  what_happened:   { en: "What happened",                  hi: "क्या हुआ" },
  when_happened:   { en: "When",                           hi: "कब" },
  time_check:      { en: "Birth time check",               hi: "जन्म समय जाँच" },
  search_window:   { en: "Search either side",             hi: "दोनों ओर खोजें" },
  minutes_either:  { en: "%1 minutes",                     hi: "%1 मिनट" },
  check_time:      { en: "Check the birth time",           hi: "जन्म समय जाँचें" },
  checking:        { en: "Checking. This takes a few seconds.",
                     hi: "जाँच हो रही है। इसमें कुछ सेकंड लगते हैं।" },
  need_events:     { en: "Add at least one dated event first; without one there is nothing to check "
                       + "a time against.",
                     hi: "पहले कम से कम एक तिथि सहित घटना जोड़ें; उसके बिना समय की जाँच किस आधार पर हो।" },
  span:            { en: "Birth time",                     hi: "जन्म समय" },
  lagna_d9_d10:    { en: "Lagna · D9 · D10",               hi: "लग्न · D9 · D10" },
  events_fit:      { en: "Events fitting",                 hi: "मेल खाती घटनाएँ" },
  by_chance:       { en: "By chance",                      hi: "संयोग से" },
  as_recorded:     { en: "as recorded",                    hi: "दर्ज समय" },

  // the last few tools
  method_horary:   { en: "Western horary",                 hi: "पाश्चात्य होररी" },
  custom_varga:    { en: "A divisional chart of your own", hi: "अपनी वर्ग कुंडली" },
  division:        { en: "Divide each sign into",          hi: "हर राशि के भाग" },
  counting:        { en: "Counting",                       hi: "गणना" },
  draw_varga:      { en: "Draw it",                        hi: "बनाएँ" },
  name_numbers:    { en: "The name's numbers",             hi: "नाम के अंक" },
  show_names:      { en: "Work out the name",              hi: "नाम की गणना करें" },
  mulank:          { en: "Mulank",                         hi: "मूलांक" },
  bhagyank:        { en: "Bhagyank",                       hi: "भाग्यांक" },
  spellings:       { en: "Spellings that fit better",      hi: "बेहतर मेल खाती वर्तनी" },
  spelling:        { en: "Spelling",                       hi: "वर्तनी" },
  compound:        { en: "Compound",                       hi: "संयुक्त अंक" },
  what_changes:    { en: "What changes",                   hi: "क्या बदलता है" },
  already_fits:    { en: "The name as written already fits the birth numbers.",
                     hi: "नाम जैसा लिखा है, वह जन्म अंकों से पहले ही मेल खाता है।" },
  notes:           { en: "Notes",                          hi: "टिप्पणियाँ" },
  notes_hint:      { en: "Anything you want to remember about this person. It stays on this computer.",
                     hi: "इस व्यक्ति के बारे में जो याद रखना हो। यह इसी कंप्यूटर पर रहता है।" },

  // readings
  readings:        { en: "Readings (%1)",                  hi: "विश्लेषण (%1)" },
  search_readings: { en: "Search the readings…",           hi: "विश्लेषण में खोजें…" },
  no_match:        { en: "Nothing matches that.",          hi: "इससे कुछ नहीं मिला।" },
};

let LANG = "en";

function setLang(lang) {
  LANG = lang === "hi" ? "hi" : "en";
  document.documentElement.lang = LANG;
  return LANG;
}

function lang() {
  return LANG;
}

/** t("period", "Jupiter", "2019-03-01", "2035-03-01") - %1, %2, %3 are filled in order. */
function t(key, ...values) {
  const entry = STRINGS[key];
  if (!entry) throw new Error(`No such string: ${key}`);
  return values.reduce((s, v, i) => s.split(`%${i + 1}`).join(String(v)), entry[LANG] ?? entry.en);
}
