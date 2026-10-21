package com.gauravmishra.jyotish

import android.content.Context
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createEmptyComposeRule
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

/** Kundali Milan for two saved profiles; the numbers must match the desktop engine (28/36, 7 of 10 Porutham). */
@OptIn(ExperimentalTestApi::class)
@RunWith(AndroidJUnit4::class)
class MilanTest {
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
    fun milanShowsTheEngineScore() {
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.onNodeWithText("Milan").performClick()
            rule.waitUntilAtLeastOneExists(hasText("7 of 10 agree"), timeoutMillis = 120_000)
            rule.onNodeWithText("28").assertExists()
            rule.onNodeWithText("Good by the usual bands").assertExists()
            rule.onNodeWithText("Counted from the lagna").assertExists()   // Neha: Mars 2nd from her lagna
            rule.shot("milan")
            rule.onNodeWithTag("koota_nadi").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasText("8 / 8"), timeoutMillis = 5_000)
            rule.onNodeWithTag("koota_meaning").assertExists()   // M6: what Nadi is about
            rule.onNodeWithText("Close").performClick()
            rule.onNodeWithTag("porutham").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasText("Partly"), timeoutMillis = 5_000)   // Rasi Adhipati
            rule.shot("porutham")
        }
    }
}
