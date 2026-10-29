package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.ArrowDropDown
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
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
import androidx.compose.ui.window.Dialog
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.Profile

/** The chosen person as a tappable card; tapping opens the list of saved Kundlis. */
@Composable
fun PersonField(label: String, chosen: Profile?, modifier: Modifier = Modifier, onClick: () -> Unit) {
    val lang = currentLang()
    Surface(
        onClick = onClick, shape = RoundedCornerShape(12.dp), color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline), modifier = modifier.heightIn(min = 56.dp),
    ) {
        Row(Modifier.padding(start = 12.dp, end = 4.dp, top = 8.dp, bottom = 8.dp), verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text(label, style = MaterialTheme.typography.labelMedium, color = Palette.Muted)
                Text(chosen?.name ?: stringResource(R.string.choose_person), style = MaterialTheme.typography.titleMedium, maxLines = 1,
                    overflow = TextOverflow.Ellipsis)
                chosen?.let {
                    Text(prettyDate(it.date, lang) + " · " + it.place.substringBefore(","), style = MaterialTheme.typography.bodySmall,
                        color = Palette.Muted, maxLines = 1, overflow = TextOverflow.Ellipsis)
                }
            }
            Icon(Icons.Filled.ArrowDropDown, contentDescription = null, tint = Palette.Accent)
        }
    }
}

/**
 * The person a screen works on: shows who is chosen, lets the user pick any saved Kundli (with search) or add a new
 * person. Shown even with one or no saved profiles, so adding is always one tap away.
 */
@Composable
fun ProfileBar(profiles: List<Profile>, profile: Profile?, onSelect: (Profile) -> Unit, onAdd: () -> Unit) {
    var open by rememberSaveable { mutableStateOf(false) }
    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        PersonField(stringResource(R.string.person_label), profile, Modifier.weight(1f).testTag("person_picker")) { open = true }
        OutlinedButton(onClick = onAdd, modifier = Modifier.heightIn(min = 56.dp).testTag("person_new"), shape = RoundedCornerShape(12.dp)) {
            Icon(Icons.Filled.Add, contentDescription = null, modifier = Modifier.size(18.dp))
            Text(stringResource(R.string.person_new), modifier = Modifier.padding(start = 4.dp))
        }
    }
    if (open) {
        ProfilePickerDialog(stringResource(R.string.pick_person_title), profiles, profile?.id,
            onPick = { open = false; onSelect(it) }, onAdd = { open = false; onAdd() }, onDismiss = { open = false })
    }
}

/** Searchable list of saved Kundlis with an "add a new person" action at the top. */
@Composable
fun ProfilePickerDialog(
    title: String,
    profiles: List<Profile>,
    selectedId: String?,
    onPick: (Profile) -> Unit,
    onAdd: () -> Unit,
    onDismiss: () -> Unit,
) {
    val lang = currentLang()
    var query by remember { mutableStateOf("") }
    val shown = filterProfiles(profiles, query, "")
    Dialog(onDismissRequest = onDismiss) {
        Surface(shape = RoundedCornerShape(20.dp), color = MaterialTheme.colorScheme.surface, modifier = Modifier.fillMaxWidth()) {
            Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text(title, style = MaterialTheme.typography.titleLarge)
                OutlinedButton(onClick = onAdd, modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp).testTag("pick_add"),
                    shape = RoundedCornerShape(12.dp)) {
                    Icon(Icons.Filled.Add, contentDescription = null, modifier = Modifier.size(18.dp))
                    Text(stringResource(R.string.add_new_person), modifier = Modifier.padding(start = 6.dp))
                }
                if (profiles.size > 5) {
                    OutlinedTextField(query, { query = it }, singleLine = true, placeholder = { Text(stringResource(R.string.saved_search)) },
                        leadingIcon = { Icon(Icons.Filled.Search, contentDescription = null) }, modifier = Modifier.fillMaxWidth().testTag("pick_search"))
                }
                if (profiles.isEmpty()) Text(stringResource(R.string.no_profiles), color = Palette.Muted)
                else if (shown.isEmpty()) Text(stringResource(R.string.saved_none), color = Palette.Muted)
                LazyColumn(Modifier.heightIn(max = 380.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    items(shown, key = { it.id }) { p ->
                        val sel = p.id == selectedId
                        Surface(onClick = { onPick(p) }, shape = RoundedCornerShape(12.dp),
                            color = if (sel) Palette.AccentSoft else MaterialTheme.colorScheme.surface,
                            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
                            modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp).testTag("pick_${p.name}")) {
                            Row(Modifier.padding(horizontal = 10.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                                Box(Modifier.size(36.dp).background(Palette.AccentSoft, CircleShape), contentAlignment = Alignment.Center) {
                                    Text(p.initials, color = Palette.AccentDeep, style = MaterialTheme.typography.labelLarge)
                                }
                                Column(Modifier.weight(1f)) {
                                    Text(p.name, style = MaterialTheme.typography.titleSmall, maxLines = 1, overflow = TextOverflow.Ellipsis)
                                    Text(prettyDate(p.date, lang) + " · " + p.place.substringBefore(","), style = MaterialTheme.typography.bodySmall,
                                        color = Palette.Muted, maxLines = 1, overflow = TextOverflow.Ellipsis)
                                }
                                if (sel) Icon(Icons.Filled.Check, contentDescription = null, tint = Palette.Accent)
                            }
                        }
                    }
                }
                TextButton(onClick = onDismiss, modifier = Modifier.align(Alignment.End).heightIn(min = 48.dp)) { Text(stringResource(R.string.cancel)) }
            }
        }
    }
}
