# Current state — 2026-09-14

## Device and ROM

- Lenovo Xiaoxin Pad Pro 2025, hardware code `TB375FC`, MediaTek MT6897/Dimensity 8300 family.
- The ported OxygenOS 16 identifies itself as `OPD2203`; Android 16/API 36.
- Current fingerprint: `OnePlus/OPD2203/TB375FC:16/BP2A.250605.015/T.R4T3.4f08503-2ad84ab:user/release-keys`.
- The owner clean-flashed the port on 2026-09-14 before the confirmed module set was reinstalled.
- Root is available through Magisk. ADB executable: `C:\Program Files (x86)\MiFlashPro\adb.exe`.
- The tablet clock is unreliable after a clean flash. Use host-side artifact dates and saved snapshots for chronology.
- The live animation tier is the OxygenOS baseline: `persist.sys.oplus.anim_level=2`. The third-party `TB375FC_ColosOS` module is not installed.

## Confirmed working behavior

- Settings v3.9 opens normally and retains the previously confirmed OxygenOS UI, icons, About-device card, easter egg, and ColorOS-compatible RAM-expansion activity/writeback.
- International OnePlus account and Gallery components are active.
- OxygenOS software-update page/activity and required system permissions work.
- Smart-cover close/open sleep and wake works and follows the Settings switch.
- Display adaptive color and color-mode controls reach the MTK PQ engine. Color-mode changes have a long visible delay; the owner accepts this as a device characteristic.
- Fullscreen three-dot window controls and the bottom-corner fullscreen-to-freeform gesture work again after the clean-flash staged restore.
- SystemUI v0.5 retains the accepted drag-corner fallback and follow-finger back gesture animation.
- WeChat scanner and ZUI Camera startup policy failures remain fixed by the camera-policy v1.1 module.
- ZUI Camera legal/privacy links work through the Lenovo privacy package.
- Four-speaker channels rotate with the display through the v2.1 bridge.
- Screen attention v0.1 is confirmed: with a 10-second timeout, continuous attention kept the display on for at least 25 seconds.
- Lift-to-wake v0.2 is active and follows the original OxygenOS Lift to wake switch while using the more sensitive ZUI MTK sensor type 23 path.
- Smart refresh v0.3 exposes the stock `智能切换` option and selects native secure mode 0. An active gesture sampled `120 Hz`; five seconds idle sampled `60 Hz`.

## Confirmed active modules

The 2026-09-14 clean-flash restore contains exactly these 12 active modules and no disable markers:

- `fixo_attention_asi` 0.1.
- `fixo_camera_optimize_disable` 1.1.
- `fixo_display_pq` 1.0.
- `fixo_freeform_corner_gesture` 1.2.
- `fixo_fullscreen_caption` 0.5.
- `fixo_global_apps` 1.0.
- `fixo_ota_system` 1.0.
- `fixo_settings_confirmed` 3.9. This is the sole Settings payload owner and supersedes v3.6.
- `fixo_speaker_rotation_prop` 2.1.
- `fixo_wake_gesture_glue` 0.2.
- `fixo_zui_lenovo_privacy` 1.2.
- `xiaoxin_hall_cover` 2.0.

Subsequent active additions after the 12-module clean-flash snapshot:

- `fixo_launcher_corner_radius` 1.0. It fixes the desktop-to-fullscreen transition corner but does not solve the separate A/B quick-switch corner issue.
- `fixo_smart_refresh` 0.3. The owner confirmed it usable with the Settings limitation documented below.

## Runtime verification

- `sys.boot_completed=1`.
- SystemUI PID remained `7008` across the required stability checks.
- `fixo_fullscreen_caption/runtime.log` reports `caption-overlay=ok pid=7008`.
- Mounted SystemUI SHA-256: `92c57e647c9520cb043be1d0a0cf010c6f1e7dec2b72129837b45cc261e57560`.
- Mounted Settings SHA-256: `dd16f3af8b453a9f8ebe19ee9fcf22be80682a8f8aac528c81c379707e63e2c0`.
- `persist.oplus.panorama.branch.enable=true`, `panoramic_forced_disable_state=0`, and the live feature table contains `oplus.software.wms.panorama_work_station`.
- `fixo_attention_asi/runtime.log` reports `set_result=true` for the Google ASI attention component.
- Snapshot: `out/confirmed-selected-modules-2026-09-14/LIVE_DEVICE_STATE.txt`.
- Smart-refresh feature XML SHA-256: `e6f666f5d9fb31f3029d89ba259cdb9197d3df273ffc702c7ff0f3352431d0e7`; `oplus_customize_screen_refresh_rate=0`.

## Do not silently restore

- OPD2514/A.30 AI add-on experiments are not part of this milestone. Do not install or merge them into the confirmed module set without a new isolated test.
- `fixo_freeform_smooth_corner`, panorama v1.4, and third-party `speaker_rotation_fix` remain rejected experiments.
- Do not install several modules that mount the same Settings or SystemUI APK.

## Open or accepted issues

- Dolby UI and parameter writes work, but the audio stream still bypasses the restored DAP primary mix; the old Dolby trials are not confirmed fixes.
- OnePlus AI remains incomplete and is intentionally outside the confirmed milestone.
- “Material contour glow” can be exposed in Settings but has no confirmed Launcher/SystemUI render effect.
- GPS is not recorded as confirmed repaired.
- ZUI remains the hardware-compatible camera; model-specific zoom behavior requires a fresh focused log before further changes.
- Smart mode is not an all-app touch boost. `com.android.settings` is explicitly present in the stock OPlus TouchIdle blacklist, so continuous Settings scrolling remains at `60 Hz`; app-switch animation reaches `120 Hz` and returns to `60 Hz` when idle. The owner accepts this for v0.3. A broader fix would require an isolated `oplus_vrr_config.json` override and video/game/thermal regression testing.

## Immediate continuation rule

Preserve the 12-module 2026-09-14 base plus the accepted launcher-corner v1.0 and smart-refresh v0.3 additions before any new experiment. Install large Settings/global-app payloads first, reboot and let package scanning settle, then install SystemUI v0.5 alone; this avoids its 30-second stability guard observing unrelated first-boot restarts.
