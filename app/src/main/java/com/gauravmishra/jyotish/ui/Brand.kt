package com.gauravmishra.jyotish.ui

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.gauravmishra.jyotish.R

/**
 * The app's mark, drawn from the launcher icon's two layers, for the Welcome and About screens. Decorative (the name
 * is shown next to it). The layers are 108 units with a 72-unit visible area, so the foreground is scaled 1.5x.
 */
@Composable
fun AppMark(modifier: Modifier = Modifier, size: Dp = 72.dp) {
    Box(modifier.size(size).clip(RoundedCornerShape(size * 0.24f))) {
        Image(painterResource(R.drawable.ic_launcher_background), contentDescription = null, modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop)
        Image(painterResource(R.drawable.ic_launcher_foreground), contentDescription = null, modifier = Modifier.fillMaxSize().scale(1.5f),
            contentScale = ContentScale.Fit)
    }
}
