package com.gauravmishra.jyotish

import com.gauravmishra.jyotish.data.MangalCheck
import com.gauravmishra.jyotish.data.MatchModel
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class MatchModelTest {
    private val m by lazy { MatchModel.parse(javaClass.classLoader!!.getResource("match_ravi_neha.json")!!.readText()) }

    @Test
    fun totalRangeAndBand() {
        assertEquals(28.0, m.total, 0.0)
        assertEquals(36, m.outOf)
        assertEquals(27.5, m.rangeLow, 0.0)
        assertEquals(29.0, m.rangeHigh, 0.0)
        assertEquals("25to32", m.band)
    }

    @Test
    fun eightKootasInOrderAddUpToTheTotal() {
        assertEquals(MatchModel.KOOTA_ORDER, m.kootas.map { it.key })
        assertEquals(m.total, m.kootas.sumOf { it.score }, 1e-9)
        assertEquals(listOf(1, 2, 3, 4, 5, 6, 7, 8), m.kootas.map { it.max })
        val vashya = m.kootas.first { it.key == "vashya" }
        assertTrue(vashya.facts.any { it.first == "table" && it.second == "onlinejyotish.com" })
        assertFalse(vashya.facts.any { it.first == "score_by_table" })
    }

    @Test
    fun poruthamAndMangal() {
        assertEquals(10, m.porutham.size)
        assertEquals(7, m.poruthamAgree)
        assertTrue(m.essentialAllAgree)
        assertTrue(m.porutham.first { it.key == "rasi_adhipati" }.partial)
        val ravi = m.mangal.first { it.name == "Ravi Shankar Tiwari" }
        val neha = m.mangal.first { it.name == "Neha Agarwal" }
        assertFalse(ravi.counted)
        assertEquals(listOf("lagna"), neha.countedFrom)
        assertEquals(setOf(1, 2, 4, 7, 8, 12), MangalCheck.MANGAL_HOUSES)
    }
}
