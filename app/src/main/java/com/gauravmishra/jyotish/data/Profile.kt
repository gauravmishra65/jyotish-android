package com.gauravmishra.jyotish.data

import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.util.UUID

/** One saved birth chart. Dates are YYYY-MM-DD and times HH:MM, local civil time at the birthplace. */
data class Profile(
    val id: String = UUID.randomUUID().toString(),
    val name: String,
    val gender: String,            // "M" or "F"
    val date: String,
    val time: String,
    val confidence: String,        // certificate, reliable, approximate, unknown
    val place: String,
    val lat: Double,
    val lon: Double,
    val tz: String,
) {
    fun toJson(): JSONObject = JSONObject()
        .put("id", id).put("name", name).put("gender", gender).put("date", date).put("time", time)
        .put("confidence", confidence).put("place", place).put("lat", lat).put("lon", lon).put("tz", tz)

    /** Request for engine_api.chart. Only the modules the v1 screens use are computed. */
    fun chartRequest(now: String, ayanamsa: String, node: String): JSONObject = JSONObject()
        .put("name", name).put("date", date).put("time", time).put("lat", lat).put("lon", lon).put("tz", tz)
        .put("gender", gender).put("time_confidence", confidence).put("place", place).put("now", now)
        .put("ayanamsa", ayanamsa).put("node", node)

    val initials: String
        get() = name.trim().split(Regex("\\s+")).filter { it.isNotEmpty() }.let { w ->
            when {
                w.isEmpty() -> "?"
                w.size == 1 -> w[0].take(1)
                else -> w.first().take(1) + w.last().take(1)
            }
        }.uppercase()

    companion object {
        fun fromJson(o: JSONObject) = Profile(
            id = o.getString("id"), name = o.getString("name"), gender = o.optString("gender", "M"),
            date = o.getString("date"), time = o.getString("time"), confidence = o.optString("confidence", "reliable"),
            place = o.optString("place", ""), lat = o.getDouble("lat"), lon = o.getDouble("lon"), tz = o.getString("tz"),
        )
    }
}

/**
 * Profiles kept in one JSON file in the app's private storage; computed charts are cached beside it.
 * Writes go to a temporary file first and are then renamed, so a crash never leaves a half-written file.
 */
class ProfileStore(private val dir: File) {
    private val file = File(dir, "profiles.json")
    private val chartDir = File(dir, "charts")

    fun load(): List<Profile> {
        if (!file.exists()) return emptyList()
        return try {
            val arr = JSONArray(file.readText())
            (0 until arr.length()).map { Profile.fromJson(arr.getJSONObject(it)) }
        } catch (e: Exception) {
            emptyList()
        }
    }

    fun save(profiles: List<Profile>) {
        dir.mkdirs()
        writeAtomic(file, JSONArray(profiles.map { it.toJson() }).toString(1))
    }

    /** The cached chart, if it was computed for this exact request. */
    fun cachedChart(id: String, requestKey: String): String? {
        val f = File(chartDir, "$id.json")
        if (!f.exists()) return null
        return try {
            val o = JSONObject(f.readText())
            if (o.optString("key") == requestKey) o.getString("chart") else null
        } catch (e: Exception) {
            null
        }
    }

    fun cacheChart(id: String, requestKey: String, chart: String) {
        chartDir.mkdirs()
        writeAtomic(File(chartDir, "$id.json"), JSONObject().put("key", requestKey).put("chart", chart).toString())
    }

    fun deleteChart(id: String) {
        File(chartDir, "$id.json").delete()
        File(chartDir, "$id.forecast.json").delete()
        File(chartDir, "$id.report.en.json").delete()
        File(chartDir, "$id.report.hi.json").delete()
    }

    private fun writeAtomic(target: File, text: String) {
        val tmp = File(target.parentFile, target.name + ".tmp")
        tmp.writeText(text)
        if (!tmp.renameTo(target)) {
            target.delete()
            tmp.renameTo(target)
        }
    }
}
