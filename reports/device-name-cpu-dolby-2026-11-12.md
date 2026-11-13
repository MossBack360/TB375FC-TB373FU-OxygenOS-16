# Device name, CPU name and Dolby policy check (2026-11-12)

## Current device name

- Current `global device_name` and `global revise_device_name` were both `OnePlus Pad`. `OplusDeviceInfoUtils.getOplusDeviceName()` checks `revise_device_name` first, then `device_name`, then the market-name/model default. Therefore baking `19-device-model-market-name-v0.2.zip` into build properties alone does **not** replace an existing database value.
- Both values were changed once, only after checking that each still equaled `OnePlus Pad`, to `Lenovo Xiaoxin Pad Pro 12.7 (2025)`. No boot script or APK hook was installed; Settings can still save a user-edited name.
- A clean data wipe should let the corrected market name become the default. A dirty flash preserves the two database values. Do not unconditionally set them at every boot.

## CPU name without changing Settings.apk

- The active `tb375fc-cpu-name-fix-v0.3.apk` LSPosed module intercepts `OplusDeviceInfoUtils.getCpuInfo(Context)` in `com.android.settings` and returns a fixed localized string.
- The unmodified method instead reads `ro.product.cpuinfo`, looks up its key in `/my_stock/etc/extension/config_processor_com.android.settings.xml`, then falls back to MTK/CPU-core detection. Current `ro.product.cpuinfo` and `ro.product.oplus.cpuinfo` are empty; `/proc/cpuinfo` only reports processor indices. That explains the eight-core fallback.
- The existing XML maps plain `MT6897` to **Dimensity 8350**, so setting `ro.product.cpuinfo=MT6897` would be wrong for this tablet.
- `patch/build_cpu_name_native_config.py` adds only a unique `MT6897-TB375FC` mapping to the stock XML, with Chinese/English names for Dimensity 8300. Generated XML: `out/cpu-name-native-v0.1-2026-11-12/config_processor_com.android.settings.xml` (SHA-256 `52337617affadbf873d42e3617ef5d248c62671ed7597b163a96a402d44125db`). The companion early property is `ro.product.cpuinfo=MT6897-TB375FC`.
- XML parses successfully. This native path is staged only; it has not been mounted, flashed, or visually tested. Keep the LSPosed module until that test succeeds.

## Dolby SELinux proposal

- The previously tested Dolby bridge source is `patch/dolby-dap-overlay/`; its v1.2–v1.5 ZIPs are in `out/dolby-dap-confirmed-2026-09-09/`. They registered DAP/started ZUI DaxService. The archived v1.5 test saw an enabled DAP effect on an actual music session and DMS profile data, but still heard no change from profiles or equalizer settings. This narrows the old failure to processing/routing below the UI and DMS parameter writes.
- The proposed commit's three statements were dry-run against the current live policy with `magiskpolicy --load /sys/fs/selinux/policy --apply ...`, without `--live` or `--save`. It reported `type platform_app_36 does not exist` for the first two and `source type platform_app_36 does not exist` for the third. Substituting `platform_app` reported `target type dms_aidl_service does not exist`.
- This ROM runs `vendor.dolby.hardware.dms@2.0-service` in `hal_dms_default` (HIDL). The current `platform_app` type already has `hal_dms_client` and `hal_dvs_client`; no matching Dolby/DMS/DVS AVC appeared in the sampled log buffer. Thus those AIDL/Android-36 policy lines do not address the currently observed profile-effect failure. No Dolby module or live policy was changed.

## ROM build state

The separate `v4-cts` tree has rebuilt `product_a` and `system_ext_a` EROFS images for the independently verified Circle-to-Search change. Neither a v4 super image nor flash-script edit has been made. CPU XML/property integration remains staged for the next ROM build pass.

## Follow-up Dolby SELinux audit

- The current vendor DMS HIDL binary (`vendor.dolby.hardware.dms@2.0-service`), `libdmshal.so`, and `dax-default.xml` are byte-identical to the saved Lenovo ZUI files. Current `/vendor/lib64/soundfx/libswdap.so` is **not** byte-identical to the saved Lenovo file (the old v1.5 archive already recorded a four-instruction difference). Thus the Dolby lower stack is mostly Lenovo, but not an untouched complete vendor copy.
- Live domains: Settings and `com.oplus.audio.effectcenter` are `system_app`; the Dolby DMS daemon is `hal_dms_default`; `audioserver` is `audioserver`. The current `audioserver` type already has `hal_dms_client`. The `platform_app` type already has both `hal_dms_client` and `hal_dvs_client`; the proposed `platform_app_36` type is absent. `system_app` has `hal_dvs_client`, but no `hal_dms_client` in its attribute list.
- Settings calls `IOplusEffectService` in AudioEffectCenter. That service constructs `DolbyAudioEffect extends AudioEffect` for UUID `9d4921da-8225-4f29-aefa-39537a04bcaa`, so normal profile control proceeds through AudioFlinger/audioserver rather than Settings directly finding DMS. A missing `system_app` DMS attribute alone does not establish a fault in this path.
- The old `patch/dolby-dap-overlay/sepolicy.rule` already granted `priv_app` HIDL DMS lookup, binder calls and fd use for its ZUI DaxService. Earlier work did consider SELinux, but did not prove every possible denial absent. The current device has no Dolby bridge/DaxService module installed, and the sampled current logs contain no Dolby/DMS/DVS AVC. No live Dolby profile test was performed in this audit.
- Most useful future discriminating test: with the archived v1.5 bridge enabled and a real music stream playing, collect AVC plus `AudioEffect`/DMS logs while switching profiles. Compare enforced and a short controlled permissive run only if a denial or silent drop remains plausible. Do not add broad SELinux rules without a matching source domain and target type.

## 2026-11-13 v1.5 reinstall and rollback

- Installed archived `fixo-dolby-dap-v1.5-zui-engine-magisk.zip` (SHA-256 `d96fbece5f78f633b9d8765f7794e4536a451a4aa3b30a72bdb69b4894f97872`) and rebooted. DaxService ran in `priv_app`, the ZUI `libswdap.so` was mounted, and AudioFlinger registered the DAP UUID. No Dolby/DMS/DVS AVC appeared in the sampled postboot logs.
- Installed Fossify Music Player 14 and copied one existing iTunes MP3 to `/sdcard/Music/DolbyTest.mp3`; playback reached `PLAYING(3)` and a DAP effect chain appeared on the music session.
- Before a mode-switch comparison could be made, Settings was absent from PackageManager (`pm path com.android.settings` returned nothing; Settings intent had no activity). The currently mounted Settings APK still had its expected SHA-256. Exact reason for the scan failure was not captured; do not call it a proven signature error.
- Disabled only `fixo_dolby_dap` and rebooted. `pm path com.android.settings` then returned the expected APK, the Settings intent resolved to `OplusSettingsHomepageActivity`, and Settings PID 2890 started. Keep v1.5 disabled; no audible-effect conclusion was reached in this run. Owner requested skipping Dolby if it remains unworkable.
