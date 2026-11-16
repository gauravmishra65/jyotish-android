package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.ChartModel
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.gocharOn
import com.gauravmishra.jyotish.engine.Engine
import org.json.JSONObject
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

private val STAMP: DateTimeFormatter = DateTimeFormatter.ofPattern("dd MMM yyyy, HH:mm")

/**
 * Chart through time (v26): the birth chart with the sky of any chosen moment drawn over it, and buttons that step the
 * moment by an hour, a day, a month or a year. Both charts are on the one square: the birth planets in dark, the
 * moment's planets under them in the accent colour.
 */
@Composable
fun TimeTravelScreen(profiles: List<Profile>, profile: Profile?, style: String, ayanamsa: String, node: String,
                     onSelect: (Profile) -> Unit, onAdd: () -> Unit, onBack: () -> Unit) {
    val lang = currentLang()
    var stepMinutes by rememberSaveable { mutableStateOf(0L) }
    var natal by remember { mutableStateOf<ChartModel?>(null) }
    var moment by remember { mutableStateOf<ChartModel?>(null) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    val at = remember(stepMinutes) { LocalDateTime.now().withSecond(0).withNano(0).plusMinutes(stepMinutes) }

    LaunchedEffect(profile?.id, stepMinutes) {
        val p = profile ?: return@LaunchedEffect
        busy = true; error = null
        try {
            if (natal == null) {
                natal = ChartModel.parse(Engine.chart(p.chartRequest(java.time.LocalDate.now().toString(), ayanamsa, node)))
            }
            val req = JSONObject().put("name", p.name).put("date", at.toLocalDate().toString())
                .put("time", "%02d:%02d".format(at.hour, at.minute))
                .put("lat", p.lat).put("lon", p.lon).put("tz", p.tz).put("gender", p.gender)
                .put("ayanamsa", ayanamsa).put("node", node).put("modules", "vedic")
            moment = ChartModel.parse(Engine.chart(req))
        } catch (t: Throwable) { error = t.message }
        busy = false
    }

    Scaffold(containerColor = MaterialTheme.colorScheme.background,
        topBar = { BackBar(stringResource(R.string.tt_title), onBack, subtitle = profile?.name) }) { pad ->
        Column(Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)) {
            ProfileBar(profiles, profile, onSelect, onAdd)
            if (profile == null) {
                Text(stringResource(R.string.pick_profile_first), style = MaterialTheme.typography.bodyLarge)
                return@Column
            }
            Text(stringResource(R.string.tt_intro), style = MaterialTheme.typography.bodyMedium, color = Palette.Muted)
            Text(at.format(STAMP), style = MaterialTheme.typography.titleMedium, modifier = Modifier.testTag("tt_moment"))
            if (busy) LinearProgressIndicator(Modifier.fillMaxWidth())
            error?.let { Text(stringResource(R.string.chart_failed, it), style = MaterialTheme.typography.bodyMedium) }

            listOf(
                listOf(-60L to R.string.tt_hour_back, 60L to R.string.tt_hour_on),
                listOf(-1440L to R.string.tt_day_back, 1440L to R.string.tt_day_on),
                listOf(-43200L to R.string.tt_month_back, 43200L to R.string.tt_month_on),
                listOf(-525600L to R.string.tt_year_back, 525600L to R.string.tt_year_on),
            ).forEach { row ->
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    row.forEach { (delta, label) ->
                        OutlinedButton(onClick = { stepMinutes += delta },
                            modifier = Modifier.weight(1f).heightIn(min = 48.dp).testTag("tt_$delta")) { Text(stringResource(label)) }
                    }
                }
            }
            OutlinedButton(onClick = { stepMinutes = 0L }, modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp).testTag("tt_now")) {
                Text(stringResource(R.string.tt_now))
            }

            val n = natal
            if (n != null) {
                KundliChart(n, style, lang,
                    chartDescription(n, lang, stringResource(R.string.house_word), stringResource(R.string.empty_word)),
                    Modifier.padding(horizontal = 4.dp).testTag("tt_chart"), overlay = moment?.gocharOn(n))
                Text(stringResource(R.string.tt_legend), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
            }
        }
    }
}
