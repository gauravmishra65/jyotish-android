package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.TextMeasurer
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.unit.sp
import com.gauravmishra.jyotish.data.Abbrev
import com.gauravmishra.jyotish.data.ChartModel
import com.gauravmishra.jyotish.data.SIGNS

/**
 * Positions in the North Indian diamond, in units of the chart's side (0 to 1), from the v1 design.
 * House 1 is the top centre kite; houses run anticlockwise.
 */
object NorthLayout {
    /** Where the planets of each house are written (index 0 = house 1). */
    val planetAt = listOf(
        0.50 to 0.27, 0.25 to 0.11, 0.11 to 0.25, 0.27 to 0.50, 0.11 to 0.75, 0.25 to 0.89,
        0.50 to 0.73, 0.75 to 0.89, 0.89 to 0.75, 0.73 to 0.50, 0.89 to 0.25, 0.75 to 0.11,
    )

    /** Where each house's sign number goes: near the inner corner, as in printed kundlis. */
    val signAt = listOf(
        0.50 to 0.44, 0.25 to 0.19, 0.19 to 0.25, 0.44 to 0.51, 0.19 to 0.76, 0.25 to 0.83,
        0.50 to 0.57, 0.75 to 0.83, 0.81 to 0.76, 0.56 to 0.51, 0.81 to 0.25, 0.75 to 0.19,
    )
}

/** South Indian grid: signs are fixed (Pisces top left, then clockwise); the lagna is marked. Row, column per sign. */
object SouthLayout {
    val cellOfSign = listOf(0 to 1, 0 to 2, 0 to 3, 1 to 3, 2 to 3, 3 to 3, 3 to 2, 3 to 1, 3 to 0, 2 to 0, 1 to 0, 0 to 0)
}

/** Text a screen reader reads for the chart: every house with its sign and planets. */
fun chartDescription(m: ChartModel, lang: String, houseWord: String, emptyWord: String): String =
    (1..12).joinToString(". ") { h ->
        val sign = Names.of(SIGNS[m.signOfHouse(h)], lang)
        val ps = m.planetsInHouse(h).joinToString(", ") { Names.of(it.name, lang) }.ifEmpty { emptyWord }
        "$houseWord $h, $sign: $ps"
    }

@Composable
fun KundliChart(m: ChartModel, style: String, lang: String, description: String, modifier: Modifier = Modifier) {
    val measurer = rememberTextMeasurer()
    val ink = Palette.Ink
    Canvas(modifier.fillMaxWidth().aspectRatio(1f).semantics { contentDescription = description }) {
        if (style == "south") drawSouth(m, lang, measurer) else drawNorth(m, lang, measurer)
        drawRect(ink, style = Stroke(width = px(1.5)), size = Size(size.width, size.height))
    }
}

private fun DrawScope.px(v: Double) = (v * density).toFloat()

/** Text size that scales with the chart, not with the phone's font setting (the chart has a fixed layout). */
private fun DrawScope.chartSp(designPx: Float) = (size.width / 300f * designPx / (density * fontScale)).sp

private fun DrawScope.drawNorth(m: ChartModel, lang: String, tm: TextMeasurer) {
    val s = size.width
    fun p(x: Double, y: Double) = Offset((x * s).toFloat(), (y * s).toFloat())
    // House 1 kite tinted, as in the design.
    drawPath(Path().apply { moveTo(s / 2, 0f); lineTo(s * 0.75f, s * 0.25f); lineTo(s / 2, s / 2); lineTo(s * 0.25f, s * 0.25f); close() }, Palette.AccentSoft)
    val line = Stroke(width = px(1.2))
    drawLine(Palette.Ink, p(0.0, 0.0), p(1.0, 1.0), strokeWidth = line.width)
    drawLine(Palette.Ink, p(1.0, 0.0), p(0.0, 1.0), strokeWidth = line.width)
    drawPath(Path().apply { moveTo(s / 2, 0f); lineTo(s, s / 2); lineTo(s / 2, s); lineTo(0f, s / 2); close() }, Palette.Ink, style = line)
    val small = TextStyle(fontSize = chartSp(11f), color = Palette.Muted)
    val big = TextStyle(fontSize = chartSp(13f), color = Palette.Ink, fontWeight = FontWeight.SemiBold)
    for (h in 1..12) {
        val (sx, sy) = NorthLayout.signAt[h - 1]
        centred(tm, "${m.signOfHouse(h) + 1}", small, p(sx, sy))
        val (px0, py0) = NorthLayout.planetAt[h - 1]
        val lines = m.planetsInHouse(h).map { Abbrev.of(it, lang) }.chunked(2).map { it.joinToString(" ") }
        val top = if (h == 1) 1 else 0   // house 1 also carries the lagna label above its planets
        if (h == 1) centred(tm, if (lang == "hi") "लग्न" else "Asc", big.copy(color = Palette.AccentDeep), p(px0, py0 - (lines.size) * 0.0275))
        lines.forEachIndexed { i, text ->
            val dy = (i + top - (lines.size + top - 1) / 2.0) * 0.055
            centred(tm, text, big, p(px0, py0 + dy))
        }
    }
}

private fun DrawScope.drawSouth(m: ChartModel, lang: String, tm: TextMeasurer) {
    val s = size.width
    val c = s / 4f
    val line = px(1.2)
    for (i in 1..3) {
        drawLine(Palette.Ink, Offset(0f, c * i), Offset(s, c * i), strokeWidth = line)
        drawLine(Palette.Ink, Offset(c * i, 0f), Offset(c * i, s), strokeWidth = line)
    }
    // The centre is one empty box: paint over the inner lines.
    drawRect(Palette.Surface, topLeft = Offset(c + line, c + line), size = Size(2 * c - 2 * line, 2 * c - 2 * line))
    val small = TextStyle(fontSize = chartSp(10f), color = Palette.Muted)
    val big = TextStyle(fontSize = chartSp(13f), color = Palette.Ink, fontWeight = FontWeight.SemiBold)
    for (sign in 0 until 12) {
        val (r, col) = SouthLayout.cellOfSign[sign]
        val x0 = col * c; val y0 = r * c
        if (sign == m.lagna.signIndex) {
            drawRect(Palette.AccentSoft, topLeft = Offset(x0 + line, y0 + line), size = Size(c - 2 * line, c - 2 * line))
            drawLine(Palette.Accent, Offset(x0, y0 + c * 0.28f), Offset(x0 + c * 0.28f, y0), strokeWidth = px(1.5))
        }
        val name = Names.of(SIGNS[sign], lang)
        drawText(tm, name, Offset(x0 + c * 0.06f, y0 + c * 0.04f + (if (sign == m.lagna.signIndex) c * 0.08f else 0f)), small)
        val labels = buildList {
            if (sign == m.lagna.signIndex) add(if (lang == "hi") "लग्न" else "Asc")
            m.planets.filter { it.signIndex == sign }.forEach { add(Abbrev.of(it, lang)) }
        }
        labels.chunked(2).forEachIndexed { i, pair ->
            centred(tm, pair.joinToString(" "), big, Offset(x0 + c / 2, y0 + c * (0.52f + 0.2f * i)))
        }
    }
}

private fun DrawScope.centred(tm: TextMeasurer, text: String, style: TextStyle, at: Offset) {
    val r = tm.measure(text, style)
    drawText(r, topLeft = Offset(at.x - r.size.width / 2f, at.y - r.size.height / 2f))
}
