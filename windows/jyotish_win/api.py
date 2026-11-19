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

from .bridge import Engine, chart_key
from .storage import Store

#: What a saved person must have before a chart can be built from them.
REQUIRED = ("name", "date", "time", "lat", "lon", "tz")

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME = re.compile(r"^\d{2}:\d{2}$")


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

    clean = dict(person)
    clean["lat"], clean["lon"] = lat, lon
    clean["name"] = person["name"].strip()
    clean.setdefault("gender", "M")
    clean.setdefault("time_confidence", "reliable")
    return clean


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

    # --- settings -------------------------------------------------------------------------------

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
