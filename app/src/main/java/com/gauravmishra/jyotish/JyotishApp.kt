package com.gauravmishra.jyotish

import android.app.Application
import com.gauravmishra.jyotish.data.Meanings
import com.gauravmishra.jyotish.engine.Engine
import com.gauravmishra.jyotish.ui.Names

/** Starts the Python engine in the background as soon as the app process starts. */
class JyotishApp : Application() {
    override fun onCreate() {
        super.onCreate()
        Engine.start(this)
        runCatching { Names.load(assets.open("hindi_names.json").bufferedReader(Charsets.UTF_8).use { it.readText() }) }
        runCatching { Meanings.load(assets.open("meanings.json").bufferedReader(Charsets.UTF_8).use { it.readText() }) }
    }
}
