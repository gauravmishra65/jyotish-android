# Unlock codes (demo edition)

The demo edition keeps one Kundli. A buyer opens **Settings > Unlock the full version** (or taps **+ New**), pays,
and enters an unlock code made for their email address. The app checks the code offline with the public key in
`app/src/main/java/com/gauravmishra/jyotish/store/Licence.kt`.

* **Private key:** `gaurav-jyotish-unlock-private-key.pem`. Keep it somewhere private and backed up (a password
  manager or an encrypted drive). Never commit it: `*.pem` is in `.gitignore`. Anyone with it can make codes. If it
  is lost, new codes cannot be made for the current app; a new key pair means a new app build.
* **Make a code:** `python3 tools/licence/make_code.py --key /path/to/gaurav-jyotish-unlock-private-key.pem buyer@example.com`
  (needs `pip install cryptography`), or use the Unlock Code Maker page, which reads the key file in your browser
  and sends it nowhere.
* **Format:** `GJ1-` and base32 of an ECDSA P-256 / SHA-256 signature over `GJ1|<email in lower case>`. Spaces, dashes
  and letter case are ignored when the buyer pastes it.
* A code works only with the email it was made for. It is not tied to a phone, so a buyer can reinstall or move
  phones with the same code. Sharing a code is possible; the "Licensed to <email>" line in the app shows whose it is.

The Play edition does not show codes or payment links (Google Play requires its own billing for digital unlocks in
apps it distributes); it sells the in-app product `full_unlock` instead.
