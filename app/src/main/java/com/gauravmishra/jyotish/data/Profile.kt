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
    /** Where the person lives now, if different from the birthplace (optional). Used for transits and the report. */
    val residence: String = "",
    val resLat: Double? = null,
    val resLon: Double? = null,
    /** Group on the Saved Kundlis screen: family, friends, clients or other ("" = not set). */
    val group: String = "",
    /** The user's own notes about this person (v20), kept apart from anything computed. */
    val notes: String = "",
    /** Dated life events "YYYY-MM-DD:kind" (marriage, child, job, property, abroad, education), for the Birth time check. */
    val events: List<String> = emptyList(),
    /** Where the birth time came from (v24): certificate, hospital, family, horoscope, rectified or "" (not said). */
    val timeSource: String = "",
    /** "person" or "event" (v25): an event has no gender and its chart is read for the moment, not for a life. */
    val kind: String = "person",
    /** The name this person uses now, when it differs from the birth name; used by the numerology section. */
    val nameInUse: String = "",
    /** Earliest and latest the birth could have been, "HH:MM" each, when the time is uncertain. */
    val timeFrom: String = "",
    val timeTo: String = "",
    /** Which occurrence of a local time that happened twice (clocks went back): 0 = the first, 1 = the second. */
    val fold: Int = 0,
    /** The calendar the date was recorded in: "gregorian" or "julian". */
    val calendar: String = "gregorian",
    /** A UTC offset in hours typed by the user, when the time zone database should not be trusted for this record. */
    val utcOffset: Double? = null,
) {
    fun toJson(): JSONObject = JSONObject()
        .put("id", id).put("name", name).put("gender", gender).put("date", date).put("time", time)
        .put("confidence", confidence).put("place", place).put("lat", lat).put("lon", lon).put("tz", tz)
        .put("residence", residence).put("res_lat", resLat ?: JSONObject.NULL).put("res_lon", resLon ?: JSONObject.NULL)
        .put("group", group).put("notes", notes).put("events", JSONArray(events)).put("time_source", timeSource)
        .put("kind", kind).put("name_in_use", nameInUse).put("time_from", timeFrom).put("time_to", timeTo)
        .put("fold", fold).put("calendar", calendar).put("utc_offset", utcOffset ?: JSONObject.NULL)

    val hasResidence: Boolean get() = residence.isNotBlank() && resLat != null && resLon != null

    /** Request for engine_api.chart. Only the modules the v1 screens use are computed. */
    fun chartRequest(now: String, ayanamsa: String, node: String): JSONObject = JSONObject()
        .put("name", name).put("date", date).put("time", time).put("lat", lat).put("lon", lon).put("tz", tz)
        .put("gender", gender).put("time_confidence", confidence).put("place", place).put("now", now)
        .put("ayanamsa", ayanamsa).put("node", node)
        .put("dasha_year", ChartPrefs.dashaYear.toDouble()).put("zi", ChartPrefs.zi).put("bazi_time", ChartPrefs.baziTime)
        .put("time_source", timeSource).put("kind", kind).put("fold", fold).put("calendar", calendar)
        .put("house_system", ChartPrefs.houseSystem).put("orb_scale", ChartPrefs.orbScale)
        .apply { if (nameInUse.isNotBlank()) put("name_in_use", nameInUse); if (utcOffset != null) put("utc_offset", utcOffset) }
        .put("v", 13)   // bump when the chart's contents change, so cached charts are recomputed (2: details for the More tab; 3: doshas, extra dashas, all 16 vargas; 4: avasthas, upagrahas, more sign dashas, Western extras; 5: ayanamsa table, Tithi Pravesha; 6: Western depth, BaZi)
        .apply { if (hasResidence) put("residence", residence).put("current_lat", resLat).put("current_lon", resLon) }

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
            residence = o.optString("residence", ""),
            resLat = if (o.has("res_lat") && !o.isNull("res_lat")) o.getDouble("res_lat") else null,
            resLon = if (o.has("res_lon") && !o.isNull("res_lon")) o.getDouble("res_lon") else null,
            group = o.optString("group", ""),
            notes = o.optString("notes", ""),
            events = o.optJSONArray("events")?.let { a -> (0 until a.length()).map { a.getString(it) } } ?: emptyList(),
            timeSource = o.optString("time_source", ""),
            kind = o.optString("kind", "person"), nameInUse = o.optString("name_in_use", ""),
            timeFrom = o.optString("time_from", ""), timeTo = o.optString("time_to", ""),
            fold = o.optInt("fold", 0), calendar = o.optString("calendar", "gregorian"),
            utcOffset = if (o.has("utc_offset") && !o.isNull("utc_offset")) o.getDouble("utc_offset") else null,
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

/** The same person entered twice: same birth date and time within a minute, and the same place to about a kilometre. */
fun List<Profile>.duplicateOf(p: Profile): Profile? = firstOrNull { o ->
    o.id != p.id && o.date == p.date && o.time == p.time &&
        kotlin.math.abs(o.lat - p.lat) < 0.01 && kotlin.math.abs(o.lon - p.lon) < 0.01
}

/**
 * People read from a CSV written by this app (or any file with the same first columns). Rows that cannot be read are
 * skipped and counted, so the screen can say what came in and what did not before anything is saved.
 */
fun parsePeopleCsv(text: String): Pair<List<Profile>, Int> {
    fun cells(line: String): List<String> {
        val out = ArrayList<String>(); val sb = StringBuilder(); var q = false; var i = 0
        while (i < line.length) {
            val c = line[i]
            when {
                c == '"' && q && i + 1 < line.length && line[i + 1] == '"' -> { sb.append('"'); i++ }
                c == '"' -> q = !q
                c == ',' && !q -> { out.add(sb.toString()); sb.setLength(0) }
                else -> sb.append(c)
            }
            i++
        }
        out.add(sb.toString()); return out
    }
    val lines = text.removePrefix("\uFEFF").split("\r\n", "\n").filter { it.isNotBlank() }
    if (lines.isEmpty()) return emptyList<Profile>() to 0
    val head = cells(lines[0]).map { it.trim().lowercase() }
    fun idx(vararg names: String) = names.firstNotNullOfOrNull { n -> head.indexOf(n).takeIf { it >= 0 } } ?: -1
    val iName = idx("name"); val iDate = idx("birth date", "date"); val iTime = idx("birth time", "time")
    val iLat = idx("latitude", "lat"); val iLon = idx("longitude", "lon"); val iTz = idx("time zone", "tz")
    if (iName < 0 || iDate < 0 || iTime < 0 || iLat < 0 || iLon < 0 || iTz < 0) return emptyList<Profile>() to (lines.size - 1)
    val iGender = idx("gender"); val iConf = idx("time confidence"); val iPlace = idx("birthplace", "place")
    val iRes = idx("lives in", "residence"); val iGroup = idx("group"); val iNotes = idx("notes"); val iSrc = idx("time source")
    var bad = 0
    val people = ArrayList<Profile>()
    for (line in lines.drop(1)) {
        val c = cells(line)
        fun at(i: Int) = if (i >= 0 && i < c.size) c[i].trim() else ""
        val lat = at(iLat).toDoubleOrNull(); val lon = at(iLon).toDoubleOrNull()
        val date = at(iDate); val time = at(iTime)
        if (at(iName).isBlank() || lat == null || lon == null || at(iTz).isBlank() ||
            !Regex("""\d{4}-\d{2}-\d{2}""").matches(date) || !Regex("""\d{2}:\d{2}""").matches(time)) { bad++; continue }
        people.add(Profile(
            name = at(iName), gender = at(iGender).ifBlank { "M" }.take(1).uppercase(), date = date, time = time,
            confidence = at(iConf).lowercase().ifBlank { "reliable" }.let { v ->
                if (v in listOf("certificate", "reliable", "approximate", "unknown")) v else "reliable"
            },
            place = at(iPlace), lat = lat, lon = lon, tz = at(iTz), residence = at(iRes), group = at(iGroup),
            notes = at(iNotes), timeSource = at(iSrc).lowercase().takeIf { it in listOf("certificate", "hospital", "family", "horoscope", "rectified") } ?: "",
        ))
    }
    return people to bad
}
