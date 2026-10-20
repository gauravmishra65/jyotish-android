package com.gauravmishra.jyotish

import com.gauravmishra.jyotish.data.Abbrev
import com.gauravmishra.jyotish.data.ChartModel
import com.gauravmishra.jyotish.data.SIGNS
import com.gauravmishra.jyotish.ui.NorthLayout
import com.gauravmishra.jyotish.ui.SouthLayout
import com.gauravmishra.jyotish.ui.chartDescription
import com.gauravmishra.jyotish.ui.degMin
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class KundaliModelTest {
    private val m by lazy { ChartModel.parse(javaClass.classLoader!!.getResource("chart_ravi.json")!!.readText()) }

    @Test
    fun parsesTheEngineChart() {
        assertEquals("Scorpio", m.lagna.sign)
        assertEquals(7, m.lagna.signIndex)
        assertEquals(9, m.planets.size)
        assertEquals("Saturn", m.planetsInHouse(2).single().name)
        assertEquals(listOf("Jupiter", "Venus"), m.planetsInHouse(7).map { it.name }.sorted())
        assertTrue(m.planetsInHouse(1).isEmpty())
        assertEquals("Taurus", SIGNS[m.signOfHouse(7)])
        assertEquals("Ketu", m.currentMaha)
        assertEquals("Mars", m.currentAntar.lord)
        assertEquals(10, m.mahadashas.size)
        assertTrue(m.mahadashas.all { it.antardashas.size == 9 })
        assertEquals(7, m.strengths.size)
        assertEquals(337, m.savBySign.values.sum())          // Sarva Ashtakavarga always totals 337
        assertEquals("lahiri", m.ayanamsa)
    }

    @Test
    fun yogasAreReportableOnesRarestFirst() {
        assertEquals(17, m.yogas.size)
        assertEquals("chamara_2", m.yogas.first().id)
        val rates = m.yogas.mapNotNull { it.baseRate }
        assertEquals(rates.sorted(), rates)
        val malavya = m.yogas.first { it.id == "mahapurusha_venus" }
        assertEquals("strong", malavya.strength)
        assertEquals(listOf("Venus"), malavya.keyPlanets)
    }

    @Test
    fun chartLabelsAndDescription() {
        val saturn = m.planets.first { it.name == "Saturn" }
        assertEquals("Sa(R)", Abbrev.of(saturn, "en"))
        assertEquals("श(व)", Abbrev.of(saturn, "hi"))
        assertEquals("Ra", Abbrev.of(m.planets.first { it.name == "Rahu" }, "en"))  // nodes are not marked retrograde
        val d = chartDescription(m, "en", "House", "empty")
        assertTrue(d.startsWith("House 1, Scorpio: empty. House 2, Sagittarius: Saturn"))
        assertEquals("0°59′", degMin("0°59'27\""))
    }

    @Test
    fun layoutsCoverTwelvePlaces() {
        assertEquals(12, NorthLayout.planetAt.size)
        assertEquals(12, NorthLayout.signAt.size)
        assertEquals(12, SouthLayout.cellOfSign.toSet().size)
        assertTrue(SouthLayout.cellOfSign.none { (r, c) -> r in 1..2 && c in 1..2 })  // the centre stays empty
        assertEquals(0 to 0, SouthLayout.cellOfSign[11])   // Pisces top left
    }
}
