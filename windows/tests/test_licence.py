"""Unlock codes.

The scheme is the Android app's, and the point of it is that one code bought once works on the phone and
on the desktop. Python cannot prove that about Kotlin, so LicenceCheck.java is the phone's side of
Licence.kt: a code made here is checked there, a code made there is checked here.

No real code and no private key appears in these tests. A throwaway key pair is generated each run, and
the shipped public key is used only to prove that a code made for a different key is refused.
"""
import base64
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jyotish_win import licence   # noqa: E402

EMAIL = "buyer@example.test"


def _throwaway_key():
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    key = ec.generate_private_key(ec.SECP256R1())
    public = base64.b64encode(key.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)).decode()
    private = base64.b64encode(key.private_bytes(
        serialization.Encoding.DER, serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption())).decode()
    return key, public, private


def _sign(key, email: str) -> str:
    """What the issuing tool does: sign, then write the 64 raw bytes in base32 after GJ1-."""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec, utils
    r, s = utils.decode_dss_signature(key.sign(licence.message(email), ec.ECDSA(hashes.SHA256())))
    raw = r.to_bytes(32, "big") + s.to_bytes(32, "big")
    out, buffer, bits = [], 0, 0
    for byte in raw:
        buffer = (buffer << 8) | byte
        bits += 8
        while bits >= 5:
            bits -= 5
            out.append(licence.B32[(buffer >> bits) & 31])
    if bits:
        out.append(licence.B32[(buffer << (5 - bits)) & 31])
    text = "".join(out)
    return "GJ1-" + "-".join(text[i:i + 5] for i in range(0, len(text), 5))


class CodeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key, cls.public, cls.private = _throwaway_key()
        cls.code = _sign(cls.key, EMAIL)

    def test_a_code_made_for_this_email_is_accepted(self):
        self.assertTrue(licence.verify(EMAIL, self.code, self.public))

    def test_how_the_code_is_typed_does_not_matter(self):
        """It is read off a screen and typed by hand, so spacing, dashes and case have to be forgiven."""
        for typed in (self.code.lower(), self.code.replace("-", ""), self.code.replace("-", " "),
                      f"  {self.code}  ", self.code.replace("GJ1-", "")):
            self.assertTrue(licence.verify(EMAIL, typed, self.public), f"refused {typed[:24]}…")

    def test_the_email_is_normalised_the_way_the_phone_normalises_it(self):
        for typed in ("  BUYER@Example.TEST", "Buyer@example.test ", EMAIL.upper()):
            self.assertTrue(licence.verify(typed, self.code, self.public), f"refused {typed!r}")

    def test_a_code_for_someone_else_is_refused(self):
        self.assertFalse(licence.verify("someone.else@example.test", self.code, self.public))

    def test_a_code_signed_with_another_key_is_refused(self):
        """The shipped public key is the real one; this code was made with a throwaway. If this ever
        passes, the app is accepting codes it did not issue."""
        self.assertFalse(licence.verify(EMAIL, self.code))

    def test_nonsense_is_refused_without_raising(self):
        for code in ("", "GJ1-", "not a code", "GJ1-11111", "GJ1-" + "A" * 200, "GJ2-ABCDE"):
            self.assertFalse(licence.verify(EMAIL, code, self.public), f"accepted {code!r}")

    def test_an_empty_email_is_refused(self):
        self.assertFalse(licence.verify("", self.code, self.public))
        self.assertFalse(licence.verify("   ", self.code, self.public))

    def test_one_altered_character_breaks_it(self):
        swapped = self.code.replace("A", "B", 1) if "A" in self.code else self.code.replace("B", "A", 1)
        self.assertNotEqual(swapped, self.code)
        self.assertFalse(licence.verify(EMAIL, swapped, self.public))


class PhoneCompatibilityTest(unittest.TestCase):
    """One code, both apps. Checked against the phone's own crypto rather than assumed."""

    @classmethod
    def setUpClass(cls):
        import shutil
        if not (shutil.which("javac") and shutil.which("java")):
            raise unittest.SkipTest("no JDK here; the phone-compatibility check needs javac and java")
        cls.key, cls.public, cls.private = _throwaway_key()

    def test_a_code_made_here_works_there_and_the_other_way_round(self):
        source = Path(__file__).resolve().parent / "LicenceCheck.java"
        with TemporaryDirectory() as tmp:
            work = Path(tmp)
            (work / "public.key").write_text(self.public)
            (work / "private.key").write_text(self.private)
            (work / "from_python.code").write_text(_sign(self.key, EMAIL))

            subprocess.run(["javac", "-d", str(work), str(source)], check=True, capture_output=True)
            done = subprocess.run(["java", "-cp", str(work), "LicenceCheck", str(work), EMAIL],
                                  check=True, capture_output=True, text=True)

            self.assertIn("PHONE ACCEPTS THE DESKTOP CODE: true", done.stdout, done.stdout)
            self.assertIn("PHONE REJECTS IT FOR ANOTHER EMAIL: true", done.stdout, done.stdout)

            theirs = (work / "from_java.code").read_text().strip()
            self.assertTrue(licence.verify(EMAIL, theirs, self.public),
                            "the desktop refused a code the phone would have issued")
            self.assertFalse(licence.verify("someone.else@example.test", theirs, self.public))


if __name__ == "__main__":
    unittest.main()
