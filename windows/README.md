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
| `tests/` | Everything above, tested without a window. |
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

## Why the window is not here yet

Everything in this folder can be proven in CI. A window cannot: a GUI needs a desktop session, and a
headless runner has none. So the design keeps the untestable part as small as possible - the shell opens a
WebView, hands it the bridge, and does nothing else. The decision that is still open is what runs inside
that WebView, and that is the UI-stack question in the plan.

## What this does not decide

Nothing here commits to shipping. The Swiss Ephemeris licence still governs whether a Windows build can be
distributed, and on Windows both routes remain open: AGPL with published source, or Astrodienst's
professional licence. That choice is unmade and unquoted.
