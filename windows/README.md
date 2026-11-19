# The Windows edition

A desktop build of the same app, from the same engine. Feature parity with the Android edition, bar the
things that only make sense on a phone (a daily notification, in-app purchase).

## Why this is the easy platform

Android needed Chaquopy and a cross-compiled wheel. iOS needs a framework-packaged C extension and an
embedded interpreter. Windows needs neither: the engine is Python, Windows runs Python, and pyswisseph
publishes a `win_amd64` wheel. `pip install` is the whole porting story for the calculation layer.

Python is pinned to **3.11** because that is the newest CPython with a prebuilt pyswisseph wheel. The
engine's own floor is 3.9 (its newest stdlib use is `zoneinfo`), so Android can stay on 3.13 and both
remain correct. CI tests the engine on both, which is what keeps that true.

## What is here

| | |
| --- | --- |
| `check_engine.py` | Builds a real chart through `engine_api` and compares it to Linux. |
| `jyotish_win/bridge.py` | The only way the app talks to the engine. The desktop counterpart of `Engine.kt`. |
| `jyotish_win/storage.py` | Profiles, settings and the chart cache in `%LOCALAPPDATA%\GauravJyotish`. |
| `jyotish_win/places.py` | 70,000 birthplaces offline, ranked as `Places.kt` ranks them. |
| `jyotish_win/backup.py` | The Android app's backup format, byte for byte. |
| `jyotish_win/licence.py` | Unlock codes, verified against a public key. It cannot make one. |
| `jyotish_win/api.py` | Everything the interface is allowed to do. |
| `jyotish_win/main.py` | The window. Deliberately tiny, because it is the one untestable file. |
| `web/` | The interface: one page, a stylesheet and four scripts, no framework. |
| `packaging/` | The icon, the PyInstaller spec and the Inno Setup installer script. |
| `tests/` | 129 tests, none of which need a window. |
| `places.tsv` | The same file the Android app ships. |

The engine itself is not copied here. `bridge.py` finds it in the Android tree, because there is one
engine and two copies would drift apart within a week. The packaged build takes a copy at build time.

## What the app does

Add people and see their chart, drawn North or South Indian. All 66 reading sections and all 16
divisional charts, in English or Hindi. Kundali Milan. Muhurta, optionally checked against the people
involved. Numerology and the Chinese side. Nine reports, each saved as one self-contained HTML page in
`Documents\Gaurav Jyotish`, which is where Windows prints to PDF from. Settings for ayanamsa, house
system, node and orb width. An encrypted backup that opens on the phone.

Both languages everywhere, not only in the readings: every word the interface says of its own is in
`web/strings.js`, in English and Hindi, taking the Android app's wording wherever the same label exists
there.

## Running it from a checkout

```
pip install -r windows/requirements.txt
python windows/check_engine.py
python -m unittest discover -s windows/tests
python -m jyotish_win.main          # from inside windows/
```

`JYOTISH_ENGINE_PATH` overrides where the engine is found, `JYOTISH_DATA_DIR` where data is written,
`JYOTISH_REPORTS_DIR` where reports go, and `JYOTISH_EDITION` whether the build behaves as the demo or
the full version. All four exist so tests and packaged builds can point somewhere other than the
defaults. `JYOTISH_DEBUG` opens the WebView2 developer tools, which is the only way to see a JavaScript
error.

## Building the installer

CI does it (`.github/workflows/windows-app.yml`), and it has to be Windows: PyInstaller freezes for the
platform it runs on and Inno Setup is a Windows compiler. Both are on the `windows-latest` image.

```
pyinstaller --noconfirm --clean windows/packaging/jyotish.spec
ISCC windows/packaging/setup.iss
```

One folder rather than one file: a single `.exe` would unpack 2 MB of ephemeris and 55 engine modules to
a temporary folder on every launch, and being able to look inside matters for an app whose promise is
that nothing leaves the computer. The installer is per-user and needs no administrator.

**The build is unsigned**, so Windows SmartScreen warns on first run. That warning is accurate and only a
code-signing certificate removes it.

## How it is put together

A WebView2 window, a page of plain HTML and JavaScript inside it, and `api.py` behind the glass. The
interface calls Python methods directly through pywebview; there is no server, no port and no JSON
protocol to keep in step, because both sides are the same process.

The window itself does almost nothing, and that is the design. A GUI cannot be exercised on a headless CI
runner, so everything that could be wrong in a way worth catching was pushed down into `api.py`,
`bridge.py`, `storage.py`, `places.py`, `backup.py` and `licence.py`, which are tested. `main.py` opens a
window and hands over the API.

Three test files are worth knowing about:

- `test_ui_contract.py` pins the chart fields the JavaScript reads, and that every word the interface
  says exists in both languages. A key the interface expects and the engine does not have fails silently
  in a browser - a dash where a date should be - so that contract is asserted in Python instead. Three
  bugs of exactly that kind were caught this way before anyone ran the app.
- `test_backup.py` runs the Android app's own crypto, as Java, against a file this build wrote, and back
  the other way. The backup format is only worth having if a file really does move between the phone and
  the desktop, and nothing in Python can prove that about Kotlin.
- `test_licence.py` does the same for unlock codes, with a throwaway key pair. No private key and no real
  code appears in any test.

Both of those skip where there is no JDK and run where there is one, including on `windows-latest`.

## The demo

The demo saves one chart - the same number as the phone's `Sales.FREE_PROFILES`. Everything else works on
that one chart, because a demo that cripples the thing being judged tells nobody whether the readings are
any good. An unlock code is the Android app's: one bought once works on both.

## What this does not decide

Nothing here commits to shipping. The Swiss Ephemeris licence still governs whether a Windows build can be
distributed, and on Windows both routes remain open: AGPL with published source, or Astrodienst's
professional licence. That choice is unmade and unquoted.
