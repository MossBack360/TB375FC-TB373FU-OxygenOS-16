# Framework display rounded-corner RRO trial

Goal: make stock SystemUI's `FullscreenTaskIndicatorManager$SpringDragManager` receive a nonzero `Display.getRoundedCorner()` value without replacing `SystemUI.apk`.

The current ROM's framework path is `Display.getRoundedCorner()` -> `DisplayInfo.roundedCorners` -> `LocalDisplayAdapter.LocalDisplayDevice.getDisplayDeviceInfoLocked()` -> `RoundedCorners.fromResources()`. With no per-display ID entry, `RoundedCorners.getRoundedCornerRadius()` reads `android:dimen/rounded_corner_radius`. Before this trial, the resource and all four `dumpsys window displays` corner radii were zero.

Source: `patch/display-corner-rro/AndroidManifest.xml` and `res/values/dimens.xml`. The RRO sets only `rounded_corner_radius=30px`, targets `android`, and is installed as Magisk module `fixo_display_corners_rro` v0.1-test at `system/product/overlay/FixoDisplayCorners.apk`. Trial ZIP: `out/display-corner-rro-v0.1-2026-11-11/fixo-display-corner-rro-v0.1-test.zip` (SHA-256 `2bece6a59f3903b16a1b1cadf5193d96c2a783fe9065794d57fcccaa972fb461`). The signed overlay APK SHA-256 is `84ab32f7fed272d918c5d7c1504a92755b175da44bc5d0de0b7e8e47b8635e68`. Signing key remains outside Git.

After installation and reboot, `cmd overlay lookup android android:dimen/rounded_corner_radius` reports `30.0px`. All four `mRoundedCorners` values are radius 30. `/data/resource-cache/product@overlay@FixoDisplayCorners.apk@idmap` maps target resource `0x01050342` to the new overlay resource `0x7f010000`. Stock SystemUI APK SHA-256 remains `72cfa6810c72d7aef8cfdfd8f57ee8f88117c2b5867f272d3700a08fe3c32dc7`; no APK of that package was replaced. The overlay is accepted through idmap despite its package name not appearing in `pm path` or `cmd overlay list`.

The `ro.oplus.display.rc.size=26,26,26,26` property module remains separately active. This RRO changes Android display-corner geometry globally, so other apps and animations may react to the new 30px value. Visual regression has not yet been confirmed by the owner. Keep the v0.1 ZIP out of the stable installer archive until that check is complete. Rollback: disable `fixo_display_corners_rro` in Magisk and reboot; recheck that the framework resource and `mRoundedCorners` return to zero.

For ROM integration, add an equivalent single-resource framework overlay to the system/product overlay set before packing `super.img`. This does not require replacing or resigning `SystemUI.apk`.
