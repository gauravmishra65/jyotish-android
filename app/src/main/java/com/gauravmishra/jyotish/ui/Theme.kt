package com.gauravmishra.jyotish.ui

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

/** Colours from the v1 design; every text pair meets 4.5:1 contrast. */
object Palette {
    val Ground = Color(0xFFFBFAF7)
    val Surface = Color(0xFFFFFFFF)
    val Ink = Color(0xFF1C1B19)
    val Muted = Color(0xFF5E5A52)
    val Line = Color(0xFFE6E2DA)
    val Outline = Color(0xFFCFC9BE)
    val Accent = Color(0xFFB4530A)
    val AccentDeep = Color(0xFF8A3F07)
    val AccentSoft = Color(0xFFFCEFE3)
    val Night = Color(0xFF1C1B19)
    val NightText = Color(0xFFD9D5CC)
    val Saffron = Color(0xFFE9A25F)
    val SaffronText = Color(0xFFE9C9A8)
    val Good = Color(0xFF2F6B3A)
    val CautionBg = Color(0xFFFFF6E5)
    val CautionText = Color(0xFF4A3A16)
}

private val colors = lightColorScheme(
    primary = Palette.Ink,
    onPrimary = Palette.Ground,
    secondary = Palette.Accent,
    onSecondary = Palette.Surface,
    secondaryContainer = Palette.AccentSoft,
    onSecondaryContainer = Palette.AccentDeep,
    background = Palette.Ground,
    onBackground = Palette.Ink,
    surface = Palette.Surface,
    onSurface = Palette.Ink,
    surfaceVariant = Color(0xFFEFEBE4),
    onSurfaceVariant = Palette.Muted,
    outline = Palette.Outline,
    outlineVariant = Palette.Line,
    error = Color(0xFF9A3B1B),
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

@Composable
fun JyotishTheme(content: @Composable () -> Unit) = MaterialTheme(colorScheme = colors, typography = type, content = content)
