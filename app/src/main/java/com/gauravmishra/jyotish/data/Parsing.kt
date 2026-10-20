package com.gauravmishra.jyotish.data

import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.time.format.ResolverStyle

val DMY = DateTimeFormatter.ofPattern("dd-MM-uuuu").withResolverStyle(ResolverStyle.STRICT)

/** "14-07-1988" to 1988-07-14, or null if it is not a real date between 1800 and today. */
fun parseDmy(s: String): LocalDate? = try {
    LocalDate.parse(s.trim().replace('/', '-').replace('.', '-'), DMY).takeIf { it.year >= 1800 && !it.isAfter(LocalDate.now()) }
} catch (e: Exception) {
    null
}

/** "9:05" or "09:05" to "09:05", or null. */
fun parseHm(s: String): String? {
    val m = Regex("^(\\d{1,2})[:.](\\d{2})$").find(s.trim()) ?: return null
    val h = m.groupValues[1].toInt(); val min = m.groupValues[2].toInt()
    return if (h in 0..23 && min in 0..59) "%02d:%02d".format(h, min) else null
}

