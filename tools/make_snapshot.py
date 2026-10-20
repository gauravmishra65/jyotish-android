"""Write the desktop results the phone must reproduce exactly.

Usage:  python tools/make_snapshot.py      (with pyswisseph and tzdata installed)

Runs engine_api.run_suite() on this computer and saves app/src/androidTest/assets/snapshot.json.
Rerun it after every tools/sync_engine.py.
"""
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "app", "src", "main", "python"))
import engine_api  # noqa: E402

snap = engine_api.make_snapshot()
out = os.path.join(ROOT, "app", "src", "androidTest", "assets", "snapshot.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(snap, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"wrote {out}: {len(snap['results'])} result groups; desktop timings {snap['desktop_timings_s']}")
