package com.gauravmishra.jyotish.data

import org.json.JSONArray
import org.json.JSONObject

/** English and Hindi versions of one piece of text. */
data class Bi(val en: String, val hi: String) {
    fun of(lang: String) = if (lang == "hi") hi else en

    companion object {
        fun parse(o: JSONObject?) = Bi(o?.optString("en").orEmpty(), o?.optString("hi").orEmpty())
    }
}

/** One reason behind a year's tone, already worded in both languages by app_forecast.py. */
data class Driver(val tone: String, val system: String, val from: String, val to: String, val text: Bi, val technical: String)

data class ForecastYear(
    val id: String, val from: String, val to: String,
    /** supportive, demanding, mixed or quiet */
    val lean: String,
    /** strong, moderate or weak: how many of the four systems agree */
    val convergence: String,
    val supportive: Int, val demanding: Int, val active: Int,
    val summary: Bi,
    val drivers: List<Driver>, val more: List<Driver>,
)

data class ForecastWindow(val kind: String, val from: String, val to: String, val baseRate: Double?, val text: Bi, val meaning: Bi)

data class ForecastArea(
    val key: String, val title: Bi, val subtitle: Bi,
    val outlookClass: String, val outlook: Bi, val best: String?, val care: String?,
    val years: List<ForecastYear>, val windows: List<ForecastWindow>,
)

/** The three-year forecast from engine_api.forecast: Marriage, Work, Health and Love & family. */
data class ForecastModel(val from: String, val to: String, val areas: List<ForecastArea>, val method: Bi, val reliability: Bi?) {
    fun area(key: String) = areas.first { it.key == key }

    companion object {
        val AREA_KEYS = listOf("marriage", "work", "health", "family")

        private fun <T> list(a: JSONArray?, f: (JSONObject) -> T): List<T> = (0 until (a?.length() ?: 0)).map { f(a!!.getJSONObject(it)) }

        private fun driver(o: JSONObject) = Driver(
            o.getString("tone"), o.getString("system"), o.getString("from"), o.getString("to"),
            Bi(o.getString("en"), o.getString("hi")), o.optString("technical"),
        )

        fun parse(json: String): ForecastModel {
            val o = JSONObject(json)
            val areas = list(o.getJSONArray("areas")) { a ->
                val ol = a.getJSONObject("outlook")
                ForecastArea(
                    key = a.getString("key"), title = Bi.parse(a.getJSONObject("title")), subtitle = Bi.parse(a.getJSONObject("subtitle")),
                    outlookClass = ol.getString("class"), outlook = Bi(ol.getString("en"), ol.getString("hi")),
                    best = ol.optString("best").takeIf { it.isNotEmpty() && it != "null" },
                    care = ol.optString("care").takeIf { it.isNotEmpty() && it != "null" },
                    years = list(a.getJSONArray("years")) { y ->
                        ForecastYear(
                            y.getString("id"), y.getString("from"), y.getString("to"), y.getString("lean"), y.getString("convergence"),
                            y.getInt("supportive"), y.getInt("demanding"), y.getInt("active"), Bi.parse(y.getJSONObject("summary")),
                            list(y.optJSONArray("drivers"), ::driver), list(y.optJSONArray("more"), ::driver),
                        )
                    },
                    windows = list(a.optJSONArray("windows")) { w ->
                        ForecastWindow(
                            w.getString("kind"), w.getString("from"), w.getString("to"),
                            if (w.isNull("base_rate")) null else w.getDouble("base_rate"),
                            Bi(w.getString("en"), w.getString("hi")), Bi.parse(w.getJSONObject("meaning")),
                        )
                    },
                )
            }
            val win = o.getJSONObject("window")
            return ForecastModel(win.getString("from"), win.getString("to"), areas, Bi.parse(o.getJSONObject("method")),
                o.optJSONObject("reliability")?.let { Bi.parse(it) })
        }
    }
}
