package com.gauravmishra.jyotish

import android.os.SystemClock
import android.util.Log
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.gauravmishra.jyotish.engine.Engine
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith

/**
 * The engine on this device must reproduce the desktop snapshot exactly (5 charts in 5 time zones, a Kundali
 * Milan, a 3-month muhurta search and name options); every step is timed. Results go to logcat as SPIKE.
 */
@RunWith(AndroidJUnit4::class)
class SpikeTest {
    @Test
    fun engineMatchesDesktopSnapshot() {
        val snapshot = InstrumentationRegistry.getInstrumentation().context.assets
            .open("snapshot.json").bufferedReader().use { it.readText() }
        val t0 = SystemClock.elapsedRealtime()
        val api = runBlocking { Engine.awaitReady() }
        val waitMs = SystemClock.elapsedRealtime() - t0
        val report = JSONObject(api.callAttr("selftest", snapshot).toString())
        report.put("python_start_ms", Engine.startMs)
        report.put("waited_for_engine_ms", waitMs)
        report.toString(1).chunked(3000).forEach { Log.i("SPIKE", it) }
        assertTrue("Device results differ from the desktop snapshot: " + report.optJSONArray("mismatches")?.toString()?.take(2000),
            report.getBoolean("ok"))
    }
}
