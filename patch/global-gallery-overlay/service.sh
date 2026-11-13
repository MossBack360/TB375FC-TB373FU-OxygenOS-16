#!/system/bin/sh
MODDIR=${0%/*}

if [ "$1" = "--apply" ]; then
    target=/my_stock/priv-app/OppoGallery2/OppoGallery2.apk
    payload="$MODDIR/payload/OppoGallery2.apk"
    [ -f "$target" ] && [ -f "$payload" ] || exit 1
    chmod 0644 "$payload" || exit 1
    chcon u:object_r:system_file:s0 "$payload" || exit 1
    mount --bind "$payload" "$target" || exit 1
    am force-stop com.oneplus.gallery || true
    for pid in $(pidof com.oneplus.gallery); do
        kill -9 "$pid" || true
    done
    sha256sum "$target"
    log -t FixOGlobalApps "Applied Gallery APK overlay"
    exit 0
fi

until [ "$(getprop sys.boot_completed)" = "1" ]; do
    sleep 1
done

su -mm -c "sh '$MODDIR/service.sh' --apply" >"$MODDIR/runtime.log" 2>&1
