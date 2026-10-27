# TB375FC OxygenOS port handoff

## 2026-10-27 PiP low-weight sweep

Installed the signature-compatible v0.5-low-weight-test LSPosed APK under the existing package; only the Ext validation lower bound changed from 0.5 to 0.0. User-confirmed Chrome Home PiP: 0.1 nearly square/no mismatch (screenshot matched), 0.5 rounded/no mismatch, 0.6 normal, 1.5 and 1.6 mismatch; 1.3 was already abnormal. A live 0.1 SurfaceFlinger dump showed both Chrome buffered children still carrying radius about 40 in display space and weight 0.1, so the visual squareness is weight-dependent rendering rather than a zero radius. Zero was not tested due boundary risk and low diagnostic value. Restored live properties to `native` / `1.7`; SystemUI PID 2298 remained present. The v0.5 APK is at `out/pip-native-radius-v0.5-low-weight-2026-10-27/`, and v0.3 is preserved for rollback. See `reports/pip-smooth-radius-weight-ab-2026-10-26.md`.

## 2026-10-26 PiP radius weight diagnostic (newer than the v0.1 note below)

Additional 1.3 A/B: owner still saw the stable defect, so 1.7 is not a uniquely failing literal value. In the live abnormal Chrome Home PiP, the two visible buffered Chrome children **both** had weight 1.3: outer 994×559 at radius 40 / 1×, video 800×432 scaled ~1.24× with local radius ~32.2 (display ~40), vertically inset ~11 px. Thus the outer layer did receive the override; differing geometry/content plus native smooth composition remain under investigation. Active task 43 was pinned, Launcher top-resumed. Restored `native` / `1.7` debug properties and SystemUI PID 2268 remained stable. See the A/B report for exact layer IDs and bounds.

Later same-video weight sweep: 1.9 still had an obvious defect nearly like 1.7; 2.0 again gave normal stable corners but a brief creation jump; 2.5 produced a smaller settled corner and a more obvious jump. 2.1 was set but never visually graded before the owner asked for a larger value. Debug properties were restored to `native` / `1.7` (the weight property is ignored in native mode), with SystemUI PID 2268 stable. An earlier animation stage using a different smooth weight is a hypothesis, not yet a captured transaction. See the updated A/B report.

Vector module v0.3-lifecycle-test is installed and SystemUI booted normally. Unlike v0.1, its PiP hook is confirmed by live per-call logs. In the same Chrome fullscreen-to-Home PiP test: `native` normal, `stock` abnormal, Ext weight `2.0` approximately normal, Ext weight `1.7` abnormal. The user still notices a brief corner change only during PiP creation, but has explicitly deferred that issue. A v0.4 experiment also intercepted the Launcher `SwipePipToHomeAnimator` helper calls; logs confirmed both Launcher and SystemUI hits, yet the brief jump remained. v0.4 was rolled back; source and device are on v0.3, scoped only to SystemUI, with debug mode defaulting to `native`. Focus now is the original stable bug and why physical display plus screenrecord show it while screencap does not. See `reports/pip-smooth-radius-weight-ab-2026-10-26.md` and `reports/pip-radius-composition-trace-2026-10-26.md`. The older v0.1 visual result must not be cited as proof that its hook fired, because its `isFirstPackage()` guard may have excluded SystemUI.

## 2026-10-26 PiP native-radius test confirmed

The owner confirmed that Chrome fullscreen-to-Home PiP corners became visually normal with Vector v2.2 (3080) and LSPosed APK `dev.mossback360.fixo.pipradius` v0.1-test enabled. Vector reports the module loaded and scoped to `com.android.systemui`; the device boots and SystemUI PID 2271 remained stable. The hook redirects only WM Shell PiP `round(...)` calls to Android's native `nativeSetCornerRadius()`, bypassing OPlus's smooth-radius extension in that path. Installed APK backup: `out/pip-corner-ext-analysis-2026-10-26/fixo-pip-native-radius-v0.1-installed.apk` (SHA-256 `0fc628e760271f393e3cf5d4ca8693df0f563c93d394910e4e492787ce035c7e`). Source: `patch/pip-native-radius-hook/`. A diagnostic v0.2 was built but not installed; do not replace the user-confirmed v0.1. No per-call hit log was captured, so this is a user-confirmed visual repair, not a fully traced native mechanism. Old SurfaceFlinger and SkiaGL Magisk A/B modules remain disabled.

## 2026-10-26 PiP SurfaceFlinger A/B addendum

The one-boot OPD2601 ColorOS SurfaceFlinger trial did **not** reach PiP rendering. The ColorOS binary required an additional MixLut3D library and, after it was supplied, failed at startup on a symbol missing from OxygenOS `libgui.so`: `IGraphicBufferProducer::setBbqQueuedBufCnt(int)`. The temporary Magisk module `fixo_pip_color_sf_ab_test` v0.1 was disabled immediately and the device rebooted to a complete OxygenOS boot; stock SurfaceFlinger and SystemUI are running. No partition was flashed. Do not repeat a single-binary transplant. Details and SHA-256 identities: `out/pip-sf-color-ab-v0.1-2026-10-26/TEST_RESULT.md`.

## 2026-10-23 PiP investigation addendum

The owner temporarily flashed a near-version OPD2601 ColorOS port, where Chrome 640x360 Home PiP was visually normal. Its graphics chain and Home/Settings PiP samples are saved under `E:\工程\github\xiaoxin Oxygen\temp3\OPD2601_graphics_2026-10-23`. After returning to OxygenOS, the same PiP pattern was confirmed abnormal on OPlus Home and normal with Settings foreground; raw samples and current graphics binaries are under `E:\工程\github\xiaoxin Oxygen\temp3\OOS16_pip_2026-10-23`.

The first strong difference was SkiaVk RenderEngine on OxygenOS versus SkiaGL on ColorOS. A two-property Magisk module (`fixo_pip_skiagl_test` v0.2) genuinely switched OxygenOS SurfaceFlinger to `RE GLES (Ganesh)`, but the owner confirmed the Chrome PiP corner defect remained. The module was disabled and the device rebooted back to stock `skiavkthreaded`/Vulkan; it must not be added to a stable module set. Test ZIP, raw GL PiP dumps and result are under `out/pip-renderengine-skiagl-v0.2-test-2026-10-23/`. The earlier v0.1 experiment changed only the backend property and did not actually switch the renderer, so it is invalid as a visual test. Next focus: PiP bounds/crop and Home-specific window transaction differences, not a blanket graphics-library transplant.

Updated: 2026-09-15

The owner confirmed a compatible trio on 2026-09-15: `fixo_fullscreen_caption` v0.5, `fixo_opd2514_ai_addons` v2.5, and `fixo_freeform_corner_gesture` v1.3. With all three together, both the three-finger Mind Space gesture and bottom-corner fullscreen-to-freeform gesture work normally. Preserve these exact versions as a tested combination and do not add `fixo_ai_a30_restore`.

The owner clean-flashed the OxygenOS 16 port and confirmed a staged base restore containing exactly 12 active Magisk modules. That historical snapshot contained no AI add-on or third-party power module and is archived at `out/confirmed-selected-modules-2026-09-14/LIVE_DEVICE_STATE.txt`. Later work added launcher-corner v1.1-test, smart-refresh v0.3, and camera-safe v2.0 before the 2026-09-15 AI/freeform trio was confirmed.

The confirmed Settings owner is `fixo_settings_confirmed` v3.9. It supersedes v3.6 and combines the accepted OxygenOS UI polish with the working ColorOS-compatible RAM-expansion activity/writeback.

The confirmed SystemUI owner is `fixo_fullscreen_caption` v0.5. It was installed only after the large Settings/global-app payloads completed a separate boot and package scan. Runtime verification reported `caption-overlay=ok pid=7008`; the PID remained stable and the mounted APK SHA-256 was `92c57e647c9520cb043be1d0a0cf010c6f1e7dec2b72129837b45cc261e57560`.

Confirmed user-visible behavior includes:

- fullscreen three-dot controls and bottom-corner freeform entry;
- Settings v3.9 and RAM expansion;
- camera startup-policy fix, display PQ bridge, global apps, OTA, smart cover, speaker rotation, and ZUI privacy pages;
- ASI screen attention glue v0.2: boot binding now retries until successful, and face-plus-gaze presence refreshes `PowerManager.userActivity()` without injecting key/touch input. The owner confirmed it works. Accepted limitations: it can briefly dim then brighten because sampling occurs near timeout, and the landscape workaround can treat a nearby person as attentive even when they are not looking directly at the panel;
- ZUI-sensitive lift-to-wake v0.2 following the OxygenOS switch.
- Smart refresh v0.3 exposes the stock `智能切换` option and native mode 0. A gesture sampled `120 Hz`, then returned to `60 Hz` after five seconds idle. Settings scrolling stays at `60 Hz` because `com.android.settings` is in the stock OPlus TouchIdle blacklist; the owner accepted v0.3 as usable with this limitation.
- ZUI Camera safe-capture v2.0 fixes the runtime algorithm-support refresh so the Morpho SR-disable switch remains effective. The owner confirmed zoom capture no longer crashes.
- Launcher-corner v1.1-test sets only `ro.oplus.display.rc.size=26,26,26,26`. The owner confirmed the desktop-launch, fullscreen-to-freeform, and A/B gesture-bar quick-switch transitions; the previous asymmetric oversized-radius flash is gone.

Do not describe smart-refresh v0.3 as an all-app, every-touch high-refresh fix. Changing that behavior requires a separate `oplus_vrr_config.json` experiment and regression testing across video, games, brightness, and thermal policy.

Do not reinstall the OPD2514/A.30 AI add-ons as part of this baseline. Panorama v1.4, formal-corner v0.4, smooth-corner, Dolby, material-stroke, and third-party speaker modules remain rejected or unconfirmed.

The `modules-2026-09-14` GitHub release publishes only new/version-changed modules. PQ, global apps, OTA, ZUI privacy, and hall v2 reuse the 2026-09-09 release because their versioned functional payloads did not change.

The authoritative confirmed inventory is now 15 active IDs. `fixo_launcher_corner_radius` v1.1-test supersedes the disabled v1.0 module under the same ID. The standalone `fixo_freeform_smooth_corner` experiment is not installed; SystemUI v0.5 separately retains its accepted drag-corner fallback.

`fixo_attention_asi` is now v0.2-trial under the existing module ID. Its confirmed archive is `out/attention-asi-glue-v0.2-2026-09-14/fixo-attention-asi-v0.2-trial-magisk.zip`, SHA-256 `c05e9acc429e691d737eae054354dbb8ee7a9fb20fd54f4b0605946d2187613e`.

See `reports/module-audit-2026-09-14.md` for superseded and rejected modules that must not be added to the baseline.
