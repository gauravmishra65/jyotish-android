package com.gauravmishra.jyotish.ui

import android.content.ActivityNotFoundException
import android.content.Intent
import android.net.Uri
import androidx.compose.animation.animateContentSize
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.KeyboardArrowUp
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Share
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.BuildConfig
import com.gauravmishra.jyotish.R

private val faqs = listOf(
    R.string.faq_time_q to R.string.faq_time_a,
    R.string.faq_place_q to R.string.faq_place_a,
    R.string.faq_switch_q to R.string.faq_switch_a,
    R.string.faq_style_q to R.string.faq_style_a,
    R.string.faq_ayanamsa_q to R.string.faq_ayanamsa_a,
    R.string.faq_data_q to R.string.faq_data_a,
    R.string.faq_certain_q to R.string.faq_certain_a,
)

/** Help: common questions with short answers, the walkthrough again, sharing, rating and writing to the author. */
@Composable
fun HelpScreen(onTour: () -> Unit, onBack: () -> Unit) {
    val ctx = LocalContext.current
    val items = if (BuildConfig.EDITION == "full") faqs else faqs + (R.string.faq_full_q to R.string.faq_full_a)
    Scaffold(containerColor = MaterialTheme.colorScheme.background, topBar = { BackBar(stringResource(R.string.help_title), onBack) }) { pad ->
        Column(
            Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            ActionRow(Icons.Filled.PlayArrow, stringResource(R.string.help_tour), stringResource(R.string.help_tour_sub), "help_tour", onTour)
            SectionLabel(stringResource(R.string.help_faq))
            items.forEachIndexed { i, (q, a) -> Faq(stringResource(q), stringResource(a), "faq_$i") }
            SectionLabel(stringResource(R.string.help_more))
            ActionRow(Icons.Filled.Share, stringResource(R.string.share_app), stringResource(R.string.share_app_sub), "help_share") { shareApp(ctx) }
            ActionRow(Icons.Filled.Star, stringResource(R.string.rate_app), stringResource(R.string.rate_app_sub), "help_rate") { openPlayPage(ctx) }
            ActionRow(Icons.Filled.Email, stringResource(R.string.help_write), CONTACT_EMAIL, "help_write") {
                try {
                    ctx.startActivity(Intent(Intent.ACTION_SENDTO, Uri.parse("mailto:$CONTACT_EMAIL"))
                        .putExtra(Intent.EXTRA_SUBJECT, ctx.getString(R.string.contact_subject, BuildConfig.VERSION_NAME)))
                } catch (_: ActivityNotFoundException) {}
            }
        }
    }
}

@Composable
private fun Faq(q: String, a: String, tag: String) {
    var open by rememberSaveable { mutableStateOf(false) }
    Surface(onClick = { open = !open }, shape = RoundedCornerShape(14.dp), color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant), modifier = Modifier.fillMaxWidth().animateContentSize().testTag(tag)) {
        Column(Modifier.padding(horizontal = 14.dp, vertical = 12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(Modifier.heightIn(min = 32.dp), verticalAlignment = Alignment.CenterVertically) {
                Text(q, style = MaterialTheme.typography.titleSmall, modifier = Modifier.weight(1f))
                Icon(if (open) Icons.Filled.KeyboardArrowUp else Icons.Filled.KeyboardArrowDown, contentDescription = null, tint = Palette.Accent)
            }
            if (open) Text(a, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.testTag("${tag}_answer"))
        }
    }
}

/** A tappable row with an icon, a title and a line of explanation; used by Help, Settings and About. */
@Composable
fun ActionRow(icon: ImageVector, title: String, sub: String, tag: String, onClick: () -> Unit) {
    Surface(onClick = onClick, shape = RoundedCornerShape(14.dp), color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant), modifier = Modifier.fillMaxWidth().heightIn(min = 64.dp).testTag(tag)) {
        Row(Modifier.padding(horizontal = 14.dp, vertical = 10.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(14.dp)) {
            Icon(icon, contentDescription = null, tint = Palette.Accent, modifier = Modifier.size(24.dp))
            Column(Modifier.weight(1f)) {
                Text(title, style = MaterialTheme.typography.bodyLarge)
                Text(sub, style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
            }
        }
    }
}
