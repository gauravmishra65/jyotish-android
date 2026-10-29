#!/usr/bin/env python3
"""Make a Gaurav Jyotish unlock code for a buyer's email.

    python3 tools/licence/make_code.py --key ~/secure/gaurav-jyotish-unlock-private-key.pem buyer@example.com

The private key must never be committed or shared. The app checks codes with the public key in
app/src/main/java/com/gauravmishra/jyotish/store/Licence.kt. Needs: pip install cryptography
"""
import argparse
import sys

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature, encode_dss_signature

B32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"


def normalize(email):
    return email.strip().lower()


def encode(raw):
    out, buf, bits = [], 0, 0
    for b in raw:
        buf = (buf << 8) | b
        bits += 8
        while bits >= 5:
            bits -= 5
            out.append(B32[(buf >> bits) & 31])
    if bits:
        out.append(B32[(buf << (5 - bits)) & 31])
    s = "".join(out)
    return "GJ1-" + "-".join(s[i:i + 5] for i in range(0, len(s), 5))


def decode(code):
    s = "".join(c for c in code.upper() if c.isalnum())
    s = s[3:] if s.startswith("GJ1") else s
    buf, bits, out = 0, 0, bytearray()
    for c in s:
        buf = (buf << 5) | B32.index(c)
        bits += 5
        if bits >= 8:
            bits -= 8
            out.append((buf >> bits) & 0xFF)
    return bytes(out)


def make(key, email):
    der = key.sign(("GJ1|" + normalize(email)).encode(), ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(der)
    return encode(r.to_bytes(32, "big") + s.to_bytes(32, "big"))


def check(public_key, email, code):
    raw = decode(code)
    if len(raw) != 64:
        return False
    der = encode_dss_signature(int.from_bytes(raw[:32], "big"), int.from_bytes(raw[32:], "big"))
    try:
        public_key.verify(der, ("GJ1|" + normalize(email)).encode(), ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--key", required=True, help="path to the private key (.pem)")
    ap.add_argument("email")
    a = ap.parse_args()
    key = serialization.load_pem_private_key(open(a.key, "rb").read(), password=None)
    code = make(key, a.email)
    assert check(key.public_key(), a.email, code)
    print(f"Email: {normalize(a.email)}\nCode:  {code}")
    print("\nSend both to the buyer: in the app, open Settings > Unlock full version, enter the email and paste the code.")
    sys.exit(0)
