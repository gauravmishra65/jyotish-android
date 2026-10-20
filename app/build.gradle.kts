import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.chaquo.python")
}

android {
    namespace = "com.gauravmishra.jyotish"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.gauravmishra.jyotish"
        minSdk = 26
        targetSdk = 36
        versionCode = 1
        versionName = "0.1-spike"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        ndk {
            // Phones are arm64; x86_64 is for the emulator. Python 3.12+ is 64-bit only.
            abiFilters += listOf("arm64-v8a", "x86_64")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

kotlin {
    compilerOptions {
        jvmTarget.set(JvmTarget.JVM_17)
    }
}

chaquopy {
    defaultConfig {
        version = "3.13"
        pip {
            // pyswisseph has no Android wheel on PyPI: CI builds it with cibuildwheel into ./wheels.
            options("--find-links", rootProject.file("wheels").absolutePath)
            options("--only-binary", ":all:")
            install("pyswisseph==2.10.3.2")
            install("tzdata")
        }
    }
}

dependencies {
    androidTestImplementation("androidx.test.ext:junit:1.2.1")
    androidTestImplementation("androidx.test:runner:1.6.2")
}
