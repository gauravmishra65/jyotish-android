package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.ForecastState
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.Driver
import com.gauravmishra.jyotish.data.ForecastArea
import com.gauravmishra.jyotish.data.ForecastModel
import com.gauravmishra.jyotish.data.ForecastYear
import com.gauravmishra.jyotish.data.Profile
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.Locale

private val Rust = Color(0xFF9A3B1B)
private val Amber = Color(0xFF8A5A07)

/** "Oct 2026" or the Hindi month name. */
fun monthYear(iso: String, lang: String): String = try {
    LocalDate.parse(iso.take(10)).format(DateTimeFormatter.ofPattern("MMM yyyy", Locale.forLanguageTag(lang)))
} catch (e: Exception) {
    iso
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun ForecastScreen(
    profiles: List<Profile>,
    profile: Profile?,
    state: ForecastState?,
    onSelect: (Profile) -> Unit,
    onRequest: (Profile) -> Unit,
    onHome: () -> Unit,
    onFeature: (Feature) -> Unit,
) {
    val lang = currentLang()
    var areaKey by rememberSaveable { mutableStateOf(ForecastModel.AREA_KEYS.first()) }
    LaunchedEffect(profile?.id) { profile?.let(onRequest) }

    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        topBar = { BackBar(stringResource(R.string.forecast_title), onHome, subtitle = profile?.name) },
        bottomBar = { BottomNav(current = null, onHome = onHome, onFeature = onFeature, homeSelected = false) },
    ) { pad ->
        Column(
            Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 4.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            if (profiles.size > 1) {
                FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    profiles.forEach { p ->
                        FilterChip(selected = p.id == profile?.id, onClick = { onSelect(p) }, label = { Text(p.name) },
                            modifier = Modifier.heightIn(min = 48.dp),
                            colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep))
                    }
                }
            }
            when (state) {
                null, ForecastState.Calculating -> {
                    if (profile == null) Text(stringResource(R.string.pick_profile_first)) else {
                        Text(stringResource(R.string.fc_working), style = MaterialTheme.typography.bodyLarge)
                        LinearProgressIndicator(Modifier.fillMaxWidth(), color = Palette.Accent)
                    }
                }
                is ForecastState.Failed -> {
                    Text(stringResource(R.string.fc_failed, state.message))
                    OutlinedButton(onClick = { profile?.let(onRequest) }, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.fc_retry)) }
                }
                is ForecastState.Ready -> {
                    val m = state.model
                    Text(stringResource(R.string.fc_window, monthYear(m.from, lang), monthYear(m.to, lang)),
                        style = MaterialTheme.typography.bodyMedium, color = Palette.Muted)
                    m.reliability?.let {
                        Text("⚠ " + it.of(lang), style = MaterialTheme.typography.bodyMedium, color = Palette.AccentDeep,
                            modifier = Modifier.fillMaxWidth().background(Palette.AccentSoft, RoundedCornerShape(12.dp)).padding(12.dp))
                    }
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        m.areas.forEach { a ->
                            FilterChip(selected = a.key == areaKey, onClick = { areaKey = a.key }, label = { Text(a.title.of(lang)) },
                                modifier = Modifier.heightIn(min = 48.dp).testTag("fc_area_${a.key}"),
                                colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep))
                        }
                    }
                    AreaView(m.area(areaKey), lang)
                    Text(stringResource(R.string.fc_how), style = MaterialTheme.typography.titleSmall)
                    Text(m.method.of(lang), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
                }
            }
        }
    }
}

@Composable
private fun AreaView(a: ForecastArea, lang: String) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.testTag("fc_area_view")) {
        Text(a.title.of(lang), style = MaterialTheme.typography.headlineSmall)
        Text(a.subtitle.of(lang), style = MaterialTheme.typography.bodyMedium, color = Palette.Muted)
        Surface(shape = RoundedCornerShape(14.dp), color = Palette.Night, modifier = Modifier.fillMaxWidth()) {
            Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(stringResource(R.string.fc_outlook), style = MaterialTheme.typography.labelMedium, color = Palette.SaffronText)
                Text(a.outlook.of(lang), style = MaterialTheme.typography.titleMedium, color = Palette.Ground, modifier = Modifier.testTag("fc_outlook"))
                val best = a.years.firstOrNull { it.id == a.best }
                val care = a.years.firstOrNull { it.id == a.care }
                Text(if (best != null) stringResource(R.string.fc_best, yearLabel(best, lang)) else stringResource(R.string.fc_no_best),
                    style = MaterialTheme.typography.bodyMedium, color = Palette.NightText)
                Text(if (care != null) stringResource(R.string.fc_care, yearLabel(care, lang)) else stringResource(R.string.fc_no_care),
                    style = MaterialTheme.typography.bodyMedium, color = Palette.NightText)
            }
        }
        if (a.windows.isNotEmpty()) {
            Text(stringResource(R.string.fc_windows), style = MaterialTheme.typography.titleMedium)
            Column(Modifier.fillMaxWidth().background(Palette.AccentSoft, RoundedCornerShape(12.dp)).padding(12.dp).testTag("fc_windows"),
                verticalArrangement = Arrangement.spacedBy(8.dp)) {
                a.windows.forEach { w ->
                    Column {
                        Text(w.text.of(lang), style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.SemiBold)
                        Text(w.meaning.of(lang), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
                    }
                }
            }
        }
        a.years.forEachIndexed { i, y -> YearCard(i + 1, y, lang, a.key) }
    }
}

@Composable
private fun yearLabel(y: ForecastYear, lang: String) =
    stringResource(R.string.fc_year_span, y.id.drop(1).toIntOrNull() ?: 1, monthYear(y.from, lang), monthYear(y.to, lang))

@Composable
private fun YearCard(n: Int, y: ForecastYear, lang: String, area: String) {
    var open by rememberSaveable(area, y.id) { mutableStateOf(false) }
    Surface(shape = RoundedCornerShape(14.dp), color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant), modifier = Modifier.fillMaxWidth().testTag("fc_year_${y.id}")) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(stringResource(R.string.fc_year_span, n, monthYear(y.from, lang), monthYear(y.to, lang)), style = MaterialTheme.typography.titleMedium)
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp), verticalAlignment = Alignment.CenterVertically) {
                LeanPill(y.lean)
                Text(signal(y), style = MaterialTheme.typography.labelMedium, color = Palette.Muted)
            }
            Text(y.summary.of(lang), style = MaterialTheme.typography.bodyLarge)
            if (y.drivers.isNotEmpty()) {
                Text(stringResource(R.string.fc_why), style = MaterialTheme.typography.labelMedium, color = Palette.Muted)
                (if (open) y.drivers + y.more else y.drivers.take(3)).forEach { DriverRow(it, lang, open) }
                val hidden = y.drivers.size + y.more.size - 3
                if (hidden > 0 || open) {
                    TextButton(onClick = { open = !open }, modifier = Modifier.heightIn(min = 48.dp).testTag("fc_more_${y.id}")) {
                        Text(if (open) stringResource(R.string.fc_less) else stringResource(R.string.fc_more, hidden), color = Palette.Accent)
                    }
                }
            }
        }
    }
}

@Composable
private fun signal(y: ForecastYear): String = when {
    y.active == 0 -> stringResource(R.string.fc_signal_none)
    else -> stringResource(R.string.fc_signal, maxOf(y.supportive, y.demanding), y.active) + " · " + stringResource(
        when (y.convergence) { "strong" -> R.string.fc_conv_strong; "moderate" -> R.string.fc_conv_moderate; else -> R.string.fc_conv_weak })
}

@Composable
private fun LeanPill(lean: String) {
    val (label, fg, bg) = when (lean) {
        "supportive" -> Triple(R.string.fc_lean_supportive, Palette.Good, Color(0xFFE6F2E8))
        "demanding" -> Triple(R.string.fc_lean_demanding, Rust, Color(0xFFF9ECE7))
        "mixed" -> Triple(R.string.fc_lean_mixed, Amber, Color(0xFFF9EEDA))
        else -> Triple(R.string.fc_lean_quiet, Palette.Muted, Color(0xFFEFEBE4))
    }
    Text(stringResource(label), style = MaterialTheme.typography.labelLarge, color = fg, fontWeight = FontWeight.SemiBold,
        modifier = Modifier.background(bg, RoundedCornerShape(10.dp)).padding(horizontal = 10.dp, vertical = 4.dp))
}

@Composable
private fun DriverRow(d: Driver, lang: String, technical: Boolean) {
    val (mark, color, word) = when (d.tone) {
        "+" -> Triple("▲", Palette.Good, R.string.fc_lean_supportive)
        "-" -> Triple("▼", Rust, R.string.fc_lean_demanding)
        "~" -> Triple("◆", Amber, R.string.fc_lean_mixed)
        else -> Triple("●", Palette.Muted, R.string.fc_active)
    }
    val label = stringResource(word)
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(mark, color = color, style = MaterialTheme.typography.bodyMedium, modifier = Modifier.width(16.dp).clearAndSetSemantics { contentDescription = label })
        Column(Modifier.weight(1f)) {
            Text(d.text.of(lang), style = MaterialTheme.typography.bodyMedium)
            if (technical && d.technical.isNotEmpty() && d.technical != d.text.en) {
                Text(d.technical, style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
            }
        }
    }
}
