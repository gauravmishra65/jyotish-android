package com.gauravmishra.jyotish

import androidx.test.ext.junit.runners.AndroidJUnit4
import com.gauravmishra.jyotish.data.Backup
import com.gauravmishra.jyotish.data.Profile
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Test
import org.junit.runner.RunWith

/** The backup file opens only with its password and gives back exactly the people put in. */
@RunWith(AndroidJUnit4::class)
class BackupTest {
    private val people = listOf(
        Profile(name = "Ravi Shankar Tiwari", gender = "M", date = "1988-07-14", time = "14:35", confidence = "reliable",
            place = "Varanasi, India", lat = 25.3176, lon = 82.9739, tz = "Asia/Kolkata"),
        Profile(name = "Priya Nair", gender = "F", date = "1972-03-12", time = "06:05", confidence = "certificate",
            place = "Kochi, India", lat = 9.9312, lon = 76.2673, tz = "Asia/Kolkata", residence = "Singapore", resLat = 1.3521, resLon = 103.8198),
    )

    @Test
    fun roundTripAndWrongPassword() {
        val file = Backup.encode(people, "test-pass-1".toCharArray())
        assertNotEquals(-1, String(file, Charsets.ISO_8859_1).indexOf("GJB1"))
        assertEquals(-1, String(file, Charsets.ISO_8859_1).indexOf("Ravi"))      // the names are not readable in the file
        val back = Backup.decode(file, "test-pass-1".toCharArray())
        assertEquals(people.map { it.toJson().toString() }, back.map { it.toJson().toString() })
        val wrong = runCatching { Backup.decode(file, "another".toCharArray()) }.exceptionOrNull()
        assertEquals(Backup.WrongPassword::class, wrong!!::class)
        val junk = runCatching { Backup.decode("hello world, not a backup at all....".toByteArray(), "x".toCharArray()) }.exceptionOrNull()
        assertEquals(Backup.NotABackup::class, junk!!::class)
    }
}
