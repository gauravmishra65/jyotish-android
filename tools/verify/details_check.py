"""Is every reading complete?

app_details assembles the 66 sections from a dozen builders, and one of them failing must not cost a
reader the other sixty - so each is guarded. The guard used to swallow the failure, which meant a chart
whose regional or BaZi builder threw came back quietly short and looked perfectly normal. Nobody counts
sections.

So the builders now record what failed, and this refuses to let that pass unnoticed: every chart in the
fixture set must come back with nothing missing, and with the full complement of sections and vargas.

Run directly, or through tools/verify/run_all.py.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "app", "src", "main", "python"))

import app_details                      # noqa: E402
import engine_api as EA                 # noqa: E402

#: The fictional people the rest of the suite uses, plus the awkward ones: a southern birth, a leap day,
#: an unknown time, and a date far enough back to leave the .se1 files and fall to Moshier.
PEOPLE = [
    {"name": "Ravi Shankar Tiwari", "date": "1988-07-14", "time": "14:35", "lat": 25.3176,
     "lon": 82.9739, "tz": "Asia/Kolkata", "gender": "M"},
    {"name": "Neha Agarwal", "date": "1992-06-03", "time": "17:45", "lat": 26.8467,
     "lon": 80.9462, "tz": "Asia/Kolkata", "gender": "F"},
    {"name": "Mei Lin Tan", "date": "1995-11-02", "time": "06:10", "lat": 1.3521,
     "lon": 103.8198, "tz": "Asia/Singapore", "gender": "F"},
    {"name": "Arjun Mehta", "date": "1990-02-11", "time": "09:20", "lat": 28.6139,
     "lon": 77.2090, "tz": "Asia/Kolkata", "gender": "M"},
    {"name": "Priya Nair", "date": "1992-02-29", "time": "23:55", "lat": -33.8688,
     "lon": 151.2093, "tz": "Australia/Sydney", "gender": "F"},          # leap day, far south
    {"name": "Unknown Time", "date": "1975-09-09", "time": "12:00", "lat": 51.5074,
     "lon": -0.1278, "tz": "Europe/London", "gender": "F", "time_confidence": "unknown"},
    {"name": "Long Ago", "date": "1890-01-20", "time": "08:30", "lat": 25.3176,
     "lon": 82.9739, "tz": "Asia/Kolkata", "gender": "M"},    # more than one Vimshottari cycle ago
    {"name": "Older Still", "date": "1799-01-20", "time": "08:30", "lat": 25.3176,
     "lon": 82.9739, "tz": "Asia/Kolkata", "gender": "M"},    # the first year the shipped ephemeris covers
]


def main() -> int:
    problems = []
    counts = set()
    core = None            # the sections a chart with a reliable birth time carries
    for person in PEOPLE:
        chart = EA.chart_obj(dict(person))
        details = app_details.build(chart)

        for lost in details.get("incomplete", []):
            problems.append(f"{person['name']}: the {lost['part']} part did not build - {lost['error']}")

        counts.add(len(details["sections"]))
        keys = {section.get("key") for section in details["sections"]}
        if core is None:
            core = keys
        else:
            # A chart may carry more than the reference one - an unknown birth time adds the BaZi hour
            # section, which is the engine being careful rather than a fault. Carrying fewer is the
            # silent shortfall this check exists for.
            lost = sorted(core - keys)
            if lost:
                problems.append(f"{person['name']}: missing {', '.join(lost)}")
        if len(details["vargas"]) != 16:
            problems.append(f"{person['name']}: {len(details['vargas'])} divisional charts, expected 16")
        if len(details["varga_meta"]) != len(details["vargas"]):
            problems.append(f"{person['name']}: the divisional charts and their names disagree")

        for i, section in enumerate(details["sections"]):
            if not section.get("title", {}).get("hi"):
                problems.append(f"{person['name']}: section {i} ({section.get('key')}) has no Hindi title")

    for line in problems:
        print("  " + line)
    print(f"details: {len(PEOPLE)} charts, {sorted(counts)[0] if counts else 0}-{sorted(counts)[-1] if counts else 0} "
          f"sections each, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
