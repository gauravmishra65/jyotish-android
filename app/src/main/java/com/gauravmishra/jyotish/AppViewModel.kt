package com.gauravmishra.jyotish

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.gauravmishra.jyotish.data.AppSettings
import com.gauravmishra.jyotish.data.Places
import com.gauravmishra.jyotish.data.Profile
import com.gauravmishra.jyotish.data.ProfileStore
import com.gauravmishra.jyotish.engine.Engine
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.time.LocalDate

/** What the Home screen shows for a profile; filled once the engine has computed its chart. */
data class ChartSummary(
    val lagnaSign: String,
    val moonSign: String,
    val mahadasha: String,
    val mahadashaEnd: String,
    val antardasha: String,
    val antardashaEnd: String,
    val nextAntardasha: String?,
    val warnings: List<String>,
)

sealed interface ChartState {
    data object Calculating : ChartState
    data class Ready(val summary: ChartSummary, val json: String) : ChartState
    data class Failed(val message: String) : ChartState
}

class AppViewModel(app: Application) : AndroidViewModel(app) {
    val settings = AppSettings(app)
    private val store = ProfileStore(app.filesDir)

    private val _profiles = MutableStateFlow(store.load())
    val profiles: StateFlow<List<Profile>> = _profiles.asStateFlow()

    private val _charts = MutableStateFlow<Map<String, ChartState>>(emptyMap())
    val charts: StateFlow<Map<String, ChartState>> = _charts.asStateFlow()

    private val _language = MutableStateFlow(settings.language)
    val language: StateFlow<String?> = _language.asStateFlow()

    /** The place list loads in the background (about 70,000 rows) the first time it is needed. */
    private val placesJob = viewModelScope.async(Dispatchers.IO, start = kotlinx.coroutines.CoroutineStart.LAZY) {
        app.assets.open("places.tsv").bufferedReader(Charsets.UTF_8).useLines { Places(it) }
    }

    suspend fun places(): Places = placesJob.await()

    init {
        placesJob.start()   // parse the place list in the background now, so the search is ready when needed
        _profiles.value.forEach { compute(it) }
    }

    fun setLanguage(lang: String) {
        settings.language = lang
        _language.value = lang
    }

    fun addOrUpdate(p: Profile) {
        _profiles.update { list -> if (list.any { it.id == p.id }) list.map { if (it.id == p.id) p else it } else list + p }
        persist()
        compute(p)
    }

    fun delete(id: String) {
        _profiles.update { list -> list.filterNot { it.id == id } }
        _charts.update { it - id }
        persist()
        viewModelScope.launch(Dispatchers.IO) { store.deleteChart(id) }
    }

    /** Recompute every chart, e.g. after the ayanamsa or node setting changes. */
    fun recomputeAll() = _profiles.value.forEach { compute(it) }

    private fun persist() {
        val snapshot = _profiles.value
        viewModelScope.launch(Dispatchers.IO) { store.save(snapshot) }
    }

    private fun compute(p: Profile) {
        val request = p.chartRequest(LocalDate.now().toString(), settings.ayanamsa, settings.node)
        val key = request.toString()
        _charts.update { it + (p.id to ChartState.Calculating) }
        viewModelScope.launch {
            val state = try {
                val json = withContext(Dispatchers.IO) { store.cachedChart(p.id, key) } ?: Engine.chart(request).also {
                    withContext(Dispatchers.IO) { store.cacheChart(p.id, key, it) }
                }
                ChartState.Ready(withContext(Dispatchers.Default) { summarize(json) }, json)
            } catch (e: Throwable) {
                ChartState.Failed(e.message ?: e.toString())
            }
            _charts.update { if (_profiles.value.any { it.id == p.id }) it + (p.id to state) else it }
        }
    }

    companion object {
        fun summarize(json: String): ChartSummary {
            val c = JSONObject(json)
            val v = c.getJSONObject("vedic")
            val cur = v.getJSONObject("dashas").getJSONObject("vimshottari").getJSONObject("current")
            val maha = cur.getJSONObject("mahadasha")
            val antar = cur.getJSONObject("antardasha")
            val warnings = c.optJSONObject("audit")?.optJSONArray("warnings")
            return ChartSummary(
                lagnaSign = v.getJSONObject("lagna").getString("sign"),
                moonSign = v.getJSONObject("planets").getJSONObject("Moon").getString("sign"),
                mahadasha = maha.getString("lord"), mahadashaEnd = maha.getString("end"),
                antardasha = antar.getString("lord"), antardashaEnd = antar.getString("end"),
                nextAntardasha = nextAntardasha(v, antar.getString("end")),
                warnings = (0 until (warnings?.length() ?: 0)).map { warnings!!.getString(it) },
            )
        }

        /** The antardasha that starts when the current one ends, if the chart lists it. */
        private fun nextAntardasha(v: JSONObject, end: String): String? {
            val periods = v.getJSONObject("dashas").getJSONObject("vimshottari").optJSONArray("mahadashas") ?: return null
            for (i in 0 until periods.length()) {
                val antars = periods.getJSONObject(i).optJSONArray("antardashas") ?: continue
                for (j in 0 until antars.length()) {
                    val a = antars.getJSONObject(j)
                    if (a.optString("start") == end) return a.optString("lord")
                }
            }
            return null
        }
    }
}
