package com.gauravmishra.jyotish.ui

import android.content.ActivityNotFoundException
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.activity.compose.LocalActivity
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
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
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.BuildConfig
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.AppSettings
import com.gauravmishra.jyotish.store.Sales
import com.gauravmishra.jyotish.store.Store

/**
 * Turns the demo into the full version. The demo edition takes an unlock code (bought by payment link or email);
 * the Play edition takes a Google Play purchase only, as Play requires for apps it distributes.
 */
@Composable
fun UpgradeScreen(
    settings: AppSettings,
    shop: Store,
    full: Boolean,
    limitReached: Boolean,
    onUnlockCode: (email: String, code: String) -> Boolean,
    onPlayPurchase: () -> Unit,
    onBack: () -> Unit,
) {
    val ctx = LocalContext.current
    val activity = LocalActivity.current
    val play = BuildConfig.EDITION == "play"
    var email by rememberSaveable { mutableStateOf(settings.unlockEmail.ifBlank { settings.userEmail }) }
    var code by rememberSaveable { mutableStateOf("") }
    var message by remember { mutableStateOf<Int?>(null) }
    var price by remember { mutableStateOf<String?>(null) }
    LaunchedEffect(play) { if (play) shop.price { price = it } }

    Scaffold(containerColor = MaterialTheme.colorScheme.background, topBar = { BackBar(stringResource(R.string.up_title), onBack) }) { pad ->
        Column(
            Modifier.fillMaxSize().padding(pad).imePadding().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(14.dp)) {
                AppMark(size = 56.dp)
                Column {
                    Text(stringResource(R.string.app_name), style = MaterialTheme.typography.titleLarge)
                    Text(stringResource(if (full) R.string.up_edition_full else R.string.up_edition_demo), style = MaterialTheme.typography.bodyMedium,
                        color = Palette.Muted, modifier = Modifier.testTag("edition"))
                }
            }
            if (full) {
                Text(stringResource(R.string.up_done), style = MaterialTheme.typography.bodyLarge, modifier = Modifier.testTag("up_done"))
                if (settings.unlockedVia == "code") Text(stringResource(R.string.up_licensed_to, settings.unlockEmail), color = Palette.Muted)
                Button(onClick = onBack, modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp)) { Text(stringResource(R.string.up_continue)) }
                return@Column
            }
            if (limitReached) {
                Text(stringResource(R.string.up_limit, Sales.FREE_PROFILES), style = MaterialTheme.typography.bodyLarge,
                    color = Palette.AccentDeep, modifier = Modifier.fillMaxWidth().background(Palette.AccentSoft, RoundedCornerShape(12.dp))
                        .padding(12.dp).testTag("up_limit"))
            }
            Text(stringResource(R.string.up_what), style = MaterialTheme.typography.titleMedium)
            Text(stringResource(R.string.up_features), style = MaterialTheme.typography.bodyMedium)

            if (play) {
                Button(onClick = {
                    message = null
                    if (activity == null) { message = R.string.up_play_failed; return@Button }
                    shop.buy(activity) { r ->
                        when (r) {
                            Store.Purchase.UNLOCKED -> { onPlayPurchase() }
                            Store.Purchase.PENDING -> { message = R.string.up_play_pending }
                            Store.Purchase.CANCELLED -> {}
                            Store.Purchase.FAILED -> { message = R.string.up_play_failed }
                        }
                    }
                }, modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp).testTag("up_buy_play"), shape = RoundedCornerShape(28.dp)) {
                    Text(price?.let { stringResource(R.string.up_buy_play_price, it) } ?: stringResource(R.string.up_buy_play))
                }
                TextButton(onClick = { shop.owned { if (it == true) { onPlayPurchase() } else { message = R.string.up_play_none } } },
                    modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp)) { Text(stringResource(R.string.up_restore)) }
            } else {
                SectionLabel(stringResource(R.string.up_step1))
                if (Sales.PRICE_TEXT.isNotBlank()) Text(stringResource(R.string.up_price, Sales.PRICE_TEXT), style = MaterialTheme.typography.titleMedium)
                if (Sales.PAY_URL.isNotBlank()) {
                    Button(onClick = { open(ctx, Intent(Intent.ACTION_VIEW, Uri.parse(Sales.PAY_URL))) },
                        modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp).testTag("up_pay"), shape = RoundedCornerShape(28.dp)) {
                        Text(stringResource(R.string.up_pay))
                    }
                }
                OutlinedButton(onClick = { open(ctx, requestEmail(ctx, settings, email)) },
                    modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp).testTag("up_request"), shape = RoundedCornerShape(28.dp)) {
                    Text(stringResource(R.string.up_request))
                }
                Text(stringResource(R.string.up_step1_help, CONTACT_NAME), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)

                SectionLabel(stringResource(R.string.up_step2))
                OutlinedTextField(email, { email = it.take(120) }, label = { Text(stringResource(R.string.reg_email)) }, singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email), modifier = Modifier.fillMaxWidth().testTag("up_email"))
                OutlinedTextField(code, { code = it.take(200); message = null }, label = { Text(stringResource(R.string.up_code)) },
                    minLines = 2, modifier = Modifier.fillMaxWidth().testTag("up_code"))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(onClick = {
                        val clip = (ctx.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager).primaryClip
                        clip?.takeIf { it.itemCount > 0 }?.getItemAt(0)?.coerceToText(ctx)?.toString()?.let { code = it.trim() }
                    }, modifier = Modifier.heightIn(min = 52.dp)) { Text(stringResource(R.string.up_paste)) }
                    Button(onClick = { if (!onUnlockCode(email, code)) { message = R.string.up_bad_code } },
                        modifier = Modifier.weight(1f).heightIn(min = 52.dp).testTag("up_unlock")) { Text(stringResource(R.string.up_unlock)) }
                }
            }
            message?.let { Text(stringResource(it), color = MaterialTheme.colorScheme.error, modifier = Modifier.testTag("up_message")) }
        }
    }
}

private fun requestEmail(ctx: Context, s: AppSettings, email: String): Intent {
    val body = listOf(
        "I would like the full version of Gaurav Jyotish.",
        "",
        "Name: ${s.userName.ifBlank { "-" }}",
        "Email for the unlock code: ${email.ifBlank { "-" }}",
        "Phone: ${s.userPhone.ifBlank { "-" }}",
        "Payment reference (if paid): ",
        "App version: ${BuildConfig.VERSION_NAME} (${BuildConfig.EDITION})",
    ).joinToString("\n")
    return Intent(Intent.ACTION_SENDTO, Uri.parse("mailto:")).putExtra(Intent.EXTRA_EMAIL, arrayOf(CONTACT_EMAIL))
        .putExtra(Intent.EXTRA_SUBJECT, ctx.getString(R.string.up_request_subject)).putExtra(Intent.EXTRA_TEXT, body)
}

private fun open(ctx: Context, i: Intent) {
    try { ctx.startActivity(i) } catch (e: ActivityNotFoundException) { /* no browser or mail app: the details stay on screen */ }
}
