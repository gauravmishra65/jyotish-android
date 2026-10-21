package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.gauravmishra.jyotish.ChartState
import com.gauravmishra.jyotish.MatchState
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.Meanings
import com.gauravmishra.jyotish.data.Koota
import com.gauravmishra.jyotish.data.MatchModel
import com.gauravmishra.jyotish.data.PoruthamItem
import com.gauravmishra.jyotish.data.Profile

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MilanScreen(
    profiles: List<Profile>,
    groom: Profile?,
    bride: Profile?,
    charts: Map<String, ChartState>,
    match: MatchState,
    onPair: (String?, String?) -> Unit,
    onRequest: (String, String) -> Unit,
    onAdd: () -> Unit,
    onHome: () -> Unit,
    onFeature: (Feature) -> Unit,
) {
    var koota by remember { mutableStateOf<Koota?>(null) }
    var porutham by remember { mutableStateOf(false) }
    val readyA = groom?.let { charts[it.id] is ChartState.Ready } == true
    val readyB = bride?.let { charts[it.id] is ChartState.Ready } == true
    LaunchedEffect(groom?.id, bride?.id, readyA, readyB) {
        if (groom != null && bride != null && groom.id != bride.id) onRequest(groom.id, bride.id)
    }

    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        topBar = { BackBar(stringResource(R.string.feature_milan), onHome) },
        bottomBar = { BottomNav(current = Feature.MILAN, onHome = onHome, onFeature = onFeature) },
    ) { pad ->
        Column(
            Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 4.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            if (profiles.size < 2) {
                Text(stringResource(R.string.need_two), style = MaterialTheme.typography.bodyLarge)
                TextButton(onClick = onAdd, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.add_profile), color = Palette.Accent) }
                return@Column
            }
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                PersonPicker(stringResource(R.string.groom), groom, profiles, Modifier.weight(1f).testTag("pick_groom")) { onPair(it.id, bride?.id) }
                val swap = stringResource(R.string.swap)
                IconButton(onClick = { onPair(bride?.id, groom?.id) }, modifier = Modifier.size(48.dp).semantics { contentDescription = swap }) {
                    Text("⇄", color = Palette.Accent, fontSize = 22.sp)
                }
                PersonPicker(stringResource(R.string.bride), bride, profiles, Modifier.weight(1f).testTag("pick_bride")) { onPair(groom?.id, it.id) }
            }
            if (groom != null && groom.id == bride?.id) { Text(stringResource(R.string.same_person), color = MaterialTheme.colorScheme.error); return@Column }

            when (match) {
                is MatchState.Waiting -> Text(stringResource(R.string.waiting_charts))
                is MatchState.Calculating -> Text(stringResource(R.string.matching))
                is MatchState.Failed -> Text(stringResource(R.string.match_failed, match.message))
                is MatchState.Ready -> MatchBody(match.model, onKoota = { koota = it }, onPorutham = { porutham = true })
            }
        }
    }

    val sheet = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    if (koota != null || porutham) {
        ModalBottomSheet(onDismissRequest = { koota = null; porutham = false }, sheetState = sheet, containerColor = MaterialTheme.colorScheme.surface) {
            Column(Modifier.padding(horizontal = 22.dp).padding(bottom = 28.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                koota?.let { KootaDetail(it) }
                if (porutham) (match as? MatchState.Ready)?.model?.let { PoruthamDetail(it.porutham) }
                OutlinedButton(onClick = { koota = null; porutham = false }, modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp)) { Text(stringResource(R.string.close)) }
            }
        }
    }
}

@Composable
private fun PersonPicker(label: String, chosen: Profile?, profiles: List<Profile>, modifier: Modifier, onPick: (Profile) -> Unit) {
    var open by remember { mutableStateOf(false) }
    Box(modifier) {
        Surface(
            onClick = { open = true }, shape = RoundedCornerShape(12.dp), color = MaterialTheme.colorScheme.surface,
            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline), modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp),
        ) {
            Column(Modifier.padding(horizontal = 12.dp, vertical = 8.dp)) {
                Text(label, style = MaterialTheme.typography.labelMedium, color = Palette.Muted)
                Text(chosen?.name ?: stringResource(R.string.choose_person), style = MaterialTheme.typography.titleMedium, maxLines = 1,
                    overflow = androidx.compose.ui.text.style.TextOverflow.Ellipsis)
            }
        }
        DropdownMenu(expanded = open, onDismissRequest = { open = false }) {
            profiles.forEach { p ->
                DropdownMenuItem(text = { Text(p.name) }, onClick = { open = false; onPick(p) })
            }
        }
    }
}

@Composable
private fun MatchBody(m: MatchModel, onKoota: (Koota) -> Unit, onPorutham: () -> Unit) {
    val score = fmt(m.total)
    Surface(shape = RoundedCornerShape(18.dp), color = MaterialTheme.colorScheme.surface, border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)) {
        Row(Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            Box(Modifier.size(104.dp).semantics { contentDescription = "$score / ${m.outOf}" }.testTag("score"), contentAlignment = Alignment.Center) {
                Canvas(Modifier.size(104.dp)) {
                    val w = 10.dp.toPx()
                    val inset = w / 2
                    val arc = Size(size.width - w, size.height - w)
                    drawArc(Color(0xFFEFEBE4), 0f, 360f, false, Offset(inset, inset), arc, style = Stroke(w))
                    drawArc(Palette.Accent, -90f, (360f * m.total / m.outOf).toFloat(), false, Offset(inset, inset), arc, style = Stroke(w, cap = StrokeCap.Round))
                }
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(score, style = MaterialTheme.typography.headlineMedium)
                    Text(stringResource(R.string.of_36), style = MaterialTheme.typography.labelMedium, color = Palette.Muted)
                }
            }
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(stringResource(when (m.band) {
                    "below18" -> R.string.band_below18; "18to24" -> R.string.band_18to24; "25to32" -> R.string.band_25to32; else -> R.string.band_above32
                }), style = MaterialTheme.typography.titleMedium)
                Text(if (m.rangeLow != m.rangeHigh) stringResource(R.string.score_range, fmt(m.rangeLow), fmt(m.rangeHigh)) else stringResource(R.string.score_one_value),
                    style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
            }
        }
    }

    Text(stringResource(R.string.eight_kootas), style = MaterialTheme.typography.titleMedium)
    Column {
        m.kootas.forEach { k ->
            Row(
                Modifier.fillMaxWidth().heightIn(min = 48.dp).clickable(role = Role.Button) { onKoota(k) }.testTag("koota_${k.key}"),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(stringResource(kootaName(k.key)), modifier = Modifier.width(110.dp), style = MaterialTheme.typography.bodyMedium)
                Box(Modifier.weight(1f).height(8.dp).background(Color(0xFFEFEBE4), RoundedCornerShape(4.dp))) {
                    Box(Modifier.fillMaxWidth((k.score / k.max).toFloat().coerceIn(0.02f, 1f)).height(8.dp).background(Palette.Accent, RoundedCornerShape(4.dp)))
                }
                Text("${fmt(k.score)}/${k.max}", modifier = Modifier.width(52.dp).padding(start = 8.dp), style = MaterialTheme.typography.labelLarge)
            }
        }
    }

    Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
        Surface(
            onClick = onPorutham, shape = RoundedCornerShape(14.dp), color = MaterialTheme.colorScheme.surface,
            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant), modifier = Modifier.weight(1f).testTag("porutham"),
        ) {
            Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(stringResource(R.string.porutham_title), style = MaterialTheme.typography.labelMedium, color = Palette.Muted)
                Text(stringResource(R.string.porutham_agree, m.poruthamAgree, m.poruthamOutOf), style = MaterialTheme.typography.titleMedium)
                Text(stringResource(if (m.essentialAllAgree) R.string.porutham_essential else R.string.porutham_essential_not),
                    style = MaterialTheme.typography.labelMedium, color = Palette.Muted)
            }
        }
    }

    Text(stringResource(R.string.mangal_title), style = MaterialTheme.typography.titleMedium)
    m.mangal.forEach { mc ->
        Surface(shape = RoundedCornerShape(14.dp), color = MaterialTheme.colorScheme.surface, border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)) {
            Column(Modifier.fillMaxWidth().padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(mc.name, style = MaterialTheme.typography.labelMedium, color = Palette.Muted)
                val from = mc.countedFrom.map { stringResource(when (it) { "lagna" -> R.string.mangal_lagna; "moon" -> R.string.mangal_moon; else -> R.string.mangal_venus }) }
                Text(if (mc.counted) stringResource(R.string.mangal_counted, from.joinToString(", ")) else stringResource(R.string.mangal_not), style = MaterialTheme.typography.titleMedium)
                Text(stringResource(R.string.mangal_houses, mc.fromLagna, mc.fromMoon, mc.fromVenus), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
            }
        }
    }
    Text(stringResource(R.string.mangal_note), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
}

private fun fmt(v: Double) = if (v % 1.0 == 0.0) v.toInt().toString() else v.toString()

private fun kootaName(k: String) = when (k) {
    "varna" -> R.string.koota_varna; "vashya" -> R.string.koota_vashya; "tara" -> R.string.koota_tara; "yoni" -> R.string.koota_yoni
    "graha_maitri" -> R.string.koota_graha_maitri; "gana" -> R.string.koota_gana; "bhakoot" -> R.string.koota_bhakoot; else -> R.string.koota_nadi
}

private fun poruthamName(k: String) = when (k) {
    "dina" -> R.string.p_dina; "gana" -> R.string.p_gana; "mahendra" -> R.string.p_mahendra; "stree_deergha" -> R.string.p_stree_deergha
    "yoni" -> R.string.p_yoni; "rasi" -> R.string.p_rasi; "rasi_adhipati" -> R.string.p_rasi_adhipati; "vasya" -> R.string.p_vasya
    "rajju" -> R.string.p_rajju; else -> R.string.p_vedha
}

@Composable
private fun KootaDetail(k: Koota) {
    Text(stringResource(kootaName(k.key)), style = MaterialTheme.typography.headlineMedium)
    Text("${fmt(k.score)} / ${k.max}", style = MaterialTheme.typography.titleLarge, color = Palette.AccentDeep)
    Meaning(listOfNotNull(Meanings.koota(k.key, currentLang())), "koota_meaning")
    Text(stringResource(R.string.koota_facts), style = MaterialTheme.typography.labelMedium, color = Palette.Muted)
    Column(Modifier.fillMaxWidth().background(Palette.Ground, RoundedCornerShape(12.dp)).padding(14.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
        k.facts.forEach { (key, v) ->
            Row {
                Text(key.replace('_', ' '), style = MaterialTheme.typography.bodySmall, color = Palette.Muted, modifier = Modifier.width(150.dp))
                Text(v, style = MaterialTheme.typography.bodyMedium, modifier = Modifier.weight(1f))
            }
        }
    }
    k.note?.let { Text(it, style = MaterialTheme.typography.bodySmall, color = Palette.Muted) }
}

@Composable
private fun PoruthamDetail(items: List<PoruthamItem>) {
    Text(stringResource(R.string.porutham_title), style = MaterialTheme.typography.headlineSmall)
    items.forEach { p ->
        Column(Modifier.fillMaxWidth().padding(vertical = 6.dp), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(stringResource(poruthamName(p.key)), style = MaterialTheme.typography.titleMedium, modifier = Modifier.weight(1f))
                val (label, color) = when {
                    p.ok && !p.partial -> stringResource(R.string.agrees) to Palette.Good
                    p.partial -> stringResource(R.string.partly) to Palette.AccentDeep
                    else -> stringResource(R.string.does_not) to Color(0xFF9A3B1B)
                }
                Text(label, color = color, fontWeight = FontWeight.SemiBold, style = MaterialTheme.typography.labelLarge)
            }
            Meanings.porutham(p.key, currentLang())?.let { Text(it, style = MaterialTheme.typography.bodyMedium) }
            Text(p.rule, style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
        }
        HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
    }
}
