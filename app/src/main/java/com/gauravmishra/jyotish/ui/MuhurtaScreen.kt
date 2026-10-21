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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.MuhurtaQuery
import com.gauravmishra.jyotish.MuhurtaState
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.DMY
import com.gauravmishra.jyotish.data.MuhurtaResult
import com.gauravmishra.jyotish.data.MuhurtaWindow
import com.gauravmishra.jyotish.data.Place
import com.gauravmishra.jyotish.data.Places
import com.gauravmishra.jyotish.data.Profile
import java.time.LocalDate
import java.time.format.ResolverStyle
import java.time.temporal.ChronoUnit

private val EVENTS = listOf(
    "marriage" to R.string.event_marriage, "griha_pravesh" to R.string.event_griha_pravesh,
    "vehicle" to R.string.event_vehicle, "business" to R.string.event_business,
)

/** A date typed as DD-MM-YYYY, with no upper limit (muhurta dates are in the future). */
private fun parseFuture(s: String): LocalDate? = try {
    LocalDate.parse(s.trim().replace('/', '-').replace('.', '-'), DMY.withResolverStyle(ResolverStyle.STRICT))
} catch (e: Exception) {
    null
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun MuhurtaScreen(
    profiles: List<Profile>,
    last: MuhurtaQuery?,
    state: MuhurtaState,
    loadPlaces: suspend () -> Places,
    onFind: (MuhurtaQuery) -> Unit,
    onHome: () -> Unit,
    onFeature: (Feature) -> Unit,
) {
    val lang = currentLang()
    val today = LocalDate.now()
    var event by rememberSaveable { mutableStateOf(last?.event ?: "marriage") }
    var fromText by rememberSaveable { mutableStateOf(LocalDate.parse(last?.from ?: today.toString()).format(DMY)) }
    var toText by rememberSaveable { mutableStateOf(LocalDate.parse(last?.to ?: today.plusMonths(3).toString()).format(DMY)) }
    var place by remember { mutableStateOf(last?.let { Place(it.place, "", "", it.lat, it.lon, it.tz, 0, emptyList()) }) }
    var people by rememberSaveable { mutableStateOf(last?.people ?: profiles.take(2).map { it.id }) }
    var showForm by rememberSaveable { mutableStateOf(state !is MuhurtaState.Ready) }
    var byDay by rememberSaveable { mutableStateOf(false) }
    var error by remember { mutableStateOf<Int?>(null) }

    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        topBar = { BackBar(stringResource(R.string.feature_muhurta), onHome) },
        bottomBar = { BottomNav(current = Feature.MUHURTA, onHome = onHome, onFeature = onFeature) },
    ) { pad ->
        Column(
            Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 4.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            if (showForm || state is MuhurtaState.Idle) {
                Text(stringResource(R.string.mu_event), style = MaterialTheme.typography.titleMedium)
                FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    EVENTS.forEach { (k, label) -> Chip(stringResource(label), event == k) { event = k } }
                }
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    OutlinedTextField(fromText, { fromText = it.take(10) }, label = { Text(stringResource(R.string.mu_from)) }, singleLine = true,
                        placeholder = { Text(stringResource(R.string.date_hint)) }, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        modifier = Modifier.weight(1f).testTag("mu_from"))
                    OutlinedTextField(toText, { toText = it.take(10) }, label = { Text(stringResource(R.string.mu_to)) }, singleLine = true,
                        placeholder = { Text(stringResource(R.string.date_hint)) }, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        modifier = Modifier.weight(1f).testTag("mu_to"))
                }
                Text(stringResource(R.string.mu_place), style = MaterialTheme.typography.titleMedium)
                if (place == null && profiles.isNotEmpty()) {
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        profiles.distinctBy { it.place }.take(3).forEach { p ->
                            Chip(stringResource(R.string.mu_use_birthplace, p.place.substringBefore(",")), false) {
                                place = Place(p.place, "", "", p.lat, p.lon, p.tz, 0, emptyList())
                            }
                        }
                    }
                }
                PlaceField(place, loadPlaces, { place = it }, tag = "mu_place")
                if (profiles.isNotEmpty()) {
                    Text(stringResource(R.string.mu_people), style = MaterialTheme.typography.titleMedium)
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        profiles.forEach { p ->
                            Chip(p.name, p.id in people) {
                                people = if (p.id in people) people - p.id else (people + p.id).takeLast(2)
                            }
                        }
                    }
                    Text(stringResource(R.string.mu_people_help), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
                }
                error?.let { Text(stringResource(it), color = MaterialTheme.colorScheme.error) }
                Button(
                    onClick = {
                        val f = parseFuture(fromText); val t = parseFuture(toText); val pl = place
                        error = when {
                            f == null || t == null || t.isBefore(f) || ChronoUnit.DAYS.between(f, t) > 400 -> R.string.mu_err_dates
                            pl == null -> R.string.mu_err_place
                            else -> null
                        }
                        if (error == null) {
                            showForm = false
                            onFind(MuhurtaQuery(event, f.toString(), t.toString(), pl!!.label, pl.lat, pl.lon, pl.tz, people))
                        }
                    },
                    modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp).testTag("mu_find"), shape = RoundedCornerShape(28.dp),
                ) { Text(stringResource(R.string.mu_find), style = MaterialTheme.typography.labelLarge) }
            } else {
                Surface(
                    onClick = { showForm = true }, shape = RoundedCornerShape(16.dp), color = MaterialTheme.colorScheme.surface,
                    border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
                ) {
                    Column(Modifier.fillMaxWidth().padding(14.dp), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                        Text(stringResource(EVENTS.first { it.first == event }.second), style = MaterialTheme.typography.titleMedium)
                        Text("${prettyDate(parseFuture(fromText).toString(), lang)} – ${prettyDate(parseFuture(toText).toString(), lang)} · ${place?.label?.substringBefore(",") ?: ""}",
                            style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
                        Text(stringResource(R.string.mu_edit), style = MaterialTheme.typography.labelLarge, color = Palette.Accent)
                    }
                }
            }

            when (state) {
                is MuhurtaState.Searching -> {
                    LinearProgressIndicator(Modifier.fillMaxWidth(), color = Palette.Accent)
                    Text(stringResource(R.string.mu_searching), style = MaterialTheme.typography.bodySmall)
                }
                is MuhurtaState.Failed -> Text(stringResource(R.string.chart_failed, state.message))
                is MuhurtaState.Ready -> if (!showForm) Results(state.result, lang, byDay) { byDay = it }
                else -> {}
            }
        }
    }
}

@Composable
private fun Chip(label: String, selected: Boolean, onClick: () -> Unit) {
    FilterChip(selected = selected, onClick = onClick, label = { Text(label) }, modifier = Modifier.heightIn(min = 40.dp),
        colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep))
}

@Composable
private fun Results(r: MuhurtaResult, lang: String, byDay: Boolean, onView: (Boolean) -> Unit) {
    val days = r.byDay
    if (days.isEmpty()) {
        Text(stringResource(R.string.mu_none), style = MaterialTheme.typography.bodyLarge)
    } else {
        Text(stringResource(R.string.mu_found, days.size), style = MaterialTheme.typography.titleMedium, modifier = Modifier.testTag("mu_found"))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Chip(stringResource(R.string.mu_view_best), !byDay) { onView(false) }
            Chip(stringResource(R.string.mu_view_days), byDay) { onView(true) }
        }
        if (!byDay) {
            r.best(10).forEach { WindowCard(it, lang, showDate = true) }
        } else {
            days.forEach { (date, ws) ->
                Text(prettyDate(date, lang) + " · " + (if (lang == "hi") ws.first().weekdayHi ?: ws.first().weekday else ws.first().weekday),
                    style = MaterialTheme.typography.titleMedium, modifier = Modifier.padding(top = 6.dp))
                ws.forEach { WindowCard(it, lang, showDate = false) }
            }
        }
    }
    Text(stringResource(R.string.mu_confirm), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun WindowCard(w: MuhurtaWindow, lang: String, showDate: Boolean) {
    val hi = lang == "hi"
    Surface(shape = RoundedCornerShape(16.dp), color = MaterialTheme.colorScheme.surface, border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)) {
        Column(Modifier.fillMaxWidth().padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row {
                if (showDate) Text(prettyDate(w.date, lang) + " · " + (if (hi) w.weekdayHi ?: w.weekday else w.weekday.take(3)),
                    style = MaterialTheme.typography.titleMedium, modifier = Modifier.weight(1f))
                else Row(Modifier.weight(1f)) {}
                Text(stringResource(R.string.mu_time_range, w.start.takeLast(5), w.end.takeLast(5)), style = MaterialTheme.typography.titleMedium, color = Palette.AccentDeep)
            }
            Text(stringResource(R.string.mu_window_line, if (hi) w.nakshatraHi ?: w.nakshatra else w.nakshatra,
                stringResource(if (w.paksha == "Krishna") R.string.krishna else R.string.shukla), w.tithiInPaksha,
                if (hi) w.lagnaHi ?: w.lagna else w.lagna), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
            val supports = (if (hi) w.supportsHi else null) ?: w.supports
            val cautions = (if (hi) w.cautionsHi else null) ?: w.cautions
            FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                supports.forEach { Tag(it, Color(0xFFE6F2E8), Color(0xFF24502C)) }
                if (cautions.isEmpty()) Tag(stringResource(R.string.mu_no_cautions), Color(0xFFEFEBE4), Color(0xFF3F3B35))
                cautions.forEach { Tag(it, Palette.CautionBg, Color(0xFF6B4A00)) }
            }
        }
    }
}

@Composable
private fun Tag(text: String, bg: Color, fg: Color) {
    Text(text, style = MaterialTheme.typography.labelMedium, color = fg,
        modifier = Modifier.background(bg, RoundedCornerShape(10.dp)).padding(horizontal = 8.dp, vertical = 3.dp))
}
