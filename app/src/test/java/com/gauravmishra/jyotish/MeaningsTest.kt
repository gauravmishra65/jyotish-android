package com.gauravmishra.jyotish

import com.gauravmishra.jyotish.data.ChartModel
import com.gauravmishra.jyotish.data.Meanings
import com.gauravmishra.jyotish.ui.Names
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.BeforeClass
import org.junit.Test
import java.io.File

class MeaningsTest {
    companion object {
        @JvmStatic @BeforeClass
        fun load() {
            Meanings.load(File("src/main/assets/meanings.json").readText())
            Names.load(File("src/main/assets/hindi_names.json").readText())
        }
        private val PREDICTIVE = Regex("\\b(will (die|divorce|suffer)|death|divorce|disease|guarantee)", RegexOption.IGNORE_CASE)
    }

    @Test
    fun everyPlanetHouseKootaAndNumberHasBothLanguages() {
        listOf("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu").forEach {
            assertNotNull(it, Meanings.planet(it, "en")); assertNotNull(it, Meanings.planet(it, "hi"))
        }
        (1..12).forEach { assertNotNull(Meanings.house(it, "en")); assertNotNull(Meanings.house(it, "hi")) }
        listOf("varna", "vashya", "tara", "yoni", "graha_maitri", "gana", "bhakoot", "nadi").forEach { assertNotNull(it, Meanings.koota(it, "hi")) }
        listOf("dina", "gana", "mahendra", "stree_deergha", "yoni", "rasi", "rasi_adhipati", "vasya", "rajju", "vedha")
            .forEach { assertNotNull(it, Meanings.porutham(it, "en")) }
        ((1..9) + listOf(11, 22, 33)).forEach { assertNotNull(Meanings.number(it, "hi")) }
        assertTrue(Meanings.number(5, "en")!!.contains("Mercury"))
    }

    @Test
    fun everyYogaInTheChartHasAMeaningAndAHindiName() {
        val m = ChartModel.parse(javaClass.classLoader!!.getResource("chart_ravi.json")!!.readText())
        assertTrue(m.yogas.isNotEmpty())
        m.yogas.forEach { y ->
            assertFalse(y.id, Meanings.yoga(y.id, y.category, "en").isEmpty())
            assertFalse(y.id, Meanings.yoga(y.id, y.category, "hi").isEmpty())
            assertTrue("no Hindi name for ${y.name}", Names.yoga(y.name, "hi").any { it in 'ऀ'..'ॿ' })
        }
        assertEquals("राज योग (चतुर्थेश और पंचमेश)", Names.yoga("Raja yoga (4th and 5th lords)", "hi"))
        assertEquals(2, Meanings.yoga("gaja_kesari", "Named", "en").size)   // its own line, then the category's
    }

    @Test
    fun noLineReadsAsAPrediction() {
        val text = File("src/main/assets/meanings.json").readText()
        assertFalse(PREDICTIVE.find(text)?.value ?: "", PREDICTIVE.containsMatchIn(text))
    }
}
