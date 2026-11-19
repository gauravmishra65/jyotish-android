"""The frozen app's entry point.

PyInstaller needs a script rather than a module, and this is it. Everything it does is in jyotish_win.
"""
import multiprocessing
import sys

from jyotish_win.main import main

if __name__ == "__main__":
    # A frozen Windows build re-executes itself for any child process. Without this, anything that
    # spawned one would start a second copy of the whole app instead.
    multiprocessing.freeze_support()
    sys.exit(main())
