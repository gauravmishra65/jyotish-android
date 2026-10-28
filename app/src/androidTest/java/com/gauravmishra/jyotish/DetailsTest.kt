package com.gauravmishra.jyotish

import android.content.Context
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createEmptyComposeRule
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.ProfileStore
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** The Kundali screen's More tab: residence, D9/D10 drawings and the extra sections; Settings' report credits. */
@OptIn(ExperimentalTestApi::class)
@RunWith(AndroidJUnit4::class)
class DetailsTest {
    @get:Rule val rule = createEmptyComposeRule()
    private val ctx: Context get() = InstrumentationRegistry.getInstrumentation().targetContext

    @Before
    fun oneProfileLivingAbroad() {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", "en").commit()
        ctx.filesDir.resolve("charts").deleteRecursively()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Ravi Shankar Tiwari", gender = "M", date = "1988-07-14", time = "14:35", confidence = "reliable",
                place = "Varanasi, India", lat = 25.3176, lon = 82.9739, tz = "Asia/Kolkata",
                residence = "Singapore", resLat = 1.3521, resLon = 103.8198),
        ))
    }

    @Test
    fun moreTabShowsAllSections() {
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasText("Ketu mahadasha", substring = true), timeoutMillis = 120_000)
            rule.onNodeWithTag("nav_kundali").performClick()
            rule.waitUntilAtLeastOneExists(hasText("More"), timeoutMillis = 60_000)
            rule.onNodeWithText("More").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("more_tab"), timeoutMillis = 10_000)
            rule.onNodeWithText("Lives in Singapore").assertExists()
            rule.onNodeWithTag("varga_chart").performScrollTo().assertExists()
            rule.shot("more_d9")
            rule.onNodeWithTag("varga_D10").performClick()
            rule.onNodeWithText("D10: career and public life.").assertExists()
            for (k in listOf("panchang", "ashtakavarga", "yogini", "jaimini", "varshaphal", "lalkitab", "kp", "western_timing")) {
                rule.onNodeWithTag("section_$k").performScrollTo().assertExists()
            }
            rule.onNodeWithText("Pratipada (Shukla paksha, tithi 1 of 30)").performScrollTo().assertExists()   // panchang opens by default
            rule.shot("more_panchang")
            rule.onNodeWithText("Lal Kitab").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasText("How to do a remedy:"), timeoutMillis = 5_000)
            rule.onNodeWithText("Lal Kitab").performScrollTo()
            rule.shot("more_lalkitab")
        }
    }

    @Test
    fun settingsHaveReportCredits() {
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasText("Ketu mahadasha", substring = true), timeoutMillis = 120_000)
            rule.onNodeWithContentDescription("Settings").performClick()
            rule.onNodeWithTag("report_by").performScrollTo().assertExists()
            rule.onNodeWithTag("report_site").assertExists()
            rule.onNodeWithText("Gaurav Mishra").assertExists()
        }
    }
}
