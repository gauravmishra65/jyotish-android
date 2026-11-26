# Swiss Ephemeris licence: what applies to this project

Read from the Professional licence contract, English version 2026-09 (update 9 Nov 2026),
at <https://www.astro.com/swisseph/secont_e_2609.pdf> — fetch it with a hard reload, since
Astrodienst update it in place. **This file is a working summary, not the contract, and not
legal advice. Read the contract itself before signing it.**

Astrodienst's reply of 26 Nov 2026 also settles one point that the repositories do not:

> Re pyswisseph: we recommend pysweph; but also pyswisseph is covered, even when its git
> repository does not say so.

which matches clause 13, where bindings must be available under both the AGPL and the
professional licence. The app's use of `pyswisseph` is therefore fine as it stands.

## Clause by clause, as it touches this project

| # | Clause | Where we stand |
| --- | --- | --- |
| 1 | Package is C source, docs, demos and **proprietary compressed data files** | We ship four: `semo_18.se1`, `sepl_18.se1`, `seas_18.se1`, `sefstars.txt` |
| 2 | Covers distributed apps and server software calling Swiss Ephemeris, including apps asking a server | Covers the Android app, the Windows edition and the planned web calculators |
| 3 | Third parties using **our API** need their own licence; we must document that and report their identities | Not applicable yet. It constrains any future public API, and the plan should not assume otherwise |
| 4 | Six-year term, then renew or stop | Diarise six years from the payment date |
| 5 | Distributing source is optional; if we do, it must be the complete original, and modifications fall under AGPL | See the open question below about the public repository |
| 6 | May use the **SWISS EPHEMERIS** and **SWISS EPHEMERIS Inside** labels | This is the permitted form of credit, and what the app now uses |
| 7 | Must supply a free copy of any distributed app on request | Nothing to do until asked |
| 8 | No warranty, no guarantee of accuracy | Our own wording already avoids guaranteeing results |
| 9 | **Must not name Astrodienst or the authors** in software, documentation or advertising without written permission for each case | **Was being breached.** The Licences screen read "Swiss Ephemeris by Astrodienst AG" in both languages; corrected to "Swiss Ephemeris", which clause 6 permits |
| 10 | Must not remove or alter copyright notices in source, library or data files | The `.se1` files are shipped byte-for-byte; their internal notice is intact |
| 11 | Support is the community mailing list | — |
| 12 | Extra asteroid files from the public GitHub areas | Not needed |
| 13 | Bindings and ports must be available under AGPL and the professional licence | `pyswisseph` confirmed covered, see above |
| 14 | Pay through the online shop; **the licence is valid only after full payment** | Signing and emailing the contract is not enough on its own |
| 15 | Transferable, with notice by email | — |
| 16 | Renewal at no more than the original fee plus Swiss inflation | Clauses 4 and 16 both cover renewal and read slightly differently |
| 17 | Jurisdiction: Meilen, Canton Zürich | — |

## Ordering, in the order it has to happen

1. Download the contract from the link above with a hard reload.
2. Fill in name, address, phone and email; sign and date it.
3. Email the signed contract to `order@astro.com`.
4. **Pay through the Astrodienst online shop**, via the "Purchase six-year license" link on
   <https://www.astro.com/swisseph/swephprice_e.htm>. Clause 14: not valid until paid.

An email asking about licensing is not part of this sequence, which is why one gets the
reply pointing at the documents.

## Genuinely open questions

Astrodienst asked for questions not already answered in the contract and not inferable from
it. These two qualify; the rest of the above does not, and should not be sent.

1. **The public repository.** `github.com/gauravmishra65/jyotish-android` is public and
   contains the four `.se1` data files, which clause 1 calls proprietary. Clause 5 addresses
   distributing *source code*, and permits it if complete and unmodified, but the data files
   are not source. Is publishing them in a public application repository within the licence,
   or should they be excluded and fetched at build time?
2. **Shipping the library to browsers.** The web plan compiles Swiss Ephemeris to
   WebAssembly so that the calculation runs in the visitor's browser and no birth data
   reaches a server. The compiled library and the data files are then served to every
   visitor. Clause 2 covers "apps that request calculations from a server"; this is the
   reverse. Is a WebAssembly build served to browsers covered by the same licence, and does
   clause 3 bear on it, given that visitors are not third-party businesses calling an API?

Both bear on decisions that cannot be made without an answer, which is the test their reply
set.

## "Can we just use the public data instead?"

Not without choosing a licence. The public GitHub repository is where **both** kinds of
licensee download from — clause 1 says so explicitly. Public availability says nothing
about what you may then do with it. There are exactly two options, and the free one is
real but has a price.

### The free option: AGPL-3.0

It permits everything the professional licence permits, and adds three obligations:

* the **entire** work that links Swiss Ephemeris goes under AGPL or a compatible licence
  — the Android app, the Windows edition and the web pages alike;
* complete corresponding source to everyone you distribute to;
* the network clause: people who use it over a network must be offered the source too,
  which reaches every visitor to the web calculators.

Selling is still allowed. The AGPL has never forbidden charging money. What it forbids is
stopping the recipient from passing it on. So anyone who buys the full version may legally
rebuild it and publish it for nothing, and `full_unlock` is a conditional in source code
that anybody may fork out. **That, not the open-sourcing, is what the free option costs.**

Note also that a public repository is not the same as an AGPL one. This repository has no
LICENSE file, which makes it all-rights-reserved by default and satisfies neither option.

### The paid option: CHF 700 for six years

Buys one thing that matters: the code stays closed, so the unlock stays meaningful. Also
unlimited projects, so Android, Windows and web are covered by the single purchase, and the
clause 6 labels.

CHF 700 over six years is about CHF 117 a year, which at USD 12 a report is roughly ten
sales a year. Against the revenue plan it is not a real number.

### The third option: stop using Swiss Ephemeris

Genuinely available, and worth stating so the choice is informed. `astronomy-engine` and
`astronomia` are both MIT, and `web/moon.js` in this repository is Meeus' published method
rather than Astrodienst's code or data, so it carries no obligation at all.

The cost is everything built on the current engine: the nine grahas, the ascendant, houses,
the sixteen divisional charts, Shadbala, Ashtakavarga, transits, and the 926-check
verification suite that is anchored to Swiss Ephemeris as its reference. Replacing that to
save CHF 117 a year is months of work and a worse product.

### Where this project actually stands

A closed-source app is live on Google Play with an active in-app purchase, built from a
public repository with no LICENSE file. That is not the free option and not the paid one.
The question is not whether to pick one, but which — and the free one removes the thing
being sold.

## "Can it wait until there are a few customers?"

No clause makes the licence conditional on revenue, customers or scale. Clause 2 attaches it
to **distributed apps and server software**, so the trigger was publication, not the first
sale — and publication happened on 22 November 2026, to 178 countries.

That means there is no compliant wait-and-see state. The three lawful positions are:

1. professional licence, code stays closed;
2. AGPL, whole project open, source to every recipient;
3. not distributing.

"Published, closed-source, unlicensed" is none of them, and taking the in-app purchase down
does not cure it — the AGPL's obligation is triggered by distribution, paid or free.

Two things worth being honest about. First, the practical risk today is low: nobody audits a
seven-install app, and Astrodienst are not scanning Google Play. Second, that stops being
true exactly when the plan works. Astrodienst sell natal reports at USD 26.90 and are in
this market; a site ranking on nakshatra queries is the thing they would notice, clause 7
lets them request a free copy of any distributed app, and the consequence is not a fine but
a takedown or a demand to open-source everything — arriving at the moment the business is
finally earning. The exposure is small now and grows in step with the thing it would destroy.

The arithmetic also does not work the way the question assumes. Five customers at USD 12 is
about USD 60. The licence is on the order of sixty reports, depending on the rate on the
day. So waiting for five customers does not fund it; waiting for sixty would. This is a
decision about risk, not affordability — and at roughly CHF 117 a year it is the cheapest
risk reduction available anywhere in this project.
