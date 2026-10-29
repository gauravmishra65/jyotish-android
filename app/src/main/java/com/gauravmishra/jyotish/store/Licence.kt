package com.gauravmishra.jyotish.store

import java.security.KeyFactory
import java.security.Signature
import java.security.spec.X509EncodedKeySpec
import java.util.Base64
import java.util.Locale

/**
 * Offline unlock codes. A code is an ECDSA P-256 / SHA-256 signature over "GJ1|<email in lower case>", made with
 * Gaurav Mishra's private key (kept outside this repository; see tools/licence/README.md) and written in base32
 * after the prefix "GJ1-". The app holds only the public key, so it can check a code but never make one.
 */
object Licence {
    const val PUBLIC_KEY = "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAElSoFIVAUDsHLdEhhX1uVybPtlq+H5MzfRTCjiBAPZKO2Ay3aUAoQeFi8YqlUP11II67hUu9F81tRuo8fm7b2PQ=="
    private const val PREFIX = "GJ1"
    private const val B32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"

    fun normalize(email: String) = email.trim().lowercase(Locale.ROOT)
    fun message(email: String) = "$PREFIX|${normalize(email)}".toByteArray(Charsets.UTF_8)

    /** The 64-byte signature (r then s) inside a code, or null. Spaces, dashes and letter case are ignored. */
    fun decode(code: String): ByteArray? {
        var s = code.uppercase(Locale.ROOT).filter { it.isLetterOrDigit() }
        if (s.startsWith(PREFIX)) s = s.removePrefix(PREFIX)
        if (s.any { it !in B32 }) return null
        var buf = 0L; var bits = 0
        val out = java.io.ByteArrayOutputStream()
        for (c in s) {
            buf = (buf shl 5) or B32.indexOf(c).toLong(); bits += 5
            if (bits >= 8) { bits -= 8; out.write(((buf shr bits) and 0xFF).toInt()) }
        }
        return out.toByteArray().takeIf { it.size == 64 }
    }

    fun encode(sig: ByteArray): String {
        val sb = StringBuilder(); var buf = 0L; var bits = 0
        for (b in sig) {
            buf = (buf shl 8) or (b.toLong() and 0xFF); bits += 8
            while (bits >= 5) { bits -= 5; sb.append(B32[((buf shr bits) and 31).toInt()]) }
        }
        if (bits > 0) sb.append(B32[((buf shl (5 - bits)) and 31).toInt()])
        return "$PREFIX-" + sb.chunked(5).joinToString("-")
    }

    /** True when [code] was made for [email] with the key whose public half is [publicKey]. */
    fun verify(email: String, code: String, publicKey: String = PUBLIC_KEY): Boolean {
        if (normalize(email).isEmpty()) return false
        val raw = decode(code) ?: return false
        return try {
            val key = KeyFactory.getInstance("EC").generatePublic(X509EncodedKeySpec(Base64.getDecoder().decode(publicKey)))
            Signature.getInstance("SHA256withECDSA").run { initVerify(key); update(message(email)); verify(toDer(raw)) }
        } catch (e: Exception) {
            false
        }
    }

    /** Java wants the signature as DER: SEQUENCE { INTEGER r, INTEGER s }. */
    fun toDer(raw: ByteArray): ByteArray {
        fun int(b: ByteArray): ByteArray {
            var v = b.dropWhile { it == 0.toByte() }.toByteArray()
            if (v.isEmpty()) v = byteArrayOf(0)
            if (v[0].toInt() and 0x80 != 0) v = byteArrayOf(0) + v
            return byteArrayOf(0x02, v.size.toByte()) + v
        }
        val body = int(raw.copyOfRange(0, 32)) + int(raw.copyOfRange(32, 64))
        return byteArrayOf(0x30, body.size.toByte()) + body
    }
}
