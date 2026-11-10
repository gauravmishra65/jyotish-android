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
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.TodayPlace
import com.gauravmishra.jyotish.engine.Engine
import kotlinx.coroutines.launch
import org.json.JSONObject

private val QUESTIONS = listOf("marriage", "job", "money", "property", "travel", "education", "children", "lost")

/**
 * A question asked now (v16): Vedic Prashna (the chart of this moment) or KP number horary (a number from 1 to 249).
 * The place is where the question is asked: the Today screen's city, else the person's home or birthplace.
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun QuestionScreen(method: String, place: TodayPlace?, ayanamsa: String, onBack: () -> Unit) {
    val lang = currentLang()
    val scope = rememberCoroutineScope()
    var question by remember { mutableStateOf("job") }
    var number by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    var result by remember { mutableStateOf<JSONObject?>(null) }
    var error by remember { mutableStateOf<String?>(null) }
    val kp = method == "kp"
    val n = number.trim().toIntOrNull()?.takeIf { it in 1..249 }

    Scaffold(containerColor = MaterialTheme.colorScheme.background,
        topBar = { BackBar(stringResource(if (kp) R.string.kp_title else R.string.pr_title), onBack, subtitle = place?.name) }) { pad ->
        Column(Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text(stringResource(if (kp) R.string.kp_intro else R.string.pr_intro), style = MaterialTheme.typography.bodyMedium)
            if (place == null) {
                Text(stringResource(R.string.pr_no_place), style = MaterialTheme.typography.bodyLarge)
                return@Column
            }
            Text(stringResource(R.string.pr_pick), style = MaterialTheme.typography.labelLarge)
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                QUESTIONS.forEach { q ->
                    FilterChip(selected = question == q, onClick = { question = q; result = null }, label = { Text(stringResource(questionName(q))) },
                        modifier = Modifier.heightIn(min = 48.dp).testTag("q_$q"),
                        colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep))
                }
            }
            if (kp) {
                OutlinedTextField(number, { number = it.filter(Char::isDigit).take(3); result = null }, label = { Text(stringResource(R.string.kp_number)) },
                    singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    isError = number.isNotEmpty() && n == null, modifier = Modifier.fillMaxWidth().testTag("kp_number"))
                Text(stringResource(R.string.kp_number_note), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
            }
            Button(
                enabled = !busy && (!kp || n != null),
                onClick = {
                    busy = true; error = null; result = null
                    val req = JSONObject().put("method", method).put("question", question).put("number", n ?: 1)
                        .put("lat", place.lat).put("lon", place.lon).put("tz", place.tz).put("place", place.name).put("ayanamsa", ayanamsa)
                    scope.launch {
                        try { result = JSONObject(Engine.question(req)) } catch (t: Throwable) { error = t.message ?: t.toString() }
                        busy = false
                    }
                },
                modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp).testTag("q_ask"),
            ) { Text(stringResource(R.string.pr_ask)) }
            if (busy) LinearProgressIndicator(Modifier.fillMaxWidth(), color = Palette.Accent)
            error?.let { Text(stringResource(R.string.bt_failed, it)) }
            result?.let { Answer(it, lang) }
        }
    }
}

@Composable
private fun Answer(o: JSONObject, lang: String) {
    fun b(x: JSONObject?) = x?.optString(lang)?.ifEmpty { x.optString("en") } ?: ""
    val lean = o.optString("lean")
    Column(Modifier.testTag("q_answer"), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text(b(o.optJSONObject("question_text")), style = MaterialTheme.typography.titleMedium)
        Surface(shape = RoundedCornerShape(12.dp), color = if (lean == "favourable") Palette.AccentSoft else MaterialTheme.colorScheme.surface,
            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant), modifier = Modifier.fillMaxWidth()) {
            Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(stringResource(when (lean) { "favourable" -> R.string.pr_lean_good; "against" -> R.string.pr_lean_wait; else -> R.string.pr_lean_mixed }),
                    style = MaterialTheme.typography.titleLarge, color = Palette.AccentDeep, modifier = Modifier.testTag("q_lean"))
                Text(b(o.optJSONObject("summary")), style = MaterialTheme.typography.bodyMedium)
            }
        }
        o.optJSONArray("checks")?.let { a ->
            for (i in 0 until a.length()) {
                val c = a.getJSONObject(i)
                Row { Text(if (c.optBoolean("ok")) "✓  " else "•  ", color = if (c.optBoolean("ok")) Palette.AccentDeep else Palette.Muted)
                    Text(b(c.optJSONObject("text")), style = MaterialTheme.typography.bodyMedium) }
            }
        }
        o.optJSONObject("ascendant")?.let { a ->
            Text(stringResource(R.string.kp_asc, o.optInt("number"), Names.of(a.optString("sign"), lang), a.optDouble("from_deg"), Names.of(a.optString("star_lord"), lang), Names.of(a.optString("sub_lord"), lang)),
                style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
            o.optJSONArray("ruling_planets")?.let { r ->
                Text(stringResource(R.string.kp_ruling, (0 until r.length()).joinToString(", ") { Names.of(r.getString(it), lang) }), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
            }
        }
        Text(b(o.optJSONObject("note")), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
    }
}

private fun questionName(q: String) = when (q) {
    "marriage" -> R.string.q_marriage
    "job" -> R.string.q_job
    "money" -> R.string.q_money
    "property" -> R.string.q_property
    "travel" -> R.string.q_travel
    "education" -> R.string.q_education
    "children" -> R.string.q_children
    else -> R.string.q_lost
}
