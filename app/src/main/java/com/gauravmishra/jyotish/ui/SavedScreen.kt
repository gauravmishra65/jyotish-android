package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.Profile
import java.text.Normalizer

/** Group keys and their labels; "" means not in a group. */
val GROUPS = listOf("family" to R.string.group_family, "friends" to R.string.group_friends, "clients" to R.string.group_clients, "other" to R.string.group_other)

private fun fold(s: String) = Normalizer.normalize(s, Normalizer.Form.NFD).replace(Regex("\\p{M}+"), "").lowercase()

/** Profiles matching a search (name or place, accents ignored) and a group ("" = all). */
fun filterProfiles(all: List<Profile>, query: String, group: String): List<Profile> {
    val q = fold(query.trim())
    return all.filter { p -> (group.isEmpty() || p.group == group) && (q.isEmpty() || fold(p.name).contains(q) || fold(p.place).contains(q)) }
        .sortedBy { fold(it.name) }
}

/** Every saved Kundli: search, filter by group, open, edit, delete. */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun SavedScreen(
    profiles: List<Profile>,
    onOpen: (Profile) -> Unit,
    onEdit: (Profile) -> Unit,
    onDelete: (Profile) -> Unit,
    onAdd: () -> Unit,
    onBack: () -> Unit,
) {
    val lang = currentLang()
    var query by rememberSaveable { mutableStateOf("") }
    var group by rememberSaveable { mutableStateOf("") }
    var confirm by remember { mutableStateOf<Profile?>(null) }
    val shown = filterProfiles(profiles, query, group)

    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        topBar = { BackBar(stringResource(R.string.saved_title), onBack, subtitle = stringResource(R.string.saved_count, profiles.size)) },
    ) { pad ->
        Column(Modifier.fillMaxSize().padding(pad).padding(horizontal = 16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            OutlinedTextField(query, { query = it }, singleLine = true, placeholder = { Text(stringResource(R.string.saved_search)) },
                leadingIcon = { Icon(Icons.Filled.Search, contentDescription = null) }, modifier = Modifier.fillMaxWidth().testTag("saved_search"))
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                (listOf("" to R.string.group_all) + GROUPS).forEach { (k, label) ->
                    val n = if (k.isEmpty()) profiles.size else profiles.count { it.group == k }
                    FilterChip(selected = group == k, onClick = { group = k }, label = { Text("${stringResource(label)} ($n)") },
                        modifier = Modifier.heightIn(min = 48.dp).testTag("group_${k.ifEmpty { "all" }}"),
                        colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep))
                }
            }
            if (shown.isEmpty()) {
                Text(stringResource(if (profiles.isEmpty()) R.string.no_profiles else R.string.saved_none), style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant)
                TextButton(onClick = onAdd, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.add_profile), color = Palette.Accent) }
            }
            LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.weight(1f).testTag("saved_list")) {
                items(shown, key = { it.id }) { p ->
                    Surface(onClick = { onOpen(p) }, shape = RoundedCornerShape(14.dp), color = MaterialTheme.colorScheme.surface,
                        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant), modifier = Modifier.fillMaxWidth().testTag("saved_${p.name}")) {
                        Row(Modifier.padding(start = 12.dp).heightIn(min = 64.dp), verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                            Box(Modifier.size(40.dp).background(Palette.AccentSoft, CircleShape), contentAlignment = Alignment.Center) {
                                Text(p.initials, color = Palette.AccentDeep, style = MaterialTheme.typography.titleSmall)
                            }
                            Column(Modifier.weight(1f)) {
                                Text(p.name, style = MaterialTheme.typography.titleMedium, maxLines = 1, overflow = TextOverflow.Ellipsis)
                                Text(listOfNotNull(prettyDate(p.date, lang) + " · " + p.time, p.place.substringBefore(",").takeIf { it.isNotBlank() },
                                    GROUPS.firstOrNull { it.first == p.group }?.let { stringResource(it.second) }).joinToString(" · "),
                                    style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant, maxLines = 2)
                            }
                            IconButton(onClick = { onEdit(p) }, modifier = Modifier.size(48.dp)) {
                                Icon(Icons.Filled.Edit, contentDescription = stringResource(R.string.edit) + " " + p.name)
                            }
                            IconButton(onClick = { confirm = p }, modifier = Modifier.size(48.dp)) {
                                Icon(Icons.Filled.Delete, contentDescription = stringResource(R.string.delete) + " " + p.name)
                            }
                        }
                    }
                }
            }
        }
    }

    confirm?.let { p ->
        AlertDialog(
            onDismissRequest = { confirm = null },
            title = { Text(stringResource(R.string.delete_profile_title, p.name)) },
            text = { Text(stringResource(R.string.delete_profile_body)) },
            confirmButton = { TextButton(onClick = { confirm = null; onDelete(p) }, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.delete)) } },
            dismissButton = { TextButton(onClick = { confirm = null }, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.cancel)) } },
        )
    }
}
