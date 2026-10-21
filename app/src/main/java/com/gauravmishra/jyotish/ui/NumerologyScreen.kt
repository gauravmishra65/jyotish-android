package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.ChartState
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.NameOption
import com.gauravmishra.jyotish.data.NameOptions
import com.gauravmishra.jyotish.data.NumerologyModel
import com.gauravmishra.jyotish.data.Profile
import kotlinx.coroutines.launch

private val DIRS_EN = mapOf("N" to "North", "NE" to "North-east", "E" to "East", "SE" to "South-east",
    "S" to "South", "SW" to "South-west", "W" to "West", "NW" to "North-west")
private val DIRS_HI = mapOf("N" to "उत्तर", "NE" to "ईशान (उत्तर-पूर्व)", "E" to "पूर्व", "SE" to "आग्नेय (दक्षिण-पूर्व)",
    "S" to "दक्षिण", "SW" to "नैऋत्य (दक्षिण-पश्चिम)", "W" to "पश्चिम", "NW" to "वायव्य (उत्तर-पश्चिम)")
private val KUA_HI = mapOf("growth" to "वृद्धि", "health" to "स्वास्थ्य", "relationships" to "संबंध", "stability" to "स्थिरता",
    "mishaps" to "दुर्घटनाएँ", "quarrels" to "झगड़े", "setbacks" to "रुकावटें", "severe loss" to "गंभीर हानि")
private val PLANE_HI = mapOf("mental" to "मानसिक", "emotional" to "भावनात्मक", "practical" to "व्यावहारिक", "thought" to "विचार",
    "will" to "इच्छा", "action" to "कर्म", "golden diagonal" to "स्वर्ण विकर्ण", "silver diagonal" to "रजत विकर्ण")

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun NumerologyScreen(
    profiles: List<Profile>,
    profile: Profile?,
    chart: ChartState?,
    onSelect: (Profile) -> Unit,
    loadNames: suspend (Profile) -> String,
    onHome: () -> Unit,
    onFeature: (Feature) -> Unit,
) {
    val lang = currentLang()
    val model = remember((chart as? ChartState.Ready)?.json) { (chart as? ChartState.Ready)?.json?.let { runCatching { NumerologyModel.parse(it) }.getOrNull() } }
    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        topBar = { BackBar(stringResource(R.string.feature_numerology), onHome, subtitle = profile?.name) },
        bottomBar = { BottomNav(current = Feature.NUMBERS, onHome = onHome, onFeature = onFeature) },
    ) { pad ->
        Column(
            Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 4.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            if (profiles.size > 1) {
                FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    profiles.forEach { p ->
                        FilterChip(selected = p.id == profile?.id, onClick = { onSelect(p) }, label = { Text(p.name) },
                            colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep))
                    }
                }
            }
            when {
                profile == null -> { Text(stringResource(R.string.pick_profile_first)); return@Column }
                chart is ChartState.Failed -> { Text(stringResource(R.string.chart_failed, chart.message)); return@Column }
                model == null -> { Text(stringResource(R.string.calculating)); return@Column }
            }
            val m = model!!
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Tile(stringResource(R.string.nu_mulank), "${m.mulank}", Names.of(m.mulankPlanet, lang), dark = true, modifier = Modifier.weight(1f))
                Tile(stringResource(R.string.nu_bhagyank), "${m.bhagyank}", Names.of(m.bhagyankPlanet, lang), dark = true, modifier = Modifier.weight(1f))
                Tile(stringResource(R.string.nu_name), "${m.chaldeanCompound}/${m.chaldeanRoot}", "", dark = true, modifier = Modifier.weight(1f))
            }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Tile(stringResource(R.string.nu_life_path), "${m.lifePath}", m.lifePathAlt?.let { stringResource(R.string.nu_life_alt, it) } ?: "", modifier = Modifier.weight(1f))
                Tile(stringResource(R.string.nu_destiny), "${m.destiny}", "", modifier = Modifier.weight(1f))
                Tile(stringResource(R.string.nu_personal_year), "${m.personalYear}", stringResource(R.string.nu_month, m.personalMonth), modifier = Modifier.weight(1f))
            }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Tile(stringResource(R.string.nu_soul), "${m.soulUrge}", "", modifier = Modifier.weight(1f))
                Tile(stringResource(R.string.nu_personality), "${m.personality}", "", modifier = Modifier.weight(1f))
                Tile(stringResource(R.string.nu_maturity), "${m.maturity}", "", modifier = Modifier.weight(1f))
            }
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                if (m.karmicDebt.isNotEmpty()) Text(stringResource(R.string.nu_karmic_debt, m.karmicDebt.joinToString(", ")), style = MaterialTheme.typography.bodyMedium)
                if (m.karmicLessons.isNotEmpty()) Text(stringResource(R.string.nu_lessons, m.karmicLessons.joinToString(", ")), style = MaterialTheme.typography.bodyMedium)
                if (m.hiddenPassion.isNotEmpty()) Text(stringResource(R.string.nu_passion, m.hiddenPassion.joinToString(", ")), style = MaterialTheme.typography.bodyMedium)
            }

            Text(stringResource(R.string.nu_loshu), style = MaterialTheme.typography.titleMedium)
            Row(horizontalArrangement = Arrangement.spacedBy(16.dp), verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.width(168.dp).testTag("loshu")) {
                    m.loshu.chunked(3).forEach { row ->
                        Row {
                            row.forEach { (num, digits) ->
                                val missing = digits.isEmpty()
                                val label = if (missing) stringResource(R.string.nu_missing_cell, num) else digits
                                Box(
                                    Modifier.weight(1f).aspectRatio(1f).border(1.dp, if (missing) Palette.Accent else MaterialTheme.colorScheme.outline)
                                        .background(if (missing) Palette.AccentSoft else MaterialTheme.colorScheme.surface)
                                        .semantics { contentDescription = label },
                                    contentAlignment = Alignment.Center,
                                ) {
                                    if (missing) Text("$num", color = Palette.Accent.copy(alpha = 0.55f), style = MaterialTheme.typography.titleMedium)
                                    else Text(digits, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.SemiBold)
                                }
                            }
                        }
                    }
                }
                Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    if (m.missing.isNotEmpty()) Text(stringResource(R.string.nu_missing_line, m.missing.joinToString(", ")), style = MaterialTheme.typography.bodyMedium)
                    Text(stringResource(R.string.nu_planes), style = MaterialTheme.typography.labelMedium, color = Palette.Muted)
                    m.planes.forEach { (k, v) ->
                        val name = k.substringBefore(" (").let { if (lang == "hi") PLANE_HI[it] ?: it else it }
                        val digits = k.substringAfter("(", "").removeSuffix(")")
                        val status = stringResource(when {
                            v.startsWith("complete") -> R.string.plane_complete; v.startsWith("partial") -> R.string.plane_partial; else -> R.string.plane_missing
                        })
                        Text("$name $digits: $status", style = MaterialTheme.typography.bodySmall,
                            fontWeight = if (v.startsWith("complete")) FontWeight.SemiBold else FontWeight.Normal)
                    }
                }
            }

            if (m.kua != null && m.kua > 0) {
                Text(stringResource(R.string.nu_kua), style = MaterialTheme.typography.titleMedium)
                Text(stringResource(R.string.nu_kua_line, m.kua, stringResource(if (m.kuaGroup == "West") R.string.nu_west else R.string.nu_east)),
                    style = MaterialTheme.typography.bodyLarge)
                KuaList(stringResource(R.string.nu_kua_good), m.kuaGood, lang, Palette.Good)
                KuaList(stringResource(R.string.nu_kua_bad), m.kuaBad, lang, Color(0xFF9A3B1B))
                Text(stringResource(R.string.nu_kua_note), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
            }

            NameOptionsCard(profile!!, lang, loadNames)
        }
    }
}

@Composable
private fun Tile(label: String, value: String, sub: String, modifier: Modifier, dark: Boolean = false) {
    Surface(
        shape = RoundedCornerShape(14.dp), color = if (dark) Palette.Night else MaterialTheme.colorScheme.surface,
        border = if (dark) null else BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant), modifier = modifier,
    ) {
        Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(label, style = MaterialTheme.typography.labelMedium, color = if (dark) Palette.SaffronText else Palette.Muted, maxLines = 2)
            Text(value, style = if (dark) MaterialTheme.typography.headlineMedium else MaterialTheme.typography.titleLarge,
                color = if (dark) Palette.Ground else Palette.Ink)
            if (sub.isNotEmpty()) Text(sub, style = MaterialTheme.typography.labelMedium, color = if (dark) Palette.NightText else Palette.Muted)
        }
    }
}

@Composable
private fun KuaList(title: String, items: List<Pair<String, String>>, lang: String, color: Color) {
    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
        Text(title, style = MaterialTheme.typography.labelLarge, color = color)
        items.forEach { (k, dir) ->
            val name = if (lang == "hi") Regex("\\((.+)\\)").find(k)?.groupValues?.get(1)?.let { KUA_HI[it] } ?: k else k
            Text("${(if (lang == "hi") DIRS_HI else DIRS_EN)[dir] ?: dir}: $name", style = MaterialTheme.typography.bodySmall)
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun NameOptionsCard(profile: Profile, lang: String, loadNames: suspend (Profile) -> String) {
    var opts by remember(profile.id) { mutableStateOf<NameOptions?>(null) }
    var loading by remember(profile.id) { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    Surface(shape = RoundedCornerShape(16.dp), color = MaterialTheme.colorScheme.surface, border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)) {
        Column(Modifier.fillMaxWidth().padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(stringResource(R.string.nu_names_title), style = MaterialTheme.typography.titleMedium, modifier = Modifier.weight(1f))
                Text(stringResource(R.string.nu_optional), style = MaterialTheme.typography.labelMedium,
                    modifier = Modifier.background(Color(0xFFEFEBE4), RoundedCornerShape(10.dp)).padding(horizontal = 8.dp, vertical = 3.dp))
            }
            Text(stringResource(R.string.nu_names_intro), style = MaterialTheme.typography.bodySmall, color = Color(0xFF3F3B35))
            val o = opts
            when {
                o == null && !loading -> OutlinedButton(onClick = {
                    loading = true
                    scope.launch { opts = runCatching { NameOptions.parse(loadNames(profile)) }.getOrNull(); loading = false }
                }, modifier = Modifier.testTag("names_show")) { Text(stringResource(R.string.nu_names_show)) }
                o == null -> Text(stringResource(R.string.nu_calculating), style = MaterialTheme.typography.bodySmall)
                else -> {
                    if (o.alreadyFits) Text(stringResource(R.string.nu_names_fits), style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.SemiBold)
                    NameRow(o.original, lang, current = true)
                    o.options.forEach { NameRow(it, lang, current = false) }
                    Text(stringResource(R.string.nu_names_note), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
                }
            }
        }
    }
}

@Composable
private fun NameRow(n: NameOption, lang: String, current: Boolean) {
    val cls = stringResource(when (n.cls) {
        "favourable" -> R.string.cls_favourable; "neutral" -> R.string.cls_neutral; "mixed" -> R.string.cls_mixed
        "difficult" -> R.string.cls_difficult; else -> R.string.cls_root
    })
    val fit = stringResource(when (n.fitMulank) {
        "same" -> R.string.fit_same; "friend" -> R.string.fit_friend; "enemy" -> R.string.fit_enemy; else -> R.string.fit_neutral
    })
    Column(Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(n.spelling.substringBefore(" ").ifEmpty { n.spelling }, style = MaterialTheme.typography.titleMedium,
                color = if (current) Palette.Muted else Palette.Ink, modifier = Modifier.weight(1f))
            Text("${n.compound}/${n.root}", style = MaterialTheme.typography.labelLarge, modifier = Modifier.padding(horizontal = 8.dp))
            Text(cls, style = MaterialTheme.typography.labelLarge, textAlign = TextAlign.End,
                color = when (n.cls) { "favourable" -> Palette.Good; "difficult" -> Color(0xFF9A3B1B); else -> Palette.Muted })
        }
        val detail = if (current) stringResource(R.string.nu_now) else n.changes.joinToString(", ") { if (lang == "hi") NameOptions.changeHi(it) else it }
        Text("$detail · ${stringResource(R.string.nu_with_mulank, fit)}", style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
    }
}
