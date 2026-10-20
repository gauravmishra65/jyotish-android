package com.gauravmishra.jyotish

import android.os.SystemClock
import android.util.Log
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.chaquo.python.Python
import org.json.JSONObject
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith

/**
 * M0 go/no-go check: the engine on this device must reproduce the desktop snapshot exactly
 * (5 charts in 5 time zones, a Kundali Milan, a 3-month muhurta search and name options),
 * and every step is timed. Results go to logcat under the tag SPIKE for the CI summary.
 */
@RunWith(AndroidJUnit4::class)
class SpikeTest {
    @Test
    fun engineMatchesDesktopSnapshot() {
        val snapshot = InstrumentationRegistry.getInstrumentation().context.assets
            .open("snapshot.json").bufferedReader().use { it.readText() }
        val t0 = SystemClock.elapsedRealtime()
        val api = Python.getInstance().getModule("engine_api")
        val importMs = SystemClock.elapsedRealtime() - t0
        val report = JSONObject(api.callAttr("selftest", snapshot).toString())
        report.put("python_start_ms", JyotishApp.pythonStartMs)
        report.put("first_import_ms", importMs)
        report.toString(1).chunked(3000).forEach { Log.i("SPIKE", it) }
        assertTrue("Device results differ from the desktop snapshot: " + report.optJSONArray("mismatches")?.toString()?.take(2000),
            report.getBoolean("ok"))
    }
}
