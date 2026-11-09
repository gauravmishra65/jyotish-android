package com.gauravmishra.jyotish

import android.content.Context
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.assertTextContains
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createEmptyComposeRule
import androidx.compose.ui.test.onAllNodesWithTag
import androidx.compose.ui.test.onFirst
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performTextInput
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.ProfileStore
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** The Today dashboard: Home's tile, the day's panchang and periods, the person's day, another date, another city, Hindi. */
@OptIn(ExperimentalTestApi::class)
@RunWith(AndroidJUnit4::class)
class TodayTest {
    @get:Rule val rule = createEmptyComposeRule()
    private val ctx: Context get() = InstrumentationRegistry.getInstrumentation().targetContext

    private fun setUp(lang: String) {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", lang)
            .putBoolean("registered", true).putBoolean("tour_seen", true).commit()
        ctx.filesDir.resolve("charts").deleteRecursively()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Ravi Shankar Tiwari", gender = "M", date = "1988-07-14", time = "14:35", confidence = "reliable",
                place = "Varanasi, India", lat = 25.3176, lon = 82.9739, tz = "Asia/Kolkata"),
        ))
    }

    @Test
    fun todayDashboard() {
        setUp("en")
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("home_today_tithi"), timeoutMillis = 90_000)
            rule.onNodeWithTag("home_today").performClick()

            rule.waitUntilAtLeastOneExists(hasTestTag("today_panchang"), timeoutMillis = 30_000)
            rule.onNodeWithTag("today_place").assertTextContains("Varanasi", substring = true)
            rule.onNodeWithTag("today_rahu").performScrollTo().assertExists()
            rule.onNodeWithTag("today_chog_day").performScrollTo().assertExists()
            // the person's day appears once the chart is ready
            rule.waitUntilAtLeastOneExists(hasTestTag("today_guidance"), timeoutMillis = 120_000)
            rule.onNodeWithTag("today_transits").performScrollTo().assertExists()
            rule.onNodeWithTag("today_festivals").performScrollTo().assertExists()
            rule.onNodeWithTag("today_conventions").performScrollTo().assertTextContains("UTC+0530", substring = true)
            rule.onNodeWithTag("today_date").performScrollTo()
            rule.shot("today")

            // another day, then back
            rule.onNodeWithTag("today_next").performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("today_back"), timeoutMillis = 10_000)
            rule.waitUntilAtLeastOneExists(hasTestTag("today_panchang"), timeoutMillis = 30_000)
            rule.onNodeWithTag("today_back").performClick()

            // another city
            rule.onNodeWithTag("today_place").performClick()
            rule.onNodeWithTag("today_place_field").performTextInput("Singap")
            rule.waitUntilAtLeastOneExists(hasTestTag("today_place_field_result"), timeoutMillis = 60_000)
            rule.onAllNodesWithTag("today_place_field_result").onFirst().performClick()
            rule.onNodeWithTag("today_place_ok").performClick()
            rule.waitUntil(30_000) { rule.onAllNodes(hasTestTag("today_conventions") and hasText("Asia/Singapore", substring = true)).fetchSemanticsNodes().isNotEmpty() }
            rule.onNodeWithTag("today_place").assertTextContains("Singapore", substring = true)
            // and back to the person's own city
            rule.onNodeWithTag("today_place").performClick()
            rule.onNodeWithTag("today_place_person").performClick()
            rule.waitUntil(30_000) { rule.onAllNodes(hasTestTag("today_place") and hasText("Varanasi", substring = true)).fetchSemanticsNodes().isNotEmpty() }
        }
    }

    @Test
    fun todayInHindi() {
        setUp("hi")
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("home_today_tithi"), timeoutMillis = 90_000)
            rule.onNodeWithTag("home_today").performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("today_panchang"), timeoutMillis = 30_000)
            rule.waitUntilAtLeastOneExists(hasText("पंचांग"), timeoutMillis = 10_000)
            rule.waitUntilAtLeastOneExists(hasText("राहु काल", substring = true), timeoutMillis = 10_000)
            rule.waitUntilAtLeastOneExists(hasTestTag("today_guidance"), timeoutMillis = 120_000)
            rule.shot("today_hi")
        }
    }

    @Test
    fun darkThemeAndTheNewChartSections() {
        setUp("en")
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().putString("theme", "dark").commit()
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("home_today_tithi"), timeoutMillis = 90_000)
            rule.shot("home_dark")
            rule.onNodeWithTag("home_today").performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("today_guidance"), timeoutMillis = 120_000)
            rule.shot("today_dark")
        }
    }
}
