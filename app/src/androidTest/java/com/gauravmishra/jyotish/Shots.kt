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
    val small = Bitmap.createScaledBitmap(bmp, 360, bmp.height * 360 / bmp.width, true)
    val out = ByteArrayOutputStream()
    small.compress(Bitmap.CompressFormat.JPEG, 75, out)
    val parts = Base64.encodeToString(out.toByteArray(), Base64.NO_WRAP).chunked(3000)
    parts.forEachIndexed { i, c -> Log.i("SHOT", "$name ${i + 1}/${parts.size} $c") }
}
