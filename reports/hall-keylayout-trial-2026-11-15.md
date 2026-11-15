# Hall static keylayout trial (2026-11-15)

The prior `xiaoxin_hall_cover` v2.0 Magisk daemon is absent from the current tablet. Hardware evidence: `/sys/bus/platform/drivers/hall/hall_status=1`, `/dev/input/event4` is named `hall`, and it exposes Linux key codes 252 and 253. `Settings.Global.device_case_enabled=1`. Before this experiment, `dumpsys input` showed that the device used `/system/usr/keylayout/Generic.kl`, which has no entries for 252/253.

Created `patch/build_hall_keylayout_trial.py` and installed `out/hall-keylayout-trial-2026-11-15/fixo-hall-keylayout-v0.1-test.zip` (SHA-256 `0e892c6fa307013ec0f3a759fee3675d1392da60dc660c6a52de8c9c287eb8f7`). It adds only `/system/usr/keylayout/hall.kl`: `key 252 SLEEP`, `key 253 WAKEUP WAKE`. After reboot, the device completed boot and `dumpsys input` showed `KeyLayoutFile: /system/usr/keylayout/hall.kl`. No daemon or SELinux policy was added.

ADB synthetic `sendevent` to event4 was denied write access by SELinux, so it did not test the behavior. The owner disconnected the cable to test with the physical magnetic cover/keyboard. Await two results: close/open sleep-wake, then whether Settings' smart-cover switch still disables that behavior. If the switch is bypassed or wake fails, disable `fixo_hall_keylayout_trial` and reboot. Do not stage this keylayout in the ROM before the owner result.

Owner result: close/open worked, but the Settings switch was bypassed. Disabled `fixo_hall_keylayout_trial` and rebooted; device returned to Generic.kl for `hall`. Superseded by the event-only hall v2.1 service described in `reports/hall-rom-stage-2026-11-15.md`.
