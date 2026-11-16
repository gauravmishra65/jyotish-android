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
import androidx.compose.material3.Button
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.DetailSection
import com.gauravmishra.jyotish.data.parseSections
import com.gauravmishra.jyotish.engine.Engine
import kotlinx.coroutines.launch
import org.json.JSONObject
import java.time.LocalDateTime

/**
 * Western horary (v30): the chart of the moment the question is asked, at the place you are now, with the traditional
 * considerations before judgement. The app lays out what the chart shows; it does not answer the question.
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun HoraryScreen(place: TodayPlace?, onBack: () -> Unit) {
    val lang = currentLang()
    var house by rememberSaveable { mutableIntStateOf(7) }
    var sections by remember { mutableStateOf<List<DetailSection>>(emptyList()) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()

    Scaffold(containerColor = MaterialTheme.colorScheme.background,
        topBar = { BackBar(stringResource(R.string.hor_title), onBack) }) { pad ->
        Column(Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text(stringResource(R.string.hor_house), style = MaterialTheme.typography.titleMedium)
            FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                (1..12).forEach { h ->
                    FilterChip(selected = house == h, onClick = { house = h }, label = { Text("$h") },
                        modifier = Modifier.heightIn(min = 48.dp).testTag("hor_house_$h"),
                        colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep))
                }
            }
            Button(enabled = !busy,
                onClick = {
                    scope.launch {
                        busy = true; error = null
                        try {
                            val now = LocalDateTime.now()
                            val req = JSONObject().put("date", now.toLocalDate().toString())
                                .put("time", "%02d:%02d".format(now.hour, now.minute))
                                .put("lat", place?.lat ?: 0.0).put("lon", place?.lon ?: 0.0)
                                .put("tz", place?.tz ?: java.time.ZoneId.systemDefault().id).put("house", house)
                            sections = parseSections(JSONObject(Engine.horary(req)).optJSONArray("sections"))
                        } catch (t: Throwable) { error = t.message }
                        busy = false
                    }
                },
                modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp).testTag("hor_ask")) { Text(stringResource(R.string.hor_ask)) }
            if (busy) LinearProgressIndicator(Modifier.fillMaxWidth())
            error?.let { Text(stringResource(R.string.chart_failed, it), style = MaterialTheme.typography.bodyMedium) }
            sections.forEach { SectionCard(it, lang, startOpen = true) }
        }
    }
}
