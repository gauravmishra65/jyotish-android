package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.DetailSection
import com.gauravmishra.jyotish.data.parseSections
import com.gauravmishra.jyotish.engine.Engine
import org.json.JSONObject
import java.time.LocalDate
import java.time.ZoneId

/** Flying Stars Feng Shui (v19): this year's and month's stars on the nine sectors, and a home's star chart. */
@Composable
fun FengShuiScreen(tz: String, onBack: () -> Unit) {
    val lang = currentLang()
    var facing by rememberSaveable { mutableStateOf("") }
    var built by rememberSaveable { mutableStateOf("") }
    var run by remember { mutableIntStateOf(0) }
    var sections by remember { mutableStateOf<List<DetailSection>>(emptyList()) }
    var grid by remember { mutableStateOf<JSONObject?>(null) }
    var house by remember { mutableStateOf<JSONObject?>(null) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    val f = facing.trim().toDoubleOrNull()?.takeIf { it >= 0 && it < 360 }
    val y = built.trim().toIntOrNull()?.takeIf { it in 1864..LocalDate.now().year + 1 }
    LaunchedEffect(run) {
        busy = true; error = null
        val offset = ZoneId.of(tz).rules.getOffset(java.time.Instant.now()).totalSeconds / 3600.0
        val req = JSONObject().put("today", LocalDate.now().toString()).put("tz_hours", offset)
        if (run > 0 && f != null && y != null) req.put("facing", f).put("built_year", y)
        try {
            val o = JSONObject(Engine.fengShui(req))
            sections = parseSections(o.optJSONArray("sections")); grid = o.optJSONObject("grid"); house = o.optJSONObject("house")
        } catch (t: Throwable) { error = t.message }
        busy = false
    }
    Scaffold(containerColor = MaterialTheme.colorScheme.background, topBar = { BackBar(stringResource(R.string.fs_title), onBack) }) { pad ->
        Column(Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 16.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text(stringResource(R.string.fs_intro), style = MaterialTheme.typography.bodyMedium)
            if (busy) LinearProgressIndicator(Modifier.fillMaxWidth(), color = Palette.Accent)
            error?.let { Text(stringResource(R.string.bt_failed, it)) }
            grid?.optJSONObject("year")?.let { yr ->
                Text(stringResource(R.string.fs_grid), style = MaterialTheme.typography.titleMedium)
                LoShu({ s -> yr.optInt(s).toString() }, house?.let { h -> { s: String -> "${h.optJSONObject("mountain")?.optInt(s)}-${h.optJSONObject("water")?.optInt(s)}" } }, lang)
            }
            Text(stringResource(R.string.fs_house), style = MaterialTheme.typography.titleMedium)
            OutlinedTextField(facing, { facing = it }, label = { Text(stringResource(R.string.fs_facing)) }, singleLine = true,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal), isError = facing.isNotEmpty() && f == null,
                modifier = Modifier.fillMaxWidth().testTag("fs_facing"))
            OutlinedTextField(built, { built = it }, label = { Text(stringResource(R.string.fs_built)) }, singleLine = true,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), isError = built.isNotEmpty() && y == null,
                modifier = Modifier.fillMaxWidth().testTag("fs_built"))
            Text(stringResource(R.string.fs_house_note), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
            Button(enabled = f != null && y != null && !busy, onClick = { run++ }, modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp).testTag("fs_run")) {
                Text(stringResource(R.string.fs_run))
            }
            sections.forEach { s -> key(s.key + s.title.en) { SectionCard(s, lang, startOpen = true) } }
        }
    }
}

/** The nine sectors in the traditional Lo Shu layout, South at the top. */
@Composable
private fun LoShu(year: (String) -> String, house: ((String) -> String)?, lang: String) {
    val rows = listOf(listOf("SE", "S", "SW"), listOf("E", "C", "W"), listOf("NE", "N", "NW"))
    val names = mapOf("N" to ("N" to "उ"), "NE" to ("NE" to "उपू"), "E" to ("E" to "पू"), "SE" to ("SE" to "दपू"), "S" to ("S" to "द"),
        "SW" to ("SW" to "दप"), "W" to ("W" to "प"), "NW" to ("NW" to "उप"), "C" to ("C" to "म"))
    Column(Modifier.fillMaxWidth().testTag("fs_grid"), verticalArrangement = Arrangement.spacedBy(3.dp)) {
        rows.forEach { r ->
            Row(horizontalArrangement = Arrangement.spacedBy(3.dp)) {
                r.forEach { s ->
                    Surface(shape = MaterialTheme.shapes.small, color = if (year(s) in setOf("2", "5")) MaterialTheme.colorScheme.surfaceVariant else Palette.AccentSoft,
                        border = BorderStroke(0.5.dp, MaterialTheme.colorScheme.outlineVariant), modifier = Modifier.weight(1f).aspectRatio(1.3f)) {
                        Column(Modifier.padding(6.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
                            Text(names[s]!!.let { if (lang == "hi") it.second else it.first }, fontSize = 11.sp, color = Palette.Muted)
                            Text(year(s), fontSize = 22.sp, fontWeight = FontWeight.Bold, color = Palette.AccentDeep)
                            house?.let { Text(it(s), fontSize = 12.sp, color = Palette.Muted) }
                        }
                    }
                }
            }
        }
        Text(stringResource(if (house != null) R.string.fs_grid_note_house else R.string.fs_grid_note), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
    }
}
