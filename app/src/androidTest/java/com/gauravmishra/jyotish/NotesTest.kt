package com.gauravmishra.jyotish

import android.content.Context
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.hasText
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
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** Tools > Notes and life events: a note and an event are saved, kept on the profile and offered to the Birth time check. */
@OptIn(ExperimentalTestApi::class)
@RunWith(AndroidJUnit4::class)
class NotesTest {
    @get:Rule val rule = createEmptyComposeRule()
    private val ctx: Context get() = InstrumentationRegistry.getInstrumentation().targetContext

    @Test
    fun notesAndEventsReachBirthTimeCheck() {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", "en")
            .putBoolean("registered", true).putBoolean("tour_seen", true).commit()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Neha Agarwal", gender = "F", date = "1991-03-02", time = "09:10", confidence = "approximate",
                place = "New Delhi, India", lat = 28.6139, lon = 77.2090, tz = "Asia/Kolkata"),
        ))
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("home_tools"), timeoutMillis = 60_000)
            rule.onNodeWithTag("home_tools").performScrollTo().performClick()
            rule.onNodeWithTag("tool_notes").performClick()
            rule.onNodeWithTag("nb_notes").performTextInput("Prefers Hindi reports")
            rule.onNodeWithTag("nb_kind_marriage").performClick()
            rule.onNodeWithTag("nb_date").performTextInput("14-02-2016")
            rule.onNodeWithTag("nb_add").performClick()
            rule.onNodeWithTag("nb_save").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("nb_saved"), timeoutMillis = 5_000)
        }
        val saved = ProfileStore(ctx.filesDir).load().single()
        assertEquals("Prefers Hindi reports", saved.notes)
        assertEquals(listOf("2016-02-14:marriage"), saved.events)
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("home_tools"), timeoutMillis = 60_000)
            rule.onNodeWithTag("home_tools").performScrollTo().performClick()
            rule.onNodeWithTag("tool_birth_time").performClick()
            rule.waitUntilAtLeastOneExists(hasText("2016-02-14", substring = true), timeoutMillis = 5_000)
        }
    }
}
