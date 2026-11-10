package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.TodayPlace
import com.gauravmishra.jyotish.data.DetailSection
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.parseSections
import com.gauravmishra.jyotish.engine.Engine
import org.json.JSONArray
import org.json.JSONObject

private val ACTIVITIES = listOf("wedding", "moving", "business", "travel", "contract")

/**
 * Chinese astrology (v17): the lunar birth date, the Zi Wei Dou Shu chart as the traditional square of twelve
 * palaces, Nine Star Ki and Tong Shu good days for a chosen activity.
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun ChineseScreen(profiles: List<Profile>, profile: Profile?, place: TodayPlace?, onSelect: (Profile) -> Unit, onAdd: () -> Unit, onBack: () -> Unit) {
    val lang = currentLang()
    var activity by remember { mutableStateOf("wedding") }
    var sections by remember { mutableStateOf<List<DetailSection>>(emptyList()) }
    var grid by remember { mutableStateOf<JSONArray?>(null) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    LaunchedEffect(profile?.id, activity, place) {
        val p = profile ?: return@LaunchedEffect
        busy = true; error = null
        val req = JSONObject().put("name", p.name).put("date", p.date).put("time", p.time).put("gender", p.gender).put("tz", p.tz)
            .put("today_tz", place?.tz ?: p.tz).put("activity", activity)
        try {
            val o = JSONObject(Engine.chineseMore(req))
            sections = parseSections(o.optJSONArray("sections"))
            grid = o.optJSONArray("grid")
        } catch (t: Throwable) { error = t.message }
        busy = false
    }
    Scaffold(containerColor = MaterialTheme.colorScheme.background, topBar = { BackBar(stringResource(R.string.cn_title), onBack, subtitle = profile?.name) }) { pad ->
        Column(Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 16.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)) {
            ProfileBar(profiles, profile, onSelect, onAdd)
            if (busy) LinearProgressIndicator(Modifier.fillMaxWidth(), color = Palette.Accent)
            error?.let { Text(stringResource(R.string.bt_failed, it)) }
            grid?.let { ZiWeiGrid(it, lang) }
            Text(stringResource(R.string.cn_activity), style = MaterialTheme.typography.labelLarge)
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                ACTIVITIES.forEach { a ->
                    FilterChip(selected = activity == a, onClick = { activity = a }, label = { Text(stringResource(activityName(a))) },
                        modifier = Modifier.heightIn(min = 48.dp).testTag("cn_act_$a"),
                        colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep))
                }
            }
            sections.forEach { s -> key(s.key + s.title.en) { SectionCard(s, lang, startOpen = s.key != "zwds") } }
        }
    }
}

/** The twelve palaces in the traditional square: Si Wu Wei Shen on top, Yin Chou Zi Hai at the bottom. */
@Composable
private fun ZiWeiGrid(g: JSONArray, lang: String) {
    val byBranch = (0 until g.length()).map { g.getJSONObject(it) }.associateBy { it.getInt("branch") }
    val layout = listOf(listOf(5, 6, 7, 8), listOf(4, -1, -1, 9), listOf(3, -1, -1, 10), listOf(2, 1, 0, 11))
    Column(Modifier.fillMaxWidth().testTag("zwds_grid"), verticalArrangement = Arrangement.spacedBy(2.dp)) {
        Text(stringResource(R.string.cn_grid), style = MaterialTheme.typography.titleMedium)
        layout.forEachIndexed { r, row ->
            Row(horizontalArrangement = Arrangement.spacedBy(2.dp)) {
                row.forEachIndexed { c, b ->
                    if (b < 0) {
                        if (r == 1 && c == 1) Box(Modifier.weight(2f).aspectRatio(1.6f), contentAlignment = Alignment.Center) {
                            Text("紫微斗数", style = MaterialTheme.typography.titleMedium, color = Palette.Muted)
                        } else if (r == 2 && c == 1) Box(Modifier.weight(2f).aspectRatio(1.6f))
                    } else Cell(byBranch[b], lang, Modifier.weight(1f).aspectRatio(0.8f))
                }
            }
        }
        Text(stringResource(R.string.cn_grid_note), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
    }
}

@Composable
private fun Cell(p: JSONObject?, lang: String, modifier: Modifier) {
    if (p == null) { Box(modifier); return }
    val life = p.optBoolean("life")
    Surface(shape = MaterialTheme.shapes.extraSmall, color = if (life) Palette.AccentSoft else MaterialTheme.colorScheme.surface,
        border = BorderStroke(if (life) 1.5.dp else 0.5.dp, if (life) Palette.Accent else MaterialTheme.colorScheme.outlineVariant), modifier = modifier) {
        Column(Modifier.padding(3.dp), verticalArrangement = Arrangement.spacedBy(1.dp)) {
            val major = p.optJSONArray("major") ?: JSONArray()
            for (i in 0 until major.length()) {
                val s = major.getJSONObject(i)
                val t = s.optString("t").takeIf { it.isNotEmpty() && it != "null" }
                Text(s.optString("zh") + (t ?: ""), fontSize = 11.sp, fontWeight = FontWeight.Bold, color = Palette.AccentDeep, maxLines = 1)
            }
            val minor = p.optJSONArray("minor") ?: JSONArray()
            Text((0 until minor.length()).joinToString(" ") { minor.getJSONObject(it).optString("zh") }, fontSize = 9.sp, color = Palette.Muted, lineHeight = 10.sp)
            Text(p.optString(if (lang == "hi") "hi" else "en") + if (p.optBoolean("body")) " ·身" else "", fontSize = 9.sp, maxLines = 2, lineHeight = 10.sp)
            Text("${p.optString("stem_zh")}${p.optString("branch_zh")} ${p.optJSONArray("decade")?.optInt(0)}–${p.optJSONArray("decade")?.optInt(1)}",
                fontSize = 9.sp, color = Palette.Muted, textAlign = TextAlign.End, modifier = Modifier.fillMaxWidth())
        }
    }
}

private fun activityName(a: String) = when (a) {
    "wedding" -> R.string.cn_wedding
    "moving" -> R.string.cn_moving
    "business" -> R.string.cn_business
    "travel" -> R.string.cn_travel
    else -> R.string.cn_contract
}
