package com.gauravmishra.jyotish

import android.app.Application
import com.gauravmishra.jyotish.engine.Engine

/** Starts the Python engine in the background as soon as the app process starts. */
class JyotishApp : Application() {
    override fun onCreate() {
        super.onCreate()
        Engine.start(this)
    }
}
