package com.gauravmishra.jyotish.data

import org.json.JSONObject

/**
 * Plain-words meanings in English and Hindi (assets/meanings.json, written by tools/make_meanings.py).
 * Every line says what a factor is traditionally associated with; none of them predicts anything.
 * A missing entry returns null and the screen simply shows nothing extra.
 */
object Meanings {
    private var root: JSONObject = JSONObject()

    fun load(json: String) {
        root = JSONObject(json)
    }

    private fun get(table: String, key: String, lang: String): String? =
        root.optJSONObject(table)?.optJSONObject(key)?.optString(if (lang == "hi") "hi" else "en")?.takeIf { it.isNotEmpty() }

    fun planet(name: String, lang: String) = get("planet", name, lang)
    fun house(n: Int, lang: String) = get("house", n.toString(), lang)
    fun koota(key: String, lang: String) = get("koota", key, lang)
    fun porutham(key: String, lang: String) = get("porutham", key, lang)
    fun number(n: Int, lang: String) = get("number", n.toString(), lang)
    fun numberType(key: String, lang: String) = get("number_type", key, lang)

    /** The yoga's own meaning when there is one, then what its category means in general. */
    fun yoga(id: String, category: String, lang: String): List<String> =
        listOfNotNull(get("yoga", id, lang), get("yoga_category", category, lang))

    /** Hindi names for yogas the skill's report does not name in Hindi. */
    fun yogaNameHi(english: String): String? = root.optJSONObject("yoga_name_hi")?.optString(english)?.takeIf { it.isNotEmpty() }
}
