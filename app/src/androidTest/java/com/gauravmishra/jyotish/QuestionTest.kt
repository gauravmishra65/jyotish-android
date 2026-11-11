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

/** Tools > Prashna and KP horary: a question asked now gets a leaning, the checks behind it and the reminder. */
@OptIn(ExperimentalTestApi::class)
@RunWith(AndroidJUnit4::class)
class QuestionTest {
    @get:Rule val rule = createEmptyComposeRule()
    private val ctx: Context get() = InstrumentationRegistry.getInstrumentation().targetContext

    @Test
    fun prashnaAndKp() {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", "en")
            .putBoolean("registered", true).putBoolean("tour_seen", true).commit()
        ctx.filesDir.resolve("charts").deleteRecursively()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Arjun Mehta", gender = "M", date = "1996-06-30", time = "01:30", confidence = "reliable",
                place = "London, UK", lat = 51.5074, lon = -0.1278, tz = "Europe/London"),
        ))
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("home_tools"), timeoutMillis = 60_000)
            rule.onNodeWithTag("home_tools").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("tool_prashna"), timeoutMillis = 30_000); rule.onNodeWithTag("tool_prashna").performScrollTo().performClick()
            rule.onNodeWithTag("q_marriage").performClick()
            rule.onNodeWithTag("q_ask").performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("q_lean"), timeoutMillis = 120_000)
            rule.shot("prashna")
            rule.onNodeWithTag("q_answer").performScrollTo().assertExists()
        }
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("home_tools"), timeoutMillis = 60_000)
            rule.onNodeWithTag("home_tools").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("tool_kp"), timeoutMillis = 30_000); rule.onNodeWithTag("tool_kp").performScrollTo().performClick()
            rule.onNodeWithTag("q_job").performClick()
            rule.onNodeWithTag("kp_number").performTextInput("131")
            rule.onNodeWithTag("q_ask").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("q_lean"), timeoutMillis = 120_000)
            rule.shot("kp_horary")
        }
    }

    /** Tools > Numerology tools: a vehicle number and a business name come back as open cards. */
    @Test
    fun numberTools() {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", "en")
            .putBoolean("registered", true).putBoolean("tour_seen", true).commit()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Ravi Shankar Tiwari", gender = "M", date = "1988-07-14", time = "14:35", confidence = "reliable",
                place = "Varanasi, India", lat = 25.3176, lon = 82.9739, tz = "Asia/Kolkata"),
        ))
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("home_tools"), timeoutMillis = 60_000)
            rule.onNodeWithTag("home_tools").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("tool_numbers"), timeoutMillis = 30_000); rule.onNodeWithTag("tool_numbers").performScrollTo().performClick()
            rule.onNodeWithTag("nt_vehicle").performClick()
            rule.onNodeWithTag("nt_text").performTextInput("UP 32 AB 1234")
            rule.onNodeWithTag("nt_run").performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("section_num_vehicle"), timeoutMillis = 60_000)
            rule.onNodeWithTag("nt_business").performClick()
            rule.onNodeWithTag("nt_text").performTextInput("Shree Ganesh Traders")
            rule.onNodeWithTag("nt_run").performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("section_num_business"), timeoutMillis = 60_000)
            rule.shot("number_tools")
        }
    }
}
