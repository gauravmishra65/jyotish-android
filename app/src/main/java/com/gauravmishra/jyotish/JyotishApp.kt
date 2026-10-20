package com.gauravmishra.jyotish

import android.app.Application
import android.os.SystemClock
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

/** Starts Python once per process and records how long it took (data files are extracted here). */
class JyotishApp : Application() {
    override fun onCreate() {
        super.onCreate()
        val t0 = SystemClock.elapsedRealtime()
        if (!Python.isStarted()) Python.start(AndroidPlatform(this))
        pythonStartMs = SystemClock.elapsedRealtime() - t0
    }

    companion object {
        @Volatile var pythonStartMs: Long = -1
    }
}
