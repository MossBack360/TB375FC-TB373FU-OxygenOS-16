# OPlus transition radius property versus Android display corners

On 2026-11-11 the owner requested installation of the archived `fixo_launcher_corner_radius` v1.1-test to determine whether its `ro.oplus.display.rc.size` value supplies the original SystemUI drag-corner fallback.

Before installation, the live property was `65,65,65,65`; `dumpsys window displays` reported all four `mRoundedCorners` radii as 0, and `cmd overlay lookup android android:dimen/rounded_corner_radius` returned `0.0dip`.

The archived ZIP `16-transition-corner-radius-config-v1.1-test.zip` (SHA-256 `6ae7ca47383cf77d354553d6a5269a2b2adebf4df9a1e8509dbc35bd936dad4d`) contains only `system.prop` with `ro.oplus.display.rc.size=26,26,26,26` plus metadata. It was installed through Magisk and the tablet rebooted. After boot, the property was `26,26,26,26`, but all four `mRoundedCorners` radii and the framework overlay lookup still reported 0. SystemUI PID 2665 stayed stable across two checks.

The stock `FullscreenTaskIndicatorManager$SpringDragManager` calls `OplusFlexibleWindowAnimationUtils.getDisplayCornerRadius(Display)`, which reads `Display.getRoundedCorner()` rather than this property. The v0.5 SystemUI patch uses `FullscreenTaskImageView.getCornerRadius()` instead; that method falls back to at least 12dp when the display API reports zero. Thus this property module does not remove the need for the separate SystemUI drag-corner fallback. Whether it changes other transition visuals is left to the owner's visual check. The freeform corner gesture module was not installed in this boot snapshot.
