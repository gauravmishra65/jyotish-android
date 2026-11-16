package com.gauravmishra.jyotish

import android.content.Context
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
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** Tools > Chart through time (v26): the birth chart draws with a chosen moment over it, and the steps move the moment. */
@OptIn(ExperimentalTestApi::class)
@RunWith(AndroidJUnit4::class)
class TimeTravelTest {
    @get:Rule val rule = createEmptyComposeRule()
    private val ctx: Context get() = InstrumentationRegistry.getInstrumentation().targetContext

    @Test
    fun stepsThroughTime() {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", "en")
            .putBoolean("registered", true).putBoolean("tour_seen", true).commit()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Ravi Shankar Tiwari", gender = "M", date = "1988-07-14", time = "14:35",
                confidence = "reliable", place = "Varanasi, Uttar Pradesh, India", lat = 25.3176, lon = 82.9739, tz = "Asia/Kolkata"),
        ))
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("home_tools"), timeoutMillis = 60_000)
            rule.openTool("tool_timetravel")
            rule.waitUntilAtLeastOneExists(hasTestTag("tt_chart"), timeoutMillis = 150_000)
            rule.onNodeWithTag("tt_moment").assertExists()
            rule.onNodeWithTag("tt_1440").performScrollTo().performClick()          // a day on
            rule.onNodeWithTag("tt_525600").performScrollTo().performClick()        // a year on
            rule.waitUntilAtLeastOneExists(hasTestTag("tt_chart"), timeoutMillis = 90_000)
            rule.shot("time_travel")
            rule.onNodeWithTag("tt_chart").performScrollTo().assertExists()
            rule.onNodeWithTag("tt_now").performScrollTo().performClick()
        }
    }

    @Test
    fun comparesAGroup() {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", "en")
            .putBoolean("registered", true).putBoolean("tour_seen", true).commit()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Ravi Shankar Tiwari", gender = "M", date = "1988-07-14", time = "14:35",
                confidence = "reliable", place = "Varanasi, Uttar Pradesh, India", lat = 25.3176, lon = 82.9739, tz = "Asia/Kolkata"),
            Profile(name = "Neha Agarwal", gender = "F", date = "1991-03-02", time = "09:10",
                confidence = "reliable", place = "Delhi, India", lat = 28.6139, lon = 77.2090, tz = "Asia/Kolkata"),
        ))
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("home_tools"), timeoutMillis = 60_000)
            rule.openTool("tool_group")
            rule.onNodeWithTag("grp_compare").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("section_group_facts"), timeoutMillis = 180_000)
            rule.onNodeWithTag("section_group_shared").performScrollTo().assertExists()
            rule.shot("group_compare")
        }
    }

    @Test
    fun ownRules() {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", "en")
            .putBoolean("registered", true).putBoolean("tour_seen", true).commit()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Ravi Shankar Tiwari", gender = "M", date = "1988-07-14", time = "14:35",
                confidence = "reliable", place = "Varanasi, Uttar Pradesh, India", lat = 25.3176, lon = 82.9739, tz = "Asia/Kolkata"),
        ))
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("home_tools"), timeoutMillis = 60_000)
            rule.openTool("tool_customrules")
            rule.onNodeWithTag("cr_varga_go").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("section_custom_varga"), timeoutMillis = 150_000)
            rule.onNodeWithTag("cr_add").performScrollTo().performClick()
            rule.onNodeWithTag("cr_check").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("section_custom_rule"), timeoutMillis = 120_000)
            rule.shot("custom_rules")
        }
    }
}
