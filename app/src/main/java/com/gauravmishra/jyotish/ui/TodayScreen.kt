package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowLeft
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.filled.Place
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.TodayPlace
import com.gauravmishra.jyotish.TodayState
import com.gauravmishra.jyotish.data.Choghadiya
import com.gauravmishra.jyotish.data.Place
import com.gauravmishra.jyotish.data.Places
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.TimeSpan
import com.gauravmishra.jyotish.data.TodayModel
import kotlinx.coroutines.delay
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

/**
 * Today: the day's panchang for a city, the good and avoided times (Choghadiya, Hora, Rahu Kaal and the rest), festivals
 * ahead, and for the chosen person their Tarabala, Chandrabala, dasha and the planets over their chart.
 */
@Composable
fun TodayScreen(
    profiles: List<Profile>,
    profile: Profile?,
    place: TodayPlace?,
    customPlace: Boolean,
    state: TodayState,
    date: LocalDate,
    onDate: (LocalDate) -> Unit,
    onSelect: (Profile) -> Unit,
    onAdd: () -> Unit,
    onPlace: (TodayPlace?) -> Unit,
    loadPlaces: suspend () -> Places,
    onBack: () -> Unit,
) {
    val lang = currentLang()
    var choosePlace by remember { mutableStateOf(false) }
    var showMonthly by rememberSaveable { mutableStateOf(false) }
    var allHora by rememberSaveable { mutableStateOf(false) }
    // the running period is marked; refresh once a minute
    var nowIso by remember { mutableStateOf("") }
    LaunchedEffect(place?.tz) {
        while (true) {
            val z = runCatching { ZoneId.of(place?.tz ?: "UTC") }.getOrDefault(ZoneId.systemDefault())
            nowIso = LocalDateTime.now(z).format(DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm"))
            delay(30_000)
        }
    }

    Scaffold(containerColor = MaterialTheme.colorScheme.background, topBar = { BackBar(stringResource(R.string.today_title), onBack) }) { pad ->
        Column(
            Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 8.dp).testTag("today"),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            // date and city
            Row(verticalAlignment = Alignment.CenterVertically) {
                IconButton(onClick = { onDate(date.minusDays(1)) }, modifier = Modifier.size(48.dp).testTag("today_prev")) {
                    Icon(Icons.AutoMirrored.Filled.KeyboardArrowLeft, contentDescription = stringResource(R.string.today_prev))
                }
                Column(Modifier.weight(1f), horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(date.format(DateTimeFormatter.ofPattern("EEEE, d MMMM yyyy", Locale.forLanguageTag(lang))),
                        style = MaterialTheme.typography.titleMedium, modifier = Modifier.testTag("today_date"))
                    if (date != LocalDate.now()) {
                        TextButton(onClick = { onDate(LocalDate.now()) }, modifier = Modifier.heightIn(min = 40.dp).testTag("today_back")) {
                            Text(stringResource(R.string.today_back_to_today), color = Palette.Accent)
                        }
                    }
                }
                IconButton(onClick = { onDate(date.plusDays(1)) }, modifier = Modifier.size(48.dp).testTag("today_next")) {
                    Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, contentDescription = stringResource(R.string.today_next))
                }
            }
            Surface(onClick = { choosePlace = true }, shape = RoundedCornerShape(12.dp), color = MaterialTheme.colorScheme.surface,
                border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline), modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp).testTag("today_place")) {
                Row(Modifier.padding(horizontal = 12.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Filled.Place, contentDescription = null, tint = Palette.Accent)
                    Column(Modifier.weight(1f).padding(start = 8.dp)) {
                        Text(stringResource(R.string.today_place), style = MaterialTheme.typography.labelMedium, color = Palette.Muted)
                        Text(place?.name ?: stringResource(R.string.today_choose_place), style = MaterialTheme.typography.titleMedium)
                    }
                    Text(stringResource(R.string.change_place), color = Palette.Accent)
                }
            }
            ProfileBar(profiles, profile, onSelect, onAdd)

            when (state) {
                is TodayState.Calculating -> Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    CircularProgressIndicator(Modifier.size(24.dp), color = Palette.Accent, strokeWidth = 2.dp)
                    Text(stringResource(R.string.calculating))
                }
                is TodayState.Failed -> Text(
                    if (state.message == "no-place") stringResource(R.string.today_no_place) else stringResource(R.string.today_failed, state.message.take(200)),
                    color = if (state.message == "no-place") Palette.Muted else MaterialTheme.colorScheme.error, modifier = Modifier.testTag("today_message"))
                is TodayState.Ready -> Day(state.model, profile, lang, nowIso, showMonthly, { showMonthly = it }, allHora, { allHora = !allHora })
            }
        }
    }

    if (choosePlace) {
        var chosen by remember { mutableStateOf<Place?>(null) }
        AlertDialog(
            onDismissRequest = { choosePlace = false },
            title = { Text(stringResource(R.string.today_choose_place)) },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    PlaceField(chosen, loadPlaces, { chosen = it }, tag = "today_place_field")
                    if (customPlace) {
                        TextButton(onClick = { choosePlace = false; onPlace(null) }, modifier = Modifier.heightIn(min = 48.dp).testTag("today_place_person")) {
                            Text(stringResource(R.string.today_use_person), color = Palette.Accent)
                        }
                    }
                }
            },
            confirmButton = {
                TextButton(enabled = chosen != null, onClick = {
                    chosen?.let { onPlace(TodayPlace(it.label, it.lat, it.lon, it.tz)) }
                    choosePlace = false
                }, modifier = Modifier.heightIn(min = 48.dp).testTag("today_place_ok")) { Text(stringResource(R.string.today_use_place)) }
            },
            dismissButton = { TextButton(onClick = { choosePlace = false }, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.cancel)) } },
        )
    }
}

@Composable
private fun Day(
    m: TodayModel, profile: Profile?, lang: String, nowIso: String,
    showMonthly: Boolean, onMonthly: (Boolean) -> Unit, allHora: Boolean, onAllHora: () -> Unit,
) {
    val isToday = nowIso.startsWith(m.date)
    val festToday = m.festivals.filter { it.date == m.date && (!it.monthly || it.key == "ekadashi_s" || it.key == "ekadashi_k" || it.key == "purnima" || it.key == "amavasya") }
    if (festToday.isNotEmpty()) {
        Text(stringResource(R.string.today_festival_today, festToday.joinToString(" · ") { it.name.of(lang) }),
            style = MaterialTheme.typography.titleMedium, color = Palette.AccentDeep,
            modifier = Modifier.fillMaxWidth().background(Palette.AccentSoft, RoundedCornerShape(12.dp)).padding(12.dp).testTag("today_festival"))
    }

    // the person's day
    m.person?.let { p ->
        Column(Modifier.fillMaxWidth().background(Palette.Night, RoundedCornerShape(18.dp)).padding(16.dp).testTag("today_person"),
            verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(stringResource(R.string.today_your_day, p.name.trim().substringBefore(" ")), style = MaterialTheme.typography.labelMedium, color = Palette.SaffronText)
            Text(p.guidance.of(lang), style = MaterialTheme.typography.titleMedium, color = Palette.NightTitle, modifier = Modifier.testTag("today_guidance"))
            NightLine(stringResource(R.string.today_tarabala), p.tara.of(lang) + " · " + stringResource(if (p.taraOk) R.string.today_ok else R.string.today_not_ok) +
                (p.taraChanges?.takeIf { isToday }?.let { " · " + stringResource(R.string.today_changes_at, it) } ?: ""))
            NightLine(stringResource(R.string.today_chandrabala), stringResource(R.string.today_house_from_moon, p.chandraHouse) + " · " +
                stringResource(if (p.chandraOk) R.string.today_ok else R.string.today_not_ok))
            NightLine(stringResource(R.string.today_moon), stringResource(R.string.today_moon_line, p.moonSign.of(lang), p.moonFromLagna))
            p.saturnPhase?.let { NightLine(stringResource(R.string.today_saturn), it.of(lang)) }
        }
    } ?: Text(if (profile == null) stringResource(R.string.today_no_person) else stringResource(R.string.today_waiting_chart, profile.name),
        style = MaterialTheme.typography.bodyMedium, color = Palette.Muted)

    // panchang
    Group(stringResource(R.string.today_panchang), "today_panchang") {
        Row2(stringResource(R.string.today_tithi), "${m.tithi.name.of(lang)} (${m.paksha.of(lang)})", m.tithi.ends?.let { stringResource(R.string.today_until, it) })
        Row2(stringResource(R.string.today_nakshatra), m.nakshatra.name.of(lang), m.nakshatra.ends?.let { stringResource(R.string.today_until, it) })
        Row2(stringResource(R.string.today_yoga), m.yoga.name.of(lang), m.yoga.ends?.let { stringResource(R.string.today_until, it) })
        Row2(stringResource(R.string.today_karana), m.karana.name.of(lang), m.karana.ends?.let { stringResource(R.string.today_until, it) })
        Row2(stringResource(R.string.today_weekday), m.weekday.of(lang), null)
        Row2(stringResource(R.string.today_moon_sign), m.moonSign.of(lang), null)
        Row2(stringResource(R.string.today_month), m.monthAmanta.of(lang) + " / " + m.monthPurnimanta.of(lang), null)
        Row2(stringResource(R.string.today_samvat), stringResource(R.string.today_samvat_line, m.vikram, m.shaka), null)
        Row2(stringResource(R.string.today_sun), "${m.sunrise ?: "–"} · ${m.sunset ?: "–"}", null)
        Row2(stringResource(R.string.today_moonrise), "${m.moonrise ?: "–"} · ${m.moonset ?: "–"}", null)
    }

    // good and avoided times
    if (m.periodsNote != null) {
        Text(m.periodsNote, color = Palette.Muted)
    } else {
        Group(stringResource(R.string.today_times), "today_times") {
            m.periods["brahma_muhurta"]?.let { Period(stringResource(R.string.today_brahma), it, true, nowIso) }
            m.periods["abhijit"]?.let {
                Period(stringResource(R.string.today_abhijit) + if (m.abhijitWednesday) " " + stringResource(R.string.today_abhijit_wed) else "",
                    it, !m.abhijitWednesday, nowIso)
            }
            m.periods["rahu_kalam"]?.let { Period(stringResource(R.string.today_rahu), it, false, nowIso, "today_rahu") }
            m.periods["yamaganda"]?.let { Period(stringResource(R.string.today_yamaganda), it, false, nowIso) }
            m.periods["gulika_kalam"]?.let { Period(stringResource(R.string.today_gulika), it, false, nowIso) }
        }
        Group(stringResource(R.string.today_chog_day), "today_chog_day") { m.choghadiyaDay.forEach { Chog(it, lang, nowIso) } }
        Group(stringResource(R.string.today_chog_night), "today_chog_night") { m.choghadiyaNight.forEach { Chog(it, lang, nowIso) } }
        Group(stringResource(R.string.today_hora), "today_hora") {
            val shown = if (allHora) m.hora else m.hora.filter { it.span.contains(nowIso) || !isToday }.take(if (isToday) 1 else 6)
            shown.forEach { h ->
                val now = h.span.contains(nowIso)
                Row2(h.lord.of(lang) + if (now) " · " + stringResource(R.string.today_now) else "", "${h.span.from} – ${h.span.to}", null, now)
            }
            TextButton(onClick = onAllHora, modifier = Modifier.heightIn(min = 48.dp).testTag("today_hora_all")) {
                Text(stringResource(if (allHora) R.string.today_show_less else R.string.today_show_all_hora), color = Palette.Accent)
            }
        }
    }

    // planets over the person's chart
    m.person?.let { p ->
        Group(stringResource(R.string.today_transits), "today_transits") {
            Row(Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp)) {
                listOf(R.string.today_col_planet to 1.3f, R.string.today_col_sign to 1.4f, R.string.today_col_lagna to 1f, R.string.today_col_moon to 1f).forEach { (s, w) ->
                    Text(stringResource(s), style = MaterialTheme.typography.labelMedium, color = Palette.Muted, modifier = Modifier.weight(w))
                }
            }
            p.transits.forEach { t ->
                Row(Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp)) {
                    Text(t.planet.of(lang) + if (t.retrograde) " (" + stringResource(R.string.today_retro) + ")" else "", modifier = Modifier.weight(1.3f))
                    Text(t.sign.of(lang) + " %.0f°".format(t.deg), modifier = Modifier.weight(1.4f))
                    Text("${t.fromLagna}", modifier = Modifier.weight(1f))
                    Text("${t.fromMoon}", modifier = Modifier.weight(1f))
                }
            }
            Text(stringResource(R.string.today_transits_note), style = MaterialTheme.typography.bodySmall, color = Palette.Muted,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp))
        }
    }

    // festivals and vrats
    Group(stringResource(R.string.today_festivals), "today_festivals") {
        Row(Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 4.dp), verticalAlignment = Alignment.CenterVertically) {
            Text(stringResource(R.string.today_show_monthly), modifier = Modifier.weight(1f))
            Switch(showMonthly, onMonthly, colors = SwitchDefaults.colors(checkedTrackColor = Palette.Accent), modifier = Modifier.testTag("today_monthly"))
        }
        val list = m.festivals.filter { showMonthly || !it.monthly }
        if (list.isEmpty()) Text(stringResource(R.string.today_no_festivals), color = Palette.Muted, modifier = Modifier.padding(16.dp))
        list.forEach { f ->
            Row2(prettyDate(f.date, lang), f.name.of(lang) + (f.time?.let { " · $it" } ?: ""), null, f.date == m.date)
        }
    }

    Text(stringResource(R.string.today_utc, m.tz, m.utcOffset) + " " + m.conventions.of(lang), style = MaterialTheme.typography.bodySmall,
        color = Palette.Muted, modifier = Modifier.testTag("today_conventions"))
}

@Composable
private fun NightLine(label: String, value: String) {
    Row {
        Text(label, style = MaterialTheme.typography.bodyMedium, color = Palette.SaffronText, modifier = Modifier.width(120.dp))
        Text(value, style = MaterialTheme.typography.bodyMedium, color = Palette.NightText, modifier = Modifier.weight(1f))
    }
}

@Composable
private fun Group(title: String, tag: String, content: @Composable () -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        SectionLabel(title)
        Surface(shape = RoundedCornerShape(16.dp), color = MaterialTheme.colorScheme.surface,
            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant), modifier = Modifier.fillMaxWidth().testTag(tag)) {
            Column(Modifier.padding(vertical = 6.dp)) { content() }
        }
    }
}

@Composable
private fun Row2(label: String, value: String, extra: String?, highlight: Boolean = false) {
    Row(Modifier.fillMaxWidth().background(if (highlight) Palette.AccentSoft else Color.Transparent).padding(horizontal = 16.dp, vertical = 8.dp),
        verticalAlignment = Alignment.Top) {
        Text(label, style = MaterialTheme.typography.bodyMedium, color = Palette.Muted, modifier = Modifier.weight(0.9f))
        Column(Modifier.weight(1.4f)) {
            Text(value, style = MaterialTheme.typography.bodyLarge, fontWeight = if (highlight) FontWeight.SemiBold else FontWeight.Normal)
            extra?.let { Text(it, style = MaterialTheme.typography.bodySmall, color = Palette.Muted) }
        }
    }
}

@Composable
private fun Period(label: String, s: TimeSpan, good: Boolean, nowIso: String, tag: String? = null) {
    val now = s.contains(nowIso)
    Row(Modifier.fillMaxWidth().background(if (now) Palette.AccentSoft else Color.Transparent).padding(horizontal = 16.dp, vertical = 10.dp)
        .let { if (tag != null) it.testTag(tag) else it }, verticalAlignment = Alignment.CenterVertically) {
        Dot(if (good) Palette.Good else Palette.Accent)
        Column(Modifier.weight(1f).padding(start = 10.dp)) {
            Text(label, style = MaterialTheme.typography.bodyLarge)
            Text(stringResource(if (good) R.string.today_good else R.string.today_avoid), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
        }
        Column(horizontalAlignment = Alignment.End) {
            Text("${s.from} – ${s.to}", style = MaterialTheme.typography.bodyLarge)
            if (now) Text(stringResource(R.string.today_now), style = MaterialTheme.typography.labelMedium, color = Palette.AccentDeep)
        }
    }
}

@Composable
private fun Chog(c: Choghadiya, lang: String, nowIso: String) {
    val now = c.span.contains(nowIso)
    val color = when (c.kind) { "good" -> Palette.Good; "neutral" -> Palette.Saffron; else -> Palette.Accent }
    Row(Modifier.fillMaxWidth().background(if (now) Palette.AccentSoft else Color.Transparent).padding(horizontal = 16.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically) {
        Dot(color)
        Text(c.name.of(lang), style = MaterialTheme.typography.bodyLarge, fontWeight = if (now) FontWeight.SemiBold else FontWeight.Normal,
            modifier = Modifier.weight(1f).padding(start = 10.dp))
        Text(stringResource(when (c.kind) { "good" -> R.string.today_chog_good; "neutral" -> R.string.today_chog_neutral; else -> R.string.today_chog_avoid }),
            style = MaterialTheme.typography.bodySmall, color = Palette.Muted, modifier = Modifier.padding(end = 10.dp))
        Text("${c.span.from} – ${c.span.to}" + if (now) " · " + stringResource(R.string.today_now) else "", style = MaterialTheme.typography.bodyMedium)
    }
}

@Composable
private fun Dot(color: Color) {
    Box(Modifier.size(10.dp).background(color, CircleShape))
}

/** The Home screen's entry to Today: the tithi and nakshatra, Rahu Kaal and the next festival. */
@Composable
fun TodayTile(state: TodayState?, onClick: () -> Unit) {
    val lang = currentLang()
    val m = (state as? TodayState.Ready)?.model
    Surface(onClick = onClick, shape = RoundedCornerShape(16.dp), color = Palette.AccentSoft, border = BorderStroke(1.dp, Palette.Accent),
        modifier = Modifier.fillMaxWidth().heightIn(min = 88.dp).testTag("home_today")) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(stringResource(R.string.today_title) + (m?.place?.substringBefore(",")?.let { " · $it" } ?: ""), style = MaterialTheme.typography.labelMedium, color = Palette.AccentDeep)
            if (state is TodayState.Failed && state.message != "no-place") {
                Text(stringResource(R.string.today_failed, state.message.take(120)), style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.error, modifier = Modifier.testTag("home_today_failed"))
            } else if (m == null) {
                Text(stringResource(R.string.today_sub), style = MaterialTheme.typography.titleMedium)
            } else {
                Text("${m.tithi.name.of(lang)} · ${m.nakshatra.name.of(lang)}", style = MaterialTheme.typography.titleMedium, modifier = Modifier.testTag("home_today_tithi"))
                m.periods["rahu_kalam"]?.let { Text(stringResource(R.string.today_rahu) + ": ${it.from} – ${it.to}", style = MaterialTheme.typography.bodyMedium) }
                m.person?.let { Text(it.guidance.of(lang), style = MaterialTheme.typography.bodySmall, color = Palette.Muted, maxLines = 2) }
                m.festivals.firstOrNull { !it.monthly }?.let {
                    Text(stringResource(R.string.today_next_festival, it.name.of(lang), prettyDate(it.date, lang)), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
                }
            }
        }
    }
}
