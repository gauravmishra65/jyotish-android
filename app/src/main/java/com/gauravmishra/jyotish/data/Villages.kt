package com.gauravmishra.jyotish.data

import android.content.Context
import android.database.sqlite.SQLiteDatabase
import java.io.File
import java.util.zip.GZIPInputStream

/**
 * Villages and small towns of India and Nepal from the full GeoNames files (assets/villages.db.gz, built by
 * tools/make_villages.py). Unpacked once into the app's private storage on first use; each search is an indexed
 * prefix lookup, so the town list in [Places] stays small and fast. Returns nothing when the asset is absent.
 */
object Villages {
    private const val ASSET = "villages.db.gz"
    @Volatile private var db: SQLiteDatabase? = null
    @Volatile private var missing = false

    private fun open(ctx: Context): SQLiteDatabase? {
        db?.let { return it }
        if (missing) return null
        synchronized(this) {
            db?.let { return it }
            val file = File(ctx.filesDir, "villages-v2.db")
            if (!file.exists()) {
                ctx.filesDir.listFiles { f -> f.name.startsWith("villages-v") }?.forEach { it.delete() }   // an older layout
                val tmp = File(ctx.filesDir, "villages.tmp")
                try {
                    ctx.assets.open(ASSET).use { a -> GZIPInputStream(a).use { g -> tmp.outputStream().use { g.copyTo(it) } } }
                } catch (e: java.io.IOException) {
                    missing = true
                    tmp.delete()
                    return null
                }
                tmp.renameTo(file)
            }
            return SQLiteDatabase.openDatabase(file.path, null, SQLiteDatabase.OPEN_READONLY).also { db = it }
        }
    }

    /** Up to [limit] places whose name starts with [query] (English or Devanagari), with district and state. */
    fun search(ctx: Context, query: String, countries: Map<String, String>, limit: Int = 8): List<Place> {
        val q = query.trim()
        if (q.length < 3) return emptyList()
        val key = if (q.any { it in 'ऀ'..'ॿ' }) q else Places.fold(q)
        val d = open(ctx) ?: return emptyList()
        val out = ArrayList<Place>()
        val cols = "SELECT p.name, p.cc, p.lat, p.lon, t.name, r.district, r.state FROM place p JOIN tz t ON t.id = p.tz JOIN region r ON r.id = p.region "
        val sql = if (key.any { it in 'ऀ'..'ॿ' })
            cols + "JOIN hindi h ON h.id = p.id WHERE h.key >= ? AND h.key < ? GROUP BY p.id ORDER BY length(h.key), p.name LIMIT ?"
        else
            cols + "WHERE p.name >= ? AND p.name < ? ORDER BY length(p.name), p.name LIMIT ?"
        d.rawQuery(sql, arrayOf(key, key + "\uFFFF", limit.toString())).use { c ->
            while (c.moveToNext()) {
                val region = listOf(c.getString(5), c.getString(6)).filter { !it.isNullOrBlank() }.joinToString(", ")
                out += Place(c.getString(0), c.getString(1), countries[c.getString(1)] ?: c.getString(1), c.getInt(2) / 10000.0,
                    c.getInt(3) / 10000.0, c.getString(4), 0, emptyList(), region = region)
            }
        }
        return out
    }
}
