package com.gauravmishra.jyotish.ui

import android.content.Context
import android.content.Intent
import android.print.PrintAttributes
import android.print.PrintManager
import android.view.ViewGroup
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.FileProvider
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.REPORT_KINDS
import com.gauravmishra.jyotish.ReportState
import com.gauravmishra.jyotish.data.Profile

/**
 * Reports in a WebView, in English or Hindi, with Save as PDF (the system print dialog) and Share (the HTML file):
 * the full multi-system reading (engine_api.report) and the focused ones (engine_api.special_report): Daily, Monthly,
 * Annual, Mahadasha, Mangal Dosh, Kaal Sarp, Sade Sati and Chandra Rashi.
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun ReportScreen(
    profiles: List<Profile>,
    profile: Profile?,
    reports: Map<String, ReportState>,
    onSelect: (Profile) -> Unit,
    onAdd: () -> Unit,
    onRequest: (Profile, String, String) -> Unit,
    onBack: () -> Unit,
    initialKind: String = "life",
) {
    val appLang = currentLang()
    var lang by rememberSaveable { mutableStateOf(if (appLang == "hi") "hi" else "en") }
    var kind by rememberSaveable { mutableStateOf(initialKind) }
    LaunchedEffect(profile?.id, lang, kind) { profile?.let { onRequest(it, lang, kind) } }
    val state = profile?.let { reports["${it.id}|$lang|$kind"] }
    val ctx = LocalContext.current
    var webView by remember { mutableStateOf<WebView?>(null) }

    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        topBar = { BackBar(stringResource(R.string.report_title), onBack, subtitle = profile?.name) },
    ) { pad ->
        Column(Modifier.fillMaxSize().padding(pad)) {
            Column(Modifier.padding(horizontal = 16.dp, vertical = 4.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                ProfileBar(profiles, profile, onSelect, onAdd)
                LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.testTag("report_kinds")) {
                    items(REPORT_KINDS) { k ->
                        FilterChip(selected = kind == k, onClick = { kind = k }, label = { Text(stringResource(reportKindName(k))) },
                            modifier = Modifier.heightIn(min = 48.dp).testTag("report_kind_$k"),
                            colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep))
                    }
                }
                Text(stringResource(reportKindNote(kind)), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    listOf("en" to "English", "hi" to "हिंदी").forEach { (k, label) ->
                        FilterChip(selected = lang == k, onClick = { lang = k }, label = { Text(label) },
                            modifier = Modifier.heightIn(min = 48.dp).testTag("report_lang_$k"),
                            colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep))
                    }
                }
                if (state is ReportState.Ready) {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        OutlinedButton(onClick = { webView?.let { printToPdf(ctx, it, state.file.nameWithoutExtension) } },
                            modifier = Modifier.weight(1f).heightIn(min = 48.dp).testTag("report_pdf")) { Text(stringResource(R.string.report_pdf)) }
                        OutlinedButton(onClick = { share(ctx, state.file) },
                            modifier = Modifier.weight(1f).heightIn(min = 48.dp).testTag("report_share")) { Text(stringResource(R.string.report_share)) }
                    }
                }
            }
            when (state) {
                null, ReportState.Calculating -> Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    if (profile == null) Text(stringResource(R.string.pick_profile_first)) else {
                        Text(stringResource(if (kind == "life") R.string.report_working else R.string.report_working_short), style = MaterialTheme.typography.bodyLarge)
                        LinearProgressIndicator(Modifier.fillMaxWidth(), color = Palette.Accent)
                    }
                }
                is ReportState.Failed -> Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text(stringResource(R.string.report_failed, state.message))
                    OutlinedButton(onClick = { profile?.let { onRequest(it, lang, kind) } }, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.fc_retry)) }
                }
                is ReportState.Ready -> key(state.html) {
                    // A fresh WebView per page; the previous one is destroyed when it leaves, so nothing stale is drawn.
                    AndroidView(
                        factory = { c ->
                            WebView(c).apply {
                                settings.javaScriptEnabled = true      // only the report's own section-nav script
                                settings.allowFileAccess = false
                                settings.allowContentAccess = false
                                webViewClient = WebViewClient()
                                loadDataWithBaseURL(null, state.html, "text/html", "utf-8", null)
                                webView = this
                            }
                        },
                        onRelease = { wv ->
                            if (webView === wv) webView = null
                            wv.stopLoading()
                            (wv.parent as? ViewGroup)?.removeView(wv)
                            wv.destroy()
                        },
                        modifier = Modifier.fillMaxSize().testTag("report_view"),
                    )
                }
            }
        }
    }
}

fun reportKindName(kind: String): Int = when (kind) {
    "daily" -> R.string.rk_daily
    "monthly" -> R.string.rk_monthly
    "annual" -> R.string.rk_annual
    "mahadasha" -> R.string.rk_mahadasha
    "mangal" -> R.string.rk_mangal
    "kaal_sarp" -> R.string.rk_kaal_sarp
    "sade_sati" -> R.string.rk_sade_sati
    "chandra" -> R.string.rk_chandra
    else -> R.string.rk_life
}

private fun reportKindNote(kind: String): Int = when (kind) {
    "daily" -> R.string.rk_daily_note
    "monthly" -> R.string.rk_monthly_note
    "annual" -> R.string.rk_annual_note
    "mahadasha" -> R.string.rk_mahadasha_note
    "mangal" -> R.string.rk_mangal_note
    "kaal_sarp" -> R.string.rk_kaal_sarp_note
    "sade_sati" -> R.string.rk_sade_sati_note
    "chandra" -> R.string.rk_chandra_note
    else -> R.string.rk_life_note
}

private fun printToPdf(ctx: Context, wv: WebView, name: String) {
    val pm = ctx.getSystemService(Context.PRINT_SERVICE) as PrintManager
    pm.print(name, wv.createPrintDocumentAdapter(name), PrintAttributes.Builder().setMediaSize(PrintAttributes.MediaSize.ISO_A4).build())
}

private fun share(ctx: Context, file: java.io.File) {
    val uri = FileProvider.getUriForFile(ctx, ctx.packageName + ".reports", file)
    val send = Intent(Intent.ACTION_SEND).setType("text/html").putExtra(Intent.EXTRA_STREAM, uri)
        .putExtra(Intent.EXTRA_SUBJECT, file.nameWithoutExtension.replace('_', ' '))
        .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    ctx.startActivity(Intent.createChooser(send, null))
}
