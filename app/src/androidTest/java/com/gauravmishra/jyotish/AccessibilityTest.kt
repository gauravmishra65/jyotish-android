package com.gauravmishra.jyotish

import android.content.Context
import androidx.compose.ui.semantics.SemanticsNode
import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.semantics.getOrNull
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.hasClickAction
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createEmptyComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.performClick
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.ProfileStore
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * M7 accessibility pass: on each main screen, every tappable element is at least 48dp in both directions
 * (Material's minimum touch target) and has something for TalkBack to read.
 */
@OptIn(ExperimentalTestApi::class)
@RunWith(AndroidJUnit4::class)
class AccessibilityTest {
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

    private fun label(n: SemanticsNode): String {
        val c = n.config
        val text = c.getOrNull(SemanticsProperties.Text)?.joinToString(" ") { it.text }
        val desc = c.getOrNull(SemanticsProperties.ContentDescription)?.joinToString(" ")
        val editable = c.getOrNull(SemanticsProperties.EditableText)?.text
        return listOfNotNull(text, desc, editable).joinToString(" ").trim()
    }

    private fun check(screen: String) {
        rule.waitForIdle()
        val density = ctx.resources.displayMetrics.density
        val problems = rule.onAllNodes(hasClickAction(), useUnmergedTree = false).fetchSemanticsNodes().mapNotNull { n ->
            val w = n.size.width / density
            val h = n.size.height / density
            val name = label(n)
            when {
                n.boundsInRoot.isEmpty -> null                       // scrolled out of view
                w < 47.5f || h < 47.5f -> "$screen: '${name.take(40)}' is ${w.toInt()}x${h.toInt()}dp"
                name.isEmpty() -> "$screen: a ${w.toInt()}x${h.toInt()}dp control has no label"
                else -> null
            }
        }
        assertTrue(problems.joinToString("\n"), problems.isEmpty())
    }

    @Test
    fun mainScreensHaveLabelledFullSizeTargets() {
        ActivityScenario.launch(MainActivity::class.java).use {
            rule.waitUntilAtLeastOneExists(hasText("Aries lagna, Moon in Virgo"), timeoutMillis = 120_000)
            check("Home")
            rule.onNodeWithTag("nav_kundali").performClick()
            rule.waitUntilAtLeastOneExists(hasText("Yogas"), timeoutMillis = 60_000)
            check("Kundali")
            rule.onNodeWithTag("nav_milan").performClick()
            rule.waitUntilAtLeastOneExists(hasText("7 of 10 agree"), timeoutMillis = 120_000)
            check("Milan")
            rule.onNodeWithTag("nav_muhurta").performClick()
            rule.waitUntilAtLeastOneExists(hasText("Use Varanasi"), timeoutMillis = 10_000)
            check("Muhurta")
            rule.onNodeWithTag("nav_numbers").performClick()
            rule.waitUntilAtLeastOneExists(hasText("44/8"), timeoutMillis = 60_000)
            check("Numbers")
        }
    }
}
