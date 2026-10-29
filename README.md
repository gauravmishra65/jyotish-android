# Gaurav Jyotish by AuthorGaurav (Android)

Android app built on the astrology-numerology-reading engine: Kundali, Kundali milan, Muhurta and Numerology in English and Hindi, calculated on the phone with no account and no internet permission. The plan and screen designs are in the "Astrology Android App: Plan" doc and the "Astrology App: v1 Screens" design.

## Status: 1.0.0-rc1 (all milestones built)

- **M0 spike.** The tested Python engine runs on Android through Chaquopy and reproduces the desktop results exactly.
- **M1 foundation.** Welcome with English or Hindi, Home with saved profiles and the current dasha, Add profile with offline place search (69,000 GeoNames places, searchable in Hindi for India and Nepal), Settings (language, chart style, ayanamsa, nodes, muhurta weekday rule, speed test).
- **M2 Kundali.** North and South Indian charts, planets, dashas, yogas with base rates, Shadbala.
- **M3 Milan.** Ashtakoota out of 36, the ten Porutham, the Mangal check.
- **M4 Muhurta.** Event, dates, place and people; best windows and a by-day view.
- **M5 Numerology.** Indian, Chaldean and Pythagorean numbers, Loshu grid, Kua, name spelling options.
- **M6 Meanings.** Plain-words meanings in both languages for planets, houses, yogas, kootas, Porutham and numbers (`assets/meanings.json`, from `tools/make_meanings.py`); Hindi names for all 195 yogas.
- **M7 release hardening.** R8-minified release APK and App Bundle, signing from the environment, adaptive icon, backups excluded, a 48dp touch-target and label check on every main screen, Play listing and data-safety text in `docs/PLAY_LISTING.md`.

Every push runs `.github/workflows/spike.yml`: it builds pyswisseph for Android (cached), checks the string resources, runs the unit tests, builds the debug and release APKs and the App Bundle, runs the instrumented tests on an Android 14 emulator, and smoke-tests the minified release. Logs, test results and screenshots go to the `ci-results` branch; the debug APK and the release outputs are attached to the run.

## Layout

```
app/src/main/python/        engine_api.py (the app's bridge) + the engine, copied from the skill
app/src/main/java/...       engine/ (Python bridge), data/ (profiles, places, settings), ui/ (Compose screens)
app/src/main/assets/        places.tsv (tools/make_places.py), hindi_names.json (tools/sync_engine.py),
                            meanings.json (tools/make_meanings.py)
app/src/androidTest/        SpikeTest and the desktop snapshot it compares against
tools/sync_engine.py        copy a new engine version from the skill folder
tools/make_snapshot.py      regenerate the snapshot after a sync
tools/make_places.py        rebuild the place list from GeoNames (pip install geonamescache==3.0.2)
tools/make_meanings.py      rebuild the meanings file; fails if any yoga lacks a Hindi name or a category meaning
tools/check_strings.py      English/Hindi string parity, escaping and placeholders (run by CI)
docs/PLAY_LISTING.md        store listing (English and Hindi) and data-safety answers
tools/ci_emulator.sh        what CI runs on the emulator
```

## Updating the engine

```
python tools/sync_engine.py /path/to/astrology-numerology-reading
python tools/make_snapshot.py          # needs pyswisseph and tzdata
python tools/make_meanings.py          # after a sync that adds yogas
```

`ENGINE_VERSION.txt` records which skill commit the app carries. The app asks only for the `vedic,western,numerology` modules; the slow life-events layer (`events`) is left out.

## Building locally

Android Studio with JDK 17, and Python 3.13 on the computer (Chaquopy uses it to install the app's Python packages). There is no Gradle wrapper yet: run `gradle wrapper --gradle-version 8.14.3` once, or let Android Studio use Gradle 8.14.3. Put the pyswisseph Android wheels from a CI run's `wheels` artifact into `./wheels` first.

Pinned versions: Android Gradle Plugin 8.13.2, Gradle 8.14.3, Kotlin 2.2.21, Chaquopy 17.1.0 (Python 3.13), compileSdk and targetSdk 36, minSdk 26.

## Release build

`gradle :app:bundleRelease` (or `assembleRelease`). Signing comes from `JYOTISH_KEYSTORE`, `JYOTISH_KEYSTORE_PASSWORD`, `JYOTISH_KEY_ALIAS` and `JYOTISH_KEY_PASSWORD`; without them the release is signed with the committed test key (`keystore/README.md`), so test builds install over each other, and must not be uploaded. Keep `mapping.txt` from each uploaded build.

## Licence note

Swiss Ephemeris is dual-licensed (AGPL or Astrodienst's professional licence). Keep this repository private and do not distribute the app until that choice is made.
