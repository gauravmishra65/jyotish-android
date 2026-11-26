/* Everything the pages share, on top of moon.js: the nakshatra and rashi tables, the
   helpers, the engine seam, and one controller per page family.

   This file is a source. engine.js is NOT - build.py writes it by putting moon.js, the
   nakshatra data from data.json and this file together, so the lunar theory the pages run
   is the same text verify.py measures rather than a copy of it that can drift. Edit here;
   never edit engine.js.

   Engine.accuracy below is the one place the accuracy figures live. verify.py measures
   them and fails if they have moved away from these values; build.py reads them out of
   this file to write the method page. */

/* ---- nakshatra data and shared page behaviour ---------------------------- */
const NAK = /*@NAK@*/[];
const NAKW = 360/27, PADAW = NAKW/4, CUSP = 0.02;
/* The twelve rashis. Names and lords are checked against the app's own tables by
   verify.py, so the site and the app cannot drift apart on something this basic. */
const RASHI = [
  {en:"Aries",       hi:"मेष",    lord:"Mars",    lordHi:"मंगल"},
  {en:"Taurus",      hi:"वृषभ",   lord:"Venus",   lordHi:"शुक्र"},
  {en:"Gemini",      hi:"मिथुन",  lord:"Mercury", lordHi:"बुध"},
  {en:"Cancer",      hi:"कर्क",   lord:"Moon",    lordHi:"चंद्र"},
  {en:"Leo",         hi:"सिंह",   lord:"Sun",     lordHi:"सूर्य"},
  {en:"Virgo",       hi:"कन्या",  lord:"Mercury", lordHi:"बुध"},
  {en:"Libra",       hi:"तुला",   lord:"Venus",   lordHi:"शुक्र"},
  {en:"Scorpio",     hi:"वृश्चिक", lord:"Mars",    lordHi:"मंगल"},
  {en:"Sagittarius", hi:"धनु",    lord:"Jupiter", lordHi:"गुरु"},
  {en:"Capricorn",   hi:"मकर",    lord:"Saturn",  lordHi:"शनि"},
  {en:"Aquarius",    hi:"कुंभ",   lord:"Saturn",  lordHi:"शनि"},
  {en:"Pisces",      hi:"मीन",    lord:"Jupiter", lordHi:"गुरु"}
];
const RASW = 30;

function dms(deg){
  let d = Math.floor(deg), mF = (deg-d)*60, m = Math.floor(mF), s = Math.round((mF-m)*60);
  if(s===60){ s=0; m++; } if(m===60){ m=0; d++; }
  return d+"\u00b0 "+String(m).padStart(2,"0")+"\u2032 "+String(s).padStart(2,"0")+"\u2033";
}
function offsetMinutes(tz, date){
  const p = new Intl.DateTimeFormat("en-US",{timeZone:tz,hour12:false,year:"numeric",month:"2-digit",
    day:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit"})
    .formatToParts(date).reduce((a,x)=>(a[x.type]=x.value,a),{});
  return (Date.UTC(+p.year,+p.month-1,+p.day,+p.hour%24,+p.minute,+p.second) - date.getTime())/60000;
}
function zonedToUTC(y,mo,d,h,mi,tz){
  let ms = Date.UTC(y,mo-1,d,h,mi);
  for(let i=0;i<2;i++) ms = Date.UTC(y,mo-1,d,h,mi) - offsetMinutes(tz,new Date(ms))*60000;
  return new Date(ms);
}
function jdOf(dateUTC){
  return julianDay(dateUTC.getUTCFullYear(), dateUTC.getUTCMonth()+1, dateUTC.getUTCDate(),
    dateUTC.getUTCHours() + dateUTC.getUTCMinutes()/60 + dateUTC.getUTCSeconds()/3600);
}
function lonAt(dateUTC){
  return moonSidereal(jdOf(dateUTC), dateUTC.getUTCFullYear(), dateUTC.getUTCMonth()+1);
}
function nakAt(dateUTC){ return Math.floor(lonAt(dateUTC)/NAKW); }
function rasAt(dateUTC){ return Math.floor(lonAt(dateUTC)/RASW); }

/* When the Moon next enters division `idx` of `at`, searched forward from `from`.
   `at` is nakAt for a nakshatra and rasAt for a rashi; the search is the same. */
function nextIn(at, idx, from){
  const DAY = 86400000;
  let t = from.getTime();
  if(at(new Date(t)) === idx){                          // already inside: step past this visit
    while(at(new Date(t)) === idx) t += 0.25*DAY;
  }
  let prev = t;
  for(let k=0;k<160;k++){                               // 40 days covers a full lunar circuit
    const next = prev + 0.25*DAY;
    if(at(new Date(next)) === idx){
      let lo = prev, hi = next;                         // bisect to the minute
      for(let b=0;b<20;b++){
        const mid = (lo+hi)/2;
        if(at(new Date(mid)) === idx) hi = mid; else lo = mid;
      }
      return new Date(hi);
    }
    prev = next;
  }
  return null;
}
function nextEntry(idx, from){ return nextIn(nakAt, idx, from); }
function nextSign(idx, from){ return nextIn(rasAt, idx, from); }
function fillZones(sel){
  let zones; try{ zones = Intl.supportedValuesOf("timeZone"); }catch(e){ zones = null; }
  if(!zones || !zones.length) zones = ["Asia/Kolkata","Asia/Singapore","Asia/Dubai","Europe/London",
    "America/New_York","America/Los_Angeles","Australia/Sydney","UTC"];
  for(const z of zones){ const o=document.createElement("option"); o.value=z; o.textContent=z.replace(/_/g," "); sel.appendChild(o); }
  /* Engines disagree on canonical names - Chromium still answers Asia/Calcutta where others say
     Asia/Kolkata - and an unmatched preference used to leave every visitor on whatever sorts
     first, which was Africa/Abidjan. Try the visitor's own zone, then India, then give up. */
  let own = null;
  try{ own = Intl.DateTimeFormat().resolvedOptions().timeZone; }catch(e){ own = null; }
  const prefer = [own, "Asia/Kolkata", "Asia/Calcutta"];
  sel.value = prefer.find(z => z && zones.indexOf(z) >= 0) || zones[0];
}
function fmtWhen(d, lang){
  return d.toLocaleString(lang === "hi" ? "hi-IN" : undefined,{weekday:"short",day:"numeric",month:"short",year:"numeric",
    hour:"2-digit",minute:"2-digit"});
}


/* ---- the engine seam ----------------------------------------------------
   Every page asks for the Moon through Engine.moonSidereal(). Today that is the
   truncated theory in this file, good to about 11 arcseconds. A WebAssembly build
   of Swiss Ephemeris itself would be exact; when one exists, it registers here and
   no page changes:

       Engine.use({ name: "swisseph-wasm", moonSidereal: dateUTC => ... });

   Pages that quote an accuracy figure read Engine.accuracy, so the wording follows
   the engine instead of being copied into twenty-eight files. */
const Engine = {
  name: "truncated-elp2000",
  accuracy: {meanArcsec: 11.2, worstArcsec: 28.3, dashaShiftDays: 1.14, dashaWorstDays: 3.81},
  moonSidereal: dateUTC => lonAt(dateUTC),
  use(impl){ Object.assign(Engine, impl); }
};

/* Per-nakshatra page: the live readout plus the birth calculator, in either language. */
const UI = {
  en:{inNow:(n,d)=>"<strong>The Moon is in "+n+" right now</strong>, at "+d+" sidereal.",
      elsewhere:(n,d)=>"The Moon is in <strong>"+n+"</strong> at the moment, at "+d+" sidereal.",
      moveOn:(n,w)=>"It moves on into "+n+" at "+w+", your local time.",
      enters:(n,w)=>"It next enters "+n+" at "+w+", your local time.",
      pada:n=>"Pada "+n, yes:" — yes, this one",
      at:(d,a)=>"Moon at "+d+" sidereal · ayanamsa "+a+"° (Lahiri)",
      cusp:(a,b)=>"Your Moon sits within a whisker of the boundary between <b>"+a+"</b> and <b>"+b
        +"</b>. At this distance the answer needs the full ephemeris, not this page."},
  hi:{inNow:(n,d)=>"<strong>इस समय चंद्रमा "+n+" में है</strong>, "+d+" निरयन पर।",
      elsewhere:(n,d)=>"इस समय चंद्रमा <strong>"+n+"</strong> में है, "+d+" निरयन पर।",
      moveOn:(n,w)=>"यह "+w+" (आपके स्थानीय समय) पर "+n+" में चला जाएगा।",
      enters:(n,w)=>"यह अगली बार "+w+" (आपके स्थानीय समय) पर "+n+" में प्रवेश करेगा।",
      pada:n=>"पाद "+n, yes:" — हाँ, यही",
      at:(d,a)=>"चंद्र "+d+" निरयन · अयनांश "+a+"° (लाहिरी)",
      cusp:(a,b)=>"आपका चंद्रमा <b>"+a+"</b> और <b>"+b+"</b> की संधि के अत्यंत निकट है। "
        +"इतनी निकटता पर उत्तर के लिए पूर्ण एफ़ेमेरिस चाहिए, यह पृष्ठ नहीं।"}
};

function initNakPage(){
  const live = document.getElementById("live");
  const idx = +live.dataset.nak, lang = live.dataset.lang === "hi" ? "hi" : "en";
  const t = UI[lang], nameOf = n => lang === "hi" ? n.hi : n.en;
  const me = NAK[idx], now = new Date(), lonNow = Engine.moonSidereal(now), here = Math.floor(lonNow/NAKW);

  if(here === idx){
    live.classList.add("hit");
    document.getElementById("liveNow").innerHTML = t.inNow(nameOf(me), dms(lonNow));
    const leaves = nextEntry((idx+1)%27, now);
    document.getElementById("liveNext").textContent =
      leaves ? t.moveOn(nameOf(NAK[(idx+1)%27]), fmtWhen(leaves, lang)) : "";
  } else {
    document.getElementById("liveNow").innerHTML = t.elsewhere(nameOf(NAK[here]), dms(lonNow));
    const nxt = nextEntry(idx, now);
    document.getElementById("liveNext").textContent =
      nxt ? t.enters(nameOf(me), fmtWhen(nxt, lang)) : "";
  }

  const tz = document.getElementById("tz");
  fillZones(tz);
  document.getElementById("form").addEventListener("submit", function(e){
    e.preventDefault();
    const dv = document.getElementById("date").value, tv = document.getElementById("time").value;
    if(!dv || !tv) return;
    const [y,mo,d] = dv.split("-").map(Number), [h,mi] = tv.split(":").map(Number);
    const utc = zonedToUTC(y,mo,d,h,mi,tz.value), lon = lonAt(utc);
    const i = Math.floor(lon/NAKW), n = NAK[i], pada = Math.floor((lon - i*NAKW)/PADAW)+1;
    document.getElementById("rName").textContent = nameOf(n);
    document.getElementById("rDev").textContent = lang === "hi" ? n.en : n.hi;
    document.getElementById("rPada").textContent = t.pada(pada) + (i===idx ? t.yes : "");
    document.getElementById("rLon").textContent = t.at(dms(lon), ayanamsa(jdOf(utc)).toFixed(4));
    const within = ((lon%NAKW)+NAKW)%NAKW, edge = Math.min(within, NAKW-within);
    const cusp = document.getElementById("rCusp");
    if(edge < CUSP){
      const other = NAK[within < NAKW/2 ? (i+26)%27 : (i+1)%27];
      cusp.innerHTML = t.cusp(nameOf(n), nameOf(other));
      cusp.hidden = false;
    } else cusp.hidden = true;
    document.getElementById("out").hidden = false;
  });
}


/* ---- rashi pages --------------------------------------------------------
   The Moon sign is the same longitude divided by 30 instead of by 13°20′, so
   every sign boundary is also a pada boundary and the cusp band that protects
   the nakshatra answer protects this one too. verify.py measures that. */
const UIR = {
  en:{inNow:(n,d)=>"<strong>The Moon is in "+n+" right now</strong>, at "+d+" of the sign.",
      elsewhere:(n,d)=>"The Moon is in <strong>"+n+"</strong> at the moment, at "+d+" of that sign.",
      moveOn:(n,w)=>"It moves on into "+n+" at "+w+", your local time.",
      enters:(n,w)=>"It next enters "+n+" at "+w+", your local time.",
      yes:" — yes, this one",
      inSign:d=>d+" into the sign",
      nak:(n,p)=>" · "+n+", pada "+p,
      at:(d,a)=>"Moon at "+d+" sidereal · ayanamsa "+a+"° (Lahiri)",
      cusp:(a,b)=>"Your Moon sits within a whisker of the boundary between <b>"+a+"</b> and <b>"+b
        +"</b>. At this distance the answer needs the full ephemeris, not this page."},
  hi:{inNow:(n,d)=>"<strong>इस समय चंद्रमा "+n+" में है</strong>, राशि में "+d+" पर।",
      elsewhere:(n,d)=>"इस समय चंद्रमा <strong>"+n+"</strong> में है, उस राशि में "+d+" पर।",
      moveOn:(n,w)=>"यह "+w+" (आपके स्थानीय समय) पर "+n+" में चला जाएगा।",
      enters:(n,w)=>"यह अगली बार "+w+" (आपके स्थानीय समय) पर "+n+" में प्रवेश करेगा।",
      yes:" — हाँ, यही",
      inSign:d=>"राशि में "+d,
      nak:(n,p)=>" · "+n+", पाद "+p,
      at:(d,a)=>"चंद्र "+d+" निरयन · अयनांश "+a+"° (लाहिरी)",
      cusp:(a,b)=>"आपका चंद्रमा <b>"+a+"</b> और <b>"+b+"</b> की संधि के अत्यंत निकट है। "
        +"इतनी निकटता पर उत्तर के लिए पूर्ण एफ़ेमेरिस चाहिए, यह पृष्ठ नहीं।"}
};

/* One sign's page when data-ras is 0-11, the hub calculator when it is -1. */
function initRashiPage(){
  const live = document.getElementById("live");
  const idx = +live.dataset.ras, lang = live.dataset.lang === "hi" ? "hi" : "en";
  const t = UIR[lang], nameOf = r => lang === "hi" ? r.hi : r.en;
  const now = new Date(), lonNow = Engine.moonSidereal(now), here = Math.floor(lonNow/RASW);

  if(here === idx){
    live.classList.add("hit");
    document.getElementById("liveNow").innerHTML = t.inNow(nameOf(RASHI[idx]), dms(lonNow % RASW));
    const leaves = nextSign((idx+1)%12, now);
    document.getElementById("liveNext").textContent =
      leaves ? t.moveOn(nameOf(RASHI[(idx+1)%12]), fmtWhen(leaves, lang)) : "";
  } else {
    document.getElementById("liveNow").innerHTML = t.elsewhere(nameOf(RASHI[here]), dms(lonNow % RASW));
    const nxt = idx >= 0 ? nextSign(idx, now) : null;
    document.getElementById("liveNext").textContent =
      nxt ? t.enters(nameOf(RASHI[idx]), fmtWhen(nxt, lang)) : "";
  }

  const tz = document.getElementById("tz");
  fillZones(tz);
  document.getElementById("form").addEventListener("submit", function(e){
    e.preventDefault();
    const dv = document.getElementById("date").value, tv = document.getElementById("time").value;
    if(!dv || !tv) return;
    const [y,mo,d] = dv.split("-").map(Number), [h,mi] = tv.split(":").map(Number);
    const utc = zonedToUTC(y,mo,d,h,mi,tz.value), lon = lonAt(utc);
    const i = Math.floor(lon/RASW), r = RASHI[i];
    const ni = Math.floor(lon/NAKW), n = NAK[ni], pada = Math.floor((lon - ni*NAKW)/PADAW)+1;
    document.getElementById("rName").textContent = nameOf(r);
    document.getElementById("rDev").textContent = lang === "hi" ? r.en : r.hi;
    document.getElementById("rPada").textContent =
      t.inSign(dms(lon % RASW)) + t.nak(lang === "hi" ? n.hi : n.en, pada) + (i === idx ? t.yes : "");
    document.getElementById("rLon").textContent = t.at(dms(lon), ayanamsa(jdOf(utc)).toFixed(4));
    const within = lon % RASW, edge = Math.min(within, RASW - within);
    const cusp = document.getElementById("rCusp");
    if(edge < CUSP){
      const other = RASHI[within < RASW/2 ? (i+11)%12 : (i+1)%12];
      cusp.innerHTML = t.cusp(nameOf(r), nameOf(other));
      cusp.hidden = false;
    } else cusp.hidden = true;
    document.getElementById("out").hidden = false;
  });
}
