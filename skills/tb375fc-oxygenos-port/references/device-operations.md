# Device operations

## Preflight

Use the explicit ADB executable because it is not guaranteed to be on `PATH`:

```powershell
$adb = 'C:\Program Files (x86)\MiFlashPro\adb.exe'
& $adb devices
```

Before installing a module, capture the live state with `scripts/capture_device_state.ps1`. Check active and disabled modules, especially other owners of the same Settings/SystemUI APK.

## Install and verify a Magisk module

Push the exact ZIP to `/data/local/tmp`, install it with `magisk --install-module`, and reboot. After boot, verify:

```powershell
& $adb shell getprop sys.boot_completed
& $adb shell pidof com.android.systemui
& $adb shell su -c 'cat /data/adb/modules/<module-id>/module.prop'
& $adb shell su -c 'cat /data/adb/modules/<module-id>/runtime.log'
& $adb shell sha256sum /system_ext/priv-app/SystemUI/SystemUI.apk
```

For a Settings payload use the Settings path and process instead. Observe a stable PID across at least two checks when a module restarts a core UI process.

## Recovery

If a newly installed module prevents the UI or device from completing boot, disable that exact module from ADB/recovery:

```sh
touch /data/adb/modules/<module-id>/disable
reboot
```

Known failed modules that should remain disabled are `fixo_freeform_smooth_corner` and `speaker_rotation_fix`. Do not remove or recursively move module directories during diagnosis; a `disable` marker is reversible and preserves evidence.

The confirmed Settings and SystemUI service scripts check the base APK SHA-256 and may self-disable when the base mismatches or the process is unstable. Read `runtime.log` before changing the payload.

## Evidence collection

- Clear logcat immediately before reproducing a focused problem.
- Do not infer chronology from the tablet's current file timestamps: its wall clock was observed at 2026-01-01 while the host date was 2026-09-11.
- Record timestamps, the exact UI route, orientation/windowing mode, package/activity, and whether the behavior differs in split screen.
- For vendor feature flags, compare live `/my_product/etc/extension/` with the matching reference ROM; a visible Settings entry does not prove the lower service/render path is enabled.
- For camera failures, capture ActivityTaskManager, CameraService/provider, vendor camera HAL, SELinux, tombstone, and ANR evidence together. The WeChat issue was an Activity startup-policy delay rather than a camera API or SELinux failure.
- Do not touch ADB while the owner says a flash is in progress.
