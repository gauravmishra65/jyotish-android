package com.gauravmishra.jyotish.data

import org.json.JSONArray
import org.json.JSONObject

/** One acceptable time window from the engine's muhurta search. Fields ending in Hi are the Hindi forms. */
data class MuhurtaWindow(
    val date: String, val start: String, val end: String, val minutes: Int, val score: Int,
    val weekday: String, val tithi: Int, val paksha: String, val nakshatra: String, val lagna: String,
    val supports: List<String>, val cautions: List<String>,
    val weekdayHi: String?, val nakshatraHi: String?, val lagnaHi: String?,
    val supportsHi: List<String>?, val cautionsHi: List<String>?,
) {
    /** Tithi counted within its paksha (1 to 15), as panchangs print it. */
    val tithiInPaksha: Int get() = if (tithi > 15) tithi - 15 else tithi
}

data class MuhurtaResult(
    val event: String,
    val windows: List<MuhurtaWindow>,
    val windowsFound: Int,
    val people: List<String>,
    val disclaimer: String,
    val rejectedHours: List<Pair<String, Int>>,
) {
    /** Days that have at least one window, each with its windows strongest first. */
    val byDay: List<Pair<String, List<MuhurtaWindow>>>
        get() = windows.groupBy { it.date }.toSortedMap().map { (d, ws) -> d to ws.sortedByDescending { it.score } }

    /** The strongest windows overall (ties go to the earlier date). */
    fun best(n: Int): List<MuhurtaWindow> = windows.sortedWith(compareBy({ -it.score }, { it.start })).take(n)

    companion object {
        private fun strings(a: JSONArray?) = (0 until (a?.length() ?: 0)).map { a!!.getString(it) }

        fun parse(json: String): MuhurtaResult {
            val o = JSONObject(json)
            val all = o.getJSONArray("all_windows")
            val windows = (0 until all.length()).map { i ->
                val w = all.getJSONObject(i)
                MuhurtaWindow(
                    date = w.optString("date", w.getString("start_local").take(10)),
                    start = w.getString("start_local"), end = w.getString("end_local"), minutes = w.optInt("minutes"), score = w.optInt("score"),
                    weekday = w.getString("weekday"), tithi = w.getInt("tithi"), paksha = w.optString("paksha"),
                    nakshatra = w.getString("nakshatra"), lagna = w.getString("lagna"),
                    supports = strings(w.optJSONArray("supports")), cautions = strings(w.optJSONArray("weaknesses")),
                    weekdayHi = w.optString("weekday_hi").ifEmpty { null }, nakshatraHi = w.optString("nakshatra_hi").ifEmpty { null },
                    lagnaHi = w.optString("lagna_hi").ifEmpty { null },
                    supportsHi = w.optJSONArray("supports_hi")?.let { strings(it) }, cautionsHi = w.optJSONArray("weaknesses_hi")?.let { strings(it) },
                )
            }
            val rej = o.optJSONObject("time_rejected_minutes_by_reason")
            return MuhurtaResult(
                event = o.getString("event"),
                windows = windows,
                windowsFound = o.optInt("windows_found", windows.size),
                people = strings(o.optJSONArray("people")),
                disclaimer = o.optString("disclaimer"),
                rejectedHours = rej?.keys()?.asSequence()?.map { it to rej.getInt(it) / 60 }?.toList() ?: emptyList(),
            )
        }
    }
}
