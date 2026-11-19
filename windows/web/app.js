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
  { name: "milan", label: "milan", sub: "milan_sub", open: () => showMilan() },
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
function drawLanguageSwitch() {
  const holder = $("#language");
  const choose = async (which) => {
    if (which === lang()) return;
    setLang(await api().set_setting("language", which).then((s) => s.language));
    drawPeople();
    drawTools();
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
function placeField(existing) {
  const input = el("input", {
    id: "f-place", name: "place", autocomplete: "off",
    placeholder: t("place_hint"), value: existing?.place ?? "",
  });
  const results = el("div", { className: "results", id: "place-results" });

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
          $("#f-lat").value = place.lat;
          $("#f-lon").value = place.lon;
          $("#f-tz").value = place.tz;
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
    el("label", { htmlFor: "f-place" }, t("birthplace")),
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
    await showChart(saved.id);
  } catch (e) {
    // Python exceptions arrive as a rejected promise; the message is written for a person to read.
    $("#problem").textContent = String(e.message || e).replace(/^.*ValidationError:\s*/s, "");
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
  return p.lord ? t("period", p.lord, p.start ?? "—", p.end ?? "—") : "—";
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
    el("tr", {}, el("th", {}, name), el("td", {}, `${p.sign} ${p.dms ?? degrees(p.deg_in_sign)}${p.retrograde ? " ℞" : ""}`)));

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
        [t("lagna"), `${v.lagna.sign} ${v.lagna.dms ?? degrees(v.lagna.lon % 30)}`],
        [t("moon_sign"), moon.sign ?? "—"],
        [t("nakshatra"), moon.nakshatra
          ? `${moon.nakshatra}${moon.pada ? ", " + t("pada", moon.pada) : ""}` : "—"],
        [t("sunrise"), pan.sunrise_local ?? "—"],
        [t("tithi"), pan.tithi ? `${pan.paksha ?? ""} ${pan.tithi}`.trim() : "—"],
        [t("vara"), pan.vara ?? "—"],
      ])),

    el("div", { className: "card" },
      el("h3", {}, t("dashas")),
      rows([[t("mahadasha"), period(maha)], [t("antardasha"), period(antara)]])),

    el("div", { className: "card" }, el("h3", {}, t("planets")), el("table", {}, ...planetRows)),
  );

  // The sixteen divisional charts, then the readings, then the way out. The buttons go last so that
  // scrolling to the end of a chart lands on them rather than on the middle of the readings.
  const main = $("#main");
  main.append(reportPanel(id));
  if (details.varga_meta?.length) {
    main.append(el("h3", { className: "panel-heading" }, t("vargas")), vargaPanel(details, style));
  }
  if (Array.isArray(details.sections) && details.sections.length) {
    main.append(
      el("h3", { className: "panel-heading" }, t("readings", details.sections.length)),
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

/* --- start -------------------------------------------------------------------------------- */

async function start() {
  const settings = await api().settings();
  setLang(settings.language);
  if (settings.theme === "dark" || settings.theme === "light") {
    document.documentElement.dataset.theme = settings.theme;
  }
  people = await api().people();
  drawPeople();
  drawTools();
  drawLanguageSwitch();
  people.length ? showChart(people[0].id) : showAddPerson();
}

$("#new-person").addEventListener("click", () => showAddPerson());

// pywebview injects its bridge after the page loads, and announces it with this event.
window.addEventListener("pywebviewready", start);
