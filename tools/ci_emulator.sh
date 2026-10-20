#!/usr/bin/env bash
# Runs inside the emulator step of .github/workflows/spike.yml.
set -u
adb logcat -c
gradle :app:connectedDebugAndroidTest --stacktrace
status=$?
adb logcat -d -s SPIKE:I > spike.log || true

# Cold start of the app (Python start happens in Application.onCreate, so it is included).
adb shell am force-stop com.gauravmishra.jyotish || true
sleep 2
adb shell am start -W -n com.gauravmishra.jyotish/.MainActivity | tee -a coldstart.log || true
adb shell am force-stop com.gauravmishra.jyotish || true
sleep 2
adb shell am start -W -n com.gauravmishra.jyotish/.MainActivity | tee -a coldstart.log || true
exit $status
