# The four things only you can do

Everything else in this project can be done from a session. These four cannot, because each
one needs a signature, a payment, a Google account or a press of Publish. They are ordered by
what they block.

Each section says what the step is, what is already prepared, and what happens next once it
is done.

---

## 1. The Swiss Ephemeris professional licence

**Why this one is first.** The app has been distributed since 22 November. Clause 2 attaches
the licence to distribution, not to the first sale, so there are only three lawful positions —
professional licence with the code closed, AGPL with the whole project opened, or not
distributing — and "published, closed-source, unlicensed" is not one of them. The free route
is also closed in practice: `billing-ktx` and `play:review` are Android SDK Licence and cannot
coexist with the AGPL, so going free means giving up in-app purchase, and an AGPL release
cannot be withdrawn from copies already taken. A purchase can always be made later; an
open-sourcing cannot be undone. CHF 700 for six years, about CHF 117 a year, roughly sixty
reports at USD 12.

**The sequence, which clause 14 makes strict — the licence is not valid until paid:**

1. Download the contract from <https://www.astro.com/swisseph/secont_e_2609.pdf> with a hard
   reload. Astrodienst update it in place, so a cached copy may be the wrong version.
2. Fill in name, address, phone, email. Sign and date it.
3. Email the signed contract to `order@astro.com`.
4. Pay through the shop, via "Purchase six-year license" on
   <https://www.astro.com/swisseph/swephprice_e.htm>.

**A draft for step 3**, to adjust rather than write from scratch:

> Subject: Signed professional licence contract — Gaurav Jyotish (Android, Windows, web)
>
> Dear Astrodienst,
>
> Attached is the professional licence contract, signed and dated, for Gaurav Jyotish — an
> Android application published on Google Play, a Windows edition, and a set of web
> calculators in preparation. I am paying through the online shop today.
>
> Two questions the contract does not settle, which I would be grateful to have your view on:
>
> 1. The application repository at github.com/gauravmishra65/jyotish-android is public and
>    contains the four Swiss Ephemeris data files (`semo_18.se1`, `sepl_18.se1`,
>    `seas_18.se1`, `sefstars.txt`), which clause 1 describes as proprietary. Clause 5
>    addresses distributing source code and permits it when complete and unmodified, but the
>    data files are not source. Is publishing them in a public application repository within
>    the licence, or should they be excluded from the repository and fetched at build time?
>
> 2. The web calculators are planned as a WebAssembly build of the library, served to the
>    visitor's browser so that the calculation happens on their device and no birth data
>    reaches a server. That necessarily delivers the compiled library and the data files to
>    every visitor. Is that within clause 2's "distributed apps", or does it need separate
>    agreement?
>
> With thanks,
> Gaurav Mishra

Nothing else from `docs/licence/swiss-ephemeris.md` should be sent: Astrodienst asked for
questions not already answered in the contract, and the rest are.

**After payment:** diarise six years from the payment date (clause 4), and tell me — the
WebAssembly build of the engine becomes possible, which is what the deferred page families
(panchang, lagna, the full chart, Western and BaZi on the site) are waiting for. The repo
should also go private until question 1 above is answered.

---

## 2. A domain

The site is finished and has nowhere to live. 90 pages, English and Hindi, no server and no
third-party request of any kind.

**What to buy.** A plain `.com` on the brand, registered for the long term rather than a year,
with WHOIS privacy on. A cheap registrar is fine; this is a name, not a service. Avoid
`.app` for this one: it forces HTTPS, which is no problem, but it reads as software rather
than as a place to look something up, and the audience here arrives from a search for
"my nakshatra", not from a store.

**Then, in this order** — the detail is in `web/DEPLOY.md`:

1. `python3 web/verify.py` — it must print `passed`.
2. `python3 web/build.py --base https://yourdomain.com` — this is what writes `sitemap.xml`,
   `robots.txt` and the canonical tags. Without the real domain they are deliberately absent.
3. Cloudflare Pages or Netlify, publish directory `web`, no build command. Not GitHub Pages:
   it serves from the repository, which would put the `.se1` files on a public URL as well as
   in a public repo, and that is open question 1 above.
4. Verify the domain in Search Console by DNS record, submit `sitemap.xml`, and then stop.
   The eight-week wait in the plan starts here.

Tell me the domain and I will do steps 1 to 3's file changes in one commit.

---

## 3. Reset the upload key

**What happened.** Play locks in the certificate of the *first* bundle ever uploaded as the
upload certificate, permanently. For this app that was the test key, which is committed to a
public repository. It works — 1.0.0 went to production with it, and the release build checks
every bundle against its fingerprint — but an upload key is meant to be the one thing only
you hold, and this one is public.

```
Play Console → App integrity → App signing → Request upload key reset
```

The procedure, the fingerprints and what to set afterwards are in `docs/PLAY_LISTING.md`
under "Before uploading". The short version: generate a new key on your own machine, keep it
off the repository, send Play the certificate, and once they switch it over set
`JYOTISH_UPLOAD_KEYSTORE_B64`, `JYOTISH_UPLOAD_KEYSTORE_PASSWORD` and
`JYOTISH_UPLOAD_KEY_ALIAS` in the repository secrets. The build already uses them when they
exist and falls back to the test key when they do not, so nothing breaks in between.

There is also an older loose end here: `gaurav-jyotish-unlock-private-key.pem`, the key that
signs full-version unlock codes, was never found on your disk and the public half entered the
repository in the first commit. If it is genuinely gone, the unlock scheme needs a new keypair
and a new app version that trusts it. `find_unlock_key.ps1` in your Downloads searches the
whole disk for it; running it once would settle the question.

---

## 4. The listing icon, and the 1.0.1 release

**The icon.** The live listing still shows the gold yantra the app used before 1.0.0. The cat
is at `docs/store/play-icon-512.png`, 512 × 512, already the right size and format.

```
Play Console → Grow → Store presence → Main store listing → App icon
```

**The release.** 1.0.1 (32) exists for one reason: the Licences screen stopped naming
Astrodienst a week ago (clause 9), and the published build still carries the old text, so the
breach is live and the correction is not. The signed bundle is built by CI and waits in a
draft release on GitHub; release notes in both languages are in
`docs/store/release-notes-1.0.1.txt`.

```
Play Console → Production → Create new release → upload the .aab → paste the notes → Save
```

Managed publishing is on, so saving puts both the icon and the release into "Changes ready to
publish" and nothing reaches anyone until you press **Publish**. I will not press it.
