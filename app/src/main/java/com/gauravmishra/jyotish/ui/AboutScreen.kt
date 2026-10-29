package com.gauravmishra.jyotish.ui

import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.net.Uri
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
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.BuildConfig
import com.gauravmishra.jyotish.R

const val CONTACT_NAME = "Gaurav Mishra"
const val CONTACT_SITE = "authorgaurav.com"
const val CONTACT_EMAIL = "gaurav.mishra65@gmail.com"

/** About and contact: who made the app, how to reach him, the version, the methods, licences and the disclaimer. */
@Composable
fun AboutScreen(engineVersion: String?, onBack: () -> Unit) {
    val ctx = LocalContext.current
    Scaffold(containerColor = MaterialTheme.colorScheme.background, topBar = { BackBar(stringResource(R.string.about_title), onBack) }) { pad ->
        Column(
            Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            Text(stringResource(R.string.app_name), style = MaterialTheme.typography.headlineMedium)
            Text(stringResource(R.string.about_tagline), style = MaterialTheme.typography.bodyLarge)
            Text(stringResource(R.string.about_version, BuildConfig.VERSION_NAME), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)

            SectionLabel(stringResource(R.string.contact_title))
            ContactRow(Icons.Filled.Person, stringResource(R.string.contact_made_by), CONTACT_NAME, "contact_name") {}
            ContactRow(Icons.Filled.Home, stringResource(R.string.contact_website), CONTACT_SITE, "contact_site") {
                open(ctx, Intent(Intent.ACTION_VIEW, Uri.parse("https://$CONTACT_SITE")))
            }
            ContactRow(Icons.Filled.Email, stringResource(R.string.contact_email), CONTACT_EMAIL, "contact_email") {
                open(ctx, Intent(Intent.ACTION_SENDTO, Uri.parse("mailto:$CONTACT_EMAIL"))
                    .putExtra(Intent.EXTRA_SUBJECT, ctx.getString(R.string.contact_subject, BuildConfig.VERSION_NAME)))
            }
            Text(stringResource(R.string.contact_note), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)

            SectionLabel(stringResource(R.string.about_methods_title))
            Text(stringResource(R.string.about_methods), style = MaterialTheme.typography.bodyMedium)
            engineVersion?.let { Text(stringResource(R.string.engine_version, it), style = MaterialTheme.typography.bodySmall, color = Palette.Muted) }

            SectionLabel(stringResource(R.string.licences))
            Text(stringResource(R.string.licences_body), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)

            SectionLabel(stringResource(R.string.about_disclaimer_title))
            Text(stringResource(R.string.about_disclaimer), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
            Text(stringResource(R.string.data_note), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
        }
    }
}

@Composable
private fun ContactRow(icon: ImageVector, label: String, value: String, tag: String, onClick: () -> Unit) {
    Surface(onClick = onClick, shape = RoundedCornerShape(14.dp), color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant), modifier = Modifier.fillMaxWidth().heightIn(min = 64.dp).testTag(tag)) {
        Row(Modifier.padding(horizontal = 14.dp, vertical = 10.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(14.dp)) {
            Icon(icon, contentDescription = null, tint = Palette.Accent, modifier = Modifier.size(24.dp))
            Column {
                Text(label, style = MaterialTheme.typography.labelMedium, color = Palette.Muted)
                Text(value, style = MaterialTheme.typography.bodyLarge)
            }
        }
    }
}

private fun open(ctx: Context, i: Intent) {
    try {
        ctx.startActivity(i)
    } catch (e: ActivityNotFoundException) {
        // No browser or mail app on the phone: nothing to open; the details stay on screen to copy.
    }
}
