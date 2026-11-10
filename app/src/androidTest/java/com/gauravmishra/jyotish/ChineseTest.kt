package com.gauravmishra.jyotish

import android.content.Context
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.junit4.createEmptyComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.ProfileStore
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** Tools > Chinese astrology: the Zi Wei grid, Nine Star Ki and Tong Shu days for a chosen activity. */
@OptIn(ExperimentalTestApi::class)
@RunWith(AndroidJUnit4::class)
class ChineseTest {
    @get:Rule val rule = createEmptyComposeRule()
    private val ctx: Context get() = InstrumentationRegistry.getInstrumentation().targetContext

    @Test
    fun ziWeiNineStarTongShu() {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", "en")
            .putBoolean("registered", true).putBoolean("tour_seen", true).commit()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Mei Lin Tan", gender = "F", date = "1979-11-23", time = "23:50", confidence = "reliable",
                place = "Singapore", lat = 1.3521, lon = 103.8198, tz = "Asia/Singapore"),
        ))
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("home_tools"), timeoutMillis = 60_000)
            rule.onNodeWithTag("home_tools").performScrollTo().performClick()
            rule.onNodeWithTag("tool_chinese").performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("zwds_grid"), timeoutMillis = 60_000)
            rule.shot("zi_wei")
            rule.onNodeWithTag("section_nine_star_ki").performScrollTo().assertExists()
            rule.onNodeWithTag("cn_act_business").performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasTestTag("section_tong_shu"), timeoutMillis = 60_000)
            rule.onNodeWithTag("section_tong_shu").performScrollTo().assertExists()
        }
    }
}
