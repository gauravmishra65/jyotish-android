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
  const input = el("input", Object.assign({ id: `f-${name}`, name }, attrs));
  return el("div", { className: attrs.wide ? "field wide" : "field" }, el("label", { htmlFor: `f-${name}` }, label), input);
}

function showAddPerson() {
  selectedId = null;
  drawPeople();
  $("#main").replaceChildren(
    el("h2", {}, "Add a person"),
    el("p", { className: "lede" }, "Birth details stay on this computer. Nothing is sent anywhere."),
    el(
      "div",
      { className: "fields" },
      field("Name", "name", { wide: true, placeholder: "Ravi Shankar Tiwari" }),
      field("Date of birth", "date", { placeholder: "1988-07-14" }),
      field("Time of birth", "time", { placeholder: "14:35" }),
      field("Latitude", "lat", { placeholder: "25.3176" }),
      field("Longitude", "lon", { placeholder: "82.9739" }),
      field("Time zone", "tz", { placeholder: "Asia/Kolkata" }),
      field("Place (optional)", "place", { placeholder: "Varanasi, India" }),
    ),
    el(
      "div",
      { className: "row" },
      el("button", { className: "primary", onclick: savePerson }, "Save and build the chart"),
      el("span", { id: "problem", className: "problem" }),
    ),
    el("p", { className: "note" },
      "Place lookup is not here yet, so coordinates and the time zone are typed in for now. " +
      "The time zone is an IANA name, as in Asia/Kolkata or Europe/London."),
  );
  $("#f-name").focus();
}

async function savePerson() {
  const person = {};
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
    $("#main").replaceChildren(
      el("h2", {}, who ? who.name : "Chart"),
      el("p", { className: "problem" }, String(e.message || e)),
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

  $("#main").replaceChildren(
    el("h2", {}, who.name),
    el("p", { className: "lede" }, `${who.date} · ${who.time}${who.place ? " · " + who.place : ""}`),

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
      el("button", { className: "quiet", onclick: () => removePerson(id) }, "Delete this person")),

    el("p", { className: "note" },
      "The drawn kundli chart, the readings and the reports are not in this build yet. " +
      "This screen exists to prove the engine, the storage and the window work together."),
  );
}

async function removePerson(id) {
  if (!window.confirm("Delete this person and their saved charts? This cannot be undone.")) return;
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

$("#new-person").addEventListener("click", showAddPerson);

// pywebview injects its bridge after the page loads, and announces it with this event.
window.addEventListener("pywebviewready", start);
