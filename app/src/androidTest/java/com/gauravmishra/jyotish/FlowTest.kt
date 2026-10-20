package com.gauravmishra.jyotish

import android.content.Context
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
        }
    }
}
