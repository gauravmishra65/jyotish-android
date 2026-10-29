package com.gauravmishra.jyotish

import com.gauravmishra.jyotish.store.Licence
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class LicenceTest {
    // Made by tools/licence/make_code.py with the real private key, for "test@example.com".
    private val code = "GJ1-PJRDZ-RNMKL-RX4G4-6TKK7-WUDSJ-SAIWQ-77DUH-2USBB-4B3CS-PR44C-2FWYC-HZPOQ-SHEBM-GEC42-3TRWR-WAV7M-MTTVR-IRFDI-KIP73-QL7IW-4OQ"

    @Test fun realCodeUnlocks() {
        assertTrue(Licence.verify("test@example.com", code))
        assertTrue(Licence.verify("  TEST@example.COM ", code))                       // case and spaces in the email
        assertTrue(Licence.verify("test@example.com", code.lowercase().replace("-", " ")))   // and in the code
    }

    @Test fun wrongEmailOrChangedCodeDoesNot() {
        assertFalse(Licence.verify("someone@example.com", code))
        val flipped = code.dropLast(1) + (if (code.last() == 'A') 'B' else 'A')
        assertFalse(Licence.verify("test@example.com", flipped))
        assertFalse(Licence.verify("test@example.com", "GJ1-ABCDE"))
        assertFalse(Licence.verify("", code))
        assertFalse(Licence.verify("test@example.com", "not a code!"))
    }

    @Test fun base32RoundTrip() {
        val raw = ByteArray(64) { (it * 37 + 11).toByte() }
        assertArrayEquals(raw, Licence.decode(Licence.encode(raw)))
    }
}
