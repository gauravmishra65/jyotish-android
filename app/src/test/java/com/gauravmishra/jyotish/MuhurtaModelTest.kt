package com.gauravmishra.jyotish

import com.gauravmishra.jyotish.data.MuhurtaResult
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class MuhurtaModelTest {
    private val r by lazy { MuhurtaResult.parse(javaClass.classLoader!!.getResource("muhurta_ravi_neha.json")!!.readText()) }

    @Test
    fun windowsGroupIntoDays() {
        assertEquals("marriage", r.event)
        assertEquals(40, r.windows.size)
        assertEquals(8, r.byDay.size)
        assertEquals("2027-01-14", r.byDay.first().first)
        assertTrue(r.byDay.all { (_, ws) -> ws.zipWithNext().all { (a, b) -> a.score >= b.score } })
    }

    @Test
    fun strongestFirstAndTithiInPaksha() {
        val best = r.best(3).first()
        assertEquals("2027-01-14 22:06", best.start)
        assertEquals(5, best.score)
        assertTrue(r.windows.all { it.tithiInPaksha in 1..15 })
        assertTrue(r.windows.all { it.paksha == "Shukla" || it.paksha == "Krishna" })
    }

    @Test
    fun hindiFieldsAreFilled() {
        val w = r.best(1).first()
        assertEquals("गुरुवार", w.weekdayHi)
        assertEquals("कन्या", w.lagnaHi)
        assertEquals(w.supports.size, w.supportsHi!!.size)
        assertTrue(w.supportsHi!!.none { it.contains("lagna") || it.contains("Thursday") })
        assertTrue(r.disclaimer.isNotEmpty())
    }
}
