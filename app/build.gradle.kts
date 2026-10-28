import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
    id("com.chaquo.python")
}

android {
    namespace = "com.gauravmishra.jyotish"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.gauravmishra.jyotish"
        minSdk = 26
        targetSdk = 36
        versionCode = 10
        versionName = "1.0.0-rc1"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        ndk {
            // Phones are arm64; x86_64 is for the emulator. Python 3.12+ is 64-bit only.
            abiFilters += listOf("arm64-v8a", "x86_64")
        }
    }

    // Release signing comes from the environment (a CI secret or the developer's machine), never from the repository:
    //   JYOTISH_KEYSTORE (path), JYOTISH_KEYSTORE_PASSWORD, JYOTISH_KEY_ALIAS, JYOTISH_KEY_PASSWORD.
    // Without them, debug and release builds are signed with the committed test key (keystore/README.md), so every CI
    // build installs over the last one on a test phone. A test-signed build must never be uploaded to Play.
    val keystore = System.getenv("JYOTISH_KEYSTORE")?.let { file(it) }?.takeIf { it.exists() }
    signingConfigs {
        create("test") {
            storeFile = rootProject.file("keystore/test-signing.jks")
            storePassword = "jyotish-test"
            keyAlias = "jyotish-test"
            keyPassword = "jyotish-test"
        }
        if (keystore != null) create("upload") {
            storeFile = keystore
            storePassword = System.getenv("JYOTISH_KEYSTORE_PASSWORD")
            keyAlias = System.getenv("JYOTISH_KEY_ALIAS")
            keyPassword = System.getenv("JYOTISH_KEY_PASSWORD")
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            signingConfig = signingConfigs.findByName("upload") ?: signingConfigs.getByName("test")
        }
        debug {
            signingConfig = signingConfigs.getByName("test")
        }
    }

    bundle {
        language { enableSplit = false }   // English and Hindi switch inside the app, so both must always be installed
    }

    buildFeatures {
        compose = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    androidResources {
        noCompress += "tsv"   // the place list is read with a buffered reader on first search
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
    val composeBom = platform("androidx.compose:compose-bom:2025.05.00")
    implementation(composeBom)
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-core")
    implementation("androidx.core:core-ktx:1.16.0")
    implementation("androidx.activity:activity-compose:1.10.1")
    implementation("androidx.navigation:navigation-compose:2.9.0")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.9.0")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.9.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.10.2")
    debugImplementation("androidx.compose.ui:ui-tooling")
    debugImplementation("androidx.compose.ui:ui-test-manifest")

    testImplementation("junit:junit:4.13.2")
    testImplementation("org.json:json:20240303")

    androidTestImplementation(composeBom)
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    androidTestImplementation("androidx.test.ext:junit:1.2.1")
    androidTestImplementation("androidx.test:runner:1.6.2")
}
