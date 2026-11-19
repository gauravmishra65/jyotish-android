/* The interface.
 *
 * Phase 1: add a person, save them, see their chart's essentials. Everything it knows comes from
 * pywebview.api, which is the Api object in api.py - there is no second copy of any rule here.
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

/* --- the list of people ------------------------------------------------------------------- */

function drawPeople() {
  const list = $("#people");
  list.replaceChildren();
  $("#count").textContent = people.length === 1 ? "1 person" : `${people.length} people`;

  if (people.length === 0) {
    list.append(el("div", { className: "empty" }, "Nobody saved yet."));
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
    placeholder: "Varanasi, or Sitapur UP, or वाराणसी", value: existing?.place ?? "",
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
    el("label", { htmlFor: "f-place" }, "Birthplace"),
    input, results);
}

/* One form for both jobs. Passing an existing person fills it in and keeps their id, so saving edits
   them in place rather than making a second copy - which is what you want when a chart will not build
   because one field is wrong. */
function showAddPerson(existing = null) {
  const editing = Boolean(existing);
  selectedId = editing ? existing.id : null;
  drawPeople();
  $("#main").replaceChildren(
    el("h2", {}, editing ? `Edit ${existing.name}` : "Add a person"),
    el("p", { className: "lede" }, "Birth details stay on this computer. Nothing is sent anywhere."),
    el(
      "div",
      { className: "fields" },
      field("Name", "name", { wide: true, placeholder: "Ravi Shankar Tiwari", value: existing?.name ?? "" }),
      field("Date of birth", "date", { placeholder: "1988-07-14", value: existing?.date ?? "" }),
      field("Time of birth", "time", { placeholder: "14:35", value: existing?.time ?? "" }),
      placeField(existing),
      field("Latitude", "lat", { placeholder: "25.3176", value: existing?.lat ?? "" }),
      field("Longitude", "lon", { placeholder: "82.9739", value: existing?.lon ?? "" }),
      field("Time zone", "tz", { placeholder: "Asia/Kolkata", list: "zones", value: existing?.tz ?? "" }),
    ),
    el(
      "div",
      { className: "row" },
      el("button", { className: "primary", onclick: () => savePerson(existing) },
        editing ? "Save and rebuild the chart" : "Save and build the chart"),
      editing ? deleteButton(existing.id) : "",
      el("span", { id: "problem", className: "problem" }),
    ),
    el("p", { className: "note" },
      "Choosing a birthplace fills in the coordinates and the time zone. " +
      "They stay editable for a village the list does not carry."),
  );
  timeZoneList().then((list) => document.body.append(list));
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

async function showChart(id) {
  selectedId = id;
  drawPeople();
  const who = people.find((p) => p.id === id);
  $("#main").replaceChildren(
    el("h2", {}, who ? who.name : "Chart"),
    el("p", { className: "lede working" }, "Building the chart…"),
  );

  let chart;
  try {
    chart = await api().chart(id);
  } catch (e) {
    // A chart that will not build is exactly when someone needs to fix or remove the person, so this
    // branch must offer both. Without them a bad entry is stuck on screen with no way out.
    $("#main").replaceChildren(
      el("h2", {}, who ? who.name : "Chart"),
      el("p", { className: "problem" }, String(e.message || e).replace(/^.*ValidationError:\s*/s, "")),
      el("div", { className: "row" },
        who ? el("button", { className: "primary", onclick: () => showAddPerson(who) }, "Fix these details") : "",
        who ? deleteButton(id) : ""),
    );
    return;
  }

  const v = chart.vedic;
  const moon = v.planets.Moon || {};
  const pan = v.panchang || {};
  const maha = v.dashas?.vimshottari?.current?.mahadasha || {};
  const antara = v.dashas?.vimshottari?.current?.antardasha || {};

  // The engine already formats degrees-minutes-seconds and the degree within the sign, so neither is
  // recomputed here: a second implementation is a second thing to get wrong.
  const planetRows = Object.entries(v.planets).map(([name, p]) =>
    el("tr", {}, el("th", {}, name), el("td", {}, `${p.sign} ${p.dms ?? degrees(p.deg_in_sign)}${p.retrograde ? " ℞" : ""}`)));

  const settings = await api().settings();
  const style = settings.chart_style === "south" ? "south" : "north";
  const lang = settings.language === "hi" ? "hi" : "en";

  const styleButton = (which, label) => {
    const button = el("button", { className: which === style ? "primary" : "" }, label);
    button.onclick = async () => { await api().set_setting("chart_style", which); showChart(id); };
    return button;
  };

  $("#main").replaceChildren(
    el("h2", {}, who.name),
    el("p", { className: "lede" }, `${who.date} · ${who.time}${who.place ? " · " + who.place : ""}`),

    el("div", { className: "card chart-card" },
      el("div", { className: "chart-holder" }, kundliSvg(chart, { style, lang, size: 340 })),
      el("div", { className: "row" }, styleButton("north", "North Indian"), styleButton("south", "South Indian"))),

    el("div", { className: "card" },
      el("h3", {}, "The chart"),
      rows([
        ["Lagna", `${v.lagna.sign} ${v.lagna.dms ?? degrees(v.lagna.lon % 30)}`],
        ["Moon sign", moon.sign ?? "—"],
        ["Nakshatra", moon.nakshatra ? `${moon.nakshatra}${moon.pada ? ", pada " + moon.pada : ""}` : "—"],
        ["Sunrise", pan.sunrise_local ?? "—"],
        ["Tithi", pan.tithi ? `${pan.paksha ?? ""} ${pan.tithi}`.trim() : "—"],
        ["Vara", pan.vara ?? "—"],
      ])),

    el("div", { className: "card" },
      el("h3", {}, "Vimshottari dasha"),
      rows([
        ["Mahadasha", maha.lord ? `${maha.lord} · ${maha.start ?? ""} to ${maha.end ?? ""}` : "—"],
        ["Antardasha", antara.lord ? `${antara.lord} · ${antara.start ?? ""} to ${antara.end ?? ""}` : "—"],
      ])),

    el("div", { className: "card" }, el("h3", {}, "Planets"), el("table", {}, ...planetRows)),

    el("div", { className: "row" },
      el("button", { onclick: () => showAddPerson(who) }, "Edit details"),
      deleteButton(id)),

    el("p", { className: "note" },
      "The drawn kundli chart, the readings and the reports are not in this build yet. " +
      "This screen exists to prove the engine, the storage and the window work together."),
  );
}

/* Deleting asks first, but in the page rather than through window.confirm: a native dialog depends on
   what the embedded browser allows, and a confirmation that silently answers "no" would look exactly
   like a delete button that does nothing. The button becomes its own confirmation instead. */
function deleteButton(id, label = "Delete this person") {
  const button = el("button", { className: "quiet" }, label);
  button.onclick = () => {
    if (button.dataset.armed) return removePerson(id);
    button.dataset.armed = "1";
    button.textContent = "Click again to delete — this cannot be undone";
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

/* --- start -------------------------------------------------------------------------------- */

async function start() {
  const settings = await api().settings();
  if (settings.theme === "dark" || settings.theme === "light") {
    document.documentElement.dataset.theme = settings.theme;
  }
  people = await api().people();
  drawPeople();
  people.length ? showChart(people[0].id) : showAddPerson();
}

$("#new-person").addEventListener("click", () => showAddPerson());

// pywebview injects its bridge after the page loads, and announces it with this event.
window.addEventListener("pywebviewready", start);
