/* Vimshottari dasha, ported from vedic.py so the site and the app agree exactly.
   Needs only the Moon's sidereal longitude: the sequence starts at the lord of
   the birth nakshatra, and the balance of that first period is the fraction of
   the nakshatra the Moon had still to travel. */

const VIM = [["Ketu",7],["Venus",20],["Sun",6],["Moon",10],["Mars",7],
             ["Rahu",18],["Jupiter",16],["Saturn",19],["Mercury",17]];
const VIM_TOTAL = 120, YEAR_DAYS = 365.25, NAK_SPAN = 360/27, DAY_MS = 86400000;

const VIM_HI = {Ketu:"केतु",Venus:"शुक्र",Sun:"सूर्य",Moon:"चंद्र",Mars:"मंगल",
                Rahu:"राहु",Jupiter:"गुरु",Saturn:"शनि",Mercury:"बुध"};

function subdivide(startMs, lengthDays, startIdx){
  const out = [];
  let t = startMs;
  for(let k=0;k<9;k++){
    const i = (startIdx + k) % 9;
    const ln = lengthDays * VIM[i][1] / VIM_TOTAL;
    out.push({i, lord: VIM[i][0], start: t, end: t + ln*DAY_MS});
    t += ln*DAY_MS;
  }
  return out;
}

/* The whole mahadasha table, plus whichever maha/antar/pratyantar contains `nowMs`. */
function vimshottari(moonLon, birthMs, nowMs){
  const lon = ((moonLon % 360) + 360) % 360;
  const ni = Math.floor(lon / NAK_SPAN), startIdx = ni % 9;
  const frac = (lon % NAK_SPAN) / NAK_SPAN;

  const virt = birthMs - VIM[startIdx][1] * frac * YEAR_DAYS * DAY_MS;
  let limit = birthMs + 120 * YEAR_DAYS * DAY_MS;
  while(limit <= nowMs) limit += 120 * YEAR_DAYS * DAY_MS;   // a birth over a cycle ago still lands

  const mahas = [];
  let t = virt, i = startIdx;
  while(t < limit){
    const [lord, yrs] = VIM[i % 9];
    const end = t + yrs * YEAR_DAYS * DAY_MS;
    mahas.push({lord, years: yrs, idx: i % 9, start: t, end,
                shown: Math.max(t, birthMs),
                antardashas: subdivide(t, yrs*YEAR_DAYS, i % 9).filter(a => a.end > birthMs)});
    t = end; i++;
  }

  const current = {};
  for(const m of mahas){
    if(m.start <= nowMs && nowMs < m.end){
      current.mahadasha = m;
      for(const a of subdivide(m.start, m.years*YEAR_DAYS, m.idx)){
        if(a.start <= nowMs && nowMs < a.end){
          current.antardasha = a;
          const lenDays = (a.end - a.start) / DAY_MS;
          for(const p of subdivide(a.start, lenDays, a.i)){
            if(p.start <= nowMs && nowMs < p.end){ current.pratyantar = p; break; }
          }
          break;
        }
      }
      break;
    }
  }
  return {startLord: VIM[startIdx][0], balanceYears: VIM[startIdx][1] * (1 - frac), mahas, current};
}

/* The dasha page: same birth form, the table rendered from vimshottari(). */
const DUI = {
  en:{rows:["Mahadasha","Antardasha","Pratyantar"],
      balance:(l,y)=>"Born in the "+l+" mahadasha, with "+y+" of it still to run.",
      yrs:n=>n+" yr"},
  hi:{rows:["महादशा","अंतर्दशा","प्रत्यंतर"],
      balance:(l,y)=>"जन्म "+l+" की महादशा में, जिसमें "+y+" शेष थे।",
      yrs:n=>n+" वर्ष"}
};

function initDashaPage(){
  const form = document.getElementById("form");
  const lang = form.dataset.lang === "hi" ? "hi" : "en";
  const t = DUI[lang], lordOf = l => lang === "hi" ? VIM_HI[l] : l;
  /* Dasha boundaries are read in the native's own local time, which is what the app shows.
     Formatting in UTC, or in whatever zone the reader happens to sit in, moves a boundary
     by a day. So every date on this page is rendered in the birth timezone. */
  let birthTz = "UTC";
  const day = ms => new Date(ms).toLocaleDateString(lang === "hi" ? "hi-IN" : "en-GB",
    {day:"numeric", month:"short", year:"numeric", timeZone: birthTz});
  const yearsText = n => {
    const whole = Math.floor(n), months = Math.round((n - whole) * 12);
    if (lang === "hi") return whole + " वर्ष " + months + " माह";
    return whole + " yr " + months + " mo";
  };

  fillZones(document.getElementById("tz"));

  form.addEventListener("submit", function(e){
    e.preventDefault();
    const dv = document.getElementById("date").value, tv = document.getElementById("time").value;
    if(!dv || !tv) return;
    const [y,mo,d] = dv.split("-").map(Number), [h,mi] = tv.split(":").map(Number);
    birthTz = document.getElementById("tz").value;
    const utc = zonedToUTC(y,mo,d,h,mi,birthTz);
    const v = vimshottari(lonAt(utc), utc.getTime(), Date.now());

    document.getElementById("rBalance").textContent =
      t.balance(lordOf(v.startLord), yearsText(v.balanceYears));

    const c = v.current, cur = [];
    if(c.mahadasha)  cur.push([t.rows[0], c.mahadasha]);
    if(c.antardasha) cur.push([t.rows[1], c.antardasha]);
    if(c.pratyantar) cur.push([t.rows[2], c.pratyantar]);
    document.getElementById("rCur").innerHTML = cur.map(([label, p]) =>
      "<tr><td>"+label+"</td><td><b>"+lordOf(p.lord)+"</b></td><td class='n'>"+day(p.start)
      + "</td><td class='n'>"+day(p.end)+"</td></tr>").join("");

    const nowMs = Date.now();
    document.getElementById("rSeq").innerHTML = v.mahas.map(m => {
      const live = m.start <= nowMs && nowMs < m.end;
      return "<tr"+(live ? " style='background:var(--band)'" : "")+"><td>"+(live ? "<b>" : "")
        + lordOf(m.lord) + (live ? "</b>" : "") + "</td><td class='n'>" + day(m.shown)
        + "</td><td class='n'>" + day(m.end) + "</td><td class='n'>" + t.yrs(m.years) + "</td></tr>";
    }).join("");

    document.getElementById("out").hidden = false;
  });
}
