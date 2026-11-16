# Magisk trial of 13/14/23 — 2026-11-16

The installed-module list, disable markers, runtime state and exact ZIP hashes were saved in `out/install-13-14-23-2026-11-16/` before the change. The v5 ROM image was not flashed.

- Installed archived 13 `fixo_attention_asi` v0.2-trial, 14 `fixo_wake_gesture_glue` v0.2, and 23 `fixo_virtualcomm_backend` v0.9-unified-feature, then rebooted.
- Boot completed with Settings and SystemUI running. 13 registered `com.google.android.as/...AiAiAttentionService`, initialized `adaptive_sleep=1`, and logged attention checks. 14 saw `ambient_tilt_to_wake=1` and its `fixo_wake_glue` process was running. Physical gaze and lift behavior await owner testing.
- 23 bound its merged feature table and found `IVirtualComm`, but `virtual-ril-daemon-0` repeatedly restarted. Logcat showed a native crash in `/vendor/odm/lib64/lib-virtual-modem-api.so`, at `RadioCommCenter::isValidProviderName`, after provider `universal:virtualcomm:ril0` was requested. Its post-boot log also reported `com.android.incallui=missing`. This is not a successful communication-sharing test.
- Touched only `/data/adb/modules/fixo_virtualcomm_backend/disable` and rebooted. The second boot completed with Settings/SystemUI running; 13/14 remain enabled, ASI and the wake daemon active, and 23 disabled. No new virtual-RIL crash was seen in the post-recovery crash buffer.

The original 23 ZIP is preserved. Diagnose the virtual-RIL provider contract before another 23 trial; do not treat the v5 native implementation as validated by this failed Magisk boot. Reboots reset the 18 ZRAM automatic-writeback timer.
