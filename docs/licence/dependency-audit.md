# Can this project go AGPL? A dependency audit

Checked on 27 Nov 2026, because "use the free licence instead of paying" only works if every
component can live under the AGPL. Most can. Two cannot, and they are the two that make the
money.

**Not legal advice.** This records what each licence says and what is in the shipped binaries.

## Every component, against AGPL-3.0

| Component | Licence | AGPL-compatible | Note |
| --- | --- | --- | --- |
| Swiss Ephemeris | AGPL-3.0 or Professional | — | This is the obligation itself |
| pyswisseph | AGPL via clause 13 | yes | Astrodienst confirmed by email, 26 Nov |
| `.se1` data files | AGPL route permits redistribution | yes | astro.com: AGPL lets you "use, copy, modify and redistribute Swiss Ephemeris", notices preserved |
| Chaquopy | MIT | yes | |
| androidx.* (Compose, core, work, navigation, lifecycle) | Apache-2.0 | yes | Apache-2.0 is one-way compatible into AGPL-3.0 |
| kotlinx-coroutines-android | Apache-2.0 | yes | |
| geonamescache | MIT | yes | |
| GeoNames place data | CC BY 4.0 | yes | |
| **com.android.billingclient:billing-ktx** | Android SDK Licence | **no** | Categorised [Proprietary Free](https://scancode-licensedb.aboutcode.org/android-sdk-license.html); s.3.4 forbids distributing software incorporating or combined with it |
| **com.google.android.play:review** | Android SDK Licence | **no** | Same |

Both incompatible entries are `playImplementation`, so they are in the Play edition only.
Confirmed in the artifacts rather than taken from the build file:

```
app-play-release.aab      billing/review symbols: 4
GauravJyotish-1.0.0.apk   billing/review symbols: 0
```

## Why the exception trick does not work here

The usual remedy when GPL code meets a proprietary library is for the copyright holder to
grant a linking exception. That is unavailable in this case. The AGPL obligation comes from
Swiss Ephemeris, which Astrodienst own, and only they can grant an exception to it. Owning
the copyright in the surrounding application does not help: you cannot except somebody
else's AGPL code from its own terms.

So an AGPL build of this project cannot contain Google Play Billing. That is not a drafting
problem to be worked around; it is the licence doing what it was written to do.

## What is and is not possible

| Edition | Links billing | Can ship under AGPL |
| --- | --- | --- |
| `demo` | no | **yes**, today |
| `full` | no | **yes**, today |
| `play` | yes | **no** |

So "go public licence" means giving up Google Play Billing. The demo and full APKs could be
released under AGPL immediately — but their unlock is an ECDSA check in source that anyone
may then fork out, so that route also ends the paywall, by a different road.

## The three honest options

1. **Professional licence, CHF 700 / six years.** Code stays closed, Play Billing is fine,
   the unlock means something. About CHF 117 a year.
2. **AGPL, and no paid tier.** Pull the Play edition or strip billing from it. Open the
   whole project. A free app with a real audience is a respectable thing to have, and the
   web calculators do not depend on this at all. But nothing is sold.
3. **Drop Swiss Ephemeris**, use an MIT engine, keep the code closed and the billing. Months
   of work and a worse engine, as recorded in `swiss-ephemeris.md`.

There is no fourth option where the app keeps its paid unlock on Google Play without the
professional licence.

## One thing that is not blocked

The AGPL/app-store conflict people warn about is largely a misconception: AGPL-3.0's
section 7 lets a recipient remove added restrictions, Android apps ship under GPL licences
routinely, and Google Play is no worse placed than any other store. Play is not the problem
here. The proprietary billing library is.
