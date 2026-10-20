package com.gauravmishra.jyotish

import com.gauravmishra.jyotish.data.Places
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.ProfileStore
import com.gauravmishra.jyotish.data.parseDmy
import com.gauravmishra.jyotish.data.parseHm
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.nio.file.Files
import java.time.LocalDate

class DataTest {
    private val places by lazy { File("src/main/assets/places.tsv").bufferedReader().useLines { Places(it) } }

    @Test
    fun placeListLoadsAndFindsIndianTowns() {
        assertTrue("about 69,000 places", places.size in 60_000..80_000)
        val v = places.search("Varan").first()
        assertEquals("Varanasi", v.name)
        assertEquals("India", v.country)
        assertEquals("Asia/Kolkata", v.tz)
        assertEquals("Moradabad", places.search("moradab").first().name)
    }

    @Test
    fun searchIgnoresAccentsAndCase() {
        assertEquals("São Paulo", places.search("sao paulo").first().name)
        assertEquals("Singapore", places.search("SINGAP").first().name)
    }

    @Test
    fun hindiSearchUsesDevanagariNames() {
        val r = places.search("वाराणसी")
        assertTrue(r.isNotEmpty())
        assertEquals("Varanasi", r.first().name)
    }

    @Test
    fun nearestPlaceGivesTheTimeZoneForTypedCoordinates() {
        assertEquals("Asia/Kolkata", places.nearest(28.84, 78.78)!!.tz)   // near Moradabad
        assertEquals("Europe/London", places.nearest(51.5, -0.12)!!.tz)
        assertEquals("America/New_York", places.nearest(40.71, -74.0)!!.tz)
    }

    @Test
    fun datesAndTimesAreParsedStrictly() {
        assertEquals(LocalDate.of(1988, 7, 14), parseDmy("14-07-1988"))
        assertEquals(LocalDate.of(1988, 7, 14), parseDmy("14/07/1988"))
        assertNull(parseDmy("31-02-1990"))
        assertNull(parseDmy("1988-07-14"))
        assertNull(parseDmy("01-01-1700"))
        assertNull(parseDmy(LocalDate.now().plusDays(2).let { "%02d-%02d-%04d".format(it.dayOfMonth, it.monthValue, it.year) }))
        assertEquals("09:05", parseHm("9:05"))
        assertEquals("14:35", parseHm("14.35"))
        assertNull(parseHm("24:00"))
        assertNull(parseHm("12:60"))
    }

    @Test
    fun profilesAndChartCacheRoundTrip() {
        val dir = Files.createTempDirectory("jyotish").toFile()
        val store = ProfileStore(dir)
        val p = Profile(name = "Ravi Shankar Tiwari", gender = "M", date = "1988-07-14", time = "14:35", confidence = "reliable",
            place = "Varanasi, India", lat = 25.3167, lon = 83.0104, tz = "Asia/Kolkata")
        store.save(listOf(p))
        assertEquals(listOf(p), ProfileStore(dir).load())
        assertEquals("RT", p.initials)
        store.cacheChart(p.id, "key1", "{\"x\":1}")
        assertEquals("{\"x\":1}", store.cachedChart(p.id, "key1"))
        assertNull("a different request must not reuse the cache", store.cachedChart(p.id, "key2"))
        store.deleteChart(p.id)
        assertNull(store.cachedChart(p.id, "key1"))
        dir.deleteRecursively()
    }

    @Test
    fun homeSummaryReadsARealEngineChart() {
        val json = javaClass.classLoader!!.getResource("chart_ravi.json")!!.readText()
        val s = AppViewModel.summarize(json)
        assertEquals("Scorpio", s.lagnaSign)
        assertEquals("Cancer", s.moonSign)
        assertEquals("Ketu", s.mahadasha)
        assertEquals("Mars", s.antardasha)
        assertEquals("2026-11-30", s.antardashaEnd)
        assertEquals("Rahu", s.nextAntardasha)
        assertTrue(s.warnings.any { "nakshatra boundary" in it })
    }
}
