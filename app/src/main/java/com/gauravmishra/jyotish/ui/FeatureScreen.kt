package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.ChartState
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.Profile
import org.json.JSONObject

/** Stand-in for the Kundali, Milan, Muhurta and Numerology screens until milestones M2 to M5. */
@Composable
fun FeatureScreen(feature: Feature, profile: Profile?, chart: ChartState?, onHome: () -> Unit, onFeature: (Feature) -> Unit) {
    val lang = currentLang()
    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        topBar = { BackBar(stringResource(feature.title), onHome, subtitle = profile?.name) },
        bottomBar = { BottomNav(current = feature, onHome = onHome, onFeature = onFeature) },
    ) { pad ->
        Column(
            Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            if (profile == null) {
                Text(stringResource(R.string.pick_profile_first), style = MaterialTheme.typography.bodyLarge)
                return@Column
            }
            Text(stringResource(R.string.coming_body), style = MaterialTheme.typography.bodyLarge)
            when (chart) {
                is ChartState.Ready -> Text(planetTable(chart.json, lang), fontFamily = FontFamily.Monospace, style = MaterialTheme.typography.bodySmall)
                is ChartState.Failed -> Text(stringResource(R.string.chart_failed, chart.message))
                else -> Text(stringResource(R.string.calculating))
            }
        }
    }
}

private fun planetTable(json: String, lang: String): String {
    val v = JSONObject(json).getJSONObject("vedic")
    val sb = StringBuilder()
    val l = v.getJSONObject("lagna")
    sb.append("%-8s %-10s %s\n".format(if (lang == "hi") "लग्न" else "Lagna", Names.of(l.getString("sign"), lang), l.getString("dms")))
    val pl = v.getJSONObject("planets")
    for (p in pl.keys()) {
        val x = pl.getJSONObject(p)
        sb.append("%-8s %-10s %-12s %s %d\n".format(Names.of(p, lang), Names.of(x.getString("sign"), lang), x.getString("dms"), x.getString("nakshatra"), x.getInt("pada")))
    }
    return sb.toString()
}
