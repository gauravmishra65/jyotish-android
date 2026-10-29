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
    var reportBy: String
        get() = prefs.getString("report_by", "Gaurav Mishra") ?: "Gaurav Mishra"
        set(v) = prefs.edit().putString("report_by", v).apply()
    var reportSite: String
        get() = prefs.getString("report_site", "authorgaurav.com") ?: "authorgaurav.com"
        set(v) = prefs.edit().putString("report_site", v).apply()
    /** On-phone registration: the app's user, kept only in this phone's private settings. */
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
}
