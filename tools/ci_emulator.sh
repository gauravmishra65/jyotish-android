#!/usr/bin/env bash
# Runs inside the emulator step of .github/workflows/spike.yml.
# Everything worth reading is also printed as a GitHub annotation, which can be read through the checks API.
set -u
adb logcat -c
gradle :app:connectedDebugAndroidTest --stacktrace 2>&1 | tee connected.log
status=${PIPESTATUS[0]}
adb logcat -d -s SPIKE:I > spike.log || true
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
adb install -r app/build/outputs/apk/debug/app-debug.apk > /dev/null || true
for i in 1 2; do
  adb shell am force-stop com.gauravmishra.jyotish || true
  sleep 2
  adb shell am start -W -n com.gauravmishra.jyotish/.MainActivity | tee -a coldstart.log || true
done
echo "::notice title=Cold start::$(grep -E 'TotalTime|WaitTime' coldstart.log | tr '\n' ' ')"
exit $status
