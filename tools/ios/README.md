# iOS groundwork

Nothing here builds an iOS app. This is the one experiment worth running before anyone decides to write one.

## What is being tested, and why

An iOS port has three unknowns. Two are ordinary work: rewriting the interface in SwiftUI, and swapping Play
Billing for StoreKit. The third is the only one that could stop the port outright — whether the astrology engine
can run on an iPhone at all.

The Python layer is already platform-neutral: no module under `app/src/main/python/` imports anything from
Chaquopy or Android, and the 926-check verification suite runs on desktop CPython. The risk sits entirely in
**pyswisseph**, whose C extension has no iOS wheels, and in Apple's rule that every binary must live inside a
signed framework rather than being loaded as a loose `.so`.

`.github/workflows/ios-engine.yml` cross-compiles pyswisseph for the device (`arm64_iphoneos`) and the simulator
(`arm64_iphonesimulator`), then runs `swisseph_check.py` **inside a simulator**. The check compares Swiss
Ephemeris output against values taken from the same library on Linux, where the verification suite passes:

| Check | Expected |
| --- | --- |
| `julday` at J2000 noon | 2451545.0 |
| Sun, tropical | 280.368920° |
| Lahiri ayanamsa | 23.857092° |
| Moon, sidereal | 199.470553° |
| Ascendant, Placidus (Varanasi, 14 Jul 1988) | 234.689115° |
| Sun, sidereal, same chart | 88.436831° |

Agreement to a millionth of a degree means the ephemeris, the sidereal modes and the house calculations all
behave identically on Apple's runtime. Disagreement means the port is not safe and the reason must be found
before any app work starts.

## Running it

The workflow is manual, because macOS runners bill at ten times the Linux rate:

```
gh workflow run ios-engine.yml
```

The device wheel is built but not tested: cibuildwheel can only run tests on a simulator matching the build
machine, and physical devices are not available in CI. The `vtool -show-build` step is there to prove the
device slice really targets iOS rather than macOS.

## What a green run does not tell you

* Nothing about the interface. All 40 Compose screens would still need rewriting in SwiftUI.
* Nothing about licensing. The App Store's terms conflict with the AGPL, so an iOS release needs the Swiss
  Ephemeris professional licence from Astrodienst — the free route that is still open on Android is closed here.
* Nothing about embedding. Running the extension under cibuildwheel's harness is not the same as initialising
  the interpreter inside a real app bundle, converting each `.so` into a `.framework`, and signing it. That work
  follows, and only makes sense once the licence question is settled.
