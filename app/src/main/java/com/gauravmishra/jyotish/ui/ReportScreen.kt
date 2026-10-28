package com.gauravmishra.jyotish.ui

import android.content.Context
import android.content.Intent
import android.print.PrintAttributes
import android.print.PrintManager
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
import com.gauravmishra.jyotish.ReportState
import com.gauravmishra.jyotish.data.Profile

/**
 * The full multi-system reading (engine_api.report) in a WebView, in English or Hindi, with Save as PDF (the system
 * print dialog) and Share (the HTML file).
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun ReportScreen(
    profiles: List<Profile>,
    profile: Profile?,
    reports: Map<String, ReportState>,
    onSelect: (Profile) -> Unit,
    onRequest: (Profile, String) -> Unit,
    onBack: () -> Unit,
) {
    val appLang = currentLang()
    var lang by rememberSaveable { mutableStateOf(if (appLang == "hi") "hi" else "en") }
    LaunchedEffect(profile?.id, lang) { profile?.let { onRequest(it, lang) } }
    val state = profile?.let { reports["${it.id}|$lang"] }
    val ctx = LocalContext.current
    var webView by remember { mutableStateOf<WebView?>(null) }

    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        topBar = { BackBar(stringResource(R.string.report_title), onBack, subtitle = profile?.name) },
    ) { pad ->
        Column(Modifier.fillMaxSize().padding(pad)) {
            Column(Modifier.padding(horizontal = 16.dp, vertical = 4.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                if (profiles.size > 1) {
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        profiles.forEach { p ->
                            FilterChip(selected = p.id == profile?.id, onClick = { onSelect(p) }, label = { Text(p.name) },
                                modifier = Modifier.heightIn(min = 48.dp),
                                colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Palette.AccentSoft, selectedLabelColor = Palette.AccentDeep))
                        }
                    }
                }
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
            // One WebView for the whole screen: switching language loads the other page into it, so no second
            // WebView is ever created over the controls. While a page is being written, the progress shows above it.
            when (state) {
                null, ReportState.Calculating -> Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    if (profile == null) Text(stringResource(R.string.pick_profile_first)) else {
                        Text(stringResource(R.string.report_working), style = MaterialTheme.typography.bodyLarge)
                        LinearProgressIndicator(Modifier.fillMaxWidth(), color = Palette.Accent)
                    }
                }
                is ReportState.Failed -> Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text(stringResource(R.string.report_failed, state.message))
                    OutlinedButton(onClick = { profile?.let { onRequest(it, lang) } }, modifier = Modifier.heightIn(min = 48.dp)) { Text(stringResource(R.string.fc_retry)) }
                }
                is ReportState.Ready -> Unit
            }
            val html = (state as? ReportState.Ready)?.html
            if (html != null || webView != null) {
                AndroidView(
                    factory = { c ->
                        WebView(c).apply {
                            settings.javaScriptEnabled = true      // only the report's own section-nav script
                            settings.allowFileAccess = false
                            settings.allowContentAccess = false
                            webViewClient = WebViewClient()
                            webView = this
                        }
                    },
                    update = { wv ->
                        if (html != null && wv.tag != html.hashCode()) {
                            wv.tag = html.hashCode()
                            wv.loadDataWithBaseURL(null, html, "text/html", "utf-8", null)
                        }
                    },
                    modifier = Modifier.fillMaxSize().testTag("report_view"),
                )
            }
        }
    }
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
