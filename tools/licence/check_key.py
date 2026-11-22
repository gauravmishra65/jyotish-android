#!/usr/bin/env python3
"""Is this .pem the key that makes unlock codes for the app people have installed?

    python3 tools/licence/check_key.py ~/secure/gaurav-jyotish-unlock-private-key.pem

The app verifies codes with one hard-coded public key. Only the private half of THAT pair can make codes it
accepts, so a candidate file is either the key or it is useless, and this says which in one line. Run it on
whichever file you think is the key; it reads the file and nothing else, and sends nothing anywhere.

With --new it makes a fresh key pair instead. Read what it prints before you use one: a new pair means a new
app build, and every code already issued stops working.
"""
import argparse
import base64
import pathlib
import sys

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

# Copied from app/src/main/java/com/gauravmishra/jyotish/store/Licence.kt
APP_PUBLIC_KEY = ("MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAElSoFIVAUDsHLdEhhX1uVybPtlq+H5MzfRTCjiBAPZK"
                  "O2Ay3aUAoQeFi8YqlUP11II67hUu9F81tRuo8fm7b2PQ==")


def public_half(private_key):
    der = private_key.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    return base64.b64encode(der).decode()


def check(path):
    data = pathlib.Path(path).read_bytes()
    try:
        key = serialization.load_pem_private_key(data, password=None)
    except TypeError:
        sys.exit("That file is password-protected. Decrypt it first, or use a key file without a password.")
    except Exception as e:
        sys.exit(f"That file is not a PEM private key this script can read: {e}")

    if not isinstance(key, ec.EllipticCurvePrivateKey) or key.curve.name != "secp256r1":
        sys.exit(f"Wrong kind of key: unlock codes need EC P-256, this is {type(key).__name__} "
                 f"{getattr(getattr(key, 'curve', None), 'name', '')}".strip())

    mine = public_half(key)
    print(f"file         : {path}")
    print(f"its public half : {mine}")
    print(f"the app wants   : {APP_PUBLIC_KEY}")
    print()
    if mine == APP_PUBLIC_KEY:
        print("MATCH. This is the key. Codes made with it work on every copy of the app already installed.")
        return 0
    print("NO MATCH. Codes made with this key will be rejected by the app people have installed.")
    print("Either this is the wrong file, or the original key is lost. If it is lost, see --new.")
    return 1


def new(path):
    p = pathlib.Path(path)
    if p.exists():
        sys.exit(f"{p} already exists. Refusing to overwrite a key file.")
    key = ec.generate_private_key(ec.SECP256R1())
    p.write_bytes(key.private_bytes(serialization.Encoding.PEM,
                                    serialization.PrivateFormat.PKCS8,
                                    serialization.NoEncryption()))
    try:
        p.chmod(0o600)
    except Exception:
        pass
    print(f"Written: {p}")
    print()
    print("This key makes codes that NOTHING currently installed will accept. To use it:")
    print()
    print("  1. Put this line in app/src/main/java/com/gauravmishra/jyotish/store/Licence.kt:")
    print()
    print(f'     const val PUBLIC_KEY = "{public_half(key)}"')
    print()
    print("  2. Raise versionCode, build, and release to Play. Only people who update get working codes.")
    print("  3. Every code you issued under the old key stops working. Reissue them from this key.")
    print()
    print("Keep this file in a password manager or an encrypted drive, and back it up. It is not in the repo")
    print("(*.pem is gitignored) and it cannot be recovered if lost - losing it costs another app release.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("keyfile", help="the .pem to check, or where to write one with --new")
    ap.add_argument("--new", action="store_true", help="make a new key pair instead of checking one")
    a = ap.parse_args()
    sys.exit(new(a.keyfile) if a.new else check(a.keyfile))
