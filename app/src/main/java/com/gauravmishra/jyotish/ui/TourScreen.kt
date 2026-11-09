package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R
import kotlinx.coroutines.launch

private class Step(val icon: ImageVector, val title: Int, val body: Int)

private val steps = listOf(
    Step(Icons.Filled.Person, R.string.tour1_title, R.string.tour1_body),
    Step(Icons.Filled.DateRange, R.string.tour2_title, R.string.tour2_body),
    Step(Icons.Filled.Favorite, R.string.tour3_title, R.string.tour3_body),
    Step(Icons.Filled.Lock, R.string.tour4_title, R.string.tour4_body),
)

/** A short first-launch walkthrough: four swipeable cards, with Skip on every card. It can be replayed from Help. */
@Composable
fun TourScreen(onDone: () -> Unit) {
    val pager = rememberPagerState { steps.size }
    val scope = rememberCoroutineScope()
    val last = pager.currentPage == steps.lastIndex
    Column(Modifier.fillMaxSize().background(Palette.Night).safeDrawingPadding().padding(horizontal = 24.dp, vertical = 16.dp).testTag("tour")) {
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            AppMark(size = 40.dp)
            Text(stringResource(R.string.app_name), style = MaterialTheme.typography.titleMedium, color = Palette.Saffron,
                modifier = Modifier.weight(1f).padding(start = 12.dp))
            TextButton(onClick = onDone, modifier = Modifier.heightIn(min = 48.dp).testTag("tour_skip")) {
                Text(stringResource(R.string.tour_skip), color = Palette.NightText)
            }
        }
        HorizontalPager(pager, Modifier.weight(1f).fillMaxWidth()) { i ->
            val s = steps[i]
            Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(vertical = 24.dp).testTag("tour_page_$i"),
                verticalArrangement = Arrangement.spacedBy(20.dp, Alignment.CenterVertically)) {
                Box(Modifier.size(88.dp).background(Palette.Saffron, CircleShape), contentAlignment = Alignment.Center) {
                    Icon(s.icon, contentDescription = null, tint = Palette.InkFixed, modifier = Modifier.size(44.dp))
                }
                Text(stringResource(s.title), style = MaterialTheme.typography.headlineMedium, color = Palette.NightTitle)
                Text(stringResource(s.body), style = MaterialTheme.typography.bodyLarge, color = Palette.NightText)
            }
        }
        val pos = stringResource(R.string.tour_position, pager.currentPage + 1, steps.size)
        Row(Modifier.fillMaxWidth().padding(vertical = 12.dp).semantics { contentDescription = pos },
            horizontalArrangement = Arrangement.spacedBy(8.dp, Alignment.CenterHorizontally)) {
            steps.indices.forEach { i ->
                Box(Modifier.size(if (i == pager.currentPage) 12.dp else 8.dp)
                    .background(if (i == pager.currentPage) Palette.Saffron else Palette.Muted, CircleShape))
            }
        }
        Button(
            onClick = { if (last) onDone() else scope.launch { pager.animateScrollToPage(pager.currentPage + 1) } },
            modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp).testTag(if (last) "tour_start" else "tour_next"),
            shape = RoundedCornerShape(28.dp),
            colors = ButtonDefaults.buttonColors(containerColor = Palette.Saffron, contentColor = Palette.InkFixed),
        ) { Text(stringResource(if (last) R.string.tour_start else R.string.tour_next), style = MaterialTheme.typography.labelLarge) }
    }
}
