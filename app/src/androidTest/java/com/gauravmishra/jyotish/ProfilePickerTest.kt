package com.gauravmishra.jyotish

import android.content.Context
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.hasAnyDescendant
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
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** Every person-based screen lets the user pick a saved Kundli or add a new person and come straight back. */
@OptIn(ExperimentalTestApi::class)
@RunWith(AndroidJUnit4::class)
class ProfilePickerTest {
    @get:Rule val rule = createEmptyComposeRule()
    private val ctx: Context get() = InstrumentationRegistry.getInstrumentation().targetContext

    @Before
    fun twoProfiles() {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", "en").putBoolean("registered", true).commit()
        ctx.filesDir.resolve("charts").deleteRecursively()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Ravi Shankar Tiwari", gender = "M", date = "1988-07-14", time = "14:35", confidence = "reliable",
                place = "Varanasi, India", lat = 25.3176, lon = 82.9739, tz = "Asia/Kolkata"),
            Profile(name = "Neha Agarwal", gender = "F", date = "1991-03-02", time = "09:10", confidence = "reliable",
                place = "New Delhi, India", lat = 28.6139, lon = 77.2090, tz = "Asia/Kolkata"),
        ))
    }

    private fun pickerShows(name: String) =
        rule.waitUntil(10_000) { rule.onAllNodesWithTag("person_picker").fetchSemanticsNodes().isNotEmpty() }.also {
            rule.onNodeWithTag("person_picker").assert(hasAnyDescendant(hasText(name)))
        }

    @Test
    fun pickSavedAndAddNew() {
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("nav_kundali"), timeoutMillis = 60_000)
            rule.onNodeWithTag("nav_kundali").performClick()

            // Pick a saved Kundli from the list.
            rule.onNodeWithTag("person_picker").performClick()
            rule.onNodeWithTag("pick_Neha Agarwal").assertExists()
            rule.onNodeWithTag("pick_add").assertExists()
            rule.shot("person_picker")
            rule.onNodeWithTag("pick_Neha Agarwal").performClick()
            pickerShows("Neha Agarwal")

            // Add a new person from the same screen: after saving we are back here, with the new person chosen.
            rule.onNodeWithTag("person_new").performClick()
            rule.onNodeWithTag("name").performTextInput("Arjun Mehta")
            rule.onNodeWithTag("date").performScrollTo().performTextInput("05-01-1985")
            rule.onNodeWithTag("time").performScrollTo().performTextInput("06:15")
            rule.onNodeWithTag("place").performScrollTo().performTextInput("Mumb")
            rule.waitUntilAtLeastOneExists(hasTestTag("place_result"), timeoutMillis = 60_000)
            rule.onAllNodesWithTag("place_result").onFirst().performScrollTo().performClick()
            rule.onNodeWithTag("save").performClick()
            pickerShows("Arjun Mehta")
            rule.waitUntilAtLeastOneExists(hasTestTag("chart"), timeoutMillis = 120_000)

            // The same picker is on the Numbers screen, and the choice carries over.
            rule.onNodeWithTag("nav_numbers").performClick()
            pickerShows("Arjun Mehta")
        }
    }
}
