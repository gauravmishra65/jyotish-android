package com.gauravmishra.jyotish.data

import org.json.JSONArray
import org.json.JSONObject

/** A span of time on the Today screen: local "HH:MM" strings for display, ISO for finding the one running now. */
data class TimeSpan(val from: String, val to: String, val fromIso: String, val toIso: String) {
    fun contains(nowIso: String): Boolean = fromIso <= nowIso && nowIso < toIso
}

data class Element(val name: Bi, val ends: String?)
data class Choghadiya(val name: Bi, val kind: String, val span: TimeSpan)
data class Hora(val lord: Bi, val night: Boolean, val span: TimeSpan)
data class Festival(val key: String, val date: String, val name: Bi, val monthly: Boolean, val time: String?)
data class Transit(val key: String, val planet: Bi, val sign: Bi, val deg: Double, val retrograde: Boolean, val fromLagna: Int, val fromMoon: Int)

data class PersonDay(
    val name: String, val guidance: Bi,
    val tara: Bi, val taraNumber: Int, val taraOk: Boolean, val taraChanges: String?,
    val chandraHouse: Int, val chandraOk: Boolean,
    val moonSign: Bi, val moonFromLagna: Int,
    val saturnFromMoon: Int, val saturnPhase: Bi?,
    val transits: List<Transit>,
)

/** The engine's "today" result (app_today.py) for one place and date, with the person's day when one was asked for. */
data class TodayModel(
    val date: String, val place: String, val tz: String, val utcOffset: String,
    val sunrise: String?, val sunset: String?, val moonrise: String?, val moonset: String?,
    val weekday: Bi, val tithi: Element, val paksha: Bi, val nakshatra: Element, val yoga: Element, val karana: Element,
    val moonSign: Bi, val sunSign: Bi, val monthAmanta: Bi, val monthPurnimanta: Bi, val vikram: Int, val shaka: Int,
    val periods: Map<String, TimeSpan>, val abhijitWednesday: Boolean,
    val choghadiyaDay: List<Choghadiya>, val choghadiyaNight: List<Choghadiya>, val hora: List<Hora>,
    val festivals: List<Festival>, val conventions: Bi, val person: PersonDay?, val periodsNote: String?,
) {
    companion object {
        private fun span(o: JSONObject) = TimeSpan(o.optString("from"), o.optString("to"), o.optString("from_iso"), o.optString("to_iso"))
        private fun el(o: JSONObject) = Element(Bi.parse(o.getJSONObject("name")), o.optString("ends").takeIf { it.isNotEmpty() && it != "null" })
        private fun str(o: JSONObject?, k: String) = o?.optString(k)?.takeIf { it.isNotEmpty() && it != "null" }
        private fun objs(a: JSONArray?) = (0 until (a?.length() ?: 0)).map { a!!.getJSONObject(it) }

        fun parse(json: String): TodayModel {
            val o = JSONObject(json)
            val p = o.getJSONObject("panchang")
            val pr = o.getJSONObject("periods")
            val periods = listOf("rahu_kalam", "yamaganda", "gulika_kalam", "abhijit", "brahma_muhurta")
                .mapNotNull { k -> pr.optJSONObject(k)?.let { k to span(it) } }.toMap()
            val person = o.optJSONObject("person")?.let { q ->
                val t = q.getJSONObject("tarabala")
                val c = q.getJSONObject("chandrabala")
                val m = q.getJSONObject("moon_transit")
                val s = q.getJSONObject("saturn")
                PersonDay(
                    q.optString("name"), Bi.parse(q.getJSONObject("guidance")),
                    Bi.parse(t.getJSONObject("tara")), t.getInt("number"), t.getBoolean("ok"), str(t, "changes"),
                    c.getInt("house"), c.getBoolean("ok"),
                    Bi.parse(m.getJSONObject("sign")), m.getInt("house_from_lagna"),
                    s.getInt("house_from_moon"), s.optJSONObject("phase")?.let { Bi.parse(it) },
                    objs(q.optJSONArray("transits")).map {
                        Transit(it.getString("key"), Bi.parse(it.getJSONObject("planet")), Bi.parse(it.getJSONObject("sign")),
                            it.getDouble("deg"), it.optBoolean("retrograde"), it.getInt("house_from_lagna"), it.getInt("house_from_moon"))
                    },
                )
            }
            return TodayModel(
                o.getString("date"), o.optString("place"), o.optString("tz"), o.optString("utc_offset"),
                str(o.optJSONObject("sun"), "rise"), str(o.optJSONObject("sun"), "set"),
                str(o.optJSONObject("moon"), "rise"), str(o.optJSONObject("moon"), "set"),
                Bi.parse(p.getJSONObject("weekday")), el(p.getJSONObject("tithi")), Bi.parse(p.getJSONObject("tithi").getJSONObject("paksha")),
                el(p.getJSONObject("nakshatra")), el(p.getJSONObject("yoga")), el(p.getJSONObject("karana")),
                Bi.parse(p.getJSONObject("moon_sign")), Bi.parse(p.getJSONObject("sun_sign")),
                Bi.parse(p.getJSONObject("month_amanta")), Bi.parse(p.getJSONObject("month_purnimanta")),
                p.optInt("vikram_samvat"), p.optInt("shaka_samvat"),
                periods, pr.optJSONObject("abhijit")?.optBoolean("wednesday") ?: false,
                objs(pr.optJSONArray("choghadiya_day")).map { Choghadiya(Bi.parse(it.getJSONObject("name")), it.optString("kind"), span(it)) },
                objs(pr.optJSONArray("choghadiya_night")).map { Choghadiya(Bi.parse(it.getJSONObject("name")), it.optString("kind"), span(it)) },
                objs(pr.optJSONArray("hora")).map { Hora(Bi.parse(it.getJSONObject("lord")), it.optBoolean("night"), span(it)) },
                objs(o.optJSONArray("festivals")).map {
                    Festival(it.getString("key"), it.getString("date"), Bi.parse(it.getJSONObject("name")), it.optBoolean("monthly"), str(it, "time"))
                },
                Bi.parse(o.optJSONObject("conventions")), person, str(pr, "status"),
            )
        }
    }
}
