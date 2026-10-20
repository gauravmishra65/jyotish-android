# Jyotish for Android

Android app built on the astrology-numerology-reading engine. This repository is at milestone **M0, the spike**: proving that the tested Python engine runs on a phone before any real interface is built. The plan and screen designs are in the "Astrology Android App: Plan" doc and the "Astrology App: v1 Screens" design.

## What the spike proves

| Question | How it is answered |
|---|---|
| Does pyswisseph build for Android? | CI builds it with cibuildwheel 4.3.1 for arm64 (phones) and x86_64 (emulator), and runs a Swiss Ephemeris smoke test on the emulator |
| Does the engine give the same numbers on a phone? | `SpikeTest` runs 5 charts in 5 time zones, a Kundali Milan, a 3-month muhurta search and name options, and must match `snapshot.json` (made on the desktop) exactly |
| Is it fast enough? | The test and the app's "Run timing suite" button time every step; CI also records the app's cold start |
| How big is the app? | CI writes a size breakdown of the APK to the run summary |

Each push runs `.github/workflows/spike.yml`. Results are in the run's summary page; the debug APK is attached to the run as an artifact.

## Layout

```
app/src/main/python/        engine_api.py (the app's bridge) + the engine, copied from the skill
app/src/main/java/...       JyotishApp (starts Python, timed) and the spike screen
app/src/androidTest/        SpikeTest and the desktop snapshot it compares against
tools/sync_engine.py        copy a new engine version from the skill folder
tools/make_snapshot.py      regenerate the snapshot after a sync
tools/ci_emulator.sh        what CI runs on the emulator
```

## Updating the engine

```
python tools/sync_engine.py /path/to/astrology-numerology-reading
python tools/make_snapshot.py          # needs pyswisseph and tzdata
```

`ENGINE_VERSION.txt` records which skill commit the app carries. The app asks only for the `vedic,western,numerology` modules; the slow life-events layer (`events`) is left out.

## Building locally

Android Studio with JDK 17, and Python 3.13 on the computer (Chaquopy uses it to install the app's Python packages). There is no Gradle wrapper yet: run `gradle wrapper --gradle-version 8.14.3` once, or let Android Studio use Gradle 8.14.3. Put the pyswisseph Android wheels from a CI run's `wheels` artifact into `./wheels` first.

Pinned versions: Android Gradle Plugin 8.13.2, Gradle 8.14.3, Kotlin 2.2.21, Chaquopy 17.1.0 (Python 3.13), compileSdk and targetSdk 36, minSdk 26.

## Licence note

Swiss Ephemeris is dual-licensed (AGPL or Astrodienst's professional licence). Keep this repository private and do not distribute the app until that choice is made.
