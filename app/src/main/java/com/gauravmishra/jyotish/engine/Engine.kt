package com.gauravmishra.jyotish.engine

import android.app.Application
import android.os.SystemClock
import android.util.Log
import com.chaquo.python.PyObject
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.asCoroutineDispatcher
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.util.concurrent.Executors

/**
 * The only way the app talks to the Python engine. Python runs on one dedicated thread (it has a global
 * lock anyway), starts in the background when the app launches, and every call waits for it to be ready,
 * so the first screen never waits for Python.
 */
object Engine {
    private val thread = Executors.newSingleThreadExecutor { r -> Thread(r, "python-engine") }.asCoroutineDispatcher()
    private val ready = CompletableDeferred<PyObject>()
    @Volatile var startMs: Long = -1
        private set
    @Volatile private var started = false

    fun start(app: Application) {
        if (started) return
        started = true
        CoroutineScope(SupervisorJob() + thread).launch {
            try {
                val t0 = SystemClock.elapsedRealtime()
                if (!Python.isStarted()) Python.start(AndroidPlatform(app))
                val api = Python.getInstance().getModule("engine_api")
                startMs = SystemClock.elapsedRealtime() - t0
                Log.i("ENGINE", "ready in $startMs ms, engine ${api.callAttr("engine_version")}")
                ready.complete(api)
            } catch (e: Throwable) {
                Log.e("ENGINE", "failed to start", e)
                ready.completeExceptionally(e)
            }
        }
    }

    suspend fun awaitReady(): PyObject = ready.await()

    private suspend fun <T> call(block: (PyObject) -> T): T {
        val api = ready.await()
        return withContext(thread) { block(api) }
    }

    /** Chart JSON for a request (see engine_api.chart). */
    suspend fun chart(request: JSONObject): String = call { it.callAttr("chart", request.toString()).toString() }

    /** Kundali Milan for two chart JSONs; [bride] is "A" or "B" (directional kootas depend on it). */
    suspend fun match(chartA: String, chartB: String, bride: String = "B"): String =
        call { it.callAttr("match", chartA, chartB, bride).toString() }

    /** Muhurta search (see engine_api.find_muhurta); [charts] are the chart JSONs of the people to check. */
    suspend fun muhurta(request: JSONObject, charts: List<String>): String =
        call { api -> api.callAttr("find_muhurta", request.toString(), *charts.toTypedArray()).toString() }

    /** Name spelling options for a name and date of birth (YYYY-MM-DD); gender "F" turns off the final-a edits. */
    suspend fun names(name: String, dob: String, gender: String): String =
        call { it.callAttr("names", name, dob, gender).toString() }

    /** Seconds per step of the fixed timing suite (5 charts, a match, a 3-month muhurta, names). */
    suspend fun timings(): String = call { it.callAttr("timings").toString() }

    suspend fun engineVersion(): String = call { it.callAttr("engine_version").toString() }
}
