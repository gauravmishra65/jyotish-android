package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Place
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.Place
import com.gauravmishra.jyotish.data.Places
import com.gauravmishra.jyotish.data.Villages
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext

/** A chosen place, or a search box with up to six offline matches. */
@Composable
fun PlaceField(chosen: Place?, loadPlaces: suspend () -> Places, onChoose: (Place?) -> Unit, tag: String = "place") {
    if (chosen != null) {
        Surface(shape = RoundedCornerShape(12.dp), color = Palette.AccentSoft, border = BorderStroke(1.dp, Palette.Accent)) {
            Row(Modifier.fillMaxWidth().padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Filled.Place, contentDescription = null, tint = Palette.AccentDeep)
                Column(Modifier.weight(1f).padding(start = 8.dp)) {
                    Text(chosen.label, style = MaterialTheme.typography.titleMedium)
                    Text("%.3f, %.3f · %s".format(chosen.lat, chosen.lon, chosen.tz), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
                }
                TextButton(onClick = { onChoose(null) }, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.change_place)) }
            }
        }
        return
    }
    var query by remember { mutableStateOf("") }
    var places by remember { mutableStateOf<Places?>(null) }
    var results by remember { mutableStateOf(emptyList<Place>()) }
    LaunchedEffect(Unit) { places = loadPlaces() }
    val appCtx = androidx.compose.ui.platform.LocalContext.current.applicationContext
    LaunchedEffect(query, places) {
        delay(150)
        val p = places
        results = if (p == null) emptyList() else withContext(Dispatchers.Default) { p.search(query, 6) }
        // villages and small towns of India and Nepal below the towns ("Rampur, Moradabad" narrows by district)
        if (p != null && query.trim().length >= 3) {
            val more = withContext(Dispatchers.IO) { runCatching { Villages.search(appCtx, query, p.countryNames, maxOf(4, 10 - results.size)) }
                .onFailure { android.util.Log.e("PLACES", "village search Exception", it) }.getOrDefault(emptyList()) }
            android.util.Log.i("PLACES", "'$query': ${results.size} towns, ${more.size} villages")
            results = results + more.filter { v -> results.none { it.name == v.name && kotlin.math.abs(it.lat - v.lat) < 0.02 } }
        }
    }
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        OutlinedTextField(query, { query = it }, label = { Text(stringResource(R.string.place_hint)) }, singleLine = true,
            modifier = Modifier.fillMaxWidth().testTag(tag))
        when {
            places == null -> Text(stringResource(R.string.place_loading), style = MaterialTheme.typography.bodySmall)
            query.trim().length >= 2 && results.isEmpty() -> Text(stringResource(R.string.place_none), style = MaterialTheme.typography.bodySmall)
        }
        results.forEach { p ->
            Surface(
                onClick = { onChoose(p) }, shape = RoundedCornerShape(10.dp), color = MaterialTheme.colorScheme.surface,
                border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant), modifier = Modifier.fillMaxWidth().testTag("${tag}_result"),
            ) {
                Column(Modifier.padding(horizontal = 14.dp, vertical = 10.dp)) {
                    Text(p.label + (p.hindiNames.firstOrNull()?.let { "  $it" } ?: ""), style = MaterialTheme.typography.bodyLarge)
                    Text("%.3f, %.3f · %s".format(p.lat, p.lon, p.tz), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
                }
            }
        }
    }
}
