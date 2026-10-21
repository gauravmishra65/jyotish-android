package com.gauravmishra.jyotish.data

import org.json.JSONArray
import org.json.JSONObject

/** The numerology block of a chart, in the shape the Numerology screen shows. */
data class NumerologyModel(
    val mulank: Int, val mulankPlanet: String,
    val bhagyank: Int, val bhagyankPlanet: String,
    val chaldeanCompound: Int, val chaldeanRoot: Int,
    val lifePath: Int, val lifePathAlt: Int?,
    val destiny: Int, val soulUrge: Int, val personality: Int, val maturity: Int, val birthday: Int,
    val personalYear: Int, val personalMonth: Int,
    val karmicDebt: List<Int>, val karmicLessons: List<Int>, val hiddenPassion: List<Int>,
    /** Loshu grid cells in layout order (4 9 2 / 3 5 7 / 8 1 6): the cell's number and the digits found, "" if missing. */
    val loshu: List<Pair<Int, String>>,
    val missing: List<Int>,
    val planes: List<Pair<String, String>>,      // e.g. "mental (4-9-2)" to "complete"
    val kua: Int?, val kuaGroup: String?,
    val kuaGood: List<Pair<String, String>>, val kuaBad: List<Pair<String, String>>,
) {
    companion object {
        val LOSHU_LAYOUT = listOf(4, 9, 2, 3, 5, 7, 8, 1, 6)

        private fun ints(a: JSONArray?) = (0 until (a?.length() ?: 0)).map { a!!.getInt(it) }
        private fun pairs(o: JSONObject?) = o?.keys()?.asSequence()?.map { it to o.getString(it) }?.toList() ?: emptyList()

        fun parse(chartJson: String): NumerologyModel {
            val n = JSONObject(chartJson).getJSONObject("numerology")
            val py = n.getJSONObject("pythagorean")
            val ind = n.getJSONObject("indian")
            val grid = ind.getJSONArray("loshu_grid")
            val cells = (0 until 3).flatMap { r -> (0 until 3).map { c -> grid.getJSONArray(r).getString(c) } }
            val kd = py.optJSONObject("karmic_debt")
            val kua = n.optJSONObject("kua")
            val lp = n.getJSONObject("life_path")
            return NumerologyModel(
                mulank = ind.getInt("mulank_driver"), mulankPlanet = ind.getString("mulank_planet"),
                bhagyank = ind.getInt("bhagyank_conductor"), bhagyankPlanet = ind.getString("bhagyank_planet"),
                chaldeanCompound = n.getJSONObject("chaldean").getInt("compound_number"),
                chaldeanRoot = n.getJSONObject("chaldean").getInt("single_digit"),
                lifePath = lp.getInt("value"),
                lifePathAlt = lp.optInt("alternate_method_value", -1).takeIf { it >= 0 && it != lp.getInt("value") },
                destiny = py.getInt("destiny_expression"), soulUrge = py.getInt("soul_urge"), personality = py.getInt("personality"),
                maturity = py.optInt("maturity_number"), birthday = n.getJSONObject("birthday_number").getInt("value"),
                personalYear = n.getJSONObject("personal_cycles").getInt("personal_year"),
                personalMonth = n.getJSONObject("personal_cycles").getInt("personal_month"),
                karmicDebt = kd?.keys()?.asSequence()?.map { kd.getInt(it) }?.distinct()?.sorted()?.toList() ?: emptyList(),
                karmicLessons = ints(py.optJSONArray("karmic_lessons")),
                hiddenPassion = ints(py.optJSONArray("hidden_passion")),
                loshu = LOSHU_LAYOUT.mapIndexed { i, num -> num to cells[i].let { if (it == "-") "" else it } },
                missing = ints(ind.optJSONArray("missing_numbers")),
                planes = pairs(ind.optJSONObject("planes")),
                kua = kua?.optInt("value"), kuaGroup = kua?.optString("group"),
                kuaGood = pairs(kua?.optJSONObject("favourable")), kuaBad = pairs(kua?.optJSONObject("unfavourable")),
            )
        }
    }
}

data class NameOption(val spelling: String, val compound: Int, val root: Int, val cls: String, val fitMulank: String, val fitBhagyank: String, val changes: List<String>)

/** Name spelling options from engine_api.names (the skill's name_correction module). */
data class NameOptions(val original: NameOption, val alreadyFits: Boolean, val options: List<NameOption>, val disclaimer: String) {
    companion object {
        private fun opt(o: JSONObject, spelling: String? = null) = NameOption(
            spelling ?: o.getString("spelling"), o.getInt("chaldean_compound"), o.getInt("chaldean_root"), o.getString("compound_class"),
            o.getString("fit_with_mulank"), o.getString("fit_with_bhagyank"),
            o.optJSONArray("changes")?.let { a -> (0 until a.length()).map { a.getString(it) } } ?: emptyList(),
        )

        fun parse(json: String): NameOptions {
            val o = JSONObject(json)
            val s = o.getJSONArray("suggestions")
            return NameOptions(
                original = opt(o.getJSONObject("original"), o.getString("name")),
                alreadyFits = o.optBoolean("original_already_fits") || o.optInt("suggestions_better_than_original") == 0,
                options = (0 until s.length()).map { opt(s.getJSONObject(it)) },
                disclaimer = o.optString("disclaimer"),
            )
        }

        /** Hindi for a change description ("double V", "a to aa"), matching the skill's report. */
        fun changeHi(d: String): String {
            val rules = listOf(
                Regex("double (\\w)") to "$1 दोहरा", Regex("single (\\w)") to "दोहरा $1 एकल",
                Regex("drop final a \\(schwa\\)") to "अंत का a हटाया", Regex("final a \\(schwa\\)") to "अंत में a जोड़ा",
                Regex("silent h after final (\\w)") to "अंतिम $1 के बाद मौन h", Regex("drop silent final h") to "अंत का मौन h हटाया",
                Regex("final (\\w+) to (\\w+)") to "अंत में $1 की जगह $2", Regex("(\\w+) to (\\w+)") to "$1 की जगह $2",
            )
            for ((re, out) in rules) if (re.matches(d)) return re.replace(d, out)
            return d
        }
    }
}
