"""Finding a birthplace, offline.

A port of Places.kt over the same assets/places.tsv the Android app ships: about 70,000 settlements from
GeoNames with their coordinates, time zone, country and alternative names. The ranking is the same, which
matters more than it sounds - someone who has learned that typing "sitapur up" finds the right Sitapur
should not have to learn something else here.

Nothing is looked up over a network. The file is read once, on the first search.
"""
import unicodedata
from functools import lru_cache
from pathlib import Path

#: Short forms of Indian states as people write them in addresses, so "Sitapur UP" narrows correctly.
STATE_SHORT = {
    "up": "uttar pradesh", "mp": "madhya pradesh", "hp": "himachal pradesh", "ap": "andhra pradesh",
    "uk": "uttarakhand", "ua": "uttarakhand", "wb": "west bengal", "tn": "tamil nadu",
    "jk": "jammu and kashmir", "j&k": "jammu and kashmir", "mh": "maharashtra", "gj": "gujarat",
    "rj": "rajasthan", "pb": "punjab", "hr": "haryana", "br": "bihar", "jh": "jharkhand",
    "cg": "chhattisgarh", "ct": "chhattisgarh", "od": "odisha", "or": "odisha", "orissa": "odisha",
    "ka": "karnataka", "kl": "kerala", "ts": "telangana", "tg": "telangana", "as": "assam",
    "dl": "delhi", "ga": "goa", "ncr": "delhi", "ar": "arunachal pradesh", "mn": "manipur",
    "ml": "meghalaya", "mz": "mizoram", "nl": "nagaland", "sk": "sikkim", "tr": "tripura",
    "py": "puducherry", "pondicherry": "puducherry", "uttaranchal": "uttarakhand",
}

DEVANAGARI = range(0x900, 0x980)


def fold(s: str) -> str:
    """Lower case without accents, so Sao and São are the same word. ASCII skips the Unicode work."""
    if s.isascii():
        return s.lower()
    return "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c)).lower()


def _has_devanagari(s: str) -> bool:
    return any(ord(c) in DEVANAGARI for c in s)


class Place:
    __slots__ = ("name", "country_code", "country", "lat", "lon", "tz", "population",
                 "hindi_names", "other_names", "region", "matched_as", "key", "other_keys")

    def __init__(self, name, country_code, country, lat, lon, tz, population,
                 hindi_names, other_names, region):
        self.name, self.country_code, self.country = name, country_code, country
        self.lat, self.lon, self.tz, self.population = lat, lon, tz, population
        self.hindi_names, self.other_names, self.region = hindi_names, other_names, region
        self.matched_as = None
        self.key = fold(name)
        self.other_keys = [fold(o) for o in other_names]

    def label(self, matched_as=None) -> str:
        bits = f"{self.name} ({matched_as})" if matched_as else self.name
        if self.region:
            bits += f", {self.region}"
        if self.country:
            bits += f", {self.country}"
        return bits

    def as_dict(self, matched_as=None) -> dict:
        return {"name": self.name, "label": self.label(matched_as), "lat": self.lat, "lon": self.lon,
                "tz": self.tz, "country": self.country, "region": self.region,
                "population": self.population}


def data_file() -> Path:
    """The same places.tsv the Android app ships. One file, two platforms."""
    here = Path(__file__).resolve().parent
    for candidate in (here / "places.tsv",                                       # packaged
                      here.parent.parent / "app" / "src" / "main" / "assets" / "places.tsv",
                      here.parent / "places.tsv"):
        if candidate.exists():
            return candidate
    raise FileNotFoundError("places.tsv was not found; place search cannot work without it.")


class Places:
    def __init__(self, path: Path | None = None):
        self.places: list[Place] = []
        self.countries: dict[str, str] = {}
        self._load(path or data_file())

    def _load(self, path: Path) -> None:
        zones: list[str] = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line:
                    continue
                if line.startswith("#tz\t"):
                    zones = line.split("\t")[1:]
                    continue
                if line.startswith("#cc\t"):
                    for kv in line.split("\t")[1:]:
                        code, _, name = kv.partition("=")
                        if name:
                            self.countries[code] = name
                    continue
                f_ = line.split("\t")
                if len(f_) < 6:
                    continue
                try:
                    tz = zones[int(f_[4])] if int(f_[4]) < len(zones) else "UTC"
                    self.places.append(Place(
                        f_[0], f_[1], self.countries.get(f_[1], f_[1]),
                        float(f_[2]), float(f_[3]), tz, int(f_[5]),
                        f_[6].split("|") if len(f_) > 6 and f_[6] else [],
                        f_[7].split("|") if len(f_) > 7 and f_[7] else [],
                        f_[8] if len(f_) > 8 else "",
                    ))
                except (ValueError, IndexError):
                    continue

    # --- searching ------------------------------------------------------------------------------

    def _is_region_word(self, word: str) -> bool:
        f = fold(word)
        if f in STATE_SHORT:
            return True
        if any(fold(c) == f for c in self.countries.values()):
            return True
        return len(f) >= 3 and any(p.region and fold(p.region).startswith(f) for p in self.places)

    def _matches_filter(self, p: Place, token: str) -> bool:
        t = fold(token)
        if not t:
            return True
        state = STATE_SHORT.get(t, t)
        region = fold(p.region)
        return (region.startswith(state) or f" {state}" in region
                or fold(p.country).startswith(t) or p.country_code.lower() == t)

    def _search_name(self, query: str, limit: int) -> list[tuple[Place, str | None]]:
        q = fold(query.strip())
        if len(q) < 2:
            return []
        devanagari = _has_devanagari(query)
        raw = query.strip()
        buckets: list[list[tuple[Place, str | None]]] = [[], [], []]

        for p in self.places:
            alias = None
            if devanagari:
                if any(n.startswith(raw) for n in p.hindi_names):
                    score = 0
                elif any(raw in n for n in p.hindi_names):
                    score = 2
                else:
                    score = -1
            else:
                k = p.key
                if k.startswith(q):
                    score = 0
                elif f" {q}" in k or f"-{q}" in k:
                    score = 1
                elif len(q) >= 3 and q in k:
                    score = 2
                else:
                    score = -1

            # An old name or other spelling - Bombay, Allahabad - when the main name did not match.
            if score < 0 and not devanagari and len(q) >= 3:
                for i, ok in enumerate(p.other_keys):
                    if ok.startswith(q):
                        score, alias = 0, p.other_names[i]
                        break

            if score >= 0 and len(buckets[score]) < limit:
                buckets[score].append((p, alias))
            if len(buckets[0]) >= limit:
                break

        return (buckets[0] + buckets[1] + buckets[2])[:limit]

    def search(self, query: str, limit: int = 8) -> list[dict]:
        """Places matching a query, best first.

        "Sitapur, UP, India" narrows by state and country; "Sitapur UP" does the same without commas,
        because that is how people actually type an address.
        """
        query = (query or "").strip()
        if not query:
            return []

        parts = [p.strip() for p in query.split(",") if p.strip()]
        if len(parts) > 1:
            found = self._search_name(parts[0], limit * 4)
            kept = [(p, a) for p, a in found if all(self._matches_filter(p, t) for t in parts[1:])]
            return [p.as_dict(a) for p, a in kept[:limit]]

        whole = self._search_name(query, limit)
        words = query.split()
        if len(words) >= 2 and not _has_devanagari(query) and self._is_region_word(words[-1]):
            narrowed = [(p, a) for p, a in self._search_name(" ".join(words[:-1]), limit * 4)
                        if self._matches_filter(p, words[-1])]
            if narrowed:
                return [p.as_dict(a) for p, a in narrowed[:limit]]
        return [p.as_dict(a) for p, a in whole]

    def nearest(self, lat: float, lon: float) -> dict | None:
        """The listed place nearest a point, used to name a time zone when coordinates are typed by hand."""
        import math
        if not self.places:
            return None
        k = math.cos(math.radians(lat))

        def d2(p: Place) -> float:
            dx = (((p.lon - lon + 540) % 360) - 180) * k
            return dx * dx + (p.lat - lat) ** 2

        best = min(self.places, key=d2)
        return dict(best.as_dict(), distance_km=round(math.sqrt(d2(best)) * 111.2, 1))


@lru_cache(maxsize=1)
def places() -> Places:
    """Loaded once, on the first search, so starting the app does not pay for it."""
    return Places()
