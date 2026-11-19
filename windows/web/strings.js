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
