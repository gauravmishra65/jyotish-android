package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.Info
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R

object Routes {
    const val WELCOME = "welcome"
    const val HOME = "home"
    const val ADD = "add?id={id}&ret={ret}"
    /** ret: "" goes Home after saving; "back" returns to the screen that opened it; "groom"/"bride" also fill that Milan slot. */
    fun add(id: String? = null, ret: String = "") = "add?id=${id ?: ""}&ret=$ret"
    const val SETTINGS = "settings"
    const val KUNDALI = "kundali"
    const val MILAN = "milan"
    const val MUHURTA = "muhurta"
    const val NUMBERS = "numbers"
    const val FORECAST = "forecast"
    const val REPORT = "report"
    const val REGISTER = "register?edit={edit}"
    fun register(edit: Boolean = false) = "register?edit=$edit"
    const val SAVED = "saved"
    const val ABOUT = "about"
    const val UPGRADE = "upgrade"
    const val FEATURE = "feature/{name}"
    fun feature(name: String) = "feature/$name"

    /** Kundali has its own screen from M2; the other features are still placeholders. */
    fun of(f: Feature) = when (f) {
        Feature.KUNDALI -> KUNDALI
        Feature.MILAN -> MILAN
        Feature.MUHURTA -> MUHURTA
        Feature.NUMBERS -> NUMBERS
    }
}

enum class Feature(val route: String, val label: Int, val title: Int, val icon: ImageVector) {
    KUNDALI("kundali", R.string.nav_kundali, R.string.feature_kundali, Icons.Filled.Star),
    MILAN("milan", R.string.nav_milan, R.string.feature_milan, Icons.Filled.Favorite),
    MUHURTA("muhurta", R.string.nav_muhurta, R.string.feature_muhurta, Icons.Filled.DateRange),
    NUMBERS("numbers", R.string.nav_numbers, R.string.feature_numerology, Icons.Filled.Info),
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BackBar(title: String, onBack: () -> Unit, subtitle: String? = null) {
    TopAppBar(
        title = {
            Column {
                Text(title, style = MaterialTheme.typography.titleLarge)
                if (subtitle != null) Text(subtitle, style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        },
        navigationIcon = {
            IconButton(onClick = onBack, modifier = Modifier.size(48.dp)) { Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = stringResource(R.string.back)) }
        },
        colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.background),
    )
}

/** Bottom navigation shown on Home and the feature screens. [current] is null on Home. */
@Composable
fun BottomNav(current: Feature?, onHome: () -> Unit, onFeature: (Feature) -> Unit, homeSelected: Boolean = current == null) {
    NavigationBar(containerColor = MaterialTheme.colorScheme.surface) {
        val itemColors = NavigationBarItemDefaults.colors(
            selectedIconColor = Palette.AccentDeep, selectedTextColor = Palette.AccentDeep, indicatorColor = Palette.AccentSoft,
            unselectedIconColor = Palette.Muted, unselectedTextColor = Palette.Muted,
        )
        NavigationBarItem(
            selected = homeSelected, onClick = onHome, colors = itemColors,
            icon = { Icon(Icons.Filled.Home, contentDescription = null, modifier = Modifier.size(22.dp)) },
            label = { Text(stringResource(R.string.nav_home)) },
        )
        Feature.entries.forEach { f ->
            NavigationBarItem(
                selected = current == f, onClick = { onFeature(f) }, colors = itemColors, modifier = Modifier.testTag("nav_${f.route}"),
                icon = { Icon(f.icon, contentDescription = null, modifier = Modifier.size(22.dp)) },
                label = { Text(stringResource(f.label), maxLines = 1) },
            )
        }
    }
}

@Composable
fun SectionLabel(text: String) {
    Row(Modifier.padding(top = 8.dp, bottom = 6.dp), verticalAlignment = Alignment.CenterVertically) {
        Text(text.uppercase(), style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

/** Plain-words meaning paragraphs from assets/meanings.json, with the "traditionally" caveat built into the wording. */
@Composable
fun Meaning(lines: List<String>, tag: String) {
    if (lines.isEmpty()) return
    Column(Modifier.testTag(tag), verticalArrangement = Arrangement.spacedBy(6.dp)) {
        lines.forEach { Text(it, style = MaterialTheme.typography.bodyLarge) }
    }
}
