# Magisk module audit — 2026-09-14

## Result

The authoritative confirmed set contains 15 module IDs. The live tablet contains all 15: 14 active and one disabled. No confirmed module is completely missing.

The only state mismatch is `fixo_launcher_corner_radius` v1.0. It is installed with a `disable` marker. The module contains only `module.prop` and `system.prop`, so it cannot disable itself. With it disabled after reboot, `ro.oplus.display.rc.size` is back to `65,65,65,65`; the previously confirmed desktop-to-fullscreen corner fix is therefore not active. This module is unrelated to the still-open A/B quick-switch corner animation.

`fixo_zui_camera_sr_disable` was omitted from the earlier 12-module recovery snapshot and patch catalog because v1.0 remained under the camera crash investigation directory instead of being promoted into the durable confirmed inventory. It has now been replaced under the same ID by confirmed v2.0.

## Confirmed inventory

| Module ID | Version | Live state |
|---|---:|---|
| `fixo_attention_asi` | 0.1 | Active |
| `fixo_camera_optimize_disable` | 1.1 | Active |
| `fixo_display_pq` | 1.0 | Active |
| `fixo_freeform_corner_gesture` | 1.2 | Active |
| `fixo_fullscreen_caption` | 0.5 | Active |
| `fixo_global_apps` | 1.0 | Active |
| `fixo_launcher_corner_radius` | 1.0 | Disabled |
| `fixo_ota_system` | 1.0 | Active |
| `fixo_settings_confirmed` | 3.9 | Active |
| `fixo_smart_refresh` | 0.3 | Active |
| `fixo_speaker_rotation_prop` | 2.1 | Active |
| `fixo_wake_gesture_glue` | 0.2 | Active |
| `fixo_zui_camera_sr_disable` | 2.0 | Active |
| `fixo_zui_lenovo_privacy` | 1.2 | Active |
| `xiaoxin_hall_cover` | 2.0 | Active |

## Deliberately excluded or superseded

- `fixo_lift_to_wake_sensor` and Settings 3.7 are superseded by Settings 3.9 plus `fixo_wake_gesture_glue` 0.2. Do not install them together.
- `fixo_global_account` is superseded by `fixo_global_apps` 1.0.
- Earlier Settings, SystemUI, hall, speaker, privacy, camera-policy, and corner-gesture packages are upgrades under the same IDs, not additional modules.
- WeChat scanner compatibility/fullscreen trials are superseded by `fixo_camera_optimize_disable` 1.1.
- Dolby modules changed UI/IPC but had no audible DSP effect and are not confirmed fixes.
- AI add-ons, material-stroke, panorama v1.4, formal-corner v0.4, smooth-corner, GPS trial, wake-framework trial, and third-party speaker modules remain rejected, unsafe, or unconfirmed.

## Process correction

Future recovery audits must compare three explicit sets: the durable confirmed catalog, all live module IDs plus `disable`/`remove` markers, and post-milestone confirmed additions. Presence alone is insufficient; the live property/mounted hash must also be checked for property-only and bind-mount modules.

The installed Codex skill copy and the repository skill copy were found out of sync. The repository references are authoritative and must be synchronized to the installed skill after this update so a new thread does not start from the stale 2026-09-11 inventory.
