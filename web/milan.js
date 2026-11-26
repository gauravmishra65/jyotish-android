/* The Kundli Milan page. Two Moon longitudes in, the eight kootas out.
   Scores come from koota.js, which carries the app's own tables. */

const MUI = {
  en:{
    names:{varna:"Varna", vashya:"Vashya", tara:"Tara", yoni:"Yoni",
           graha_maitri:"Graha Maitri", gana:"Gana", bhakoot:"Bhakoot", nadi:"Nadi"},
    what:{varna:"Rank of the two Moon signs", vashya:"Which group each Moon sign belongs to",
          tara:"Counting between the two birth stars", yoni:"The animal of each birth star",
          graha_maitri:"How the two Moon-sign lords regard each other",
          gana:"Temperament of each birth star", bhakoot:"Where the Moon signs stand from each other",
          nadi:"The constitutional group of each birth star"},
    bands:{below18:"Below 18. Tradition does not usually recommend a match on this score alone.",
           "18to24":"18 to 24. Customarily acceptable.",
           "25to32":"25 to 32. Customarily a good score.",
           above32:"Above 32. Customarily an excellent score."},
    cols:["Koota","What it compares","Groom","Bride","Score"],
    groomH:"First person", brideH:"Second person",
    lDate:"Date of birth", lTime:"Time of birth", lTz:"Time zone at birth",
    go:"Compare the charts",
    totalWord:"out of 36", sixWord:"of which the six rashi-and-star kootas give",
    moonLine:(n,s)=>n + " in " + s,
    dosha:"dosha", same:"same", 
    rangeNote:r=>"Published Vashya tables disagree about this pair, so the total runs from "
      + r[0] + " to " + r[1] + " depending on which is used. The figure above uses the first.",
    caveats:"<strong>What this score is and is not.</strong> The 36 gunas compare two Moons — their "
      + "birth stars and their signs — and nothing else. They say nothing about the seventh house, "
      + "the strength of Venus or Jupiter, Mangal, or the Navamsa, all of which a practitioner weighs "
      + "before saying anything at all. Published tables also disagree: Vashya has at least three in "
      + "circulation, the Gana matrix scores Deva-Manushya as 5 or 6 depending on the publisher, and "
      + "Nadi and Bhakoot both carry traditional exceptions this page does not apply. Treat the number "
      + "as one reading among several, not a verdict on two people."
  },
  hi:{
    names:{varna:"वर्ण", vashya:"वश्य", tara:"तारा", yoni:"योनि",
           graha_maitri:"ग्रह मैत्री", gana:"गण", bhakoot:"भकूट", nadi:"नाड़ी"},
    what:{varna:"दोनों चंद्र राशियों का वर्ण", vashya:"हर चंद्र राशि किस वर्ग में आती है",
          tara:"दोनों जन्म नक्षत्रों के बीच गणना", yoni:"हर जन्म नक्षत्र का पशु",
          graha_maitri:"दोनों राशि-स्वामियों का परस्पर भाव",
          gana:"हर जन्म नक्षत्र का स्वभाव", bhakoot:"चंद्र राशियाँ एक-दूसरे से किस स्थान पर",
          nadi:"हर जन्म नक्षत्र की नाड़ी"},
    bands:{below18:"18 से कम। परंपरा सामान्यतः केवल इस अंक पर मिलान की संस्तुति नहीं करती।",
           "18to24":"18 से 24। परंपरा में स्वीकार्य।",
           "25to32":"25 से 32। परंपरा में अच्छा अंक।",
           above32:"32 से ऊपर। परंपरा में उत्तम अंक।"},
    cols:["कूट","किसकी तुलना","वर","वधू","अंक"],
    groomH:"पहला व्यक्ति", brideH:"दूसरा व्यक्ति",
    lDate:"जन्म तिथि", lTime:"जन्म समय", lTz:"जन्म के समय का टाइम ज़ोन",
    go:"कुंडली मिलाइए",
    totalWord:"36 में से", sixWord:"जिसमें छह राशि-नक्षत्र कूट देते हैं",
    moonLine:(n,s)=>n + ", " + s + " में",
    dosha:"दोष", same:"समान",
    rangeNote:r=>"प्रकाशित वश्य सारणियाँ इस जोड़ी पर असहमत हैं, इसलिए कुल " + r[0] + " से " + r[1]
      + " तक जाता है। ऊपर का अंक पहली सारणी से है।",
    caveats:"<strong>यह अंक क्या है और क्या नहीं।</strong> 36 गुण केवल दो चंद्रमाओं की तुलना करते हैं "
      + "— उनके जन्म नक्षत्र और राशियाँ — और कुछ नहीं। सप्तम भाव, शुक्र या गुरु का बल, मंगल, "
      + "नवांश — इनमें से किसी पर ये कुछ नहीं कहते, जबकि कोई भी कुछ कहने से पहले इन सबको तौलता है। "
      + "सारणियाँ भी असहमत हैं: वश्य की कम से कम तीन प्रचलित हैं, गण सारणी देव-मनुष्य को प्रकाशक के "
      + "अनुसार 5 या 6 देती है, और नाड़ी तथा भकूट दोनों में परंपरागत अपवाद हैं जो यह पृष्ठ लागू नहीं "
      + "करता। इस संख्या को कई पाठों में से एक मानिए, दो व्यक्तियों पर निर्णय नहीं।"
  }
};

function initMilanPage(){
  const form = document.getElementById("form");
  const lang = form.dataset.lang === "hi" ? "hi" : "en";
  const t = MUI[lang];
  const ORDER = ["varna","vashya","tara","yoni","graha_maitri","gana","bhakoot","nadi"];

  for(const who of ["g","b"]) fillZones(document.getElementById("tz_" + who));

  const moonOf = who => {
    const dv = document.getElementById("date_" + who).value;
    const tv = document.getElementById("time_" + who).value;
    if(!dv || !tv) return null;
    const [y,mo,d] = dv.split("-").map(Number), [h,mi] = tv.split(":").map(Number);
    return Engine.moonSidereal(zonedToUTC(y,mo,d,h,mi,document.getElementById("tz_" + who).value));
  };

  form.addEventListener("submit", function(e){
    e.preventDefault();
    const lg = moonOf("g"), lb = moonOf("b");
    if(lg === null || lb === null) return;
    const v = gunaMilan(lg, lb), K = v.kootas;

    const cell = (k, side) => {
      const x = K[k];
      if(k === "tara") return side === "groom" ? String(x.brideToGroom) : String(x.groomToBride);
      if(k === "bhakoot") return x.moonSigns[side === "groom" ? 0 : 1] + " (" + x.positions.join("/") + ")";
      if(k === "graha_maitri") return side === "groom" ? x.groomLord : x.brideLord;
      return x[side] !== undefined ? String(x[side]) : "—";
    };
    document.getElementById("rRows").innerHTML = ORDER.map(k => {
      const x = K[k], flag = x.dosha ? " <span class='dim'>(" + t.dosha + ")</span>" : "";
      return "<tr><td><b>" + t.names[k] + "</b></td><td class='dim'>" + t.what[k] + "</td><td>"
        + cell(k,"groom") + "</td><td>" + cell(k,"bride") + "</td><td class='n'><b>"
        + x.score + "</b> / " + x.max + flag + "</td></tr>";
    }).join("");

    document.getElementById("rTotal").innerHTML =
      "<b style='font-size:1.9rem;font-family:var(--serif)'>" + v.total + "</b> " + t.totalWord;
    document.getElementById("rBand").textContent = t.bands[v.band];
    const rn = document.getElementById("rRange");
    if(v.range[0] !== v.range[1]){ rn.textContent = t.rangeNote(v.range); rn.hidden = false; }
    else rn.hidden = true;

    document.getElementById("rMoons").innerHTML =
      "<span>" + t.groomH + ": <b>" + t.moonLine(v.groom.nak, KOOTA.SIGNS[v.groom.sign]) + "</b></span>"
      + " &nbsp;·&nbsp; <span>" + t.brideH + ": <b>" + t.moonLine(v.bride.nak, KOOTA.SIGNS[v.bride.sign]) + "</b></span>";

    document.getElementById("out").hidden = false;
  });
}
