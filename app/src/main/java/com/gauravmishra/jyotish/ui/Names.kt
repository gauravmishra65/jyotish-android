package com.gauravmishra.jyotish.ui

import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalConfiguration
import org.json.JSONObject
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.Locale

/**
 * Hindi for the engine's English names. The tables come from the skill's report code (assets/hindi_names.json,
 * written by tools/sync_engine.py); anything not in them is shown in English.
 */
object Names {
    private var tables: Map<String, Map<String, String>> = mapOf(
        "sign" to mapOf("Aries" to "मेष", "Taurus" to "वृषभ", "Gemini" to "मिथुन", "Cancer" to "कर्क", "Leo" to "सिंह",
            "Virgo" to "कन्या", "Libra" to "तुला", "Scorpio" to "वृश्चिक", "Sagittarius" to "धनु", "Capricorn" to "मकर",
            "Aquarius" to "कुंभ", "Pisces" to "मीन"),
        "planet" to mapOf("Sun" to "सूर्य", "Moon" to "चंद्र", "Mars" to "मंगल", "Mercury" to "बुध", "Jupiter" to "गुरु",
            "Venus" to "शुक्र", "Saturn" to "शनि", "Rahu" to "राहु", "Ketu" to "केतु"),
    )

    /** Called once at start-up with the contents of assets/hindi_names.json. */
    fun load(json: String) {
        val o = JSONObject(json)
        tables = o.keys().asSequence().associateWith { k ->
            val t = o.getJSONObject(k)
            t.keys().asSequence().associateWith { t.getString(it) }
        }
    }

    private fun lookup(table: String, english: String, lang: String) =
        if (lang == "hi") tables[table]?.get(english) ?: english else english

    /** A sign or a planet (the two tables never share a name). */
    fun of(english: String, lang: String): String =
        if (lang == "hi") tables["sign"]?.get(english) ?: tables["planet"]?.get(english) ?: english else english

    fun nakshatra(english: String, lang: String) = lookup("nakshatra", english, lang)
    fun yoga(english: String, lang: String) = lookup("yoga", english, lang)
    fun yogaCategory(english: String, lang: String) = lookup("yoga_category", english, lang)

    /** Dignity labels from the engine ("own sign", "friend's sign"); "n/a" for the nodes becomes a dash. */
    fun dignity(english: String, lang: String): String =
        if (english == "n/a" || english.isEmpty()) "–" else lookup("tag", english, lang)
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
