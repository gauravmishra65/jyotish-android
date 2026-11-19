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
from datetime import date, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones

from pathlib import Path

from . import licence
from .bridge import Engine, chart_key
from .places import places
from .storage import Store, _write_atomic, reports_dir

#: The window, once there is one. Only the file picker needs it, and only when running for real.
WINDOW: list = []

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


class DemoLimit(ValidationError):
    """The demo will not save another person. A kind of ValidationError so that every screen already
    shows it, but its own class so the interface can offer the unlock screen beside the message."""


def _born_edition() -> str:
    """"demo" unless this build was made as the full one.

    A file beside the package rather than a constant, so the same code can be packaged either way
    without a second branch to keep in step.
    """
    import os
    from pathlib import Path as _Path
    marked = os.environ.get("JYOTISH_EDITION")
    if marked:
        return marked.strip().lower()
    for root in (_Path(__file__).resolve().parent, _Path(__file__).resolve().parent.parent):
        marker = root / "edition.txt"
        if marker.exists():
            return marker.read_text(encoding="utf-8").strip().lower() or "demo"
    return "demo"


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

    def __init__(self, store: Store | None = None, engine: Engine | None = None,
                 opened_with: str | None = None):
        self.store = store or Store()
        self._engine = engine
        self._engine_ready = engine is not None
        self._pending = opened_with if opened_with and Path(opened_with).is_file() else None

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
        # Editing somebody already saved is always allowed; it is adding a new one that the demo limits.
        if len(people) == len(self.store.profiles()) and self.edition()["edition"] == "demo" \
                and len(people) >= licence.FREE_PROFILES:
            raise DemoLimit(
                f"The demo saves {licence.FREE_PROFILES} chart. Unlock the full version to add more.")
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

    # --- which edition this is ----------------------------------------------------------------

    def edition(self) -> dict:
        """Demo or full, and why.

        The demo saves one person. That is not a trial period and nothing expires: everything the engine
        can do works on that one chart, which is the honest way to let somebody see whether the readings
        are any good before paying for more.

        A build can be born full - that is the directly sold edition - or be unlocked by a code. The code
        is the same one the Android app takes, so a person who bought once does not buy again.
        """
        unlocked = bool(self.store.setting("unlock_code"))
        born = _born_edition()
        return {
            "edition": "full" if (born == "full" or unlocked) else "demo",
            "unlocked_to": self.store.setting("unlock_email") if unlocked else None,
            "free_profiles": licence.FREE_PROFILES,
            "people": len(self.store.profiles()),
        }

    def unlock(self, email: str, code: str) -> dict:
        """Check an unlock code and remember it. Nothing is sent anywhere to do this."""
        if not licence.verify(email, code):
            raise ValidationError("That code is not right for that email address.")
        self.store.set_setting("unlock_email", licence.normalize(email))
        self.store.set_setting("unlock_code", (code or "").strip())
        return self.edition()

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

    # --- two charts together ----------------------------------------------------------------------

    def match(self, groom_id: str, bride_id: str) -> dict:
        """Kundli Milan between two saved people.

        Which of the two is the bride matters: several of the kootas are counted from the bride's Moon
        to the groom's and not the other way round, so a screen that let the pair be entered in either
        order without saying which is which would quietly give a different answer.
        """
        if groom_id == bride_id:
            raise ValidationError("Choose two different people.")
        groom, bride = self.person(groom_id), self.person(bride_id)
        for who in (groom, bride):
            if who is None:
                raise ValidationError("That person is not saved on this computer.")
            validate(who)
        return self.engine.match(self.chart(groom_id), self.chart(bride_id), bride="B")

    # --- the tools that are not one chart ---------------------------------------------------------

    #: What muhurta can be asked for. The engine knows these four; the labels are the app's.
    EVENTS = (
        ("marriage", {"en": "Marriage", "hi": "विवाह"}),
        ("griha_pravesh", {"en": "Entering a new home", "hi": "गृह प्रवेश"}),
        ("vehicle", {"en": "A new vehicle", "hi": "नया वाहन"}),
        ("business", {"en": "Opening a business", "hi": "व्यापार आरंभ"}),
    )

    def muhurta_events(self) -> list[dict]:
        return [{"event": k, "name": name} for k, name in self.EVENTS]

    def muhurta(self, request: dict) -> dict:
        """Good windows for an event in a date range, optionally checked against the people involved.

        Passing the people matters: Tarabala and Chandrabala are counted from each person's own Moon, so
        a window that suits the couple is not the same as a window that is merely well aspected. The
        search walks the range in ten-minute steps, so a long range is slow - the screen says so.
        """
        if request.get("event") not in dict(self.EVENTS):
            raise ValidationError("Choose what the muhurta is for.")
        for field in ("from", "to", "lat", "lon", "tz"):
            if str(request.get(field, "")).strip() == "":
                raise ValidationError("A place and a date range are both needed.")
        for field in ("from", "to"):
            if not DATE.match(str(request[field])):
                raise ValidationError("The dates should look like 2026-12-01.")
        if request["from"] > request["to"]:
            raise ValidationError("The range ends before it starts.")
        if (date.fromisoformat(request["to"]) - date.fromisoformat(request["from"])).days > 120:
            raise ValidationError("Search four months or less at a time; a longer range takes too long.")

        charts = [self.chart(pid) for pid in request.get("people", []) if self.person(pid)]
        ask = {k: request[k] for k in ("event", "from", "to", "lat", "lon", "tz")}
        ask["lat"], ask["lon"] = float(ask["lat"]), float(ask["lon"])
        ask["top"] = int(request.get("top", 12))
        ask["lang"] = self.settings().get("language", "en")
        return self.engine.muhurta(ask, charts)

    #: The numerology tools, and which fields each one asks for.
    NUMBER_TOOLS = (
        ("personal", {"en": "Personal year, month and day", "hi": "व्यक्तिगत वर्ष, माह और दिन"}, ()),
        ("pair", {"en": "Two people together", "hi": "दो व्यक्ति साथ"}, ()),
        ("business", {"en": "A business name", "hi": "व्यापार का नाम"}, ("text",)),
        ("phone", {"en": "A mobile number", "hi": "मोबाइल नंबर"}, ("text",)),
        ("vehicle", {"en": "A vehicle number", "hi": "वाहन नंबर"}, ("text",)),
        ("house", {"en": "A house number", "hi": "मकान नंबर"}, ("text",)),
    )

    def number_tools(self) -> list[dict]:
        return [{"kind": k, "name": name, "needs": list(needs)} for k, name, needs in self.NUMBER_TOOLS]

    def numbers(self, request: dict) -> dict:
        """One of the numerology tools, answered for a saved person (or two, for the pair tool)."""
        kind = request.get("kind", "personal")
        if kind not in dict((k, n) for k, n, _ in self.NUMBER_TOOLS):
            raise ValidationError(f"There is no {kind!r} tool.")
        who = self.person(request.get("person_id", ""))
        if who is None:
            raise ValidationError("That person is not saved on this computer.")

        ask = {"kind": kind, "dob": who["date"]}
        if kind == "pair":
            other = self.person(request.get("other_id", ""))
            if other is None or other["id"] == who["id"]:
                raise ValidationError("Choose two different people.")
            ask.update({"a_name": who["name"], "a_dob": who["date"],
                        "b_name": other["name"], "b_dob": other["date"]})
        elif kind != "personal":
            text = str(request.get("text", "")).strip()
            if not text:
                raise ValidationError("Type the name or number to look at.")
            ask["text"] = text
        else:
            ask["on"] = request.get("on") or date.today().isoformat()
        return self.engine.number_tools(ask)

    def chinese(self, person_id: str) -> dict:
        """The Chinese side of a saved person: lunar birth date, Zi Wei Dou Shu, Nine Star Ki, Tong Shu."""
        who = self.person(person_id)
        if who is None:
            raise ValidationError("That person is not saved on this computer.")
        validate(who)
        ask = {k: who[k] for k in ("date", "time", "lat", "lon", "tz")}
        ask["gender"] = who.get("gender", "M")
        return self.engine.chinese_more(ask)

    # --- today, and what is coming ----------------------------------------------------------------

    def today_place(self) -> dict:
        """Where "today" is being read from.

        Not the birthplace: the panchang, the choghadiya and the transits are about where somebody is
        now, and most people are not where they were born. It is remembered once chosen, and until then
        it is taken from the first saved person so the screen has something true to show rather than an
        empty form.
        """
        s = self.store.settings()
        if s.get("today_lat") not in (None, "") and s.get("today_tz"):
            return {"place": s.get("today_place", ""), "lat": float(s["today_lat"]),
                    "lon": float(s["today_lon"]), "tz": s["today_tz"]}
        people = self.store.profiles()
        if people:
            first = people[0]
            return {"place": first.get("place", ""), "lat": float(first["lat"]),
                    "lon": float(first["lon"]), "tz": first["tz"]}
        return {}

    def set_today_place(self, place: dict) -> dict:
        for field in ("lat", "lon", "tz"):
            if str(place.get(field, "")).strip() == "":
                raise ValidationError("A place, with its coordinates and time zone, is needed.")
        try:
            ZoneInfo(str(place["tz"]).strip())
        except (ZoneInfoNotFoundError, ValueError, OSError) as e:
            raise ValidationError(f"{place['tz']!r} is not a time zone name.") from e
        self.store.set_setting("today_place", str(place.get("place", "")).strip())
        self.store.set_setting("today_lat", float(place["lat"]))
        self.store.set_setting("today_lon", float(place["lon"]))
        self.store.set_setting("today_tz", str(place["tz"]).strip())
        return self.today_place()

    def today(self, when: str | None = None) -> dict:
        """The panchang for a day: tithi, nakshatra, the periods to use and the ones to avoid."""
        where = self.today_place()
        if not where:
            raise ValidationError("Choose where you are before reading today's panchang.")
        ask = dict(where)
        ask["date"] = when or date.today().isoformat()
        return self.engine.today(ask)

    def forecast(self, person_id: str, years: int = 3) -> dict:
        """The three-year outlook, by area of life. The same layers the full reading uses."""
        who = self.person(person_id)
        if who is None:
            raise ValidationError("That person is not saved on this computer.")
        validate(who)
        return self.engine.forecast(dict(self.chart_request(who), years=int(years)))

    #: What predict() will answer for, in the order the buttons appear.
    PERIODS = (
        ("day", {"en": "Today", "hi": "आज"}),
        ("week", {"en": "This week", "hi": "इस सप्ताह"}),
        ("month", {"en": "This month", "hi": "इस माह"}),
        ("year", {"en": "This year", "hi": "इस वर्ष"}),
        ("three", {"en": "Three years", "hi": "तीन वर्ष"}),
    )

    def periods(self) -> list[dict]:
        return [{"period": k, "name": name} for k, name in self.PERIODS]

    def predict(self, person_id: str, period: str = "year") -> dict:
        """What the period ahead looks like by area of life, with the reasons given."""
        if period not in dict(self.PERIODS):
            raise ValidationError("Choose a period.")
        who = self.person(person_id)
        if who is None:
            raise ValidationError("That person is not saved on this computer.")
        validate(who)
        ask = dict(self.chart_request(who), period=period)
        where = self.today_place()
        if where:
            # Transits are read from where the person is now, not where they were born.
            ask.update({"current_lat": where["lat"], "current_lon": where["lon"]})
        return self.engine.predict(ask)

    def ask_question(self, request: dict) -> dict:
        """Prashna, or a KP number horary: a chart for the moment the question was asked.

        The place and the moment are the question's, not anybody's birth - a prashna is read for whoever
        is standing in front of you, and the saved people have nothing to do with it.
        """
        text = str(request.get("question", "")).strip()
        if not text:
            raise ValidationError("Type the question first.")
        method = request.get("method", "prashna")
        if method not in ("prashna", "kp"):
            raise ValidationError("The method is either prashna or kp.")
        where = self.today_place()
        if not where:
            raise ValidationError("Choose where you are before asking.")
        ask = dict(where, method=method, question=text)
        if method == "kp":
            try:
                number = int(str(request.get("number", "")).strip())
            except ValueError as e:
                raise ValidationError("A KP horary needs a number from 1 to 249.") from e
            if not 1 <= number <= 249:
                raise ValidationError("The number runs from 1 to 249.")
            ask["number"] = number
        return self.engine.question(ask)

    def compare_group(self, person_ids: list[str]) -> dict:
        """Several people side by side - a family, a team - rather than two at a time."""
        people = [self.person(pid) for pid in person_ids]
        if len([p for p in people if p]) < 2:
            raise ValidationError("Choose at least two people.")
        return self.engine.group({"people": [self.chart_request(validate(p)) for p in people if p]})

    def flying_stars(self, when: str | None = None) -> dict:
        """The annual and monthly Flying Stars for a date."""
        return self.engine.feng_shui({"today": when or date.today().isoformat()})

    # --- life events, and checking a birth time against them --------------------------------------

    def event_kinds(self) -> dict:
        """The dated events a birth time can be checked against, named by the engine in both languages."""
        return self.engine.rectify({"date": "2000-01-01", "time": "12:00", "lat": 0.0, "lon": 0.0,
                                    "tz": "UTC", "window_min": 1, "events": []}).get("kinds", {})

    def set_events(self, person_id: str, events: list[dict]) -> list[dict]:
        """Dated events in somebody's life, kept with them.

        They are what a birth time is checked against, and they stay on this computer like everything
        else. Anything without both a kind and a date is dropped rather than stored half-written.
        """
        who = self.person(person_id)
        if who is None:
            raise ValidationError("That person is not saved on this computer.")
        kept = []
        for event in events or []:
            kind, when = str(event.get("kind", "")).strip(), str(event.get("date", "")).strip()
            if not kind or not DATE.match(when):
                continue
            try:
                datetime.strptime(when, "%Y-%m-%d")
            except ValueError:
                continue
            kept.append({"kind": kind, "date": when})
        people = [dict(p, events=kept) if p.get("id") == person_id else p
                  for p in self.store.profiles()]
        self.store.save_profiles(people)
        return kept

    def events(self, person_id: str) -> list[dict]:
        who = self.person(person_id)
        return list(who.get("events", [])) if who else []

    def rectify(self, person_id: str, window_min: int = 60) -> dict:
        """Which spans of birth time fit the recorded events better than chance would.

        This answers with spans and probabilities, never with a corrected time. A birth time is a fact
        about somebody's life, and the honest output is "these minutes explain your events better than
        the others", which a person can weigh against what they were told.
        """
        who = self.person(person_id)
        if who is None:
            raise ValidationError("That person is not saved on this computer.")
        validate(who)
        try:
            window = int(window_min)
        except (TypeError, ValueError) as e:
            raise ValidationError("The window is a number of minutes.") from e
        if not 5 <= window <= 240:
            raise ValidationError("Search between 5 and 240 minutes either side.")

        ask = {k: who[k] for k in ("date", "time", "lat", "lon", "tz")}
        ask["gender"] = who.get("gender", "M")
        ask["window_min"] = window
        ask["events"] = self.events(person_id)
        settings = self.store.settings()
        if settings.get("ayanamsa"):
            ask["ayanamsa"] = settings["ayanamsa"]
        return self.engine.rectify(ask)

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
        settings = self.settings()
        request["lang"] = settings.get("language", "en")
        request["by"] = settings.get("report_by") or "Gaurav Mishra"
        request["site"] = settings.get("report_site") or "authorgaurav.com"
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

    # --- backup and restore -------------------------------------------------------------------

    def backup(self, password: str) -> dict:
        """Write every saved person to an encrypted file in the reports folder.

        The format is the phone's, so a file written here restores on the Android app and the other way
        round. The password is never stored: a forgotten one means a lost file, and the screen says so
        before it asks.
        """
        from . import backup as fmt
        people = self.store.profiles()
        if not people:
            raise ValidationError("There is nobody saved to back up.")
        blob = fmt.encode(people, password)
        path = reports_dir() / f"Gaurav Jyotish backup {date.today().isoformat()}.gjb"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(blob)
        return {"path": str(path), "file": path.name, "count": len(people)}

    def restore(self, path: str, password: str) -> dict:
        """Read a backup and add what it holds to this computer.

        People already here are kept: a restore adds and updates rather than replacing, because somebody
        restoring an old phone backup onto a desktop they have been using should not lose the desktop's
        work to do it. Matching is by id, which both apps generate and neither reuses.
        """
        from . import backup as fmt
        target = Path(path)
        if not target.is_file():
            raise ValidationError("There is no file there.")
        if target.stat().st_size > 8 * 1024 * 1024:
            raise ValidationError("That file is far too large to be a backup.")
        incoming = fmt.decode(target.read_bytes(), password)

        existing = {p.get("id"): p for p in self.store.profiles()}
        demo = self.edition()["edition"] == "demo"
        added = updated = skipped = waiting = 0
        for person in incoming:
            try:
                clean = validate(person)
            except ValidationError:
                skipped += 1                 # a row the engine could not use; the rest still restore
                continue
            clean.setdefault("id", uuid.uuid4().hex[:12])
            if clean["id"] in existing:
                updated += 1
            elif demo and len(existing) >= licence.FREE_PROFILES:
                # A backup of twenty people must not become a way round the demo limit. What fits is
                # restored and the rest is counted, so the screen can say how many are waiting.
                waiting += 1
                continue
            else:
                added += 1
            existing[clean["id"]] = clean
        self.store.save_profiles(list(existing.values()))
        return {"added": added, "updated": updated, "skipped": skipped,
                "waiting": waiting, "total": len(existing)}

    def pending_restore(self) -> str | None:
        """A backup file the app was started with, because the person double-clicked it.

        The installer associates .gjb with this app, so opening one has to lead somewhere. It leads to
        the settings screen with the file already chosen - and no further, because restoring without
        being asked would be a surprising thing for a double-click to do.
        """
        waiting, self._pending = self._pending, None
        return waiting

    def pick_backup(self) -> str | None:
        """The system file picker, so a backup can be restored from wherever the person keeps it."""
        window = WINDOW[0] if WINDOW else None
        if window is None:
            return None
        import webview
        chosen = window.create_file_dialog(
            webview.OPEN_DIALOG, allow_multiple=False,
            file_types=("Gaurav Jyotish backup (*.gjb)", "All files (*.*)"))
        return chosen[0] if chosen else None

    # --- settings ---------------------------------------------------------------------------------

    #: Every setting the screen offers, with the values the engine actually accepts. Keeping the list
    #: here rather than in JavaScript means a value the engine would reject cannot reach it from a form.
    CHOICES = {
        "ayanamsa": (("lahiri", {"en": "Lahiri", "hi": "लाहिड़ी"}),
                     ("true_chitra", {"en": "True Chitra", "hi": "ट्रू चित्रा"}),
                     ("krishnamurti", {"en": "KP (Krishnamurti)", "hi": "केपी (कृष्णमूर्ति)"}),
                     ("raman", {"en": "Raman", "hi": "रमन"})),
        "house_system": (("placidus", {"en": "Placidus", "hi": "प्लेसिडस"}),
                         ("whole", {"en": "Whole sign", "hi": "पूर्ण राशि"}),
                         ("koch", {"en": "Koch", "hi": "कोख"}),
                         ("equal", {"en": "Equal", "hi": "समान"}),
                         ("regiomontanus", {"en": "Regiomontanus", "hi": "रेजियोमोंटेनस"}),
                         ("campanus", {"en": "Campanus", "hi": "कैम्पेनस"}),
                         ("porphyry", {"en": "Porphyry", "hi": "पोर्फिरी"})),
        "node": (("mean", {"en": "Mean node", "hi": "मध्यम राहु"}),
                 ("true", {"en": "True node", "hi": "स्पष्ट राहु"})),
        "orb_scale": (("0.75", {"en": "Tight", "hi": "संकीर्ण"}),
                      ("1.0", {"en": "Standard", "hi": "सामान्य"}),
                      ("1.25", {"en": "Wide", "hi": "विस्तृत"})),
        "chart_style": (("north", {"en": "North Indian", "hi": "उत्तर भारतीय"}),
                        ("south", {"en": "South Indian", "hi": "दक्षिण भारतीय"})),
        "theme": (("system", {"en": "Follow Windows", "hi": "विंडोज़ के अनुसार"}),
                  ("light", {"en": "Light", "hi": "उजला"}),
                  ("dark", {"en": "Dark", "hi": "गहरा"})),
    }

    #: Where the first option is not the right default. Orb width reads tight-standard-wide, which is
    #: the order to show it in, but standard is what the engine has always used.
    DEFAULTS = {"orb_scale": "1.0", "theme": "system"}

    #: Settings that are free text rather than a choice.
    TEXT_SETTINGS = ("report_by", "report_site")

    def setting_choices(self) -> list[dict]:
        return [{"key": key, "options": [{"value": v, "name": n} for v, n in options]}
                for key, options in self.CHOICES.items()]

    def settings(self) -> dict:
        s = self.store.settings()
        s.setdefault("language", "en")
        for key, options in self.CHOICES.items():
            s.setdefault(key, self.DEFAULTS.get(key, options[0][0]))
        s.setdefault("report_by", "Gaurav Mishra")
        s.setdefault("report_site", "authorgaurav.com")
        return s

    def set_setting(self, key: str, value) -> dict:
        """Refuse a value the engine would reject rather than storing it and failing on the next chart.

        A bad ayanamsa saved into settings.json would break every chart from then on, including after a
        restart, and the person would have no way to see why. Checking here keeps that impossible.
        """
        if key in self.CHOICES:
            allowed = [v for v, _ in self.CHOICES[key]]
            if value not in allowed:
                raise ValidationError(f"{value!r} is not one of: {', '.join(allowed)}")
        elif key == "language":
            if value not in ("en", "hi"):
                raise ValidationError("The language is either 'en' or 'hi'.")
        elif key in self.TEXT_SETTINGS:
            value = str(value).strip()[:120]
        self.store.set_setting(key, value)
        return self.settings()

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

    # --- about ----------------------------------------------------------------------------------

    def about(self) -> dict:
        import sys
        return {
            "engine": self.engine.version(),
            "python": sys.version.split()[0],
            "data_dir": str(self.store.root),
            "reports_dir": str(reports_dir()),
            "people": len(self.store.profiles()),
            "licences": (
                "Planetary positions: Swiss Ephemeris by Astrodienst AG. "
                "Place names and time zones: GeoNames (CC BY 4.0). "
                "The window: pywebview, on Microsoft WebView2."),
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
