# FixO smart refresh feature glue v0.3

Restores the native OPlus `智能切换` refresh-rate option without replacing Settings, SystemUI, or framework APKs.

The target exposes `/my_product` as a standalone partition, so Magisk magic mount does not create or replace files there. `post-fs-data.sh` follows the confirmed freeform feature-module pattern and bind-mounts the merged feature XML before OPlus feature discovery.

Confirmed behavior on 2026-09-14:

- secure mode `oplus_customize_screen_refresh_rate=0`;
- an active gesture sampled display mode ID 2 (`120 Hz`);
- five seconds idle sampled display mode ID 3 (`60 Hz`);
- Settings scrolling remains at `60 Hz` because the stock OPlus TouchIdle configuration blacklists `com.android.settings`;
- Settings and SystemUI APK hashes remain unchanged.

The Settings limitation is accepted for v0.3. Do not edit `oplus_vrr_config.json` as part of this module without a separate regression test covering video, games, brightness, and thermal policy.
