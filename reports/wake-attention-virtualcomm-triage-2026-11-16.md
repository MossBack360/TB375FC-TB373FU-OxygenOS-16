# Wake, attention, communication triage — 2026-11-16

## Lift to wake

The owner confirmed that the MTK type-23 wake daemon wakes the tablet, but the hidden AOSP switch on Display resets to off after navigating away. The current `LiftToWakePreferenceController` in Settings `classes5.dex` reads/writes `Settings.Secure.wake_gesture_enabled`. OPlus SettingsProvider returns 0 on `get`, even after `settings put secure wake_gesture_enabled 1`; `settings list secure` shows the stored 1. The working daemon instead reads `Settings.Global.ambient_tilt_to_wake` (currently 1).

`patch/build_wake_switch_settings.py` changes only that controller to use the global key and Global API. A single-class JADX check shows both read and write changed. The early-scan v5.4 candidate was **rejected**: after a later reboot PackageManager stopped registering `com.android.settings`, despite the mounted APK being present. Reinstalling the earlier early-scan v0.1 did not restore registration. Disabling early-scan restored the stock signed Settings package. The known v5.3 postboot bind restored modified Settings reliably. `patch/package_settings_lift_postboot.py` then packaged the same controller change as `fixo_settings_confirmed` v5.4 postboot; it is currently mounted, PackageManager registers Settings, and the Settings activity opens. Physical hidden-switch navigation test awaits the owner. The old early-scan module `fixo_settings_rom_scan_trial` remains disabled. Original v5.3 postboot recovery ZIP is preserved in `out/settings-postboot-recovery-2026-11-16/`.

## Screen attention

Module 13 v0.2 registers Google ASI and `adaptive_sleep=1`. The owner reports no screen extension. Runtime logs repeatedly show `face=0 gaze=0`. ASI opens the front camera and reports 0 face frames out of 11; camera permission is granted. The device has a newer Google ASI update B.31 (`/data/app`) over built-in B.19 (`/my_product`). The B.31 APK was backed up at `out/attention-asi-version-ab-2026-11-16/AndroidSystemIntelligence-B31.apk` before any version A/B. No update has been removed or changed. A controlled face-on-camera check is pending before blaming the update or changing the service.

## Communication sharing

Module 23 v0.9 forced `persist.radio.multisim.config=dsds` and started virtual RIL at boot. Tombstone 25 shows `subsys_daemon` crashing on `getCurrentCalls`: `RadioCommCenter::isValidProviderName` reads `this+0xb8` while `this` is null, after `CommStatusTracker::notifyCallStartOrEnd`. The v0.9 module was disabled. `patch/build_virtualcomm_safe_trial.py` produces v1.0, retaining feature XML/overlay and late virtualcomm properties but not forcing multisim or starting virtual RIL. It is now active; `IVirtualComm` exists, virtual RIL remains stopped, and no repeat native crash appeared. Module 24 official signed Google Dialer and Messages frontends were installed. Both packages exist and Android assigned them the default DIALER and SMS roles. A paired OPlus phone is required to verify actual calling/text transfer; no such end-to-end result is claimed.

The v5 ROM staging script `patch/stage_wake_virtualcomm_rom.py` was changed to **disable** the old unsafe virtual RIL startup and remove its now-unneeded SELinux signal grant. The v5 images remain unbuilt/unflashed. The safe Magisk behavior is not yet a confirmed native ROM service design.
