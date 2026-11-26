# web/ — the calculator site

A static site that computes Vedic astrology in the visitor's browser and sends nothing
anywhere. 90 pages in English and Hindi. No server, no database, no third-party requests.

The reason the architecture is this way, and the business it is part of, are in the plan
document; the short version is that the one defensible claim here is that birth details
never leave the device, and a server-side calculator would forfeit it.

## What is here

| File | What it is |
| --- | --- |
| `build.py` | Generates every page from the data. `--base https://host` also writes `sitemap.xml` and `robots.txt` |
| `verify.py` | Checks the browser engine against Swiss Ephemeris and the app. Must print `passed` before anything ships |
| `moon.js` | Moon's sidereal longitude: ELP-2000/82 truncated, Lahiri ayanamsa, ΔT table. No Swiss Ephemeris code or data, so no licence obligation |
| `ui.js` | Everything the pages share on top of `moon.js`: the nakshatra and rashi tables, the helpers, the `Engine` seam, one controller per page family, and `Engine.accuracy` |
| `engine.js` | **Generated.** `moon.js` + the data from `data.json` + `ui.js`, assembled by `build.py`, so the lunar theory the pages run is the same text `verify.py` measures. Never edit it |
| `dasha.js` | Vimshottari, ported from `vedic.py` |
| `koota.js` | Ashtakoota guna milan; its tables were **exported** from `ashtakoota.py`, never retyped |
| `koota-data.json` | Those exported tables, regenerated from the app rather than edited by hand |
| `data.json` | The 27 nakshatras, bilingual |
| `site.css` | One stylesheet. System fonts only |
| `nakshatra.html` | The nakshatra hub, which is also the page most search traffic lands on |
| `stage.py` | Stages the built site for an artifact preview, where `index.html` is reserved and the home page becomes `home.html`. A real host needs none of this |
| `DEPLOY.md` | Verify, build, serve, submit — in that order |

Generated pages are gitignored. The sources above are what is kept.

## Build and check

```sh
python3 web/verify.py                               # must print: passed
python3 web/build.py --base https://yourdomain.com  # 90 pages + sitemap + robots
```

`verify.py` points Swiss Ephemeris at `app/src/main/python/ephe` and **exits if the
fallback to Moshier happens**, because a verification against a silently substituted
reference proves nothing. It checks seven things: the Moon against the data files over 5,000
dates; that no nakshatra, pada or Moon-sign disagreement ever escapes the cusp band the
pages use to flag an uncertain answer, which must be zero; the navamsa rule against
`vedic.py` for all 108 padas; the twelve rashi names and lords in `engine.js` against the
app's own tables; that each sign's navamsa start reproduces the classical movable/fixed/dual
rule, which twelve pages state as a fact; the eight kootas and the /36 total against
`ashtakoota.py` over 1,500 pairs; and how far the Vimshottari table shifts, which the dasha
page quotes and so must stay true. It also compares the figures the pages print against the
figures it has just measured, so a stale number cannot ship quietly.

## The page families

| Family | Pages | What makes each page its own |
| --- | --- | --- |
| Nakshatra | hub + 27 × 2 languages | Its degree span, its four padas and their navamsa signs, its lord's dasha length |
| Rashi | hub + 12 × 2 languages | Its span, its nine padas with their nakshatras and navamsas, and where its navamsa sequence starts |
| Vimshottari dasha | 1 × 2 | The whole sequence with dates, and the measured shift those dates carry |
| Kundli Milan | 1 × 2 | The eight kootas, including where the published tables disagree |
| Method | 1 × 2 | Every accuracy figure, read out of `Engine.accuracy` rather than retyped |
| Home, privacy | 2 × 2 | — |

A rashi is the same longitude cut by 30° instead of 13°20′, so every sign boundary is also a
pada boundary: the cusp band that protects a nakshatra answer protects a sign answer too,
nine padas fall in each sign exactly, and both facts are measured rather than asserted.

## The engine seam

Pages ask for the Moon through `Engine.moonSidereal()`, never `moon.js` directly, and read
their accuracy wording from `Engine.accuracy` in `ui.js`. A licensed WebAssembly build of Swiss
Ephemeris registers itself in one call and no page changes — see `wasm/README.md`.

## Rules that are not style preferences

* **No third-party requests.** The privacy page invites the reader to open their Network tab
  and see only this site's own files. Adding a webfont, an analytics tag or a chat widget
  makes that page a lie, and its own instructions are how a visitor would catch it. This
  already happened once: the first build loaded Google Fonts.
* **No birth data to a server, ever**, including the paid report when it exists.
* **Accuracy figures are measured.** The numbers on the pages and in `Engine.accuracy` are
  what `verify.py` prints. They move in the same commit as the engine or not at all.
* **Tables come from the app, by export.** Anything the app also computes — kootas, navamsa,
  dasha — is ported or exported, never reimplemented from a book, so the two cannot drift.
