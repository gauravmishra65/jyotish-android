package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.parseDmy
import com.gauravmishra.jyotish.engine.Engine
import kotlinx.coroutines.launch
import org.json.JSONArray
import org.json.JSONObject

private val EVENT_KINDS = listOf("marriage", "child", "job", "property", "abroad", "education")

private data class LifeEvent(val kind: String, val date: String)

private sealed interface CheckState {
    data object Idle : CheckState
    data object Working : CheckState
    data class Done(val json: JSONObject) : CheckState
    data class Failed(val message: String) : CheckState
}

/**
 * Birth time check (engine_api.rectify): the time window around the recorded birth time cut into spans that keep the
 * same Lagna, Navamsa Lagna and Dashamsa Lagna, each with the dasha running on the person's dated life events and,
 * with events, a score against chance. It narrows the time; it never claims to prove one.
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun BirthTimeScreen(profiles: List<Profile>, profile: Profile?, ayanamsa: String, onSelect: (Profile) -> Unit, onAdd: () -> Unit, onBack: () -> Unit) {
    val lang = currentLang()
    val scope = rememberCoroutineScope()
    var window by remember { mutableStateOf(30) }
    val events = remember { mutableStateListOf<LifeEvent>() }
    var kind by remember { mutableStateOf("marriage") }
    var dateText by remember { mutableStateOf("") }
    var state by remember { mutableStateOf<CheckState>(CheckState.Idle) }

    Scaffold(containerColor = MaterialTheme.colorScheme.background, topBar = { BackBar(stringResource(R.string.bt_title), onBack, subtitle = profile?.name) }) { pad ->
        Column(
            Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            ProfileBar(profiles, profile, { onSelect(it); state = CheckState.Idle }, onAdd)
            Text(stringResource(R.string.bt_intro), style = MaterialTheme.typography.bodyMedium)
            profile?.let { Text(stringResource(R.string.bt_recorded, it.time), style = MaterialTheme.typography.titleMedium) }

            Text(stringResource(R.string.bt_window), style = MaterialTheme.typography.labelLarge)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf(15, 30, 60).forEach { w ->
                    FilterChip(selected = window == w, onClick = { window = w }, label = { Text(stringResource(R.string.bt_minutes, w)) },
                        modifier = Modifier.heightIn(min = 48.dp).testTag("bt_window_$w"),
                        colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep))
                }
            }

            Text(stringResource(R.string.bt_events), style = MaterialTheme.typography.labelLarge)
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                EVENT_KINDS.forEach { k ->
                    FilterChip(selected = kind == k, onClick = { kind = k }, label = { Text(stringResource(eventName(k))) },
                        modifier = Modifier.heightIn(min = 48.dp).testTag("bt_kind_$k"),
                        colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep))
                }
            }
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(dateText, { dateText = it }, label = { Text(stringResource(R.string.bt_date_hint)) }, singleLine = true,
                    modifier = Modifier.weight(1f).testTag("bt_date"))
                val d = parseDmy(dateText)
                OutlinedButton(enabled = d != null, onClick = { d?.let { events += LifeEvent(kind, it.toString()); dateText = "" } },
                    modifier = Modifier.heightIn(min = 52.dp).testTag("bt_add")) { Text(stringResource(R.string.bt_add)) }
            }
            events.forEachIndexed { i, e ->
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("${stringResource(eventName(e.kind))} · ${e.date}", style = MaterialTheme.typography.bodyMedium, modifier = Modifier.weight(1f))
                    TextButton(onClick = { events.removeAt(i) }, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.bt_remove)) }
                }
            }
            Text(stringResource(R.string.bt_events_note), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)

            Button(
                enabled = profile != null && state != CheckState.Working,
                onClick = {
                    val p = profile ?: return@Button
                    state = CheckState.Working
                    val req = JSONObject().put("date", p.date).put("time", p.time).put("lat", p.lat).put("lon", p.lon).put("tz", p.tz)
                        .put("gender", p.gender).put("ayanamsa", ayanamsa).put("window_min", window)
                        .put("events", JSONArray(events.map { JSONObject().put("kind", it.kind).put("date", it.date) }))
                    scope.launch {
                        state = try { CheckState.Done(JSONObject(Engine.rectify(req))) } catch (t: Throwable) { CheckState.Failed(t.message ?: t.toString()) }
                    }
                },
                modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp).testTag("bt_run"),
            ) { Text(stringResource(R.string.bt_run)) }

            when (val s = state) {
                CheckState.Working -> { Text(stringResource(R.string.bt_working)); LinearProgressIndicator(Modifier.fillMaxWidth(), color = Palette.Accent) }
                is CheckState.Failed -> Text(stringResource(R.string.bt_failed, s.message))
                is CheckState.Done -> Results(s.json, lang)
                CheckState.Idle -> {}
            }
        }
    }
}

@Composable
private fun Results(o: JSONObject, lang: String) {
    val hi = lang == "hi"
    val signs = o.optJSONObject("signs_hi")
    val planets = o.optJSONObject("planets_hi")
    fun sign(s: String) = if (hi) signs?.optString(s, s) ?: s else s
    fun planet(s: String) = if (hi) planets?.optString(s, s) ?: s else s
    val segs = o.getJSONArray("segments")
    val scored = o.optJSONArray("scored") ?: JSONArray()
    val score = (0 until scored.length()).map { scored.getJSONObject(it) }.filter { it.has("p") }.associateBy { it.optString("from") }
    val best = score.values.minOfOrNull { it.optDouble("p", 1.0) }
    Column(Modifier.testTag("bt_results"), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(stringResource(R.string.bt_results, segs.length()), style = MaterialTheme.typography.titleMedium)
        for (i in 0 until segs.length()) {
            val s = segs.getJSONObject(i)
            val sc = score[s.optString("from")]
            val top = sc != null && best != null && sc.optDouble("p", 1.0) == best && best < 0.5
            Surface(shape = RoundedCornerShape(12.dp), color = if (top) Palette.AccentSoft else MaterialTheme.colorScheme.surface,
                border = BorderStroke(1.dp, if (s.optBoolean("contains_recorded")) Palette.Accent else MaterialTheme.colorScheme.outlineVariant),
                modifier = Modifier.fillMaxWidth().testTag("bt_seg_$i")) {
                Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text("${s.optString("from")} – ${s.optString("to")}" + if (s.optBoolean("contains_recorded")) "  ·  ${stringResource(R.string.bt_recorded_mark)}" else "",
                        style = MaterialTheme.typography.titleSmall)
                    Text(stringResource(R.string.bt_lagnas, sign(s.optString("lagna")), sign(s.optString("d9")), sign(s.optString("d10"))), style = MaterialTheme.typography.bodyMedium)
                    val ev = s.optJSONArray("events") ?: JSONArray()
                    for (j in 0 until ev.length()) {
                        val e = ev.getJSONObject(j)
                        Text("${stringResource(eventName(e.optString("kind")))} ${e.optString("date")}: ${planet(e.optString("mahadasha"))} – ${planet(e.optString("antardasha"))}",
                            style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
                    }
                    sc?.let {
                        Text(stringResource(R.string.bt_score, it.optInt("hits"), it.optDouble("expected"), (it.optDouble("p") * 100).toInt()),
                            style = MaterialTheme.typography.bodySmall, color = if (top) Palette.AccentDeep else Palette.Muted)
                    }
                }
            }
        }
        o.optJSONObject("note")?.let { Text(it.optString(if (hi) "hi" else "en"), style = MaterialTheme.typography.bodySmall, color = Palette.Muted) }
    }
}

private fun eventName(k: String) = when (k) {
    "marriage" -> R.string.bt_ev_marriage
    "child" -> R.string.bt_ev_child
    "job" -> R.string.bt_ev_job
    "property" -> R.string.bt_ev_property
    "abroad" -> R.string.bt_ev_abroad
    else -> R.string.bt_ev_education
}
