package com.gauravmishra.jyotish

import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.ui.filterProfiles
import org.junit.Assert.assertEquals
import org.junit.Test

class SavedFilterTest {
    private fun p(name: String, place: String, group: String) =
        Profile(name = name, gender = "M", date = "1990-01-01", time = "10:00", confidence = "reliable", place = place, lat = 0.0, lon = 0.0, tz = "UTC", group = group)

    private val all = listOf(p("Zoë Fernández", "São Paulo", "clients"), p("arjun mehta", "London", "friends"), p("Ravi", "Varanasi", "family"))

    @Test
    fun searchIgnoresCaseAndAccentsAndSortsByName() {
        assertEquals(listOf("arjun mehta", "Ravi", "Zoë Fernández"), filterProfiles(all, "", "").map { it.name })
        assertEquals(listOf("Zoë Fernández"), filterProfiles(all, "zoe", "").map { it.name })
        assertEquals(listOf("Zoë Fernández"), filterProfiles(all, "sao", "").map { it.name })   // place, without the accent
    }

    @Test
    fun groupFilterCombinesWithSearch() {
        assertEquals(listOf("Ravi"), filterProfiles(all, "", "family").map { it.name })
        assertEquals(emptyList<String>(), filterProfiles(all, "ravi", "clients").map { it.name })
    }
}
