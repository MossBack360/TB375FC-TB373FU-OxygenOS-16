# Current state — 2026-09-11

## Device and ROM

- Lenovo Xiaoxin Pad Pro 2025, hardware code `TB375FC`, MediaTek MT6897/Dimensity 8300 family.
- Ported OxygenOS 16 identifies itself as `OPD2203`; Android 16/API 36.
- Current fingerprint: `OnePlus/OPD2203/TB375FC:16/BP2A.250605.015/T.R4T3.4f08503-2ad84ab:user/release-keys`.
- Root is available through Magisk. ADB executable: `C:\Program Files (x86)\MiFlashPro\adb.exe`.
- The tablet's wall clock currently reports 2026-01-01 and is unreliable for module installation timestamps; use host-side artifact dates and recorded baselines when reconstructing chronology.
- The reference model `OPD2203` is not this tablet. Never call it the target hardware.
- `persist.sys.oplus.anim_level=1`. The base `TB375FC_ColosOS` module originally forced `3`; its original installed file is backed up as `/data/adb/modules/TB375FC_ColosOS/system.prop.anim-level-3.bak`. A saved OxygenOS baseline from 2026-09-09 reported `2`.

## Confirmed working behavior

- Settings opens normally, including All apps. The OxygenOS Settings icons, OnePlus AI label, About-device blue/red OxygenOS version card, and OxygenOS easter-egg/logo assets are present.
- International account and OnePlus Gallery components are active. The built-in account was later found to already be the international variant; do not install the separate account-only experiment.
- OxygenOS software-update page/activity and required system permissions work.
- Smart-cover close/open sleep and wake works and follows the Settings switch.
- Display adaptive color and color-mode controls reach the MTK PQ engine. Color-mode changes have a long visible delay; the owner accepts this as a device characteristic.
- Fullscreen application three-dot window controls work. The root cause was the `OPD2203` entry in SystemUI's `NOT_SUPPORT_FULLSCREEN_WINDOW_DECOR_PRODUCTS` denylist.
- Bottom-corner fullscreen-to-freeform gesture works. It requires `oplus.software.wms.panorama_work_station` plus the panorama branch property.
- The drag phase has the original v0.2 rounded-corner fallback. Back gesture now uses the follow-finger `RubberBandBezierCalculator` even when the global Oplus animation tier would choose the non-rubber-band path.
- WeChat scanner and ZUI camera startup crashes caused by the Oplus camera startup policy are fixed by disabling `/system_ext/etc/sys_camera_optimize_config.xml` through the confirmed module.
- ZUI Camera legal/privacy links no longer crash because the stock Lenovo privacy package is supplied.
- Four-speaker channels rotate with the display through the confirmed v2.1 bridge.
- Lift-to-wake can work through the Oplus tilt path, but it is reliable only with a phone-like portrait “removed from pocket” motion. This is accepted as a characteristic and its module is not currently active.

## Active modules

The 2026-09-11 live snapshot reports these active modules:

- `TB375FC_ColosOS` V1 — third-party power/ColorOS bug bundle; locally changed to animation tier 1.
- `fixo_camera_optimize_disable` 1.1.
- `fixo_display_pq` 1.0.
- `fixo_freeform_corner_gesture` 1.2.
- `fixo_fullscreen_caption` 0.5 — combined three-dot menu, original drag-corner fallback, and back-gesture fix.
- `fixo_global_apps` 1.0.
- `fixo_ota_system` 1.0.
- `fixo_settings_confirmed` 3.6.
- `fixo_speaker_rotation_prop` 2.1.
- `fixo_zui_lenovo_privacy` 1.2.
- `xiaoxin_hall_cover` 2.0.

Disabled modules that must remain disabled:

- `fixo_freeform_smooth_corner` 0.1 test.
- `speaker_rotation_fix` 1.1 third-party implementation; it caused a second-screen boot hang on this ROM.

## Open or accepted issues

- Dolby UI and parameter writes work, but Dolby/scene/EQ changes produce no audible effect. The audio stream bypasses the restored DAP primary mix. Stop reusing the old Dolby trials until the vendor audio policy/DSP route is understood.
- ZUI remains the only hardware-compatible camera. It can still have device-specific zoom behavior; capture a fresh log before changing camera components.
- OnePlus AI is incomplete. OPD2514 AI add-on experiments and domestic `com.coloros.sceneservice` are disabled; domestic components introduce “Personalized information and services,” which is not appropriate for the international port.
- “Material contour glow” can be exposed in Settings but has no visible Launcher/SystemUI render effect. Existing material-stroke experiments are disabled.
- The v0.4 30↔50 px formal freeform corner interpolation was rejected because the resulting motion looked worse. It is archived for study only. Current v0.5 deliberately keeps stock handoff behavior.
- GPS status was investigated but is not recorded as confirmed repaired. Recheck live behavior and logs before claiming its state.
- Camera is from ZUI; some missing full-screen or AI behavior is a model-feature gap rather than a missing Settings string.

## Immediate continuation rule

Before new experiments, ensure `fixo_fullscreen_caption` is version 0.5, the two failed modules above are disabled, and Settings/SystemUI each have only one active replacement source. Use the latest live evidence rather than assuming the snapshot is still current.
