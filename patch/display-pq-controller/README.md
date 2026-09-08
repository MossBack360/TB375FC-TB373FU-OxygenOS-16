# FixO Display PQ bridge

This Magisk module connects the OxygenOS 16 display settings to the TB375FC
MediaTek PQ implementation without replacing `services.jar`.

- `setting_enable_color_temperature_regulation`: enables or disables MTK
  Chameleon and its `tcs3701_cct` sensor input.
- `oplus_customize_color_mode`: maps OxygenOS Vivid (`0`), Natural (`1`), and
  Professional/Real (`6`) to the matching ZUI peridot CCORR matrices.

The service reapplies both settings after boot and whenever the vendor PQ
service restarts. Runtime messages use the `FixODisplayPQ` log tag.

## Known behavior

Screen color mode changes have a noticeable delay. The bridge polls the
OxygenOS setting every two seconds, starts a short-lived `app_process`, and the
vendor PQ engine then performs its own transition. This delay is expected and
does not indicate that the selection failed.
