# Jyotish for Android

Android app built on the astrology-numerology-reading engine. This repository is at milestone **M0, the spike**: proving that the tested Python engine runs on a phone before any real interface is built. The plan and screen designs are in the "Astrology Android App: Plan" doc and the "Astrology App: v1 Screens" design.

## Status

- **M0 spike: done.** The tested Python engine runs on Android through Chaquopy and reproduces the desktop results exactly.
- **M1 foundation: in progress.** Jetpack Compose app: Welcome with English or Hindi, Home with saved profiles and the current dasha, Add profile with offline place search (69,000 GeoNames places, searchable in Hindi for India and Nepal) or typed coordinates, Settings (language, chart style, ayanamsa, nodes, muhurta weekday rule, speed test). The Kundali, Milan, Muhurta and Numerology screens are placeholders until M2 to M5.

Every push runs `.github/workflows/spike.yml`: it builds pyswisseph for Android (cached), runs the unit tests, builds the app, and runs the instrumented tests on an Android 14 emulator (the engine snapshot test and a first-launch-to-chart flow in English and Hindi). Results, timings, APK size and cold start are written to the run summary and as annotations; the debug APK is attached to the run.

## Layout

```
app/src/main/python/        engine_api.py (the app's bridge) + the engine, copied from the skill
app/src/main/java/...       engine/ (Python bridge), data/ (profiles, places, settings), ui/ (Compose screens)
app/src/main/assets/        places.tsv, the offline place list (tools/make_places.py)
app/src/androidTest/        SpikeTest and the desktop snapshot it compares against
tools/sync_engine.py        copy a new engine version from the skill folder
tools/make_snapshot.py      regenerate the snapshot after a sync
tools/make_places.py        rebuild the place list from GeoNames (pip install geonamescache==3.0.2)
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
