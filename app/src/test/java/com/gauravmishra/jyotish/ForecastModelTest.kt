package com.gauravmishra.jyotish

import com.gauravmishra.jyotish.data.ForecastModel
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test

/** forecast_ravi.json: engine_api.forecast for Ravi Shankar Tiwari (fictional), now = 2027-01-14, 3 years. */
class ForecastModelTest {
    private val raw by lazy { javaClass.classLoader!!.getResource("forecast_ravi.json")!!.readText() }
    private val m by lazy { ForecastModel.parse(raw) }

    @Test
    fun fourAreasThreeYears() {
        assertEquals(ForecastModel.AREA_KEYS, m.areas.map { it.key })
        assertEquals("2027-01-14", m.from)
        m.areas.forEach { a ->
            assertEquals(listOf("Y1", "Y2", "Y3"), a.years.map { it.id })
            assertTrue(a.title.hi.any { it in 'ऀ'..'ॿ' })
            a.years.forEach { y ->
                assertTrue(y.lean in setOf("supportive", "demanding", "mixed", "quiet"))
                assertTrue(y.summary.en.isNotEmpty() && y.summary.hi.isNotEmpty())
                (y.drivers + y.more).forEach { d -> assertTrue(d.text.en.isNotEmpty() && d.text.hi.isNotEmpty()) }
            }
        }
    }

    @Test
    fun marriageHasWindowsAndKnRaoMonths() {
        val a = m.area("marriage")
        assertTrue(a.windows.any { it.kind == "marriage" })
        assertTrue(a.windows.any { it.kind == "kn_rao" })
        assertNotNull(a.best)
    }

    @Test
    fun healthNeverNamesIllnessAndPointsToADoctor() {
        val h = m.area("health")
        assertTrue(h.subtitle.en.contains("Not medical advice"))
        assertTrue(h.windows.isEmpty())
    }

    @Test
    fun noForbiddenPredictionAnywhere() {
        // Case-sensitive: "Cancer" the sign is fine; the illness is never named.
        val banned = Regex("\\b(death|die|dies|disease|illness|cancer|divorce|accident|surgery|guarantee)\\b|मृत्यु|तलाक|रोग|दुर्घटना")
        assertFalse(banned.find(raw)?.value ?: "", banned.containsMatchIn(raw))
    }

    /** forecast_minor.json: Asha Kumari (fictional), born 2012-05-05, now = 2027-01-14. */
    @Test
    fun underEighteenGetsNoWeddingTalkAndNoMarriageWindows() {
        val f = ForecastModel.parse(javaClass.classLoader!!.getResource("forecast_minor.json")!!.readText())
        val m = f.area("marriage")
        assertTrue(m.subtitle.en.contains("18th birthday"))
        m.years.filter { it.from < "2030-05-05" }.forEach { y ->
            assertFalse(y.summary.en, Regex("wedding|marriage").containsMatchIn(y.summary.en))
            assertFalse(y.summary.hi, y.summary.hi.contains("विवाह"))
        }
        f.areas.flatMap { it.windows }.filter { it.kind in setOf("marriage", "kn_rao", "children") }
            .forEach { assertTrue("${it.kind} ${it.from}", it.from >= "2030-05-05") }
    }
}
