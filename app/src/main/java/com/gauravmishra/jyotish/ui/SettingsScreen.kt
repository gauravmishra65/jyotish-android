package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.toggleable
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.rememberCoroutineScope
import kotlinx.coroutines.launch
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.AppSettings

@Composable
fun SettingsScreen(
    settings: AppSettings,
    lang: String,
    engineVersion: String?,
    onLanguage: (String) -> Unit,
    onCalculationChanged: () -> Unit,
    onChartStyle: (String) -> Unit,
    onSpeedTest: suspend () -> String,
    onBack: () -> Unit,
) {
    var speed by remember { mutableStateOf<String?>(null) }
    var running by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    var chartStyle by remember { mutableStateOf(settings.chartStyle) }
    var ayanamsa by remember { mutableStateOf(settings.ayanamsa) }
    var node by remember { mutableStateOf(settings.node) }
    var weekdayHard by remember { mutableStateOf(settings.weekdayHard) }

    Scaffold(containerColor = MaterialTheme.colorScheme.background, topBar = { BackBar(stringResource(R.string.settings), onBack) }) { pad ->
        Column(
            Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            SectionLabel(stringResource(R.string.display))
            Group {
                Setting(stringResource(R.string.language)) {
                    Pick("English", lang == "en") { onLanguage("en") }
                    Pick("हिन्दी", lang == "hi") { onLanguage("hi") }
                }
                HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
                Setting(stringResource(R.string.chart_style)) {
                    Pick(stringResource(R.string.north_indian), chartStyle == "north") { chartStyle = "north"; onChartStyle("north") }
                    Pick(stringResource(R.string.south_indian), chartStyle == "south") { chartStyle = "south"; onChartStyle("south") }
                }
            }

            SectionLabel(stringResource(R.string.calculation))
            Group {
                Setting(stringResource(R.string.ayanamsa)) {
                    listOf("lahiri" to "Lahiri", "raman" to "Raman", "krishnamurti" to "KP", "true_chitra" to "True Chitra").forEach { (k, label) ->
                        Pick(label, ayanamsa == k) { if (ayanamsa != k) { ayanamsa = k; settings.ayanamsa = k; onCalculationChanged() } }
                    }
                }
                HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
                Setting(stringResource(R.string.nodes)) {
                    Pick(stringResource(R.string.mean_node), node == "mean") { if (node != "mean") { node = "mean"; settings.node = "mean"; onCalculationChanged() } }
                    Pick(stringResource(R.string.true_node), node == "true") { if (node != "true") { node = "true"; settings.node = "true"; onCalculationChanged() } }
                }
                HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
                Row(
                    Modifier.fillMaxWidth().heightIn(min = 64.dp)
                        .toggleable(value = weekdayHard, role = Role.Switch) { weekdayHard = it; settings.weekdayHard = it }
                        .padding(horizontal = 16.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Column(Modifier.weight(1f)) {
                        Text(stringResource(R.string.weekday_hard), style = MaterialTheme.typography.bodyLarge)
                        Text(stringResource(R.string.weekday_hard_sub), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    Switch(checked = weekdayHard, onCheckedChange = null, colors = SwitchDefaults.colors(checkedTrackColor = Palette.Accent))
                }
            }

            SectionLabel(stringResource(R.string.your_data))
            Text(stringResource(R.string.data_note), style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)

            SectionLabel(stringResource(R.string.about))
            Group {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text(engineVersion?.let { stringResource(R.string.engine_version, it) } ?: stringResource(R.string.engine_starting), style = MaterialTheme.typography.bodySmall)
                    TextButton(enabled = !running, onClick = {
                        running = true
                        scope.launch { speed = runCatching { onSpeedTest() }.getOrElse { it.toString() }; running = false }
                    }) { Text(stringResource(if (running) R.string.speed_running else R.string.speed_test)) }
                    speed?.let { Text(it, style = MaterialTheme.typography.bodySmall, fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace) }
                    Text(stringResource(R.string.licences), style = MaterialTheme.typography.titleMedium)
                    Text(stringResource(R.string.licences_body), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }
    }
}

@Composable
private fun Group(content: @Composable () -> Unit) {
    Surface(shape = RoundedCornerShape(16.dp), color = MaterialTheme.colorScheme.surface, border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)) {
        Column { content() }
    }
}

@OptIn(androidx.compose.foundation.layout.ExperimentalLayoutApi::class)
@Composable
private fun Setting(label: String, options: @Composable () -> Unit) {
    Column(Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(label, style = MaterialTheme.typography.bodyLarge)
        androidx.compose.foundation.layout.FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) { options() }
    }
}

@Composable
private fun Pick(label: String, selected: Boolean, onClick: () -> Unit) {
    FilterChip(
        selected = selected, onClick = onClick, label = { Text(label) }, modifier = Modifier.heightIn(min = 48.dp),
        colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep),
    )
}
