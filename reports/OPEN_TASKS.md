# Open tasks — 2026-11-16

1. **SystemUI freeform fallback corners.** In Settings and other apps without freeform support, multi-finger scaling falls back and shows an abnormal corner transition. Capture the fallback transaction and fix that path. The ordinary corner gesture and Chrome PiP fixes are separate and already confirmed.
2. **RAM expansion automatic writeback.** The 8 GiB backing and manual one-shot writeback work. Confirm the unchanged background timer reaches its first writeback around one hour after boot completion. Inspect `runtime.log` as well as `bd_stat`; a zero-page cycle can execute successfully without increasing the counter. If a controlled cold-page sample is needed on a later boot, run `scripts/zram-cold-page-probe.sh` as root before the 30-minute idle-mark point. It writes bounded, temporary, nonzero data to tmpfs and removes it on normal exit or interruption. It does not guarantee swapping: Android may reclaim file cache or kill processes first. Do not use wall-clock changes to test the timer, because the script uses sleep/uptime rather than the date.

Module 13 is staged for v5, but the current Magisk test has exposed an attention-detection problem below.

## Newly reported on 2026-11-16

- Lift-to-wake hidden AOSP switch: v5.4 postboot Settings patch is installed; confirm it remains on/off after leaving the page and that both states control the type-23 daemon. The early-scan candidate failed PackageManager and is disabled.
- Screen attention: ASI returns zero detected face/gaze frames despite opening the front camera. Check with the owner facing the camera, then compare built-in B.19 with the updated B.31 if needed.
- Communication sharing: v1.0 safe feature/backend module and v0.2 Dialer/Messages frontends are installed; no native crash after removing forced multisim/RIL start. End-to-end phone sharing is unverified; the old v0.9 forced-RIL startup is rejected.
