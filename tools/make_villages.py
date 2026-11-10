"""Build the offline village and small-town database (app/src/main/assets/villages.db.gz) from the full GeoNames
country files, for the places too small for places.tsv.

Usage (GitHub Actions runs this, see .github/workflows/places.yml):
  python tools/make_villages.py DIR      # DIR holds IN.txt, NP.txt, admin1CodesASCII.txt, admin2Codes.txt

Source: GeoNames (CC BY 4.0, https://www.geonames.org). Every populated place (feature class P) in India and Nepal
except sections of cities, historical, abandoned and destroyed places, and those already in places.tsv. Each row
keeps its district and state so places with the same name can be told apart, and Devanagari names for Hindi search.

Tables:  place(id, name, cc, lat, lon, tz, district, state)   name(key, id)  with an index on name(key).
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
    db.execute("CREATE TABLE place(id INTEGER PRIMARY KEY, name TEXT, cc TEXT, lat REAL, lon REAL, tz TEXT, district TEXT, state TEXT)")
    db.execute("CREATE TABLE name(key TEXT, id INTEGER)")
    n_places = n_names = 0
    counts = {}
    for cc in COUNTRIES:
        for line in open(os.path.join(src, f"{cc}.txt"), encoding="utf-8"):
            f = line.rstrip("\n").split("\t")
            if len(f) < 18 or f[6] != "P" or f[7] in SKIP or f[0] in have or not f[17]:
                continue
            gid = int(f[0])
            name = "".join(c for c in unicodedata.normalize("NFD", f[1]) if unicodedata.category(c) != "Mn")
            state = adm1.get(f"{cc}.{f[10]}", "")
            district = adm2.get(f"{cc}.{f[10]}.{f[11]}", "")
            db.execute("INSERT INTO place VALUES (?,?,?,?,?,?,?,?)",
                       (gid, name, cc, round(float(f[4]), 4), round(float(f[5]), 4), f[17], district, state))
            keys = {fold(name), fold(f[2])}
            keys |= {a.strip() for a in f[3].split(",") if DEV.search(a)}            # Devanagari names as they are
            for k in keys:
                if len(k) >= 2:
                    db.execute("INSERT INTO name VALUES (?,?)", (k, gid))
                    n_names += 1
            n_places += 1
            counts[cc] = counts.get(cc, 0) + 1
    db.execute("CREATE INDEX name_key ON name(key)")
    db.commit()
    db.execute("VACUUM")
    db.close()
    with open(tmp, "rb") as a, gzip.open(OUT, "wb", compresslevel=9) as b:
        shutil.copyfileobj(a, b)
    print(f"places {n_places} {counts}, names {n_names}, db {os.path.getsize(tmp) // 1024 // 1024} MB, "
          f"gz {os.path.getsize(OUT) // 1024 // 1024} MB")


if __name__ == "__main__":
    main(sys.argv[1])
