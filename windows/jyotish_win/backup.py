"""Backup and restore of the saved people.

The file format is the Android app's, byte for byte: "GJB1" | salt (16) | iv (12) | AES-256-GCM, with
the key from PBKDF2-HMAC-SHA256 of the password and salt over 150,000 rounds and the magic as the
additional authenticated data. That is not a coincidence worth losing - it means a backup taken on the
phone restores on the desktop and the other way round, which is the only reason most people would want
a backup in the first place.

Nothing is uploaded. The person chooses where the file goes and the app never keeps the password, so a
forgotten password means a lost file: there is no recovery and the screen says so before asking for one.
"""
import json
import os

MAGIC = b"GJB1"
ROUNDS = 150_000
MIN_PASSWORD = 6
HEADER = len(MAGIC) + 16 + 12
TAG = 16

#: Android writes "confidence"; this app's own profiles call the same thing "time_confidence".
ALIASES = {"confidence": "time_confidence"}


class NotABackup(ValueError):
    """The file is not one of ours - wrong magic, or too short to hold a header and a tag."""


class WrongPassword(ValueError):
    """The password did not open it. GCM cannot tell a wrong password from a damaged file, and neither
    can this: both mean the same thing to the person holding it."""


def _aesgcm():
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError as e:                                      # pragma: no cover - a broken install
        raise RuntimeError("Backups need the 'cryptography' package: pip install cryptography") from e
    return AESGCM


def _key(password: str, salt: bytes) -> bytes:
    import hashlib
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ROUNDS, 32)


def encode(profiles: list[dict], password: str) -> bytes:
    if len(password) < MIN_PASSWORD:
        raise ValueError(f"The password needs at least {MIN_PASSWORD} characters.")
    body = json.dumps({"app": "gaurav-jyotish", "format": 1, "count": len(profiles),
                       "profiles": [_for_android(p) for p in profiles]},
                      ensure_ascii=False).encode("utf-8")
    salt, iv = os.urandom(16), os.urandom(12)
    sealed = _aesgcm()(_key(password, salt)).encrypt(iv, body, MAGIC)
    return MAGIC + salt + iv + sealed


def decode(blob: bytes, password: str) -> list[dict]:
    if len(blob) < HEADER + TAG or blob[:4] != MAGIC:
        raise NotABackup("That is not a Gaurav Jyotish backup file.")
    salt, iv = blob[4:20], blob[20:32]
    try:
        plain = _aesgcm()(_key(password, salt)).decrypt(iv, blob[32:], MAGIC)
    except Exception as e:                       # InvalidTag, and anything else the backend raises
        raise WrongPassword("Wrong password, or the file is damaged.") from e
    try:
        body = json.loads(plain.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise NotABackup("The file opened but holds nothing this app can read.") from e
    if body.get("app") != "gaurav-jyotish":
        raise NotABackup("That is not a Gaurav Jyotish backup file.")
    return [_from_android(p) for p in body.get("profiles", [])]


def _for_android(profile: dict) -> dict:
    """Write the field names the phone expects, keeping this app's own alongside them so that nothing
    is lost in a round trip through a version that does not know about a field yet."""
    out = dict(profile)
    for theirs, ours in ALIASES.items():
        if ours in out:
            out[theirs] = out[ours]
    return out


def _from_android(profile: dict) -> dict:
    out = dict(profile)
    for theirs, ours in ALIASES.items():
        if theirs in out and not out.get(ours):
            out[ours] = out.pop(theirs)
        out.pop(theirs, None)
    out.pop("v", None)
    return out
