package com.gauravmishra.jyotish

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import androidx.work.CoroutineWorker
import androidx.work.ExistingWorkPolicy
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.WorkerParameters
import com.gauravmishra.jyotish.data.AppSettings
import com.gauravmishra.jyotish.data.ProfileStore
import com.gauravmishra.jyotish.data.TodayModel
import com.gauravmishra.jyotish.engine.Engine
import org.json.JSONObject
import java.time.Duration
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.util.Locale

/**
 * The optional daily reminder: one notification a day, at the time the user chose, with the day's tithi, nakshatra,
 * Rahu Kaal and any festival. Off by default. Everything is worked out on the phone; nothing is sent anywhere.
 */
object Reminders {
    private const val WORK = "daily-panchang"
    const val CHANNEL = "daily"
    const val EXTRA_OPEN = "open"
    /** Set when the app is opened from the reminder; the app then shows Today. */
    val pendingOpen = kotlinx.coroutines.flow.MutableStateFlow<String?>(null)

    fun schedule(ctx: Context, time: String) {
        val t = runCatching { LocalTime.parse(time) }.getOrNull() ?: return cancel(ctx)
        val now = LocalDateTime.now()
        var next = now.toLocalDate().atTime(t)
        if (!next.isAfter(now.plusMinutes(1))) next = next.plusDays(1)
        val req = OneTimeWorkRequestBuilder<ReminderWorker>().setInitialDelay(Duration.between(now, next)).build()
        WorkManager.getInstance(ctx).enqueueUniqueWork(WORK, ExistingWorkPolicy.REPLACE, req)
    }

    fun cancel(ctx: Context) {
        WorkManager.getInstance(ctx).cancelUniqueWork(WORK)
    }

    fun canNotify(ctx: Context): Boolean = Build.VERSION.SDK_INT < 33 ||
        ContextCompat.checkSelfPermission(ctx, Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED

    fun ensureChannel(ctx: Context, name: String) {
        if (Build.VERSION.SDK_INT >= 26) {
            val nm = ctx.getSystemService(NotificationManager::class.java)
            nm.createNotificationChannel(NotificationChannel(CHANNEL, name, NotificationManager.IMPORTANCE_DEFAULT))
        }
    }
}

class ReminderWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
    override suspend fun doWork(): Result {
        val ctx = applicationContext
        val settings = AppSettings(ctx)
        val time = settings.reminderTime
        if (time.isBlank()) return Result.success()
        try {
            val lang = settings.language ?: "en"
            val local = ctx.createConfigurationContext(android.content.res.Configuration(ctx.resources.configuration).apply { setLocale(Locale.forLanguageTag(lang)) })
            val place = TodayPlace.decode(settings.todayPlace) ?: ProfileStore(ctx.filesDir).load().firstOrNull()?.let {
                if (it.hasResidence) TodayPlace(it.residence, it.resLat!!, it.resLon!!, it.tz) else TodayPlace(it.place, it.lat, it.lon, it.tz)
            }
            if (place != null && Reminders.canNotify(ctx)) {
                Engine.start(ctx as android.app.Application)
                val req = JSONObject().put("date", LocalDate.now(java.time.ZoneId.of(place.tz)).toString()).put("lat", place.lat).put("lon", place.lon)
                    .put("tz", place.tz).put("place", place.name).put("ayanamsa", settings.ayanamsa).put("festival_days", 0)
                val m = TodayModel.parse(Engine.today(req))
                val fest = m.festivals.filter { it.date == m.date }.joinToString(" · ") { it.name.of(lang) }
                val title = if (fest.isNotBlank()) fest else local.getString(R.string.reminder_title, m.tithi.name.of(lang), m.paksha.of(lang))
                val rahu = m.periods["rahu_kalam"]?.let { local.getString(R.string.today_rahu) + " " + it.from + "–" + it.to } ?: ""
                val body = listOf("${m.tithi.name.of(lang)} · ${m.nakshatra.name.of(lang)}", rahu, place.name.substringBefore(",")).filter { it.isNotBlank() }.joinToString(" · ")
                Reminders.ensureChannel(ctx, local.getString(R.string.reminder_channel))
                val open = PendingIntent.getActivity(ctx, 0, Intent(ctx, MainActivity::class.java).putExtra(Reminders.EXTRA_OPEN, "today")
                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP), PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
                val n = NotificationCompat.Builder(ctx, Reminders.CHANNEL).setSmallIcon(R.drawable.ic_launcher_monochrome)
                    .setContentTitle(title).setContentText(body).setStyle(NotificationCompat.BigTextStyle().bigText(body))
                    .setContentIntent(open).setAutoCancel(true).build()
                @Suppress("MissingPermission")
                NotificationManagerCompat.from(ctx).notify(1, n)
            }
        } catch (e: Throwable) {
            android.util.Log.w("REMINDER", "could not build the reminder", e)
        } finally {
            Reminders.schedule(ctx, time)          // tomorrow at the same time
        }
        return Result.success()
    }
}
