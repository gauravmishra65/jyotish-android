package com.gauravmishra.jyotish

import android.content.Context
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.junit4.createEmptyComposeRule
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

/** Tools > Birth time check: two life events, then the time spans with their scores. */
@OptIn(ExperimentalTestApi::class)
@RunWith(AndroidJUnit4::class)
class BirthTimeTest {
    @get:Rule val rule = createEmptyComposeRule()
    private val ctx: Context get() = InstrumentationRegistry.getInstrumentation().targetContext

    @Test
    fun spansWithEvents() {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", "en")
            .putBoolean("registered", true).putBoolean("tour_seen", true).commit()
        ctx.filesDir.resolve("charts").deleteRecursively()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Neha Agarwal", gender = "F", date = "1991-03-02", time = "09:10", confidence = "approximate",
                place = "New Delhi, India", lat = 28.6139, lon = 77.2090, tz = "Asia/Kolkata"),
        ))
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("home_tools"), timeoutMillis = 60_000)
            rule.onNodeWithTag("home_tools").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("tool_birth_time"), timeoutMillis = 30_000); rule.onNodeWithTag("tool_birth_time").performScrollTo().performClick()
            rule.onNodeWithTag("bt_window_15").performClick()
            rule.onNodeWithTag("bt_kind_marriage").performClick()
            rule.onNodeWithTag("bt_date").performTextInput("14-02-2016")
            rule.onNodeWithTag("bt_add").performClick()
            rule.onNodeWithTag("bt_kind_child").performScrollTo().performClick()
            rule.onNodeWithTag("bt_date").performTextInput("01-09-2018")
            rule.onNodeWithTag("bt_add").performClick()
            rule.onNodeWithTag("bt_run").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("bt_results"), timeoutMillis = 240_000)
            rule.onNodeWithTag("bt_seg_0").performScrollTo().assertExists()
            rule.shot("birth_time")
        }
    }
}
