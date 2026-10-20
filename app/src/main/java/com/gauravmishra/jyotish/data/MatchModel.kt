package com.gauravmishra.jyotish.data

import org.json.JSONObject

/** One of the eight Ashtakoota kootas, with the facts the engine used. */
data class Koota(val key: String, val score: Double, val max: Int, val facts: List<Pair<String, String>>, val note: String?)

data class PoruthamItem(val key: String, val ok: Boolean, val partial: Boolean, val rule: String)

/** Mars counted from the lagna, the Moon and Venus, for one person. */
data class MangalCheck(val name: String, val fromLagna: Int, val fromMoon: Int, val fromVenus: Int) {
    private fun counts(h: Int) = h in MANGAL_HOUSES
    val countedFrom: List<String> get() = buildList {
        if (counts(fromLagna)) add("lagna"); if (counts(fromMoon)) add("moon"); if (counts(fromVenus)) add("venus")
    }
    val counted: Boolean get() = countedFrom.isNotEmpty()

    companion object { val MANGAL_HOUSES = setOf(1, 2, 4, 7, 8, 12) }
}

/** The parts of the engine's match JSON that the Milan screen shows. */
data class MatchModel(
    val total: Double,
    val outOf: Int,
    val rangeLow: Double,
    val rangeHigh: Double,
    val band: String,                 // "below18", "18to24", "25to32", "above32"
    val vashyaTable: String,
    val kootas: List<Koota>,
    val porutham: List<PoruthamItem>,
    val poruthamAgree: Int,
    val poruthamOutOf: Int,
    val essentialAllAgree: Boolean,
    val mangal: List<MangalCheck>,
) {
    companion object {
        val KOOTA_ORDER = listOf("varna", "vashya", "tara", "yoni", "graha_maitri", "gana", "bhakoot", "nadi")

        fun parse(json: String): MatchModel {
            val m = JSONObject(json)
            val ak = m.getJSONObject("ashtakoota")
            val t = ak.getJSONObject("total_36")
            val range = t.optJSONArray("range_across_vashya_tables")
            val ks = ak.getJSONObject("kootas")
            val kootas = KOOTA_ORDER.filter { ks.has(it) }.map { k ->
                val o = ks.getJSONObject(k)
                val facts = o.keys().asSequence()
                    .filter { it !in setOf("max", "score", "note", "score_by_table", "unfavourable_remainders") }
                    .map { it to readable(o.get(it)) }
                    .toList()
                Koota(k, o.getDouble("score"), o.getInt("max"), facts, o.optString("note").takeIf { it.isNotEmpty() })
            }
            val p = ak.getJSONObject("porutham")
            val items = p.getJSONObject("items")
            val porutham = items.keys().asSequence().map { k ->
                val o = items.getJSONObject(k)
                PoruthamItem(k, o.optBoolean("ok"), o.optBoolean("partial"), o.optString("rule"))
            }.toList()
            val essential = p.optJSONObject("essential")
            val mc = m.optJSONObject("mangal_comparison")
            val mangal = mc?.keys()?.asSequence()?.filter { mc.opt(it) is JSONObject }?.map { name ->
                val o = mc.getJSONObject(name)
                MangalCheck(name, o.optInt("from_lagna"), o.optInt("from_moon"), o.optInt("from_venus"))
            }?.toList() ?: emptyList()
            val bandText = t.optString("band")
            return MatchModel(
                total = t.getDouble("score"), outOf = t.optInt("out_of", 36),
                rangeLow = range?.optDouble(0) ?: t.getDouble("score"), rangeHigh = range?.optDouble(1) ?: t.getDouble("score"),
                band = when {
                    bandText.startsWith("under") || bandText.startsWith("below") -> "below18"
                    bandText.startsWith("18") -> "18to24"
                    bandText.startsWith("25") -> "25to32"
                    else -> "above32"
                },
                vashyaTable = t.optString("vashya_table"),
                kootas = kootas,
                porutham = porutham,
                poruthamAgree = p.optInt("agree"), poruthamOutOf = p.optInt("out_of", porutham.size),
                essentialAllAgree = essential != null && essential.keys().asSequence().all { essential.optBoolean(it) },
                mangal = mangal,
            )
        }

        private fun readable(v: Any?): String = when (v) {
            is org.json.JSONArray -> (0 until v.length()).joinToString(", ") { readable(v.get(it)) }
            is Boolean -> if (v) "yes" else "no"
            is Double -> if (v % 1.0 == 0.0) v.toInt().toString() else v.toString()
            null, JSONObject.NULL -> "–"
            else -> v.toString()
        }
    }
}
