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
