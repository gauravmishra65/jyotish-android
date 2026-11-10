package com.gauravmishra.jyotish.ui

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.lightColorScheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

/**
 * Colours from the v1 design; every text pair meets 4.5:1 contrast in both themes. [dark] is set by [JyotishTheme] (from
 * the Settings choice or the phone's theme) and is snapshot state, so every screen redraws when it changes.
 */
object Palette {
    var dark by mutableStateOf(false)
    private fun c(light: Long, night: Long) = Color(if (dark) night else light)
    val Ground: Color get() = c(0xFFFBFAF7, 0xFF141210)
    val Surface: Color get() = c(0xFFFFFFFF, 0xFF1F1C19)
    val Ink: Color get() = c(0xFF1C1B19, 0xFFF2EDE4)
    val Muted: Color get() = c(0xFF5E5A52, 0xFFB3AA9A)
    val Line: Color get() = c(0xFFE6E2DA, 0xFF3A352E)
    val Outline: Color get() = c(0xFFCFC9BE, 0xFF5A534A)
    val Accent: Color get() = c(0xFFB4530A, 0xFFF0A45A)
    val AccentDeep: Color get() = c(0xFF8A3F07, 0xFFF6C48F)
    val AccentSoft: Color get() = c(0xFFFCEFE3, 0xFF3A2A1C)
    val Night: Color get() = c(0xFF1C1B19, 0xFF2A2622)
    val NightText: Color get() = Color(0xFFD9D5CC)
    val Saffron: Color get() = Color(0xFFE9A25F)
    val SaffronText: Color get() = Color(0xFFE9C9A8)
    val Good: Color get() = c(0xFF2F6B3A, 0xFF8FD19E)
    val Bad: Color get() = c(0xFF9A3B1B, 0xFFF2A68F)
    val CautionBg: Color get() = c(0xFFFFF6E5, 0xFF3A3020)
    val CautionText: Color get() = c(0xFF4A3A16, 0xFFF2E2B8)
    val CautionBorder: Color get() = c(0xFFE8C98E, 0xFF7A6436)
    val Track: Color get() = c(0xFFEFEBE4, 0xFF2E2A26)
    val ChipGood: Color get() = c(0xFFE6F2E8, 0xFF1E3524)
    val ChipGoodText: Color get() = c(0xFF24502C, 0xFFA9DDB4)
    val ChipText: Color get() = c(0xFF3F3B35, 0xFFD9D2C5)
    /** Always light: titles on the dark (Night) cards. */
    val NightTitle: Color get() = Color(0xFFFBFAF7)
    /** Always dark: text on saffron buttons and on the light chips of the Welcome screen. */
    val InkFixed: Color get() = Color(0xFF1C1B19)
}

private fun scheme(dark: Boolean) = if (dark) darkColorScheme(
    primary = Palette.Ink, onPrimary = Palette.Ground, secondary = Palette.Accent, onSecondary = Palette.Ground,
    secondaryContainer = Palette.AccentSoft, onSecondaryContainer = Palette.AccentDeep,
    background = Palette.Ground, onBackground = Palette.Ink, surface = Palette.Surface, onSurface = Palette.Ink,
    surfaceVariant = Palette.Track, onSurfaceVariant = Palette.Muted, outline = Palette.Outline, outlineVariant = Palette.Line,
    error = Palette.Bad,
) else lightColorScheme(
    primary = Palette.Ink, onPrimary = Palette.Ground, secondary = Palette.Accent, onSecondary = Palette.Surface,
    secondaryContainer = Palette.AccentSoft, onSecondaryContainer = Palette.AccentDeep,
    background = Palette.Ground, onBackground = Palette.Ink, surface = Palette.Surface, onSurface = Palette.Ink,
    surfaceVariant = Palette.Track, onSurfaceVariant = Palette.Muted, outline = Palette.Outline, outlineVariant = Palette.Line,
    error = Palette.Bad,
)

private val heading = FontFamily.Serif

private val type = Typography(
    headlineLarge = TextStyle(fontFamily = heading, fontWeight = FontWeight.SemiBold, fontSize = 32.sp, lineHeight = 40.sp),
    headlineMedium = TextStyle(fontFamily = heading, fontWeight = FontWeight.SemiBold, fontSize = 26.sp, lineHeight = 34.sp),
    headlineSmall = TextStyle(fontFamily = heading, fontWeight = FontWeight.SemiBold, fontSize = 20.sp, lineHeight = 28.sp),
    titleLarge = TextStyle(fontWeight = FontWeight.SemiBold, fontSize = 19.sp, lineHeight = 26.sp),
    titleMedium = TextStyle(fontWeight = FontWeight.SemiBold, fontSize = 16.sp, lineHeight = 22.sp),
    bodyLarge = TextStyle(fontSize = 16.sp, lineHeight = 24.sp),
    bodyMedium = TextStyle(fontSize = 14.sp, lineHeight = 21.sp),
    bodySmall = TextStyle(fontSize = 13.sp, lineHeight = 19.sp),
    labelLarge = TextStyle(fontWeight = FontWeight.SemiBold, fontSize = 15.sp),
    labelMedium = TextStyle(fontSize = 12.sp, lineHeight = 16.sp),
)

/** [mode] is "system", "light" or "dark" (Settings). */
@Composable
fun JyotishTheme(mode: String = "system", content: @Composable () -> Unit) {
    val dark = when (mode) { "dark" -> true; "light" -> false; else -> isSystemInDarkTheme() }
    // set after the frame is applied, not while composing (a write to state during composition is not supported)
    androidx.compose.runtime.SideEffect { if (Palette.dark != dark) Palette.dark = dark }
    MaterialTheme(colorScheme = scheme(dark), typography = type, content = content)
}
