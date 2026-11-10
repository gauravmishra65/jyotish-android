package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
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
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.DetailSection
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.parseDmy
import com.gauravmishra.jyotish.data.parseSections
import com.gauravmishra.jyotish.engine.Engine
import kotlinx.coroutines.launch
import org.json.JSONObject

private val KINDS = listOf("pair", "business", "phone", "vehicle", "house", "personal")

/** Numerology tools (v16): couple compatibility, business name, mobile, vehicle and house numbers, personal days. */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun NumberToolsScreen(profiles: List<Profile>, profile: Profile?, onSelect: (Profile) -> Unit, onAdd: () -> Unit, onBack: () -> Unit) {
    val lang = currentLang()
    val scope = rememberCoroutineScope()
    var kind by remember { mutableStateOf("pair") }
    var text by remember { mutableStateOf("") }
    var otherName by remember { mutableStateOf("") }
    var otherDob by remember { mutableStateOf("") }
    var sections by remember { mutableStateOf<List<DetailSection>>(emptyList()) }
    var error by remember { mutableStateOf<String?>(null) }

    Scaffold(containerColor = MaterialTheme.colorScheme.background, topBar = { BackBar(stringResource(R.string.nt_title), onBack, subtitle = profile?.name) }) { pad ->
        Column(Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)) {
            ProfileBar(profiles, profile, { onSelect(it); sections = emptyList() }, onAdd)
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                KINDS.forEach { k ->
                    FilterChip(selected = kind == k, onClick = { kind = k; sections = emptyList(); text = "" }, label = { Text(stringResource(kindName(k))) },
                        modifier = Modifier.heightIn(min = 48.dp).testTag("nt_$k"),
                        colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep))
                }
            }
            when (kind) {
                "pair" -> {
                    Text(stringResource(R.string.nt_pair_note), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        profiles.filter { it.id != profile?.id }.forEach { p ->
                            AssistChip(onClick = { otherName = p.name; otherDob = p.date.split("-").reversed().joinToString("-") }, label = { Text(p.name) },
                                modifier = Modifier.heightIn(min = 48.dp))
                        }
                    }
                    OutlinedTextField(otherName, { otherName = it }, label = { Text(stringResource(R.string.nt_other_name)) }, singleLine = true,
                        modifier = Modifier.fillMaxWidth().testTag("nt_other_name"))
                    OutlinedTextField(otherDob, { otherDob = it }, label = { Text(stringResource(R.string.bt_date_hint)) }, singleLine = true,
                        modifier = Modifier.fillMaxWidth().testTag("nt_other_dob"))
                }
                "personal" -> {}
                else -> OutlinedTextField(text, { text = it }, label = { Text(stringResource(kindHint(kind))) }, singleLine = true,
                    modifier = Modifier.fillMaxWidth().testTag("nt_text"))
            }
            val otherDate = parseDmy(otherDob)
            val ready = profile != null && when (kind) {
                "pair" -> otherName.isNotBlank() && otherDate != null
                "personal" -> true
                else -> text.isNotBlank()
            }
            Button(enabled = ready, onClick = {
                val p = profile ?: return@Button
                val req = JSONObject().put("kind", kind).put("dob", p.date).put("text", text)
                    .put("a_name", p.name).put("a_dob", p.date).put("b_name", otherName.trim()).put("b_dob", otherDate?.toString() ?: "")
                error = null
                scope.launch {
                    try { sections = parseSections(JSONObject(Engine.numberTools(req)).optJSONArray("sections")) } catch (t: Throwable) { error = t.message }
                }
            }, modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp).testTag("nt_run")) { Text(stringResource(R.string.nt_run)) }
            error?.let { Text(stringResource(R.string.bt_failed, it)) }
            sections.forEach { androidx.compose.runtime.key(it.title.en) { SectionCard(it, lang, startOpen = true) } }
        }
    }
}

private fun kindName(k: String) = when (k) {
    "pair" -> R.string.nt_pair
    "business" -> R.string.nt_business
    "phone" -> R.string.nt_phone
    "vehicle" -> R.string.nt_vehicle
    "house" -> R.string.nt_house
    else -> R.string.nt_personal
}

private fun kindHint(k: String) = when (k) {
    "business" -> R.string.nt_business_hint
    "phone" -> R.string.nt_phone_hint
    "vehicle" -> R.string.nt_vehicle_hint
    else -> R.string.nt_house_hint
}
