package com.gauravmishra.jyotish.data

import android.content.Context

/** Small preferences kept in SharedPreferences. Language is null until the Welcome screen is done. */
class AppSettings(context: Context) {
    private val prefs = context.getSharedPreferences("settings", Context.MODE_PRIVATE)

    var language: String?
        get() = prefs.getString("language", null)
        set(v) = prefs.edit().putString("language", v).apply()
    var chartStyle: String
        get() = prefs.getString("chart_style", "north") ?: "north"
        set(v) = prefs.edit().putString("chart_style", v).apply()
    var ayanamsa: String
        get() = prefs.getString("ayanamsa", "lahiri") ?: "lahiri"
        set(v) = prefs.edit().putString("ayanamsa", v).apply()
    var node: String
        get() = prefs.getString("node", "mean") ?: "mean"
        set(v) = prefs.edit().putString("node", v).apply()
    var weekdayHard: Boolean
        get() = prefs.getBoolean("weekday_hard", false)
        set(v) = prefs.edit().putBoolean("weekday_hard", v).apply()
    /** Name and website printed on the full report's cover and header. */
    /** The report credit is fixed (shown, never edited); values saved by earlier builds are ignored. */
    val reportBy: String get() = "Gaurav Mishra"
    val reportSite: String get() = "authorgaurav.com"
    /** On-phone registration: the app's user, kept only in this phone's private settings. */
    /** Unlock of the demo: "code" (an unlock code for unlockEmail) or "play" (a Google Play purchase); "" = not unlocked. */
    var unlockedVia: String
        get() = prefs.getString("unlocked_via", "") ?: ""
        set(v) = prefs.edit().putString("unlocked_via", v).apply()
    var unlockEmail: String
        get() = prefs.getString("unlock_email", "") ?: ""
        set(v) = prefs.edit().putString("unlock_email", v).apply()
    var unlockCode: String
        get() = prefs.getString("unlock_code", "") ?: ""
        set(v) = prefs.edit().putString("unlock_code", v).apply()
    var registered: Boolean
        get() = prefs.getBoolean("registered", false)
        set(v) = prefs.edit().putBoolean("registered", v).apply()
    var userName: String
        get() = prefs.getString("user_name", "") ?: ""
        set(v) = prefs.edit().putString("user_name", v).apply()
    var userEmail: String
        get() = prefs.getString("user_email", "") ?: ""
        set(v) = prefs.edit().putString("user_email", v).apply()
    var userPhone: String
        get() = prefs.getString("user_phone", "") ?: ""
        set(v) = prefs.edit().putString("user_phone", v).apply()
    /** The first-launch walkthrough has been seen or skipped. */
    var tourSeen: Boolean
        get() = prefs.getBoolean("tour_seen", false)
        set(v) = prefs.edit().putBoolean("tour_seen", v).apply()
    /** Forecasts and readings the user has finished viewing; used only to time the optional rating card. */
    var moments: Int
        get() = prefs.getInt("moments", 0)
        set(v) = prefs.edit().putInt("moments", v).apply()
    var reviewAsks: Int
        get() = prefs.getInt("review_asks", 0)
        set(v) = prefs.edit().putInt("review_asks", v).apply()
    var lastReviewAsk: Long
        get() = prefs.getLong("last_review_ask", 0L)
        set(v) = prefs.edit().putLong("last_review_ask", v).apply()
    /** The Today screen's city: "name|lat|lon|tz", or "" to use the person's residence or birthplace. */
    var todayPlace: String
        get() = prefs.getString("today_place", "") ?: ""
        set(v) = prefs.edit().putString("today_place", v).apply()
    /** Daily reminder time "HH:MM", or "" when the reminder is off (the default). */
    var reminderTime: String
        get() = prefs.getString("reminder_time", "") ?: ""
        set(v) = prefs.edit().putString("reminder_time", v).apply()
    /** "system" (default), "light" or "dark". */
    var theme: String
        get() = prefs.getString("theme", "system") ?: "system"
        set(v) = prefs.edit().putString("theme", v).apply()
}
