package com.gauravmishra.jyotish

import android.content.res.Configuration
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.gauravmishra.jyotish.engine.Engine
import com.gauravmishra.jyotish.ui.AddProfileScreen
import com.gauravmishra.jyotish.ui.Feature
import com.gauravmishra.jyotish.ui.FeatureScreen
import com.gauravmishra.jyotish.ui.HomeScreen
import com.gauravmishra.jyotish.ui.JyotishTheme
import com.gauravmishra.jyotish.ui.Routes
import com.gauravmishra.jyotish.ui.SettingsScreen
import com.gauravmishra.jyotish.ui.WelcomeScreen
import java.util.Locale

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent { App() }
    }
}

/** Applies the chosen language to everything below it without restarting the activity. */
@Composable
private fun Localized(lang: String, content: @Composable () -> Unit) {
    val base = LocalContext.current
    val config = remember(lang) { Configuration(base.resources.configuration).apply { setLocale(Locale.forLanguageTag(lang)) } }
    val ctx = remember(lang) { base.createConfigurationContext(config) }
    CompositionLocalProvider(LocalContext provides ctx, LocalConfiguration provides config) { content() }
}

@Composable
fun App(vm: AppViewModel = viewModel()) {
    val chosen by vm.language.collectAsStateWithLifecycle()
    var welcomeLang by remember { mutableStateOf(chosen ?: if (Locale.getDefault().language == "hi") "hi" else "en") }
    val lang = chosen ?: welcomeLang
    Localized(lang) {
        JyotishTheme {
            val nav = rememberNavController()
            val profiles by vm.profiles.collectAsStateWithLifecycle()
            val charts by vm.charts.collectAsStateWithLifecycle()
            NavHost(nav, startDestination = if (chosen == null) Routes.WELCOME else Routes.HOME) {
                composable(Routes.WELCOME) {
                    WelcomeScreen(lang = welcomeLang, onLanguage = { welcomeLang = it }, onContinue = {
                        vm.setLanguage(welcomeLang)
                        nav.navigate(Routes.add()) { popUpTo(Routes.WELCOME) { inclusive = true } }
                    })
                }
                composable(Routes.HOME) {
                    HomeScreen(
                        profiles = profiles, charts = charts,
                        onAdd = { nav.navigate(Routes.add()) },
                        onEdit = { nav.navigate(Routes.add(it.id)) },
                        onDelete = { vm.delete(it.id) },
                        onSettings = { nav.navigate(Routes.SETTINGS) },
                        onFeature = { nav.navigate(Routes.feature(it.route)) },
                    )
                }
                composable(Routes.ADD, arguments = listOf(navArgument("id") { type = NavType.StringType; nullable = true })) { entry ->
                    val id = entry.arguments?.getString("id")
                    AddProfileScreen(
                        existing = profiles.firstOrNull { it.id == id },
                        loadPlaces = { vm.places() },
                        onBack = { nav.goHome() },
                        onSave = { vm.addOrUpdate(it); nav.goHome() },
                    )
                }
                composable(Routes.SETTINGS) {
                    var version by remember { mutableStateOf<String?>(null) }
                    LaunchedEffect(Unit) { version = runCatching { Engine.engineVersion() }.getOrNull() }
                    SettingsScreen(vm.settings, lang, version, onLanguage = { vm.setLanguage(it) }, onCalculationChanged = { vm.recomputeAll() },
                        onSpeedTest = { org.json.JSONObject(Engine.timings()).toString(1) }, onBack = { nav.popBackStack() })
                }
                composable(Routes.FEATURE) { entry ->
                    val f = Feature.entries.first { it.route == entry.arguments?.getString("name") }
                    val p = profiles.firstOrNull()
                    FeatureScreen(f, p, p?.let { charts[it.id] }, onHome = { nav.goHome() }, onFeature = { nav.navigate(Routes.feature(it.route)) { popUpTo(Routes.HOME) } })
                }
            }
        }
    }
}

private fun NavHostController.goHome() = navigate(Routes.HOME) { popUpTo(graph.id) { inclusive = true } }
