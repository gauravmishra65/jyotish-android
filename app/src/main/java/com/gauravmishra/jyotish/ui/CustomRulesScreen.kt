package com.gauravmishra.jyotish.ui

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
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.DetailSection
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.parseSections
import com.gauravmishra.jyotish.engine.Engine
import kotlinx.coroutines.launch
import org.json.JSONArray
import org.json.JSONObject

private val PLANETS = listOf("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")

/**
 * Your own rules (v27): a divisional chart for any division you name, and a yoga you define yourself, tested against
 * every saved person. Nothing here is interpreted: the chart is drawn and the rule says only whether it holds.
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun CustomRulesScreen(profiles: List<Profile>, profile: Profile?, ayanamsa: String, node: String, onBack: () -> Unit) {
    val lang = currentLang()
    var nText by rememberSaveable { mutableStateOf("7") }
    var rule by rememberSaveable { mutableStateOf("cyclic") }
    var vargaSections by remember { mutableStateOf<List<DetailSection>>(emptyList()) }
    var ruleSections by remember { mutableStateOf<List<DetailSection>>(emptyList()) }
    var planet by rememberSaveable { mutableStateOf("Jupiter") }
    var kind by rememberSaveable { mutableStateOf("house") }
    var value by rememberSaveable { mutableStateOf("1") }
    val conditions = remember { mutableStateListOf<Triple<String, String, String>>() }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()
    val today = java.time.LocalDate.now().toString()

    Scaffold(containerColor = MaterialTheme.colorScheme.background,
        topBar = { BackBar(stringResource(R.string.cr_title), onBack, subtitle = profile?.name) }) { pad ->
        Column(Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)) {
            if (profile == null) {
                Text(stringResource(R.string.pick_profile_first), style = MaterialTheme.typography.bodyLarge)
                return@Column
            }
            Text(stringResource(R.string.cr_varga_title), style = MaterialTheme.typography.titleMedium)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(value = nText, onValueChange = { nText = it.filter { c -> c.isDigit() }.take(2) },
                    label = { Text(stringResource(R.string.cr_division)) }, singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.weight(1f).testTag("cr_n"))
            }
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                PickChip(stringResource(R.string.cr_from_aries), rule == "cyclic") { rule = "cyclic" }
                PickChip(stringResource(R.string.cr_from_sign), rule == "from_sign") { rule = "from_sign" }
            }
            Button(enabled = !busy && (nText.toIntOrNull() ?: 0) >= 2,
                onClick = {
                    scope.launch {
                        busy = true; error = null
                        try {
                            val req = profile.chartRequest(today, ayanamsa, node).put("n", nText.toInt()).put("rule", rule)
                            vargaSections = parseSections(JSONObject(Engine.customVarga(req)).optJSONArray("sections"))
                        } catch (t: Throwable) { error = t.message }
                        busy = false
                    }
                },
                modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp).testTag("cr_varga_go")) { Text(stringResource(R.string.cr_draw)) }
            vargaSections.forEach { SectionCard(it, lang, startOpen = true) }

            HorizontalDivider()
            Text(stringResource(R.string.cr_yoga_title), style = MaterialTheme.typography.titleMedium)
            FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                PLANETS.forEach { p -> PickChip(p, planet == p) { planet = p } }
            }
            FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                PickChip(stringResource(R.string.cr_in_house), kind == "house") { kind = "house" }
                PickChip(stringResource(R.string.cr_in_sign), kind == "sign") { kind = "sign" }
                PickChip(stringResource(R.string.cr_with), kind == "with") { kind = "with" }
                PickChip(stringResource(R.string.cr_opposite), kind == "aspects") { kind = "aspects" }
            }
            OutlinedTextField(value = value, onValueChange = { value = it.take(12) }, singleLine = true,
                label = {
                    Text(when (kind) {
                        "house" -> stringResource(R.string.cr_house_no)
                        "sign" -> stringResource(R.string.cr_sign_name)
                        else -> stringResource(R.string.cr_other_planet)
                    })
                },
                modifier = Modifier.fillMaxWidth().testTag("cr_value"))
            OutlinedButton(onClick = { if (conditions.size < 6) conditions.add(Triple(planet, kind, value.trim())) },
                modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp).testTag("cr_add")) { Text(stringResource(R.string.cr_add)) }
            conditions.forEachIndexed { i, (p, k, v) ->
                Text("$p · $k · $v", style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.fillMaxWidth().testTag("cr_cond_$i"))
            }
            if (conditions.isNotEmpty()) {
                OutlinedButton(onClick = { conditions.clear(); ruleSections = emptyList() },
                    modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp).testTag("cr_clear")) { Text(stringResource(R.string.cr_clear)) }
            }
            Button(enabled = !busy && conditions.isNotEmpty(),
                onClick = {
                    scope.launch {
                        busy = true; error = null
                        try {
                            val conds = JSONArray()
                            conditions.forEach { (p, k, v) -> conds.put(JSONObject().put("planet", p).put("in", k).put("value", v)) }
                            val people = JSONArray()
                            profiles.take(12).forEach { people.put(it.chartRequest(today, ayanamsa, node)) }
                            val req = JSONObject()
                                .put("rule", JSONObject().put("name", "").put("conditions", conds).put("all", true))
                                .put("people", people)
                            ruleSections = parseSections(JSONObject(Engine.customRule(req)).optJSONArray("sections"))
                        } catch (t: Throwable) { error = t.message }
                        busy = false
                    }
                },
                modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp).testTag("cr_check")) { Text(stringResource(R.string.cr_check)) }
            if (busy) LinearProgressIndicator(Modifier.fillMaxWidth())
            error?.let { Text(stringResource(R.string.chart_failed, it), style = MaterialTheme.typography.bodyMedium) }
            ruleSections.forEach { SectionCard(it, lang, startOpen = true) }
        }
    }
}

@Composable
private fun PickChip(label: String, selected: Boolean, onClick: () -> Unit) {
    androidx.compose.material3.FilterChip(
        selected = selected, onClick = onClick, label = { Text(label) },
        modifier = Modifier.heightIn(min = 48.dp),
        colors = androidx.compose.material3.FilterChipDefaults.filterChipColors(
            selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep),
    )
}
