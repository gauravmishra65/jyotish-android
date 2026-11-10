package com.gauravmishra.jyotish

import android.content.Context
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createEmptyComposeRule
import androidx.compose.ui.test.onAllNodesWithTag
import androidx.compose.ui.test.onFirst
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
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** Birthplace search finds old names (Bombay) and villages from the bundled GeoNames database, narrowed by district. */
@OptIn(ExperimentalTestApi::class)
@RunWith(AndroidJUnit4::class)
class PlacesTest {
    @get:Rule val rule = createEmptyComposeRule()
    private val ctx: Context get() = InstrumentationRegistry.getInstrumentation().targetContext

    @Test
    fun oldNamesAndVillages() {
        ctx.getSharedPreferences("settings", Context.MODE_PRIVATE).edit().clear().putString("language", "en")
            .putBoolean("registered", true).putBoolean("tour_seen", true).commit()
        ctx.filesDir.resolve("charts").deleteRecursively()
        ProfileStore(ctx.filesDir).save(listOf(
            Profile(name = "Priya Nair", gender = "F", date = "1990-05-05", time = "05:30", confidence = "reliable",
                place = "Kochi, India", lat = 9.9312, lon = 76.2673, tz = "Asia/Kolkata"),
        ))
        // the village database itself, called directly so any error shows in full
        val direct = com.gauravmishra.jyotish.data.Villages.search(ctx, "Rampur, Moradabad", mapOf("IN" to "India"))
        check(direct.isNotEmpty()) { "no villages found directly" }
        check(direct.first().label.contains("Moradabad, Uttar Pradesh")) { direct.first().label }
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasTestTag("nav_kundali"), timeoutMillis = 60_000)
            rule.onNodeWithTag("nav_kundali").performClick()
            rule.onNodeWithTag("person_new").performClick()

            rule.onNodeWithTag("place").performScrollTo().performTextInput("Bombay")
            rule.waitUntil(30_000) { rule.onAllNodes(hasTestTag("place_result") and hasText("Mumbai (Bombay)", substring = true)).fetchSemanticsNodes().isNotEmpty() }

            rule.onNodeWithTag("place").performTextClearance()
            rule.onNodeWithTag("place").performTextInput("Rampur, Moradabad")
            try {
                rule.waitUntil(30_000) {
                    rule.onAllNodes(hasTestTag("place_result") and hasText("Moradabad, Uttar Pradesh", substring = true)).fetchSemanticsNodes().isNotEmpty()
                }
            } catch (e: Throwable) {
                val shown = rule.onAllNodesWithTag("place_result", useUnmergedTree = true).fetchSemanticsNodes().map { n ->
                    n.config.getOrElseNullable(androidx.compose.ui.semantics.SemanticsProperties.Text) { null }?.joinToString(" | ") ?: "?"
                }
                throw AssertionError("village not listed; results shown: $shown", e)
            }
            rule.shot("places_village")
            rule.onAllNodesWithTag("place_result").onFirst().performScrollTo().performClick()
            rule.waitUntilAtLeastOneExists(hasText("Uttar Pradesh", substring = true), timeoutMillis = 5_000)
        }
    }
}
