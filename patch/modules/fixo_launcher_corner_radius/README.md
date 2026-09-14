# FixO OPlus transition corner radius v1.1-test

This property-only test upgrades `fixo_launcher_corner_radius` in place and does not replace Launcher, SystemUI, framework, or vendor files.

- Stock/live OxygenOS port value: `65,65,65,65`.
- Previous v1.0 value: `0,0,0,0` for primary and secondary displays.
- This isolated test value: `26,26,26,26` for `ro.oplus.display.rc.size` only.

Disable this module and reboot to restore the ROM value of 65 px.
