package com.gauravmishra.jyotish.ui

import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalConfiguration
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.Locale

/** Hindi for the engine's English names (signs, planets), matching the skill's report glossary. */
object Names {
    private val hi = mapOf(
        "Aries" to "मेष", "Taurus" to "वृषभ", "Gemini" to "मिथुन", "Cancer" to "कर्क", "Leo" to "सिंह", "Virgo" to "कन्या",
        "Libra" to "तुला", "Scorpio" to "वृश्चिक", "Sagittarius" to "धनु", "Capricorn" to "मकर", "Aquarius" to "कुंभ", "Pisces" to "मीन",
        "Sun" to "सूर्य", "Moon" to "चंद्र", "Mars" to "मंगल", "Mercury" to "बुध", "Jupiter" to "गुरु", "Venus" to "शुक्र",
        "Saturn" to "शनि", "Rahu" to "राहु", "Ketu" to "केतु",
    )

    fun of(english: String, lang: String): String = if (lang == "hi") hi[english] ?: english else english
}

@Composable
fun currentLang(): String = LocalConfiguration.current.locales[0].language

/** 2026-11-30 as "30 Nov 2026" (or the Hindi month name). */
fun prettyDate(iso: String, lang: String): String = try {
    LocalDate.parse(iso.take(10)).format(DateTimeFormatter.ofPattern("d MMM yyyy", Locale.forLanguageTag(lang)))
} catch (e: Exception) {
    iso
}

fun longToday(lang: String): String =
    LocalDate.now().format(DateTimeFormatter.ofPattern("EEEE, d MMMM yyyy", Locale.forLanguageTag(lang)))
