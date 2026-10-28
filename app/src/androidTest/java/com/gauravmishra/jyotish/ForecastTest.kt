package com.gauravmishra.jyotish

import android.content.Context
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createEmptyComposeRule
import androidx.compose.ui.test.onNodeWithTag
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
class ForecastTest {
    @get:Rule val rule = createEmptyComposeRule()
    private val ctx: Context get() = InstrumentationRegistry.getInstrumentation().targetContext

    private fun oneProfile(lang: String) {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", lang).commit()
        ctx.filesDir.resolve("charts").deleteRecursively()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Ravi Shankar Tiwari", gender = "M", date = "1988-07-14", time = "14:35", confidence = "reliable",
                place = "Varanasi, India", lat = 25.3176, lon = 82.9739, tz = "Asia/Kolkata"),
        ))
    }

    @Before
    fun english() = oneProfile("en")

    @Test
    fun fourAreasYearByYear() {
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("home_forecast"), timeoutMillis = 60_000)
            rule.onNodeWithTag("home_forecast").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("fc_outlook"), timeoutMillis = 180_000)
            rule.onNodeWithTag("fc_year_Y1").assertExists()
            rule.onNodeWithTag("fc_windows").assertExists()          // marriage windows
            rule.shot("forecast_marriage")
            rule.onNodeWithTag("fc_year_Y2").performScrollTo()
            rule.onNodeWithTag("fc_more_Y2").performScrollTo().performClick()
            rule.shot("forecast_year_open")
            rule.onNodeWithTag("fc_area_work").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasText("Work & career"), timeoutMillis = 5_000)
            rule.onNodeWithTag("fc_area_health").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasText("Not medical advice", substring = true), timeoutMillis = 5_000)
            rule.shot("forecast_health")
            rule.onNodeWithTag("fc_area_family").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasText("Love & family"), timeoutMillis = 5_000)
            rule.onNodeWithTag("fc_year_Y3").performScrollTo().assertExists()
        }
    }

    @Test
    fun hindiForecast() {
        oneProfile("hi")
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("home_forecast"), timeoutMillis = 60_000)
            rule.onNodeWithTag("home_forecast").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("fc_outlook"), timeoutMillis = 180_000)
            rule.waitUntilAtLeastOneExists(hasText("विवाह और जीवनसाथी"), timeoutMillis = 5_000)
            rule.shot("forecast_hindi")
        }
    }
}
