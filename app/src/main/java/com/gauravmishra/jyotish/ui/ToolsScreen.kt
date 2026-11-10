package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R

/** One entry on the Tools screen: its title and line of explanation, the route it opens and its test tag. */
data class Tool(val key: String, val title: Int, val sub: Int, val route: String)

/** The Tools screen's entries, in order. */
val TOOLS = listOf(
    Tool("birth_time", R.string.bt_title, R.string.bt_sub, Routes.BIRTH_TIME),
    Tool("prashna", R.string.pr_title, R.string.pr_sub, Routes.PRASHNA),
    Tool("kp", R.string.kp_title, R.string.kp_sub, Routes.KP_HORARY),
    Tool("numbers", R.string.nt_title, R.string.nt_sub, Routes.NUMBER_TOOLS),
    Tool("backup", R.string.bk_title, R.string.bk_sub, Routes.BACKUP),
)

/** Tools beyond the main features: Birth time check, Prashna, KP horary, backup and restore. */
@Composable
fun ToolsScreen(tools: List<Tool>, onOpen: (String) -> Unit, onBack: () -> Unit) {
    Scaffold(containerColor = MaterialTheme.colorScheme.background, topBar = { BackBar(stringResource(R.string.tools_title), onBack) }) { pad ->
        Column(Modifier.fillMaxSize().padding(pad).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)) {
            tools.forEach { t ->
                Card(onClick = { onOpen(t.route) }, shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                    border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
                    modifier = Modifier.fillMaxWidth().heightIn(min = 76.dp).testTag("tool_${t.key}")) {
                    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text(stringResource(t.title), style = MaterialTheme.typography.titleMedium)
                        Text(stringResource(t.sub), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
            }
        }
    }
}
