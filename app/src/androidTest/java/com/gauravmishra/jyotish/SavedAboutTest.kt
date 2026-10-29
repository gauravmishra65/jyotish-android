package com.gauravmishra.jyotish

import android.content.Context
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createEmptyComposeRule
import androidx.compose.ui.test.onAllNodesWithTag
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performTextInput
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.ProfileStore
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** Saved Kundlis (search, groups, open), My details from Settings, About and contact. */
@OptIn(ExperimentalTestApi::class)
@RunWith(AndroidJUnit4::class)
class SavedAboutTest {
    @get:Rule val rule = createEmptyComposeRule()
    private val ctx: Context get() = InstrumentationRegistry.getInstrumentation().targetContext

    @Before
    fun threeProfiles() {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", "en").commit()
        ctx.filesDir.resolve("charts").deleteRecursively()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Ravi Shankar Tiwari", gender = "M", date = "1988-07-14", time = "14:35", confidence = "reliable",
                place = "Varanasi, India", lat = 25.3176, lon = 82.9739, tz = "Asia/Kolkata", group = "family"),
            Profile(name = "Neha Agarwal", gender = "F", date = "1991-03-02", time = "09:10", confidence = "reliable",
                place = "New Delhi, India", lat = 28.6139, lon = 77.2090, tz = "Asia/Kolkata", group = "friends"),
            Profile(name = "Mei Lin Tan", gender = "F", date = "1979-11-23", time = "23:50", confidence = "reliable",
                place = "Singapore", lat = 1.3521, lon = 103.8198, tz = "Asia/Singapore", group = "clients"),
        ))
    }

    @Test
    fun savedKundlisSearchGroupsAndOpen() {
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("home_saved"), timeoutMillis = 60_000)
            rule.onNodeWithTag("home_saved").performScrollTo().performClick()
            rule.onNodeWithText("3 saved").assertExists()
            rule.onNodeWithTag("group_clients").performClick()
            rule.onNodeWithTag("saved_Mei Lin Tan").assertExists()
            rule.onNodeWithTag("saved_Neha Agarwal").assertDoesNotExist()
            rule.onNodeWithTag("group_all").performClick()
            rule.onNodeWithTag("saved_search").performTextInput("delhi")          // place search
            rule.onNodeWithTag("saved_Neha Agarwal").assertExists()
            rule.onNodeWithTag("saved_Ravi Shankar Tiwari").assertDoesNotExist()
            rule.shot("saved")
            rule.onNodeWithTag("saved_Neha Agarwal").performClick()
            rule.waitUntilAtLeastOneExists(hasText("Neha Agarwal"), timeoutMillis = 10_000)
            rule.waitUntilAtLeastOneExists(hasTestTag("chart"), timeoutMillis = 120_000)
        }
    }

    @Test
    fun myDetailsAndAboutFromSettings() {
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasText("Gaurav Jyotish"), timeoutMillis = 30_000)
            rule.onNodeWithContentDescription("Settings").performClick()
            rule.onNodeWithTag("settings_my_details").performClick()
            rule.onNodeWithTag("reg_name").performTextInput("Priya Nair")
            rule.onNodeWithTag("reg_save").performScrollTo().performClick()
            rule.waitUntil(5_000) { rule.onAllNodesWithTag("reg_send_no").fetchSemanticsNodes().isNotEmpty() }
            rule.onNodeWithTag("reg_send_no").performClick()
            rule.onNodeWithText("Priya Nair").assertExists()                        // Settings shows the registered name
            rule.onNodeWithTag("settings_about").performClick()
            rule.onNodeWithText("gaurav.mishra65@gmail.com").assertExists()
            rule.onNodeWithText("authorgaurav.com").assertExists()
            rule.onNodeWithText("Gaurav Mishra").assertExists()
            rule.shot("about")
        }
    }
}
