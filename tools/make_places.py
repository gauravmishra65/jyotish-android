"""Build the offline place list the app searches (app/src/main/assets/places.tsv).

Usage:  pip install geonamescache==3.0.2 && python tools/make_places.py

Source: GeoNames (CC BY 4.0, https://www.geonames.org) as packaged by geonamescache (MIT): every place with
5,000 or more people, and in South Asia every place with 500 or more, with coordinates and IANA time zone.
Indian and Nepali places also carry their Devanagari names so the list can be searched in Hindi, and South Asian
places carry their other English spellings and old names (Bombay, Calcutta, Allahabad, Gurgaon) for search.

Format: first line "#tz<TAB>zone1<TAB>zone2...", second line "#cc<TAB>IN=India<TAB>..."; then one place per line:
name, country code, latitude, longitude, time-zone index, population, Devanagari names (joined by "|"),
other spellings (joined by "|").
"""
import json
import os
import re
import unicodedata

import geonamescache

DATA = os.path.join(os.path.dirname(geonamescache.__file__), "data")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app", "src", "main", "assets", "places.tsv")
PLAIN = {"IN", "NP", "PK", "BD", "LK", "BT"}
SOUTH_ASIA = PLAIN   # GeoNames writes these with scholarly accents (Morādābād); show Moradabad


def plain(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

DEVANAGARI = re.compile(r"[ऀ-ॿ]")


def other_spellings(c, name, limit=30):
    """Other English spellings and old names (Bombay, Calcutta): capitalised Latin words, no codes, not the name itself."""
    seen, out = {name.lower()}, []
    for a in c.get("alternatenames", []):
        a = plain(a).strip()
        if len(a) < 4 or " - " in a or not a[0].isupper() or a.isupper() or not all(ch.isascii() and (ch.isalpha() or ch in " -.'") for ch in a):
            continue
        if a.lower() in seen:
            continue
        seen.add(a.lower())
        out.append(a)
        if len(out) >= limit:
            break
    return out


def main():
    world = json.load(open(os.path.join(DATA, "cities5000.json"), encoding="utf-8"))
    small = json.load(open(os.path.join(DATA, "cities500.json"), encoding="utf-8"))
    for k, c in small.items():          # smaller towns in South Asia
        if c["countrycode"] in SOUTH_ASIA and k not in world:
            world[k] = c
    cities = world.values()
    countries = {c["iso"]: c["name"] for c in json.load(open(os.path.join(DATA, "countries.json"), encoding="utf-8")).values()}
    zones = sorted({c["timezone"] for c in cities if c.get("timezone")})
    zi = {z: i for i, z in enumerate(zones)}
    rows = []
    for c in sorted(cities, key=lambda c: -c["population"]):
        if not c.get("timezone"):
            continue
        hi = sorted({a for a in c.get("alternatenames", []) if DEVANAGARI.search(a)}) if c["countrycode"] in ("IN", "NP") else []
        name = c["name"].replace("\t", " ")
        if c["countrycode"] in PLAIN:
            name = plain(name)
        alt = other_spellings(c, name) if c["countrycode"] in SOUTH_ASIA else []
        rows.append(f'{name}\t{c["countrycode"]}\t{c["latitude"]:.4f}\t{c["longitude"]:.4f}\t{zi[c["timezone"]]}\t{c["population"]}\t{"|".join(hi)}\t{"|".join(alt)}')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("#tz\t" + "\t".join(zones) + "\n")
        f.write("#cc\t" + "\t".join(f"{k}={v}" for k, v in sorted(countries.items())) + "\n")
        f.write("\n".join(rows) + "\n")
    print(f"wrote {OUT}: {len(rows)} places, {len(zones)} time zones, {os.path.getsize(OUT) // 1024} KB")


if __name__ == "__main__":
    main()
