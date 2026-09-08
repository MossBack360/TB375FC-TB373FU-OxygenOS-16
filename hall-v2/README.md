# Xiaoxin Hall Cover v2

For TB375FC. It reads `/sys/bus/platform/drivers/hall/hall_status` (`1` open, `0` closed) and listens to the `hall` input device.

The daemon emits `KEYCODE_SLEEP`/`KEYCODE_WAKEUP` only while `Settings.Global.device_case_enabled` is `1`. This is the same database key written by the system smart-cover switch.

The module id remains `xiaoxin_hall_cover`, so installing the ZIP upgrades v1. The confirmed v1 archive is not modified.
