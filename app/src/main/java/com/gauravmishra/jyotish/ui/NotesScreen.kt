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
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.parseDmy

val EVENT_KINDS_ALL = listOf("marriage", "child", "job", "property", "abroad", "education")

fun eventLabel(kind: String) = when (kind) {
    "marriage" -> R.string.bt_ev_marriage
    "child" -> R.string.bt_ev_child
    "job" -> R.string.bt_ev_job
    "property" -> R.string.bt_ev_property
    "abroad" -> R.string.bt_ev_abroad
    else -> R.string.bt_ev_education
}

/** Notes and dated life events for each saved person (v20); the Birth time check starts from these events. */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun NotesScreen(profiles: List<Profile>, profile: Profile?, onSelect: (Profile) -> Unit, onAdd: () -> Unit, onSave: (Profile) -> Unit, onBack: () -> Unit) {
    if (profile == null) {
        Scaffold(topBar = { BackBar(stringResource(R.string.nb_title), onBack) }) { pad ->
            Text(stringResource(R.string.pick_profile_first), Modifier.padding(pad).padding(20.dp))
        }
        return
    }
    androidx.compose.runtime.key(profile.id) {
        var notes by remember { mutableStateOf(profile.notes) }
        val events = remember { mutableStateListOf<String>().apply { addAll(profile.events) } }
        var kind by remember { mutableStateOf("marriage") }
        var dateText by remember { mutableStateOf("") }
        var saved by remember { mutableStateOf(false) }
        Scaffold(containerColor = MaterialTheme.colorScheme.background, topBar = { BackBar(stringResource(R.string.nb_title), onBack, subtitle = profile.name) }) { pad ->
            Column(Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)) {
                ProfileBar(profiles, profile, onSelect, onAdd)
                Text(stringResource(R.string.nb_notes), style = MaterialTheme.typography.titleMedium)
                OutlinedTextField(notes, { notes = it; saved = false }, label = { Text(stringResource(R.string.nb_notes_hint)) },
                    minLines = 4, modifier = Modifier.fillMaxWidth().testTag("nb_notes"))
                Text(stringResource(R.string.nb_events), style = MaterialTheme.typography.titleMedium)
                FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    EVENT_KINDS_ALL.forEach { k ->
                        FilterChip(selected = kind == k, onClick = { kind = k }, label = { Text(stringResource(eventLabel(k))) },
                            modifier = Modifier.heightIn(min = 48.dp).testTag("nb_kind_$k"),
                            colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep))
                    }
                }
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedTextField(dateText, { dateText = it }, label = { Text(stringResource(R.string.bt_date_hint)) }, singleLine = true,
                        modifier = Modifier.weight(1f).testTag("nb_date"))
                    val d = parseDmy(dateText)
                    OutlinedButton(enabled = d != null, onClick = { d?.let { events += "$it:$kind"; events.sortDescending(); dateText = ""; saved = false } },
                        modifier = Modifier.heightIn(min = 52.dp).testTag("nb_add")) { Text(stringResource(R.string.bt_add)) }
                }
                events.toList().forEach { e ->
                    val (date, k) = e.split(":").let { it[0] to it.getOrElse(1) { "" } }
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text("${stringResource(eventLabel(k))} · $date", style = MaterialTheme.typography.bodyMedium, modifier = Modifier.weight(1f))
                        TextButton(onClick = { events.remove(e); saved = false }, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.bt_remove)) }
                    }
                }
                Button(onClick = { onSave(profile.copy(notes = notes.trim(), events = events.toList())); saved = true },
                    modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp).testTag("nb_save")) { Text(stringResource(R.string.nb_save)) }
                if (saved) Text(stringResource(R.string.nb_saved), color = Palette.AccentDeep, modifier = Modifier.testTag("nb_saved"))
                Text(stringResource(R.string.nb_privacy), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
            }
        }
    }
}
