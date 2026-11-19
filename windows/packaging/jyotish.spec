# -*- mode: python ; coding: utf-8 -*-
"""How the Windows app is packaged.

One folder, not one file. A single .exe would have to unpack 2 MB of ephemeris and 55 engine modules to
a temporary folder on every launch, which is both slower to start and harder for a person to look inside
- and being able to look inside matters for an app that promises nothing leaves the computer.

The engine ships as plain .py files rather than frozen modules on purpose: engine_api imports two dozen
of them by name at call time, so freezing it would mean listing every one as a hidden import and finding
out at runtime which was missed. As data it is the same tree the Android build carries, and bridge.py
finds it the same way.
"""
from pathlib import Path

ROOT = Path(SPECPATH).resolve().parent.parent          # the repo root
WINDOWS = ROOT / "windows"
ENGINE = ROOT / "app" / "src" / "main" / "python"

a = Analysis(
    [str(WINDOWS / "packaging" / "run.py")],
    pathex=[str(WINDOWS)],
    binaries=[],
    datas=[
        (str(ENGINE), "engine"),                       # the engine, its ephemeris and its data files
        (str(WINDOWS / "web"), "web"),                 # the interface
        (str(WINDOWS / "places.tsv"), "."),            # 70,000 birthplaces
        (str(WINDOWS / "packaging" / "app.ico"), "."),
    ],
    hiddenimports=["jyotish_win", "jyotish_win.api", "jyotish_win.backup", "jyotish_win.bridge",
                   "jyotish_win.places", "jyotish_win.storage", "jyotish_win.main"],
    excludes=["tkinter", "matplotlib", "numpy.distutils", "pytest", "setuptools"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="GauravJyotish",
    console=False,                                     # a window, not a console
    icon=str(WINDOWS / "packaging" / "app.ico"),
    version=str(WINDOWS / "packaging" / "version_info.txt"),
)

COLLECT(exe, a.binaries, a.datas, name="GauravJyotish")
