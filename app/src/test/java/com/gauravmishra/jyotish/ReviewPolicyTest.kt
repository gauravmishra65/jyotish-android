package com.gauravmishra.jyotish

import com.gauravmishra.jyotish.ui.ReviewPolicy
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ReviewPolicyTest {
    private val day = 24L * 60 * 60 * 1000

    @Test fun notBeforeThreeFinishedTasks() {
        assertFalse(ReviewPolicy.shouldAsk(moments = 0, asks = 0, lastAskMs = 0, nowMs = 100 * day))
        assertFalse(ReviewPolicy.shouldAsk(2, 0, 0, 100 * day))
        assertTrue(ReviewPolicy.shouldAsk(3, 0, 0, 100 * day))
    }

    @Test fun thirtyDaysBetweenAsks() {
        assertFalse(ReviewPolicy.shouldAsk(10, 1, lastAskMs = 100 * day, nowMs = 129 * day))
        assertTrue(ReviewPolicy.shouldAsk(10, 1, lastAskMs = 100 * day, nowMs = 130 * day))
    }

    @Test fun atMostThreeAsksEver() {
        assertFalse(ReviewPolicy.shouldAsk(50, 3, lastAskMs = 0, nowMs = 1000 * day))
    }
}
