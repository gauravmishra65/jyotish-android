package com.gauravmishra.jyotish.ui

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R
import com.gauravmishra.jyotish.data.Backup
import com.gauravmishra.jyotish.data.Profile
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * Backup and restore (v16): the saved people go into one password-protected file that the person saves wherever they
 * like through the system file picker, and come back from it on a new phone. The app itself never goes online.
 */
@Composable
fun BackupScreen(profiles: List<Profile>, onRestore: (List<Profile>) -> Pair<Int, Int>, onBack: () -> Unit) {
    val ctx = LocalContext.current
    val scope = rememberCoroutineScope()
    var pass by remember { mutableStateOf("") }
    var pass2 by remember { mutableStateOf("") }
    var restorePass by remember { mutableStateOf("") }
    var status by remember { mutableStateOf<String?>(null) }
    var picked by remember { mutableStateOf<Uri?>(null) }
    val okSaved = stringResource(R.string.bk_saved)
    val okRestored = stringResource(R.string.bk_restored)
    val wrong = stringResource(R.string.bk_wrong)
    val notOurs = stringResource(R.string.bk_not_backup)
    val failed = stringResource(R.string.bk_failed)
    val limited = stringResource(R.string.bk_limited)

    val create = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/octet-stream")) { uri ->
        if (uri == null) return@rememberLauncherForActivityResult
        val pw = pass.toCharArray()
        scope.launch {
            status = try {
                withContext(Dispatchers.IO) {
                    val bytes = Backup.encode(profiles, pw)
                    ctx.contentResolver.openOutputStream(uri)?.use { it.write(bytes) } ?: error("cannot write")
                }
                pass = ""; pass2 = ""
                okSaved.format(profiles.size)
            } catch (t: Throwable) { failed.format(t.message ?: "") } finally { pw.fill(' ') }
        }
    }
    val open = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri -> picked = uri; status = null }

    Scaffold(containerColor = MaterialTheme.colorScheme.background, topBar = { BackBar(stringResource(R.string.bk_title), onBack) }) { pad ->
        Column(Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text(stringResource(R.string.bk_intro), style = MaterialTheme.typography.bodyMedium)

            Text(stringResource(R.string.bk_make), style = MaterialTheme.typography.titleMedium)
            Text(stringResource(R.string.bk_count, profiles.size), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
            OutlinedTextField(pass, { pass = it }, label = { Text(stringResource(R.string.bk_password)) }, singleLine = true,
                visualTransformation = PasswordVisualTransformation(), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                modifier = Modifier.fillMaxWidth().testTag("bk_pass"))
            OutlinedTextField(pass2, { pass2 = it }, label = { Text(stringResource(R.string.bk_password_again)) }, singleLine = true,
                visualTransformation = PasswordVisualTransformation(), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                isError = pass2.isNotEmpty() && pass2 != pass, modifier = Modifier.fillMaxWidth().testTag("bk_pass2"))
            Text(stringResource(R.string.bk_password_note, Backup.MIN_PASSWORD), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
            Button(enabled = profiles.isNotEmpty() && pass.length >= Backup.MIN_PASSWORD && pass == pass2,
                onClick = { create.launch("GauravJyotish_backup_${java.time.LocalDate.now()}.gjb") },
                modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp).testTag("bk_save")) { Text(stringResource(R.string.bk_save)) }

            HorizontalDivider()
            Text(stringResource(R.string.bk_restore_title), style = MaterialTheme.typography.titleMedium)
            OutlinedButton(onClick = { open.launch(arrayOf("*/*")) }, modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp).testTag("bk_pick")) {
                Text(if (picked == null) stringResource(R.string.bk_pick) else stringResource(R.string.bk_picked))
            }
            OutlinedTextField(restorePass, { restorePass = it }, label = { Text(stringResource(R.string.bk_password)) }, singleLine = true,
                visualTransformation = PasswordVisualTransformation(), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                modifier = Modifier.fillMaxWidth().testTag("bk_restore_pass"))
            Button(enabled = picked != null && restorePass.isNotEmpty(),
                onClick = {
                    val uri = picked ?: return@Button
                    val pw = restorePass.toCharArray()
                    scope.launch {
                        status = try {
                            val people = withContext(Dispatchers.IO) {
                                val bytes = ctx.contentResolver.openInputStream(uri)?.use { it.readBytes() } ?: error("cannot read")
                                Backup.decode(bytes, pw)
                            }
                            val (done, left) = onRestore(people)
                            restorePass = ""; picked = null
                            okRestored.format(done) + if (left > 0) " " + limited.format(left) else ""
                        } catch (e: Backup.WrongPassword) { wrong } catch (e: Backup.NotABackup) { notOurs } catch (t: Throwable) { failed.format(t.message ?: "") }
                        finally { pw.fill(' ') }
                    }
                },
                modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp).testTag("bk_restore")) { Text(stringResource(R.string.bk_restore)) }
            status?.let { Text(it, style = MaterialTheme.typography.bodyLarge, color = Palette.AccentDeep, modifier = Modifier.testTag("bk_status")) }
            Text(stringResource(R.string.bk_privacy), style = MaterialTheme.typography.bodySmall, color = Palette.Muted)
        }
    }
}
