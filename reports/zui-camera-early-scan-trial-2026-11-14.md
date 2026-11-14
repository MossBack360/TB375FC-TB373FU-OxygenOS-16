# ZuiCamera v2.0 early PackageManager scan A/B — 2026-11-14

Goal: test the same camera DEX patch as a system APK visible at package-scan time, without the old post-boot bind that bypassed the scan. Target: Lenovo TB375FC, OxygenOS port, boot slot `_a`, Magisk 30.7.

## Baseline

- Boot complete; `/system/priv-app/ZuiCamera/ZuiCamera.apk` SHA-256 `6752402e1d1f2308941d50aaf056f9a69246337884f7cc1b9a7905b9f5f2c9ba`.
- `pm path com.zui.camera` returned the original system path. The old `fixo_zui_camera_sr_disable` v2.0 module was absent.

## Test A: raw v2.0 APK

`patch/package_zui_camera_early_scan_trial.py` wrapped the exact v2.0 patched APK (SHA-256 `42e55eb755521791ac757e6c8ca1d0b1c6b6fcdf02e7a29004a126fcface1676`) in a static Magisk mount module, ID `fixo_zui_camera_early_scan_trial`. It contains `system/priv-app/ZuiCamera/ZuiCamera.apk` and `system.prop`; no `service.sh` or post-boot bind. ZIP SHA-256 `7c006333200360cbb26402192949572ef7a2f397f05a8e18c60be4e22ec0c18d`.

After reboot, boot completed and the mounted path had the patched APK hash, but `pm path com.zui.camera` returned nothing. The raw APK was therefore **not registered by PackageManager** on this ROM. The test module was disabled and rebooted; the original APK hash and package registration both returned. Keep this test module disabled.

## Test B: same APK with original ROM signing block

The already prepared `ZuiCamera-v2-rom-signing-block-candidate.apk` (SHA-256 `7a21a0c3f28b1eb715dbbb9bd4a1be5e3722eef4f998de100c68bd58a4beb862`) has identical patched APK entries and the original 4096-byte v3 signing block. Its independent `apksigner verify` still reports a content digest mismatch; it is **not** a generally valid signed APK. Wrapped as another static mount module, ID `fixo_zui_camera_sigblock_scan_trial`, ZIP SHA-256 `a48fc199384ef4cf3bdc37f4558c22761a27303fe2c2d20bb8a6df35e10efc42`.

After reboot, boot completed, mounted file hash matched, and `pm path com.zui.camera` returned `/system/priv-app/ZuiCamera/ZuiCamera.apk`. `dumpsys package` showed the system package, installed for user 0, version `18.0.1.260104202516`. `debug.camera.morpho.sr.on=0`. `am start -n com.zui.camera/.CameraLauncher` succeeded and PID `7935` remained alive after eight seconds, without a sampled crash. The foreground first showed the Android camera permission dialog; after it was dismissed, `CameraActivity` was foreground and `dumpsys media.camera` showed an active `com.zui.camera` client (camera ID 1, PID 7935). This proves camera HAL access, while visual preview and capture still await the owner's confirmation.

The owner confirmed that preview and capture both work normally. The candidate is currently enabled; the raw trial remains installed but disabled. This A/B shows the original signing block is necessary for PackageManager registration in the current early-scan path, but does not establish general APK signature validity on other ROMs.

`patch/stage_zui_camera_rom.py` then copied this exact candidate into both v3 and v4-cts extracted `system_a/system/priv-app/ZuiCamera/ZuiCamera.apk` trees and added exactly one `debug.camera.morpho.sr.on=0` line to each `system/build.prop`. Both tree APK hashes match the tested candidate. The shared original backup is `out/zui-camera-rom-scan-2026-11-13/ZuiCamera-original-before-solidification.apk` (SHA-256 `6752402e1d1f2308941d50aaf056f9a69246337884f7cc1b9a7905b9f5f2c9ba`). Existing EROFS images are stale; no image or super was rebuilt or flashed.
