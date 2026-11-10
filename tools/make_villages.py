"""Build the offline village and small-town database (app/src/main/assets/villages.db.gz) from the full GeoNames
country files, for the places too small for places.tsv.

Usage (GitHub Actions runs this, see .github/workflows/places.yml):
  python tools/make_villages.py DIR      # DIR holds IN.txt, NP.txt, admin1CodesASCII.txt, admin2Codes.txt

Source: GeoNames (CC BY 4.0, https://www.geonames.org). Every populated place (feature class P) in India and Nepal
except sections of cities, historical, abandoned and destroyed places, and those already in places.tsv. Each row
keeps its district and state so places with the same name can be told apart, and Devanagari names for Hindi search.

Tables (compact: district/state and time zone stored once, coordinates as degrees x 10,000):
  place(id, name COLLATE NOCASE, cc, lat, lon, tz, region)  region(id, district, state)  tz(id, name)  hindi(key, id)
  with indexes on place(name) and hindi(key).
"""
import gzip
import os
import re
import shutil
import sqlite3
import sys
import unicodedata

import geonamescache

COUNTRIES = ("IN", "NP")
SKIP = {"PPLX", "PPLH", "PPLQ", "PPLW", "PPLCH"}
DEV = re.compile(r"[ऀ-ॿ]")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app", "src", "main", "assets", "villages.db.gz")


def fold(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower().strip()


def main(src):
    data = os.path.join(os.path.dirname(geonamescache.__file__), "data")
    import json
    have = set(json.load(open(os.path.join(data, "cities500.json"), encoding="utf-8")).keys())
    adm1 = {}
    for line in open(os.path.join(src, "admin1CodesASCII.txt"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        adm1[f[0]] = f[2] or f[1]
    adm2 = {}
    for line in open(os.path.join(src, "admin2Codes.txt"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if f[0][:2] in COUNTRIES:
            adm2[f[0]] = f[2] or f[1]
    tmp = os.path.join(src, "villages.db")
    if os.path.exists(tmp):
        os.remove(tmp)
    db = sqlite3.connect(tmp)
    db.execute("PRAGMA page_size=4096")
    # compact: district/state and time zone stored once; coordinates as integers (degrees x 10,000)
    db.execute("CREATE TABLE region(id INTEGER PRIMARY KEY, district TEXT, state TEXT)")
    db.execute("CREATE TABLE tz(id INTEGER PRIMARY KEY, name TEXT)")
    db.execute("CREATE TABLE place(id INTEGER PRIMARY KEY, name TEXT COLLATE NOCASE, cc TEXT, lat INTEGER, lon INTEGER, tz INTEGER, region INTEGER)")
    db.execute("CREATE TABLE hindi(key TEXT, id INTEGER)")
    regions, zones, rows = {}, {}, []
    counts = {}
    for cc in COUNTRIES:
        for line in open(os.path.join(src, f"{cc}.txt"), encoding="utf-8"):
            f = line.rstrip("\n").split("\t")
            if len(f) < 18 or f[6] != "P" or f[7] in SKIP or f[0] in have or not f[17]:
                continue
            name = "".join(c for c in unicodedata.normalize("NFD", f[1]) if unicodedata.category(c) != "Mn").strip()
            if len(name) < 2:
                continue
            reg = (adm2.get(f"{cc}.{f[10]}.{f[11]}", ""), adm1.get(f"{cc}.{f[10]}", ""))
            rid = regions.setdefault(reg, len(regions) + 1)
            zid = zones.setdefault(f[17], len(zones) + 1)
            hi = sorted({a.strip() for a in f[3].split(",") if DEV.search(a)})
            rows.append((name, cc, round(float(f[4]) * 10000), round(float(f[5]) * 10000), zid, rid, hi))
            counts[cc] = counts.get(cc, 0) + 1
    rows.sort(key=lambda r: r[0].lower())          # name order keeps a prefix search on neighbouring pages
    db.executemany("INSERT INTO region VALUES (?,?,?)", [(i, d, st) for (d, st), i in regions.items()])
    db.executemany("INSERT INTO tz VALUES (?,?)", [(i, z) for z, i in zones.items()])
    db.executemany("INSERT INTO place VALUES (?,?,?,?,?,?,?)", [(i + 1,) + r[:6] for i, r in enumerate(rows)])
    hindi = [(h, i + 1) for i, r in enumerate(rows) for h in r[6]]
    db.executemany("INSERT INTO hindi VALUES (?,?)", hindi)
    n_places, n_names = len(rows), len(hindi)
    db.execute("CREATE INDEX place_name ON place(name COLLATE NOCASE)")
    db.execute("CREATE INDEX hindi_key ON hindi(key)")
    db.commit()
    db.execute("VACUUM")
    db.close()
    with open(tmp, "rb") as a, gzip.open(OUT, "wb", compresslevel=9) as b:
        shutil.copyfileobj(a, b)
    print(f"places {n_places} {counts}, hindi names {n_names}, regions {len(regions)}, db {os.path.getsize(tmp) // 1024 // 1024} MB, "
          f"gz {os.path.getsize(OUT) // 1024 // 1024} MB")


if __name__ == "__main__":
    main(sys.argv[1])
