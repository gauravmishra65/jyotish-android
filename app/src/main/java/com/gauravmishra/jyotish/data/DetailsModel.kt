package com.gauravmishra.jyotish.data

import org.json.JSONArray
import org.json.JSONObject

/** One block of a details section: a table, a paragraph or a list (see app_details.py). */
sealed interface DetailBlock {
    data class Table(val head: List<Bi>, val rows: List<List<Bi>>) : DetailBlock
    data class Para(val text: Bi) : DetailBlock
    data class Items(val items: List<Bi>) : DetailBlock
}

data class DetailSection(val key: String, val title: Bi, val intro: Bi?, val blocks: List<DetailBlock>, val note: Bi?)

/** The chart's "details" (app_details.build): extra sections for the Kundali screen's More tab, and D9/D10 sign maps. */
/** A divisional chart's name and what it is read for. */
data class VargaMeta(val key: String, val name: Bi, val use: Bi)

data class DetailsModel(val sections: List<DetailSection>, val vargas: Map<String, Map<String, String>>, val vargaMeta: List<VargaMeta> = emptyList()) {
    companion object {

        /** Null when the chart was computed before the details existed (an old cache entry). */
        fun parse(chartJson: String): DetailsModel? {
            val d = JSONObject(chartJson).optJSONObject("details") ?: return null
            val sections = parseSections(d.optJSONArray("sections"))
            val v = d.optJSONObject("vargas") ?: JSONObject()
            val vargas = v.keys().asSequence().associateWith { k ->
                val m = v.getJSONObject(k)
                m.keys().asSequence().associateWith { m.getString(it) }
            }
            val vm = d.optJSONArray("varga_meta") ?: JSONArray()
            val meta = (0 until vm.length()).map { vm.getJSONObject(it) }
                .map { VargaMeta(it.getString("key"), Bi.parse(it.getJSONObject("name")), Bi.parse(it.getJSONObject("use"))) }
            return DetailsModel(sections, vargas, meta)
        }
    }
}

private fun biOf(o: JSONObject?) = o?.let { Bi(it.optString("en"), it.optString("hi")) }
private fun bisOf(a: JSONArray?) = (0 until (a?.length() ?: 0)).map { Bi.parse(a!!.getJSONObject(it)) }

/** A list of bilingual sections (app_details.py's format): used by the Kundali details and by Milan's Western side. */
fun parseSections(secs: JSONArray?): List<DetailSection> = (0 until (secs?.length() ?: 0)).map { i ->
    val s = secs!!.getJSONObject(i)
    val blocks = s.optJSONArray("blocks") ?: JSONArray()
    DetailSection(
        s.getString("key"), Bi.parse(s.getJSONObject("title")), biOf(s.optJSONObject("intro")),
        (0 until blocks.length()).mapNotNull { j ->
            val b = blocks.getJSONObject(j)
            when (b.optString("type")) {
                "table" -> {
                    val rows = b.getJSONArray("rows")
                    DetailBlock.Table(bisOf(b.getJSONArray("head")), (0 until rows.length()).map { bisOf(rows.getJSONArray(it)) })
                }
                "para" -> DetailBlock.Para(Bi.parse(b.getJSONObject("text")))
                "list" -> DetailBlock.Items(bisOf(b.getJSONArray("items")))
                else -> null
            }
        },
        biOf(s.optJSONObject("note"))?.takeIf { it.en.isNotBlank() },
    )
}

/** The same chart with every planet and the lagna moved to its sign in a divisional chart (whole-sign houses). */
fun ChartModel.varga(signs: Map<String, String>): ChartModel {
    val lagSign = signs["Lagna"] ?: return this
    val li = SIGNS.indexOf(lagSign)
    return copy(
        lagna = lagna.copy(sign = lagSign, signIndex = li, dms = ""),
        planets = planets.map { p ->
            val s = signs[p.name] ?: p.sign
            val si = SIGNS.indexOf(s)
            p.copy(sign = s, signIndex = si, house = (si - li + 12) % 12 + 1, combust = false, vargottama = false)
        },
    )
}
