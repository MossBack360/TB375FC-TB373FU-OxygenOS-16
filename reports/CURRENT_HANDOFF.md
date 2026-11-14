# TB375FC OxygenOS port handoff

## 2026-11-14 ZuiCamera early package scan A/B

Raw v2.0 camera APK installed as a static early-mount module (`fixo_zui_camera_early_scan_trial`) was visible at the system path after reboot but omitted from PackageManager. It was disabled; the original camera hash and package registration returned after reboot. A second early-mount module (`fixo_zui_camera_sigblock_scan_trial`) uses the same modified APK entries with the original ROM v3 signing block. This time PackageManager registered `com.zui.camera`; `CameraLauncher` started and PID remained stable, but the app is waiting at the Android camera permission dialog, so preview/capture remain unverified. The signed-block candidate is currently enabled, raw trial disabled. Full evidence and rollback IDs: `reports/zui-camera-early-scan-trial-2026-11-14.md`.

## 2026-11-13 ROM glue source staged; USB v3 tree simplified

`patch/prepare_rom_glue.py` stages 11 adapted shell scripts, their small runtime assets and four brightness tables under `out/rom-glue-stage-2026-11-13/`. WSL `sh -n` passed for all scripts. Its init RC keeps all nine services disabled pending SELinux/boot-order checks; early auto-brightness and dynamic ZRAM fstab setup are not auto-started. See `reports/rom-glue-stage-2026-11-13.md`. The v3 working tree `init.usb.configfs.rc` now contains only the one-action `rndis,adb -> start adbd` fix on the original v2 baseline (SHA-256 `49835fc24c37f536ac3ce9428bb69cc94458adac7edcdf078f3e1c7671c10ebe`); previous v3 RC is backed up in `out/rom-solidification-prep-2026-11-13/`. No image was rebuilt, no device operation was performed. Camera v2.0 ROM replacement still awaits the owner's functional/early-scan test.

## 2026-11-13 ROM solidification preflight (no image build)

The owner requested preparation only while the offline-charger issue remains open. `reports/rom-solidification-preflight-2026-11-13.md` and its copy in `temp3/稳定安装/` classify the archived modules, newer Settings/SystemUI/CTS candidates, dynamic services, and deduplication. The Gallery-only v1.1 module is staged but not installed. Camera v2.0 was post-boot bound; its `classes.dex` is the sole changed APK entry. An offline camera candidate with the original ROM v3 signing block is at `out/zui-camera-rom-scan-2026-11-13/`, not installed or included in any ROM. Original ROM camera signer is `Codex Debug`; the candidate requires an early package-scan test. Signed Gallery, AI, OTA, Lenovo privacy, Google Dialer, and Messages APKs were independently verified. SystemUI CTS v0.8 inherits the confirmed v0.6 26px source and changes only `classes6.dex`. USB RNDIS is staged as a minimal one-action RC file under `out/rom-solidification-prep-2026-11-13/`; do not copy v3's two extra gadget actions. No partition image, super, or flash script was built or changed.

## 2026-11-13 Dolby v1.5 rollback

Archived Dolby bridge v1.5 was installed and booted; DaxService and DAP effect registered, with no sampled Dolby AVC. Settings then disappeared from PackageManager before profile testing. Disabling only `fixo_dolby_dap` and rebooting restored Settings registration and launch. Module remains installed **disabled**. Fossify Music Player 14 and `/sdcard/Music/DolbyTest.mp3` were added for the test. Do not re-enable the Dolby module as a stable fix. Details: `reports/device-name-cpu-dolby-2026-11-12.md`.

Final rollback: the owner requested the pretest state. `fixo_dolby_dap` was removed through Magisk's `remove` marker and a reboot; the temporary Fossify APK and `/sdcard/Music/DolbyTest.mp3` were also removed. Boot completed, Settings registered and launched (PID 2939), audioserver ran, and the original seven modules remained. The prior paragraph records the intermediate disabled state, not the current state.

## 2026-11-12 device name, CPU and Dolby (latest)

Current `global device_name` and `revise_device_name` were both `OnePlus Pad`; each was conditionally changed once to `Lenovo Xiaoxin Pad Pro 12.7 (2025)`. User editing remains possible. Settings CPU-name LSPosed v0.3 only overrides `getCpuInfo(Context)`; the native route is an early `ro.product.cpuinfo=MT6897-TB375FC` property plus one mapping in `/my_stock/etc/extension/config_processor_com.android.settings.xml`. A generated, XML-validated mapping is staged in `out/cpu-name-native-v0.1-2026-11-12/`; it has **not** been installed or baked. Do not remove the LSPosed module yet. The suggested Dolby `platform_app_36`/`dms_aidl_service` policy cannot apply to this ROM: both types are absent, while the current Dolby DMS is HIDL and `platform_app` already carries DMS/DVS client attributes. No Dolby module was changed. Details: `reports/device-name-cpu-dolby-2026-11-12.md`.

Follow-up audit: current DMS daemon, `libdmshal.so`, and tuning XML match Lenovo ZUI by SHA-256; `libswdap.so` differs. Settings and AudioEffectCenter run as `system_app`, while `audioserver` already has `hal_dms_client`. Settings drives AudioEffectCenter's `DolbyAudioEffect` through AudioFlinger; the old Dolby bridge already had targeted `priv_app` HIDL DMS SELinux rules. SELinux is not fully ruled out until an active profile-switch log is captured with the old bridge, but the proposed three-line policy does not fit this ROM.

## 2026-11-12 Circle to Search without Eta

Eta is disabled. `fixo_fullscreen_caption` v0.8 early-scan SystemUI candidate and `fixo_circle_to_search` v0.3 static framework overlay booted; `contextual_search` binder exists and a Home-bar long press opened Google Circle to Search. Owner reports normal behavior. Separate `v4-cts` EROFS `product_a` and `system_ext_a` images were built within their original allocations; no v4 super or flash-script modification has been made. Sources are staged under `patch/` and binaries under `out/cts-native-v0.1-2026-11-12/`.

## 2026-11-12 Settings companion separated (current)

Owner requested keeping Settings APK and its runtime helpers independently replaceable. `fixo_settings_rom_scan_trial` still provides only the v5.3 APK before PackageManager scan. New `fixo_settings_companion` v0.1 provides the two unchanged v5.3 properties and the high-performance PowerManager bridge, without an APK. ZIP: `temp3/稳定安装/01-当前启用-Magisk/30-settings-companion-properties-performance-bridge-v0.1.zip`, SHA-256 `52c426336c8af2d6631ec7435b05f5ec72f920aa18e789deeab95eafc1af469b`. Reboot confirmed properties `ro.build.release_type=true` and `persist.sys.oplus.nandswap.storage.min=19`; bridge process running. Current `high_performance_mode_on=null`, so power-mode action was not tested. Settings candidate remains registered as UID 1000 with original signer hash. This is still a Magisk simulation, not a rebuilt ROM image; only the companion uses a runtime script. See `reports/settings-rom-signature-audit-2026-11-12.md`.

## 2026-11-12 Settings early-scan signature-block trial (current)

Owner authorized testing whether patched Settings v5.3 can be scanned as a system APK without replacing PackageManager. `fixo_settings_rom_scan_trial` v0.1 uses a retained ROM v3 signing block on the v5.3 payload, magic-mounted before scan. Boot completed; live APK SHA-256 `4d763c6c3a3fa15e7561d48434fce8b7373470ac5e0eec6adbbcc4cb11c1b098`; package remained `android.uid.system/1000` with same signer hash `17e1e36b`; Settings launcher activity started and PID was stable. The module is active and reversible. It includes only Settings.apk, so original v5.3 `system.prop` and performance bridge are absent. Await owner UI regression checks before declaring a complete ROM-integrated replacement. See `reports/settings-rom-signature-audit-2026-11-12.md`.

## 2026-11-12 fixed 26px SystemUI selected (current)

The owner compared 12px, 20px, 26px, 60px, and the old v0.5 radius source; 26px was accepted. `fixo_fullscreen_caption` v0.6 is the current module, promoted from the tested 26px APK without changing its bytes. ZIP: `temp3/稳定安装/01-当前启用-Magisk/17-systemui-fixes-fixed-drag-radius-26px-v0.6.zip`, SHA-256 `e658cae701cc119ffb55ab5653e8ddcb749140c399dfb6038cad3ca78cee7d0c`; mounted SystemUI SHA-256 `d5ecf22aa1c6fc3945a508c008af06554e3a1e6bcda9380258a9b266f821bf26`, runtime `caption-overlay=ok pid=7052`. `fixo_launcher_corner_radius` remains enabled with `ro.oplus.display.rc.size=26,26,26,26`; `fixo_freeform_corner_gesture` v1.3 remains enabled. The old v0.5 ZIP moved to `temp3/稳定安装/旧方案/` with its original SHA-256 preserved. The live tablet currently only has these three relevant modules; do not infer the rest of the archive is installed. Builder and promotion source are under `patch/`.

## 2026-11-11 12px drag radius and Settings v5.3 (latest)

The 60px SystemUI drag radius variant was confirmed visibly rounder by the owner. The owner requested a 12px comparison. Current `fixo_fullscreen_caption` module is v0.6-12px-test, mounted SystemUI SHA-256 `bfc03540057ce4870e6c5c1693ebbd7f5cb85383de0bfbb0cee51be186413eac`, runtime log `caption-overlay=ok pid=7409`; the visual 12px result is pending. `fixo_settings_confirmed` v5.3 remains mounted, Settings SHA-256 `fe8b6161f642fbbacc5eb54646f5b5040afbfa93ca999de967f7013041369bcb`. `12` here is pixels, distinct from the old 12dp/30px fallback. Both test ZIPs and builder are documented in `reports/systemui-drag-radius-60px-trial-2026-11-11.md`.

## 2026-11-11 Settings v5.3 installed for permission-page test (latest)

The owner requested `temp3/稳定安装/01-当前启用-Magisk/20-settings-apk-fix-v5.3-original-sound-effects.zip`. It was installed as module ID `fixo_settings_confirmed` and the tablet rebooted. `sys.boot_completed=1`; module runtime log ends with `postboot-overlay=ok`, and mounted `/system_ext/priv-app/Settings/Settings.apk` SHA-256 is `fe8b6161f642fbbacc5eb54646f5b5040afbfa93ca999de967f7013041369bcb` (base before mount was `7520229a7f190d35d86a4b1945b03966a49df61aa90799f57904011fdba71c12`). Launching `android.settings.SETTINGS` succeeded; Settings PID 6757 stayed stable across a five-second check. The script's `am force-stop` emitted one startup-time ActivityManager failed-transaction line but did not prevent the mount or launch. Permission-page behavior is for the owner to test. The separate SystemUI drag-radius v0.6-60px trial remains active pending owner visual feedback.

## 2026-11-11 60px bottom-corner drag radius trial (latest)

The owner requested alternate values for the old SystemUI drag preview radius. `fixo_fullscreen_caption` is now v0.6-60px-test, built by `patch/build_systemui_drag_radius_trial.py` from the exact v0.5 APK. Its `SpringDragManager.handleMoveInAnim()` uses a 60px base radius; only `classes2.dex` changes from v0.5. After reboot, service logged `caption-overlay=ok pid=7557`, and mounted SystemUI SHA-256 is `74063211a9b3b59598655f7a1c0d6b1644e04e05e9aa0db67e2f7aaa58eb6a01`. Visual result is pending. OPD2403 product name and 26px OPlus transition property remain active; framework display radius is zero. PiP RenderEngine no-clip and framework corner RRO remain disabled. A preliminary LSPosed hook did not produce a hit and was uninstalled. See `reports/systemui-drag-radius-60px-trial-2026-11-11.md`. Old v0.5 ZIP remains in stable archive for rollback.

## 2026-11-11 archive classification

The owner confirmed the Chrome PiP RenderEngine fix is stable. Its `28-pip-rounded-corner-renderengine-fix-v1.0.zip` remains in `temp3/稳定安装/01-当前启用-Magisk/` (SHA-256 `7e1addb53c1e69b3bb46b38ac58ff9c7c72be9547416b6f8ee01fe96c0142e53`), although the module is temporarily disabled on the tablet for other tests. The stock-SystemUI product-name experiment `29` was moved to `temp3/稳定安装/06-测试中-不替换SystemUI/`, alongside a copy of the 26px framework RRO trial. The folder contains a README distinguishing confirmed single behavior from unconfirmed combination behavior. Old `10`, `16`, and `17` archives remain in place. The `01` folder name is historical, not a live module-state inventory.

## 2026-11-11 stock SystemUI, freeform, and 26px OPlus property trial (latest)

The owner clarified that the OPlus transition-property module at `26,26,26,26` must also remain enabled. After reboot, `sys.boot_completed=1`, `ro.product.name=OPD2403`, `ro.oplus.display.rc.size=26,26,26,26`, framework `rounded_corner_radius=0.0dip`, and stock SystemUI SHA-256 `72cfa6810c72d7aef8cfdfd8f88117c2b5867f272d3700a08fe3c32dc7`. Active relevant modules: `fixo_freeform_corner_gesture` v1.3, `fixo_product_name_opd2403_test` v0.1, and `fixo_launcher_corner_radius` v1.1. Old SystemUI v0.5 and framework display-corner RRO remain disabled. Other unrelated modules unchanged.

## 2026-11-11 two-module fullscreen/freeform trial (superseded)

The owner requested only `fixo_freeform_corner_gesture` v1.3 and the OPD2403 product-name build.prop module for this feature test. The old `fixo_fullscreen_caption` v0.5 SystemUI replacement, framework display-corner RRO, and `fixo_launcher_corner_radius` property module are disabled. After reboot: `sys.boot_completed=1`, `ro.product.name=OPD2403`, `ro.oplus.display.rc.size=65,65,65,65` (ROM default), framework `rounded_corner_radius=0.0dip`, stock SystemUI SHA-256 `72cfa6810c72d7aef8cfdfd8f88117c2b5867f272d3700a08fe3c32dc7`, panorama branch `true`, and secure `fixo_corner_mode=1`. Other unrelated modules were left as they were. Visual result is pending.

## 2026-11-11 stock SystemUI restored; drag radius method clarified

The owner requested the new stock-SystemUI approach. `fixo_fullscreen_caption` v0.5 is disabled and `fixo_product_name_opd2403_test` is enabled. After reboot, `ro.product.name=OPD2403`, the stock SystemUI APK SHA-256 is `72cfa6810c72d7aef8cfdfd8f88117c2b5867f272d3700a08fe3c32dc7`, and the framework display-corner RRO remains 26px. Direct JADX of stock `FullscreenTaskImageView.getCornerRadius()` shows it internally calls `OplusFlexibleWindowAnimationUtils.getDisplayCornerRadius(Display)` and computes `dpToPx(max((int)(radiusPx / density) - 8, 12))`. Prior shorthand that v0.5 entirely bypasses `Display.getRoundedCorner()` was wrong: it replaces the caller's raw radius with this adjusted/minimum radius. At 400dpi and framework radius 26px, the return is about 30px. This may explain visual differences between old and stock SystemUI even though both read the framework corner. Decompiled local class: `C:/Users/GY/Documents/GitHub/temp/FullscreenTaskImageView-stock.java` (temporary, not Git).

## 2026-11-11 rounded-corner test restored to 26

Current booted state: `ro.oplus.display.rc.size=26,26,26,26`, framework `rounded_corner_radius=26px`, and all four `Display.getRoundedCorner()` radii 26. `fixo_fullscreen_caption` v0.5 and `fixo_freeform_corner_gesture` v1.3 are enabled. The 100px OPlus/framework test looked wrong to the owner and was rolled back. The PiP RenderEngine no-clip module and OPD2403 product-name trial remain disabled. See `reports/corner-source-ab-2026-11-11.md` for archived trial ZIPs and observations.

## 2026-11-10 complete `forceNoClipSmooth` internal gates

The original OOS binary was restored byte-for-byte from the four-byte test copy and its SHA-256 matched the saved stock hash. Full 660-byte function disassembly is saved locally under `out/pip-force-gates-2026-11-10/`; the complete conditional pseudocode is in `reports/pip-weight-native-consumer-2026-10-27.md`. The earlier shorthand that `d0=1` alone triggers the change was incomplete. Active `sSkipClipSmooth` first excludes `SkRRect type=0`; two alternative DisplaySettings gate routes then apply; weight must remap into [0.99,1.34], and names beginning `DecorNavBarBg` or `InputMethod` are excluded. `type=3` is not a literal requirement, and `d0=1` is not globally necessary (only decisive for the measured Chrome child, where `d5=0`). The no-op library is still a non-persistent live bind, not a stable module.

## 2026-11-09 PiP exact RenderEngine gate byte

The same Chrome PiP child enters `forceNoClipSmooth()` in both OPlus Home and Settings. A temporary arm64 entry uprobe on the currently mounted non-persistent no-op library found `DisplaySettings + 0xd0 = 1` on Home versus `0` in Settings, while sampled neighboring flags were all zero. For this Chrome child, the original OOS function's branch would transform the radius only for the Home state. Thus the call itself is not Home-only; the `+0xd0` byte distinguishes these two measured states, subject to the additional gates above. The OPlus field name and writer are not yet known. Probe events were removed and tracing returned off. The no-op bind remains a non-persistent experiment, not a stable module. See `reports/pip-weight-native-consumer-2026-10-27.md`.

## 2026-10-27 PiP RenderEngine gate: Home / Recents / Settings

The user confirmed that a temporary four-byte `forceNoClipSmooth()` no-op in the matching OOS `librenderengineextimpl.so`, with the scoped PiP hook in original `stock` Ext mode, fixes both the Chrome Home PiP stable mismatch and the entry jump. This is **not** an installed or stable module; it is a live bind mount lost on reboot. Under the original library with its own diagnostic log enabled, the same Chrome child `#176` repeatedly logged `No Smooth` on Home and Recents. With Settings foreground, the child remained visible and its frame counter advanced 3521 -> 3616, but that log stopped. Re-entering Home restored the logs. Thus the abnormal transformation is gated by a Home/Recents-dependent render state, but the exact field is not yet identified. The debug log property was reset to 0 and the temporary no-op remounted; SurfaceFlinger PID 9874 was running, with patched library SHA-256 `7c5c7c37234886135482c69fc0bbc50b3b2b9ca8f38544d12ccc7df0336de895`. Detailed report: `reports/pip-weight-native-consumer-2026-10-27.md`. Next: identify the changing `DisplaySettings` / `LayerSettings` flag and narrow the patch before making it persistent.

## 2026-10-27 PiP low-weight sweep

Installed the signature-compatible v0.5-low-weight-test LSPosed APK under the existing package; only the Ext validation lower bound changed from 0.5 to 0.0. User-confirmed Chrome Home PiP: 0.1 nearly square/no mismatch (screenshot matched), 0.5 rounded/no mismatch, 0.6 normal, 1.5 and 1.6 mismatch; 1.3 was already abnormal. A live 0.1 SurfaceFlinger dump showed both Chrome buffered children still carrying radius about 40 in display space and weight 0.1, so the visual squareness is weight-dependent rendering rather than a zero radius. Zero was not tested due boundary risk and low diagnostic value. Restored live properties to `native` / `1.7`; SystemUI PID 2298 remained present. The v0.5 APK is at `out/pip-native-radius-v0.5-low-weight-2026-10-27/`, and v0.3 is preserved for rollback. See `reports/pip-smooth-radius-weight-ab-2026-10-26.md`.

## 2026-10-26 PiP radius weight diagnostic (newer than the v0.1 note below)

Additional 1.3 A/B: owner still saw the stable defect, so 1.7 is not a uniquely failing literal value. In the live abnormal Chrome Home PiP, the two visible buffered Chrome children **both** had weight 1.3: outer 994×559 at radius 40 / 1×, video 800×432 scaled ~1.24× with local radius ~32.2 (display ~40), vertically inset ~11 px. Thus the outer layer did receive the override; differing geometry/content plus native smooth composition remain under investigation. Active task 43 was pinned, Launcher top-resumed. Restored `native` / `1.7` debug properties and SystemUI PID 2268 remained stable. See the A/B report for exact layer IDs and bounds.

Later same-video weight sweep: 1.9 still had an obvious defect nearly like 1.7; 2.0 again gave normal stable corners but a brief creation jump; 2.5 produced a smaller settled corner and a more obvious jump. 2.1 was set but never visually graded before the owner asked for a larger value. Debug properties were restored to `native` / `1.7` (the weight property is ignored in native mode), with SystemUI PID 2268 stable. An earlier animation stage using a different smooth weight is a hypothesis, not yet a captured transaction. See the updated A/B report.

Vector module v0.3-lifecycle-test is installed and SystemUI booted normally. Unlike v0.1, its PiP hook is confirmed by live per-call logs. In the same Chrome fullscreen-to-Home PiP test: `native` normal, `stock` abnormal, Ext weight `2.0` approximately normal, Ext weight `1.7` abnormal. The user still notices a brief corner change only during PiP creation, but has explicitly deferred that issue. A v0.4 experiment also intercepted the Launcher `SwipePipToHomeAnimator` helper calls; logs confirmed both Launcher and SystemUI hits, yet the brief jump remained. v0.4 was rolled back; source and device are on v0.3, scoped only to SystemUI, with debug mode defaulting to `native`. Focus now is the original stable bug and why physical display plus screenrecord show it while screencap does not. See `reports/pip-smooth-radius-weight-ab-2026-10-26.md` and `reports/pip-radius-composition-trace-2026-10-26.md`. The older v0.1 visual result must not be cited as proof that its hook fired, because its `isFirstPackage()` guard may have excluded SystemUI.

## 2026-10-26 PiP native-radius test confirmed

The owner confirmed that Chrome fullscreen-to-Home PiP corners became visually normal with Vector v2.2 (3080) and LSPosed APK `dev.mossback360.fixo.pipradius` v0.1-test enabled. Vector reports the module loaded and scoped to `com.android.systemui`; the device boots and SystemUI PID 2271 remained stable. The hook redirects only WM Shell PiP `round(...)` calls to Android's native `nativeSetCornerRadius()`, bypassing OPlus's smooth-radius extension in that path. Installed APK backup: `out/pip-corner-ext-analysis-2026-10-26/fixo-pip-native-radius-v0.1-installed.apk` (SHA-256 `0fc628e760271f393e3cf5d4ca8693df0f563c93d394910e4e492787ce035c7e`). Source: `patch/pip-native-radius-hook/`. A diagnostic v0.2 was built but not installed; do not replace the user-confirmed v0.1. No per-call hit log was captured, so this is a user-confirmed visual repair, not a fully traced native mechanism. Old SurfaceFlinger and SkiaGL Magisk A/B modules remain disabled.

## 2026-10-26 PiP SurfaceFlinger A/B addendum

The one-boot OPD2601 ColorOS SurfaceFlinger trial did **not** reach PiP rendering. The ColorOS binary required an additional MixLut3D library and, after it was supplied, failed at startup on a symbol missing from OxygenOS `libgui.so`: `IGraphicBufferProducer::setBbqQueuedBufCnt(int)`. The temporary Magisk module `fixo_pip_color_sf_ab_test` v0.1 was disabled immediately and the device rebooted to a complete OxygenOS boot; stock SurfaceFlinger and SystemUI are running. No partition was flashed. Do not repeat a single-binary transplant. Details and SHA-256 identities: `out/pip-sf-color-ab-v0.1-2026-10-26/TEST_RESULT.md`.

## 2026-10-23 PiP investigation addendum

The owner temporarily flashed a near-version OPD2601 ColorOS port, where Chrome 640x360 Home PiP was visually normal. Its graphics chain and Home/Settings PiP samples are saved under `E:\工程\github\xiaoxin Oxygen\temp3\OPD2601_graphics_2026-10-23`. After returning to OxygenOS, the same PiP pattern was confirmed abnormal on OPlus Home and normal with Settings foreground; raw samples and current graphics binaries are under `E:\工程\github\xiaoxin Oxygen\temp3\OOS16_pip_2026-10-23`.

The first strong difference was SkiaVk RenderEngine on OxygenOS versus SkiaGL on ColorOS. A two-property Magisk module (`fixo_pip_skiagl_test` v0.2) genuinely switched OxygenOS SurfaceFlinger to `RE GLES (Ganesh)`, but the owner confirmed the Chrome PiP corner defect remained. The module was disabled and the device rebooted back to stock `skiavkthreaded`/Vulkan; it must not be added to a stable module set. Test ZIP, raw GL PiP dumps and result are under `out/pip-renderengine-skiagl-v0.2-test-2026-10-23/`. The earlier v0.1 experiment changed only the backend property and did not actually switch the renderer, so it is invalid as a visual test. Next focus: PiP bounds/crop and Home-specific window transaction differences, not a blanket graphics-library transplant.

Updated: 2026-09-15

The owner confirmed a compatible trio on 2026-09-15: `fixo_fullscreen_caption` v0.5, `fixo_opd2514_ai_addons` v2.5, and `fixo_freeform_corner_gesture` v1.3. With all three together, both the three-finger Mind Space gesture and bottom-corner fullscreen-to-freeform gesture work normally. Preserve these exact versions as a tested combination and do not add `fixo_ai_a30_restore`.

The owner clean-flashed the OxygenOS 16 port and confirmed a staged base restore containing exactly 12 active Magisk modules. That historical snapshot contained no AI add-on or third-party power module and is archived at `out/confirmed-selected-modules-2026-09-14/LIVE_DEVICE_STATE.txt`. Later work added launcher-corner v1.1-test, smart-refresh v0.3, and camera-safe v2.0 before the 2026-09-15 AI/freeform trio was confirmed.

The confirmed Settings owner is `fixo_settings_confirmed` v3.9. It supersedes v3.6 and combines the accepted OxygenOS UI polish with the working ColorOS-compatible RAM-expansion activity/writeback.

The confirmed SystemUI owner is `fixo_fullscreen_caption` v0.5. It was installed only after the large Settings/global-app payloads completed a separate boot and package scan. Runtime verification reported `caption-overlay=ok pid=7008`; the PID remained stable and the mounted APK SHA-256 was `92c57e647c9520cb043be1d0a0cf010c6f1e7dec2b72129837b45cc261e57560`.

Confirmed user-visible behavior includes:

- fullscreen three-dot controls and bottom-corner freeform entry;
- Settings v3.9 and RAM expansion;
- camera startup-policy fix, display PQ bridge, global apps, OTA, smart cover, speaker rotation, and ZUI privacy pages;
- ASI screen attention glue v0.2: boot binding now retries until successful, and face-plus-gaze presence refreshes `PowerManager.userActivity()` without injecting key/touch input. The owner confirmed it works. Accepted limitations: it can briefly dim then brighten because sampling occurs near timeout, and the landscape workaround can treat a nearby person as attentive even when they are not looking directly at the panel;
- ZUI-sensitive lift-to-wake v0.2 following the OxygenOS switch.
- Smart refresh v0.3 exposes the stock `智能切换` option and native mode 0. A gesture sampled `120 Hz`, then returned to `60 Hz` after five seconds idle. Settings scrolling stays at `60 Hz` because `com.android.settings` is in the stock OPlus TouchIdle blacklist; the owner accepted v0.3 as usable with this limitation.
- ZUI Camera safe-capture v2.0 fixes the runtime algorithm-support refresh so the Morpho SR-disable switch remains effective. The owner confirmed zoom capture no longer crashes.
- Launcher-corner v1.1-test sets only `ro.oplus.display.rc.size=26,26,26,26`. The owner confirmed the desktop-launch, fullscreen-to-freeform, and A/B gesture-bar quick-switch transitions; the previous asymmetric oversized-radius flash is gone.

Do not describe smart-refresh v0.3 as an all-app, every-touch high-refresh fix. Changing that behavior requires a separate `oplus_vrr_config.json` experiment and regression testing across video, games, brightness, and thermal policy.

Do not reinstall the OPD2514/A.30 AI add-ons as part of this baseline. Panorama v1.4, formal-corner v0.4, smooth-corner, Dolby, material-stroke, and third-party speaker modules remain rejected or unconfirmed.

The `modules-2026-09-14` GitHub release publishes only new/version-changed modules. PQ, global apps, OTA, ZUI privacy, and hall v2 reuse the 2026-09-09 release because their versioned functional payloads did not change.

The authoritative confirmed inventory is now 15 active IDs. `fixo_launcher_corner_radius` v1.1-test supersedes the disabled v1.0 module under the same ID. The standalone `fixo_freeform_smooth_corner` experiment is not installed; SystemUI v0.5 separately retains its accepted drag-corner fallback.

`fixo_attention_asi` is now v0.2-trial under the existing module ID. Its confirmed archive is `out/attention-asi-glue-v0.2-2026-09-14/fixo-attention-asi-v0.2-trial-magisk.zip`, SHA-256 `c05e9acc429e691d737eae054354dbb8ee7a9fb20fd54f4b0605946d2187613e`.

See `reports/module-audit-2026-09-14.md` for superseded and rejected modules that must not be added to the baseline.

## 2026-11-11 restored SystemUI v0.5 for drag-animation comparison (latest)

Owner observed the constant 12px trial was visibly smaller than 60px and requested the original modified-APK behavior. Reinstalled the preserved `fixo_fullscreen_caption` v0.5 ZIP under the same module ID. After reboot, `sys.boot_completed=1`, service log `caption-overlay=ok pid=7300`, and mounted SystemUI SHA-256 `92c57e647c9520cb043be1d0a0cf010c6f1e7dec2b72129837b45cc261e57560`. Settings v5.3 remained mounted (SHA-256 `fe8b6161f642fbbacc5eb54646f5b5040afbfa93ca999de967f7013041369bcb`). Await owner comparison of v0.5 drag animation. The v0.5 radius has a 12dp minimum (~30px at 400dpi); constant 12px bypasses its dynamic calculation.

