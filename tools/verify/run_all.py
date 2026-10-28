"""Runs the three verification scripts (see README in this folder). Exit code 1 if any reports a problem."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
failed = []
for name in ("independent.py", "layer.py", "report_check.py"):
    print(f"\n===== {name}", flush=True)
    if subprocess.call([sys.executable, os.path.join(HERE, name)]) != 0:
        failed.append(name)
print("\nFAILED: " + ", ".join(failed) if failed else "\nall verification passed")
sys.exit(1 if failed else 0)
