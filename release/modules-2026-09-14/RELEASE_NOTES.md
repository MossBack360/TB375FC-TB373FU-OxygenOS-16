# TB375FC / TB373FU OxygenOS 16 confirmed modules — 2026-09-14

This milestone was tested after a clean flash. It publishes only modules that are new or whose version changed since `modules-2026-09-09`.

## New or updated assets

- `fixo-settings-memory-expand-coloros-activity-v3.9-magisk.zip`
  - Upgrades `fixo_settings_confirmed` from v3.6 to v3.9.
  - Keeps the confirmed OxygenOS Settings UI and adds the working ColorOS-compatible RAM-expansion activity/writeback.
- `fixo-systemui-gesture-polish-v0.5-magisk.zip`
  - Restores fullscreen three-dot controls, the accepted drag-corner fallback, and follow-finger back animation.
- `fixo-camera-optimize-disable-v1.1-magisk.zip`
  - Disables the Oplus startup policy responsible for WeChat scanner and ZUI Camera startup failures.
- `fixo-freeform-corner-gesture-confirmed-v1.2-magisk.zip`
  - Enables the Panorama work-station feature and bottom-corner freeform gesture gates.
- `fixo-speaker-rotation-bridge-v2.1-magisk.zip`
  - Rotates the four physical speaker channels with display orientation.
- `fixo-attention-asi-v0.1-magisk.zip`
  - Routes Android AttentionManager to the bundled Google ASI attention service.
  - Confirmed with a 10-second screen timeout while continuous attention kept the display awake for at least 25 seconds.
- `fixo-wake-gesture-glue-v0.2-magisk.zip`
  - Uses the ZUI-sensitive MTK sensor type 23 path for lift-to-wake and follows the OxygenOS switch.

## Reuse from modules-2026-09-09

These versions are unchanged and are intentionally not uploaded again:

- `fixo-display-pq-v1.0-magisk.zip`
- `fixo-global-apps-v1.0-magisk.zip`
- `fixo-ota-system-magisk.zip`
- `fixo-zui-camera-privacy-v1.2-magisk.zip`
- `xiaoxin-hall-settings-linked-v2-magisk.zip`

The local hall v2 archive additionally contains a README, but its `module.prop`, `service.sh`, version, and behavior match the existing release asset.

## Installation order

For a clean flash, install the non-SystemUI modules first and reboot. Let Settings/global-app package scanning settle, then install SystemUI v0.5 separately and reboot again. This keeps the SystemUI module's 30-second stability guard from observing unrelated first-boot package restarts.

Do not mix this confirmed baseline with OPD2514/A.30 AI add-on experiments.
