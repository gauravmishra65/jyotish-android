package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.RadioButton
import androidx.compose.material3.RadioButtonDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.gauravmishra.jyotish.R

/** First launch: choose English or Hindi, then add the first chart. Choosing switches the screen's language at once. */
@Composable
fun WelcomeScreen(lang: String, onLanguage: (String) -> Unit, onContinue: () -> Unit) {
    Column(
        Modifier.fillMaxSize().background(Palette.Night).safeDrawingPadding().verticalScroll(rememberScrollState())
            .padding(horizontal = 28.dp, vertical = 40.dp),
        verticalArrangement = Arrangement.spacedBy(28.dp),
    ) {
        Text("☉", color = Palette.Saffron, fontSize = 64.sp)
        Text(stringResource(R.string.welcome_title), style = MaterialTheme.typography.headlineLarge, color = Palette.Ground)
        Text(stringResource(R.string.welcome_body), style = MaterialTheme.typography.bodyLarge, color = Palette.NightText)
        Spacer(Modifier.heightIn(min = 24.dp))
        Column(Modifier.selectableGroup(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text(stringResource(R.string.welcome_language), style = MaterialTheme.typography.bodyMedium, color = Palette.NightText)
            LanguageOption("English", lang == "en") { onLanguage("en") }
            LanguageOption("हिन्दी", lang == "hi") { onLanguage("hi") }
        }
        Button(
            onClick = onContinue,
            modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp),
            shape = RoundedCornerShape(28.dp),
            colors = ButtonDefaults.buttonColors(containerColor = Palette.Saffron, contentColor = Palette.Ink),
        ) { Text(stringResource(R.string.welcome_continue), style = MaterialTheme.typography.labelLarge) }
        Text(
            stringResource(R.string.welcome_disclaimer), style = MaterialTheme.typography.labelMedium,
            color = Palette.NightText, textAlign = TextAlign.Center, modifier = Modifier.fillMaxWidth(),
        )
    }
}

@Composable
private fun LanguageOption(label: String, selected: Boolean, onClick: () -> Unit) {
    Surface(
        shape = RoundedCornerShape(14.dp),
        color = if (selected) Palette.Ground else Palette.Night,
        border = if (selected) null else BorderStroke(1.dp, Palette.Muted),
        modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp)
            .selectable(selected = selected, onClick = onClick, role = Role.RadioButton),
    ) {
        Row(Modifier.padding(horizontal = 18.dp, vertical = 12.dp), verticalAlignment = Alignment.CenterVertically) {
            Text(label, style = MaterialTheme.typography.titleMedium, color = if (selected) Palette.Ink else Palette.Ground, modifier = Modifier.weight(1f))
            RadioButton(selected = selected, onClick = null, colors = RadioButtonDefaults.colors(selectedColor = Palette.Accent, unselectedColor = Palette.NightText))
        }
    }
}
