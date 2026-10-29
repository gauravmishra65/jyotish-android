package com.gauravmishra.jyotish

import android.content.Context
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.assert
import androidx.compose.ui.test.hasAnyDescendant
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createEmptyComposeRule
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performTextClearance
import androidx.compose.ui.test.performTextInput
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.ProfileStore
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** Demo edition only: one profile, then the upgrade screen; a valid unlock code opens the full version. */
@OptIn(ExperimentalTestApi::class)
@RunWith(AndroidJUnit4::class)
class DemoTest {
    @get:Rule val rule = createEmptyComposeRule()
    private val ctx: Context get() = InstrumentationRegistry.getInstrumentation().targetContext

    @Before
    fun oneProfile() {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", "en")
            .putBoolean("registered", true).putString("user_email", "test@example.com").commit()
        ctx.filesDir.resolve("charts").deleteRecursively()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Ravi Shankar Tiwari", gender = "M", date = "1988-07-14", time = "14:35", confidence = "reliable",
                place = "Varanasi, India", lat = 25.3176, lon = 82.9739, tz = "Asia/Kolkata"),
        ))
    }

    @Test
    fun secondProfileNeedsUnlock() {
        assertEquals("demo", BuildConfig.EDITION)
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("nav_kundali"), timeoutMillis = 60_000)
            rule.onNodeWithTag("nav_kundali").performClick()
            rule.onNodeWithTag("person_new").performClick()
            rule.onNodeWithTag("up_limit").assertExists()
            rule.onNodeWithTag("edition").assert(hasText("Demo edition"))
            rule.shot("upgrade_demo")

            // A code made for another email is refused.
            rule.onNodeWithTag("up_email").performScrollTo().performTextClearance()
            rule.onNodeWithTag("up_email").performTextInput("someone@example.com")
            rule.onNodeWithTag("up_code").performScrollTo().performTextInput("GJ1-PJRDZ-RNMKL-RX4G4-6TKK7-WUDSJ-SAIWQ-77DUH-2USBB-4B3CS-PR44C-2FWYC-HZPOQ-SHEBM-GEC42-3TRWR-WAV7M-MTTVR-IRFDI-KIP73-QL7IW-4OQ")
            rule.onNodeWithTag("up_unlock").performScrollTo().performClick()
            rule.onNodeWithTag("up_message").assertExists()

            // The right email opens the full version, and the add form appears in place.
            rule.onNodeWithTag("up_email").performScrollTo().performTextClearance()
            rule.onNodeWithTag("up_email").performTextInput("test@example.com")
            rule.onNodeWithTag("up_unlock").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("name"), timeoutMillis = 10_000)
            rule.onNodeWithTag("name").assertExists()
        }
        // Remembered across restarts, and Settings says so.
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("nav_kundali"), timeoutMillis = 60_000)
            rule.onNodeWithContentDescription("Settings").performClick()
            rule.onNodeWithTag("settings_upgrade").performScrollTo().assert(hasText("Edition: Full version"))
        }
    }
}
