# FixO contour glow trial

This is an experimental, separate module for the missing `质感轮廓光` option
under the blurred texture settings. It keeps the signed OxygenOS UXDesign APK
at boot, then bind-mounts the modified APK after boot so PackageManager can
finish scanning the original package first.

The patch adds the ColorOS `MATERIAL_STROKE` entry to the existing OxygenOS
texture list, adds the matching read/write path for the
`system_material_stroke_enable` system setting, and adds the metadata gate used
by the ColorOS tablet implementation. It does not replace SystemUI or Launcher.

This remains a trial: the current OxygenOS SystemUI/Launcher implementation
has not been proven to render the effect on TB375FC. Disable this module from
Magisk if the option does not work or UXDesign behaves unexpectedly.
