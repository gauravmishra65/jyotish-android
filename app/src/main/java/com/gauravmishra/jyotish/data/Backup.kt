package com.gauravmishra.jyotish.data

import org.json.JSONArray
import org.json.JSONObject
import java.security.SecureRandom
import javax.crypto.AEADBadTagException
import javax.crypto.Cipher
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.PBEKeySpec
import javax.crypto.spec.SecretKeySpec

/**
 * Backup file of the saved people (v16): JSON of every profile, encrypted with a password the person chooses.
 * Layout: "GJB1" | salt (16) | iv (12) | AES-256-GCM ciphertext. The key is PBKDF2-HMAC-SHA256 (150,000 rounds) of the
 * password and salt. Nothing is sent anywhere: the person saves the file where they like (Drive, email, a USB stick)
 * through the system file picker, and the app keeps no copy of the password.
 */
object Backup {
    private val MAGIC = "GJB1".toByteArray()
    private const val ROUNDS = 150_000
    const val MIN_PASSWORD = 6

    class WrongPassword : Exception("wrong password or damaged file")
    class NotABackup : Exception("not a Gaurav Jyotish backup file")

    private fun key(password: CharArray, salt: ByteArray): SecretKeySpec {
        val spec = PBEKeySpec(password, salt, ROUNDS, 256)
        val bytes = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).encoded
        spec.clearPassword()
        return SecretKeySpec(bytes, "AES")
    }

    fun encode(profiles: List<Profile>, password: CharArray): ByteArray {
        val body = JSONObject().put("app", "gaurav-jyotish").put("format", 1).put("count", profiles.size)
            .put("profiles", JSONArray(profiles.map { it.toJson() })).toString().toByteArray(Charsets.UTF_8)
        val rnd = SecureRandom()
        val salt = ByteArray(16).also(rnd::nextBytes)
        val iv = ByteArray(12).also(rnd::nextBytes)
        val c = Cipher.getInstance("AES/GCM/NoPadding")
        c.init(Cipher.ENCRYPT_MODE, key(password, salt), GCMParameterSpec(128, iv))
        c.updateAAD(MAGIC)
        return MAGIC + salt + iv + c.doFinal(body)
    }

    fun decode(file: ByteArray, password: CharArray): List<Profile> {
        if (file.size < 4 + 16 + 12 + 16 || !file.copyOfRange(0, 4).contentEquals(MAGIC)) throw NotABackup()
        val salt = file.copyOfRange(4, 20)
        val iv = file.copyOfRange(20, 32)
        val c = Cipher.getInstance("AES/GCM/NoPadding")
        c.init(Cipher.DECRYPT_MODE, key(password, salt), GCMParameterSpec(128, iv))
        c.updateAAD(MAGIC)
        val plain = try { c.doFinal(file, 32, file.size - 32) } catch (e: AEADBadTagException) { throw WrongPassword() }
        val o = JSONObject(String(plain, Charsets.UTF_8))
        if (o.optString("app") != "gaurav-jyotish") throw NotABackup()
        val a = o.getJSONArray("profiles")
        return (0 until a.length()).map { Profile.fromJson(a.getJSONObject(it)) }
    }
}
