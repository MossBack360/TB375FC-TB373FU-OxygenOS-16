#!/system/bin/sh
MODDIR=${0%/*}

if [ "$1" = "--apply" ]; then
    target=/my_stock/priv-app/KeKeUserCenter/KeKeUserCenter.apk
    payload="$MODDIR/payload/KeKeUserCenter.apk"
    [ -f "$target" ] && [ -f "$payload" ] || exit 1
    chmod 0644 "$payload" || exit 1
    chcon u:object_r:system_file:s0 "$payload" || exit 1
    mount --bind "$payload" "$target" || exit 1
    am force-stop com.oneplus.account || true
    log -t FixOAccount "Applied global OnePlus account overlay"
    sha256sum "$target"
    exit 0
fi

until [ "$(getprop sys.boot_completed)" = "1" ]; do
    sleep 1
done

su -mm -c "sh '$MODDIR/service.sh' --apply" >"$MODDIR/runtime.log" 2>&1
