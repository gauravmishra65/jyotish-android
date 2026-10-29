package com.gauravmishra.jyotish.store

import android.app.Activity

/**
 * A shop the app can buy the full version from. Only the Play edition has one (Google Play Billing); the demo and
 * full editions use [NoStore]. Callbacks may arrive on any thread.
 */
interface Store {
    val available: Boolean
    /** The localised price shown by Play, or null when Play cannot be reached. */
    fun price(onPrice: (String?) -> Unit)
    /** Opens Play's purchase sheet. [onResult] gets UNLOCKED, PENDING, CANCELLED or FAILED. */
    fun buy(activity: Activity, onResult: (Purchase) -> Unit)
    /** Asks Play whether this account already owns the full version; null when Play cannot be reached. */
    fun owned(onOwned: (Boolean?) -> Unit)

    enum class Purchase { UNLOCKED, PENDING, CANCELLED, FAILED }
}

object NoStore : Store {
    override val available = false
    override fun price(onPrice: (String?) -> Unit) = onPrice(null)
    override fun buy(activity: Activity, onResult: (Store.Purchase) -> Unit) = onResult(Store.Purchase.FAILED)
    override fun owned(onOwned: (Boolean?) -> Unit) = onOwned(null)
}

/** Selling details. PAY_URL is the payment page for unlock codes (a Razorpay, UPI or PayPal link); empty means
 *  buyers ask by email. PRICE_TEXT is shown on the upgrade screen in the demo; Play shows its own price. */
object Sales {
    const val PAY_URL = ""
    const val PRICE_TEXT = ""
    const val FREE_PROFILES = 1
}
