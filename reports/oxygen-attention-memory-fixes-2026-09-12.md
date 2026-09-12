# OxygenOS attention and memory fixes — 2026-09-12

## Device and stable state

- Hardware: Lenovo TB375FC, OxygenOS product identity OPD2203.
- Fingerprint: `OnePlus/OPD2203/TB375FC:16/BP2A.250605.015/T.R4T3.4f08503-2ad84ab:user/release-keys`.
- Final Settings module: `fixo_settings_confirmed` 3.9 (versionCode 12).
- Final mounted Settings SHA-256: `DD16F3AF8B453A9F8EBE19EE9FCF22BE80682A8F8AAC528C81C379707E63E2C0`.
- PackageManager boot-scan APK retained unchanged at SHA-256 `7520229A7F190D35D86A4B1945B03966A49DF61AA90799F57904011FDBA71C12`.

## Memory expansion

Two independent omissions caused the page to appear unusable.

1. `persist.sys.oplus.nandswap.storage.min` was empty. `RamExpandUtils.isDataDirectoryEnough()` treats an empty value as false, so the switch and seek bar were disabled even though `/data` had about 221 GB free. The device's own `nandswap_tool` exposed the default tuple `0 4 19 4 8 12`; running it set the missing minimum to 19. The final module makes `persist.sys.oplus.nandswap.storage.min=19` persistent through `system.prop`.
2. OxygenOS `RamExpandSizePreference.onProgressChanged()` wrote only the level index. The previously extracted TB375FC ColorOS reference differs in exactly this method and additionally writes the chosen capacity to `persist.sys.oplus.nandswap.swapsize.curr`, `sys.oplus.nandswap.request`, and `persist.sys.oplus.nandswap.swapsize`. The final patch copies that ColorOS class exactly; `RamExpandFragment`, `RamExpandUtils`, and `RamExpandSwitchPreferenceController` are byte-identical between the two sources.

End-to-end UI test after reboot:

- Page action: `oplus.intent.action.settings.RAM_EXPANSION_SETTINGS`.
- Switch and seek bar: both `enabled=true`; 4/6/8 GB choices displayed.
- Selecting 6 GB produced `lvl=1`, `swapsize=6`, `swapsize.curr=6`, and `request=6`.
- Selecting 4 GB again produced `lvl=0`, `swapsize=4`, `swapsize.curr=4`, and `request=4`.
- Final user-facing capacity was restored to 4 GB.

Build and module:

- Script: `patch/build_memory_expand_coloros_activity.py`.
- Archive: `out/memory-expand-coloros-activity-v39-2026-09-12`.
- Module SHA-256: `DF527EB814BB107EE57AABA57EB74BF61C52CA15C82DC00DFBE53B826EDE30AC`.

### Packaging regression and recovery

An earlier 3.8 package incorrectly replaced both Settings layers with the modified APK. PackageManager then reported `System package com.android.settings no longer exists`. The confirmed 3.6 module was immediately restored and Settings returned after reboot. The final 3.9 package retains the original signed APK in `system/system_ext/priv-app/Settings/Settings.apk` and changes only `payload/Settings.apk`, which the existing service bind-mounts after PackageManager has scanned the original.

The unsafe archive was renamed with `.DO_NOT_INSTALL` and accompanied by a warning file.

## Screen attention

OxygenOS already ships a newer full `com.google.android.as` package at
`/my_product/priv-app/AndroidSystemIntelligence_Features/AndroidSystemIntelligence_Features.apk`.
It contains `com.google.android.apps.miphone.aiai.attention.service.AiAiAttentionService`, so the ZUI APK was not transplanted.

The active `fixo_attention_asi` 0.1 module grants the existing package camera permission and selects it using `cmd attention setTestableAttentionService com.google.android.as` after boot. Its runtime component is:

`com.google.android.as/com.google.android.apps.miphone.aiai.attention.service.AiAiAttentionService`

The enhanced `patch/test_zui_attention.ps1` test preserves and restores adaptive-sleep, screen-timeout, and stay-awake settings. With a real 10-second timeout, the screen remained awake through 25 seconds; AttentionDetector generated repeated checks and ASI returned successful face/gaze results. This remains a trial override rather than a static framework overlay.

## Raise-to-wake investigation

- OxygenOS UI currently enables `ambient_tilt_to_wake=1`, using MTK sensor type 22 (`tilt`).
- ZUI uses `wake_gesture_enabled=1`, using MTK sensor type 23 (`wake_gesture`, one-shot wake-up), which explains the observed higher sensitivity.
- OxygenOS SettingsProvider contains a deliberate special case in `getSecureSetting`: when the requested key is `wake_gesture_enabled`, it changes the returned value to `0`. Consequently both shell and root writes read back as 0 and PhoneWindowManager never requests the type-23 trigger.
- A minimal services.jar trial redirected PhoneWindowManager's read and observer to an unblocked same-length key. The DEX rebuilt and re-decoded correctly, but the first boot did not reach `sys.boot_completed` inside the three-minute safety window. The watchdog disabled the module and rebooted successfully. The module remains disabled on-device and its archive is marked `DO_NOT_INSTALL`.

No wake-gesture framework change is part of the confirmed release.

### Post-boot wake-gesture glue

A boot-safe alternative was verified without replacing framework files. A small root
`app_process` daemon directly registers MTK `TYPE_WAKE_GESTURE` (23), calls
`PowerManager.wakeUp` on a one-shot trigger, and re-arms the sensor. A direct test moved
the device from `mWakefulness=Asleep` to `Awake`; SensorService reported a successful
type-23 registration with sensor access.

The first 0.1 supervisor stored the launcher PID, but `app_process` changed PID during
startup. This made the watchdog falsely assume the daemon had exited and create 13
instances, temporarily increasing RAM use. All duplicate processes were killed and the
module was disabled immediately. Version 0.2 identifies the final process by the unique
`fixo_wake_glue` process name. Tests held at exactly one instance, changed to zero when
`ambient_tilt_to_wake=0`, and returned to one when the setting was restored to 1.

After cleanup, Android reported about 7.7 GB free RAM, 4.45 GB used RAM, and about
181 MB of physical ZRAM use. The abnormal memory rise was caused by the 0.1 process
supervisor, not by OPlus memory expansion.

- Module: `fixo_wake_gesture_glue` 0.2.
- Archive: `out/wake-gesture-glue-v02-2026-09-12/fixo-wake-gesture-glue-v0.2-magisk.zip`.
- Archive SHA-256: `0ACCEFA7B0D9022D790F8C73A2F1CD38653BD1EF87112F9FBCC3024E0FABDC16`.
