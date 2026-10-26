plugins { id("com.android.application") }

android {
    namespace = "dev.mossback360.fixo.pipradius"
    compileSdk = 30
    defaultConfig {
        applicationId = "dev.mossback360.fixo.pipradius"
        minSdk = 30
        targetSdk = 30
        versionCode = 1
        versionName = "0.1-test"
    }
    buildTypes { release { isMinifyEnabled = false } }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    packaging { resources { merges += "META-INF/xposed/*" } }
}

dependencies { compileOnly("io.github.libxposed:api:102.0.0") }
