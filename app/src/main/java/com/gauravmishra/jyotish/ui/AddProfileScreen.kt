package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.layout.size
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.material.icons.filled.Place
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.DatePicker
import androidx.compose.material3.DatePickerDialog
import androidx.compose.material3.ExperimentalMaterial3Api
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
import androidx.compose.material3.TimePicker
import androidx.compose.material3.rememberDatePickerState
import androidx.compose.material3.rememberTimePickerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.Place
import com.gauravmishra.jyotish.data.Places
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.DMY
import com.gauravmishra.jyotish.data.parseDmy
import com.gauravmishra.jyotish.data.parseHm
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneOffset

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun AddProfileScreen(
    existing: Profile?,
    loadPlaces: suspend () -> Places,
    onBack: () -> Unit,
    onSave: (Profile) -> Unit,
) {
    var name by rememberSaveable { mutableStateOf(existing?.name ?: "") }
    var gender by rememberSaveable { mutableStateOf(existing?.gender ?: "M") }
    var dateText by rememberSaveable { mutableStateOf(existing?.date?.let { LocalDate.parse(it).format(DMY) } ?: "") }
    var timeText by rememberSaveable { mutableStateOf(existing?.time ?: "") }
    var confidence by rememberSaveable { mutableStateOf(existing?.confidence ?: "reliable") }
    var query by rememberSaveable { mutableStateOf("") }
    var chosen by remember { mutableStateOf(existing?.let { Place(it.place, "", "", it.lat, it.lon, it.tz, 0, emptyList()) }) }
    var useCoords by rememberSaveable { mutableStateOf(false) }
    var residence by remember { mutableStateOf(existing?.takeIf { it.hasResidence }?.let { Place(it.residence, "", "", it.resLat!!, it.resLon!!, "", 0, emptyList()) }) }
    var latText by rememberSaveable { mutableStateOf("") }
    var lonText by rememberSaveable { mutableStateOf("") }
    var showErrors by rememberSaveable { mutableStateOf(false) }
    var showDate by remember { mutableStateOf(false) }
    var showTime by remember { mutableStateOf(false) }

    var places by remember { mutableStateOf<Places?>(null) }
    LaunchedEffect(Unit) { places = loadPlaces() }
    var results by remember { mutableStateOf(emptyList<Place>()) }
    LaunchedEffect(query, places) {
        delay(150)
        val p = places
        results = if (p == null) emptyList() else withContext(Dispatchers.Default) { p.search(query) }
    }

    val date = parseDmy(dateText)
    val time = parseHm(timeText)
    val lat = latText.trim().toDoubleOrNull()?.takeIf { it in -90.0..90.0 }
    val lon = lonText.trim().toDoubleOrNull()?.takeIf { it in -180.0..180.0 }
    val nearest = if (useCoords && lat != null && lon != null) places?.nearest(lat, lon) else null
    val place: Place? = if (useCoords) nearest?.let { n ->
        Place("%.4f, %.4f".format(lat, lon), n.countryCode, n.country, lat!!, lon!!, n.tz, 0, emptyList())
    } else chosen
    val valid = name.isNotBlank() && date != null && time != null && place != null

    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        topBar = { BackBar(stringResource(if (existing == null) R.string.new_chart else R.string.edit_chart), onBack) },
        bottomBar = {
            Surface(color = MaterialTheme.colorScheme.surface, shadowElevation = 4.dp) {
                Button(
                    onClick = {
                        if (!valid) { showErrors = true; return@Button }
                        onSave(Profile(
                            id = existing?.id ?: java.util.UUID.randomUUID().toString(),
                            name = name.trim(), gender = gender, date = date.toString(), time = time!!, confidence = confidence,
                            place = place!!.label, lat = place.lat, lon = place.lon, tz = place.tz,
                            residence = residence?.label ?: "", resLat = residence?.lat, resLon = residence?.lon,
                        ))
                    },
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 12.dp).heightIn(min = 56.dp).testTag("save"),
                    shape = RoundedCornerShape(28.dp),
                ) { Text(stringResource(R.string.save_show), style = MaterialTheme.typography.labelLarge) }
            }
        },
    ) { pad ->
        Column(
            Modifier.fillMaxSize().padding(pad).imePadding().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            OutlinedTextField(
                value = name, onValueChange = { name = it }, label = { Text(stringResource(R.string.name)) }, singleLine = true,
                isError = showErrors && name.isBlank(),
                supportingText = if (showErrors && name.isBlank()) ({ Text(stringResource(R.string.err_name)) }) else null,
                modifier = Modifier.fillMaxWidth().testTag("name"),
            )

            Text(stringResource(R.string.gender), style = MaterialTheme.typography.titleMedium)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Choice(stringResource(R.string.male), gender == "M") { gender = "M" }
                Choice(stringResource(R.string.female), gender == "F") { gender = "F" }
            }

            OutlinedTextField(
                value = dateText, onValueChange = { dateText = it.take(10) },
                label = { Text(stringResource(R.string.date_of_birth)) }, placeholder = { Text(stringResource(R.string.date_hint)) },
                singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                isError = showErrors && date == null,
                supportingText = if (showErrors && date == null) ({ Text(stringResource(R.string.err_date)) }) else ({ Text(stringResource(R.string.date_hint)) }),
                trailingIcon = { IconButton(onClick = { showDate = true }, modifier = Modifier.size(48.dp)) { Icon(Icons.Filled.DateRange, stringResource(R.string.pick_date)) } },
                modifier = Modifier.fillMaxWidth().testTag("date"),
            )
            OutlinedTextField(
                value = timeText, onValueChange = { timeText = it.take(5) },
                label = { Text(stringResource(R.string.time_of_birth)) }, placeholder = { Text(stringResource(R.string.time_hint)) },
                singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                isError = showErrors && time == null,
                supportingText = if (showErrors && time == null) ({ Text(stringResource(R.string.err_time)) }) else ({ Text(stringResource(R.string.time_hint)) }),
                trailingIcon = { TextButton(onClick = { showTime = true }, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.pick_time)) } },
                modifier = Modifier.fillMaxWidth().testTag("time"),
            )

            Text(stringResource(R.string.how_sure), style = MaterialTheme.typography.titleMedium)
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf("certificate" to R.string.conf_certificate, "reliable" to R.string.conf_reliable,
                    "approximate" to R.string.conf_approximate, "unknown" to R.string.conf_unknown).forEach { (k, label) ->
                    Choice(stringResource(label), confidence == k) { confidence = k }
                }
            }

            Text(stringResource(R.string.birthplace), style = MaterialTheme.typography.titleMedium)
            if (!useCoords) {
                val c = chosen
                if (c != null) {
                    Surface(shape = RoundedCornerShape(12.dp), color = Palette.AccentSoft, border = BorderStroke(1.dp, Palette.Accent)) {
                        Row(Modifier.fillMaxWidth().padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Filled.Place, contentDescription = null, tint = Palette.AccentDeep)
                            Column(Modifier.weight(1f).padding(start = 8.dp)) {
                                Text(c.label, style = MaterialTheme.typography.titleMedium)
                                Text("%.3f, %.3f · %s".format(c.lat, c.lon, c.tz), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            }
                            TextButton(onClick = { chosen = null }, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.change_place)) }
                        }
                    }
                } else {
                    OutlinedTextField(
                        value = query, onValueChange = { query = it }, label = { Text(stringResource(R.string.place_hint)) }, singleLine = true,
                        isError = showErrors, supportingText = if (showErrors) ({ Text(stringResource(R.string.err_place)) }) else null,
                        modifier = Modifier.fillMaxWidth().testTag("place"),
                    )
                    when {
                        places == null -> Text(stringResource(R.string.place_loading), style = MaterialTheme.typography.bodySmall)
                        query.trim().length >= 2 && results.isEmpty() -> Text(stringResource(R.string.place_none), style = MaterialTheme.typography.bodySmall)
                    }
                    results.forEach { p ->
                        Surface(
                            onClick = { chosen = p; query = "" },
                            shape = RoundedCornerShape(10.dp), color = MaterialTheme.colorScheme.surface,
                            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
                            modifier = Modifier.fillMaxWidth().testTag("place_result"),
                        ) {
                            Column(Modifier.padding(horizontal = 14.dp, vertical = 10.dp)) {
                                Text(p.label + (p.hindiNames.firstOrNull()?.let { "  $it" } ?: ""), style = MaterialTheme.typography.bodyLarge)
                                Text("%.3f, %.3f · %s".format(p.lat, p.lon, p.tz), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            }
                        }
                    }
                    Text(stringResource(R.string.place_help), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
                TextButton(onClick = { useCoords = true }, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.enter_coordinates)) }
            } else {
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    OutlinedTextField(latText, { latText = it }, label = { Text(stringResource(R.string.latitude)) }, singleLine = true,
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal), modifier = Modifier.weight(1f),
                        isError = latText.isNotBlank() && lat == null)
                    OutlinedTextField(lonText, { lonText = it }, label = { Text(stringResource(R.string.longitude)) }, singleLine = true,
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal), modifier = Modifier.weight(1f),
                        isError = lonText.isNotBlank() && lon == null)
                }
                if ((latText.isNotBlank() && lat == null) || (lonText.isNotBlank() && lon == null)) Text(stringResource(R.string.err_coords), color = MaterialTheme.colorScheme.error)
                if (nearest != null && lat != null && lon != null) {
                    Text(stringResource(R.string.tz_from_nearest, nearest.tz, nearest.label, places!!.distanceKm(lat, lon, nearest.lat, nearest.lon).toInt()),
                        style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
                TextButton(onClick = { useCoords = false }, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.search_places)) }
            }
            Text(stringResource(R.string.residence_title), style = MaterialTheme.typography.titleMedium)
            Text(stringResource(R.string.residence_help), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            PlaceField(residence, loadPlaces, { residence = it }, tag = "residence")
        }
    }

    if (showDate) {
        val initial = (date ?: LocalDate.of(1990, 1, 1)).atStartOfDay().toInstant(ZoneOffset.UTC).toEpochMilli()
        val state = rememberDatePickerState(initialSelectedDateMillis = initial, yearRange = 1800..LocalDate.now().year)
        DatePickerDialog(
            onDismissRequest = { showDate = false },
            confirmButton = {
                TextButton(onClick = {
                    state.selectedDateMillis?.let { dateText = Instant.ofEpochMilli(it).atZone(ZoneOffset.UTC).toLocalDate().format(DMY) }
                    showDate = false
                }) { Text(stringResource(R.string.ok)) }
            },
            dismissButton = { TextButton(onClick = { showDate = false }, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.cancel)) } },
        ) { DatePicker(state = state) }
    }
    if (showTime) {
        val (h, m) = (time ?: "12:00").split(":").map { it.toInt() }
        val state = rememberTimePickerState(initialHour = h, initialMinute = m, is24Hour = true)
        AlertDialog(
            onDismissRequest = { showTime = false },
            confirmButton = { TextButton(onClick = { timeText = "%02d:%02d".format(state.hour, state.minute); showTime = false }, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.ok)) } },
            dismissButton = { TextButton(onClick = { showTime = false }, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.cancel)) } },
            text = { TimePicker(state = state) },
        )
    }
}

@Composable
private fun Choice(label: String, selected: Boolean, onClick: () -> Unit) {
    FilterChip(
        selected = selected, onClick = onClick, label = { Text(label) },
        modifier = Modifier.heightIn(min = 48.dp).semantics { role = Role.RadioButton },
        colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep),
    )
}
