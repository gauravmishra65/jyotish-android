package com.gauravmishra.jyotish.data

import java.text.Normalizer
import kotlin.math.cos
import kotlin.math.sqrt

data class Place(
    val name: String,
    val countryCode: String,
    val country: String,
    val lat: Double,
    val lon: Double,
    val tz: String,
    val population: Int,
    val hindiNames: List<String>,
    /** Other English spellings and old names (Bombay, Allahabad), searched too. */
    val otherNames: List<String> = emptyList(),
    /** The other name the search matched, shown in brackets so "Allahabad" finds "Prayagraj (Allahabad)". */
    val matchedAs: String? = null,
    /** District and state, for villages (several share a name). */
    val region: String = "",
) {
    val label: String get() = (if (matchedAs != null) "$name ($matchedAs)" else name) +
        (if (region.isNotEmpty()) ", $region" else "") + if (country.isNotEmpty()) ", $country" else ""
}

/**
 * Offline place search over the GeoNames list in assets/places.tsv (see tools/make_places.py).
 * Rows are already sorted by population, so ties keep the larger place first.
 */
class Places(lines: Sequence<String>) {
    private val places: List<Place>
    private val keys: List<String>
    private val otherKeys: List<List<String>>
    private val countryByCode: Map<String, String>

    init {
        var zones = emptyList<String>()
        val countries = HashMap<String, String>()
        val list = ArrayList<Place>(70000)
        for (line in lines) {
            if (line.isEmpty()) continue
            if (line.startsWith("#tz\t")) { zones = line.split('\t').drop(1); continue }
            if (line.startsWith("#cc\t")) {
                line.split('\t').drop(1).forEach { kv -> kv.split('=', limit = 2).let { if (it.size == 2) countries[it[0]] = it[1] } }
                continue
            }
            val f = line.split('\t')
            if (f.size < 6) continue
            list += Place(
                name = f[0], countryCode = f[1], country = countries[f[1]] ?: f[1],
                lat = f[2].toDouble(), lon = f[3].toDouble(), tz = zones.getOrElse(f[4].toInt()) { "UTC" },
                population = f[5].toInt(),
                hindiNames = if (f.size > 6 && f[6].isNotEmpty()) f[6].split('|') else emptyList(),
                otherNames = if (f.size > 7 && f[7].isNotEmpty()) f[7].split('|') else emptyList(),
            )
        }
        places = list
        countryByCode = countries
        keys = list.map { fold(it.name) }
        otherKeys = list.map { p -> p.otherNames.map { fold(it) } }
    }

    val size: Int get() = places.size
    /** Country names by code, for the village list. */
    val countryNames: Map<String, String> get() = countryByCode

    /** Up to [limit] places: names starting with the query first, then a word starting with it, then containing it. */
    fun search(query: String, limit: Int = 8): List<Place> {
        val q = fold(query.trim())
        if (q.length < 2) return emptyList()
        val devanagari = query.any { it in 'ऀ'..'ॿ' }
        val buckets = Array(3) { ArrayList<Place>() }
        for (i in places.indices) {
            var score = if (devanagari) {
                val names = places[i].hindiNames
                when {
                    names.any { it.startsWith(query.trim()) } -> 0
                    names.any { it.contains(query.trim()) } -> 2
                    else -> -1
                }
            } else {
                val k = keys[i]
                when {
                    k.startsWith(q) -> 0
                    k.contains(" $q") || k.contains("-$q") -> 1
                    q.length >= 3 && k.contains(q) -> 2
                    else -> -1
                }
            }
            // an old name or other spelling (Bombay, Allahabad) when the main name did not match
            var alias: String? = null
            val other = if (score < 0 && !devanagari && q.length >= 3) otherKeys[i].indexOfFirst { it.startsWith(q) } else -1
            if (other >= 0) { score = 0; alias = places[i].otherNames[other] }
            if (score >= 0 && buckets[score].size < limit) buckets[score] += if (alias != null) places[i].copy(matchedAs = alias) else places[i]
            if (buckets[0].size >= limit) break
        }
        return buckets.flatMap { it }.take(limit)
    }

    /** The listed place nearest to a point (used for the time zone when coordinates are typed in). */
    fun nearest(lat: Double, lon: Double): Place? {
        val k = cos(Math.toRadians(lat))
        return places.minByOrNull { p ->
            val dx = (((p.lon - lon + 540) % 360) - 180) * k
            val dy = p.lat - lat
            dx * dx + dy * dy
        }
    }

    /** Approximate distance in km, for showing how far the nearest listed place is. */
    fun distanceKm(lat1: Double, lon1: Double, lat2: Double, lon2: Double): Double {
        val k = cos(Math.toRadians((lat1 + lat2) / 2))
        val dx = (((lon2 - lon1 + 540) % 360) - 180) * k
        val dy = lat2 - lat1
        return sqrt(dx * dx + dy * dy) * 111.2
    }

    companion object {
        private val MARKS = Regex("\\p{Mn}+")

        /** Lower case without accents ("São" to "sao"). Plain ASCII skips the Unicode work: most names are ASCII. */
        fun fold(s: String): String =
            if (s.all { it.code < 128 }) s.lowercase() else Normalizer.normalize(s, Normalizer.Form.NFD).replace(MARKS, "").lowercase()
    }
}
