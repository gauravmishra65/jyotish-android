#!/usr/bin/env bash
# Runs inside the emulator step of .github/workflows/spike.yml.
# Everything worth reading is also printed as a GitHub annotation, which can be read through the checks API.
set -u
adb logcat -c
adb logcat -G 64M || true
gradle :app:connectedFullDebugAndroidTest --stacktrace 2>&1 | tee connected.log
status=${PIPESTATUS[0]}
# The demo edition: only its own test (one profile, then the unlock), so the full suite is not run twice.
gradle :app:connectedDemoDebugAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=com.gauravmishra.jyotish.DemoTest --stacktrace 2>&1 | tee -a connected.log
[ "${PIPESTATUS[0]}" -eq 0 ] || status=1
adb logcat -d -s SPIKE:I > spike.log || true
adb logcat -d -s SHOT:I > shots.log || true
python3 - <<'EOF'
import base64, collections, os, re
parts = collections.defaultdict(dict)
for l in open("shots.log", errors="replace"):
    m = re.search(r"SHOT\s*:\s*(\S+) (\d+)/(\d+) (\S+)", l)
    if m:
        parts[m.group(1)][int(m.group(2))] = (int(m.group(3)), m.group(4))
os.makedirs("shots", exist_ok=True)
for name, d in parts.items():
    n = next(iter(d.values()))[0]
    if len(d) == n:
        open(f"shots/{name}.jpg", "wb").write(base64.b64decode("".join(d[i][1] for i in range(1, n + 1))))
print("screenshots:", sorted(os.listdir("shots")))
EOF
adb logcat -d -t 400 '*:E' > errors.log || true

python3 - <<'EOF'
import glob, re, xml.etree.ElementTree as ET
def note(level, title, body):
    body = body[:6000].replace("%", "%25").replace("\r", "").replace("\n", "%0A")
    print(f"::{level} title={title}::{body}")
spike = open("spike.log", errors="replace").read()
lines = [re.sub(r"^.*?SPIKE\s*:\s?", "", l) for l in spike.splitlines() if "SPIKE" in l]
if lines:
    note("notice", "Spike report", "".join(lines))
for f in glob.glob("app/build/outputs/androidTest-results/connected/**/*.xml", recursive=True):
    for tc in ET.parse(f).getroot().iter("testcase"):
        for fail in list(tc.findall("failure")) + list(tc.findall("error")):
            note("error", f"Test {tc.get('name')}", (fail.get("message") or "") + "\n" + (fail.text or "")[:4000])
EOF
if [ "$status" -ne 0 ]; then
  python3 tools/ci_annotate.py connected.log
  python3 - <<'EOF'
body = "".join(l for l in open("errors.log", errors="replace") if any(k in l for k in ("python", "Python", "chaquo", "AndroidRuntime", "jyotish")))[-5000:]
print("::error title=Device error log::" + body.replace("%", "%25").replace("\n", "%0A"))
EOF
fi

# Cold start of the app. The test run uninstalls it, so install the debug APK again first.
adb install -r app/build/outputs/apk/full/debug/app-full-debug.apk > /dev/null || true
for i in 1 2; do
  adb shell am force-stop com.gauravmishra.jyotish || true
  sleep 2
  adb shell am start -W -n com.gauravmishra.jyotish/.MainActivity | tee -a coldstart.log || true
done
echo "::notice title=Cold start::$(grep -E 'TotalTime|WaitTime' coldstart.log | tr '\n' ' ')"

# Release smoke test: each R8-minified edition must start and bring the Python engine up.
for ed in demo full play; do
  APK=app/build/outputs/apk/$ed/release/app-$ed-release.apk
  adb uninstall com.gauravmishra.jyotish > /dev/null || true
  if adb install $APK > release-$ed.log 2>&1; then
    adb logcat -c
    adb shell am start -W -n com.gauravmishra.jyotish/.MainActivity | tee -a release-$ed.log || true
    ok=""
    for i in $(seq 1 30); do
      if adb logcat -d -s ENGINE:I | grep -q "ready in"; then ok=1; break; fi
      sleep 1
    done
    sleep 3   # give the Play edition time to try (and fail) to reach Play, which this emulator does not have
    adb logcat -d -s ENGINE:* AndroidRuntime:E >> release-$ed.log || true
    if [ -n "$ok" ] && ! grep -q "FATAL EXCEPTION" release-$ed.log; then
      echo "::notice title=Release smoke test ($ed)::$(grep 'ready in' release-$ed.log | sed 's/^.*ENGINE *: //' | head -1); $(grep -E 'TotalTime' release-$ed.log | tr '\n' ' ')"
    else
      echo "::error title=Release smoke test ($ed)::$(tail -c 3000 release-$ed.log | tr '\n' ' ')"
      status=1
    fi
  else
    echo "::error title=Release install ($ed)::$(cat release-$ed.log | tr '\n' ' ')"
    status=1
  fi
  cat release-$ed.log >> release.log
done
exit $status
