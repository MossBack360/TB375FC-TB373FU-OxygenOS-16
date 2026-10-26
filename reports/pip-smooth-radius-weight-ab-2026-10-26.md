# Chrome PiP smooth-radius weight A/B (2026-10-26)

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

The live v0.3 hook logged PiP calls with radii including `69.69697`, `40.0`, and animation values decreasing toward the final radius. Both ext weights were confirmed in the hook log. The stock test logged a mode switch, and the same Chrome video was re-entered for each visual comparison. This directly supports that the extra smooth-radius weight (or its downstream interpretation) causes the **stable-state** defect; it does not yet identify the native consumer or the brief creation-time transition.

After the 1.7 test, `debug.fixo.pip.corner_mode` was restored to `native`; SystemUI stayed running. The owner re-entered the same PiP and confirmed its stable corners normal again. Do not promote this diagnostic build to the stable module set until the brief entry transition and basic PiP regression tests are addressed.

## Remaining entry transition lead

The extracted current OplusLauncher.apk (SHA-256 `5ee1555fd478024ae33c91057606eb6462dc26007c1c770bdcb409ae937f2eb9`) has a separate Chrome-to-Home path: `AbsSwipeUpHandler.createWindowAnimationToPip()` creates `SwipePipToHomeAnimator`, which calls `com.android.systemui.shared.pip.PipSurfaceTransactionHelper.scaleAndCrop()` or `scaleAndRotate()`. Both submit ordinary Java `Transaction.setCornerRadius()`, which on this ROM is expected to take the 1.7-weight Ext path in the **Launcher process**, outside the v0.3 SystemUI scope. This is a plausible cause of the brief creation-time corner change, not yet a runtime-proven fix. A next experiment should only instrument/redirect those Launcher helper methods, leaving unrelated Launcher transitions unchanged.

Recovery: the preserved v0.1 APK is `out/pip-corner-ext-analysis-2026-10-26/fixo-pip-native-radius-v0.1-installed.apk`, but because v0.1 may be a no-op it is **not** a reliable functional fallback. To disable v0.3, disable `dev.mossback360.fixo.pipradius` in Vector or uninstall the app and restart SystemUI; this restores stock behavior.
