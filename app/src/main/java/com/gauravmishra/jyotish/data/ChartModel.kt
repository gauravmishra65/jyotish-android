package com.gauravmishra.jyotish.data

import org.json.JSONObject

val SIGNS = listOf("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")

data class Planet(
    val name: String, val lon: Double, val sign: String, val signIndex: Int, val dms: String, val house: Int,
    val nakshatra: String, val pada: Int, val nakshatraLord: String, val signLord: String, val dignity: String,
    val retrograde: Boolean, val combust: Boolean, val vargottama: Boolean, val dailyMotion: Double,
)

data class Lagna(val sign: String, val signIndex: Int, val dms: String, val nakshatra: String, val pada: Int, val signLord: String)

data class Period(val lord: String, val start: String, val end: String)

data class Mahadasha(val lord: String, val start: String, val end: String, val antardashas: List<Period>)

data class Yoga(
    val id: String, val name: String, val category: String, val source: String, val rule: String,
    val strength: String?, val strengthScore: Double?, val tone: String, val baseRate: Double?,
    val keyPlanets: List<String>, val note: String?,
)

data class Strength(val planet: String, val rupas: Double, val required: Double, val ratio: Double)

/** The parts of the engine's chart JSON that the Kundali screen shows. */
data class ChartModel(
    val lagna: Lagna,
    val planets: List<Planet>,
    val mahadashas: List<Mahadasha>,
    val currentMaha: String,
    val currentAntar: Period,
    val yogas: List<Yoga>,
    val strengths: List<Strength>,
    val savBySign: Map<String, Int>,
    val ayanamsa: String,
    val warnings: List<String>,
) {
    /** Planets in each house, counted from the lagna (whole-sign houses, as the engine uses). */
    fun planetsInHouse(h: Int): List<Planet> = planets.filter { it.house == h }

    /** Sign index (0 = Aries) of house h. */
    fun signOfHouse(h: Int): Int = (lagna.signIndex + h - 1) % 12

    companion object {
        fun parse(json: String): ChartModel {
            val c = JSONObject(json)
            val v = c.getJSONObject("vedic")
            val l = v.getJSONObject("lagna")
            val lagnaSign = l.getString("sign")
            val pl = v.getJSONObject("planets")
            val planets = pl.keys().asSequence().map { name ->
                val p = pl.getJSONObject(name)
                Planet(
                    name, p.getDouble("lon"), p.getString("sign"), p.getInt("sign_index"), p.getString("dms"), p.getInt("house"),
                    p.getString("nakshatra"), p.getInt("pada"), p.optString("nakshatra_lord"), p.optString("sign_lord"),
                    p.optString("dignity"), p.optBoolean("retrograde"), p.optBoolean("combust"), p.optBoolean("vargottama"),
                    p.optDouble("daily_motion", 0.0),
                )
            }.toList()
            val vim = v.getJSONObject("dashas").getJSONObject("vimshottari")
            val mds = vim.getJSONArray("mahadashas")
            val mahadashas = (0 until mds.length()).map { i ->
                val m = mds.getJSONObject(i)
                val a = m.optJSONArray("antardashas")
                Mahadasha(m.getString("lord"), m.getString("start"), m.getString("end"),
                    (0 until (a?.length() ?: 0)).map { j -> a!!.getJSONObject(j).let { Period(it.getString("lord"), it.getString("start"), it.getString("end")) } })
            }
            val cur = vim.getJSONObject("current")
            val antar = cur.getJSONObject("antardasha")
            val yl = v.optJSONObject("yoga_library")
            val found = yl?.optJSONArray("found")
            val yogas = (0 until (found?.length() ?: 0)).map { found!!.getJSONObject(it) }
                .filter { it.optBoolean("report", true) && it.optString("status", "present") == "present" }
                .map { y ->
                    val kp = y.optJSONArray("key_planets")
                    Yoga(
                        y.getString("id"), y.getString("name"), y.optString("category"), y.optString("source"), y.optString("rule"),
                        y.optString("strength").takeIf { it.isNotEmpty() && it != "null" },
                        if (y.isNull("strength_score")) null else y.optDouble("strength_score"),
                        y.optString("tone", "mixed"),
                        if (y.isNull("base_rate_present")) null else y.optDouble("base_rate_present"),
                        (0 until (kp?.length() ?: 0)).map { kp!!.getString(it) },
                        y.optString("note").takeIf { it.isNotEmpty() && it != "null" },
                    )
                }
                .sortedWith(compareBy({ it.baseRate ?: 1.0 }, { it.name }))   // rarer yogas first: they say more about a person
            val sb = v.optJSONObject("shadbala")?.optJSONObject("bphs")?.optJSONObject("planets")
            val strengths = sb?.keys()?.asSequence()?.map { k ->
                val s = sb.getJSONObject(k)
                Strength(k, s.getDouble("rupas"), s.getDouble("required_rupas"), s.getDouble("ratio"))
            }?.toList() ?: emptyList()
            val sav = v.optJSONObject("ashtakavarga")?.optJSONObject("sarva")
            val savBySign = sav?.keys()?.asSequence()?.associate { it to sav.getInt(it) } ?: emptyMap()
            val w = c.optJSONObject("audit")?.optJSONArray("warnings")
            return ChartModel(
                lagna = Lagna(lagnaSign, SIGNS.indexOf(lagnaSign), l.getString("dms"), l.getString("nakshatra"), l.getInt("pada"), l.optString("sign_lord")),
                planets = planets,
                mahadashas = mahadashas,
                currentMaha = cur.getJSONObject("mahadasha").getString("lord"),
                currentAntar = Period(antar.getString("lord"), antar.getString("start"), antar.getString("end")),
                yogas = yogas,
                strengths = strengths,
                savBySign = savBySign,
                ayanamsa = v.optJSONObject("conventions")?.optString("ayanamsa")?.takeIf { it.isNotEmpty() }
                    ?: c.optJSONObject("meta")?.optString("ayanamsa") ?: "",
                warnings = (0 until (w?.length() ?: 0)).map { w!!.getString(it) },
            )
        }
    }
}

/** Short planet labels used inside the chart drawing. */
object Abbrev {
    private val en = mapOf("Sun" to "Su", "Moon" to "Mo", "Mars" to "Ma", "Mercury" to "Me", "Jupiter" to "Ju",
        "Venus" to "Ve", "Saturn" to "Sa", "Rahu" to "Ra", "Ketu" to "Ke")
    private val hi = mapOf("Sun" to "सू", "Moon" to "चं", "Mars" to "मं", "Mercury" to "बु", "Jupiter" to "गु",
        "Venus" to "शु", "Saturn" to "श", "Rahu" to "रा", "Ketu" to "के")

    fun of(p: Planet, lang: String): String {
        val base = (if (lang == "hi") hi else en)[p.name] ?: p.name.take(2)
        // Rahu and Ketu always move backwards, so only the true planets are marked.
        return if (p.retrograde && p.name != "Rahu" && p.name != "Ketu") base + (if (lang == "hi") "(व)" else "(R)") else base
    }
}
