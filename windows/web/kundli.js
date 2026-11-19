/* The drawn kundli chart.
 *
 * A port of ChartDrawing.kt, deliberately keeping its geometry to the number: the same house positions, the
 * same tinted first house, the same two-planets-to-a-line stacking. A chart somebody has read for years
 * should not quietly move because it changed platforms.
 *
 * Drawn in a 100 x 100 viewBox so every coordinate here is the fraction the Kotlin uses, times one hundred.
 * The SVG scales to whatever box it is placed in.
 */

const SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];

const SIGNS_HI = ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या",
  "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"];

const ABBREV_EN = { Sun: "Su", Moon: "Mo", Mars: "Ma", Mercury: "Me", Jupiter: "Ju", Venus: "Ve", Saturn: "Sa", Rahu: "Ra", Ketu: "Ke" };
const ABBREV_HI = { Sun: "सू", Moon: "चं", Mars: "मं", Mercury: "बु", Jupiter: "गु", Venus: "शु", Saturn: "श", Rahu: "रा", Ketu: "के" };

/** Where each house's planets are written, house 1 first. Straight from NorthLayout.planetAt. */
const NORTH_PLANET_AT = [
  [50, 27], [25, 11], [11, 25], [27, 50], [11, 75], [25, 89],
  [50, 73], [75, 89], [89, 75], [73, 50], [89, 25], [75, 11],
];

/** Where each house's sign number goes: near the inner corner, as in printed kundlis. */
const NORTH_SIGN_AT = [
  [50, 44], [25, 19], [19, 25], [44, 51], [19, 76], [25, 83],
  [50, 57], [75, 83], [81, 76], [56, 51], [81, 25], [75, 19],
];

/** South Indian grid: signs are fixed, Aries at row 0 column 1, running clockwise. [row, column]. */
const SOUTH_CELL_OF_SIGN = [
  [0, 1], [0, 2], [0, 3], [1, 3], [2, 3], [3, 3],
  [3, 2], [3, 1], [3, 0], [2, 0], [1, 0], [0, 0],
];

const INK = "var(--ink)";
const MUTED = "var(--muted)";
const ACCENT_SOFT = "var(--accent-soft)";
const ACCENT_DEEP = "var(--accent-deep)";
const ACCENT = "var(--accent)";
const SURFACE = "var(--surface)";

const SVG_NS = "http://www.w3.org/2000/svg";

function svgEl(tag, attrs = {}, text = null) {
  const node = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, String(v));
  if (text !== null) node.textContent = text;
  return node;
}

function label(planet, lang) {
  const table = lang === "hi" ? ABBREV_HI : ABBREV_EN;
  const base = table[planet.name] || planet.name.slice(0, 2);
  // Rahu and Ketu always move backwards, so marking them would say nothing.
  const retro = planet.retrograde && planet.name !== "Rahu" && planet.name !== "Ketu";
  return retro ? base + (lang === "hi" ? "(व)" : "(R)") : base;
}

/** Planets two to a line, as the Android chart stacks them. */
function inPairs(labels) {
  const lines = [];
  for (let i = 0; i < labels.length; i += 2) lines.push(labels.slice(i, i + 2).join(" "));
  return lines;
}

function text(x, y, content, { size = 4.33, fill = INK, weight = 600, anchor = "middle" } = {}) {
  return svgEl("text", {
    x, y, "text-anchor": anchor, "dominant-baseline": "middle",
    "font-size": size, "font-weight": weight, fill,
  }, content);
}

/** The planets of a chart, by the house they sit in (1-12). */
function planetsByHouse(planets) {
  const byHouse = Object.fromEntries(Array.from({ length: 12 }, (_, i) => [i + 1, []]));
  for (const [name, p] of Object.entries(planets)) {
    if (byHouse[p.house]) byHouse[p.house].push({ name, ...p });
  }
  return byHouse;
}

/** The lagna's sign as an index 0-11.
 *
 * The engine gives planets a sign_index but gives the lagna only its name and longitude, so this is
 * worked out rather than read. Longitude first because it is language-proof; the name is the fallback.
 */
function lagnaSignIndex(lagna) {
  if (typeof lagna.sign_index === "number") return lagna.sign_index;
  if (typeof lagna.lon === "number") return Math.floor((lagna.lon % 360) / 30);
  const i = SIGNS.indexOf(lagna.sign);
  if (i < 0) throw new Error(`The chart's lagna has no sign this can place: ${JSON.stringify(lagna)}`);
  return i;
}

function planetsBySign(planets) {
  const bySign = Object.fromEntries(Array.from({ length: 12 }, (_, i) => [i, []]));
  for (const [name, p] of Object.entries(planets)) {
    if (bySign[p.sign_index]) bySign[p.sign_index].push({ name, ...p });
  }
  return bySign;
}

/* --- North Indian: houses fixed, signs rotate --------------------------------------------- */

function drawNorth(svg, vedic, lang) {
  const lagnaSign = lagnaSignIndex(vedic.lagna);
  const byHouse = planetsByHouse(vedic.planets);

  // House 1 is tinted, as in the printed form.
  svg.append(svgEl("path", { d: "M50 0 L75 25 L50 50 L25 25 Z", fill: ACCENT_SOFT }));

  const stroke = { stroke: INK, "stroke-width": 0.4, fill: "none" };
  svg.append(svgEl("rect", { x: 0, y: 0, width: 100, height: 100, ...stroke }));
  svg.append(svgEl("line", { x1: 0, y1: 0, x2: 100, y2: 100, ...stroke }));
  svg.append(svgEl("line", { x1: 100, y1: 0, x2: 0, y2: 100, ...stroke }));
  svg.append(svgEl("path", { d: "M50 0 L100 50 L50 100 L0 50 Z", ...stroke }));

  for (let h = 1; h <= 12; h++) {
    const [sx, sy] = NORTH_SIGN_AT[h - 1];
    const sign = (lagnaSign + h - 1) % 12;
    svg.append(text(sx, sy, String(sign + 1), { size: 3.67, fill: MUTED, weight: 400 }));

    const [px, py] = NORTH_PLANET_AT[h - 1];
    const lines = inPairs(byHouse[h].map((p) => label(p, lang)));
    const top = h === 1 ? 1 : 0;           // house 1 also carries the lagna label above its planets
    if (h === 1) {
      svg.append(text(px, py - lines.length * 2.75, lang === "hi" ? "लग्न" : "Asc", { fill: ACCENT_DEEP }));
    }
    lines.forEach((line, i) => {
      const dy = (i + top - (lines.length + top - 1) / 2) * 5.5;
      svg.append(text(px, py + dy, line));
    });
  }
}

/* --- South Indian: signs fixed, the lagna is marked ---------------------------------------- */

function drawSouth(svg, vedic, lang) {
  const c = 25;
  const lagnaSign = lagnaSignIndex(vedic.lagna);
  const bySign = planetsBySign(vedic.planets);
  const stroke = { stroke: INK, "stroke-width": 0.4, fill: "none" };

  svg.append(svgEl("rect", { x: 0, y: 0, width: 100, height: 100, ...stroke }));
  for (let i = 1; i <= 3; i++) {
    svg.append(svgEl("line", { x1: 0, y1: c * i, x2: 100, y2: c * i, ...stroke }));
    svg.append(svgEl("line", { x1: c * i, y1: 0, x2: c * i, y2: 100, ...stroke }));
  }
  // The centre is one empty box: paint over the inner lines.
  svg.append(svgEl("rect", { x: c, y: c, width: 2 * c, height: 2 * c, fill: SURFACE }));

  for (let sign = 0; sign < 12; sign++) {
    const [row, col] = SOUTH_CELL_OF_SIGN[sign];
    const x0 = col * c, y0 = row * c;

    if (sign === lagnaSign) {
      svg.append(svgEl("rect", { x: x0, y: y0, width: c, height: c, fill: ACCENT_SOFT }));
      svg.append(svgEl("rect", { x: x0, y: y0, width: c, height: c, ...stroke }));
      // The lagna mark: a diagonal across the top-right corner, clear of the sign name.
      svg.append(svgEl("line", {
        x1: x0 + c * 0.72, y1: y0, x2: x0 + c, y2: y0 + c * 0.28,
        stroke: ACCENT, "stroke-width": 0.5,
      }));
    }

    const names = lang === "hi" ? SIGNS_HI : SIGNS;
    svg.append(text(x0 + c * 0.06, y0 + c * 0.14, names[sign],
      { size: 3.33, fill: MUTED, weight: 400, anchor: "start" }));

    const labels = [];
    if (sign === lagnaSign) labels.push(lang === "hi" ? "लग्न" : "Asc");
    bySign[sign].forEach((p) => labels.push(label(p, lang)));

    inPairs(labels).forEach((line, i) => {
      svg.append(text(x0 + c / 2, y0 + c * (0.44 + 0.18 * i), line));
    });
  }
}

/* --- what the rest of the app calls -------------------------------------------------------- */

/** A sentence a screen reader can read instead of the picture. */
function chartDescription(vedic, lang) {
  const names = lang === "hi" ? SIGNS_HI : SIGNS;
  const byHouse = planetsByHouse(vedic.planets);
  const houseWord = lang === "hi" ? "भाव" : "House";
  const empty = lang === "hi" ? "कोई ग्रह नहीं" : "no planets";
  return Array.from({ length: 12 }, (_, i) => {
    const h = i + 1;
    const sign = names[(lagnaSignIndex(vedic.lagna) + i) % 12];
    const ps = byHouse[h].map((p) => p.name).join(", ") || empty;
    return `${houseWord} ${h}, ${sign}: ${ps}`;
  }).join(". ");
}

/** Build the chart as an <svg> element. style is "north" or "south". */
function kundliSvg(chart, { style = "north", lang = "en", size = 320 } = {}) {
  const vedic = chart.vedic;
  const svg = svgEl("svg", {
    viewBox: "0 0 100 100",
    width: size,
    height: size,
    role: "img",
    "aria-label": chartDescription(vedic, lang),
    class: "kundli",
  });
  (style === "south" ? drawSouth : drawNorth)(svg, vedic, lang);
  return svg;
}

/* --- divisional charts -------------------------------------------------------------------------
 *
 * A varga arrives as nothing but names - {Lagna: "Scorpio", Sun: "Gemini", ...} - because that is all a
 * divisional chart is: which sign each body falls into once the sign is divided. There are no degrees to
 * carry, so the drawing's shape has to be built here rather than read off the engine.
 *
 * The house number is the only thing worth working out: counted from the varga's own Lagna, not the
 * birth chart's, which is the whole point of looking at a varga at all.
 */
function vargaVedic(varga) {
  const lagnaSign = SIGNS.indexOf(varga.Lagna);
  if (lagnaSign < 0) {
    throw new Error(`This divisional chart has no Lagna sign to count from: ${JSON.stringify(varga.Lagna)}`);
  }
  const planets = {};
  for (const [name, sign] of Object.entries(varga)) {
    if (name === "Lagna") continue;
    const signIndex = SIGNS.indexOf(sign);
    if (signIndex < 0) continue;
    planets[name] = {
      sign,
      sign_index: signIndex,
      house: ((signIndex - lagnaSign + 12) % 12) + 1,
    };
  }
  return { lagna: { sign: varga.Lagna, sign_index: lagnaSign }, planets };
}

/** The same drawing as the birth chart, fed from a varga's sign names. */
function vargaSvg(varga, { style = "north", lang = "en", size = 300 } = {}) {
  return kundliSvg({ vedic: vargaVedic(varga) }, { style, lang, size });
}
