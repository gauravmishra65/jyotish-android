package com.gauravmishra.jyotish

import android.content.Context
import android.graphics.Bitmap
import android.util.Base64
import android.util.Log
import androidx.compose.ui.graphics.asAndroidBitmap
import androidx.compose.ui.test.captureToImage
import androidx.compose.ui.test.onRoot
import java.io.ByteArrayOutputStream
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createEmptyComposeRule
import androidx.compose.ui.test.onAllNodesWithTag
import androidx.compose.ui.test.onFirst
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performTextInput
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** First launch to a computed chart on Home, in both languages, as a user would do it. */
@OptIn(ExperimentalTestApi::class)
@RunWith(AndroidJUnit4::class)
class FlowTest {
    @get:Rule val rule = createEmptyComposeRule()

    private val ctx: Context get() = InstrumentationRegistry.getInstrumentation().targetContext

    /** A small JPEG of the screen, logged as base64 under SHOT so CI can return it as text. */
    private fun shot(name: String) {
        rule.waitForIdle()
        val bmp = rule.onRoot().captureToImage().asAndroidBitmap()
        val w = 360
        val small = Bitmap.createScaledBitmap(bmp, w, bmp.height * w / bmp.width, true)
        val out = ByteArrayOutputStream()
        small.compress(Bitmap.CompressFormat.JPEG, 70, out)
        val b64 = Base64.encodeToString(out.toByteArray(), Base64.NO_WRAP)
        val parts = b64.chunked(3000)
        parts.forEachIndexed { i, c -> Log.i("SHOT", "$name ${i + 1}/${parts.size} $c") }
    }

    @Before
    fun freshInstall() {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().commit()
        ctx.filesDir.resolve("profiles.json").delete()
        ctx.filesDir.resolve("charts").deleteRecursively()
    }

    @Test
    fun welcomeAddProfileAndSeeTheChartOnHome() {
        ActivityScenario.launch(MainActivity::class.java).use {
            // Choosing Hindi switches the Welcome screen at once; then back to English.
            rule.onNodeWithText("हिन्दी").performClick()
            rule.onNodeWithText("पहली कुंडली जोड़ें").assertExists()
            rule.onNodeWithText("English").performClick()
            rule.onNodeWithText("Add the first birth chart").performScrollTo().performClick()

            rule.onNodeWithTag("name").performTextInput("Ravi Shankar Tiwari")
            rule.onNodeWithTag("date").performScrollTo().performTextInput("14-07-1988")
            rule.onNodeWithTag("time").performScrollTo().performTextInput("14:35")
            rule.onNodeWithTag("place").performScrollTo().performTextInput("Varan")
            rule.waitUntilAtLeastOneExists(hasTestTag("place_result"), timeoutMillis = 60_000)
            rule.onAllNodesWithTag("place_result").onFirst().performScrollTo().performClick()
            rule.onNodeWithText("Varanasi, India").assertExists()
            rule.onNodeWithTag("save").performClick()

            // Home shows the profile, and the engine fills in the chart (first run includes Python start-up).
            rule.waitUntilAtLeastOneExists(hasText("Ravi Shankar Tiwari"), timeoutMillis = 10_000)
            rule.waitUntilAtLeastOneExists(hasText("Scorpio lagna, Moon in Cancer"), timeoutMillis = 120_000)
            rule.waitUntilAtLeastOneExists(hasText("Ketu mahadasha", substring = true), timeoutMillis = 10_000)

            // Kundali: chart, both styles, tabs and a yoga's details.
            rule.onNodeWithText("Ravi Shankar Tiwari").performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("chart"), timeoutMillis = 20_000)
            shot("kundali_north")
            rule.onNodeWithTag("planet_Moon").performScrollTo().assertExists()
            rule.onNodeWithText("South Indian").performScrollTo().performClick()
            rule.onNodeWithTag("chart").performScrollTo().assertExists()
            shot("kundali_south")
            rule.onNodeWithText("Dashas").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasText("Now"), timeoutMillis = 5_000)
            rule.onNodeWithText("Yogas").performScrollTo().performClick()
            rule.onNodeWithTag("yoga_mahapurusha_venus").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasText("Venus in its own or exaltation sign in a kendra from the Lagna"), timeoutMillis = 5_000)
            rule.waitUntilAtLeastOneExists(hasText("In 8% of charts"), timeoutMillis = 5_000)
            shot("yoga_sheet")
            rule.onNodeWithText("Close").performClick()
        }
    }

    @Test
    fun hindiInterfaceShowsHindiNames() {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().putString("language", "hi").commit()
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.onNodeWithText("ज्योतिष").assertExists()
            rule.onNodeWithText("+ प्रोफ़ाइल जोड़ें").performClick()
            rule.onNodeWithTag("name").performTextInput("रवि")
            rule.onNodeWithTag("date").performScrollTo().performTextInput("14-07-1988")
            rule.onNodeWithTag("time").performScrollTo().performTextInput("14:35")
            rule.onNodeWithTag("place").performScrollTo().performTextInput("वाराणसी")
            rule.waitUntilAtLeastOneExists(hasTestTag("place_result"), timeoutMillis = 60_000)
            rule.onAllNodesWithTag("place_result").onFirst().performScrollTo().performClick()
            rule.onNodeWithTag("save").performClick()
            rule.waitUntilAtLeastOneExists(hasText("वृश्चिक लग्न, चंद्र कर्क में"), timeoutMillis = 120_000)
            rule.onNodeWithText("रवि").performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("chart"), timeoutMillis = 20_000)
            rule.onNodeWithText("योग").performScrollTo().performClick()
            rule.onNodeWithText("मालव्य (पंच महापुरुष)").performScrollTo().assertExists()
            shot("kundali_hindi_yogas")
        }
    }
}
