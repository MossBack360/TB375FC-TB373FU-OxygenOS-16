# v5 stage: 14 lift to wake, 23 communication sharing, 27 Homebar

This is staging in the unpacked v5 ROM tree only. No `super.img` was built or flashed.

## 27 Homebar

`product_a/overlay/FixoNavbarLandscape.apk` was already present. Its SHA-256 `0cbb6dcad8e33a22281b5e9a1e5dd7c243a75d355833759afe860fe552750a8d` matches archived `27-navigation-homebar-landscape-width-v0.1.zip` exactly. No further patch was needed.

## 14 lift to wake

Source archive `14-lift-to-wake-zui-sensor-glue-v0.2.zip` SHA-256 `6509b211c93f36bf3aa785431cb70df68489d66e4550e90bd14f1d022efc0e8c`.

Staged the original `wake-glue.dex` under `/system/etc/fixo/`, adapted the original 3-second switch listener to a ROM path and writable log, and added `fixo-wake-gesture.rc` to start it after boot completed as UID 0 in `u:r:shell:s0`. It still follows `Settings.Global.ambient_tilt_to_wake` and registers MTK sensor type 23 only while enabled. A six-second probe launched the DEX on the current tablet under the same UID/domain; SensorService logged registration and later removal of handle 23. This proves class loading and sensor access, not a physical raise-to-wake event under the unflashed ROM.

## 23 communication sharing

Source archive `23-communication-sharing-backend-v0.9-unified-feature.zip` SHA-256 `7ec62c0fc4018e8b9062077214045f7f3d51c203efa566e60ecb6748dbde3636`.

The source ZIP's Wi-Fi tablet XML and VirtualComm capability overlay were already staged byte-for-byte. The unified OPlus feature XML already contains all five required panorama, three-finger and virtual-modem gates. The two virtualcomm build properties were also already in v5.

Staged `/system/etc/init/fixo-virtualcomm.rc` and `/system/etc/fixo/virtualcomm.sh`. Init now owns the early property writes and service start/stop/restart actions. The shell service retains the source module's order: wait for ISubsys binder, restart the cached `com.oplus.subsys` process, then request virtual RIL stop/start through a `debug.fixo.virtualcomm.stage` property acknowledged by init. On the current device, UID 0 in `u:r:shell:s0` cannot directly set `ctl.start` or vendor radio properties, while it can set `debug.fixo.*`; this motivated the split. Init also restores the two vendor virtualcomm properties if OxygenOS writes them back to 0 after boot. The source's first-minute polling loop was replaced by those property-change actions.

The original module's targeted cached-process restart requires `shell` to send SIGKILL to `system_app`; the v5 `system_ext_sepolicy.cil` adds `(allow shell system_app (process (sigkill)))`. A root shell-domain `kill -0` probe was denied before this policy. This permission is broader than the single package because several system apps share the SELinux domain; native ROM policy and actual restart behavior require first-boot review.

## Checks

`patch/stage_wake_virtualcomm_rom.py` checks both archived ZIP hashes, exact static 23 payloads and all five feature gates, stages fs_config/file-context entries, and is idempotent. Both shell scripts passed `sh -n` on Android. The file-context patterns were also checked to contain one regex escape before each dot. WSL `secilc -N` produced a policy binary using the v5 partition CIL files, validating new rule syntax and symbols. Full neverallow compilation did not pass because the mixed baseline platform/vendor CILs produce many pre-existing neverallow conflicts; this is not a native boot validation. Do not retire any known-good Magisk 14/23 installation based only on this staging. On a first v5 ROM boot, inspect init service states, the wake sensor callback, virtual RIL states, `IVirtualComm`, and SELinux denials.

The tablet uptime was about 13 minutes at the start of this work and about 21 minutes at the last check. ZRAM's first automatic writeback attempt is around one hour after boot, not at the 30-minute idle mark.
