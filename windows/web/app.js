/* The interface.
 *
 * Everything it knows comes from pywebview.api, which is the Api object in api.py - there is no second
 * copy of any rule here. Every word it says of its own comes from strings.js, in English and Hindi.
 *
 * Deliberately plain JavaScript. A framework would be another thing to package and another thing to
 * learn when this is picked up again in six months.
 */

const api = () => window.pywebview.api;
const $ = (sel) => document.querySelector(sel);
const el = (tag, props = {}, ...kids) => {
  const node = Object.assign(document.createElement(tag), props);
  kids.flat().forEach((k) => node.append(k instanceof Node ? k : document.createTextNode(k)));
  return node;
};

let people = [];
let selectedId = null;
let screen = { name: "chart" };      // what to redraw when the language changes
let edition = { edition: "full", free_profiles: 1 };
let glossary = {};        // the engine's Hindi names for signs, planets, nakshatras and weekdays

/* The engine answers a chart in English names - Scorpio, Thursday, Pushya - whatever the language is
   set to, because those are the keys the rest of the engine counts on. The readings and the reports are
   translated inside the engine; the tables this page draws itself are not, so they are translated here.
   In English this returns what it was given, which is why it is safe to wrap everything in it. */
function hi(value, table) {
  if (lang() !== "hi" || value === null || value === undefined) return value ?? "—";
  const words = glossary[table] || {};
  return String(value).split(/([^A-Za-z]+)/)
    .map((part) => words[part] ?? part)
    .join("");
}

/* A chart gives the tithi as a number and its paksha as a word; the fifteen names belong to both
   halves of the month, so the number is read modulo fifteen. In English the number is what people
   recognise, so it is kept beside the name rather than replaced by it. */
function tithi(paksha, number) {
  if (!number) return "—";
  const half = lang() === "hi" ? (glossary.paksha || {})[paksha] ?? paksha : paksha;
  if (lang() !== "hi") return `${half ?? ""} ${number}`.trim();
  // Fourteen names serve both halves of the month; the fifteenth is the full moon in the bright half
  // and the new moon in the dark one, so it is named rather than numbered.
  const within = (Number(number) - 1) % 15;
  const name = within === 14
    ? (glossary.full_moon || {})[paksha]
    : (glossary.tithis || [])[within];
  return name ? (within === 14 ? name : `${half} ${name}`.trim()) : `${half ?? ""} ${number}`.trim();
}

/* --- the list of people ------------------------------------------------------------------- */

function drawPeople() {
  const list = $("#people");
  list.replaceChildren();
  $("#count").textContent = people.length === 1 ? t("people_one") : t("people_many", people.length);
  $("#new-person").textContent = t("add_person");

  if (people.length === 0) {
    list.append(el("div", { className: "empty" }, t("nobody_yet")));
    return;
  }
  for (const p of people) {
    const button = el(
      "button",
      { className: "person", onclick: () => showChart(p.id) },
      el("div", { className: "who" }, p.name),
      el("div", { className: "when" }, `${p.date} · ${p.time}`),
    );
    if (p.id === selectedId) button.setAttribute("aria-current", "true");
    list.append(button);
  }
}

/* The tools that are not about one person. Each is a screen of its own, and each knows how to redraw
   itself when the language changes - so this list is the one place a new tool has to be registered. */
const TOOLS = [
  { name: "today", label: "today", sub: "today_sub", open: () => showToday() },
  { name: "milan", label: "milan", sub: "milan_sub", open: () => showMilan() },
  { name: "compare", label: "compare", sub: "compare_sub", open: () => showCompare() },
  { name: "muhurta", label: "muhurta", sub: "muhurta_sub", open: () => showMuhurta() },
  { name: "numbers", label: "numbers", sub: "numbers_sub", open: () => showNumbers() },
  { name: "prashna", label: "prashna", sub: "prashna_sub", open: () => showPrashna() },
  { name: "chinese", label: "chinese", sub: "chinese_sub", open: () => showChinese() },
  { name: "settings", label: "settings", sub: "settings_sub", open: () => showSettings() },
];

function drawTools() {
  $("#tools").replaceChildren(...TOOLS.map((tool) => {
    const button = el("button", { className: "person tool", onclick: tool.open },
      el("div", { className: "who" }, t(tool.label)),
      el("div", { className: "when" }, t(tool.sub)));
    if (screen.name === tool.name) button.setAttribute("aria-current", "true");
    return button;
  }));
}

/* The language switch lives in the sidebar rather than behind a settings screen: it changes every word
   on the page, so it should be visible while you read them. The choice is remembered by Python. */
/* The sidebar says which edition this is, because a demo that does not say so is a trap: somebody
   would get as far as a second birth chart before finding out. */
function drawEdition() {
  const holder = $("#edition");
  if (edition.edition !== "demo") {
    holder.replaceChildren(edition.unlocked_to
      ? el("span", { className: "switch-label" }, t("unlocked_to", edition.unlocked_to))
      : "");
    return;
  }
  const n = edition.free_profiles;
  holder.replaceChildren(
    el("span", { className: "switch-label" }, n === 1 ? t("demo_one", n) : t("demo_many", n)),
    el("button", { className: "quiet unlock-link", onclick: () => showUnlock() }, t("unlock")));
}

function drawLanguageSwitch() {
  const holder = $("#language");
  const choose = async (which) => {
    if (which === lang()) return;
    setLang(await api().set_setting("language", which).then((s) => s.language));
    drawPeople();
    drawTools();
    drawEdition();
    drawLanguageSwitch();
    screen.redraw ? screen.redraw() : (selectedId ? showChart(selectedId) : showAddPerson());
  };
  holder.replaceChildren(
    el("span", { className: "switch-label" }, t("language")),
    el("div", { className: "switch" },
      el("button", { className: lang() === "en" ? "on" : "", onclick: () => choose("en") }, "English"),
      el("button", { className: lang() === "hi" ? "on" : "", onclick: () => choose("hi") }, "हिन्दी")),
  );
}

/* --- adding someone ----------------------------------------------------------------------- */

function field(label, name, attrs = {}) {
  const { wide, list, ...rest } = attrs;
  const input = el("input", Object.assign({ id: `f-${name}`, name }, rest));
  if (list) input.setAttribute("list", list);
  return el("div", { className: wide ? "field wide" : "field" }, el("label", { htmlFor: `f-${name}` }, label), input);
}

/* The time zone is the one field where a plausible-looking answer can be wrong: "Asia" is not a zone,
   "Asia/Kolkata" is. Offering the real list turns a typing problem into a picking one. */
async function timeZoneList() {
  const zones = await api().time_zones();
  return el("datalist", { id: "zones" }, ...zones.map((z) => el("option", { value: z })));
}

/* Birthplace.
 *
 * Typing a place searches about 70,000 settlements offline and fills in the three fields nobody should
 * have to look up: latitude, longitude and time zone. Those stay visible and editable, because a birth
 * certificate sometimes names a village the list does not have, and because showing the numbers is how
 * someone checks the right place was chosen.
 */
function placeField(existing, prefix = "f", label = t("birthplace")) {
  const input = el("input", {
    id: `${prefix}-place`, name: "place", autocomplete: "off",
    placeholder: t("place_hint"), value: existing?.place ?? "",
  });
  const results = el("div", { className: "results" });

  let token = 0;
  const run = async () => {
    const query = input.value.trim();
    const mine = ++token;
    if (query.length < 2) return results.replaceChildren();
    const found = await api().search_places(query, 8);
    if (mine !== token) return;                 // a later keystroke already answered
    results.replaceChildren(...found.map((place) =>
      el("button", {
        className: "result", type: "button",
        onclick: () => {
          input.value = place.label;
          $(`#${prefix}-lat`).value = place.lat;
          $(`#${prefix}-lon`).value = place.lon;
          $(`#${prefix}-tz`).value = place.tz;
          results.replaceChildren();
        },
      },
      el("span", { className: "result-name" }, place.label),
      el("span", { className: "result-where" }, `${place.lat.toFixed(3)}, ${place.lon.toFixed(3)} · ${place.tz}`))));
  };

  let typing;
  input.addEventListener("input", () => { clearTimeout(typing); typing = setTimeout(run, 120); });
  input.addEventListener("blur", () => setTimeout(() => results.replaceChildren(), 200));

  return el("div", { className: "field wide place-field" },
    el("label", { htmlFor: `${prefix}-place` }, label),
    input, results);
}

/* One form for both jobs. Passing an existing person fills it in and keeps their id, so saving edits
   them in place rather than making a second copy - which is what you want when a chart will not build
   because one field is wrong. */
function showAddPerson(existing = null) {
  const editing = Boolean(existing);
  selectedId = editing ? existing.id : null;
  screen = { name: "person", redraw: () => showAddPerson(existing) };
  drawPeople();
  drawTools();
  $("#main").replaceChildren(
    el("h2", {}, editing ? t("edit_person", existing.name) : t("add_person")),
    el("p", { className: "lede" }, t("data_note")),
    el(
      "div",
      { className: "fields" },
      field(t("name"), "name", { wide: true, placeholder: "Ravi Shankar Tiwari", value: existing?.name ?? "" }),
      field(t("date_of_birth"), "date", { placeholder: "1988-07-14", value: existing?.date ?? "" }),
      field(t("time_of_birth"), "time", { placeholder: "14:35", value: existing?.time ?? "" }),
      placeField(existing),
      field(t("latitude"), "lat", { placeholder: "25.3176", value: existing?.lat ?? "" }),
      field(t("longitude"), "lon", { placeholder: "82.9739", value: existing?.lon ?? "" }),
      field(t("time_zone"), "tz", { placeholder: "Asia/Kolkata", list: "zones", value: existing?.tz ?? "" }),
    ),
    el(
      "div",
      { className: "row" },
      el("button", { className: "primary", onclick: () => savePerson(existing) },
        editing ? t("save_rebuild") : t("save_build")),
      editing ? deleteButton(existing.id) : "",
      el("span", { id: "problem", className: "problem" }),
    ),
    el("p", { className: "note" }, t("place_note")),
  );
  timeZoneList().then((list) => {
    document.getElementById("zones")?.remove();
    document.body.append(list);
  });
  $("#f-name").focus();
}

async function savePerson(existing = null) {
  const person = existing ? { id: existing.id } : {};
  for (const name of ["name", "date", "time", "lat", "lon", "tz", "place"]) {
    person[name] = $(`#f-${name}`).value.trim();
  }
  $("#problem").textContent = "";
  try {
    const saved = await api().add_person(person);
    people = await api().people();
    edition = await api().edition();
    drawEdition();
    await showChart(saved.id);
  } catch (e) {
    // Python exceptions arrive as a rejected promise; the message is written for a person to read.
    const said = String(e.message || e);
    $("#problem").textContent = said.replace(/^.*(?:ValidationError|DemoLimit):\s*/s, "");
    // A demo limit is not a mistake to correct but a thing to buy, so the way out goes beside it.
    if (said.includes("DemoLimit")) {
      $("#problem").after(el("button", { className: "primary", onclick: () => showUnlock() }, t("unlock")));
    }
  }
}

/* --- a chart ------------------------------------------------------------------------------ */

function rows(pairs) {
  return el("table", {}, ...pairs.map(([k, v]) => el("tr", {}, el("th", {}, k), el("td", {}, v))));
}

function degrees(value) {
  return typeof value === "number" ? `${value.toFixed(2)}°` : String(value ?? "—");
}

function period(p) {
  return p.lord ? t("period", hi(p.lord, "planets"), p.start ?? "—", p.end ?? "—") : "—";
}

/* The sixteen divisional charts, one at a time.
 *
 * They come with the chart and cost nothing more to show, so the only question is how not to drown the
 * page in sixteen drawings. One drawing and a row of buttons: the same way an astrologer turns the page
 * of a printed kundli rather than laying all sixteen on the table at once.
 */
function vargaPanel(details, style) {
  const meta = details.varga_meta || [];
  if (!meta.length) return "";
  let chosen = meta[0].key;

  const holder = el("div", { className: "chart-holder" });
  const caption = el("p", { className: "note varga-use" });
  const buttons = el("div", { className: "row varga-row" });

  const draw = () => {
    const m = meta.find((x) => x.key === chosen);
    holder.replaceChildren(vargaSvg(details.vargas[chosen], { style, lang: lang(), size: 300 }));
    caption.textContent = `${m.name[lang()] ?? m.name.en} — ${t("varga_use", m.use[lang()] ?? m.use.en)}`;
    for (const b of buttons.children) b.className = b.dataset.key === chosen ? "primary" : "";
  };

  buttons.append(...meta.map((m) => {
    const b = el("button", {}, m.key);
    b.dataset.key = m.key;
    b.onclick = () => { chosen = m.key; draw(); };
    return b;
  }));

  const card = el("div", { className: "card chart-card varga-card" }, holder, caption, buttons);
  draw();
  return card;
}

/* Reports.
 *
 * The readings on screen are for looking something up; a report is for keeping. The engine writes the
 * whole thing as one self-contained HTML page, so it is saved to Documents and opened in the browser,
 * where Windows already knows how to print it to PDF. There is no viewer to build and no format to
 * invent - and the file still opens in ten years on a computer that has never heard of this app.
 */
function reportPanel(id) {
  const status = el("p", { className: "note report-status" });
  const buttons = el("div", { className: "row report-row" });
  let busy = false;

  const build = async (kind, name, button) => {
    if (busy) return;
    busy = true;
    button.classList.add("primary");
    status.replaceChildren(t("report_working", name));
    try {
      const saved = await api().make_report(id, kind);
      status.replaceChildren(
        el("span", {}, t("report_saved", saved.file) + " "),
        el("button", { className: "quiet link", onclick: () => api().open_path(saved.path) }, t("open_report")),
      );
    } catch (e) {
      status.replaceChildren(t("report_failed", String(e.message || e).replace(/^.*Error:\s*/s, "")));
    } finally {
      busy = false;
      button.classList.remove("primary");
    }
  };

  api().report_kinds().then((kinds) => {
    buttons.replaceChildren(...kinds.map((k) => {
      const name = k.name[lang()] ?? k.name.en;
      const button = el("button", {}, name);
      button.onclick = () => build(k.kind, name, button);
      return button;
    }));
  });

  return el("div", { className: "card report-card" },
    el("h3", {}, t("reports")), buttons, status, el("p", { className: "note" }, t("report_note")));
}

/* The outlook and the predictions, on the person they are about.
 *
 * Both are slow enough to be worth asking for rather than computing with every chart - three years of
 * timing windows takes a second and a half - so each is a button that fills its own card.
 */
function outlookPanel(id) {
  const result = el("div", { className: "outlook-result" });
  const go = el("button", { className: "primary" }, t("show_forecast"));
  go.onclick = async () => {
    result.replaceChildren(el("p", { className: "working" }, t("building")));
    try {
      const f = await api().forecast(id);
      result.replaceChildren(...(f.areas || []).map((area) => el("div", { className: "area" },
        el("h4", {}, bi(area.title, lang())),
        el("p", { className: "area-outlook" }, bi(area.outlook, lang())),
        el("p", { className: "note" }, bi(area.subtitle, lang())),
        el("table", { className: "section-table wide" }, el("tbody", {},
          ...(area.years || []).map((y) => el("tr", {},
            el("th", {}, `${y.from} – ${y.to}`),
            el("td", {}, bi(y.summary, lang())))))),
        ...(area.windows || []).map((w) => el("p", { className: "note" }, bi(w, lang()))))));
      if (f.method) result.append(el("p", { className: "note" }, bi(f.method, lang())));
    } catch (e) {
      result.replaceChildren(el("p", { className: "problem" },
        String(e.message || e).replace(/^.*Error:\s*/s, "")));
    }
  };
  return el("div", { className: "card" },
    el("h3", {}, t("forecast")), el("div", { className: "row" }, go), result);
}

function predictionPanel(id) {
  const result = el("div", { className: "outlook-result" });
  const buttons = el("div", { className: "row report-row" });

  const run = async (period, button) => {
    for (const b of buttons.children) b.className = b === button ? "primary" : "";
    result.replaceChildren(el("p", { className: "working" }, t("building")));
    try {
      const out = await api().predict(id, period);
      const dasha = out.dasha ? t("dasha_now", out.dasha.maha, out.dasha.antar) : "";
      result.replaceChildren(
        el("p", { className: "note" }, [bi(out.title, lang()), dasha].filter(Boolean).join(" · ")),
        ...(out.areas || []).map((area) => el("div", { className: "area" },
          el("h4", {}, `${bi(area.title, lang())} ${stars(area.stars)}`),
          el("p", {}, bi(area.reading, lang())))),
        out.note ? el("p", { className: "note" }, bi(out.note, lang())) : "");
    } catch (e) {
      result.replaceChildren(el("p", { className: "problem" },
        String(e.message || e).replace(/^.*Error:\s*/s, "")));
    }
  };

  api().periods().then((list) => buttons.replaceChildren(...list.map((k) => {
    const button = el("button", {}, k.name[lang()] ?? k.name.en);
    button.onclick = () => run(k.period, button);
    return button;
  })));

  return el("div", { className: "card" }, el("h3", {}, t("predictions")), buttons, result);
}

/* Out of five, as the Android app shows them. A filled star reads faster than "4/5" and does not
   pretend to a precision the reading does not have. */
function stars(n) {
  const filled = Math.max(0, Math.min(5, Number(n) || 0));
  return "★".repeat(filled) + "☆".repeat(5 - filled);
}

/* Life events, and checking a birth time against them.
 *
 * The answer is spans and probabilities, never a corrected time. A birth time is a fact about somebody's
 * life; the honest output is "these minutes explain your events better than the others", which a person
 * can weigh against what they were told. A screen that announced a new birth time would be claiming to
 * know something it does not.
 */
function timeCheckPanel(id) {
  const list = el("div", { className: "events" });
  const result = el("div", { className: "outlook-result" });
  let kinds = {};
  let events = [];

  const save = () => api().set_events(id, events);

  const draw = () => {
    list.replaceChildren(...events.map((event, i) => {
      const kind = el("select", {});
      kind.append(...Object.entries(kinds).map(([key, name]) =>
        el("option", { value: key, textContent: name[lang()] ?? name.en })));
      kind.value = event.kind || Object.keys(kinds)[0] || "";
      kind.onchange = () => { events[i].kind = kind.value; save(); };

      const when = el("input", { type: "text", placeholder: "2014-02-09", value: event.date || "" });
      when.onchange = () => { events[i].date = when.value.trim(); save(); };

      const drop = el("button", { className: "quiet" }, t("remove"));
      drop.onclick = () => { events.splice(i, 1); save(); draw(); };

      return el("div", { className: "event-row" }, kind, when, drop);
    }));
  };

  const add = el("button", {}, t("add_event"));
  add.onclick = () => { events.push({ kind: Object.keys(kinds)[0] || "", date: "" }); draw(); };

  const window_ = el("select", {});
  window_.append(...[30, 60, 120, 240].map((m) =>
    el("option", { value: String(m), textContent: t("minutes_either", m) })));
  window_.value = "60";

  const go = el("button", { className: "primary" }, t("check_time"));
  go.onclick = async () => {
    if (!events.some((e) => e.kind && e.date)) {
      result.replaceChildren(el("p", { className: "note" }, t("need_events")));
      return;
    }
    result.replaceChildren(el("p", { className: "working" }, t("checking")));
    try {
      await save();
      drawTimeCheck(result, await api().rectify(id, Number(window_.value)));
    } catch (e) {
      result.replaceChildren(el("p", { className: "problem" },
        String(e.message || e).replace(/^.*Error:\s*/s, "")));
    }
  };

  Promise.all([api().event_kinds(), api().events(id)]).then(([k, saved]) => {
    kinds = k;
    events = saved.length ? saved : [];
    draw();
  });

  return el("div", { className: "card" },
    el("h3", {}, t("time_check")),
    el("p", { className: "note" }, t("events_note")),
    list,
    el("div", { className: "row" }, add),
    el("div", { className: "fields" },
      el("div", { className: "field" }, el("label", {}, t("search_window")), window_)),
    el("div", { className: "row" }, go),
    result);
}

function drawTimeCheck(into, out) {
  const byFrom = Object.fromEntries((out.scored || []).map((s) => [s.from, s]));
  // Lowest chance first: the spans that explain the events least like a coincidence.
  const rows = [...(out.segments || [])]
    .sort((a, b) => (byFrom[a.from]?.p ?? 1) - (byFrom[b.from]?.p ?? 1))
    .map((seg) => {
      const score = byFrom[seg.from] || {};
      return el("tr", { className: seg.contains_recorded ? "recorded" : "" },
        el("th", {}, `${seg.from} – ${seg.to}${seg.contains_recorded ? ` · ${t("as_recorded")}` : ""}`),
        el("td", {}, [seg.lagna, seg.d9, seg.d10].filter(Boolean)
          .map((sign) => hi(sign, "signs")).join(" · ")),
        el("td", {}, String(score.hits ?? "—")),
        el("td", { className: "muted-cell" },
          score.p === undefined ? "—" : `${Math.round(score.p * 100)}%`));
    });

  into.replaceChildren(
    el("table", { className: "section-table wide" },
      el("thead", {}, el("tr", {},
        el("th", {}, t("span")), el("th", {}, t("lagna_d9_d10")),
        el("th", {}, t("events_fit")), el("th", {}, t("by_chance")))),
      el("tbody", {}, ...rows)),
    out.note ? el("p", { className: "note" }, bi(out.note, lang())) : "");
}

/* Notes: a box that saves itself. There is no Save button because there is nothing to decide - the
   text is the person's own and nobody wants to be asked whether they meant it. */
function notesPanel(id) {
  const box = el("textarea", { id: "notes", rows: 4, placeholder: "" });
  const saved = el("span", { className: "saved-note" });
  let pending;
  box.addEventListener("input", () => {
    clearTimeout(pending);
    pending = setTimeout(async () => {
      await api().set_notes(id, box.value);
      saved.textContent = t("saved");
      setTimeout(() => (saved.textContent = ""), 1500);
    }, 600);
  });
  api().notes(id).then((text) => (box.value = text || ""));
  return el("div", { className: "card" },
    el("h3", {}, t("notes")), box,
    el("p", { className: "note" }, t("notes_hint"), " ", saved));
}

function namesPanel(id) {
  const result = el("div", { className: "outlook-result" });
  const go = el("button", { className: "primary" }, t("show_names"));
  go.onclick = async () => {
    result.replaceChildren(el("p", { className: "working" }, t("building")));
    try {
      const n = await api().name_numbers(id);
      const suggestions = Array.isArray(n.suggestions) ? n.suggestions : [];
      result.replaceChildren(
        rows([[t("mulank"), `${n.mulank} · ${hi(n.mulank_planet, "planets")}`],
              [t("bhagyank"), `${n.bhagyank} · ${hi(n.bhagyank_planet, "planets")}`]]),
        n.original_already_fits || !suggestions.length
          ? el("p", { className: "note" }, t("already_fits"))
          : el("div", {},
              el("h4", { className: "panel-heading" }, t("spellings")),
              // The spelling and what it would cost to use it: a suggestion nobody can act on without
              // knowing how many letters change is not much of a suggestion.
              el("table", { className: "section-table wide" },
                el("thead", {}, el("tr", {},
                  el("th", {}, t("spelling")), el("th", {}, t("compound")),
                  el("th", {}, t("what_changes")))),
                el("tbody", {}, ...suggestions.slice(0, 8).map((sug) => el("tr", {},
                  el("th", {}, sug.spelling ?? ""),
                  el("td", {}, `${sug.chaldean_compound ?? ""} · ${sug.compound_class ?? ""}`.trim()),
                  el("td", { className: "muted-cell" }, (sug.changes || []).join(", "))))))),
        n.disclaimer ? el("p", { className: "note" }, bi(n.disclaimer, lang())) : "");
    } catch (e) {
      result.replaceChildren(el("p", { className: "problem" },
        String(e.message || e).replace(/^.*Error:\s*/s, "")));
    }
  };
  return el("div", { className: "card" },
    el("h3", {}, t("name_numbers")), el("div", { className: "row" }, go), result);
}

/* A divisional chart for any division, by either counting rule. The engine's own note says on the chart
   that a D7 counted this way is not the classical D7, and that note is shown rather than tidied away:
   the whole value of the tool is in knowing which one you are looking at. */
function customVargaPanel(id) {
  const result = el("div", { className: "outlook-result" });
  const n = el("input", { type: "number", min: "2", max: "300", value: "7", id: "cv-n" });
  const rule = el("select", { id: "cv-rule" });
  api().varga_rules().then((list) => rule.append(...list.map((r) =>
    el("option", { value: r.rule, textContent: r.name[lang()] ?? r.name.en }))));

  const go = el("button", { className: "primary" }, t("draw_varga"));
  go.onclick = async () => {
    result.replaceChildren(el("p", { className: "working" }, t("building")));
    try {
      const out = await api().custom_varga(id, Number(n.value), rule.value);
      const settings = await api().settings();
      result.replaceChildren(
        el("div", { className: "chart-holder" },
          vargaSvg(out.signs, { style: settings.chart_style === "south" ? "south" : "north",
                                lang: lang(), size: 300 })),
        sectionsPanel(out.sections || [], lang()));
    } catch (e) {
      result.replaceChildren(el("p", { className: "problem" },
        String(e.message || e).replace(/^.*Error:\s*/s, "")));
    }
  };

  return el("div", { className: "card" },
    el("h3", {}, t("custom_varga")),
    el("div", { className: "fields" },
      el("div", { className: "field" }, el("label", { htmlFor: "cv-n" }, t("division")), n),
      el("div", { className: "field" }, el("label", { htmlFor: "cv-rule" }, t("counting")), rule)),
    el("div", { className: "row" }, go), result);
}

async function showChart(id) {
  selectedId = id;
  screen = { name: "chart", redraw: () => showChart(id) };
  drawPeople();
  drawTools();
  const who = people.find((p) => p.id === id);
  $("#main").replaceChildren(
    el("h2", {}, who ? who.name : t("chart")),
    el("p", { className: "lede working" }, t("building")),
  );

  let chart;
  try {
    chart = await api().chart(id);
  } catch (e) {
    // A chart that will not build is exactly when someone needs to fix or remove the person, so this
    // branch must offer both. Without them a bad entry is stuck on screen with no way out.
    $("#main").replaceChildren(
      el("h2", {}, who ? who.name : t("chart")),
      el("p", { className: "problem" }, String(e.message || e).replace(/^.*ValidationError:\s*/s, "")),
      el("div", { className: "row" },
        who ? el("button", { className: "primary", onclick: () => showAddPerson(who) }, t("fix_details")) : "",
        who ? deleteButton(id) : ""),
    );
    return;
  }

  const v = chart.vedic;
  const moon = v.planets.Moon || {};
  const pan = v.panchang || {};
  const maha = v.dashas?.vimshottari?.current?.mahadasha || {};
  const antara = v.dashas?.vimshottari?.current?.antardasha || {};
  const details = chart.details || {};

  // The engine already formats degrees-minutes-seconds and the degree within the sign, so neither is
  // recomputed here: a second implementation is a second thing to get wrong.
  const planetRows = Object.entries(v.planets).map(([name, p]) =>
    el("tr", {}, el("th", {}, hi(name, "planets")),
      el("td", {}, `${hi(p.sign, "signs")} ${p.dms ?? degrees(p.deg_in_sign)}${p.retrograde ? " ℞" : ""}`)));

  const settings = await api().settings();
  const style = settings.chart_style === "south" ? "south" : "north";

  const styleButton = (which, label) => {
    const button = el("button", { className: which === style ? "primary" : "" }, label);
    button.onclick = async () => { await api().set_setting("chart_style", which); showChart(id); };
    return button;
  };

  $("#main").replaceChildren(
    el("h2", {}, who.name),
    el("p", { className: "lede" }, `${who.date} · ${who.time}${who.place ? " · " + who.place : ""}`),

    el("div", { className: "card chart-card" },
      el("div", { className: "chart-holder" }, kundliSvg(chart, { style, lang: lang(), size: 340 })),
      el("div", { className: "row" },
        styleButton("north", t("north_indian")), styleButton("south", t("south_indian")))),

    el("div", { className: "card" },
      el("h3", {}, t("the_chart")),
      rows([
        [t("lagna"), `${hi(v.lagna.sign, "signs")} ${v.lagna.dms ?? degrees(v.lagna.lon % 30)}`],
        [t("moon_sign"), hi(moon.sign, "signs")],
        [t("nakshatra"), moon.nakshatra
          ? `${hi(moon.nakshatra, "nakshatras")}${moon.pada ? ", " + t("pada", moon.pada) : ""}` : "—"],
        [t("sunrise"), pan.sunrise_local ?? "—"],
        [t("tithi"), tithi(pan.paksha, pan.tithi)],
        [t("vara"), hi(pan.vara, "weekdays")],
      ])),

    el("div", { className: "card" },
      el("h3", {}, t("dashas")),
      rows([[t("mahadasha"), period(maha)], [t("antardasha"), period(antara)]])),

    el("div", { className: "card" }, el("h3", {}, t("planets")), el("table", {}, ...planetRows)),
  );

  // The sixteen divisional charts, then the readings, then the way out. The buttons go last so that
  // scrolling to the end of a chart lands on them rather than on the middle of the readings.
  const main = $("#main");
  main.append(predictionPanel(id), outlookPanel(id), timeCheckPanel(id),
    namesPanel(id), customVargaPanel(id), notesPanel(id), reportPanel(id));
  if (details.varga_meta?.length) {
    main.append(el("h3", { className: "panel-heading" }, t("vargas")), vargaPanel(details, style));
  }
  if (Array.isArray(details.sections) && details.sections.length) {
    main.append(
      el("h3", { className: "panel-heading" }, t("readings", details.sections.length)),
      // A reading is only ever short because a part of it failed to build. Saying so beats leaving
      // somebody to notice that a section they remember is no longer there.
      details.incomplete?.length
        ? el("p", { className: "note" },
            t("details_incomplete", details.incomplete.map((m) => m.part).join(", ")))
        : "",
      sectionsPanel(details.sections, lang()));
  }
  main.append(el("div", { className: "row" },
    el("button", { onclick: () => showAddPerson(who) }, t("edit_details")),
    deleteButton(id)));
}

/* Deleting asks first, but in the page rather than through window.confirm: a native dialog depends on
   what the embedded browser allows, and a confirmation that silently answers "no" would look exactly
   like a delete button that does nothing. The button becomes its own confirmation instead. */
function deleteButton(id, label = t("delete_person")) {
  const button = el("button", { className: "quiet" }, label);
  button.onclick = () => {
    if (button.dataset.armed) return removePerson(id);
    button.dataset.armed = "1";
    button.textContent = t("delete_again");
    setTimeout(() => {
      if (!button.isConnected) return;
      delete button.dataset.armed;
      button.textContent = label;
    }, 5000);
  };
  return button;
}

async function removePerson(id) {
  await api().delete_person(id);
  people = await api().people();
  edition = await api().edition();
  drawEdition();
  glossary = await api().glossary();
  selectedId = null;
  people.length ? showChart(people[0].id) : showAddPerson();
}

/* --- Kundli Milan ------------------------------------------------------------------------- */

const KOOTAS = ["varna", "vashya", "tara", "yoni", "graha_maitri", "gana", "bhakoot", "nadi"];

/* Which of the two is the bride is not a detail: several kootas are counted from the bride's Moon to
   the groom's and not the other way round. So the two fields are labelled, not merely first and second,
   and swapping them is a visible act rather than something the screen decides. */
function showMilan() {
  screen = { name: "milan", redraw: () => showMilan() };
  selectedId = null;
  drawPeople();
  drawTools();

  const main = $("#main");
  main.replaceChildren(el("h2", {}, t("milan")), el("p", { className: "lede" }, t("milan_sub")));

  if (people.length < 2) {
    main.append(el("p", { className: "note" }, t("need_two")),
      el("div", { className: "row" },
        el("button", { className: "primary", onclick: () => showAddPerson() }, t("add_person"))));
    return;
  }

  const chooser = (id, label, preferred) => {
    const select = el("select", { id });
    select.append(...people.map((p) => el("option", { value: p.id, textContent: p.name })));
    select.value = preferred;
    return el("div", { className: "field" }, el("label", { htmlFor: id }, label), select);
  };

  const result = el("div", { id: "milan-result" });
  const go = el("button", { className: "primary" }, t("match_now"));
  go.onclick = async () => {
    const groom = $("#m-groom").value;
    const bride = $("#m-bride").value;
    if (groom === bride) {
      result.replaceChildren(el("p", { className: "problem" }, t("same_person")));
      return;
    }
    result.replaceChildren(el("p", { className: "working" }, t("matching")));
    try {
      drawMatch(result, await api().match(groom, bride));
    } catch (e) {
      result.replaceChildren(el("p", { className: "problem" },
        t("match_failed", String(e.message || e).replace(/^.*Error:\s*/s, ""))));
    }
  };

  main.append(
    el("div", { className: "fields" },
      chooser("m-groom", t("groom"), people[0].id),
      chooser("m-bride", t("bride"), people[1].id)),
    el("div", { className: "row" }, go),
    result,
  );
}

/* The South Indian side of the same question. It is not a score out of anything: each porutham either
   agrees or it does not, six of them are the ones Tamil practice treats as essential, and the engine's
   own note is shown because it says the important part - a missing Rajju is not a prediction about
   anybody's life. */
function poruthamCard(porutham) {
  const items = porutham?.items;
  if (!items) return "";
  const essential = porutham.essential || {};

  const rows = Object.entries(items).map(([key, item]) => el("tr", {},
    el("th", {}, `${t(`p_${key}`)}${key in essential ? ` · ${t("essential")}` : ""}`),
    el("td", {}, item.ok ? "✓" : "·"),
    el("td", { className: "muted-cell" }, item.rule ?? "")));

  const allEssential = Object.keys(essential).length > 0
    && Object.values(essential).every(Boolean);

  return el("div", { className: "card" },
    el("h3", {}, t("porutham")),
    el("p", {}, t("porutham_agree", porutham.agree ?? 0, porutham.out_of ?? rows.length)),
    el("p", { className: "note" },
      allEssential ? t("porutham_essential") : t("porutham_essential_not")),
    el("table", { className: "section-table wide" }, el("tbody", {}, ...rows)),
    porutham.note ? el("p", { className: "note" }, porutham.note) : "");
}

function drawMatch(into, m) {
  const ak = m.ashtakoota || {};
  const total = ak.total_36 || {};
  const kootas = ak.kootas || {};
  const names = m.people || [];

  const kootaRows = KOOTAS.filter((k) => kootas[k]).map((k) => {
    const koota = kootas[k];
    const detail = [koota.groom, koota.bride].filter(Boolean).join(" · ") || koota.status || "";
    return el("tr", {},
      el("th", {}, t(`koota_${k}`)),
      el("td", {}, t("score_of", koota.score, koota.max)),
      el("td", { className: "muted-cell" }, detail));
  });

  const porutham = poruthamCard(ak.porutham);
  const mangal = m.mangal_comparison || {};
  const mangalRows = names.filter((n) => mangal[n]).map((n) => el("tr", {},
    el("th", {}, n),
    el("td", {}, [["from_lagna", mangal[n].from_lagna], ["from_moon", mangal[n].from_moon],
                  ["from_venus", mangal[n].from_venus]]
      .map(([key, house]) => `${t(key)}: ${t("house_n", house)}`).join(" · "))));

  into.replaceChildren(
    el("div", { className: "card score-card" },
      el("div", { className: "score" }, `${total.score ?? "—"} / ${total.out_of ?? 36}`),
      el("div", { className: "score-band" }, total.band ?? ""),
      el("div", { className: "score-who" }, names.join("  ·  "))),

    el("div", { className: "card" },
      el("h3", {}, t("eight_kootas")),
      el("table", {},
        el("thead", {}, el("tr", {}, el("th", {}, t("koota")), el("th", {}, t("points")), el("th", {}, ""))),
        el("tbody", {}, ...kootaRows))),

    porutham,

    mangalRows.length
      ? el("div", { className: "card" }, el("h3", {}, t("mangal_compare")), el("table", {}, ...mangalRows))
      : "",

    el("p", { className: "note" }, t("milan_note")),
  );

  if (Array.isArray(m.sections) && m.sections.length) {
    into.append(el("h3", { className: "panel-heading" }, t("readings", m.sections.length)),
      sectionsPanel(m.sections, lang()));
  }
}

/* --- Muhurta ------------------------------------------------------------------------------ */

/* A screen with four questions and one answer. The people are optional and the note says why they
   matter: Tarabala and Chandrabala are counted from each person's own Moon, so naming the couple can
   take a fortnight of windows down to none - which is a true answer, not a broken screen, and the
   empty state says so rather than showing nothing. */
function showMuhurta() {
  screen = { name: "muhurta", redraw: () => showMuhurta() };
  selectedId = null;
  drawPeople();
  drawTools();

  const today = new Date();
  const iso = (d) => d.toISOString().slice(0, 10);
  const later = new Date(today.getTime() + 30 * 86400000);

  const events = el("select", { id: "mu-event" });
  api().muhurta_events().then((list) => events.append(
    ...list.map((e) => el("option", { value: e.event, textContent: e.name[lang()] ?? e.name.en }))));

  const chosen = new Set();
  const peopleBoxes = el("div", { className: "checks" }, ...people.map((p) => {
    const box = el("input", { type: "checkbox", id: `mu-p-${p.id}` });
    box.onchange = () => (box.checked ? chosen.add(p.id) : chosen.delete(p.id));
    return el("label", { className: "check", htmlFor: `mu-p-${p.id}` }, box, el("span", {}, p.name));
  }));

  const result = el("div", { id: "muhurta-result" });
  const go = el("button", { className: "primary" }, t("find_times"));
  go.onclick = async () => {
    result.replaceChildren(el("p", { className: "working" }, t("searching")));
    try {
      const found = await api().muhurta({
        event: $("#mu-event").value,
        from: $("#mu-from").value.trim(),
        to: $("#mu-to").value.trim(),
        lat: $("#mu-lat").value.trim(),
        lon: $("#mu-lon").value.trim(),
        tz: $("#mu-tz").value.trim(),
        people: [...chosen],
      });
      drawMuhurta(result, found);
    } catch (e) {
      result.replaceChildren(el("p", { className: "problem" },
        String(e.message || e).replace(/^.*Error:\s*/s, "")));
    }
  };

  $("#main").replaceChildren(
    el("h2", {}, t("muhurta")),
    el("p", { className: "lede" }, t("muhurta_sub")),
    el("div", { className: "fields" },
      el("div", { className: "field" }, el("label", { htmlFor: "mu-event" }, t("what_for")), events),
      el("div", { className: "field" }),
      field(t("from_date"), "from", { value: iso(today) }),
      field(t("to_date"), "to", { value: iso(later) }),
      placeField(null, "mu", t("where")),
      field(t("latitude"), "lat", { placeholder: "25.3176" }),
      field(t("longitude"), "lon", { placeholder: "82.9739" }),
      field(t("time_zone"), "tz", { placeholder: "Asia/Kolkata", list: "zones" })),
    people.length
      ? el("div", { className: "card" },
          el("h3", {}, t("who_involved")), peopleBoxes,
          el("p", { className: "note" }, t("who_involved_note")))
      : "",
    el("div", { className: "row" }, go),
    result,
  );
  // The muhurta form uses the same ids with its own prefix, so its fields are mu-from, mu-lat and so on.
  for (const name of ["from", "to", "lat", "lon", "tz"]) {
    const input = $(`#f-${name}`);
    input.id = `mu-${name}`;
    input.previousElementSibling.htmlFor = `mu-${name}`;
  }
  timeZoneList().then((list) => {
    document.getElementById("zones")?.remove();
    document.body.append(list);
  });
}

function drawMuhurta(into, found) {
  const windows = found.all_windows || [];
  if (!windows.length) {
    into.replaceChildren(el("p", { className: "note" }, t("no_windows", found.event_label || "")));
    return;
  }
  const pick = (w, key) => (lang() === "hi" && w[`${key}_hi`]) || w[key];
  const list = (items) => items.join("; ");

  into.replaceChildren(
    el("h3", { className: "panel-heading" }, t("windows_found", windows.length)),
    el("div", { className: "card" },
      el("table", { className: "section-table wide" },
        el("thead", {}, el("tr", {},
          el("th", {}, t("window_when")), el("th", {}, t("window_detail")),
          el("th", {}, t("supports")), el("th", {}, t("weaknesses")))),
        el("tbody", {}, ...windows.map((w) => el("tr", {},
          el("th", {}, `${w.start_local} – ${w.end_local.slice(11)} · ${t("minutes_n", w.minutes)}`),
          el("td", {}, [hi(pick(w, "weekday"), "weekdays"), hi(pick(w, "nakshatra"), "nakshatras"),
                        hi(pick(w, "lagna"), "signs")].join(" · ")),
          el("td", { className: "muted-cell" }, list(pick(w, "supports") || [])),
          el("td", { className: "muted-cell" }, list(pick(w, "weaknesses") || []))))))),
    found.disclaimer ? el("p", { className: "note" }, found.disclaimer) : "",
  );
}

/* --- numerology --------------------------------------------------------------------------- */

function showNumbers() {
  screen = { name: "numbers", redraw: () => showNumbers() };
  selectedId = null;
  drawPeople();
  drawTools();

  const main = $("#main");
  main.replaceChildren(el("h2", {}, t("numbers")), el("p", { className: "lede" }, t("numbers_sub")));
  if (!people.length) {
    main.append(el("p", { className: "note" }, t("nobody_yet")),
      el("div", { className: "row" },
        el("button", { className: "primary", onclick: () => showAddPerson() }, t("add_person"))));
    return;
  }

  const result = el("div", { id: "numbers-result" });
  const tools = el("select", { id: "n-kind" });
  const person = el("select", { id: "n-person" });
  person.append(...people.map((p) => el("option", { value: p.id, textContent: p.name })));
  const other = el("select", { id: "n-other" });
  other.append(...people.map((p) => el("option", { value: p.id, textContent: p.name })));
  if (people.length > 1) other.value = people[1].id;

  const otherField = el("div", { className: "field" }, el("label", { htmlFor: "n-other" }, t("second_person")), other);
  const textField = field(t("the_text"), "n-text", { placeholder: "9876543210" });

  // Each tool asks for different things, so the form shows only what the chosen one needs.
  const fit = (needs, kind) => {
    otherField.style.display = kind === "pair" ? "" : "none";
    textField.style.display = needs.includes("text") ? "" : "none";
  };

  api().number_tools().then((list) => {
    tools.append(...list.map((k) => el("option", { value: k.kind, textContent: k.name[lang()] ?? k.name.en })));
    const byKind = Object.fromEntries(list.map((k) => [k.kind, k.needs]));
    fit(byKind[tools.value] || [], tools.value);
    tools.onchange = () => fit(byKind[tools.value] || [], tools.value);
  });

  const go = el("button", { className: "primary" }, t("look"));
  go.onclick = async () => {
    result.replaceChildren(el("p", { className: "working" }, t("matching")));
    try {
      const out = await api().numbers({
        kind: tools.value, person_id: person.value,
        other_id: other.value, text: $("#f-n-text").value.trim(),
      });
      result.replaceChildren(sectionsPanel(out.sections || [], lang()));
    } catch (e) {
      result.replaceChildren(el("p", { className: "problem" },
        String(e.message || e).replace(/^.*Error:\s*/s, "")));
    }
  };

  main.append(
    el("div", { className: "fields" },
      el("div", { className: "field" }, el("label", { htmlFor: "n-kind" }, t("tool")), tools),
      el("div", { className: "field" }, el("label", { htmlFor: "n-person" }, t("person")), person),
      otherField, textField),
    el("div", { className: "row" }, go),
    result,
  );
}

/* --- the Chinese side --------------------------------------------------------------------- */

/* Eleven sections, all of them already written by the engine in both languages, so this screen is a
   person chooser and nothing else. */
function showChinese() {
  screen = { name: "chinese", redraw: () => showChinese() };
  selectedId = null;
  drawPeople();
  drawTools();

  const main = $("#main");
  main.replaceChildren(el("h2", {}, t("chinese")), el("p", { className: "lede" }, t("chinese_sub")));
  if (!people.length) {
    main.append(el("p", { className: "note" }, t("nobody_yet")),
      el("div", { className: "row" },
        el("button", { className: "primary", onclick: () => showAddPerson() }, t("add_person"))));
    return;
  }

  const result = el("div", { id: "chinese-result" });
  const person = el("select", { id: "c-person" });
  person.append(...people.map((p) => el("option", { value: p.id, textContent: p.name })));

  const run = async () => {
    result.replaceChildren(el("p", { className: "working" }, t("building")));
    try {
      // The Flying Stars are not about a birth chart at all - they are about the year and the month -
      // but they belong to the same tradition, and a screen of their own for one section would be a
      // menu entry that nobody would ever look for.
      const [out, stars] = await Promise.all([api().chinese(person.value), api().flying_stars()]);
      result.replaceChildren(
        sectionsPanel(out.sections || [], lang()),
        (stars.sections || []).length
          ? el("div", {}, el("h3", { className: "panel-heading" }, t("flying_stars")),
              sectionsPanel(stars.sections, lang()))
          : "");
    } catch (e) {
      result.replaceChildren(el("p", { className: "problem" },
        String(e.message || e).replace(/^.*Error:\s*/s, "")));
    }
  };
  person.onchange = run;

  main.append(
    el("div", { className: "fields" },
      el("div", { className: "field" }, el("label", { htmlFor: "c-person" }, t("person")), person)),
    result,
  );
  run();
}

/* --- today -------------------------------------------------------------------------------- */

/* The panchang is read from where somebody is now, not from where they were born - sunrise, the
   choghadiya and rahu kalam are all local to the morning they are standing in. The place is remembered
   once, and until it is chosen the first saved person's birthplace stands in, so the screen shows
   something true rather than an empty form. */
async function showToday() {
  screen = { name: "today", redraw: () => showToday() };
  selectedId = null;
  drawPeople();
  drawTools();

  const main = $("#main");
  main.replaceChildren(el("h2", {}, t("today")), el("p", { className: "lede" }, t("today_sub")));

  const where = await api().today_place();
  if (!where || !where.tz) return main.append(todayPlaceForm(null));

  let day;
  try {
    day = await api().today();
  } catch (e) {
    return main.append(el("p", { className: "problem" },
      String(e.message || e).replace(/^.*Error:\s*/s, "")), todayPlaceForm(where));
  }

  const p = day.panchang || {};
  const periods = day.periods || {};
  const span = (x) => (x && x.from ? `${x.from} – ${x.to}` : "—");

  /* Some panchang limbs arrive as {en, hi} and others as {name: {en, hi}, ends}, because the ones that
     change during the day carry the time they change at. One reader for both, with the time when there
     is one - "until 06:40" is the part anybody planning a day actually needs. */
  const limb = (x) => {
    if (!x) return "—";
    const name = bi(x.name ?? x, lang());
    return name ? (x.ends ? `${name} (→ ${x.ends})` : name) : "—";
  };

  main.append(
    el("p", { className: "note" }, t("today_where", `${where.place || day.place || ""} · ${day.date}`.trim()),
      " ", el("button", { className: "quiet link", onclick: () => showTodayPlace(where) }, t("change_place"))),

    el("div", { className: "card" },
      el("h3", {}, t("panchang")),
      rows([
        [t("weekday"), `${bi(p.weekday, lang())}${p.weekday_lord ? " · " + bi(p.weekday_lord, lang()) : ""}`],
        [t("tithi"), p.tithi ? `${bi(p.tithi.paksha, lang())} ${limb(p.tithi)}`.trim() : "—"],
        [t("nakshatra"), limb(p.nakshatra)],
        [t("yoga"), limb(p.yoga)],
        [t("karana"), limb(p.karana)],
        [t("moon_sign"), bi(p.moon_sign, lang()) || "—"],
        [t("sun_sign"), bi(p.sun_sign, lang()) || "—"],
        [t("lunar_month"), [bi(p.month_amanta, lang()), bi(p.month_purnimanta, lang())]
          .filter(Boolean).filter((v, i, all) => all.indexOf(v) === i).join(" · ") || "—"],
        [t("samvat"), [p.vikram_samvat, p.shaka_samvat].filter(Boolean).join(" · ") || "—"],
      ])),

    el("div", { className: "card" },
      el("h3", {}, t("sun_moon")),
      rows([
        [t("sunrise_set"), `${day.sun?.rise ?? "—"} · ${day.sun?.set ?? "—"}`],
        [t("moonrise_set"), `${day.moon?.rise ?? "—"} · ${day.moon?.set ?? "—"}`],
      ])),

    el("div", { className: "card" },
      el("h3", {}, t("periods_good")),
      rows([[t("abhijit"), span(periods.abhijit)], [t("brahma_muhurta"), span(periods.brahma_muhurta)]])),

    el("div", { className: "card" },
      el("h3", {}, t("periods_avoid")),
      rows([[t("rahu_kalam"), span(periods.rahu_kalam)], [t("yamaganda"), span(periods.yamaganda)],
            [t("gulika_kalam"), span(periods.gulika_kalam)]])),

    choghadiyaCard(periods),

    (day.festivals || []).length
      ? el("div", { className: "card" }, el("h3", {}, t("festivals")),
          el("table", {}, ...day.festivals.slice(0, 10).map((f) =>
            el("tr", {}, el("th", {}, f.date), el("td", {}, bi(f.name, lang()))))))
      : "",

    day.conventions ? el("p", { className: "note" }, bi(day.conventions, lang())) : "",
  );
}

/* Sixteen slots, day and night. A table rather than a list: what anybody wants from the choghadiya is
   "which of these am I in now", and that is a question you answer by scanning a column. */
function choghadiyaCard(periods) {
  const slots = (list, label) => (list || []).map((c) => el("tr", {},
    el("th", {}, `${c.from} – ${c.to}`),
    el("td", {}, c.name),
    el("td", { className: "muted-cell" }, `${label} · ${c.kind ?? ""}`.trim())));

  const day = slots(periods.choghadiya_day, t("by_day"));
  const night = slots(periods.choghadiya_night, t("by_night"));
  if (!day.length && !night.length) return "";
  return el("div", { className: "card" },
    el("h3", {}, t("choghadiya")),
    el("table", { className: "section-table wide" }, el("tbody", {}, ...day, ...night)));
}

function todayPlaceForm(where) {
  const card = el("div", { className: "card" },
    el("p", { className: "note" }, t("set_place_first")),
    el("div", { className: "fields" },
      placeField(where, "td", t("where")),
      field(t("latitude"), "lat", { value: where?.lat ?? "" }),
      field(t("longitude"), "lon", { value: where?.lon ?? "" }),
      field(t("time_zone"), "tz", { list: "zones", value: where?.tz ?? "" })));

  const go = el("button", { className: "primary" }, t("saved").length ? t("change_place") : "");
  go.textContent = t("change_place");
  go.onclick = async () => {
    try {
      await api().set_today_place({
        place: $("#td-place").value.trim(), lat: $("#td-lat").value.trim(),
        lon: $("#td-lon").value.trim(), tz: $("#td-tz").value.trim(),
      });
      showToday();
    } catch (e) {
      card.append(el("p", { className: "problem" }, String(e.message || e).replace(/^.*Error:\s*/s, "")));
    }
  };
  card.append(el("div", { className: "row" }, go));
  // The three fields share their ids with the birth form, so they are renamed once in place.
  queueMicrotask(() => {
    for (const name of ["lat", "lon", "tz"]) {
      const input = card.querySelector(`#f-${name}`);
      if (!input) continue;
      input.id = `td-${name}`;
      input.previousElementSibling.htmlFor = `td-${name}`;
    }
  });
  timeZoneList().then((list) => {
    document.getElementById("zones")?.remove();
    document.body.append(list);
  });
  return card;
}

function showTodayPlace(where) {
  screen = { name: "today", redraw: () => showTodayPlace(where) };
  $("#main").replaceChildren(
    el("h2", {}, t("today")), el("p", { className: "lede" }, t("today_sub")), todayPlaceForm(where));
}

/* --- Prashna ------------------------------------------------------------------------------ */

function showPrashna() {
  screen = { name: "prashna", redraw: () => showPrashna() };
  selectedId = null;
  drawPeople();
  drawTools();

  const question = el("input", { id: "q-text", placeholder: "…" });
  const method = el("select", { id: "q-method" });
  method.append(el("option", { value: "prashna", textContent: t("method_prashna") }),
                el("option", { value: "kp", textContent: t("method_kp") }),
                el("option", { value: "horary", textContent: t("method_horary") }));
  const number = el("input", { id: "q-number", type: "number", min: "1", max: "249", value: "" });
  const numberField = el("div", { className: "field" },
    el("label", { htmlFor: "q-number" }, t("kp_number")), number);
  numberField.style.display = "none";
  method.onchange = () => (numberField.style.display = method.value === "kp" ? "" : "none");

  const result = el("div", { id: "prashna-result" });
  const go = el("button", { className: "primary" }, t("ask_now"));
  go.onclick = async () => {
    result.replaceChildren(el("p", { className: "working" }, t("building")));
    try {
      // Western horary answers in the same bilingual blocks as everything else, so it needs no drawing
      // of its own - only a different question of the engine.
      if (method.value === "horary") {
        const answer = await api().horary(question.value);
        result.replaceChildren(sectionsPanel(answer.sections || [], lang()));
        return;
      }
      drawPrashna(result, await api().ask_question({
        method: method.value, question: question.value, number: number.value,
      }));
    } catch (e) {
      result.replaceChildren(el("p", { className: "problem" },
        String(e.message || e).replace(/^.*Error:\s*/s, "")));
    }
  };

  $("#main").replaceChildren(
    el("h2", {}, t("prashna")),
    el("p", { className: "lede" }, t("prashna_sub")),
    el("div", { className: "fields" },
      el("div", { className: "field wide" }, el("label", { htmlFor: "q-text" }, t("the_question")), question),
      el("div", { className: "field" }, el("label", { htmlFor: "q-method" }, t("method")), method),
      numberField),
    el("div", { className: "row" }, go),
    result,
  );
  question.focus();
}

/* The engine's three words for which way a prashna leans, and nothing else. It says "against", not
   "unfavourable" - and a map that guessed the wrong word did not fail, it quietly showed an
   unfavourable answer as "mixed", which is a wrong answer to a yes-or-no question rather than a
   cosmetic slip. LEANS is checked against the engine's own vocabulary by a test. */
const LEANS = { favourable: "lean_favourable", against: "lean_against", mixed: "lean_mixed" };

function drawPrashna(into, answer) {
  const lean = LEANS[answer.lean] || "lean_mixed";
  into.replaceChildren(
    el("div", { className: "card score-card" },
      el("div", { className: "score-band" }, t(lean)),
      el("div", { className: "score-who" },
        t("checks_passed", answer.favourable ?? 0, answer.out_of ?? (answer.checks || []).length))),
    el("div", { className: "card" },
      el("h3", {}, t("the_chart")),
      rows([
        [t("lagna"), `${hi(answer.lagna, "signs")}`
          + (answer.lagna_lord ? " · " + hi(answer.lagna_lord, "planets") : "")],
        [t("moon_sign"), hi(answer.moon_sign, "signs")],
        ["", answer.asked_at ?? ""],
      ])),
    (answer.checks || []).length
      ? el("div", { className: "card" },
          el("table", { className: "section-table wide" }, el("tbody", {},
            ...answer.checks.map((c) => el("tr", {},
              el("th", {}, c.ok ? "✓" : "·"),
              el("td", {}, bi(c.text, lang())))))))
      : "",
    el("p", { className: "note" }, t("prashna_note")),
    answer.note ? el("p", { className: "note" }, bi(answer.note, lang())) : "",
  );
}

/* --- comparing several people ------------------------------------------------------------- */

function showCompare() {
  screen = { name: "compare", redraw: () => showCompare() };
  selectedId = null;
  drawPeople();
  drawTools();

  const main = $("#main");
  main.replaceChildren(el("h2", {}, t("compare")), el("p", { className: "lede" }, t("compare_sub")));
  if (people.length < 2) {
    main.append(el("p", { className: "note" }, t("need_two")),
      el("div", { className: "row" },
        el("button", { className: "primary", onclick: () => showAddPerson() }, t("add_person"))));
    return;
  }

  const chosen = new Set(people.slice(0, 2).map((p) => p.id));
  const boxes = el("div", { className: "checks" }, ...people.map((p) => {
    const box = el("input", { type: "checkbox", id: `cmp-${p.id}`, checked: chosen.has(p.id) });
    box.onchange = () => (box.checked ? chosen.add(p.id) : chosen.delete(p.id));
    return el("label", { className: "check", htmlFor: `cmp-${p.id}` }, box, el("span", {}, p.name));
  }));

  const result = el("div", { id: "compare-result" });
  const go = el("button", { className: "primary" }, t("compare_now"));
  go.onclick = async () => {
    result.replaceChildren(el("p", { className: "working" }, t("matching")));
    try {
      const out = await api().compare_group([...chosen]);
      result.replaceChildren(sectionsPanel(out.sections || [], lang()));
    } catch (e) {
      result.replaceChildren(el("p", { className: "problem" },
        String(e.message || e).replace(/^.*Error:\s*/s, "")));
    }
  };

  main.append(
    el("div", { className: "card" }, el("h3", {}, t("choose_people")), boxes),
    el("div", { className: "row" }, go),
    result,
  );
}

/* --- settings ----------------------------------------------------------------------------- */

/* Which values a setting may take is Python's business, not this screen's: an ayanamsa the engine does
   not know would break every chart from then on, including after a restart, with nothing on screen to
   say why. So the options are fetched and the save is checked at the other end. */
async function showSettings(openWith = null) {
  screen = { name: "settings", redraw: () => showSettings() };
  selectedId = null;
  drawPeople();
  drawTools();

  const main = $("#main");
  main.replaceChildren(el("h2", {}, t("settings")), el("p", { className: "lede" }, t("settings_sub")));

  const [choices, settings, about] = await Promise.all([
    api().setting_choices(), api().settings(), api().about(),
  ]);
  const byKey = Object.fromEntries(choices.map((c) => [c.key, c.options]));

  const note = el("span", { className: "saved-note" });
  const chooser = (key) => {
    const select = el("select", { id: `s-${key}` });
    select.append(...byKey[key].map((o) =>
      el("option", { value: o.value, textContent: o.name[lang()] ?? o.name.en })));
    select.value = settings[key];
    select.onchange = async () => {
      try {
        await api().set_setting(key, select.value);
        note.textContent = t("saved");
        setTimeout(() => (note.textContent = ""), 1500);
        if (key === "theme") applyTheme(select.value);
      } catch (e) {
        select.value = settings[key];
        note.textContent = String(e.message || e).replace(/^.*Error:\s*/s, "");
      }
    };
    return el("div", { className: "field" }, el("label", { htmlFor: `s-${key}` }, t(key)), select);
  };

  const credit = (key) => {
    const input = el("input", { id: `s-${key}`, value: settings[key] ?? "" });
    input.onchange = async () => {
      await api().set_setting(key, input.value);
      note.textContent = t("saved");
      setTimeout(() => (note.textContent = ""), 1500);
    };
    return el("div", { className: "field" }, el("label", { htmlFor: `s-${key}` }, t(key)), input);
  };

  main.append(
    el("div", { className: "card" },
      el("h3", {}, t("calculation")),
      el("div", { className: "fields" },
        chooser("ayanamsa"), chooser("house_system"), chooser("node"), chooser("orb_scale")),
      el("p", { className: "note" }, t("calc_note"))),

    el("div", { className: "card" },
      el("h3", {}, t("appearance")),
      el("div", { className: "fields" }, chooser("theme"), chooser("chart_style"))),

    el("div", { className: "card" },
      el("h3", {}, t("credits")),
      el("div", { className: "fields" }, credit("report_by"), credit("report_site"))),

    el("p", { className: "note" }, note),
    backupCard(openWith),

    el("div", { className: "card" },
      el("h3", {}, t("about")),
      rows([
        [t("engine_version"), about.engine],
        ["Python", about.python],
        [t("where_data"), about.data_dir],
        [t("where_reports"), about.reports_dir],
      ]),
      el("p", { className: "note" }, about.licences)),
  );
}

function applyTheme(theme) {
  if (theme === "light" || theme === "dark") document.documentElement.dataset.theme = theme;
  else delete document.documentElement.dataset.theme;
}

/* Backup and restore.
 *
 * The file is the Android app's format, so one taken on the phone opens here and the other way round -
 * which is the only reason most people want a backup at all. The password is never stored, and the
 * note says what that means before the box is typed in rather than after the file cannot be opened.
 */
function backupCard(openWith = null) {
  const status = el("p", { className: "note", id: "backup-status" });
  const password = el("input", { type: "password", id: "b-password", autocomplete: "new-password" });
  let chosenFile = openWith;

  const say = (text, bad = false) => {
    status.className = bad ? "problem" : "note";
    status.textContent = text;
  };

  const write = el("button", { className: "primary" }, t("make_backup"));
  write.onclick = async () => {
    try {
      const done = await api().backup(password.value);
      say(t("backup_done", done.count, done.file));
    } catch (e) {
      say(String(e.message || e).replace(/^.*Error:\s*/s, ""), true);
    }
  };

  const chosenName = el("span", { className: "chosen" },
    chosenFile ? chosenFile.split(/[\\/]/).pop() : "");
  const choose = el("button", {}, t("choose_file"));
  const restore = el("button", {}, t("restore_now"));
  restore.disabled = !chosenFile;

  choose.onclick = async () => {
    chosenFile = await api().pick_backup();
    chosenName.textContent = chosenFile ? chosenFile.split(/[\\/]/).pop() : "";
    restore.disabled = !chosenFile;
  };
  restore.onclick = async () => {
    try {
      const done = await api().restore(chosenFile, password.value);
      say(t("restore_done", done.added, done.updated, done.skipped)
          + (done.waiting ? " " + t("waiting_people", done.waiting) : ""));
      people = await api().people();
      edition = await api().edition();
      drawEdition();
      drawPeople();
    } catch (e) {
      say(String(e.message || e).replace(/^.*Error:\s*/s, ""), true);
    }
  };

  return el("div", { className: "card" },
    el("h3", {}, t("backup")),
    el("p", { className: "note" }, t("backup_note")),
    el("div", { className: "fields" },
      el("div", { className: "field wide" },
        el("label", { htmlFor: "b-password" }, t("password")), password)),
    el("div", { className: "row" }, write, choose, chosenName, restore),
    el("p", { className: "note" }, t("restore_note")),
    status);
}

/* --- the full version --------------------------------------------------------------------- */

/* The code is checked here, on this computer, against a public key the app carries. It can check a code
   and never make one, and nothing is sent anywhere to do it - which is what lets the whole app keep
   working with no internet at all. */
function showUnlock() {
  screen = { name: "unlock", redraw: () => showUnlock() };
  selectedId = null;
  drawPeople();
  drawTools();

  const status = el("p", { className: "note" });
  const email = el("input", { id: "u-email", type: "email", autocomplete: "email" });
  const code = el("input", { id: "u-code", placeholder: "GJ1-XXXXX-XXXXX-…", autocapitalize: "characters" });

  const go = el("button", { className: "primary" }, t("unlock_now"));
  go.onclick = async () => {
    try {
      edition = await api().unlock(email.value, code.value);
      status.className = "note";
      status.textContent = t("unlock_done");
      drawEdition();
      drawPeople();
    } catch (e) {
      status.className = "problem";
      status.textContent = String(e.message || e).replace(/^.*Error:\s*/s, "");
    }
  };

  $("#main").replaceChildren(
    el("h2", {}, t("unlock_title")),
    el("p", { className: "lede" }, t("unlock_sub")),
    el("div", { className: "card" }, el("p", {}, t("unlock_what"))),
    el("div", { className: "card" },
      el("p", { className: "note" }, t("unlock_where")),
      el("div", { className: "fields" },
        el("div", { className: "field wide" }, el("label", { htmlFor: "u-email" }, t("your_email")), email),
        el("div", { className: "field wide" }, el("label", { htmlFor: "u-code" }, t("your_code")), code)),
      el("div", { className: "row" }, go),
      status,
      el("p", { className: "note" }, t("unlock_offline"))),
  );
  email.focus();
}

/* --- start -------------------------------------------------------------------------------- */

async function start() {
  const settings = await api().settings();
  setLang(settings.language);
  applyTheme(settings.theme);
  people = await api().people();
  drawPeople();
  drawTools();
  drawLanguageSwitch();

  // Double-clicking a .gjb backup starts the app with that file. It opens the settings screen with the
  // file chosen and stops there: restoring somebody's saved people without being asked is not what a
  // double-click should do.
  edition = await api().edition();
  drawEdition();
  glossary = await api().glossary();

  const opened = await api().pending_restore();
  if (opened) return showSettings(opened);
  people.length ? showChart(people[0].id) : showAddPerson();
}

$("#new-person").addEventListener("click", () => showAddPerson());

// pywebview injects its bridge after the page loads, and announces it with this event.
window.addEventListener("pywebviewready", start);
