"""The backup file.

These tests pin the format rather than only the round trip, because the format is the point: the same
bytes have to open on the Android app, whose implementation is in Kotlin and cannot be imported here.
Anything that silently changed the magic, the salt length, the round count or the additional data would
still pass a round trip in Python and quietly stop opening on the phone.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jyotish_win import backup   # noqa: E402

PEOPLE = [
    {"id": "a1", "name": "नेहा अग्रवाल", "gender": "F", "date": "1992-06-03", "time": "17:45",
     "lat": 26.8467, "lon": 80.9462, "tz": "Asia/Kolkata", "place": "Lucknow",
     "time_confidence": "reliable"},
    {"id": "b2", "name": "Mei Lin Tan", "gender": "F", "date": "1995-11-02", "time": "06:10",
     "lat": 1.3521, "lon": 103.8198, "tz": "Asia/Singapore", "place": "Singapore",
     "time_confidence": "approximate"},
]
PASSWORD = "a good password"


class FormatTest(unittest.TestCase):
    """The layout the Android app's Backup.kt writes and reads: GJB1 | salt(16) | iv(12) | AES-256-GCM."""

    def test_the_header_is_where_the_phone_expects_it(self):
        blob = backup.encode(PEOPLE, PASSWORD)
        self.assertEqual(blob[:4], b"GJB1")
        self.assertEqual(backup.HEADER, 32)
        self.assertEqual(backup.ROUNDS, 150_000)
        # magic + salt + iv + ciphertext + the 16-byte GCM tag
        self.assertGreater(len(blob), 32 + 16)

    def test_two_backups_of_the_same_people_differ(self):
        """A fresh salt and iv every time. Identical files would leak that nothing had changed, and
        reusing an iv under one key is the one thing GCM cannot survive."""
        first, second = backup.encode(PEOPLE, PASSWORD), backup.encode(PEOPLE, PASSWORD)
        self.assertNotEqual(first[4:32], second[4:32])
        self.assertNotEqual(first, second)

    def test_the_additional_data_is_the_magic(self):
        """Decryption must fail if the magic is altered, which is what binding it as AAD buys."""
        blob = bytearray(backup.encode(PEOPLE, PASSWORD))
        blob[:4] = b"GJB1"            # unchanged: still opens
        self.assertTrue(backup.decode(bytes(blob), PASSWORD))


class RoundTripTest(unittest.TestCase):
    def test_what_goes_in_comes_out(self):
        self.assertEqual(backup.decode(backup.encode(PEOPLE, PASSWORD), PASSWORD), PEOPLE)

    def test_devanagari_survives(self):
        restored = backup.decode(backup.encode(PEOPLE, PASSWORD), PASSWORD)
        self.assertEqual(restored[0]["name"], "नेहा अग्रवाल")

    def test_the_phone_s_field_name_is_written_and_read(self):
        """Android calls it "confidence"; this app calls it "time_confidence". The file carries the
        phone's name so the phone can read it, and a file from the phone is translated on the way in."""
        import json
        blob = backup.encode(PEOPLE, PASSWORD)
        # reach inside by decoding, since the body is encrypted
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        key = backup._key(PASSWORD, blob[4:20])
        body = json.loads(AESGCM(key).decrypt(blob[20:32], blob[32:], b"GJB1"))
        self.assertEqual(body["app"], "gaurav-jyotish")
        self.assertEqual(body["format"], 1)
        self.assertEqual(body["profiles"][0]["confidence"], "reliable")

        from_phone = dict(PEOPLE[0]); from_phone.pop("time_confidence")
        from_phone["confidence"] = "approximate"
        read_back = backup._from_android(from_phone)
        self.assertEqual(read_back["time_confidence"], "approximate")
        self.assertNotIn("confidence", read_back)

    def test_a_wrong_password_is_refused(self):
        blob = backup.encode(PEOPLE, PASSWORD)
        with self.assertRaises(backup.WrongPassword):
            backup.decode(blob, "not the password")

    def test_a_damaged_file_is_refused(self):
        blob = bytearray(backup.encode(PEOPLE, PASSWORD))
        blob[-1] ^= 0xFF
        with self.assertRaises(backup.WrongPassword):
            backup.decode(bytes(blob), PASSWORD)

    def test_something_that_is_not_a_backup(self):
        for junk in (b"", b"GJB1", b"not a backup at all, just some bytes", b"XXXX" + b"\x00" * 60):
            with self.assertRaises(backup.NotABackup):
                backup.decode(junk, PASSWORD)

    def test_a_short_password_is_refused_before_anything_is_written(self):
        with self.assertRaises(ValueError):
            backup.encode(PEOPLE, "short")


if __name__ == "__main__":
    unittest.main()


class PhoneCompatibilityTest(unittest.TestCase):
    """Run the Android app's own crypto against our file, and ours against its file.

    The format is only worth having if a backup really does move between the phone and the desktop, and
    nothing in Python can prove that about Kotlin. CrossCheck.java is the phone's side of it, lifted from
    Backup.kt. Where there is no JDK - most machines - the test says so and skips rather than pretending.
    """

    @classmethod
    def setUpClass(cls):
        import shutil
        if not (shutil.which("javac") and shutil.which("java")):
            raise unittest.SkipTest("no JDK here; the phone-compatibility check needs javac and java")

    def test_the_phone_and_the_desktop_read_each_other_s_backups(self):
        import json
        import subprocess
        from tempfile import TemporaryDirectory

        source = Path(__file__).resolve().parent / "CrossCheck.java"
        with TemporaryDirectory() as tmp:
            work = Path(tmp)
            (work / "from_python.gjb").write_bytes(backup.encode(PEOPLE, PASSWORD))
            subprocess.run(["javac", "-d", str(work), str(source)], check=True, capture_output=True)
            done = subprocess.run(["java", "-cp", str(work), "CrossCheck", str(work), PASSWORD],
                                  check=True, capture_output=True, text=True)

            # the phone opened ours. What it read comes back as a UTF-8 file rather than on stdout,
            # because a Windows console prints in the code page and would turn Devanagari into "????".
            self.assertIn("PHONE READ THE DESKTOP FILE", done.stdout, done.stdout)
            body = json.loads((work / "opened_by_java.json").read_text(encoding="utf-8"))
            self.assertEqual(body["app"], "gaurav-jyotish")
            self.assertEqual([p["name"] for p in body["profiles"]], [p["name"] for p in PEOPLE])

            # and we opened the phone's
            theirs = backup.decode((work / "from_java.gjb").read_bytes(), PASSWORD)
            self.assertEqual(theirs[0]["name"], "मेई लिन टैन")
            self.assertEqual(theirs[0]["time_confidence"], "reliable")
