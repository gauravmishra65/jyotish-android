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

/** Tools > Flying Stars: the year's grid, then a home facing south built in 2010 (Period 8). */
@OptIn(ExperimentalTestApi::class)
@RunWith(AndroidJUnit4::class)
class FengShuiTest {
    @get:Rule val rule = createEmptyComposeRule()
    private val ctx: Context get() = InstrumentationRegistry.getInstrumentation().targetContext

    @Test
    fun yearGridAndHouse() {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", "en")
            .putBoolean("registered", true).putBoolean("tour_seen", true).commit()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Mei Lin Tan", gender = "F", date = "1979-11-23", time = "23:50", confidence = "reliable",
                place = "Singapore", lat = 1.3521, lon = 103.8198, tz = "Asia/Singapore"),
        ))
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("home_tools"), timeoutMillis = 60_000)
            rule.onNodeWithTag("home_tools").performScrollTo().performClick()
            rule.onNodeWithTag("tool_fengshui").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("fs_grid"), timeoutMillis = 60_000)
            rule.onNodeWithTag("fs_facing").performScrollTo().performTextInput("180")
            rule.onNodeWithTag("fs_built").performScrollTo().performTextInput("2010")
            rule.onNodeWithTag("fs_run").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("section_fs_house"), timeoutMillis = 60_000)
            rule.shot("feng_shui")
        }
    }
}
