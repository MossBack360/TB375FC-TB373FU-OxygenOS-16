# PiP `setCornerRadiusExt` static analysis (2026-10-26)

Scope: read-only analysis of the currently running TB375FC OxygenOS files. No module or device setting was changed. Pulled copies and selected JADX output are in `out/pip-corner-ext-analysis-2026-10-26/live/`.

## Artifact identity

- Device `framework.jar`: SHA-256 `60ea788ac729e8f39c40c287ab91f65ce8575b2f4e560172d1d8de2add1cef37`.
- Device `oplus-framework.jar`: SHA-256 `d1e6ce599c0d154b784c968894eec7dea72b16d8349d9eb59d2e14b8987924da`.
- Device `SystemUI.apk`: SHA-256 `72cfa6810c72d7aef8cfdfd8f57ee8f88117c2b5867f272d3700a08fe3c32dc7`.
- Device `OplusLauncher.apk`: SHA-256 `5ee1555fd478024ae33c91057606eb6462dc26007c1c770bdcb409ae937f2eb9`.
- Device `libgui.so`: SHA-256 `c6208e124b0f4c57d82ce01a6c2a8d868a8488c49994be24253f9824b2a19367`.

The older local `OxygenOS_GLO` JAR/APK hashes differ, so findings below are based on the live copies where possible.

## Definition and implementation

The Java entry is `android.view.SurfaceControl.Transaction.setCornerRadiusExt(SurfaceControl, float cornerRadius, float weight)` in the live `framework.jar`. It calls `SurfaceControl.nativeSetCornerRadiusExt(long transaction, long surface, float radius, float weight)` when `mTransactionExt.isSmoothRadiusOn()` is true. Otherwise it calls ordinary `nativeSetCornerRadius` with `reverseNoWeightRadius(radius, weight)`.

The live `libandroid_runtime.so` imports native `android::SurfaceComposerClient::Transaction::setCornerRadiusExt(android::sp<android::SurfaceControl> const&, float, float)` from `libgui.so`. ARM64 disassembly of the live `libgui.so` at `0x16a4a0` shows `getLayerState()`, stores the first float at layer-state offset `0x17c`, stores the second float at offset `0x0c`, and sets bit `0x80000000` at offset `0x148`. The ordinary `setCornerRadius` implementation at `0xe9c70` stores only the first float at `0x17c` and sets the same bit. Thus the extension is **not merely a call-through wrapper**. Field semantics are inferred from the Java names; the exact parcel/SF consumer of the second field remains to be traced.

`com.oplus.view.OplusSmoothRoundedManager` in the live `oplus-framework.jar` enables smooth radius when `(anim_level < 3 || upgrade_anim_level < 3) && default_weight != 2.0`. The device currently reports `persist.sys.oplus.anim_level=2`, `persist.sys.oplus.upgrade_anim_level=2`, and no explicit `persist.sys.oplus.default_smooth_weight`; the compiled default is `170 / 100 = 1.7`. Therefore this branch is expected active for newly initialized processes, though the static inspection is not a runtime call trace.

## Callers

- Live `SystemUI.apk`: `com.android.wm.shell.pip.PipSurfaceTransactionHelper.round(...)` calls ordinary Java `Transaction.setCornerRadius(...)` in both boolean and scaling overloads. On the active smooth-radius branch, that Java method forwards to `nativeSetCornerRadiusExt(radius, defaultWeight)`. This is an **indirect PiP path**.
- Live `OplusLauncher.apk`: `com.oplus.splitscreen.ReflectionHelper.setCornerRadiusExt(...)` reflectively calls the Java method. A confirmed direct caller is `com.android.wm.shell.fullscreen.FullscreenTaskOperations$TransitionHandler`, which passes weight `2.0` and also calls ordinary `setCornerRadius` on the same leash. Other direct callers appeared in the older decompiled Launcher tree (`OplusDragTaskFullAnimation`, panorama transition, window decoration), but these have not all been reverified against the live APK.
- No direct `setCornerRadiusExt` call has yet been established inside the live PiP helper or the Launcher swipe-PiP-to-Home path. The PiP helper's ordinary `setCornerRadius` call is sufficient to reach the native extension under the active feature gate.

## Interpretation and limit

This interface sends radius **and an additional weight** into a native layer-state transaction. It is worth testing as a PiP corner-path candidate. Static code does not prove the defect originates here, nor explain why identical PiP geometry is normal in Settings and abnormal on Home. A minimal next experiment should trace/compare the submitted radius and weight and the native consumer across Home/Settings before modifying this API globally.
