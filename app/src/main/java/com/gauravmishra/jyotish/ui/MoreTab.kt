package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.ChartModel
import com.gauravmishra.jyotish.data.DetailBlock
import com.gauravmishra.jyotish.data.DetailSection
import com.gauravmishra.jyotish.data.DetailsModel
import com.gauravmishra.jyotish.data.varga

/** The Kundali screen's fifth tab: D9/D10 drawn, then every extra section from app_details as a collapsible card. */
@Composable
fun MoreTab(m: ChartModel, details: DetailsModel?, style: String, lang: String, residence: String?) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.testTag("more_tab")) {
        residence?.let { Text(stringResource(R.string.residence_label, it), style = MaterialTheme.typography.bodyMedium, color = Palette.Muted) }
        if (details == null) {
            Text(stringResource(R.string.calculating), style = MaterialTheme.typography.bodyMedium)
            return@Column
        }
        if (details.vargas.isNotEmpty()) {
            var which by rememberSaveable { mutableStateOf("D9") }
            Text(stringResource(R.string.vargas_title), style = MaterialTheme.typography.titleMedium)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf("D9" to R.string.d9_label, "D10" to R.string.d10_label).filter { details.vargas.containsKey(it.first) }.forEach { (k, label) ->
                    FilterChip(selected = which == k, onClick = { which = k }, label = { Text(stringResource(label)) },
                        modifier = Modifier.heightIn(min = 48.dp).testTag("varga_$k"),
                        colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep))
                }
            }
            details.vargas[which]?.let { signs ->
                val vm = m.varga(signs)
                KundliChart(vm, style, lang,
                    chartDescription(vm, lang, stringResource(R.string.house_word), stringResource(R.string.empty_word)),
                    Modifier.padding(horizontal = 4.dp).testTag("varga_chart"))
                Text(stringResource(if (which == "D9") R.string.d9_note else R.string.d10_note), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
            }
        }
        details.sections.forEach { SectionCard(it, lang) }
    }
}

@Composable
private fun SectionCard(s: DetailSection, lang: String) {
    var open by rememberSaveable(s.key) { mutableStateOf(s.key == "panchang") }
    Surface(shape = RoundedCornerShape(14.dp), color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant), modifier = Modifier.fillMaxWidth().testTag("section_${s.key}")) {
        Column {
            Row(
                Modifier.fillMaxWidth().heightIn(min = 52.dp).clickable(role = Role.Button) { open = !open }
                    .semantics { stateDescription = if (open) "expanded" else "collapsed" }.padding(horizontal = 14.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(s.title.of(lang), style = MaterialTheme.typography.titleMedium, modifier = Modifier.weight(1f))
                Text(if (open) "−" else "+", style = MaterialTheme.typography.titleLarge, color = Palette.Accent)
            }
            if (open) {
                Column(Modifier.padding(start = 14.dp, end = 14.dp, bottom = 14.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    s.intro?.let { Text(it.of(lang), style = MaterialTheme.typography.bodySmall, color = Palette.Muted) }
                    s.blocks.forEach { b ->
                        when (b) {
                            is DetailBlock.Para -> Text(b.text.of(lang), style = MaterialTheme.typography.bodyMedium)
                            is DetailBlock.Items -> Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                                b.items.forEach { Row { Text("•  ", color = Palette.Accent); Text(it.of(lang), style = MaterialTheme.typography.bodyMedium) } }
                            }
                            is DetailBlock.Table -> DataTable(b, lang)
                        }
                    }
                    s.note?.let { Text(it.of(lang), style = MaterialTheme.typography.bodySmall, color = Palette.Muted) }
                }
            }
        }
    }
}

/** A plain table; wide ones (Ashtakavarga has 13 columns) scroll sideways. */
@Composable
private fun DataTable(t: DetailBlock.Table, lang: String) {
    val wide = t.head.size > 4
    val first = if (wide) 76.dp else 110.dp
    val other = if (wide) 30.dp else 96.dp
    Column(Modifier.then(if (wide) Modifier.horizontalScroll(rememberScrollState()) else Modifier)
        .background(Palette.Ground, RoundedCornerShape(10.dp)).padding(8.dp)) {
        Row(Modifier.padding(vertical = 4.dp)) {
            t.head.forEachIndexed { i, h ->
                Text(h.of(lang), style = MaterialTheme.typography.labelMedium, color = Palette.Muted, fontWeight = FontWeight.SemiBold,
                    modifier = cell(i, wide, first, other, t.head.size))
            }
        }
        t.rows.forEach { r ->
            Row(Modifier.padding(vertical = 3.dp)) {
                r.forEachIndexed { i, c ->
                    Text(c.of(lang), style = MaterialTheme.typography.bodySmall, modifier = cell(i, wide, first, other, t.head.size))
                }
            }
        }
    }
}

private fun cell(i: Int, wide: Boolean, first: androidx.compose.ui.unit.Dp, other: androidx.compose.ui.unit.Dp, n: Int): Modifier =
    if (wide) Modifier.width(if (i == 0) first else other)
    else if (i == 0) Modifier.width(first).padding(end = 6.dp)
    else Modifier.widthIn(min = 60.dp).padding(end = 6.dp).then(if (n == 2) Modifier.fillMaxWidth() else Modifier.width(other))
