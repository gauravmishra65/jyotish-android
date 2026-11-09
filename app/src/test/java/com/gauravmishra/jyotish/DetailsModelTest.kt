package com.gauravmishra.jyotish

import com.gauravmishra.jyotish.data.ChartModel
import com.gauravmishra.jyotish.data.DetailBlock
import com.gauravmishra.jyotish.data.DetailsModel
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.varga
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class DetailsModelTest {
    private val json by lazy { javaClass.classLoader!!.getResource("chart_ravi.json")!!.readText() }
    private val d by lazy { DetailsModel.parse(json)!! }

    @Test
    fun allSectionsPresentInBothLanguages() {
        assertEquals(listOf("panchang", "doshas", "avakahada", "pratyantar", "sensitivity", "chara", "narayana", "arudhas", "bhava_chalit",
            "ashtakavarga", "yogini", "jaimini", "varshaphal", "lalkitab", "kp", "western_timing"), d.sections.map { it.key })
        d.sections.forEach { s ->
            assertTrue(s.key, s.title.hi.any { it in '\u0900'..'\u097F' })
            assertTrue(s.key, s.blocks.isNotEmpty())
        }
        val av = d.sections.first { it.key == "ashtakavarga" }.blocks.first() as DetailBlock.Table
        assertEquals(13, av.head.size)                    // planet + 12 houses
        assertEquals("337", av.rows.last().drop(1).sumOf { it.en.toInt() }.toString())
    }

    @Test
    fun allSixteenDivisionalChartsWithNames() {
        assertEquals(16, d.vargas.size)
        assertEquals(listOf("D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"), d.vargaMeta.map { it.key })
        d.vargaMeta.forEach { assertTrue(it.key, d.vargas.containsKey(it.key) && it.use.hi.isNotBlank()) }
    }

    @Test
    fun avakahadaGivesTheNameSyllable() {
        val t = d.sections.first { it.key == "avakahada" }.blocks.first() as DetailBlock.Table
        val syl = t.rows.first { it[0].en.startsWith("Name syllable") }[1]
        assertTrue(syl.en, syl.en.startsWith("Hu"))        // Moon in Pushya, pada 1
        assertTrue(syl.hi, syl.hi.startsWith("हू"))
    }

    @Test
    fun noSectionShowsForbiddenWords() {
        val bad = Regex("(?i:\\b(death|dies?|disease|illness|divorce|accident|widow|childless|poverty|blind)\\b)|मृत्यु|मौत|तलाक|बीमार|विधवा")
        d.sections.forEach { s ->
            val all = s.blocks.flatMap { b -> when (b) {
                is DetailBlock.Para -> listOf(b.text)
                is DetailBlock.Items -> b.items
                is DetailBlock.Table -> b.rows.flatten() + b.head
            } } + listOfNotNull(s.title, s.intro, s.note)
            all.flatMap { listOf(it.en, it.hi) }.forEach { assertFalse("${s.key}: $it", bad.containsMatchIn(it)) }
        }
    }

    @Test
    fun lalKitabNeverShowsForbiddenWords() {
        val bad = Regex("(?i:\\b(death|dies?|disease|illness|divorce|accident|widow|childless|poverty|blind)\\b)|मृत्यु|मौत|तलाक|बीमार|विधवा")
        val lk = d.sections.first { it.key == "lalkitab" }
        val all = lk.blocks.flatMap { b -> when (b) {
            is DetailBlock.Para -> listOf(b.text)
            is DetailBlock.Items -> b.items
            is DetailBlock.Table -> b.rows.flatten()
        } }.flatMap { listOf(it.en, it.hi) }
        all.forEach { assertFalse(it, bad.containsMatchIn(it)) }
    }

    @Test
    fun navamsaChartMovesPlanetsToTheirD9Signs() {
        val m = ChartModel.parse(json)
        val d9 = m.varga(d.vargas.getValue("D9"))
        assertEquals(d.vargas.getValue("D9")["Lagna"], d9.lagna.sign)
        d9.planets.forEach { p ->
            assertEquals(d.vargas.getValue("D9")[p.name], p.sign)
            assertEquals((p.signIndex - d9.lagna.signIndex + 12) % 12 + 1, p.house)
        }
    }

    @Test
    fun oldCachedChartHasNoDetails() {
        assertNull(DetailsModel.parse(JSONObject(json).apply { remove("details") }.toString()))
    }

    @Test
    fun residenceGoesToTheEngineOnlyWhenSet() {
        val p = Profile(name = "A", gender = "M", date = "1990-01-01", time = "10:00", confidence = "reliable", place = "X", lat = 1.0, lon = 2.0, tz = "UTC")
        assertFalse(p.chartRequest("2026-10-29", "lahiri", "mean").has("current_lat"))
        val q = p.copy(residence = "Singapore", resLat = 1.35, resLon = 103.82)
        val r = q.chartRequest("2026-10-29", "lahiri", "mean")
        assertEquals(1.35, r.getDouble("current_lat"), 1e-9)
        assertEquals("Singapore", Profile.fromJson(q.toJson()).residence)
    }
}
