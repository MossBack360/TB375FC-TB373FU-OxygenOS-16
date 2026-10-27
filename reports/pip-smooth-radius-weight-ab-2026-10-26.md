# Chrome PiP smooth-radius weight A/B (2026-10-26)

## 2026-10-27 low-weight extension

The same signed LSPosed package was upgraded in place to v0.5-low-weight-test (versionCode 5); it changes only the Ext weight guard from `0.5..2.5` to `0..2.5`, with the same SystemUI-only PiP hook. APK: `out/pip-native-radius-v0.5-low-weight-2026-10-27/fixo-pip-native-radius-v0.5-low-weight.apk`, SHA-256 `367fb2b065e30483549865e03b1bd70d546f819edc32a9a028045754d1ef33de`. Certificate SHA-256 matches v0.3: `a42ad4a68423c59ca38b929cf901636f7b88d260157b502fa896ac242517e5ed`. Android booted normally after install; SystemUI PID 2298 remained stable across the sweep. The preserved v0.3 APK is still the rollback archive.

User-observed same-Chrome-video Home PiP results:

| Ext weight | Stable visual result |
| ---: | --- |
| 0.1 | Nearly straight/square corners; no inner/outer mismatch; screenshot agreed with visual observation |
| 0.5 | Rounded corners appeared; no mismatch |
| 0.6 | Still normal; shape difference from 0.5 too small to judge |
| 1.3 | Mismatch (prior test) |
| 1.5 | Mismatch |
| 1.6 | Mismatch |

At 0.1, the pinned Chrome PiP task had bounds `(1749,768)-(2898,1413)` with OPlus Launcher top-resumed. Both visible buffered `ChromeChildSurface` layers received weight 0.1. The outer was 1149×645, radius 40, 1× display transform; the video child was 800×432, scaled about 1.436×/1.440×, locally rounded about 27.85/27.78 (approximately 40 in display space) and inset 12 px from the outer top. Both were reported as `DEVICE` composition. Thus 0.1 did **not** merely zero out the stored radius; it changed the rendered shape while radius remained about 40. The lower-weight results place the observed transition somewhere between 0.6 and 1.3 for this particular video/geometry. They do not prove a fixed native threshold, a literal 1.7 precision issue, or the exact compositor branch. The exact zero value was deliberately not exercised after 0.1 already answered the near-zero question, because it could be an unsupported arithmetic boundary.

After testing, transient properties were restored to `native` / `1.7` (`corner_weight` ignored in native mode), with SystemUI PID 2298 still present. v0.5 remains installed as a diagnostic build, not promoted to the stable set.

Device: TB375FC OxygenOS 16, Chrome fullscreen video -> Home PiP. This is a reversible Vector/LSPosed experiment scoped to `com.android.systemui`; no SystemUI APK or native graphics library was replaced.

## Important correction

The previously preserved v0.1 APK was visually associated with a good PiP state, but it had no captured per-call hit. Its setup was gated on `PackageLoadedParam.isFirstPackage()`. On the current Vector/SystemUI process, package-load callbacks observed by v0.3 reported `first=false` for early packages. Therefore v0.1 must **not** be treated as a proven active fix. v0.3 removed that gate and logged actual intercepted PiP calls.

## Current diagnostic build

- Source: `patch/pip-native-radius-hook/`.
- Installed package: `dev.mossback360.fixo.pipradius` v0.3-lifecycle-test, scoped only to SystemUI.
- Local APK: `out/pip-native-radius-v0.3-lifecycle-2026-10-26/fixo-pip-native-radius-v0.3-lifecycle.apk`.
- APK SHA-256: `9612859d914ab2497fdf3801685ed1336840a4e089087c10cfd124b7eab03917`.
- Signing certificate SHA-256 matches v0.1: `a42ad4a68423c59ca38b929cf901636f7b88d260157b502fa896ac242517e5ed`.
- Stable boot: `sys.boot_completed=1`, SystemUI PID 2319 during the experiment.
- `debug.fixo.pip.corner_mode` controls `native` (default), `stock`, or `ext`; `debug.fixo.pip.corner_weight` applies only to `ext`. These are transient debug properties and reset on reboot.

## Results

| Mode | Submitted call | User-observed stable Chrome Home PiP |
| --- | --- | --- |
| `native` | `nativeSetCornerRadius(radius)` | Normal; creation has a brief separate corner change |
| `stock` | Original OxygenOS `Transaction.setCornerRadius()` | Oversized corner defect returns |
| `ext`, weight `2.0` | `nativeSetCornerRadiusExt(radius, 2.0)` | Approximately normal; brief creation change remains |
| `ext`, weight `1.7` | `nativeSetCornerRadiusExt(radius, 1.7)` | Oversized corner defect returns |
| `ext`, weight `1.9` | `nativeSetCornerRadiusExt(radius, 1.9)` | Defect still obvious, visually almost like 1.7 |
| `ext`, weight `1.3` | `nativeSetCornerRadiusExt(radius, 1.3)` | Oversized/inner-outer mismatch defect still present |
| `ext`, weight `2.5` | `nativeSetCornerRadiusExt(radius, 2.5)` | Stable corner becomes smaller than at 2.0; creation-time jump becomes more pronounced |

Later same-video retest: the owner reconfirmed 2.0 gives normal stable corners but still jumps during creation. `2.1` was selected briefly but the owner requested a more exaggerated value before reporting a visual verdict, so **there is no 2.1 result**. The diagnostic property was then set to 2.5 (the v0.3 hook's upper accepted bound) and the owner reported the smaller stable corner / larger jump above. Afterward both debug properties were returned to `native` / `1.7` and SystemUI PID remained 2268. These later property values were read back, but no new per-call log was captured for 1.9 or 2.5.

The owner's hypothesis is that an earlier transition stage may still use stock smooth weight 1.7 while the settled SystemUI PiP uses the override. The larger creation jump at 2.5 is compatible with a shape mismatch, **but does not establish** which component submits that earlier transaction or its actual weight; the previous v0.4 Launcher helper hook did not remove the jump.

### Live 1.3 abnormal layer inspection

After the owner visually confirmed the defect at Ext 1.3, live `dumpsys activity activities` identified Chrome task 43 in pinned mode, bounds `(1910,1201)-(2904,1760)`, with OPlus Launcher top-resumed. SurfaceFlinger showed **both visible buffered** `ChromeChildSurface` layers carrying `weight=1.3`:

- Outer child `#1323`: 994×559 buffer, display bounds `(1910,1201)-(2904,1760)`, transform 1×, `cornerRadius=40`, `weight=1.3`, premultiplied blend, `DEVICE` composition.
- Video child `#1325`: 800×432 buffer, display bounds starting `(1910,1212)`, transform about 1.2425× / 1.2454×, local `cornerRadius≈32.19/32.12`, `weight=1.3`, opaque blend, `DEVICE` composition. Its display-space radius is approximately 40. It leaves about 11 px above and 10 px below the video within the outer 994×559 layer.
- Chrome main Activity buffer `#1312` and the PiP menu leash also showed radius 40 / weight 1.3; the menu had no visible buffer. Other old unreachable transition layers retained prior weights and must not be mistaken for the active PiP.

Therefore the specific claim that the outer Chrome child *never receives the override* is contradicted by the active layer state. The two active child layers do have different buffer geometry and vertical placement, so weight/corner equality does **not** establish identical effective masks or output pixels. The lower-weight defect also rules out a numeric precision issue unique to the literal value 1.7. The remaining target is how the native compositor applies smooth clipping to two overlapping buffered children and their ancestors in the Home output path, compared with the normal Settings/ColorOS path. This snapshot does not identify the exact native branch. Debug properties were restored to `native` / `1.7` afterward; SystemUI PID remained 2268.

The live v0.3 hook logged PiP calls with radii including `69.69697`, `40.0`, and animation values decreasing toward the final radius. Both ext weights were confirmed in the hook log. The stock test logged a mode switch, and the same Chrome video was re-entered for each visual comparison. This directly supports that the extra smooth-radius weight (or its downstream interpretation) causes the **stable-state** defect; it does not yet identify the native consumer or the brief creation-time transition.

After the 1.7 test, `debug.fixo.pip.corner_mode` was restored to `native`; SystemUI stayed running. The owner re-entered the same PiP and confirmed its stable corners normal again. Do not promote this diagnostic build to the stable module set until the brief entry transition and basic PiP regression tests are addressed.

## Deferred entry transition experiment

The extracted current OplusLauncher.apk (SHA-256 `5ee1555fd478024ae33c91057606eb6462dc26007c1c770bdcb409ae937f2eb9`) has a separate Chrome-to-Home path: `AbsSwipeUpHandler.createWindowAnimationToPip()` creates `SwipePipToHomeAnimator`, which calls `com.android.systemui.shared.pip.PipSurfaceTransactionHelper.scaleAndCrop()` or `scaleAndRotate()`. A v0.4 test additionally intercepted those Launcher helper calls; the hook log confirmed both Launcher and SystemUI hits, but the owner still saw the brief creation-time corner change and stable corners remained normal. This disproves the simple hypothesis that adding only those Launcher hooks fixes the transition. The v0.4 APK is retained as a rejected experiment at `out/pip-native-radius-v0.4-launcher-2026-10-26/fixo-pip-native-radius-v0.4-launcher.apk` (SHA-256 `4b0e9f987ca773ded18ed4ba893fd951fedef3dafeb2c19f5fad9734c786bd4d`). It was uninstalled by downgrading back to v0.3, Launcher scope removed, and device rebooted successfully. The owner has deferred the brief transition issue.

Recovery: the preserved v0.1 APK is `out/pip-corner-ext-analysis-2026-10-26/fixo-pip-native-radius-v0.1-installed.apk`, but because v0.1 may be a no-op it is **not** a reliable functional fallback. To disable v0.3, disable `dev.mossback360.fixo.pipradius` in Vector or uninstall the app and restart SystemUI; this restores stock behavior.
