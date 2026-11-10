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
import com.gauravmishra.jyotish.data.TodayModel
import com.gauravmishra.jyotish.engine.Engine
import com.gauravmishra.jyotish.store.Licence
import com.gauravmishra.jyotish.store.Sales
import com.gauravmishra.jyotish.store.Store
import com.gauravmishra.jyotish.store.createStore
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

/** The city the Today screen works for. */
data class TodayPlace(val name: String, val lat: Double, val lon: Double, val tz: String) {
    fun encode() = listOf(name.replace("|", " "), lat, lon, tz).joinToString("|")
    companion object {
        fun decode(s: String): TodayPlace? = s.split("|").takeIf { it.size == 4 }?.let {
            runCatching { TodayPlace(it[0], it[1].toDouble(), it[2].toDouble(), it[3]) }.getOrNull()
        }
    }
}

sealed interface TodayState {
    data object Calculating : TodayState
    data class Ready(val model: TodayModel) : TodayState
    data class Failed(val message: String) : TodayState
}

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

/** The report kinds offered on the Reports screen, in order ("life" is the full multi-system reading). */
val REPORT_KINDS = listOf("life", "daily", "monthly", "annual", "mahadasha", "mangal", "kaal_sarp", "sade_sati", "chandra")
private val REPORT_FILE_NAMES = mapOf(
    "life" to "Astrology_Reading", "daily" to "Daily_Report", "monthly" to "Monthly_Report", "annual" to "Annual_Report",
    "mahadasha" to "Mahadasha_Report", "mangal" to "Mangal_Dosh_Report", "kaal_sarp" to "Kaal_Sarp_Report",
    "sade_sati" to "Sade_Sati_Report", "chandra" to "Chandra_Rashi_Report",
)

sealed interface ReportState {
    data object Calculating : ReportState
    data class Ready(val html: String, val file: java.io.File) : ReportState
    data class Failed(val message: String) : ReportState
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

    // ---- Edition: demo (one profile until unlocked), full, or play (unlocked by a Google Play purchase) ----
    val shop: Store = createStore(app)
    private fun unlockedNow(): Boolean = BuildConfig.EDITION == "full" || when (settings.unlockedVia) {
        "code" -> Licence.verify(settings.unlockEmail, settings.unlockCode)
        "play" -> BuildConfig.EDITION == "play"
        else -> false
    }
    private val _full = MutableStateFlow(unlockedNow())
    /** True when every feature is open: the full edition, or a demo unlocked by a code or a Play purchase. */
    val full: StateFlow<Boolean> = _full.asStateFlow()
    /** A new profile is allowed: always in the full version, and while the demo is under its limit. */
    fun canAddProfile(): Boolean = _full.value || _profiles.value.size < Sales.FREE_PROFILES

    /** Checks an unlock code for an email; saves it and opens the full version when it matches. */
    fun unlockWithCode(email: String, code: String): Boolean {
        if (!Licence.verify(email, code)) return false
        settings.unlockEmail = Licence.normalize(email); settings.unlockCode = code.trim(); settings.unlockedVia = "code"
        _full.value = true
        return true
    }

    fun markPlayPurchase() { settings.unlockedVia = "play"; _full.value = true }

    init {
        // Play edition: restore a purchase after a reinstall, and close it again if Play reports it refunded.
        if (shop.available) shop.owned { owned ->
            when {
                owned == true -> markPlayPurchase()
                owned == false && settings.unlockedVia == "play" -> { settings.unlockedVia = ""; _full.value = unlockedNow() }
            }
        }
    }

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

    private val _reports = MutableStateFlow<Map<String, ReportState>>(emptyMap())
    /** Reports by "profileId|lang|kind" (kind "life" is the full reading). Worked out on request, cached for the day. */
    val reports: StateFlow<Map<String, ReportState>> = _reports.asStateFlow()
    private val reportKeys = mutableMapOf<String, String>()

    fun requestReport(p: Profile, lang: String, kind: String = "life") {
        val slot = "${p.id}|$lang|$kind"
        val request = p.chartRequest(LocalDate.now().toString(), settings.ayanamsa, settings.node)
            .put("years", 3).put("lang", lang).put("by", settings.reportBy).put("site", settings.reportSite).put("kind", kind)
        if (kind == "daily" || kind == "monthly") placeFor(p)?.let {
            request.put("today_lat", it.lat).put("today_lon", it.lon).put("today_tz", it.tz).put("today_place", it.name)
        }
        val key = request.toString()
        if (reportKeys[slot] == key && _reports.value[slot] !is ReportState.Failed) return
        reportKeys[slot] = key
        _reports.update { it + (slot to ReportState.Calculating) }
        viewModelScope.launch {
            val cacheId = if (kind == "life") "${p.id}.report.$lang" else "${p.id}.report.$kind.$lang"
            val state = try {
                val json = withContext(Dispatchers.IO) { store.cachedChart(cacheId, key) }
                    ?: (if (kind == "life") Engine.report(request) else Engine.specialReport(request)).also {
                        withContext(Dispatchers.IO) { store.cacheChart(cacheId, key, it) }
                    }
                val html = JSONObject(json).getString("html")
                // A copy in the cache folder, named after the person and the report, for sharing.
                val file = withContext(Dispatchers.IO) {
                    val dir = java.io.File(getApplication<Application>().cacheDir, "reports").apply { mkdirs() }
                    val safe = p.name.replace(Regex("[^A-Za-z0-9]+"), "_").trim('_').ifEmpty { "Reading" }
                    val what = REPORT_FILE_NAMES[kind] ?: "Astrology_Reading"
                    java.io.File(dir, "${safe}_$what${if (lang == "hi") "_Hindi" else ""}.html").apply { writeText(html) }
                }
                ReportState.Ready(html, file)
            } catch (e: Throwable) {
                android.util.Log.e("REPORT", "report $kind failed", e)
                ReportState.Failed(e.message ?: e.toString())
            }
            if (reportKeys[slot] == key) _reports.update { it + (slot to state) }
        }
    }

    private val _theme = MutableStateFlow(settings.theme)
    val theme: StateFlow<String> = _theme.asStateFlow()
    fun setTheme(t: String) { settings.theme = t; _theme.value = t }

    private val _todayPlace = MutableStateFlow(TodayPlace.decode(settings.todayPlace))
    /** The Today screen's chosen city; null = the person's residence, else their birthplace. */
    val todayPlace: StateFlow<TodayPlace?> = _todayPlace.asStateFlow()
    fun setTodayPlace(p: TodayPlace?) { settings.todayPlace = p?.encode() ?: ""; _todayPlace.value = p }

    /** The city used for a person on the Today screen. */
    fun placeFor(p: Profile?): TodayPlace? = _todayPlace.value ?: p?.let {
        if (it.hasResidence) TodayPlace(it.residence, it.resLat!!, it.resLon!!, it.tz) else TodayPlace(it.place, it.lat, it.lon, it.tz)
    }

    private val _today = MutableStateFlow<TodayState>(TodayState.Calculating)
    val today: StateFlow<TodayState> = _today.asStateFlow()
    private var todayKey = ""

    /**
     * The day's panchang for [date] at [place], and the day for [p] once their chart is ready. Sub-second; the result
     * is kept until the date, place, person or settings change.
     */
    fun requestToday(date: LocalDate, place: TodayPlace?, p: Profile?) {
        if (place == null) { _today.value = TodayState.Failed("no-place"); return }
        val chartJson = p?.let { (_charts.value[it.id] as? ChartState.Ready)?.json }
        val request = JSONObject().put("date", date.toString()).put("lat", place.lat).put("lon", place.lon).put("tz", place.tz)
            .put("place", place.name).put("ayanamsa", settings.ayanamsa).put("festival_days", 45)
        if (date == LocalDate.now()) request.put("now", java.time.LocalDateTime.now(java.time.ZoneId.of(place.tz)).withSecond(0).withNano(0).toString())
        if (p != null && chartJson != null) request.put("person", personFor(p, chartJson))
        val key = request.toString().replace(Regex("\"now\":\"[^\"]*\""), "") + (chartJson != null)
        if (key == todayKey && _today.value is TodayState.Ready) return
        todayKey = key
        if (_today.value !is TodayState.Ready) _today.value = TodayState.Calculating
        viewModelScope.launch {
            val state = try {
                val json = Engine.today(request)
                TodayState.Ready(withContext(Dispatchers.Default) { TodayModel.parse(json) })
            } catch (e: Throwable) {
                android.util.Log.e("TODAY", "could not work out the day", e)
                TodayState.Failed(e.message ?: e.toString())
            }
            if (todayKey == key) _today.value = state
        }
    }

    private fun personFor(p: Profile, chartJson: String): JSONObject {
        val v = JSONObject(chartJson).getJSONObject("vedic")
        val cur = v.getJSONObject("dashas").getJSONObject("vimshottari").optJSONObject("current")
        return JSONObject().put("name", p.name)
            .put("moon_lon", v.getJSONObject("planets").getJSONObject("Moon").getDouble("lon"))
            .put("lagna_lon", v.getJSONObject("lagna").getDouble("lon"))
            .put("dasha", cur ?: JSONObject.NULL)
    }

    private val _userName = MutableStateFlow(settings.userName.takeIf { settings.registered } ?: "")
    /** The registered user's name for the Home greeting ("" when not registered). */
    val userName: StateFlow<String> = _userName.asStateFlow()
    fun refreshUser() { _userName.value = settings.userName.takeIf { settings.registered } ?: "" }

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

    /**
     * Adds the people from a backup file: one already saved (same id) is replaced by the backup's copy. The demo edition
     * keeps its limit, so only as many new people as it allows are added. Returns (added or updated, left out).
     */
    fun restore(people: List<Profile>): Pair<Int, Int> {
        var done = 0
        var skipped = 0
        people.forEach { p ->
            if (_profiles.value.any { it.id == p.id } || canAddProfile()) { addOrUpdate(p); done++ } else skipped++
        }
        return done to skipped
    }

    fun delete(id: String) {
        _profiles.update { list -> list.filterNot { it.id == id } }
        if (_selected.value == id) _selected.value = _profiles.value.firstOrNull()?.id
        _charts.update { it - id }
        _forecasts.update { it - id }
        _reports.update { m -> m.filterKeys { !it.startsWith("$id|") } }
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
