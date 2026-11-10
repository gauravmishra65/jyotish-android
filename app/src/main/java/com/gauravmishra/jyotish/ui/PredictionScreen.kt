package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
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
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.TodayPlace
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.engine.Engine
import org.json.JSONObject
import java.time.LocalDate

private val PERIODS = listOf("day", "week", "month", "year", "three")

/**
 * Predictions (v18): today, this week, this month, this year and the next three years for the chosen person, by life
 * area, each with stars, a short reading and the main reason. Tendencies only; the engine is app_predict.py.
 */
@Composable
fun PredictionScreen(profiles: List<Profile>, profile: Profile?, place: TodayPlace?, ayanamsa: String, node: String,
                     onSelect: (Profile) -> Unit, onAdd: () -> Unit, onReport: () -> Unit, onBack: () -> Unit) {
    val lang = currentLang()
    var period by rememberSaveable { mutableStateOf("day") }
    val cache = remember { mutableStateMapOf<String, JSONObject>() }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    val today = LocalDate.now().toString()
    val key = "${profile?.id}|$period|$today|${place?.name}"
    LaunchedEffect(key) {
        val p = profile ?: return@LaunchedEffect
        if (cache.containsKey(key)) return@LaunchedEffect
        busy = true; error = null
        val req = p.chartRequest(today, ayanamsa, node).put("period", period)
        place?.let { req.put("today_lat", it.lat).put("today_lon", it.lon).put("today_tz", it.tz) }
        try { cache[key] = JSONObject(Engine.predict(req)) } catch (t: Throwable) { error = t.message }
        busy = false
    }
    val o = cache[key]
    fun b(x: JSONObject?) = x?.optString(lang)?.ifEmpty { x.optString("en") } ?: ""
    Scaffold(containerColor = MaterialTheme.colorScheme.background, topBar = { BackBar(stringResource(R.string.pred_title), onBack, subtitle = profile?.name) }) { pad ->
        Column(Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 16.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)) {
            ProfileBar(profiles, profile, onSelect, onAdd)
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.testTag("pred_periods")) {
                items(PERIODS) { k ->
                    FilterChip(selected = period == k, onClick = { period = k }, label = { Text(stringResource(periodName(k))) },
                        modifier = Modifier.heightIn(min = 48.dp).testTag("pred_$k"),
                        colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep))
                }
            }
            if (profile == null) Text(stringResource(R.string.pick_profile_first))
            if (busy) LinearProgressIndicator(Modifier.fillMaxWidth(), color = Palette.Accent)
            error?.let { Text(stringResource(R.string.bt_failed, it)) }
            o?.let { r ->
                r.optJSONObject("best_time")?.let { Highlight(stringResource(R.string.pred_best_time), b(it)) }
                r.optJSONObject("best_days")?.let { Highlight(stringResource(R.string.pred_best_days), b(it)) }
                r.optJSONObject("dasha_note")?.let { Highlight(stringResource(R.string.pred_dasha), b(it)) }
                r.optJSONObject("lucky")?.let { l ->
                    Highlight(stringResource(R.string.pred_lucky), stringResource(R.string.pred_lucky_line, b(l.optJSONObject("colour")), l.optInt("number")))
                }
                val areas = r.optJSONArray("areas")
                if (areas != null) for (i in 0 until areas.length()) {
                    val a = areas.getJSONObject(i)
                    AreaCard(b(a.optJSONObject("title")), a.optInt("stars"), b(a.optJSONObject("reading")), b(a.optJSONObject("why")), a.optString("key"))
                }
                Text(b(r.optJSONObject("note")), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
                OutlinedButton(onClick = onReport, modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp)) { Text(stringResource(R.string.pred_more)) }
            }
        }
    }
}

@Composable
private fun Highlight(label: String, text: String) {
    Surface(shape = RoundedCornerShape(12.dp), color = Palette.AccentSoft, modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(label, style = MaterialTheme.typography.labelMedium, color = Palette.AccentDeep)
            Text(text, style = MaterialTheme.typography.bodyMedium)
        }
    }
}

@Composable
private fun AreaCard(title: String, stars: Int, reading: String, why: String, key: String) {
    val starText = "★".repeat(stars) + "☆".repeat(5 - stars)
    val desc = stringResource(R.string.pred_stars, stars)
    Surface(shape = RoundedCornerShape(14.dp), color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant), modifier = Modifier.fillMaxWidth().testTag("pred_area_$key")) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(title, style = MaterialTheme.typography.titleMedium, modifier = Modifier.weight(1f))
                Text(starText, color = Palette.Accent, style = MaterialTheme.typography.titleMedium, modifier = Modifier.semantics { contentDescription = desc })
            }
            Text(reading, style = MaterialTheme.typography.bodyMedium)
            Text(why, style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
        }
    }
}

private fun periodName(k: String) = when (k) {
    "day" -> R.string.pred_day
    "week" -> R.string.pred_week
    "month" -> R.string.pred_month
    "year" -> R.string.pred_year
    else -> R.string.pred_three
}
