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
