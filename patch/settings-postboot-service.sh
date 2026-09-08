#!/system/bin/sh
# Let PackageManager scan the original signed APK before applying the tested overlay.
MODDIR=${0%/*}

if [ "$1" = "--apply" ]; then
    target=/system_ext/priv-app/Settings/Settings.apk
    payload="$MODDIR/payload/Settings.apk"
    [ -f "$payload" ] && [ -f "$target" ] || exit 1
    chmod 0644 "$payload" || exit 1
    chcon u:object_r:system_file:s0 "$payload" || exit 1
    mount --bind "$payload" "$target" || exit 1
    # ActivityManager may reject a transaction briefly during startup.
    am force-stop com.android.settings || true
    for settings_pid in $(pidof com.android.settings); do
        kill -9 "$settings_pid" || exit 1
    done
    log -t FixOSettings "Applied confirmed Settings after package scan"
    echo "postboot-overlay=ok"
    exit 0
fi

until [ "$(getprop sys.boot_completed)" = "1" ]; do
    sleep 1
done

su -mm -c "sh '$MODDIR/service.sh' --apply" >"$MODDIR/runtime.log" 2>&1
