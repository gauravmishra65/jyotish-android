package com.gauravmishra.jyotish.ui

import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.net.Uri
import com.gauravmishra.jyotish.BuildConfig
import com.gauravmishra.jyotish.R

/** The app's public Google Play page; the same link works for every edition (they share one package name). */
val PLAY_URL = "https://play.google.com/store/apps/details?id=${BuildConfig.APPLICATION_ID}"

/** Opens the phone's share sheet with a short message in the app's language; the user can edit it in the app they pick. */
fun shareApp(ctx: Context) {
    val send = Intent(Intent.ACTION_SEND).setType("text/plain")
        .putExtra(Intent.EXTRA_SUBJECT, ctx.getString(R.string.share_subject))
        .putExtra(Intent.EXTRA_TEXT, ctx.getString(R.string.share_message, PLAY_URL))
    try { ctx.startActivity(Intent.createChooser(send, ctx.getString(R.string.share_app))) } catch (_: ActivityNotFoundException) {}
}

/** Opens the app's page in the Play Store app (or the browser when Play is missing), where the user can rate it. */
fun openPlayPage(ctx: Context) {
    val market = Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=${BuildConfig.APPLICATION_ID}"))
    try { ctx.startActivity(market) } catch (_: ActivityNotFoundException) {
        try { ctx.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(PLAY_URL))) } catch (_: ActivityNotFoundException) {}
    }
}

/**
 * When to offer Google's in-app rating card: only after the user has finished something worthwhile (a forecast or a
 * reading) at least three times, never more than three times in all, and at least 30 days apart. Google applies its
 * own limit too, so the card may still not appear.
 */
object ReviewPolicy {
    const val FIRST_AFTER = 3
    const val MAX_ASKS = 3
    const val GAP_MS = 30L * 24 * 60 * 60 * 1000

    fun shouldAsk(moments: Int, asks: Int, lastAskMs: Long, nowMs: Long): Boolean =
        moments >= FIRST_AFTER && asks < MAX_ASKS && (asks == 0 || nowMs - lastAskMs >= GAP_MS)
}
