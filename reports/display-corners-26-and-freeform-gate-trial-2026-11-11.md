# 26px display corners and bottom-corner gesture trial

The owner confirmed that `fixo_fullscreen_caption` v0.5 alone did not restore the bottom-corner drag. The two paths are separate: the stock `SpringDragManager` obtains the drag preview radius via `OplusFlexibleWindowAnimationUtils.getDisplayCornerRadius(Display)` and `Display.getRoundedCorner()`, while the `fixo_freeform_corner_gesture` module registers the panorama work-station feature and enables the FlexibleWindowUI branch.

The v0.1 framework-corner RRO used 30px. Its successor `patch/display-corner-rro-v0.2/` uses 26px, matching the installed `ro.oplus.display.rc.size=26,26,26,26`. The new archive is `out/display-corner-rro-v0.2-2026-11-11/fixo-display-corner-rro-v0.2-test.zip`, SHA-256 `f66bd6c9451c12f7bdeeb77930f7aa0e9e86f2e05e409c86c61be6c85141e1cd`. The overlay APK is signed and verified; resource dump reports `rounded_corner_radius=26.000000px`.

The archived `10-freeform-corner-feature-config-v1.3.zip` adds only `oplus.software.wms.panorama_work_station` to the live feature XML, aside from a timestamp line. Its service script sets `persist.oplus.panorama.branch.enable=true` and `panoramic_forced_disable_state=0` when `fixo_corner_mode=1`.

Both modules were installed and the tablet rebooted. Initial readback: `sys.boot_completed=1`, framework lookup `26.0px`, panorama property `true`, secure mode `1`, forced-disable state `0`, and the feature line is present in the mounted XML. The owner has not yet visually confirmed the bottom-corner drag on this combination. `fixo_fullscreen_caption` v0.5 remains installed during the test. The OPD2403 product-name experiment remains disabled.
