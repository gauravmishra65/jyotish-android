package com.gauravmishra.jyotish

import android.content.Context
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createEmptyComposeRule
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.onFirst
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performTextClearance
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

/** Marriage muhurta for the test couple, January to March 2027 in Varanasi: 8 days, as on the desktop. */
@OptIn(ExperimentalTestApi::class)
@RunWith(AndroidJUnit4::class)
class MuhurtaTest {
    @get:Rule val rule = createEmptyComposeRule()
    private val ctx: Context get() = InstrumentationRegistry.getInstrumentation().targetContext

    @Before
    fun twoProfiles() {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", "en").commit()
        ctx.filesDir.resolve("charts").deleteRecursively()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Ravi Shankar Tiwari", gender = "M", date = "1988-07-14", time = "14:35", confidence = "reliable",
                place = "Varanasi, India", lat = 25.3176, lon = 82.9739, tz = "Asia/Kolkata"),
            Profile(name = "Neha Agarwal", gender = "F", date = "1991-03-02", time = "09:10", confidence = "reliable",
                place = "New Delhi, India", lat = 28.6139, lon = 77.2090, tz = "Asia/Kolkata"),
        ))
    }

    @Test
    fun findsTheSameDaysAsTheDesktop() {
        ActivityScenario.launch(MainActivity::class.java).use {
            // Wait for both charts on Home before searching, so Tarabala and Chandrabala are applied for both people.
            rule.waitUntilAtLeastOneExists(hasText("Ketu mahadasha", substring = true), timeoutMillis = 120_000)
            rule.waitUntilAtLeastOneExists(hasText("Aries lagna, Moon in Virgo"), timeoutMillis = 60_000)   // Neha's chart
            rule.onNodeWithTag("nav_muhurta").performClick()   // the Home tile may be below the fold
            rule.onNodeWithTag("mu_from").performTextClearance()
            rule.onNodeWithTag("mu_from").performTextInput("01-01-2027")
            rule.onNodeWithTag("mu_to").performTextClearance()
            rule.onNodeWithTag("mu_to").performTextInput("31-03-2027")
            rule.onNodeWithText("Use Varanasi").performScrollTo().performClick()
            rule.onNodeWithTag("mu_find").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("mu_found"), timeoutMillis = 180_000)
            rule.onNodeWithText("8 days pass every rule.").assertExists()
            rule.onNodeWithText("22:06 to 23:26").assertExists()   // the strongest window, 14 Jan 2027
            rule.shot("muhurta_best")
            rule.onNodeWithText("By day").performClick()
            rule.shot("muhurta_days")
        }
    }
}
