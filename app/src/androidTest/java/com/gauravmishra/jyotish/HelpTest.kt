package com.gauravmishra.jyotish

import android.content.Context
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.hasTestTag
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

/** Settings has Help, Share and Rate; Help answers common questions and replays the walkthrough, in both languages. */
@OptIn(ExperimentalTestApi::class)
@RunWith(AndroidJUnit4::class)
class HelpTest {
    @get:Rule val rule = createEmptyComposeRule()
    private val ctx: Context get() = InstrumentationRegistry.getInstrumentation().targetContext

    private fun setUp(lang: String) {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", lang)
            .putBoolean("registered", true).putBoolean("tour_seen", true).commit()
        ctx.filesDir.resolve("charts").deleteRecursively()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Mei Lin Tan", gender = "F", date = "1993-11-21", time = "07:45", confidence = "reliable",
                place = "Singapore", lat = 1.3521, lon = 103.8198, tz = "Asia/Singapore"),
        ))
    }

    @Before fun english() = setUp("en")

    @Test
    fun helpShareRateAndTourReplay() {
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("nav_kundali"), timeoutMillis = 60_000)
            rule.onNodeWithContentDescription("Settings").performClick()
            rule.onNodeWithTag("settings_share").performScrollTo().assertExists()
            rule.onNodeWithTag("settings_rate").performScrollTo().assertExists()
            rule.onNodeWithText("Rate the app").assertExists()
            rule.shot("settings_help")
            rule.onNodeWithTag("settings_help").performScrollTo().performClick()

            // A question opens to show its answer.
            rule.onNodeWithText("Why does the exact birth time matter?").performScrollTo().performClick()
            rule.onNodeWithTag("faq_0_answer").assertExists()
            rule.onNodeWithTag("faq_5").performScrollTo().performClick()
            rule.onNodeWithText("No internet is needed", substring = true).assertExists()
            rule.onNodeWithTag("help_share").performScrollTo().assertExists()
            rule.onNodeWithTag("help_rate").performScrollTo().assertExists()
            rule.shot("help")

            // Replaying the walkthrough from Help, Skip returns to Help.
            rule.onNodeWithTag("help_tour").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("tour_page_0"), timeoutMillis = 5_000)
            rule.onNodeWithTag("tour_skip").performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("help_tour"), timeoutMillis = 5_000)

            // About offers sharing and rating too.
            rule.onNodeWithContentDescription("Back").performClick()
            rule.onNodeWithTag("settings_about").performScrollTo().performClick()
            rule.onNodeWithTag("about_share").performScrollTo().assertExists()
            rule.onNodeWithTag("about_rate").performScrollTo().assertExists()
        }
    }

    @Test
    fun hindiHelp() {
        setUp("hi")
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("nav_kundali"), timeoutMillis = 60_000)
            rule.onNodeWithTag("nav_kundali").assertExists()
            rule.onNodeWithContentDescription("सेटिंग्स").performClick()
            rule.onNodeWithText("ऐप साझा करें").performScrollTo().assertExists()
            rule.onNodeWithTag("settings_help").performScrollTo().performClick()
            rule.onNodeWithText("जन्म का सही समय क्यों ज़रूरी है?").performScrollTo().performClick()
            rule.onNodeWithTag("faq_0_answer").assertExists()
            rule.shot("help_hi")
        }
    }
}
