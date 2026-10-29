package com.gauravmishra.jyotish.store

import android.content.Context

/** This edition sells through unlock codes (or is already full), so there is no in-app shop. */
fun createStore(context: Context): Store = NoStore
