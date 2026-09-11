#!/system/bin/sh
# Keep the signed system APK for PackageManager scanning, then mount the patched code.
MODDIR=${0%/*}

if [ "$1" = "--apply" ]; then
    target=/system_ext/app/OplusGestureUI/OplusGestureUI.apk
    payload="$MODDIR/payload/OplusGestureUI.apk"
    [ -f "$payload" ] && [ -f "$target" ] || exit 1
    chmod 0644 "$payload" || exit 1
    chcon u:object_r:system_file:s0 "$payload" || exit 1
    mount --bind "$payload" "$target" || exit 1

    # Restart the service so the process loads the patched DEX from the bind mount.
    gesture_pid=$(pidof com.oplus.gesture)
    [ -z "$gesture_pid" ] || kill -9 $gesture_pid
    sleep 2
    am startservice -n com.oplus.gesture/.server.ScreenOffGestureService || exit 1
    log -t FixOLiftToWake "Applied MTK tilt value compatibility patch"
    echo "postboot-overlay=ok"
    exit 0
fi

until [ "$(getprop sys.boot_completed)" = "1" ]; do
    sleep 1
done

su -mm -c "sh '$MODDIR/service.sh' --apply" >"$MODDIR/runtime.log" 2>&1
