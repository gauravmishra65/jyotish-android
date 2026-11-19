# The Windows edition

Work in progress. The engine runs; the interface does not exist yet.

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
| `check_engine.py` | Phase 0. Builds a real chart through `engine_api` and compares it to Linux. |
| `jyotish_win/bridge.py` | The only way the app talks to the engine. The desktop counterpart of `Engine.kt`. |
| `jyotish_win/storage.py` | Profiles, settings and the chart cache in `%LOCALAPPDATA%\GauravJyotish`. |
| `jyotish_win/api.py` | What the interface is allowed to do: people, charts, settings. |
| `jyotish_win/main.py` | The window. Deliberately tiny, because it is the one untestable file. |
| `web/` | The interface: one page, one stylesheet, one script, no framework. |
| `tests/` | 49 tests, none of which need a window. |
| `requirements.txt` | Three packages. |

The engine itself is not copied here. `bridge.py` finds it in the Android tree, because there is one
engine and two copies would drift apart within a week.

## Running it

```
pip install -r windows/requirements.txt
python windows/check_engine.py
python -m unittest discover -s windows/tests
```

`JYOTISH_ENGINE_PATH` overrides where the engine is found, and `JYOTISH_DATA_DIR` overrides where data is
written - both exist so tests and packaged builds can point somewhere other than the defaults.

## How it is put together

A WebView2 window, a page of plain HTML and JavaScript inside it, and `api.py` behind the glass. The
interface calls Python methods directly through pywebview; there is no server, no port and no JSON
protocol to keep in step, because both sides are the same process.

The window itself does almost nothing, and that is the design. A GUI cannot be exercised on a headless CI
runner, so everything that could be wrong in a way worth catching was pushed down into `api.py`,
`bridge.py` and `storage.py`, which are tested. `main.py` opens a window and hands over the API.

`tests/test_ui_contract.py` is worth knowing about: it pins the chart fields the JavaScript reads. A key
the interface expects and the engine does not have fails silently in a browser - a dash where a date
should be - so that contract is asserted in Python instead.

Phase 1 is done: the window opens, a person can be added and saved, and their chart is computed and
cached. The drawn kundli, the readings and the reports are phases 3 and 4.

## What this does not decide

Nothing here commits to shipping. The Swiss Ephemeris licence still governs whether a Windows build can be
distributed, and on Windows both routes remain open: AGPL with published source, or Astrodienst's
professional licence. That choice is unmade and unquoted.
