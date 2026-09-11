# ZUI memory expansion and attention findings

Device build: `Lenovo/TB373FU/TB373FU:16/BP2A.250605.031.A3/10.057.260311W:user/release-keys`

## Memory expansion

After selecting 2 GB in ZUI:

- `persist.sys.zram_wb_enabled=true`
- `persist.sys.zram_wb_list=2_4_7`
- `persist.sys.zram_wb_size=2G`

The exact ZUI `MemoryExpandFragment` writes `enabled=true` and a suffixed size such as `2G`, then reboots. Selecting off writes `enabled=false` and `size=0`.

## Attention

ZUI resolves the framework Attention service to:

`com.google.android.as/com.google.android.apps.miphone.aiai.attention.service.AiAiAttentionService`

A one-shot request returned success code 1. An end-to-end test temporarily set `adaptive_sleep=1` and the screen timeout to 10 seconds. After 25 seconds the display remained awake. PowerManager issued four checks; the first three completed in about 393-407 ms with a detected face and gaze on screen. The original settings were restored.

Minimum reference artifacts are archived under `out/zui-attention-reference-2026-09-12`:

- `AndroidSystemIntelligence.apk`
- `GmsConfigOverlayASI.apk`
- `privapp-permissions-google-product.xml`
- `asi_features.xml`

The overlay sets `android:string/config_defaultAttentionService`. The service is exported with `android.permission.BIND_ATTENTION_SERVICE`, and the app requests both `CAMERA` and `SYSTEM_CAMERA`.

## Lift to wake

ZUI uses `Settings.Secure.wake_gesture_enabled=1`. `PhoneWindowManager` registers the MTK `wake_gesture` sensor (type 23) with `mTriggerRequested=true`. The saved OxygenOS baseline has the same sensor but `wake_gesture_enabled=0` and `mTriggerRequested=false`. The preferred repair is to unblock the standard setting path instead of routing through the less suitable OPlus `tilt` sensor (type 22).
