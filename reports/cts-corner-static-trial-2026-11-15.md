# Circle to Search + bottom corner static-only trial (2026-11-15)

The tablet reconnected as `HA2FNXNQ` after the user booted it. Initial state: `fixo_circle_to_search` v0.3, `fixo_fullscreen_caption` v0.8, `fixo_freeform_corner_gesture` v1.3 and `fixo_launcher_corner_radius` v1.1 were installed but each had a `disable` marker. Live SystemUI was stock SHA-256 `72cfa6810c72d7aef8cfdfd8f88117c2b5867f272d3700a08fe3c32dc7`; `ro.oplus.display.rc.size=65,65,65,65`. Snapshot: `out/cts-restore-2026-11-15/before-modules.txt` and `before-runtime.txt`.

Installed, under their existing module IDs:

- `out/cts-native-v0.1-2026-11-12/fixo-circle-to-search-framework-v0.3-test.zip` (`fixo_circle_to_search`).
- `out/freeform-corner-static-v1.4-2026-11-15/fixo-freeform-corner-feature-v1.4-static-only.zip` (`fixo_freeform_corner_gesture`). Builder: `patch/build_freeform_corner_static.py`. This keeps v1.3's post-fs-data feature-file bind, uses the AI v2.9 unified feature table that is a superset of the old corner table, and omits `service.sh` and the obsolete three-mode poller. ZIP SHA-256 `257f7246f6b19bcdbbd194a31469ddf4f1ddefdb4c22943196570a4b2e1e6349`.
- `temp3/稳定安装/01-当前启用-Magisk/16-transition-corner-radius-config-v1.1-test.zip` (`fixo_launcher_corner_radius`).
- `out/cts-native-v0.1-2026-11-12/fixo-systemui-cts-rom-scan-v0.8-test.zip` (`fixo_fullscreen_caption`). It contains SystemUI APK SHA-256 `a4aa5664013ada9a87089a142b7d6f4a2328d62b2c5ddd22f16213dea7d339b1`, same bytes as the v5 extracted ROM tree. v0.8 inherits the confirmed v0.6 SystemUI fixes and adds native CTS dispatch.

No disable marker remained for those four modules before reboot. After reboot, `sys.boot_completed=1`, SystemUI PID `2212` remained stable across two reads, mounted APK SHA-256 matched v0.8, `ro.oplus.display.rc.size=26,26,26,26`, `persist.oplus.panorama.branch.enable=true`, secure `fixo_corner_mode=1` and `panoramic_forced_disable_state=0`. Mounted feature XML SHA-256 `001aa89e70911f6467dab4e2316af595e878725ce601719b33fb90f1144765ac`; CTS feature XML SHA-256 `8c0853b74ba7dfa15f7d74767e6ca2a780a8b0ca41b889999da7e8d36efa85a2`; CTS framework overlay APK SHA-256 `3799a1bf9451e846256abc64329662df1181b96c73095fb374c4767a789eafa6`. `cmd overlay list` showed `[x] com.fixo.cts.framework.overlay`, and binder service `contextual_search` exists.

Owner UI check is pending for top three-dot menu, bottom-corner drag and Home-bar long press. Do not promote v1.4 to stable archive until this check passes. The modified v1.3 ZIP and all prior ZIPs are preserved for rollback. The current build.prop model is OPD2203, but the v0.8 modified SystemUI includes the earlier three-dot fix; if that UI test fails, inspect this branch before changing the global product name.

Device-name module `19-device-model-market-name-v0.2.zip` remains in the stable archive. CPU-name LSPosed APK `tb375fc-cpu-name-fix-v0.3.apk` and the native XML at `out/cpu-name-native-v0.1-2026-11-12/` are preserved. The native CPU route has not been installed or baked into v5. Current editable global `device_name` and `revise_device_name` are both `Lenovo Xiaoxin Pad Pro 12.7 (2025)`; current `ro.product.model` remains OPD2203.

## Confirmed after owner test

Owner confirmed that the top three-dot menu, bottom-corner drag, and Homebar Circle to Search all work. The initial Homebar report was a missed touch target.

After the owner reported stock Settings and CPU labels, installed device-name module `19-device-model-market-name-v0.2.zip` and native CPU trial `out/cpu-name-native-v0.1-2026-11-12/fixo-cpu-name-native-v0.1-test.zip`. Re-enabled existing `fixo_settings_rom_scan_trial` and `fixo_settings_companion` and rebooted. Verification: `sys.boot_completed=1`; live Settings PID `2866`; mounted Settings APK SHA-256 `4d763c6c3a3fa15e7561d48434fce8b7373470ac5e0eec6adbbcc4cb11c1b098`; mounted CPU mapping XML SHA-256 `52337617affadbf873d42e3617ef5d248c62671ed7597b163a96a402d44125db`; `ro.product.cpuinfo=MT6897-TB375FC`; `ro.product.model=Lenovo Xiaoxin Pad Pro 12.7 (2025)`. Editable global `device_name` and `revise_device_name` have the same name. CPU trial source: `patch/build_cpu_name_native_module.py`. Settings/CPU visual check remains pending. Native CPU mapping is not yet baked into v5.
