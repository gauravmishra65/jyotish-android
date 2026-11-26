# Replacing the browser engine with Swiss Ephemeris itself

The site currently computes the Moon from a truncated ELP-2000/82 series: about 11
arcseconds from Swiss Ephemeris on average, 28 at worst, which moves a Vimshottari
table by 1.1 days on average and up to 3.75. `web/verify.py` measures all of that on
every run, and the dasha page states the figures rather than hiding them.

A WebAssembly build of Swiss Ephemeris removes the error entirely, and the pages are
already shaped for it: everything asks for the Moon through `Engine.moonSidereal()`
in `web/engine.js`, so a replacement registers itself and no page changes.

```js
Engine.use({
  name: "swisseph-wasm",
  accuracy: {meanArcsec: 0, worstArcsec: 0, dashaShiftDays: 0, dashaWorstDays: 0},
  moonSidereal: dateUTC => /* swe_calc_ut through the wasm module */
});
```

## Do not use the npm package

`sweph-wasm` on npm looks like the obvious shortcut. It is not usable here:

* Its `package.json` declares `AGPL-3.0-or-later` and it ships the full AGPL text as
  its `LICENSE`. The README's "MIT" badge and its "This project is MIT licensed" line
  contradict both, and no third party can relicense Swiss Ephemeris as MIT in any
  case - Astrodienst's dual licence governs.
* Taking it at AGPL means this entire project goes AGPL, which is the thing the
  professional licence exists to avoid.
* It also carries 105 MB of `.se1` data files across 150 files, which this project
  does not want (see below).

Build from Astrodienst's own sources instead. Then the professional licence covers it
directly and there is no third-party claim anywhere in the chain.

## Which data files to ship

The app ships four, inside `assets/chaquopy/app.imy`, and `chart_engine.py` points
`swe_set_ephe_path` at them:

| File | Size | What it covers |
| --- | --- | --- |
| `semo_18.se1` | 1.3 MB | Moon, from 1800 |
| `sepl_18.se1` | 473 KB | planets, from 1800 |
| `seas_18.se1` | 218 KB | main asteroids, from 1800 |
| `sefstars.txt` | 133 KB | fixed stars |

A WASM build should carry the same ones, which is about 2 MB - fetched once and
cached, not per calculation. That is a real cost on a first visit and worth measuring
against the alternative: without them Swiss Ephemeris silently falls back to Moshier,
which for the Moon is 0.56 arcseconds from the data files on average and 2.58 at
worst. Either is far inside the cusp band, so Moshier alone would be defensible for
the free pages; the data files matter for the paid report, where exact dates are the
product.

The 105 MB that `sweph-wasm` carries is 150 files covering every century and every
asteroid. Four files is what this project actually uses.

## Build recipe

Not runnable in the Claude container: emscripten's distribution host is blocked
there, so this has to be run on a normal machine.

```sh
# 1. toolchain
git clone https://github.com/emscripten-core/emsdk && cd emsdk
./emsdk install latest && ./emsdk activate latest && source ./emsdk_env.sh

# 2. sources - the release matching the app's pyswisseph 2.10.3
git clone --branch v2.10.03 https://github.com/aloistr/swisseph

# 3. compile, Moshier only, no data files
emcc swisseph/sw*.c \
  -O3 -flto \
  -DNO_JPL \
  -s MODULARIZE=1 -s EXPORT_ES6=1 -s ENVIRONMENT=web \
  -s ALLOW_MEMORY_GROWTH=1 \
  -s EXPORTED_RUNTIME_METHODS='["ccall","cwrap","getValue","setValue"]' \
  -s EXPORTED_FUNCTIONS='["_swe_calc_ut","_swe_set_sid_mode","_swe_get_ayanamsa_ut","_swe_julday","_swe_deltat","_swe_close","_malloc","_free"]' \
  -o swisseph.mjs
```

Call it with `SEFLG_MOSEPH | SEFLG_SIDEREAL` and `SE_SIDM_LAHIRI`, which is what the
app uses. Publish `swisseph.wasm` beside the pages and fetch it by relative URL:
artifacts and most static hosts allow that, while a CDN will not serve it under the
artifact content policy.

## Before you ship it

Add a WASM arm to `web/verify.py` comparing it against pyswisseph on the same 5,000
dates. The numbers should collapse to zero, and the dasha page's tolerance paragraph
and `Engine.accuracy` must be updated together - the page quotes those figures, so
leaving them stale would be worse than the error they describe.
