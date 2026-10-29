package com.gauravmishra.jyotish.store

import android.app.Activity
import android.content.Context
import android.os.Handler
import android.os.Looper
import com.android.billingclient.api.AcknowledgePurchaseParams
import com.android.billingclient.api.BillingClient
import com.android.billingclient.api.BillingClientStateListener
import com.android.billingclient.api.BillingFlowParams
import com.android.billingclient.api.BillingResult
import com.android.billingclient.api.PendingPurchasesParams
import com.android.billingclient.api.ProductDetails
import com.android.billingclient.api.Purchase
import com.android.billingclient.api.PurchasesUpdatedListener
import com.android.billingclient.api.QueryProductDetailsParams
import com.android.billingclient.api.QueryPurchasesParams

fun createStore(context: Context): Store = PlayStore(context.applicationContext)

/**
 * Google Play Billing for the one-time product "full_unlock" (create it in Play Console as an in-app product).
 * Purchases are acknowledged on the phone; there is no server, so a purchase is trusted as Play reports it.
 */
class PlayStore(context: Context) : Store, PurchasesUpdatedListener {
    companion object { const val PRODUCT = "full_unlock" }

    private val main = Handler(Looper.getMainLooper())
    private val client = BillingClient.newBuilder(context).setListener(this)
        .enablePendingPurchases(PendingPurchasesParams.newBuilder().enableOneTimeProducts().build())
        .enableAutoServiceReconnection().build()
    private var details: ProductDetails? = null
    private var pending: ((Store.Purchase) -> Unit)? = null

    override val available = true

    private fun connect(then: (Boolean) -> Unit) {
        if (client.isReady) return then(true)
        client.startConnection(object : BillingClientStateListener {
            override fun onBillingSetupFinished(r: BillingResult) { then(r.responseCode == BillingClient.BillingResponseCode.OK) }
            override fun onBillingServiceDisconnected() {}
        })
    }

    private fun loadDetails(then: (ProductDetails?) -> Unit) = connect { ok ->
        if (!ok) return@connect then(null)
        details?.let { return@connect then(it) }
        val q = QueryProductDetailsParams.newBuilder().setProductList(listOf(
            QueryProductDetailsParams.Product.newBuilder().setProductId(PRODUCT).setProductType(BillingClient.ProductType.INAPP).build(),
        )).build()
        // Billing 8: the result carries the found products (and any that could not be fetched).
        client.queryProductDetailsAsync(q) { _, result -> details = result.productDetailsList.firstOrNull(); then(details) }
    }

    override fun price(onPrice: (String?) -> Unit) = loadDetails { d -> main.post { onPrice(d?.oneTimePurchaseOfferDetails?.formattedPrice) } }

    override fun buy(activity: Activity, onResult: (Store.Purchase) -> Unit) = loadDetails { d ->
        main.post {
            if (d == null) return@post onResult(Store.Purchase.FAILED)
            pending = onResult
            val params = BillingFlowParams.newBuilder().setProductDetailsParamsList(listOf(
                BillingFlowParams.ProductDetailsParams.newBuilder().setProductDetails(d).build(),
            )).build()
            val r = client.launchBillingFlow(activity, params)
            if (r.responseCode != BillingClient.BillingResponseCode.OK) { pending = null; onResult(Store.Purchase.FAILED) }
        }
    }

    override fun onPurchasesUpdated(r: BillingResult, purchases: MutableList<Purchase>?) {
        val cb = pending ?: return
        val mine = purchases.orEmpty().filter { PRODUCT in it.products }
        val result = when {
            r.responseCode == BillingClient.BillingResponseCode.USER_CANCELED -> Store.Purchase.CANCELLED
            r.responseCode == BillingClient.BillingResponseCode.ITEM_ALREADY_OWNED -> Store.Purchase.UNLOCKED
            r.responseCode != BillingClient.BillingResponseCode.OK -> Store.Purchase.FAILED
            mine.any { it.purchaseState == Purchase.PurchaseState.PURCHASED } -> Store.Purchase.UNLOCKED
            mine.any { it.purchaseState == Purchase.PurchaseState.PENDING } -> Store.Purchase.PENDING
            else -> Store.Purchase.FAILED
        }
        mine.forEach(::acknowledge)
        pending = null
        main.post { cb(result) }
    }

    override fun owned(onOwned: (Boolean?) -> Unit) = connect { ok ->
        if (!ok) { main.post { onOwned(null) }; return@connect }
        client.queryPurchasesAsync(QueryPurchasesParams.newBuilder().setProductType(BillingClient.ProductType.INAPP).build()) { r, list ->
            val mine = list.filter { PRODUCT in it.products && it.purchaseState == Purchase.PurchaseState.PURCHASED }
            mine.forEach(::acknowledge)
            main.post { onOwned(if (r.responseCode == BillingClient.BillingResponseCode.OK) mine.isNotEmpty() else null) }
        }
    }

    /** Play refunds a purchase that is not acknowledged within three days. */
    private fun acknowledge(p: Purchase) {
        if (p.purchaseState != Purchase.PurchaseState.PURCHASED || p.isAcknowledged) return
        client.acknowledgePurchase(AcknowledgePurchaseParams.newBuilder().setPurchaseToken(p.purchaseToken).build()) {}
    }
}
