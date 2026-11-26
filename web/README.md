# web/ — the calculator site

A static site that computes Vedic astrology in the visitor's browser and sends nothing
anywhere. 62 pages in English and Hindi. No server, no database, no third-party requests.

The reason the architecture is this way, and the business it is part of, are in the plan
document; the short version is that the one defensible claim here is that birth details
never leave the device, and a server-side calculator would forfeit it.

## What is here

| File | What it is |
| --- | --- |
| `build.py` | Generates every page from the data. `--base https://host` also writes `sitemap.xml` and `robots.txt` |
| `verify.py` | Checks the browser engine against Swiss Ephemeris and the app. Must print `passed` before anything ships |
| `moon.js` | Moon's sidereal longitude: ELP-2000/82 truncated, Lahiri ayanamsa, ΔT table. No Swiss Ephemeris code or data, so no licence obligation |
| `engine.js` | `moon.js` plus the nakshatra data, the shared helpers, and the `Engine` seam |
| `dasha.js` | Vimshottari, ported from `vedic.py` |
| `koota.js` | Ashtakoota guna milan; its tables were **exported** from `ashtakoota.py`, never retyped |
| `koota-data.json` | Those exported tables, regenerated from the app rather than edited by hand |
| `data.json` | The 27 nakshatras, bilingual |
| `site.css` | One stylesheet. System fonts only |
| `nakshatra.html` | The nakshatra hub, which is also the page most search traffic lands on |
| `DEPLOY.md` | Verify, build, serve, submit — in that order |

Generated pages are gitignored. The sources above are what is kept.

## Build and check

```sh
python3 web/verify.py                               # must print: passed
python3 web/build.py --base https://yourdomain.com  # 62 pages + sitemap + robots
```

`verify.py` points Swiss Ephemeris at `app/src/main/python/ephe` and **exits if the
fallback to Moshier happens**, because a verification against a silently substituted
reference proves nothing. It checks five things: the Moon against the data files over 5,000
dates; that no nakshatra or pada disagreement ever escapes the cusp band the pages use to
flag an uncertain answer, which must be zero; the navamsa rule against `vedic.py` for all
108 padas; the eight kootas and the /36 total against `ashtakoota.py` over 1,500 pairs; and
how far the Vimshottari table shifts, which the dasha page quotes and so must stay true.

## The engine seam

Pages ask for the Moon through `Engine.moonSidereal()`, never `moon.js` directly, and read
their accuracy wording from `Engine.accuracy`. A licensed WebAssembly build of Swiss
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
