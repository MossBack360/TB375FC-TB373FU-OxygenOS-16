---
name: tb375fc-oxygenos-port
description: Continue and maintain the Lenovo TB375FC/TB373FU OxygenOS 16 port in the fixO repository, including ADB diagnosis, APK comparison, Magisk module construction, regression recovery, patch records, and milestone Git checkpoints. Use when working on this specific ROM port or resuming its repair history.
---

# TB375FC OxygenOS Port

Work from `C:\Users\GY\Documents\GitHub\fixO`. At the start of a new window, read [references/current-state.md](references/current-state.md) and [references/patch-catalog.md](references/patch-catalog.md). Read [references/file-map.md](references/file-map.md) when locating ROM sources or build artifacts, and [references/device-operations.md](references/device-operations.md) before installing, rebooting, or recovering modules.

Treat evidence in this order:

1. Current device behavior, logs, mounted-file hashes, and user test results.
2. Items explicitly marked confirmed in the state and patch catalog.
3. Decompiled stock ZUI, ColorOS, and OxygenOS implementations.
4. Working hypotheses and community reports.

Preserve every confirmed build. Put each experiment in a new dated `out/` directory and never overwrite a confirmed archive. When multiple modules replace the same APK, produce one combined successor or use the established module ID as an upgrade; do not leave competing Settings or SystemUI bind mounts active. For small APK code changes, prefer a bounded raw DEX patch with an exact source SHA-256 and changed-entry assertion. A full apktool rebuild is acceptable only when resource editing requires it and the rebuilt APK has been validated.

Before a device-changing test, record the active module list and relevant hashes. After reboot, verify `sys.boot_completed`, module status/runtime log, stable process PID, mounted payload SHA-256, and the specific behavior. Keep recovery possible by retaining the preceding ZIP and knowing the module ID to disable.

After the user confirms or rejects a result:

- Update `references/current-state.md`, `references/patch-catalog.md`, and `reports/CURRENT_HANDOFF.md`.
- Mark abandoned experiments as disabled and explain the observed failure; do not silently reuse them.
- Keep proprietary ROM dumps, APKs, images, generated ZIPs, keys, screenshots, and temporary extraction trees out of Git.
- Commit only the coherent source scripts, module metadata, checksums, and reports for that milestone. Review the exact staged diff instead of using an indiscriminate add.
- The owner requested periodic pushes to `origin/main`. Push after a confirmed repair, before changing windows, at the end of a substantial session, or after two to three material recorded changes. If credentials or network access are unavailable, leave a clean local commit and report that the push remains pending.

When the user says they are opening a new window, refresh the device snapshot with `scripts/capture_device_state.ps1`, update the handoff, checkpoint the repository, and tell them to invoke `$tb375fc-oxygenos-port` in the new window.
