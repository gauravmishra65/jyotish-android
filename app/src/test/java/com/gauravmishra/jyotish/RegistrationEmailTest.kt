package com.gauravmishra.jyotish

import com.gauravmishra.jyotish.ui.CONTACT_EMAIL
import com.gauravmishra.jyotish.ui.registrationEmail
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class RegistrationEmailTest {
    @Test
    fun registrationDetailsOnly() {
        val (subject, body) = registrationEmail("Priya Nair", "priya@example.com", "", "hi", "1.0.0-rc1", "2026-10-29")
        assertEquals("Jyotish app registration: Priya Nair", subject)
        assertTrue(body.contains("Name: Priya Nair"))
        assertTrue(body.contains("Email: priya@example.com"))
        assertTrue(body.contains("Phone: -"))
        assertTrue(body.contains("Language: Hindi"))
        assertTrue(body.contains("App version: 1.0.0-rc1"))
        assertTrue(body.contains("Registered on: 2026-10-29"))
        assertFalse(body.contains("birth", ignoreCase = true))
        assertEquals("gaurav.mishra65@gmail.com", CONTACT_EMAIL)
    }
}
