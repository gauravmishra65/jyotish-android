"""Build the offline place list the app searches (app/src/main/assets/places.tsv).

Usage:  pip install geonamescache==3.0.2 && python tools/make_places.py

Source: GeoNames (CC BY 4.0, https://www.geonames.org) as packaged by geonamescache (MIT): every place with
5,000 or more people, with coordinates and IANA time zone. Indian places also carry their Devanagari names
so the list can be searched in Hindi.

Format: first line "#tz<TAB>zone1<TAB>zone2...", second line "#cc<TAB>IN=India<TAB>..."; then one place per line:
name, country code, latitude, longitude, time-zone index, population, Devanagari names (joined by "|").
"""
import json
import os
import re
import unicodedata

import geonamescache

DATA = os.path.join(os.path.dirname(geonamescache.__file__), "data")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app", "src", "main", "assets", "places.tsv")
PLAIN = {"IN", "NP", "PK", "BD", "LK", "BT"}   # GeoNames writes these with scholarly accents (Morādābād); show Moradabad


def plain(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

DEVANAGARI = re.compile(r"[ऀ-ॿ]")


def main():
    cities = json.load(open(os.path.join(DATA, "cities5000.json"), encoding="utf-8")).values()
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
        rows.append(f'{name}\t{c["countrycode"]}\t{c["latitude"]:.4f}\t{c["longitude"]:.4f}\t{zi[c["timezone"]]}\t{c["population"]}\t{"|".join(hi)}')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("#tz\t" + "\t".join(zones) + "\n")
        f.write("#cc\t" + "\t".join(f"{k}={v}" for k, v in sorted(countries.items())) + "\n")
        f.write("\n".join(rows) + "\n")
    print(f"wrote {OUT}: {len(rows)} places, {len(zones)} time zones, {os.path.getsize(OUT) // 1024} KB")


if __name__ == "__main__":
    main()
