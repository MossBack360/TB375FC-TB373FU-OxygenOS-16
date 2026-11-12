# Circle to Search / Eta setup (2026-11-12)

- Device: HA2FNXNQ, OxygenOS 16. No SystemUI or Settings APK changed in this setup.
- Magisk `fixo_circle_to_search` v0.2-test installed from `temp3/稳定安装/01-当前启用-Magisk/22-circle-to-search-feature-config-v0.2-test.zip`; provides `com.google.android.feature.CONTEXTUAL_SEARCH`. `pm has-feature` is `true` after reboot.
- Vector v2.2-3080 installed from `temp3/稳定安装/02-基础框架/Vector-v2.2-3080-Release.zip`; Magisk Zygisk was enabled (setting `zygisk=1`) because Vector initially had no daemon socket.
- Eta v3.0.4 (`io.github.mangi.eta`, versionCode 2026091202) installed from `C:/Users/GY/Downloads/Eta-3.0.4.apk`, enabled in Vector and assigned its nine declared static scopes. Vector reports one enabled module; log shows Eta loaded in system/server and app processes. This confirms injection, not Circle to Search behavior.
- Exact Eta source: `E:/工程/github/xiaoxin Oxygen/temp3/Eta-v3.0.4-source`, Git tag `v3.0.4`, commit `bc952e27169bf83dbef86380a54fc5b159e5609d`. Its gesture-bar path hooks `OplusOcrScreenBusiness.onLongPressed`, calls `CircleToSearchInvoker`, and includes separate system_server contextual-search and Google eligibility hooks. Choose a specific feature before solidifying.
- Current live Settings v5.3 decompilation: `fixO/work/settings-v5.3-current-decoded-2026-11-12`, source APK SHA-256 `4d763c6c3a3fa15e7561d48434fce8b7373470ac5e0eec6adbbcc4cb11c1b098`, matching mounted Settings APK. The older `opd2403-oxygen-settings-decoded` tree is not this build.

## Eta page interpretation and ROM integration boundary

The visible `Root 与系统增强 > Gemini 与一圈即搜` row is a capability description (`res/values/root_capabilities.xml`), not a single switch or one implementation. `SettingsScreen.kt` has separate Gemini hotword/voice toggles and Circle to Search gesture-bar/two-finger toggles.

Exact v3.0.4 paths:
- `hook/system/ContextualSearchHooks.kt`: ensures `ContextualSearchManagerService` starts, selects Google as provider, and allows SystemUI/ColorDirect callers.
- `hook/system/SystemUiHooks.kt` + `CircleToSearchInvoker.kt`: intercepts `OplusOcrScreenBusiness.onLongPressed` and calls `IContextualSearchManager.startContextualSearch(2)`.
- `hook/google/GoogleEligibilityHooks.kt` + `GoogleAppHooks.kt`: process-local Google eligibility features/property and Samsung S24 Ultra Build spoof; separate optional Gemini voice-command repair.
- `hook/colordirect/`: two-finger path.

Current device: `contextual_search` binder exists with Eta enabled; `ro.opa.eligible_device=true`; global `GOOGLE_BUILD` and `GOOGLE_EXPERIENCE` are false; Google App remains under `/data/app`; assistant and voice interaction service are Google. The feature XML from module 22 is true. These facts do not prove gesture behavior or that Eta can be removed. A Settings APK change alone cannot replace these runtime hooks. To solidify without Eta, first isolate which of these behaviors the user wants, then modify the correct ROM layer and A/B test against Eta.

## User-confirmed narrow target (2026-11-12)

The target is the Eta switch `gesture_bar_circle_to_search`: long-press Home bar invokes Circle to Search. User reports it works when Eta's option is enabled. Current OOS SystemUI already recognizes long press and calls `OplusOcrScreenBusiness.onLongPressed()`; its original implementation only dispatches to `currentServiceHandler`. Eta intercepts exactly that method, checks Google entry and `contextual_search` binder, then calls `IContextualSearchManager.startContextualSearch(2)`; it suppresses the original OCR dispatch on success. Source: `work/oxygen-ui-current-2026-09-09/SystemUI-decoded/smali_classes6/com/oplus/systemui/navigationbar/ocrscreen/OplusOcrScreenBusiness.smali` and Eta `hook/system/SystemUiHooks.kt`, `CircleToSearchInvoker.kt`.

Therefore existing gesture detection is present, but the Google contextual-search dispatch is not in this SystemUI path. The current `contextual_search` service is alive with Eta loaded; current framework resource lookup `android:string/config_defaultContextualSearchPackageName` returned blank. Do not infer from this session that the service would stay alive without Eta. Solidification should target the narrow dispatch plus service/provider configuration, not Settings UI or a broad SystemUI replacement. Google App eligibility hooks may still be necessary; test that separately after a native dispatch works.
