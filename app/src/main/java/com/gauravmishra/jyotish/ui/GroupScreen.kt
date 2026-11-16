package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.runtime.toMutableStateList
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.DetailSection
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.parseSections
import com.gauravmishra.jyotish.engine.Engine
import kotlinx.coroutines.launch
import org.json.JSONArray
import org.json.JSONObject

/** Group (v26): two to six saved people side by side, with what the group shares. */
@Composable
fun GroupScreen(profiles: List<Profile>, ayanamsa: String, node: String, onAdd: () -> Unit, onBack: () -> Unit) {
    val lang = currentLang()
    val picked = remember(profiles) { profiles.take(3).map { it.id }.toMutableStateList() }
    var sections by remember { mutableStateOf<List<DetailSection>>(emptyList()) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()
    val today = java.time.LocalDate.now().toString()

    Scaffold(containerColor = MaterialTheme.colorScheme.background,
        topBar = { BackBar(stringResource(R.string.grp_title), onBack) }) { pad ->
        Column(Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)) {
            if (profiles.size < 2) {
                Text(stringResource(R.string.grp_need_two), style = MaterialTheme.typography.bodyLarge)
                Button(onClick = onAdd, modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp).testTag("grp_add")) {
                    Text(stringResource(R.string.grp_title))
                }
                return@Column
            }
            Text(stringResource(R.string.grp_pick), style = MaterialTheme.typography.bodyMedium, color = Palette.Muted)
            profiles.forEach { p ->
                val on = picked.contains(p.id)
                androidx.compose.material3.FilterChip(
                    selected = on,
                    onClick = { if (on) picked.remove(p.id) else if (picked.size < 6) picked.add(p.id) },
                    label = { Text(p.name) },
                    modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp).testTag("grp_${p.id}"),
                )
            }
            Button(
                enabled = !busy && picked.size >= 2,
                onClick = {
                    scope.launch {
                        busy = true; error = null
                        try {
                            val people = JSONArray()
                            profiles.filter { picked.contains(it.id) }.forEach { people.put(it.chartRequest(today, ayanamsa, node)) }
                            sections = parseSections(JSONObject(Engine.group(JSONObject().put("people", people))).optJSONArray("sections"))
                        } catch (t: Throwable) { error = t.message }
                        busy = false
                    }
                },
                modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp).testTag("grp_compare"),
            ) { Text(stringResource(R.string.grp_compare)) }
            if (busy) LinearProgressIndicator(Modifier.fillMaxWidth())
            error?.let { Text(stringResource(R.string.chart_failed, it), style = MaterialTheme.typography.bodyMedium) }
            sections.forEach { SectionCard(it, lang, startOpen = true) }
        }
    }
}
