package com.gauravmishra.jyotish

import android.graphics.Bitmap
import android.util.Base64
import android.util.Log
import androidx.compose.ui.graphics.asAndroidBitmap
import androidx.compose.ui.test.captureToImage
import androidx.compose.ui.test.isRoot
import androidx.compose.ui.test.junit4.ComposeTestRule
import androidx.compose.ui.test.onLast
import java.io.ByteArrayOutputStream

/**
 * A small JPEG of the topmost window (a bottom sheet or dialog if one is open), logged as base64 under the
 * tag SHOT. CI reassembles it into shots/<name>.jpg and publishes it on the ci-results branch.
 */
fun ComposeTestRule.shot(name: String) {
    waitForIdle()
    val bmp = onAllNodes(isRoot()).onLast().captureToImage().asAndroidBitmap()
    log(name, Bitmap.createScaledBitmap(bmp, 360, bmp.height * 360 / bmp.width, true), 75)
    // The screens used for the Play Store listing are also kept at full resolution, as store_<name>.jpg.
    if (name in STORE) log("store_$name", bmp, 92)
}

private val STORE = setOf(
    "kundali_north", "milan", "forecast_marriage", "report_en", "numerology", "muhurta_best", "kundali_hindi_yogas",
    "forecast_hindi", "saved",
)

private fun log(name: String, bmp: Bitmap, quality: Int) {
    val out = ByteArrayOutputStream()
    bmp.compress(Bitmap.CompressFormat.JPEG, quality, out)
    val parts = Base64.encodeToString(out.toByteArray(), Base64.NO_WRAP).chunked(3000)
    parts.forEachIndexed { i, c -> Log.i("SHOT", "$name ${i + 1}/${parts.size} $c") }
}
