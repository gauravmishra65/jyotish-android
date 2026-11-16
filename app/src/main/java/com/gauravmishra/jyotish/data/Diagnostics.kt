package com.gauravmishra.jyotish.data

import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

/**
 * A short log of anything that went wrong while the app was running (v29), kept in memory only. It lets a person send
 * the author a useful report instead of "it did not work". Nothing is sent anywhere by itself, and no birth data is
 * recorded: only where the problem happened and what the error said.
 */
object Diagnostics {
    private val stamp: DateTimeFormatter = DateTimeFormatter.ofPattern("dd MMM HH:mm:ss")
    private const val MAX = 50
    private val entries = ArrayDeque<String>()

    @Synchronized
    fun note(where: String, t: Throwable) = note(where, t::class.java.simpleName + ": " + (t.message ?: ""))

    @Synchronized
    fun note(where: String, message: String) {
        entries.addLast("${LocalDateTime.now().format(stamp)}  $where — ${message.take(300)}")
        while (entries.size > MAX) entries.removeFirst()
    }

    @Synchronized
    fun lines(): List<String> = entries.toList()

    @Synchronized
    fun text(appVersion: String): String =
        (listOf("Gaurav Jyotish $appVersion", "Android ${android.os.Build.VERSION.RELEASE}, ${android.os.Build.MODEL}", "") + entries)
            .joinToString("\n")

    @Synchronized
    fun clear() = entries.clear()
}
