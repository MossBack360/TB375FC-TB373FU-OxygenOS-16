# TB375FC OxygenOS port handoff

Updated: 2026-09-14

The owner clean-flashed the OxygenOS 16 port and confirmed a staged base restore containing exactly 12 active Magisk modules. No AI add-on or third-party power module is installed. The base snapshot is archived at `out/confirmed-selected-modules-2026-09-14/LIVE_DEVICE_STATE.txt`. Later work added launcher-corner v1.1-test, smart-refresh v0.3, and camera-safe v2.0. All 15 current module IDs are active.

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
