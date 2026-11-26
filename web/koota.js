/* Ashtakoota guna milan, ported from ashtakoota.py. Every table below was exported
   from that file rather than retyped, so the site and the app score identically. */
const KOOTA = {"SIGNS":["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"],"SIGN_LORD":["Mars","Venus","Mercury","Moon","Sun","Mercury","Venus","Mars","Jupiter","Saturn","Saturn","Jupiter"],"NAKSHATRAS":["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"],"VARNA":{"3":4,"7":4,"11":4,"0":3,"4":3,"8":3,"1":2,"5":2,"9":2,"2":1,"6":1,"10":1},"VARNA_NAME":{"4":"Brahmin","3":"Kshatriya","2":"Vaishya","1":"Shudra"},"GANA":{"Ashwini":"Deva","Mrigashira":"Deva","Punarvasu":"Deva","Pushya":"Deva","Hasta":"Deva","Swati":"Deva","Anuradha":"Deva","Shravana":"Deva","Revati":"Deva","Bharani":"Manushya","Rohini":"Manushya","Ardra":"Manushya","Purva Phalguni":"Manushya","Uttara Phalguni":"Manushya","Purva Ashadha":"Manushya","Uttara Ashadha":"Manushya","Purva Bhadrapada":"Manushya","Uttara Bhadrapada":"Manushya","Krittika":"Rakshasa","Ashlesha":"Rakshasa","Magha":"Rakshasa","Chitra":"Rakshasa","Vishakha":"Rakshasa","Jyeshtha":"Rakshasa","Mula":"Rakshasa","Dhanishta":"Rakshasa","Shatabhisha":"Rakshasa"},"GANA_SCORE":{"Deva|Deva":6,"Deva|Manushya":6,"Deva|Rakshasa":1,"Manushya|Deva":5,"Manushya|Manushya":6,"Manushya|Rakshasa":0,"Rakshasa|Deva":1,"Rakshasa|Manushya":0,"Rakshasa|Rakshasa":6},"NADI_PATTERN":["Adi","Madhya","Antya","Antya","Madhya","Adi"],"YONI":["Horse","Elephant","Sheep","Serpent","Serpent","Dog","Cat","Sheep","Cat","Rat","Rat","Cow","Buffalo","Tiger","Buffalo","Tiger","Deer","Deer","Dog","Monkey","Mongoose","Monkey","Lion","Horse","Lion","Cow","Elephant"],"YONI_ORDER":["Horse","Elephant","Sheep","Serpent","Dog","Cat","Rat","Cow","Buffalo","Tiger","Deer","Monkey","Mongoose","Lion"],"YONI_MATRIX":[[4,2,2,3,2,2,2,1,0,1,1,3,2,1],[2,4,3,3,2,2,2,2,3,1,2,3,2,0],[2,3,4,2,1,2,1,3,3,1,2,0,3,1],[3,3,2,4,2,1,1,1,1,2,2,2,0,2],[2,2,1,2,4,2,1,2,2,1,0,2,1,1],[2,2,2,1,2,4,0,2,2,1,3,3,2,1],[2,2,1,1,1,0,4,2,2,2,2,2,1,2],[1,2,3,1,2,2,2,4,3,0,3,2,2,1],[0,3,3,1,2,2,2,3,4,1,2,2,2,1],[1,1,1,2,1,1,2,0,1,4,1,1,2,1],[1,2,2,2,0,3,2,3,2,1,4,2,2,1],[3,3,0,2,2,3,2,2,2,1,2,4,3,2],[2,2,3,0,1,2,1,2,2,2,2,3,4,2],[1,0,1,2,1,1,2,1,1,1,1,2,2,4]],"YONI_ENEMY":[["Deer","Dog"],["Mongoose","Serpent"],["Cow","Tiger"],["Buffalo","Horse"],["Monkey","Sheep"],["Elephant","Lion"],["Cat","Rat"]],"YONI_TABLE_NAME":"common North Indian 14x14 Yoni table","VASHYA_ORDER":["Chatushpad (quadruped)","Dwipad (human)","Jalachar (water)","Vanachar (wild)","Keeta (insect)"],"VASHYA_TABLES":{"onlinejyotish.com":[[2,1,1,0,1],[1,2,0.5,0,1],[1,0.5,2,1,1],[0,0,1,2,0],[1,0,1,0,2]],"AstroYogi":[[2,1,1,1.5,1],[1,2,1.5,0,1],[1,1.5,2,1,1],[0,0,0,2,0],[1,1,1,0,2]],"Saravali.de":[[2,0.5,1,0,2],[0.5,2,0,0,0],[1,0,2,2,2],[0,0,2,2,0],[1,0,1,0,2]]},"VASHYA_DEFAULT":"onlinejyotish.com","FRIENDS":{"Sun":["Jupiter","Mars","Moon"],"Moon":["Mercury","Sun"],"Mars":["Jupiter","Moon","Sun"],"Mercury":["Sun","Venus"],"Jupiter":["Mars","Moon","Sun"],"Venus":["Mercury","Saturn"],"Saturn":["Mercury","Venus"]},"ENEMIES":{"Sun":["Saturn","Venus"],"Moon":[],"Mars":["Mercury"],"Mercury":["Moon"],"Jupiter":["Mercury","Venus"],"Venus":["Moon","Sun"],"Saturn":["Mars","Moon","Sun"]}};

const NAK_SPAN_K = 360/27;

function rel(a, b){
  if(a === b) return "same";
  if((KOOTA.FRIENDS[a] || []).indexOf(b) >= 0) return "friend";
  if((KOOTA.ENEMIES[a] || []).indexOf(b) >= 0) return "enemy";
  return "neutral";
}
function vashyaGroup(signIdx, moonLon){
  const d = ((moonLon % 30) + 30) % 30;
  if([2,5,6,10].indexOf(signIdx) >= 0) return "Dwipad (human)";
  if(signIdx === 8) return d < 15 ? "Dwipad (human)" : "Chatushpad (quadruped)";
  if([0,1].indexOf(signIdx) >= 0) return "Chatushpad (quadruped)";
  if(signIdx === 9) return d < 15 ? "Chatushpad (quadruped)" : "Jalachar (water)";
  if([3,11].indexOf(signIdx) >= 0) return "Jalachar (water)";
  if(signIdx === 4) return "Vanachar (wild)";
  return "Keeta (insect)";
}
function personOf(moonLon){
  const lon = ((moonLon % 360) + 360) % 360;
  const ni = Math.floor(lon / NAK_SPAN_K), s = Math.floor(lon / 30);
  return {nakI: ni, nak: KOOTA.NAKSHATRAS[ni], sign: s, lord: KOOTA.SIGN_LORD[s], lon};
}

/* Groom and bride given as sidereal Moon longitudes. Returns the eight kootas and the total. */
function gunaMilan(groomMoonLon, brideMoonLon){
  const groom = personOf(groomMoonLon), bride = personOf(brideMoonLon);
  const K = {};

  const gv = KOOTA.VARNA[String(groom.sign)], bv = KOOTA.VARNA[String(bride.sign)];
  K.varna = {max:1, score: gv >= bv ? 1 : 0,
             groom: KOOTA.VARNA_NAME[String(gv)], bride: KOOTA.VARNA_NAME[String(bv)]};

  const vg = vashyaGroup(groom.sign, groom.lon), vb = vashyaGroup(bride.sign, bride.lon);
  const vi = KOOTA.VASHYA_ORDER.indexOf(vb), vj = KOOTA.VASHYA_ORDER.indexOf(vg);
  const byTable = {};
  for(const name of Object.keys(KOOTA.VASHYA_TABLES)) byTable[name] = KOOTA.VASHYA_TABLES[name][vi][vj];
  const spread = Object.keys(byTable).map(k => byTable[k]);
  K.vashya = {max:2, score: byTable[KOOTA.VASHYA_DEFAULT], groom: vg, bride: vb,
              table: KOOTA.VASHYA_DEFAULT, byTable,
              status: vg === vb ? "same group, which is 2 in every table"
                    : (new Set(spread).size === 1 ? "all tables agree" : "tables differ for this pair")};

  const tara = (from, to) => { const r = (((to - from) % 27 + 27) % 27 + 1) % 9; return r === 0 ? 9 : r; };
  const t1 = tara(bride.nakI, groom.nakI), t2 = tara(groom.nakI, bride.nakI);
  const nBad = [3,5,7].indexOf(t1) >= 0 ? 1 : 0;
  const nBad2 = [3,5,7].indexOf(t2) >= 0 ? 1 : 0;
  K.tara = {max:3, score: [3.0, 1.5, 0.0][nBad + nBad2], brideToGroom: t1, groomToBride: t2};

  const yg = KOOTA.YONI[groom.nakI], yb = KOOTA.YONI[bride.nakI];
  const ysc = KOOTA.YONI_MATRIX[KOOTA.YONI_ORDER.indexOf(yb)][KOOTA.YONI_ORDER.indexOf(yg)];
  const sworn = KOOTA.YONI_ENEMY.some(p => p[0] === [yg,yb].sort()[0] && p[1] === [yg,yb].sort()[1]);
  K.yoni = {max:4, score: ysc, groom: yg, bride: yb, table: KOOTA.YONI_TABLE_NAME,
            status: yg === yb ? "same yoni" : sworn ? "sworn enemies"
                  : ({3:"friendly",2:"neutral",1:"unfriendly"}[ysc] || "graded")};

  const r1 = rel(groom.lord, bride.lord), r2 = rel(bride.lord, groom.lord);
  const pair = [r1, r2].sort();
  let gm;
  if(pair.indexOf("same") >= 0 || (pair[0] === "friend" && pair[1] === "friend")) gm = 5.0;
  else if(pair[0] === "friend" && pair[1] === "neutral") gm = 4.0;
  else if(pair[0] === "neutral" && pair[1] === "neutral") gm = 3.0;
  else if(pair[0] === "enemy" && pair[1] === "friend") gm = 1.0;
  else if(pair[0] === "enemy" && pair[1] === "neutral") gm = 0.5;
  else gm = 0.0;
  K.graha_maitri = {max:5, score: gm, groomLord: groom.lord, brideLord: bride.lord, relations: [r1, r2]};

  const gg = KOOTA.GANA[groom.nak], gb = KOOTA.GANA[bride.nak];
  K.gana = {max:6, score: KOOTA.GANA_SCORE[gg + "|" + gb], groom: gg, bride: gb};

  const relG = ((bride.sign - groom.sign) % 12 + 12) % 12 + 1;
  const relB = ((groom.sign - bride.sign) % 12 + 12) % 12 + 1;
  const pr = [relG, relB].sort((a,b) => a-b);
  const dosha = (pr[0] === 2 && pr[1] === 12) || (pr[0] === 5 && pr[1] === 9) || (pr[0] === 6 && pr[1] === 8);
  K.bhakoot = {max:7, score: dosha ? 0 : 7, dosha,
               moonSigns: [KOOTA.SIGNS[groom.sign], KOOTA.SIGNS[bride.sign]], positions: pr};

  const ng = KOOTA.NADI_PATTERN[groom.nakI % 6], nb = KOOTA.NADI_PATTERN[bride.nakI % 6];
  K.nadi = {max:8, score: ng === nb ? 0 : 8, groom: ng, bride: nb, dosha: ng === nb};

  const total = Object.keys(K).reduce((s, k) => s + K[k].score, 0);
  const sixKeys = ["varna","tara","graha_maitri","gana","bhakoot","nadi"];
  const six = sixKeys.reduce((s, k) => s + K[k].score, 0);
  const others = spread.map(v => six + K.yoni.score + v);
  return {kootas: K, groom, bride, total, outOf: 36, subtotalSix: six,
          range: [Math.min.apply(null, others), Math.max.apply(null, others)],
          band: total < 18 ? "below18" : total <= 24 ? "18to24" : total <= 32 ? "25to32" : "above32"};
}
