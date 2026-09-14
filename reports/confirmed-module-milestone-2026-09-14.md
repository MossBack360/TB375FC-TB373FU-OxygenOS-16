# Confirmed module milestone — 2026-09-14

## Outcome

After a clean flash, the owner tested and accepted the selected module set as the new recovery baseline. The previous AI-add-on regression state is not part of this milestone.

Installation was deliberately staged:

1. Install the 11 non-SystemUI modules, reboot, wait for large Settings/global-app package scanning, and verify stable SystemUI/system_server PIDs.
2. Install SystemUI v0.5 alone, reboot, wait through its 30-second guard, and verify its runtime log and mounted hash.

This sequence produced no disabled modules. The owner then confirmed the patches work.

## Runtime evidence

- `sys.boot_completed=1`.
- SystemUI PID: `7008` across both checks.
- SystemUI runtime: `caption-overlay=ok pid=7008`.
- SystemUI SHA-256: `92C57E647C9520CB043BE1D0A0CF010C6F1E7DEC2B72129837B45CC261E57560`.
- Settings SHA-256: `DD16F3AF8B453A9F8EBE19EE9FCF22BE80682A8F8AAC528C81C379707E63E2C0`.
- Panorama branch: `true`; forced-disable state: `0`; work-station feature present.
- ASI runtime: `set_result=true`.
- Device snapshot: `out/confirmed-selected-modules-2026-09-14/LIVE_DEVICE_STATE.txt`.

## Release policy

GitHub `modules-2026-09-09` assets were compared by the asset API digest, not filename alone.

- Byte-identical and reused: display PQ 1.0, global apps 1.0, OTA 1.0, ZUI privacy 1.2.
- Hall v2.0 is reused because its functional entries (`module.prop` and `service.sh`) are byte-identical; the local archive only adds README documentation.
- New/version-changed and published in `modules-2026-09-14`: Settings 3.9, SystemUI 0.5, camera policy 1.1, corner gesture 1.2, speaker rotation 2.1, attention 0.1, wake gesture 0.2.
