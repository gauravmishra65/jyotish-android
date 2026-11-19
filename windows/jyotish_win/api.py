"""What the interface is allowed to do.

Everything the window can ask for passes through this one object. Keeping it here rather than in the
window means the whole of the app's behaviour can be tested without a desktop session - which matters,
because a headless CI runner has no desktop and anything that cannot be tested there will not be tested
at all.

The methods are deliberately plain: they take and return ordinary dicts and lists, because on the other
side of this boundary is JavaScript, and anything clever would have to survive a JSON round trip anyway.
"""
import re
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones

from pathlib import Path

from .bridge import Engine, chart_key
from .places import places
from .storage import Store, _write_atomic, reports_dir

#: What a saved person must have before a chart can be built from them.
REQUIRED = ("name", "date", "time", "lat", "lon", "tz")

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME = re.compile(r"^\d{2}:\d{2}$")


def _safe_filename(stem: str) -> str:
    """A file name Windows will accept, built from a person's name without mangling it beyond recognition.

    Devanagari is left alone - NTFS stores it perfectly well, and a Hindi speaker's report should be
    findable under their own name - but the nine characters Windows reserves are replaced, and a trailing
    dot or space is removed because Windows silently drops those and then cannot find the file again.
    """
    cleaned = "".join("-" if c in '<>:"/\\|?*' else c for c in stem)
    cleaned = "".join(c for c in cleaned if c.isprintable() and ord(c) > 31)
    return cleaned[:120].strip(" .-") or "Report"


class ValidationError(ValueError):
    """Something the person typed is wrong, and the message is meant for them to read."""


def validate(person: dict) -> dict:
    """Check a person well enough that the engine will not be handed nonsense, and no further.

    This is not the place to be clever about what a birth time means - the engine already handles unknown
    and approximate times. It is only here to catch the mistakes a form can make.
    """
    missing = [f for f in REQUIRED if not str(person.get(f, "")).strip()]
    if missing:
        raise ValidationError("Still needed: " + ", ".join(missing))

    if not DATE.match(person["date"]):
        raise ValidationError("The date should look like 1988-07-14.")
    if not TIME.match(person["time"]):
        raise ValidationError("The time should look like 14:35, on a 24-hour clock.")
    try:
        datetime.strptime(f"{person['date']} {person['time']}", "%Y-%m-%d %H:%M")
    except ValueError as e:
        raise ValidationError(f"That is not a real date and time: {e}") from e

    try:
        lat, lon = float(person["lat"]), float(person["lon"])
    except (TypeError, ValueError) as e:
        raise ValidationError("Latitude and longitude should be numbers.") from e
    if not -90 <= lat <= 90:
        raise ValidationError("Latitude runs from -90 to 90.")
    if not -180 <= lon <= 180:
        raise ValidationError("Longitude runs from -180 to 180.")

    tz = str(person["tz"]).strip()
    try:
        ZoneInfo(tz)
    except (ZoneInfoNotFoundError, ValueError, OSError) as e:
        # Without this check an unknown zone reaches zoneinfo, which on Windows tries to open a folder
        # as a file and raises a bare PermissionError with a path in it. "Asia" alone does exactly that:
        # the key needs the city too. OSError is caught for that reason, not for tidiness.
        raise ValidationError(
            f"{tz!r} is not a time zone name. It needs the region and the city, "
            f"as in Asia/Kolkata, Asia/Singapore or Europe/London." ) from e

    clean = dict(person)
    clean["lat"], clean["lon"] = lat, lon
    clean["tz"] = tz
    clean["name"] = person["name"].strip()
    clean.setdefault("gender", "M")
    clean.setdefault("time_confidence", "reliable")
    return clean


def time_zones() -> list[str]:
    """Every zone this machine knows, for the form to offer. Sorted, with the common ones first so the
    list is useful before a single letter is typed."""
    common = ["Asia/Kolkata", "Asia/Singapore", "Asia/Dubai", "Europe/London", "America/New_York",
              "America/Los_Angeles", "Australia/Sydney", "UTC"]
    known = available_timezones()
    rest = sorted(z for z in known if z not in common)
    return [z for z in common if z in known] + rest


class Api:
    """The object handed to the window. One instance per running app."""

    def __init__(self, store: Store | None = None, engine: Engine | None = None):
        self.store = store or Store()
        self._engine = engine
        self._engine_ready = engine is not None

    @property
    def engine(self) -> Engine:
        """Loaded on first use, not at start.

        Importing the engine pulls in Swiss Ephemeris and 55 modules, which takes a second or two. Doing
        that before the window appears would make the app look slow to open for no reason: nothing on the
        first screen needs a chart until someone asks for one.
        """
        if self._engine is None:
            self._engine = Engine()
        if not self._engine_ready:
            self._engine_ready = True
            self._retire_stale_charts()
        return self._engine

    # --- people ---------------------------------------------------------------------------------

    def people(self) -> list[dict]:
        return self.store.profiles()

    def add_person(self, person: dict) -> dict:
        """Save a person and hand back the stored copy, including the id it was given."""
        clean = validate(person)
        clean.setdefault("id", uuid.uuid4().hex[:12])
        people = [p for p in self.store.profiles() if p.get("id") != clean["id"]]
        people.append(clean)
        self.store.save_profiles(people)
        return clean

    def delete_person(self, person_id: str) -> bool:
        """Forget a person and every chart cached for them. There is no undo, and no copy elsewhere."""
        people = self.store.profiles()
        remaining = [p for p in people if p.get("id") != person_id]
        if len(remaining) == len(people):
            return False
        self.store.save_profiles(remaining)
        return True

    def person(self, person_id: str) -> dict | None:
        return next((p for p in self.store.profiles() if p.get("id") == person_id), None)

    # --- charts ---------------------------------------------------------------------------------

    def chart(self, person_id: str) -> dict:
        """The chart for a saved person, computed once and then remembered.

        The cache key covers the request and the chart version together, so a person who edits a birth
        time, or an engine that changes what a chart contains, both get a fresh calculation without
        anyone having to clear anything.
        """
        who = self.person(person_id)
        if who is None:
            raise ValidationError("That person is not saved on this computer.")
        # Checked again here, not only when saving: a profile written by an older build, restored from a
        # backup or edited by hand can hold something the engine cannot use, and the person reading the
        # screen deserves the same sentence either way.
        validate(who)
        request = self.chart_request(who)
        key = chart_key(request)
        cached = self.store.cached_chart(key)
        if cached:
            import json
            return json.loads(cached)
        chart = self.engine.chart(request)
        import json
        self.store.cache_chart(key, json.dumps(chart, ensure_ascii=False))
        return chart

    def chart_request(self, person: dict) -> dict:
        """Turn a saved person into the request the engine expects, applying the current settings."""
        s = self.store.settings()
        request = {k: person[k] for k in REQUIRED if k in person}
        for optional in ("gender", "place", "time_confidence", "name_in_use", "calendar", "fold"):
            if person.get(optional):
                request[optional] = person[optional]
        for setting, field in (("ayanamsa", "ayanamsa"), ("house_system", "house_system"),
                               ("orb_scale", "orb_scale"), ("node", "node")):
            if s.get(setting):
                request[field] = s[setting]
        return request

    # --- readings as files ------------------------------------------------------------------------

    #: What report() will build, in the order the buttons appear. "life" is the whole reading; the rest
    #: are the single-subject reports the Android app offers under the same names.
    REPORTS = (
        ("life", {"en": "Full reading", "hi": "संपूर्ण विश्लेषण"}),
        ("daily", {"en": "Daily", "hi": "दैनिक"}),
        ("monthly", {"en": "Monthly", "hi": "मासिक"}),
        ("annual", {"en": "Annual", "hi": "वार्षिक"}),
        ("mahadasha", {"en": "Mahadasha", "hi": "महादशा"}),
        ("mangal", {"en": "Mangal Dosh", "hi": "मंगल दोष"}),
        ("kaal_sarp", {"en": "Kaal Sarp Dosh", "hi": "काल सर्प दोष"}),
        ("sade_sati", {"en": "Sade Sati", "hi": "साढ़े साती"}),
        ("chandra", {"en": "Chandra Rashi", "hi": "चंद्र राशि"}),
    )

    def report_kinds(self) -> list[dict]:
        return [{"kind": k, "name": name} for k, name in self.REPORTS]

    def make_report(self, person_id: str, kind: str = "life") -> dict:
        """Build a reading and save it as an HTML page in the reports folder.

        A file rather than another screen, because this is the output somebody prints, emails to a client
        or opens again in five years. It is one self-contained page: no stylesheet beside it, nothing
        fetched when it opens, so it still reads correctly on a computer that has never heard of this app.
        """
        if kind not in dict(self.REPORTS):
            raise ValidationError(f"There is no {kind!r} report.")
        who = self.person(person_id)
        if who is None:
            raise ValidationError("That person is not saved on this computer.")
        validate(who)

        request = self.chart_request(who)
        request["kind"] = kind
        request["lang"] = self.settings().get("language", "en")
        built = self.engine.special_report(request)
        html = built.get("html")
        if not html:
            raise ValidationError("The engine returned no report.")

        name = dict(self.REPORTS)[kind][request["lang"]] if kind in dict(self.REPORTS) else kind
        stem = _safe_filename(f"{who['name']} - {dict(self.REPORTS)[kind]['en']}")
        path = reports_dir() / f"{stem}.html"
        _write_atomic(path, html)
        return {"path": str(path), "folder": str(path.parent), "name": name, "file": path.name}

    def open_path(self, path: str) -> bool:
        """Open a saved report in whatever the computer uses for HTML - normally the browser, where it
        can be read and printed to PDF. Only files this app wrote are opened, so a path arriving from
        anywhere unexpected cannot turn this into a way to launch something else."""
        import os
        import subprocess
        target = Path(path).resolve()
        folder = reports_dir().resolve()
        if folder not in target.parents or not target.is_file():
            raise ValidationError("That file is not one of the saved reports.")
        if hasattr(os, "startfile"):
            os.startfile(str(target))                      # Windows
        else:
            subprocess.Popen(["xdg-open", str(target)])    # so the same button works while developing
        return True

    def reports(self) -> list[dict]:
        """Everything saved so far, newest first, so the panel can offer them again without rebuilding."""
        folder = reports_dir()
        if not folder.is_dir():
            return []
        files = sorted(folder.glob("*.html"), key=lambda f: f.stat().st_mtime, reverse=True)
        return [{"file": f.name, "path": str(f), "when": int(f.stat().st_mtime)} for f in files[:40]]

    # --- settings -------------------------------------------------------------------------------

    # --- places ---------------------------------------------------------------------------------

    def search_places(self, query: str, limit: int = 8) -> list[dict]:
        """Birthplaces matching what has been typed so far, best first.

        The coordinates and the time zone come with each result, so choosing a place fills in the three
        fields nobody should have to look up.
        """
        try:
            return places().search(query, limit)
        except FileNotFoundError:
            return []

    def nearest_place(self, lat: float, lon: float) -> dict | None:
        """The nearest listed place to a point, for naming the time zone when coordinates are typed."""
        try:
            return places().nearest(float(lat), float(lon))
        except (FileNotFoundError, TypeError, ValueError):
            return None

    def time_zones(self) -> list[str]:
        """Offered by the form so a half-typed zone cannot reach the engine."""
        return time_zones()

    def settings(self) -> dict:
        s = self.store.settings()
        s.setdefault("language", "en")
        s.setdefault("chart_style", "north")
        s.setdefault("theme", "light")
        return s

    def set_setting(self, key: str, value) -> dict:
        self.store.set_setting(key, value)
        return self.settings()

    # --- about ----------------------------------------------------------------------------------

    def about(self) -> dict:
        import sys
        return {
            "engine": self.engine.version(),
            "python": sys.version.split()[0],
            "data_dir": str(self.store.root),
            "people": len(self.store.profiles()),
        }

    # --- plumbing -------------------------------------------------------------------------------

    def _retire_stale_charts(self) -> None:
        """Charts cached by an older engine are thrown away on start.

        The cache key already includes the chart version, so stale entries would never be served - but
        they would sit on disk for ever. This is housekeeping, not correctness.
        """
        seen = self.store.setting("engine_version")
        now = self.engine.version()
        if seen != now:
            self.store.clear_charts()
            self.store.set_setting("engine_version", now)
