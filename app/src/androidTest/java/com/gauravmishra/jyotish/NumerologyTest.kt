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

@OptIn(ExperimentalTestApi::class)
@RunWith(AndroidJUnit4::class)
class NumerologyTest {
    @get:Rule val rule = createEmptyComposeRule()
    private val ctx: Context get() = InstrumentationRegistry.getInstrumentation().targetContext

    @Before
    fun oneProfile() {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", "en").commit()
        ctx.filesDir.resolve("charts").deleteRecursively()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Ravi Shankar Tiwari", gender = "M", date = "1988-07-14", time = "14:35", confidence = "reliable",
                place = "Varanasi, India", lat = 25.3176, lon = 82.9739, tz = "Asia/Kolkata"),
        ))
    }

    @Test
    fun numbersGridAndNameOptions() {
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.onNodeWithText("Numbers").performClick()
            rule.waitUntilAtLeastOneExists(hasText("44/8"), timeoutMillis = 120_000)
            rule.onNodeWithText("Mercury").assertExists()                   // Mulank 5
            rule.onNodeWithText("11 by total digits").assertExists()       // Life Path 2, or 11 by the other method
            rule.onNodeWithTag("loshu").performScrollTo()
            rule.onNodeWithText("Missing: 3, 6").assertExists()
            rule.shot("numerology")
            rule.onNodeWithTag("names_show").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasText("Ravvi"), timeoutMillis = 30_000)
            rule.onNodeWithText("Ravvi").performScrollTo()
            rule.shot("name_options")
        }
    }
}
