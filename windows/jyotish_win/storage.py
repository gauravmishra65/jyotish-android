"""Where a Windows copy keeps its data.

The Android app keeps profiles and settings in its private storage and never uploads them. The Windows
edition keeps the same promise by writing to the user's own AppData folder and nothing else. No registry,
no roaming profile, no telemetry - a person who deletes the folder has deleted the app's memory of them.

Writes are atomic: content goes to a temporary file beside the target and is then moved over it, so a
crash or a power cut leaves either the old file or the new one, never half of either.
"""
import json
import os
import tempfile
from pathlib import Path

APP_FOLDER = "GauravJyotish"


def data_dir() -> Path:
    """%LOCALAPPDATA%\\GauravJyotish on Windows; an XDG-ish equivalent elsewhere so tests can run on Linux."""
    base = os.environ.get("JYOTISH_DATA_DIR")
    if base:
        return Path(base)
    local = os.environ.get("LOCALAPPDATA")
    if local:
        return Path(local) / APP_FOLDER
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / APP_FOLDER


def _write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)          # atomic on NTFS, and replaces an existing file unlike os.rename
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


class Store:
    """Profiles, settings and the chart cache. One instance per running app."""

    def __init__(self, root: Path | None = None):
        self.root = Path(root) if root else data_dir()
        self.profiles_path = self.root / "profiles.json"
        self.settings_path = self.root / "settings.json"
        self.charts_dir = self.root / "charts"

    # --- profiles -------------------------------------------------------------------------------

    def profiles(self) -> list[dict]:
        """Every saved person, oldest first. A missing or damaged file reads as empty rather than crashing:
        losing the list is bad, but refusing to start is worse, and the file is never silently overwritten
        until the person saves something."""
        try:
            data = json.loads(self.profiles_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return []
        return data if isinstance(data, list) else []

    def save_profiles(self, profiles: list[dict]) -> None:
        _write_atomic(self.profiles_path, json.dumps(profiles, ensure_ascii=False, indent=1))

    # --- settings -------------------------------------------------------------------------------

    def settings(self) -> dict:
        try:
            data = json.loads(self.settings_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        return data if isinstance(data, dict) else {}

    def save_settings(self, settings: dict) -> None:
        _write_atomic(self.settings_path, json.dumps(settings, ensure_ascii=False, indent=1))

    def setting(self, key: str, default=None):
        return self.settings().get(key, default)

    def set_setting(self, key: str, value) -> None:
        s = self.settings()
        s[key] = value
        self.save_settings(s)

    # --- the chart cache ------------------------------------------------------------------------

    def cached_chart(self, key: str) -> str | None:
        """A computed chart, by the same kind of key the Android app uses: a hash of the request including
        its version number, so a change to what a chart contains invalidates every cached copy."""
        path = self.charts_dir / f"{key}.json"
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            return None

    def cache_chart(self, key: str, chart_json: str) -> None:
        _write_atomic(self.charts_dir / f"{key}.json", chart_json)

    def clear_charts(self) -> int:
        """Drop every cached chart. Returns how many went. Used when the engine version changes."""
        gone = 0
        for p in self.charts_dir.glob("*.json"):
            try:
                p.unlink()
                gone += 1
            except OSError:
                pass
        return gone
