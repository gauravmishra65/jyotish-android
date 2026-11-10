package com.gauravmishra.jyotish

import android.content.Context
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.junit4.createEmptyComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performScrollToNode
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.ProfileStore
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** Home > Predictions: today's six life areas, then the year from the forecast layer. */
@OptIn(ExperimentalTestApi::class)
@RunWith(AndroidJUnit4::class)
class PredictionTest {
    @get:Rule val rule = createEmptyComposeRule()
    private val ctx: Context get() = InstrumentationRegistry.getInstrumentation().targetContext

    @Test
    fun todayAndYear() {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", "en")
            .putBoolean("registered", true).putBoolean("tour_seen", true).commit()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Ravi Shankar Tiwari", gender = "M", date = "1988-07-14", time = "14:35", confidence = "reliable",
                place = "Varanasi, India", lat = 25.3176, lon = 82.9739, tz = "Asia/Kolkata"),
        ))
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("home_predictions"), timeoutMillis = 60_000)
            rule.onNodeWithTag("home_predictions").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("pred_area_career"), timeoutMillis = 60_000)
            rule.onNodeWithTag("pred_area_learning").performScrollTo().assertExists()
            rule.shot("predictions_today")
            rule.onNodeWithTag("pred_periods").performScrollToNode(hasTestTag("pred_year"))
            rule.onNodeWithTag("pred_year").performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("pred_area_money"), timeoutMillis = 180_000)
            rule.shot("predictions_year")
        }
    }
}
