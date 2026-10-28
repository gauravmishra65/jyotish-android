package com.gauravmishra.jyotish

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.gauravmishra.jyotish.data.AppSettings
import com.gauravmishra.jyotish.data.ChartModel
import com.gauravmishra.jyotish.data.ForecastModel
import com.gauravmishra.jyotish.data.MatchModel
import com.gauravmishra.jyotish.data.MuhurtaResult
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

sealed interface MuhurtaState {
    data object Idle : MuhurtaState
    data object Searching : MuhurtaState
    data class Ready(val result: MuhurtaResult) : MuhurtaState
    data class Failed(val message: String) : MuhurtaState
}

/** What the Muhurta form asks for. Dates are YYYY-MM-DD. */
data class MuhurtaQuery(
    val event: String, val from: String, val to: String,
    val place: String, val lat: Double, val lon: Double, val tz: String,
    val people: List<String>,
)

sealed interface MatchState {
    data object Waiting : MatchState          // one of the two charts is still being calculated
    data object Calculating : MatchState
    data class Ready(val model: MatchModel) : MatchState
    data class Failed(val message: String) : MatchState
}

sealed interface ForecastState {
    data object Calculating : ForecastState
    data class Ready(val model: ForecastModel) : ForecastState
    data class Failed(val message: String) : ForecastState
}

sealed interface ChartState {
    data object Calculating : ChartState
    data class Ready(val summary: ChartSummary, val model: ChartModel, val json: String) : ChartState
    data class Failed(val message: String) : ChartState
}

class AppViewModel(app: Application) : AndroidViewModel(app) {
    val settings = AppSettings(app)
    private val store = ProfileStore(app.filesDir)

    private val _profiles = MutableStateFlow(store.load())
    val profiles: StateFlow<List<Profile>> = _profiles.asStateFlow()

    private val _charts = MutableStateFlow<Map<String, ChartState>>(emptyMap())
    val charts: StateFlow<Map<String, ChartState>> = _charts.asStateFlow()

    private val _selected = MutableStateFlow(_profiles.value.firstOrNull()?.id)
    /** The profile the Kundali and other feature screens show. */
    val selected: StateFlow<String?> = _selected.asStateFlow()
    fun select(id: String) { _selected.value = id }

    private val _chartStyle = MutableStateFlow(settings.chartStyle)
    val chartStyle: StateFlow<String> = _chartStyle.asStateFlow()
    fun setChartStyle(style: String) { settings.chartStyle = style; _chartStyle.value = style }

    private val _pair = MutableStateFlow<Pair<String?, String?>>(null to null)
    /** Groom and bride for Kundali Milan; by default the first man and the first woman among the profiles. */
    val pair: StateFlow<Pair<String?, String?>> = _pair.asStateFlow()
    fun setPair(groom: String?, bride: String?) { _pair.value = groom to bride }

    fun defaultPair(list: List<Profile>): Pair<String?, String?> {
        val (g, b) = _pair.value
        val groom = g?.takeIf { id -> list.any { it.id == id } } ?: list.firstOrNull { it.gender == "M" }?.id ?: list.getOrNull(0)?.id
        val bride = b?.takeIf { id -> list.any { it.id == id } && id != groom }
            ?: list.firstOrNull { it.gender == "F" && it.id != groom }?.id ?: list.firstOrNull { it.id != groom }?.id
        return groom to bride
    }

    private val _match = MutableStateFlow<MatchState>(MatchState.Waiting)
    val match: StateFlow<MatchState> = _match.asStateFlow()
    private var matchKey: String? = null

    /** Match two profiles once both charts are ready; repeated calls with the same inputs reuse the result. */
    fun requestMatch(groomId: String, brideId: String) {
        val a = _charts.value[groomId] as? ChartState.Ready
        val b = _charts.value[brideId] as? ChartState.Ready
        if (a == null || b == null) { _match.value = MatchState.Waiting; matchKey = null; return }
        val key = "$groomId|$brideId|${a.json.hashCode()}|${b.json.hashCode()}"
        if (key == matchKey && _match.value !is MatchState.Failed) return
        matchKey = key
        _match.value = MatchState.Calculating
        viewModelScope.launch {
            val state = try {
                val json = Engine.match(a.json, b.json, "B")
                MatchState.Ready(withContext(Dispatchers.Default) { MatchModel.parse(json) })
            } catch (e: Throwable) {
                MatchState.Failed(e.message ?: e.toString())
            }
            if (matchKey == key) _match.value = state
        }
    }

    private val _muhurta = MutableStateFlow<MuhurtaState>(MuhurtaState.Idle)
    val muhurta: StateFlow<MuhurtaState> = _muhurta.asStateFlow()
    private val _muhurtaQuery = MutableStateFlow<MuhurtaQuery?>(null)
    /** The last search, so the form keeps its values when the user comes back to the screen. */
    val muhurtaQuery: StateFlow<MuhurtaQuery?> = _muhurtaQuery.asStateFlow()

    fun findMuhurta(q: MuhurtaQuery, lang: String) {
        _muhurtaQuery.value = q
        val charts = q.people.mapNotNull { (_charts.value[it] as? ChartState.Ready)?.json }
        _muhurta.value = MuhurtaState.Searching
        viewModelScope.launch {
            _muhurta.value = try {
                val req = JSONObject().put("event", q.event).put("from", q.from).put("to", q.to)
                    .put("lat", q.lat).put("lon", q.lon).put("tz", q.tz).put("top", 2000).put("lang", lang)
                    .put("weekday_rule", if (settings.weekdayHard) "hard" else "soft")
                val json = Engine.muhurta(req, charts)
                MuhurtaState.Ready(withContext(Dispatchers.Default) { MuhurtaResult.parse(json) })
            } catch (e: Throwable) {
                MuhurtaState.Failed(e.message ?: e.toString())
            }
        }
    }

    private val _forecasts = MutableStateFlow<Map<String, ForecastState>>(emptyMap())
    /** Three-year forecasts by profile id. Worked out only when asked for (a few seconds), then cached for the day. */
    val forecasts: StateFlow<Map<String, ForecastState>> = _forecasts.asStateFlow()
    private val forecastKeys = mutableMapOf<String, String>()

    fun requestForecast(p: Profile) {
        val request = p.chartRequest(LocalDate.now().toString(), settings.ayanamsa, settings.node).put("years", 3)
        val key = request.toString()
        if (forecastKeys[p.id] == key && _forecasts.value[p.id] !is ForecastState.Failed) return
        forecastKeys[p.id] = key
        _forecasts.update { it + (p.id to ForecastState.Calculating) }
        viewModelScope.launch {
            val cacheId = "${p.id}.forecast"
            val state = try {
                val json = withContext(Dispatchers.IO) { store.cachedChart(cacheId, key) } ?: Engine.forecast(request).also {
                    withContext(Dispatchers.IO) { store.cacheChart(cacheId, key, it) }
                }
                ForecastState.Ready(withContext(Dispatchers.Default) { ForecastModel.parse(json) })
            } catch (e: Throwable) {
                ForecastState.Failed(e.message ?: e.toString())
            }
            if (forecastKeys[p.id] == key) _forecasts.update { it + (p.id to state) }
        }
    }

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
        if (_selected.value == null) _selected.value = p.id
        persist()
        compute(p)
    }

    fun delete(id: String) {
        _profiles.update { list -> list.filterNot { it.id == id } }
        if (_selected.value == id) _selected.value = _profiles.value.firstOrNull()?.id
        _charts.update { it - id }
        _forecasts.update { it - id }
        forecastKeys.remove(id)
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
                withContext(Dispatchers.Default) { ChartState.Ready(summarize(json), ChartModel.parse(json), json) }
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
