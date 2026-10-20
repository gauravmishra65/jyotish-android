package com.gauravmishra.jyotish

import android.app.Activity
import android.graphics.Typeface
import android.os.Bundle
import android.os.SystemClock
import android.view.ViewGroup.LayoutParams.MATCH_PARENT
import android.view.ViewGroup.LayoutParams.WRAP_CONTENT
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import com.chaquo.python.Python
import org.json.JSONObject
import kotlin.concurrent.thread

/**
 * Spike screen: proves the Python engine runs on the phone and shows how long each step takes.
 * The real interface (Jetpack Compose, the designed screens) starts in milestone M1.
 */
class MainActivity : Activity() {
    private lateinit var out: TextView
    private val buttons = mutableListOf<Button>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val pad = (16 * resources.displayMetrics.density).toInt()
        val col = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(pad, pad * 2, pad, pad) }
        col.addView(TextView(this).apply { text = "Jyotish engine spike"; textSize = 22f; setTypeface(typeface, Typeface.BOLD) })
        col.addView(TextView(this).apply { text = "Python started in ${JyotishApp.pythonStartMs} ms"; textSize = 15f })
        col.addView(button("Compute sample chart") { sampleChart() })
        col.addView(button("Run timing suite (5 charts, match, muhurta, names)") { timingSuite() })
        out = TextView(this).apply { typeface = Typeface.MONOSPACE; textSize = 13f; setTextIsSelectable(true) }
        col.addView(out)
        setContentView(ScrollView(this).apply { addView(col, LinearLayout.LayoutParams(MATCH_PARENT, WRAP_CONTENT)) })
    }

    private fun button(label: String, action: () -> Unit) = Button(this).apply {
        text = label
        minHeight = (48 * resources.displayMetrics.density).toInt()
        setOnClickListener { action() }
        buttons += this
    }

    private fun busy(on: Boolean, msg: String = "") = runOnUiThread {
        buttons.forEach { it.isEnabled = !on }
        if (on) out.text = msg
    }

    private fun sampleChart() {
        busy(true, "Computing...")
        thread {
            val text = try {
                val t0 = SystemClock.elapsedRealtime()
                val api = Python.getInstance().getModule("engine_api")
                val tImport = SystemClock.elapsedRealtime() - t0
                val req = JSONObject(mapOf("name" to "Ravi Shankar Tiwari", "date" to "1988-07-14", "time" to "14:35",
                    "lat" to 25.3176, "lon" to 82.9739, "tz" to "Asia/Kolkata", "gender" to "M")).toString()
                val t1 = SystemClock.elapsedRealtime()
                val chart = JSONObject(api.callAttr("chart", req).toString())
                val tChart = SystemClock.elapsedRealtime() - t1
                val v = chart.getJSONObject("vedic")
                val lagna = v.getJSONObject("lagna")
                val sb = StringBuilder("import ${tImport} ms, chart ${tChart} ms\n\n")
                sb.append("Lagna ${lagna.getString("sign")} ${lagna.getString("dms")}\n")
                val pl = v.getJSONObject("planets")
                for (p in pl.keys()) {
                    val x = pl.getJSONObject(p)
                    sb.append("%-8s %-12s %-12s %s %d\n".format(p, x.getString("sign"), x.getString("dms"), x.getString("nakshatra"), x.getInt("pada")))
                }
                val cur = v.getJSONObject("dashas").getJSONObject("vimshottari").getJSONObject("current")
                sb.append("\nDasha ${cur.getJSONObject("mahadasha").getString("lord")} / ${cur.getJSONObject("antardasha").getString("lord")}\n")
                sb.append("Yogas found: ${v.getJSONObject("yoga_library").getJSONArray("found").length()}\n")
                sb.toString()
            } catch (e: Throwable) {
                "Failed: $e"
            }
            runOnUiThread { out.text = text }
            busy(false)
        }
    }

    private fun timingSuite() {
        busy(true, "Running the suite (this takes a while)...")
        thread {
            val text = try {
                val api = Python.getInstance().getModule("engine_api")
                JSONObject(api.callAttr("timings").toString()).toString(2)
            } catch (e: Throwable) {
                "Failed: $e"
            }
            runOnUiThread { out.text = "Seconds per step\n$text" }
            busy(false)
        }
    }
}
