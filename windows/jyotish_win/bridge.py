"""The only way the Windows app talks to the astrology engine.

This is the desktop counterpart of Engine.kt on Android, and it exists for the same reason: one place that
knows how to reach the engine, so no screen ever imports a calculation module directly. The engine takes
and returns JSON strings; on Android that crosses into Kotlin, here it crosses into JavaScript, and in both
cases the engine neither knows nor cares which.

The engine itself is unchanged - the same 55 modules the Android build ships. Nothing in this file adds
astrology; it only carries requests across.
"""
import hashlib
import json
import os
import sys
import threading
from pathlib import Path

#: Bumped when what a chart contains changes, exactly as Profile.chartRequest does on Android, so that a
#: cached chart from an older engine is never served against newer code.
CHART_VERSION = 14


def engine_path() -> Path:
    """Where the Python engine lives.

    In a packaged build it sits beside this package. In a developer checkout it is still in the Android
    tree, because there is one engine and copying it would guarantee the two drift apart.
    """
    override = os.environ.get("JYOTISH_ENGINE_PATH")
    if override:
        return Path(override)
    here = Path(__file__).resolve().parent
    roots = [here, here.parent]
    frozen = getattr(sys, "_MEIPASS", None)
    if frozen:
        # A PyInstaller build. The engine ships as plain .py files rather than frozen modules, because
        # engine_api imports two dozen of them by name at call time and a frozen build would have to be
        # told about every one. _MEIPASS is where those files are unpacked; the folder beside the .exe is
        # where a one-folder build keeps them.
        roots = [Path(frozen), Path(sys.executable).resolve().parent, *roots]
    for root in roots:
        for candidate in (root / "engine", root / "_internal" / "engine"):
            if (candidate / "engine_api.py").exists():
                return candidate
    for candidate in (here.parent.parent / "app" / "src" / "main" / "python",):   # a checkout
        if (candidate / "engine_api.py").exists():
            return candidate
    raise RuntimeError(
        "The astrology engine was not found. Set JYOTISH_ENGINE_PATH to the folder holding engine_api.py."
    )


class Engine:
    """Loads the engine once and answers requests from the interface.

    Calls are serialised behind a lock. The engine is ordinary single-threaded Python with module-level
    state (the ayanamsa mode, the ephemeris path), so two charts computed at once could read each other's
    settings. On Android the same problem is solved by giving Python one dedicated thread; here one lock
    does it, and the window stays responsive because the interface calls this from a worker.
    """

    def __init__(self):
        self._lock = threading.Lock()
        path = engine_path()
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
        import engine_api                      # noqa: E402  - deliberately late: sys.path must be set first
        self._api = engine_api
        self.path = path

    # --- the calls the interface makes ----------------------------------------------------------

    def version(self) -> str:
        """The engine's commit stamp. Alone among the entry points this answers a bare string, not JSON."""
        return str(self._api.engine_version())

    def chart(self, request: dict) -> dict:
        return self._call("chart", request)

    def forecast(self, request: dict) -> dict:
        return self._call("forecast", request)

    def report(self, request: dict) -> dict:
        return self._call("report", request)

    def special_report(self, request: dict) -> dict:
        return self._call("special_report", request)

    def rectify(self, request: dict) -> dict:
        return self._call("rectify", request)

    def question(self, request: dict) -> dict:
        return self._call("question", request)

    def horary(self, request: dict) -> dict:
        return self._call("horary", request)

    def number_tools(self, request: dict) -> dict:
        return self._call("number_tools", request)

    def chinese_more(self, request: dict) -> dict:
        return self._call("chinese_more", request)

    def group(self, request: dict) -> dict:
        return self._call("group", request)

    def custom_varga(self, request: dict) -> dict:
        return self._call("custom_varga", request)

    def custom_rule(self, request: dict) -> dict:
        return self._call("custom_rule", request)

    def today(self, request: dict) -> dict:
        return self._call("today", request)

    def predict(self, request: dict) -> dict:
        return self._call("predict", request)

    def feng_shui(self, request: dict) -> dict:
        return self._call("feng_shui", request)

    def match(self, chart_a: dict, chart_b: dict, bride: str = "B") -> dict:
        with self._lock:
            return self._json(self._api.match(json.dumps(chart_a), json.dumps(chart_b), bride))

    def muhurta(self, request: dict, charts: list[dict]) -> dict:
        with self._lock:
            return self._json(self._api.find_muhurta(json.dumps(request), *[json.dumps(c) for c in charts]))

    # --- plumbing -------------------------------------------------------------------------------

    def _call(self, name: str, request: dict) -> dict:
        fn = getattr(self._api, name)
        with self._lock:
            return self._json(fn(json.dumps(request)))

    @staticmethod
    def _json(raw) -> dict:
        """The engine answers with a JSON string. A non-JSON answer is a bug worth seeing, not hiding."""
        if isinstance(raw, (dict, list)):
            return raw
        try:
            return json.loads(raw)
        except (TypeError, ValueError) as e:
            raise RuntimeError(f"The engine returned something that is not JSON: {e}") from e


def chart_key(request: dict) -> str:
    """A stable cache key for a chart request, including the version, so that bumping CHART_VERSION
    retires every cached chart without anyone having to delete files."""
    payload = dict(request)
    payload["v"] = CHART_VERSION
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:32]
