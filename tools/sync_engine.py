"""Copy the calculation engine from the astrology-numerology-reading skill into the app.

Usage:  python tools/sync_engine.py /path/to/astrology-numerology-reading

Copies the skill's scripts (minus report, book and test tooling), its ephemeris files and the yoga base
rates into app/src/main/python, and records the skill's git commit in ENGINE_VERSION.txt. engine_api.py is
the app's own file and is never overwritten.
"""
import os
import shutil
import subprocess
import sys

SKIP = {"render_report.py", "book.py", "verify_engine.py", "golden_regression.py", "yoga_base_rates.py",
        "setup_env.sh"}
APP_PY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app", "src", "main", "python")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    skill = os.path.abspath(sys.argv[1])
    src = os.path.join(skill, "scripts")
    if not os.path.isfile(os.path.join(src, "chart_engine.py")):
        sys.exit(f"not a skill folder: {skill}")
    os.makedirs(APP_PY, exist_ok=True)
    for f in os.listdir(APP_PY):  # remove engine files from a previous sync, keep the app's own
        p = os.path.join(APP_PY, f)
        if (f.endswith(".py") and f != "engine_api.py") or f.endswith(".json"):
            os.remove(p)
    if os.path.isdir(os.path.join(APP_PY, "ephe")):
        shutil.rmtree(os.path.join(APP_PY, "ephe"))
    n = 0
    for f in sorted(os.listdir(src)):
        if f.endswith(".py") and f not in SKIP:
            shutil.copy2(os.path.join(src, f), APP_PY)
            n += 1
    for f in sorted(os.listdir(src)):  # data files the engine reads beside its modules
        if f.endswith(".json"):
            shutil.copy2(os.path.join(src, f), APP_PY)
    shutil.copytree(os.path.join(src, "ephe"), os.path.join(APP_PY, "ephe"))
    # Hindi names the app shows (signs, planets, nakshatras, dignities, yogas), taken from the skill's report code.
    hindi = subprocess.check_output([sys.executable, "-c", (
        "import json, render_report as R, hindi_shell as HS;"
        "print(json.dumps({'sign': HS.SIGN, 'planet': HS.PLANET, 'nakshatra': HS.NAK, 'tag': HS.TAGS,"
        " 'yoga': R.YOGA_NAME_HI, 'yoga_category': R.YOGA_CAT_HI}, ensure_ascii=False))")], cwd=src, text=True)
    assets = os.path.join(APP_PY, "..", "assets")
    os.makedirs(assets, exist_ok=True)
    open(os.path.join(assets, "hindi_names.json"), "w", encoding="utf-8").write(hindi)
    try:
        rev = subprocess.check_output(["git", "-C", skill, "log", "-1", "--format=%h %cs %s"], text=True).strip()
    except Exception:
        rev = "unknown (not a git checkout)"
    open(os.path.join(APP_PY, "ENGINE_VERSION.txt"), "w").write(f"astrology-numerology-reading {rev}\n")
    print(f"copied {n} modules, data files and ephemeris; engine {rev}")


if __name__ == "__main__":
    main()
