# Patch catalog

Generated ZIP/APK artifacts under `out/` are local and intentionally ignored by Git. Source scripts and module trees under `patch/`, `hall/`, and `hall-v2/` are the durable record. Verify checksums from each artifact directory before installation.

## Current confirmed set

| Module ID | Purpose | Durable source or build script | Current local artifact |
|---|---|---|---|
| `fixo_settings_confirmed` | Stable Settings, OxygenOS icons/card/easter egg | `patch/build_global_polish.py`, `patch/build_easter_logo_only.py`, Settings reports | `out/confirmed-2026-09-06/` and later confirmed Settings directories |
| `fixo_global_apps` | International OnePlus Gallery and account components | `patch/global-apps-overlay/`, `patch/package_global_apps.py` | `out/global-apps-overlay-2026-09-08/` |
| `fixo_ota_system` | OxygenOS updater Activity and system permissions | `patch/package_ota_restore.py` | `out/ota-system-restore-2026-09-07/fixo-ota-system-magisk.zip` |
| `xiaoxin_hall_cover` | Settings-linked hall-cover sleep/wake | `hall-v2/`, `patch/package_hall_v2.py` | `out/hall-settings-linked-confirmed-2026-09-08/` |
| `fixo_display_pq` | MTK PQ bridge for adaptive color and color modes | `patch/display-pq-controller/`, `patch/package_display_pq.py` | `out/display-pq-bridge-2026-09-08/` |
| `fixo_zui_lenovo_privacy` | ZUI Camera agreement/privacy activities | `patch/package_zui_privacy.py` | `out/zui-lenovo-privacy-2026-09-08/` or the v1.2 solidified ZIP |
| `fixo_camera_optimize_disable` | Remove Oplus scanner/camera startup optimization policy | `patch/camera-optimize-disable/` | `out/camera-optimize-disable-2026-09-10/fixo-camera-optimize-disable-v1.1-magisk.zip` |
| `fixo_freeform_corner_gesture` | Enable bottom-corner freeform gesture feature gates | `patch/freeform-corner-gesture/` | `out/freeform-corner-gesture-confirmed-2026-09-10/` |
| `fixo_fullscreen_caption` | Three-dot controls, v0.2 drag radius, follow-finger back gesture | `patch/build_systemui_gesture_v05.py`, `patch/fullscreen-caption/` | `out/systemui-gesture-polish-v0.5-2026-09-11/fixo-systemui-gesture-polish-v0.5-magisk.zip` |
| `fixo_speaker_rotation_prop` | Rotate physical speaker channels with display | `patch/speaker-rotation-bridge/` | `out/speaker-rotation-confirmed-2026-09-11/` |

Current SystemUI v0.5 checksums:

- APK: `92c57e647c9520cb043be1d0a0cf010c6f1e7dec2b72129837b45cc261e57560`
- Magisk ZIP: `dae75d0b2d274c1224714316434e4bb60cbc49f6e74d1e73ef45f07b931cf3e2`

## Archived experiments

| Experiment | Location/source | Result |
|---|---|---|
| Formal 30↔50 px freeform radius interpolation v0.4 | `patch/archive/build_systemui_animation_v04.py`; local `out/systemui-animation-polish-v0.4-2026-09-11/` | Functioned, but owner rejected the look. Archive only. |
| Earlier corner transition v0.3 | `out/freeform-corner-transition-v0.3-2026-09-11/` | Superseded by v0.4/v0.5. |
| `fixo_freeform_smooth_corner` | `out/rounded-corner-transition-2026-09-11/` | Ineffective and disabled. |
| OPD2514 AI add-ons | `patch/build_opd2514_ai.py`, `out/opd2514-ai-addons-*` | No useful user-visible change; disabled. |
| Material contour glow | `patch/material-stroke/`, `patch/build_contour_glow_trial.py` | Settings switch can appear, render effect absent; disabled. |
| Dolby DAP trials | `patch/dolby-dap-overlay/`, `patch/package_dolby_trial.py`, `out/dolby-*` | UI/IPC restored but no audible DSP effect. Do not publish as fixed. |
| Third-party `speaker_rotation_fix` | local analyzed archive | Boot hang; keep disabled. |
| Lift-to-wake sensor bridge | `patch/package_lift_to_wake*.py`, `out/lift-to-wake-*` | Works only with phone-like pose; accepted experiment, currently not installed. |

## Replacement-module invariant

`fixo_fullscreen_caption` is the one active SystemUI payload owner. Its v0.5 uses the same ID as earlier caption/corner versions so upgrades replace the payload instead of creating competing bind mounts. Apply the same pattern to Settings: extend the confirmed payload or rebuild a combined successor; never activate several unrelated modules that each mount `/system_ext/priv-app/Settings/Settings.apk`.
