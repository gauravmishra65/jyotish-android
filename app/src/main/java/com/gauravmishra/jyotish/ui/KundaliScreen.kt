package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
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
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.ChartState
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.Meanings
import com.gauravmishra.jyotish.data.ChartModel
import com.gauravmishra.jyotish.data.Planet
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.SIGNS
import com.gauravmishra.jyotish.data.Yoga
import java.time.LocalDate
import kotlin.math.roundToInt

private sealed interface Detail {
    data class OfPlanet(val p: Planet) : Detail
    data class OfYoga(val y: Yoga) : Detail
}

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun KundaliScreen(
    profiles: List<Profile>,
    profile: Profile?,
    chart: ChartState?,
    style: String,
    onSelect: (Profile) -> Unit,
    onStyle: (String) -> Unit,
    onHome: () -> Unit,
    onFeature: (Feature) -> Unit,
) {
    val lang = currentLang()
    val model = (chart as? ChartState.Ready)?.model
    var tab by rememberSaveable { mutableStateOf(0) }
    var detail by remember { mutableStateOf<Detail?>(null) }

    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        topBar = {
            BackBar(
                profile?.name ?: stringResource(R.string.feature_kundali), onHome,
                subtitle = model?.let { stringResource(R.string.kundali_subtitle, Names.of(it.lagna.sign, lang), degMin(it.lagna.dms), ayanamsaLabel(it.ayanamsa, lang)) },
            )
        },
        bottomBar = { BottomNav(current = Feature.KUNDALI, onHome = onHome, onFeature = onFeature) },
    ) { pad ->
        Column(Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState())) {
            Column(Modifier.padding(horizontal = 20.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                if (profiles.size > 1) {
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        profiles.forEach { p ->
                            FilterChip(selected = p.id == profile?.id, onClick = { onSelect(p) }, label = { Text(p.name) },
                                colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep))
                        }
                    }
                }
                when {
                    profile == null -> { Text(stringResource(R.string.pick_profile_first), style = MaterialTheme.typography.bodyLarge); return@Column }
                    chart is ChartState.Failed -> { Text(stringResource(R.string.chart_failed, chart.message)); return@Column }
                    model == null -> { Text(stringResource(R.string.calculating)); return@Column }
                }
                val m = model!!
                Row(Modifier.fillMaxWidth().background(MaterialTheme.colorScheme.surfaceVariant, RoundedCornerShape(12.dp)).padding(4.dp)) {
                    StyleButton(stringResource(R.string.north_indian), style == "north", Modifier.weight(1f)) { onStyle("north") }
                    StyleButton(stringResource(R.string.south_indian), style == "south", Modifier.weight(1f)) { onStyle("south") }
                }
                KundliChart(
                    m, style, lang,
                    chartDescription(m, lang, stringResource(R.string.house_word), stringResource(R.string.empty_word)),
                    Modifier.padding(horizontal = 4.dp).testTag("chart"),
                )
                Warnings(m)
            }

            if (model != null) {
                val titles = listOf(R.string.tab_planets, R.string.tab_dashas, R.string.tab_yogas, R.string.tab_strength)
                TabBar(titles.map { stringResource(it) }, tab) { tab = it }
                Column(Modifier.padding(horizontal = 20.dp, vertical = 8.dp)) {
                    when (tab) {
                        0 -> PlanetsTab(model, lang) { detail = Detail.OfPlanet(it) }
                        1 -> DashasTab(model, lang)
                        2 -> YogasTab(model, lang) { detail = Detail.OfYoga(it) }
                        else -> StrengthTab(model, lang)
                    }
                }
            }
        }
    }

    detail?.let { d ->
        ModalBottomSheet(onDismissRequest = { detail = null }, sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true),
            containerColor = MaterialTheme.colorScheme.surface) {
            Column(Modifier.padding(horizontal = 22.dp).padding(bottom = 28.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                when (d) {
                    is Detail.OfPlanet -> PlanetDetail(d.p, (chart as? ChartState.Ready)?.model, lang)
                    is Detail.OfYoga -> YogaDetail(d.y, lang)
                }
                OutlinedButton(onClick = { detail = null }, modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp)) { Text(stringResource(R.string.close)) }
            }
        }
    }
}

/** Four equal tabs with an underline; no inner padding, so labels fit on narrow phones. */
@Composable
private fun TabBar(labels: List<String>, selected: Int, onSelect: (Int) -> Unit) {
    Column(Modifier.padding(top = 10.dp)) {
        Row(Modifier.fillMaxWidth().padding(horizontal = 8.dp).selectableGroup()) {
            labels.forEachIndexed { i, label ->
                Column(
                    Modifier.weight(1f).heightIn(min = 48.dp)
                        .selectable(selected = i == selected, role = Role.Tab, onClick = { onSelect(i) }),
                    horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center,
                ) {
                    Text(label, maxLines = 1, style = MaterialTheme.typography.bodyMedium,
                        fontWeight = if (i == selected) FontWeight.SemiBold else FontWeight.Normal,
                        color = if (i == selected) Palette.Ink else Palette.Muted, modifier = Modifier.padding(vertical = 12.dp))
                    Box(Modifier.fillMaxWidth(0.7f).height(3.dp).background(if (i == selected) Palette.Accent else Color.Transparent, RoundedCornerShape(2.dp)))
                }
            }
        }
        HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
    }
}

/** 0°59'27" as 0°59′. */
fun degMin(dms: String): String = Regex("^(\\d+°\\d+)").find(dms)?.groupValues?.get(1)?.plus("′") ?: dms

private fun ayanamsaLabel(a: String, lang: String) = if (lang == "hi") when (a) {
    "lahiri" -> "लाहिरी"; "raman" -> "रमन"; "krishnamurti" -> "कृष्णमूर्ति"; "true_chitra" -> "ट्रू चित्रा"; else -> a
} else when (a) {
    "lahiri" -> "Lahiri"; "raman" -> "Raman"; "krishnamurti" -> "KP"; "true_chitra" -> "True Chitra"; else -> a
}

@Composable
private fun StyleButton(label: String, selected: Boolean, modifier: Modifier, onClick: () -> Unit) {
    Surface(
        onClick = onClick, shape = RoundedCornerShape(9.dp),
        color = if (selected) MaterialTheme.colorScheme.surface else Color.Transparent,
        modifier = modifier.heightIn(min = 40.dp),
    ) {
        Box(contentAlignment = Alignment.Center) {
            Text(label, style = MaterialTheme.typography.bodyMedium, fontWeight = if (selected) FontWeight.SemiBold else FontWeight.Normal,
                color = if (selected) Palette.Ink else Palette.Muted, modifier = Modifier.padding(vertical = 10.dp))
        }
    }
}

/** The engine's warnings that matter on this screen, in plain words and in the chosen language. */
@Composable
private fun Warnings(m: ChartModel) {
    val lines = buildList {
        if (m.warnings.any { "nakshatra boundary" in it }) add(stringResource(R.string.warn_moon_boundary))
        if (m.warnings.any { it.startsWith("Lagna sign flips") }) add(stringResource(R.string.warn_lagna_flip))
        m.warnings.firstOrNull { "alternative ayanamsas" in it }?.let { w ->
            Regex("^(\\d+) placement").find(w)?.groupValues?.get(1)?.toIntOrNull()?.let { add(stringResource(R.string.warn_ayanamsa, it)) }
        }
    }
    lines.forEach { text ->
        Surface(shape = RoundedCornerShape(12.dp), color = Palette.CautionBg, border = BorderStroke(1.dp, Color(0xFFE8C98E))) {
            Text("⚠  $text", style = MaterialTheme.typography.bodySmall, color = Palette.CautionText, modifier = Modifier.padding(horizontal = 12.dp, vertical = 10.dp))
        }
    }
}

@Composable
private fun PlanetsTab(m: ChartModel, lang: String, onOpen: (Planet) -> Unit) {
    Row(Modifier.fillMaxWidth().padding(vertical = 10.dp), verticalAlignment = Alignment.CenterVertically) {
        Text(stringResource(R.string.lagna_label), fontWeight = FontWeight.SemiBold, modifier = Modifier.width(84.dp))
        Column(Modifier.weight(1f)) {
            Text("${Names.of(m.lagna.sign, lang)} ${m.lagna.dms}", style = MaterialTheme.typography.bodyMedium)
            Text("${Names.nakshatra(m.lagna.nakshatra, lang)} ${m.lagna.pada}", style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
        }
    }
    HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
    m.planets.forEach { p ->
        Row(
            Modifier.fillMaxWidth().heightIn(min = 56.dp).clickable(role = Role.Button) { onOpen(p) }.padding(vertical = 8.dp).testTag("planet_${p.name}"),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(Names.of(p.name, lang), fontWeight = FontWeight.SemiBold, modifier = Modifier.width(84.dp))
            Column(Modifier.weight(1f)) {
                Text("${Names.of(p.sign, lang)} ${p.dms}" + if (p.retrograde && p.name != "Rahu" && p.name != "Ketu") " · ${stringResource(R.string.retrograde)}" else "",
                    style = MaterialTheme.typography.bodyMedium)
                Text(stringResource(R.string.nak_house, Names.nakshatra(p.nakshatra, lang), p.pada, p.house), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
            }
            val good = p.dignity in setOf("exalted", "own sign", "moolatrikona")
            val bad = p.dignity in setOf("debilitated", "enemy's sign")
            Text(Names.dignity(p.dignity, lang), style = MaterialTheme.typography.labelMedium,
                color = when { good -> Palette.Good; bad -> Color(0xFF9A3B1B); else -> Palette.Muted },
                fontWeight = if (good || bad) FontWeight.SemiBold else FontWeight.Normal, modifier = Modifier.widthIn(max = 96.dp))
        }
        HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
    }
}

@Composable
private fun DashasTab(m: ChartModel, lang: String) {
    var open by rememberSaveable { mutableStateOf(m.currentMaha + "@" + m.mahadashas.firstOrNull { it.lord == m.currentMaha && isNow(it.start, it.end) }?.start) }
    m.mahadashas.forEach { md ->
        val key = md.lord + "@" + md.start
        val current = md.lord == m.currentMaha && isNow(md.start, md.end)
        Column(Modifier.fillMaxWidth()) {
            Row(
                Modifier.fillMaxWidth().heightIn(min = 52.dp).clickable(role = Role.Button) { open = if (open == key) "" else key }.padding(vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(Names.of(md.lord, lang), style = MaterialTheme.typography.titleMedium, modifier = Modifier.width(96.dp),
                    color = if (current) Palette.AccentDeep else Palette.Ink)
                Text(stringResource(R.string.date_range, prettyDate(md.start, lang), prettyDate(md.end, lang)), style = MaterialTheme.typography.bodySmall,
                    color = Palette.Muted, modifier = Modifier.weight(1f))
                if (current) NowChip()
                Text(if (open == key) "▴" else "▾", color = Palette.Muted, modifier = Modifier.padding(start = 8.dp))
            }
            if (open == key) {
                Column(Modifier.fillMaxWidth().background(Palette.Ground, RoundedCornerShape(10.dp)).padding(horizontal = 12.dp, vertical = 6.dp)) {
                    Text(stringResource(R.string.antardashas), style = MaterialTheme.typography.labelMedium, color = Palette.Muted, modifier = Modifier.padding(vertical = 4.dp))
                    md.antardashas.forEach { a ->
                        val now = current && a.start == m.currentAntar.start
                        Row(Modifier.fillMaxWidth().padding(vertical = 5.dp), verticalAlignment = Alignment.CenterVertically) {
                            Text(Names.of(a.lord, lang), modifier = Modifier.width(84.dp), fontWeight = if (now) FontWeight.SemiBold else FontWeight.Normal,
                                color = if (now) Palette.AccentDeep else Palette.Ink)
                            Text(stringResource(R.string.date_range, prettyDate(a.start, lang), prettyDate(a.end, lang)), style = MaterialTheme.typography.bodySmall,
                                color = Palette.Muted, modifier = Modifier.weight(1f))
                            if (now) NowChip()
                        }
                    }
                }
            }
            HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
        }
    }
}

private fun isNow(start: String, end: String): Boolean {
    val t = LocalDate.now().toString()
    return start <= t && t < end
}

@Composable
private fun NowChip() {
    Text(stringResource(R.string.now_label), style = MaterialTheme.typography.labelMedium, color = Palette.AccentDeep, fontWeight = FontWeight.SemiBold,
        modifier = Modifier.background(Palette.AccentSoft, RoundedCornerShape(10.dp)).padding(horizontal = 8.dp, vertical = 2.dp))
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun YogasTab(m: ChartModel, lang: String, onOpen: (Yoga) -> Unit) {
    if (m.yogas.isEmpty()) { Text(stringResource(R.string.no_yogas)); return }
    Text(stringResource(R.string.rare_first), style = MaterialTheme.typography.bodySmall, color = Palette.Muted, modifier = Modifier.padding(vertical = 6.dp))
    m.yogas.forEach { y ->
        Column(
            Modifier.fillMaxWidth().heightIn(min = 48.dp).clickable(role = Role.Button) { onOpen(y) }.padding(vertical = 10.dp).testTag("yoga_${y.id}"),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(Names.yoga(y.name, lang), style = MaterialTheme.typography.titleMedium)
            Text(Names.yogaCategory(y.category, lang), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
            FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                y.strength?.let { Pill(strengthLabel(it), it == "strong") }
                Pill(toneLabel(y.tone), false)
                y.baseRate?.let { Pill(rateLabel(it), false) }
            }
        }
        HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
    }
}

@Composable
private fun rateLabel(rate: Double): String {
    val pct = (rate * 100).roundToInt()
    return if (pct < 1) stringResource(R.string.yoga_rate_lt1) else stringResource(R.string.yoga_rate, pct)
}

@Composable
private fun strengthLabel(s: String) = stringResource(when (s) { "strong" -> R.string.strength_strong; "moderate" -> R.string.strength_moderate; else -> R.string.strength_weak })

@Composable
private fun toneLabel(t: String) = stringResource(when (t) { "supportive" -> R.string.tone_supportive; "demanding" -> R.string.tone_demanding; else -> R.string.tone_mixed })

@Composable
private fun Pill(text: String, good: Boolean) {
    Text(text, style = MaterialTheme.typography.labelMedium, color = if (good) Color(0xFF24502C) else Color(0xFF3F3B35),
        modifier = Modifier.background(if (good) Color(0xFFE6F2E8) else Color(0xFFEFEBE4), RoundedCornerShape(10.dp)).padding(horizontal = 8.dp, vertical = 3.dp))
}

@Composable
private fun StrengthTab(m: ChartModel, lang: String) {
    Text(stringResource(R.string.shadbala_title), style = MaterialTheme.typography.titleMedium, modifier = Modifier.padding(vertical = 8.dp).semantics { heading() })
    m.strengths.forEach { s ->
        Column(Modifier.fillMaxWidth().padding(vertical = 6.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(Names.of(s.planet, lang), fontWeight = FontWeight.SemiBold, modifier = Modifier.width(84.dp))
                Text(stringResource(R.string.shadbala_line, "%.2f".format(s.rupas), "%.1f".format(s.required)), style = MaterialTheme.typography.bodySmall,
                    color = Palette.Muted, modifier = Modifier.weight(1f))
                Text("%.2f×".format(s.ratio), style = MaterialTheme.typography.labelLarge, color = if (s.ratio >= 1) Palette.Good else Color(0xFF9A3B1B))
            }
            Bar(fraction = (s.ratio / 2.0).toFloat(), mark = 0.5f, good = s.ratio >= 1)
        }
    }
    Spacer(Modifier.height(16.dp))
    Text(stringResource(R.string.sav_title), style = MaterialTheme.typography.titleMedium, modifier = Modifier.semantics { heading() })
    Text(stringResource(R.string.sav_note), style = MaterialTheme.typography.bodySmall, color = Palette.Muted, modifier = Modifier.padding(vertical = 4.dp))
    (1..12).forEach { h ->
        val sign = SIGNS[m.signOfHouse(h)]
        val pts = m.savBySign[sign] ?: return@forEach
        Row(Modifier.fillMaxWidth().padding(vertical = 4.dp), verticalAlignment = Alignment.CenterVertically) {
            Text("${stringResource(R.string.house_label)} $h", modifier = Modifier.width(64.dp), style = MaterialTheme.typography.bodySmall)
            Text(Names.of(sign, lang), modifier = Modifier.width(84.dp), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
            Box(Modifier.weight(1f)) { Bar(fraction = pts / 48f, mark = 28f / 48f, good = pts >= 28) }
            Text("$pts", modifier = Modifier.width(32.dp).padding(start = 8.dp), style = MaterialTheme.typography.labelLarge)
        }
    }
}

/** A horizontal bar with a reference mark (1.0 for Shadbala, 28 for Ashtakavarga). */
@Composable
private fun Bar(fraction: Float, mark: Float, good: Boolean) {
    Box(Modifier.fillMaxWidth().height(8.dp).background(Color(0xFFEFEBE4), RoundedCornerShape(4.dp))) {
        Box(Modifier.fillMaxWidth(fraction.coerceIn(0.02f, 1f)).height(8.dp).background(if (good) Palette.Good else Palette.Accent, RoundedCornerShape(4.dp)))
        Box(Modifier.fillMaxWidth(mark).height(8.dp)) { Box(Modifier.align(Alignment.CenterEnd).width(2.dp).height(8.dp).background(Palette.Ink)) }
    }
}

@Composable
private fun PlanetDetail(p: Planet, m: ChartModel?, lang: String) {
    Text(Names.of(p.name, lang), style = MaterialTheme.typography.headlineMedium)
    val flags = buildList {
        if (p.retrograde && p.name != "Rahu" && p.name != "Ketu") add(stringResource(R.string.retrograde))
        if (p.combust) add(stringResource(R.string.combust))
        if (p.vargottama) add(stringResource(R.string.vargottama))
    }
    if (flags.isNotEmpty()) Text(flags.joinToString(" · "), color = Palette.AccentDeep, style = MaterialTheme.typography.labelLarge)
    Meaning(listOfNotNull(
        Meanings.planet(p.name, lang),
        Meanings.house(p.house, lang)?.let { stringResource(R.string.meaning_in_house, p.house, it) },
    ), "planet_meaning")
    Facts(listOf(
        stringResource(R.string.sign_label) to "${Names.of(p.sign, lang)} ${p.dms}",
        stringResource(R.string.house_label) to "${p.house}",
        stringResource(R.string.nakshatra_label) to "${Names.nakshatra(p.nakshatra, lang)} ${p.pada}",
        stringResource(R.string.nak_lord) to Names.of(p.nakshatraLord, lang),
        stringResource(R.string.sign_lord) to Names.of(p.signLord, lang),
        stringResource(R.string.dignity_label) to Names.dignity(p.dignity, lang),
        stringResource(R.string.motion_label) to "%.3f°".format(p.dailyMotion),
    ) + (m?.strengths?.firstOrNull { it.planet == p.name }?.let {
        listOf(stringResource(R.string.strength_label) to stringResource(R.string.shadbala_line, "%.2f".format(it.rupas), "%.1f".format(it.required)))
    } ?: emptyList()))
}

@Composable
private fun YogaDetail(y: Yoga, lang: String) {
    Text(Names.yogaCategory(y.category, lang).uppercase(), style = MaterialTheme.typography.labelMedium, color = Palette.Muted)
    Text(Names.yoga(y.name, lang), style = MaterialTheme.typography.headlineMedium)
    Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
        y.strength?.let { Pill(strengthLabel(it), it == "strong") }
        Pill(toneLabel(y.tone), false)
        y.baseRate?.let { Pill(rateLabel(it), false) }
    }
    Meaning(Meanings.yoga(y.id, y.category, lang), "yoga_meaning")
    Facts(buildList {
        add(stringResource(R.string.rule_label) to y.rule)
        if (y.keyPlanets.isNotEmpty()) add(stringResource(R.string.key_planets) to y.keyPlanets.joinToString(", ") { Names.of(it, lang) })
        y.strengthScore?.let { add(stringResource(R.string.strength_label) to "%.2f".format(it)) }
        add(stringResource(R.string.source_label) to y.source)
        y.note?.let { add(stringResource(R.string.note_label) to it) }
    })
    if (y.strength != null) Text(stringResource(R.string.strength_heuristic), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
}

@Composable
private fun Facts(rows: List<Pair<String, String>>) {
    Column(Modifier.fillMaxWidth().background(Palette.Ground, RoundedCornerShape(12.dp)).padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        rows.forEach { (k, v) ->
            Row {
                Text(k, style = MaterialTheme.typography.bodySmall, color = Palette.Muted, modifier = Modifier.width(118.dp))
                Text(v, style = MaterialTheme.typography.bodyMedium, modifier = Modifier.weight(1f))
            }
        }
    }
}
