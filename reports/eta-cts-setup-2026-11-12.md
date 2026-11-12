# Circle to Search / Eta setup (2026-11-12)

- Device: HA2FNXNQ, OxygenOS 16. No SystemUI or Settings APK changed in this setup.
- Magisk `fixo_circle_to_search` v0.2-test installed from `temp3/稳定安装/01-当前启用-Magisk/22-circle-to-search-feature-config-v0.2-test.zip`; provides `com.google.android.feature.CONTEXTUAL_SEARCH`. `pm has-feature` is `true` after reboot.
- Vector v2.2-3080 installed from `temp3/稳定安装/02-基础框架/Vector-v2.2-3080-Release.zip`; Magisk Zygisk was enabled (setting `zygisk=1`) because Vector initially had no daemon socket.
- Eta v3.0.4 (`io.github.mangi.eta`, versionCode 2026091202) installed from `C:/Users/GY/Downloads/Eta-3.0.4.apk`, enabled in Vector and assigned its nine declared static scopes. Vector reports one enabled module; log shows Eta loaded in system/server and app processes. This confirms injection, not Circle to Search behavior.
- Exact Eta source: `E:/工程/github/xiaoxin Oxygen/temp3/Eta-v3.0.4-source`, Git tag `v3.0.4`, commit `bc952e27169bf83dbef86380a54fc5b159e5609d`. Its gesture-bar path hooks `OplusOcrScreenBusiness.onLongPressed`, calls `CircleToSearchInvoker`, and includes separate system_server contextual-search and Google eligibility hooks. Choose a specific feature before solidifying.
- Current live Settings v5.3 decompilation: `fixO/work/settings-v5.3-current-decoded-2026-11-12`, source APK SHA-256 `4d763c6c3a3fa15e7561d48434fce8b7373470ac5e0eec6adbbcc4cb11c1b098`, matching mounted Settings APK. The older `opd2403-oxygen-settings-decoded` tree is not this build.
