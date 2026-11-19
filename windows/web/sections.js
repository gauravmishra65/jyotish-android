/* Bilingual sections.
 *
 * Every chart already carries 66 of these - panchang, doshas, ashtakavarga, chara dasha, the lot -
 * each with a title, blocks and a note, and each with English and Hindi side by side. The engine did
 * the work; this file only lays them out. That is why the Windows build reached feature parity on
 * readings without a line of new astrology.
 *
 * A block is one of three shapes: a table with a head and rows, a list of lines, or a paragraph.
 */

/** Pick the language out of a {en, hi} pair. Falls back to English, which is always present. */
function bi(value, lang) {
  if (value === null || value === undefined) return "";
  if (typeof value === "string") return value;
  return value[lang] ?? value.en ?? "";
}

function sectionBlock(block, lang) {
  if (block.type === "table") {
    const head = (block.head || []).map((h) => el("th", {}, bi(h, lang)));
    const rows = (block.rows || []).map((row) =>
      el("tr", {}, ...row.map((cell, i) =>
        el(i === 0 ? "th" : "td", {}, bi(cell, lang)))));
    // Two columns read as label-and-value and get a fixed label width; three or more are a grid and
    // must share the room, or the last column wraps to one word a line.
    const columns = Math.max(head.length, ...(block.rows || []).map((r) => r.length), 0);
    return el("table", { className: columns > 2 ? "section-table wide" : "section-table" },
      head.length ? el("thead", {}, el("tr", {}, ...head)) : "",
      el("tbody", {}, ...rows));
  }
  if (block.type === "list") {
    return el("ul", { className: "section-list" },
      ...(block.items || []).map((item) => el("li", {}, bi(item, lang))));
  }
  return el("p", {}, bi(block.text ?? block, lang));
}

/** One section as a collapsible card. Collapsed by default: 66 of them open at once is a wall. */
function sectionCard(section, lang, { open = false } = {}) {
  const body = el("div", { className: "section-body" },
    section.intro ? el("p", { className: "section-intro" }, bi(section.intro, lang)) : "",
    ...(section.blocks || []).map((b) => sectionBlock(b, lang)),
    section.note ? el("p", { className: "section-note" }, bi(section.note, lang)) : "");

  const summary = el("summary", {}, bi(section.title, lang));
  const card = el("details", { className: "section" }, summary, body);
  if (open) card.setAttribute("open", "open");
  return card;
}

/** Everything a chart's details hold, with a search box over the titles. */
function sectionsPanel(sections, lang) {
  const list = el("div", { className: "sections" });
  const draw = (filter = "") => {
    const needle = filter.trim().toLowerCase();
    const shown = sections.filter((s) => !needle || bi(s.title, lang).toLowerCase().includes(needle));
    list.replaceChildren(
      ...(shown.length
        ? shown.map((s) => sectionCard(s, lang, { open: Boolean(needle) && shown.length <= 3 }))
        : [el("p", { className: "empty" }, t("no_match"))]),
    );
  };

  const search = el("input", {
    type: "search", placeholder: t("search_readings"), className: "section-search",
  });
  search.addEventListener("input", () => draw(search.value));
  draw();
  return el("div", {}, search, list);
}
