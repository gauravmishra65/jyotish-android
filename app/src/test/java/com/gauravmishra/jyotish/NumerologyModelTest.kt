package com.gauravmishra.jyotish

import com.gauravmishra.jyotish.data.NameOptions
import com.gauravmishra.jyotish.data.NumerologyModel
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class NumerologyModelTest {
    private val m by lazy { NumerologyModel.parse(javaClass.classLoader!!.getResource("chart_ravi.json")!!.readText()) }

    @Test
    fun coreNumbers() {
        assertEquals(5, m.mulank); assertEquals("Mercury", m.mulankPlanet)
        assertEquals(2, m.bhagyank); assertEquals("Moon", m.bhagyankPlanet)
        assertEquals(44, m.chaldeanCompound); assertEquals(8, m.chaldeanRoot)
        assertEquals(2, m.lifePath); assertEquals(11, m.lifePathAlt)
        assertEquals(4, m.destiny); assertEquals(4, m.personalYear)
        assertEquals(listOf(13, 14), m.karmicDebt)
        assertEquals(listOf(3, 6, 7), m.karmicLessons)
    }

    @Test
    fun loshuGridInLayoutOrder() {
        assertEquals(NumerologyModel.LOSHU_LAYOUT, m.loshu.map { it.first })
        assertEquals("4", m.loshu[0].second)       // top left is the 4 cell
        assertEquals("", m.loshu[3].second)        // 3 is missing
        assertEquals("88", m.loshu[6].second)
        assertEquals(listOf(3, 6), m.missing)
        assertEquals(8, m.planes.size)
        assertEquals(3, m.kua); assertEquals("East", m.kuaGroup)
        assertEquals(4, m.kuaGood.size)
    }

    @Test
    fun nameOptions() {
        val n = NameOptions.parse(javaClass.classLoader!!.getResource("names_ravi.json")!!.readText())
        assertEquals(44, n.original.compound)
        assertFalse(n.alreadyFits)
        assertTrue(n.options.first().spelling.startsWith("Ravvi"))
        assertTrue(n.options.none { it.spelling.startsWith("Rave ") })
        assertEquals("V दोहरा", NameOptions.changeHi("double V"))
        assertEquals("अंत में i की जगह ey", NameOptions.changeHi("final i to ey"))
    }
}
