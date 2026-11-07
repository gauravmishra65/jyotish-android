package com.gauravmishra.jyotish.store

import android.app.Activity
import com.google.android.play.core.review.ReviewManagerFactory

/** Google Play's in-app rating card. Play decides whether it actually shows; nothing is reported back either way. */
fun askForReview(activity: Activity) {
    runCatching {
        val manager = ReviewManagerFactory.create(activity)
        manager.requestReviewFlow().addOnCompleteListener { task ->
            if (task.isSuccessful && !activity.isFinishing) manager.launchReviewFlow(activity, task.result)
        }
    }
}
