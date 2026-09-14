# Patch catalog

Generated ZIP/APK artifacts under `out/` are local and intentionally ignored by Git. Source scripts and module trees under `patch/`, `hall/`, and `hall-v2/` are the durable record. Verify checksums before installation.

## Current confirmed set — 2026-09-14

| Module ID | Version | Purpose | Current artifact | ZIP SHA-256 |
|---|---:|---|---|---|
| `fixo_settings_confirmed` | 3.9 | OxygenOS Settings UI plus working RAM expansion | `out/memory-expand-coloros-activity-v39-2026-09-12/fixo-settings-memory-expand-coloros-activity-v3.9-magisk.zip` | `df527eb814bb107ee57aaba57eb74bf61c52ca15c82dc00dfbe53b826ede30ac` |
| `fixo_fullscreen_caption` | 0.5 | Three-dot controls, drag-radius fallback, follow-finger back gesture | `out/systemui-gesture-polish-v0.5-2026-09-11/fixo-systemui-gesture-polish-v0.5-magisk.zip` | `dae75d0b2d274c1224714316434e4bb60cbc49f6e74d1e73ef45f07b931cf3e2` |
| `fixo_camera_optimize_disable` | 1.1 | Disable the Oplus scanner/camera startup policy | `out/camera-optimize-disable-2026-09-10/fixo-camera-optimize-disable-v1.1-magisk.zip` | `f97613c5a9ef5305f19ac2dd4ac743525d3043cbd9b874ca2e12a6f4003529f9` |
| `fixo_display_pq` | 1.0 | MTK PQ bridge for adaptive color and color modes | `out/display-pq-bridge-2026-09-08/fixo-display-pq-v1.0-magisk.zip` | `5d7d1f7c3dd64adafe7898d33f8bf3d2bdeca027ae6a450befb2e64005a8e286` |
| `fixo_freeform_corner_gesture` | 1.2 | Enable the Panorama/bottom-corner freeform gates | `out/freeform-corner-gesture-confirmed-2026-09-10/fixo-freeform-corner-gesture-confirmed-v1.2-magisk.zip` | `e14f8d9f3a787ad31725f4861848cad9987b7128b7fad750daa62ad12935c7f4` |
| `fixo_global_apps` | 1.0 | International OnePlus Gallery/account components | `out/global-apps-overlay-2026-09-08/fixo-global-apps-v1.0-magisk.zip` | `106de26b224bbdb1b078c8bb332433528183f851d988cd61c5d5feefb09afa37` |
| `fixo_ota_system` | 1.0 | OxygenOS updater activity and permissions | `out/ota-system-restore-2026-09-07/fixo-ota-system-magisk.zip` | `dae68e01dd3815097f49e07879ba251757a062e4c47de797868be4706b3ef458` |
| `xiaoxin_hall_cover` | 2.0 | Settings-linked hall-cover sleep/wake | `out/hall-settings-linked-confirmed-2026-09-08/xiaoxin-hall-settings-linked-v2-magisk.zip` | `57b64c3d7e5b1864577762cdd54b5cc329c40e5609f8a8487df92d4775fed365` |
| `fixo_speaker_rotation_prop` | 2.1 | Rotate physical speaker channels with display | `out/speaker-rotation-confirmed-2026-09-11/fixo-speaker-rotation-bridge-v2.1-magisk.zip` | `9c40cb9575498511e3e8e4fd206232802f3bce6e36b2ee29005f5717ef0fd92e` |
| `fixo_zui_lenovo_privacy` | 1.2 | ZUI Camera agreement/privacy activities | `out/zui-camera-privacy-test-2026-09-08/fixo-zui-camera-privacy-v1.2-magisk.zip` | `836f2406258c6fd8a6796b48b237ea5f720ae94762979b9ed47decf2a5c05998` |
| `fixo_attention_asi` | 0.1 | Route AttentionManager to Google ASI attention | `out/attention-asi-trial-2026-09-12/fixo-attention-asi-v0.1-magisk.zip` | `e6660fc6e7da908b6bd32c39b2d49f26f602865ab722615d2ba04543bb31b45d` |
| `fixo_wake_gesture_glue` | 0.2 | ZUI-sensitive MTK sensor-23 lift-to-wake bridge | `out/wake-gesture-glue-v02-2026-09-12/fixo-wake-gesture-glue-v0.2-magisk.zip` | `0accefa7b0d9022d790f8c73a2f1cd38653bd1ef87112f9fbcc3024e0fabdc16` |
| `fixo_smart_refresh` | 0.3 | Expose native OPlus `智能切换` and mode 0 | `out/smart-refresh-feature-v0.3-2026-09-14/fixo-smart-refresh-v0.3-magisk.zip` | `a67f428c8e246f50461d387757aa571a56fa02ae31fe5330643922fc4f2d709e` |

Current mounted APK hashes:

- SystemUI v0.5: `92c57e647c9520cb043be1d0a0cf010c6f1e7dec2b72129837b45cc261e57560`.
- Settings v3.9: `dd16f3af8b453a9f8ebe19ee9fcf22be80682a8f8aac528c81c379707e63e2c0`.
- Smart-refresh mounted feature XML: `e6f666f5d9fb31f3029d89ba259cdb9197d3df273ffc702c7ff0f3352431d0e7`.

Smart-refresh v0.3 is confirmed usable, with a deliberate recorded limit: Settings scrolling stays at `60 Hz` because the stock TouchIdle configuration blacklists `com.android.settings`. The observed native behavior is `120 Hz` during an active gesture and `60 Hz` after five seconds idle. Treat an `oplus_vrr_config.json` override as a new experiment, not part of v0.3.

## GitHub release comparison

The existing `modules-2026-09-09` release already has byte-identical PQ 1.0, global apps 1.0, OTA 1.0, and ZUI privacy 1.2 assets. They must not be uploaded again.

The release hall v2 archive differs only because the local archive also contains `README.md`; `module.prop` and `service.sh` are byte-identical, and the version remains 2.0. Per owner instruction, do not republish it without a version bump.

The `modules-2026-09-14` release contains only new or version-changed assets: Settings 3.9, SystemUI 0.5, camera policy 1.1, corner gesture 1.2, speaker rotation 2.1, attention 0.1, and wake gesture 0.2.

## Archived or rejected experiments

| Experiment | Location/source | Result |
|---|---|---|
| Panorama tablet gate v1.4 | `out/panorama-tablet-gate-v1.4-abandoned-2026-09-14/` | Registered deeper branch hooks but did not restore the gesture; rejected and superseded by confirmed v1.2. |
| Formal freeform radius interpolation v0.4 | `patch/archive/build_systemui_animation_v04.py` | Functioned, but owner rejected the look. |
| `fixo_freeform_smooth_corner` | `out/rounded-corner-transition-2026-09-11/` | Ineffective; keep disabled/not installed. |
| OPD2514/A.30 AI add-ons | `patch/build_opd2514_ai.py`, local `out/opd2514-ai-addons-*` | Removed from the confirmed set after regressions; do not silently reinstall. |
| Material contour glow | `patch/material-stroke/` | Settings switch appeared, render effect absent. |
| Dolby DAP trials | `patch/dolby-dap-overlay/` | UI/IPC restored but no audible DSP effect. |
| Third-party `speaker_rotation_fix` | local analyzed archive | Caused a second-screen boot hang. |

## Replacement-module invariant

`fixo_fullscreen_caption` is the only active SystemUI payload owner. `fixo_settings_confirmed` is the only active Settings payload owner. Extend those module IDs as upgrades; never activate competing bind mounts for either APK.
