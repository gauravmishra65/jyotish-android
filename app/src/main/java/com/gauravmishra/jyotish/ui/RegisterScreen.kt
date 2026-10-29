package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
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
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.AppSettings

private val EMAIL = Regex("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$")

/**
 * On-phone registration: the user's own name, email and phone, kept only in this phone's private settings (no
 * account, no internet). Shown once after the Welcome screen and editable later from Settings.
 */
@Composable
fun RegisterScreen(settings: AppSettings, editing: Boolean, onDone: () -> Unit, onSkip: () -> Unit) {
    var name by rememberSaveable { mutableStateOf(settings.userName) }
    var email by rememberSaveable { mutableStateOf(settings.userEmail) }
    var phone by rememberSaveable { mutableStateOf(settings.userPhone) }
    var tried by rememberSaveable { mutableStateOf(false) }
    val emailOk = email.isBlank() || EMAIL.matches(email.trim())
    val phoneOk = phone.isBlank() || phone.count { it.isDigit() } in 6..15
    val ok = name.isNotBlank() && emailOk && phoneOk

    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        topBar = { if (editing) BackBar(stringResource(R.string.reg_title), onSkip) },
    ) { pad ->
        Column(
            Modifier.fillMaxSize().padding(pad).imePadding().verticalScroll(rememberScrollState()).padding(horizontal = 24.dp, vertical = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            if (!editing) {
                Text(stringResource(R.string.reg_title), style = MaterialTheme.typography.headlineMedium)
            }
            Text(stringResource(R.string.reg_intro), style = MaterialTheme.typography.bodyLarge)
            OutlinedTextField(name, { name = it.take(80) }, label = { Text(stringResource(R.string.reg_name)) }, singleLine = true,
                isError = tried && name.isBlank(), modifier = Modifier.fillMaxWidth().testTag("reg_name"))
            OutlinedTextField(email, { email = it.take(120) }, label = { Text(stringResource(R.string.reg_email)) }, singleLine = true,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email), isError = !emailOk,
                supportingText = { if (!emailOk) Text(stringResource(R.string.reg_email_bad)) },
                modifier = Modifier.fillMaxWidth().testTag("reg_email"))
            OutlinedTextField(phone, { phone = it.take(20) }, label = { Text(stringResource(R.string.reg_phone)) }, singleLine = true,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone), isError = !phoneOk,
                supportingText = { if (!phoneOk) Text(stringResource(R.string.reg_phone_bad)) },
                modifier = Modifier.fillMaxWidth().testTag("reg_phone"))
            Text(stringResource(R.string.reg_privacy), style = MaterialTheme.typography.bodySmall, color = Palette.AccentDeep,
                modifier = Modifier.fillMaxWidth().background(Palette.AccentSoft, RoundedCornerShape(12.dp)).padding(12.dp))
            Button(
                onClick = {
                    tried = true
                    if (!ok) return@Button
                    settings.userName = name.trim(); settings.userEmail = email.trim(); settings.userPhone = phone.trim()
                    settings.registered = true
                    onDone()
                },
                modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp).testTag("reg_save"), shape = RoundedCornerShape(28.dp),
            ) { Text(stringResource(if (editing) R.string.reg_save_edit else R.string.reg_save)) }
            if (!editing) {
                TextButton(onClick = onSkip, modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp).testTag("reg_skip")) {
                    Text(stringResource(R.string.reg_skip))
                }
            } else if (settings.registered) {
                TextButton(onClick = {
                    settings.userName = ""; settings.userEmail = ""; settings.userPhone = ""; settings.registered = false; onSkip()
                }, modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp).testTag("reg_clear")) {
                    Text(stringResource(R.string.reg_clear), color = MaterialTheme.colorScheme.error)
                }
            }
        }
    }
}
