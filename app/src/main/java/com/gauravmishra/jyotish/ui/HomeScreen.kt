package com.gauravmishra.jyotish.ui

import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.ui.platform.testTag
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.ChartState
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.Profile

@Composable
fun HomeScreen(
    profiles: List<Profile>,
    charts: Map<String, ChartState>,
    onAdd: () -> Unit,
    onEdit: (Profile) -> Unit,
    onOpenProfile: (Profile) -> Unit,
    onDelete: (Profile) -> Unit,
    onSettings: () -> Unit,
    onFeature: (Feature) -> Unit,
    onForecast: () -> Unit = {},
    onReport: () -> Unit = {},
    onSaved: () -> Unit = {},
    userName: String = "",
) {
    val lang = currentLang()
    var actionsFor by remember { mutableStateOf<Profile?>(null) }
    var confirmDelete by remember { mutableStateOf<Profile?>(null) }

    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        bottomBar = { BottomNav(current = null, onHome = {}, onFeature = onFeature) },
    ) { pad ->
        Column(
            Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(20.dp),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    Text(longToday(lang), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(if (userName.isNotBlank()) stringResource(R.string.home_greeting, userName.trim().split(" ").first()) else stringResource(R.string.home_title),
                        style = MaterialTheme.typography.headlineMedium)
                }
                IconButton(onClick = onSettings, modifier = Modifier.size(48.dp)) { Icon(Icons.Filled.Settings, contentDescription = stringResource(R.string.settings)) }
            }

            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(stringResource(R.string.profiles), style = MaterialTheme.typography.titleMedium, modifier = Modifier.weight(1f))
                    TextButton(onClick = onAdd, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.add_profile), color = Palette.Accent) }
                }
                if (profiles.isEmpty()) {
                    Text(stringResource(R.string.no_profiles), style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                } else {
                    LazyRow(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                        items(profiles, key = { it.id }) { p ->
                            ProfileCard(p, charts[p.id], lang, onOpen = { onOpenProfile(p) }, onLongPress = { actionsFor = p })
                        }
                    }
                }
            }

            if (profiles.isNotEmpty()) {
                TextButton(onClick = onSaved, modifier = Modifier.heightIn(min = 48.dp).testTag("home_saved")) {
                    Text(stringResource(R.string.saved_open, profiles.size), color = Palette.Accent)
                }
            }

            profiles.firstOrNull()?.let { first -> NowRunning(first, charts[first.id], lang) }

            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    FeatureTile(Feature.KUNDALI, R.string.feature_kundali_sub, Modifier.weight(1f), onFeature)
                    FeatureTile(Feature.MILAN, R.string.feature_milan_sub, Modifier.weight(1f), onFeature)
                }
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    FeatureTile(Feature.MUHURTA, R.string.feature_muhurta_sub, Modifier.weight(1f), onFeature)
                    FeatureTile(Feature.NUMBERS, R.string.feature_numerology_sub, Modifier.weight(1f), onFeature)
                }
                ForecastTile(onForecast)
                ReportTile(onReport)
            }
        }
    }

    actionsFor?.let { p ->
        AlertDialog(
            onDismissRequest = { actionsFor = null },
            title = { Text(stringResource(R.string.profile_actions, p.name)) },
            confirmButton = { TextButton(onClick = { actionsFor = null; onEdit(p) }, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.edit)) } },
            dismissButton = { TextButton(onClick = { actionsFor = null; confirmDelete = p }, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.delete)) } },
        )
    }
    confirmDelete?.let { p ->
        AlertDialog(
            onDismissRequest = { confirmDelete = null },
            title = { Text(stringResource(R.string.delete_profile_title, p.name)) },
            text = { Text(stringResource(R.string.delete_profile_body)) },
            confirmButton = { TextButton(onClick = { confirmDelete = null; onDelete(p) }, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.delete)) } },
            dismissButton = { TextButton(onClick = { confirmDelete = null }, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.cancel)) } },
        )
    }
}

@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun ProfileCard(p: Profile, state: ChartState?, lang: String, onOpen: () -> Unit, onLongPress: () -> Unit) {
    val sub = when (state) {
        is ChartState.Ready -> stringResource(R.string.lagna_moon, Names.of(state.summary.lagnaSign, lang), Names.of(state.summary.moonSign, lang))
        is ChartState.Failed -> stringResource(R.string.chart_failed, state.message.take(60))
        else -> stringResource(R.string.calculating)
    }
    Card(
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
        modifier = Modifier.width(220.dp).combinedClickable(onClick = onOpen, onLongClick = onLongPress, onLongClickLabel = stringResource(R.string.profile_actions, p.name)),
    ) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Box(Modifier.size(40.dp).background(Palette.AccentSoft, CircleShape), contentAlignment = Alignment.Center) {
                Text(p.initials, color = Palette.AccentDeep, style = MaterialTheme.typography.titleMedium)
            }
            Text(p.name, style = MaterialTheme.typography.titleMedium, maxLines = 2, overflow = TextOverflow.Ellipsis)
            Text("${prettyDate(p.date, lang)}, ${p.time}, ${p.place.substringBefore(",")}", style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant, maxLines = 2, overflow = TextOverflow.Ellipsis)
            Text(sub, style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant, maxLines = 2)
        }
    }
}

@Composable
private fun NowRunning(p: Profile, state: ChartState?, lang: String) {
    val firstName = p.name.trim().substringBefore(" ")
    Column(
        Modifier.fillMaxWidth().background(Palette.Night, RoundedCornerShape(18.dp)).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(stringResource(R.string.now_running, firstName), style = MaterialTheme.typography.labelMedium, color = Palette.SaffronText)
        when (state) {
            is ChartState.Ready -> {
                val s = state.summary
                Text(stringResource(R.string.dasha_line, Names.of(s.mahadasha, lang), Names.of(s.antardasha, lang)),
                    style = MaterialTheme.typography.headlineSmall, color = Palette.Ground)
                val then = s.nextAntardasha?.let { stringResource(R.string.dasha_then, Names.of(it, lang)) } ?: ""
                Text(stringResource(R.string.dasha_detail, Names.of(s.antardasha, lang), prettyDate(s.antardashaEnd, lang), then,
                    Names.of(s.mahadasha, lang), prettyDate(s.mahadashaEnd, lang)), style = MaterialTheme.typography.bodyMedium, color = Palette.NightText)
            }
            is ChartState.Failed -> Text(stringResource(R.string.chart_failed, state.message.take(200)), color = Palette.NightText)
            else -> Text(stringResource(R.string.calculating), style = MaterialTheme.typography.bodyLarge, color = Palette.NightText)
        }
    }
}

@Composable
private fun FeatureTile(f: Feature, sub: Int, modifier: Modifier, onFeature: (Feature) -> Unit) {
    Card(
        onClick = { onFeature(f) },
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
        modifier = modifier.heightIn(min = 112.dp),
    ) {
        Column(Modifier.padding(16.dp).fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Icon(f.icon, contentDescription = null, tint = Palette.Accent, modifier = Modifier.size(28.dp))
            Text(stringResource(f.title), style = MaterialTheme.typography.titleMedium)
            Text(stringResource(sub), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}

@Composable
private fun ForecastTile(onClick: () -> Unit) {
    Card(
        onClick = onClick,
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Palette.Night),
        modifier = Modifier.fillMaxWidth().heightIn(min = 88.dp).testTag("home_forecast"),
    ) {
        Row(Modifier.padding(16.dp).fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(14.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Filled.DateRange, contentDescription = null, tint = Palette.Saffron, modifier = Modifier.size(28.dp))
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(stringResource(R.string.forecast_title), style = MaterialTheme.typography.titleMedium, color = Palette.Ground)
                Text(stringResource(R.string.forecast_sub), style = MaterialTheme.typography.bodySmall, color = Palette.NightText)
            }
        }
    }
}

@Composable
private fun ReportTile(onClick: () -> Unit) {
    Card(
        onClick = onClick,
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
        modifier = Modifier.fillMaxWidth().heightIn(min = 88.dp).testTag("home_report"),
    ) {
        Row(Modifier.padding(16.dp).fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(14.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Filled.Info, contentDescription = null, tint = Palette.Accent, modifier = Modifier.size(28.dp))
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(stringResource(R.string.report_title), style = MaterialTheme.typography.titleMedium)
                Text(stringResource(R.string.report_sub), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
    }
}
