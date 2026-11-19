"""Offline unlock codes.

A port of the Android app's Licence.kt, and deliberately the same scheme, so that a code bought once
works on the phone and on the desktop: an ECDSA P-256 / SHA-256 signature over "GJ1|<email in lower
case>", written in base32 after the prefix "GJ1-".

The app holds only the public half of the key, so it can check a code and never make one. The private
key is not in this repository and never will be.
"""
import re

#: The same public key the Android app carries. A code made for one app verifies in the other.
PUBLIC_KEY = ("MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAElSoFIVAUDsHLdEhhX1uVybPtlq+H5MzfRTCjiBAPZKO2"
              "Ay3aUAoQeFi8YqlUP11II67hUu9F81tRuo8fm7b2PQ==")
PREFIX = "GJ1"
B32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"

#: How many people the demo saves. The same number as the phone's Sales.FREE_PROFILES.
FREE_PROFILES = 1


def normalize(email: str) -> str:
    return (email or "").strip().lower()


def message(email: str) -> bytes:
    return f"{PREFIX}|{normalize(email)}".encode("utf-8")


def decode(code: str) -> bytes | None:
    """The 64 raw signature bytes inside a code, or None. Spaces, dashes and case are ignored, because
    a code is read off a screen and typed by hand."""
    text = re.sub(r"[^A-Z0-9]", "", (code or "").upper())
    if text.startswith(PREFIX):
        text = text[len(PREFIX):]
    if not text or any(c not in B32 for c in text):
        return None
    buffer = bits = 0
    out = bytearray()
    for c in text:
        buffer = (buffer << 5) | B32.index(c)
        bits += 5
        if bits >= 8:
            bits -= 8
            out.append((buffer >> bits) & 0xFF)
    return bytes(out) if len(out) == 64 else None


def to_der(raw: bytes) -> bytes:
    """Most libraries want the signature as DER: SEQUENCE { INTEGER r, INTEGER s }."""
    def integer(part: bytes) -> bytes:
        value = part.lstrip(b"\x00") or b"\x00"
        if value[0] & 0x80:
            value = b"\x00" + value
        return bytes([0x02, len(value)]) + value

    body = integer(raw[:32]) + integer(raw[32:])
    return bytes([0x30, len(body)]) + body


def verify(email: str, code: str, public_key: str = PUBLIC_KEY) -> bool:
    """True when this code was made for this email with the matching private key.

    Every failure answers the same way - a wrong code, a damaged one, a code for somebody else, a
    missing crypto library - because the person on the other side can do nothing different about any
    of them, and a message that distinguishes them tells an attacker which part they got right.
    """
    if not normalize(email):
        return False
    raw = decode(code)
    if raw is None:
        return False
    try:
        from base64 import b64decode

        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives.serialization import load_der_public_key

        key = load_der_public_key(b64decode(public_key))
        if not isinstance(key, ec.EllipticCurvePublicKey):
            return False
        key.verify(to_der(raw), message(email), ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False
