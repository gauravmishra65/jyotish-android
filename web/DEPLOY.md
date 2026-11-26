# Putting the site on a domain

The site is static: HTML, one stylesheet, three scripts, no build step at serve time and
no server-side anything. Any static host runs it. These are the steps in the order they
have to happen.

## 1. Verify before you build

```sh
python3 web/verify.py
```

It must print `passed`. It refuses to run if Swiss Ephemeris cannot find the app's `.se1`
files, because a verification against a silently substituted reference is worthless. If it
fails, nothing below should happen.

## 2. Build with the real domain

```sh
python3 web/build.py --base https://yourdomain.com
```

Without `--base` you get the pages but no `sitemap.xml`, no `robots.txt` and no canonical
tags — deliberately, since a canonical pointing at a domain that does not exist is worse
than none. With it you get 90 pages, the sitemap listing every one, and `robots.txt`
pointing at the sitemap.

## 3. Serve it

Any of these, in rough order of how little there is to go wrong:

* **Cloudflare Pages** — connect the repository, set the output directory to `web`, no
  build command. Free tier, global, and the bandwidth is irrelevant at this size.
* **Netlify** — same shape: publish directory `web`, no build command.
* **GitHub Pages** — works, but serves from the repository, so the `.se1` files and the
  Android source would be public at a URL as well as in the repository. Given the open
  question about whether those files may sit in a public repository at all, this is the
  one to avoid until Astrodienst answer.

Point the apex domain and `www` at whichever you pick, and let the host issue the
certificate. `index.html` is the front door; `nakshatra.html` and `rashi.html` are the two
hubs most search traffic will land on directly, and `method.html` is where the accuracy
figures live so the other pages can link to one copy of them.

For an artifact preview rather than a domain, `python3 web/stage.py <dir>` makes the one
adjustment that needs: an artifact reserves `index.html` for its own entry page, so the home
page is staged as `home.html` with every link to it rewritten. A real host needs none of it.

## 4. Tell Google it exists

Verify the domain in Search Console by DNS record, then submit `sitemap.xml`. Then stop.
Resubmitting a sitemap does not make indexing faster, and the eight-week wait in the plan
starts here rather than when the pages were written.

## What must not drift

* **No third-party requests.** The privacy page invites the reader to open their Network
  tab and see only this site's own files. That is currently true: there are no webfonts, no
  analytics, no pixels, no embedded anything. Adding Google Analytics, a Google Font or a
  chat widget breaks the one claim the site is built on, and a sceptical visitor following
  the page's own instructions is exactly who will notice. If measurement is needed, use the
  host's own server-side request logs, which see no birth data because none is sent.
* **No birth data to a server, ever.** Including the paid report, when it exists: take the
  payment, build the report in the browser, store nothing but the order.
* **The accuracy figures on the pages are measured, not decorative.** `Engine.accuracy` in
  `engine.js` and the tolerance paragraph on the dasha page quote numbers that `verify.py`
  prints. If the engine changes, both move with it in the same commit.
