# PiP smooth-radius/composition trace (2026-10-26)

Question: why does the **stable** Chrome Home PiP render an oversized/black corner in OxygenOS, while `screencap` looks normal and physical display/`screenrecord` show the defect? This is an evidence inventory, not a native root-cause claim. The owner deferred the brief PiP creation jump.

## Proven by same-ROM intervention

- v0.3 scoped to SystemUI intercepts `PipSurfaceTransactionHelper.round(...)`; per-call hit logs were recorded.
- Same Chrome fullscreen-to-Home test: original `Transaction.setCornerRadius()` (`stock`) reproduces the stable defect; direct `nativeSetCornerRadius(radius)` (`native`) yields normal stable corners. Explicit `nativeSetCornerRadiusExt(radius, 1.7)` reproduces; Ext `2.0` is approximately normal. These modes submit new transactions when PiP is re-entered.
- A live read-only SurfaceFlinger dump with v0.3 `native` and Chrome Home PiP showed `weight=2` on the visible PiP task and both visible Chrome children. The PiP task/outer child had radius 40; the scaled video child had radius about 30.3 in local coordinates and about 1.32 display scale. An old stock OOS Home dump with the defect showed `weight=1.7` on the corresponding visible layers. The two samples differ in orientation/size, so this is evidence of the weight-state effect, **not** a pixel-identical geometry A/B. A stale, unreachable transition leash retained weight 1.7 in the current dump; it was marked invisible and is not evidence that the active PiP still uses 1.7.
- This establishes that **how the SystemUI PiP round transaction carries the smooth-radius weight matters**. It does not establish that Chrome chooses the weight, that weight 1.7 is universally bad, or that a particular SurfaceFlinger function is faulty.

## Existing cross-state/cross-ROM records

Raw OxygenOS records: `E:\工程\github\xiaoxin Oxygen\temp3\OOS16_pip_2026-10-23\runtime\`. Normal OPD2601 ColorOS records: `E:\工程\github\xiaoxin Oxygen\temp3\OPD2601_graphics_2026-10-23\runtime\`.

- OOS Home `sf_home.txt` shows the PiP task at radius 40, weight 1.7; the visible 640×360 Chrome video child at radius about 21.21 in its own coordinates (scaled about 1.886 to the display); the other visible Chrome child at radius 40, weight 1.7. The owner observed the defect on the physical panel.
- OOS Settings `sf_settings.txt` shows the same kind of two visible Chrome children and weight 1.7, yet the owner observed normal corners. Thus there is no demonstrated Home-only change in the **submitted weight value**.
- OPD2601 ColorOS Home `sf_home.txt` also shows two visible Chrome children and weight 1.7 (PiP task radius 38, rather than OOS's 40), yet the owner observed normal corners. The 2 px radius difference is not by itself a demonstrated explanation.
- `sf_home_during_screenrecord.txt` records a `ScreenRecorder` virtual display and mirrored display-0 tree. The physical display uses a mix of `DEVICE` and `CLIENT` layers; the recorder virtual display is `usesDeviceComposition=false`, `usesClientComposition=true`, with both Chrome children in its output list. The equivalent OPD2601 dump also has a client-composed recorder virtual display. Therefore "only DEVICE composition is broken" and "virtual display alone is broken" are both too simple.
- Both ROMs export Skia smooth-round-rect routines in SurfaceFlinger/RenderEngine; the binaries differ. The exact call site that consumes the extra weight and the branch used for display versus capture have **not** been resolved. REA offline ELF layout currently rejects ARM64 under its available pwntools profile; WSL `nm/readelf/objdump` can inspect symbols and disassembly without modifying the device.

## Why a screenshot can disagree with recording

The saved runtime dump proves `screenrecord` creates a mirrored virtual display. AOSP's `screenrecord.cpp` explicitly creates a `ScreenRecorder` display and mirrors the physical display, whereas `screencap.cpp` calls `ScreenshotClient::captureDisplay()` for a one-shot image. This is a genuine pipeline distinction, not a frame-timing explanation. It **does not yet prove** exactly which OPlus code produces different rounded clipping in the two routes. Relevant AOSP sources:

- https://android.googlesource.com/platform/frameworks/av/+/b675cea85b508d7f60f1344e5a24c3db7a5b8d0f/cmds/screenrecord/screenrecord.cpp
- https://android.googlesource.com/platform/frameworks/base/+/master/cmds/screencap/screencap.cpp

## Narrow next checks

1. On one fixed Chrome PiP geometry, collect `dumpsys SurfaceFlinger` in v0.3 `native` and `stock`, annotate with the owner's visual verdict, and compare task/child radius, weight, parentage, and display-output geometry. Restore `native` immediately after stock capture. This distinguishes transaction-state changes from purely downstream interpretation.
2. Compare with a visually normal multi-surface PiP (e.g. Google Maps) using the same fields. If Maps also uses 1.7, then the fault requires the Chrome plane geometry/content or its overlap, not merely the weight value.
3. Trace the layer-state weight through the **matching** OOS `libgui.so` to SurfaceFlinger and its `captureDisplay`/physical/virtual render call sites. Do not transplant cross-ROM native binaries: the earlier OPD2601 SurfaceFlinger A/B failed to start because OOS `libgui.so` lacks `IGraphicBufferProducer::setBbqQueuedBufCnt(int)`.
