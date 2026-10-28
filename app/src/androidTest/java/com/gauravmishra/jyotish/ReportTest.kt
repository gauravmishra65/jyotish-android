package com.gauravmishra.jyotish

import android.content.Context
import android.view.View
import android.view.ViewGroup
import android.webkit.WebView
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.junit4.createEmptyComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.ProfileStore
import org.json.JSONArray
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

@OptIn(ExperimentalTestApi::class)
@RunWith(AndroidJUnit4::class)
class ReportTest {
    @get:Rule val rule = createEmptyComposeRule()
    private val ctx: Context get() = InstrumentationRegistry.getInstrumentation().targetContext

    @Before
    fun oneProfile() {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", "en").commit()
        ctx.filesDir.resolve("charts").deleteRecursively()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Ravi Shankar Tiwari", gender = "M", date = "1988-07-14", time = "14:35", confidence = "reliable",
                place = "Varanasi, India", lat = 25.3176, lon = 82.9739, tz = "Asia/Kolkata"),
        ))
    }

    private fun findWebView(v: View): WebView? = when (v) {
        is WebView -> v
        is ViewGroup -> (0 until v.childCount).firstNotNullOfOrNull { findWebView(v.getChildAt(it)) }
        else -> null
    }

    /** Runs [js] in the report's WebView and returns its JSON result, once the page has loaded. */
    private fun eval(scenario: ActivityScenario<MainActivity>, js: String): String {
        var out = ""
        repeat(60) {
            val latch = CountDownLatch(1)
            scenario.onActivity { a ->
                val wv = findWebView(a.window.decorView)
                if (wv == null) latch.countDown() else wv.evaluateJavascript(js) { out = it; latch.countDown() }
            }
            latch.await(5, TimeUnit.SECONDS)
            if (out.isNotEmpty() && out != "null" && out != "0" && out != "\"\"") return out
            Thread.sleep(500)
        }
        return out
    }

    @Test
    fun fullReadingInEnglishAndHindi() {
        ActivityScenario.launch(MainActivity::class.java).use { sc ->
            rule.waitUntilAtLeastOneExists(hasTestTag("home_report"), timeoutMillis = 60_000)
            rule.onNodeWithTag("home_report").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("report_view"), timeoutMillis = 180_000)
            rule.onNodeWithTag("report_pdf").assertExists()
            rule.onNodeWithTag("report_share").assertExists()
            // All eight sections are in the page, with the person's Vedic facts.
            assertEquals("8", eval(sc, "document.querySelectorAll('section.page').length"))
            val en = JSONArray("[" + eval(sc, "document.getElementById('sec2').innerText") + "]").getString(0)
            assertTrue(en, en.contains("Your rising sign (lagna) is Scorpio"))
            rule.shot("report_en")
            rule.onNodeWithTag("report_lang_hi").performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("report_view"), timeoutMillis = 180_000)
            var hi = ""
            for (i in 0 until 40) {
                hi = JSONArray("[" + eval(sc, "document.documentElement.lang + '|' + document.getElementById('sec2').innerText") + "]").getString(0)
                if (hi.startsWith("hi|")) break
                Thread.sleep(500)
            }
            assertTrue(hi.take(200), hi.startsWith("hi|") && hi.contains("आपकी लग्न वृश्चिक है"))
            rule.shot("report_hi")
        }
    }
}
